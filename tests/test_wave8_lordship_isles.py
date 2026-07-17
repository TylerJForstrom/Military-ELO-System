from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_lordship_isles import (
    WAVE8_LORDSHIP_ISLES_CONTRACT_IDS,
    WAVE8_LORDSHIP_ISLES_CONTRACTS,
    WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_ENTITIES,
    WAVE8_LORDSHIP_ISLES_EXCLUSIONS,
    WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS,
    WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE,
    WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT,
    WAVE8_LORDSHIP_ISLES_HOLD_IDS,
    WAVE8_LORDSHIP_ISLES_HOLDS,
    WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_LORDSHIP_ISLES_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS,
    WAVE8_LORDSHIP_ISLES_NONPROMOTIONS,
    WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES,
    WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_RESERVED_IDS,
    WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_SOURCES,
    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS,
    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
    install_wave8_lordship_isles_entities,
    install_wave8_lordship_isles_sources,
    promote_wave8_lordship_isles_contracts,
    validate_wave8_lordship_isles_funnel,
    validate_wave8_lordship_isles_integration_dispositions,
    validate_wave8_lordship_isles_queue_contracts,
    wave8_lordship_isles_audit_signature,
    wave8_lordship_isles_cohort_counts,
    wave8_lordship_isles_counts,
    wave8_lordship_isles_location_quarantine_additions,
    wave8_lordship_isles_metadata,
    wave8_lordship_isles_row_dispositions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_lordship_isles_"
EXACT_LABEL = "lordship of the isles"

ALEXANDER_REGIME = "alexander_macdonald_lordship_regime_1423_1449"
LOCHABER_ROYAL = "james_i_lochaber_royal_coalition_1429"
INVERLOCHY_ISLANDS = (
    "donald_balloch_alasdair_carrach_inverlochy_coalition_1431"
)
INVERLOCHY_ROYAL = "mar_caithness_inverlochy_royal_coalition_1431"
STRATHFLEET_SUTHERLAND = "robert_sutherland_strathfleet_defence_1453"
STRATHFLEET_ISLANDS = "john_macdonald_strathfleet_raid_detachment_1453"

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Lochaber1429-1": ({LOCHABER_ROYAL}, {ALEXANDER_REGIME}),
    "hced-Inverlochy1431-1": ({INVERLOCHY_ISLANDS}, {INVERLOCHY_ROYAL}),
    "hced-Strathfleet1453-1": (
        {STRATHFLEET_SUTHERLAND},
        {STRATHFLEET_ISLANDS},
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


class Wave8LordshipIslesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "wave8-funnel-current.json")

    def _installed(self):
        fixture_entity_ids = {
            str(entity["id"]) for entity in WAVE8_LORDSHIP_ISLES_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_lordship_isles_entities(entities)

        fixture_source_ids = {
            str(source["id"]) for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_lordship_isles_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_LORDSHIP_ISLES_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_lordship_isles_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return events, entities, sources, existing

    def test_signature_counts_cohorts_and_metadata_are_pinned(self) -> None:
        payload = {
            "contracts": WAVE8_LORDSHIP_ISLES_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_LORDSHIP_ISLES_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS
            ),
            "funnel_audit": WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT,
            "holds": WAVE8_LORDSHIP_ISLES_HOLDS,
            "integration_dispositions": WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT,
            "location_reviews": WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS,
            "outcome_overrides": WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": (
                WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS
            ),
            "row_dispositions": WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS,
            "sources": WAVE8_LORDSHIP_ISLES_SOURCES,
            "terminal_exclusions": WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
        }
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(
            digest,
            "b5af4f7d3683add9f1931dc42ac24b97582618e1a3c79e7a7816b255aed68b89",
        )
        self.assertEqual(digest, wave8_lordship_isles_audit_signature())
        self.assertEqual(digest, WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_lordship_isles_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "new_entities": 6,
                "new_sources": 11,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "related_hced_dispositions": 1,
                "reviewed_hced_rows": 5,
                "sole_blocker_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_lordship_isles_cohort_counts(),
            {
                "james_i_lordship_campaign_1429_1431": 2,
                "lordship_internal_conflict_early_1480s": 1,
                "ross_succession_conflict_1411": 1,
                "sutherland_lordship_raid_1453": 1,
            },
        )

        metadata = wave8_lordship_isles_metadata()
        self.assertEqual(metadata["exact_label"], EXACT_LABEL)
        self.assertEqual(metadata["module_owner"], "wave8_lordship_isles")
        self.assertEqual(metadata["signature"], digest)
        self.assertEqual(
            metadata["candidate_ids"],
            sorted(WAVE8_LORDSHIP_ISLES_RESERVED_IDS),
        )
        self.assertEqual(metadata["counts"], wave8_lordship_isles_counts())
        metadata["row_dispositions"].clear()
        self.assertEqual(
            wave8_lordship_isles_row_dispositions(),
            WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS,
        )

    def test_historical_funnel_pins_five_rows_four_sole_and_one_shared(self) -> None:
        sole_ids = {
            "hced-Bloody Bay1480-1",
            "hced-Harlaw1411-1",
            "hced-Inverlochy1431-1",
            "hced-Lochaber1429-1",
        }
        historical_funnel = {
            "labels": [
                {
                    "label": EXACT_LABEL,
                    "event_candidate_id_sha256": WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
                        "event_candidate_id_sha256"
                    ],
                    "events_touched": 5,
                    "sole_blocker_events": 4,
                    "failure_cases": {"zero_time_valid_candidates": 5},
                }
            ],
            "greedy_batch": {
                "ranking": [
                    {
                        "label": EXACT_LABEL,
                        "events_touched": 5,
                        "marginal_events": 4,
                        "newly_unblocked_candidate_id_sha256": (
                            WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
                                "newly_unblocked_candidate_id_sha256"
                            ]
                        ),
                    }
                ]
            },
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "label_failures": [
                        {
                            "label": EXACT_LABEL,
                            "failure_case": "zero_time_valid_candidates",
                        }
                    ],
                    "sole_blocker_label": (
                        EXACT_LABEL if candidate_id in sole_ids else None
                    ),
                }
                for candidate_id in sorted(
                    WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS
                )
            ],
        }
        self.assertEqual(
            validate_wave8_lordship_isles_funnel(historical_funnel),
            {
                "exact_label_rows": 5,
                "shared_label_rows": 1,
                "sole_blocker_rows": 4,
            },
        )
        exact_payload = "".join(
            f"{candidate_id}\n"
            for candidate_id in sorted(WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS)
        )
        sole_payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(sole_ids)
        )
        self.assertEqual(
            hashlib.sha256(exact_payload.encode()).hexdigest(),
            WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT["event_candidate_id_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(sole_payload.encode()).hexdigest(),
            WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
                "newly_unblocked_candidate_id_sha256"
            ],
        )

        changed = copy.deepcopy(historical_funnel)
        next(
            row for row in changed["labels"] if row["label"] == EXACT_LABEL
        )["events_touched"] = 6
        with self.assertRaisesRegex(ValueError, "funnel events_touched changed"):
            validate_wave8_lordship_isles_funnel(changed)

        changed = copy.deepcopy(historical_funnel)
        next(
            row for row in changed["greedy_batch"]["ranking"]
            if row["label"] == EXACT_LABEL
        )["marginal_events"] = 5
        with self.assertRaisesRegex(ValueError, "greedy audit changed"):
            validate_wave8_lordship_isles_funnel(changed)

        changed = copy.deepcopy(historical_funnel)
        next(
            row
            for row in changed["row_label_data"]
            if row.get("candidate_id") == "hced-Harlaw1411-1"
        )["sole_blocker_label"] = None
        with self.assertRaisesRegex(ValueError, "sole-blocker cohort changed"):
            validate_wave8_lordship_isles_funnel(changed)

        changed = copy.deepcopy(historical_funnel)
        next(
            row
            for row in changed["row_label_data"]
            if row.get("candidate_id") == "hced-Strathfleet1453-1"
        )["sole_blocker_label"] = EXACT_LABEL
        with self.assertRaisesRegex(ValueError, "sole-blocker cohort changed"):
            validate_wave8_lordship_isles_funnel(changed)

        self.assertFalse(
            any(
                row.get("label") == EXACT_LABEL
                for row in self.funnel.get("labels", [])
            ),
            "the completed Lordship of the Isles lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                row.get("label") == EXACT_LABEL
                for row in self.funnel.get("greedy_batch", {}).get("ranking", [])
            ),
            "the completed Lordship of the Isles lane must not remain in the "
            "greedy ranking",
        )
        live_row_ids = {
            str(row.get("candidate_id"))
            for row in self.funnel.get("row_label_data", [])
        }
        self.assertFalse(
            live_row_ids & WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS,
            "resolved Lordship of the Isles candidates must be absent from the "
            "live funnel row-label data",
        )

    def test_complete_exact_inventory_hashes_and_one_exact_side_fail_closed(
        self,
    ) -> None:
        self.assertEqual(
            validate_wave8_lordship_isles_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 1,
            },
        )
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == EXACT_LABEL
            or normalize_label(row.get("side_2_raw")) == EXACT_LABEL
        }
        self.assertEqual(set(exact_rows), WAVE8_LORDSHIP_ISLES_RESERVED_IDS)
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS,
            {
                "hced-Bloody Bay1480-1",
                "hced-Harlaw1411-1",
                "hced-Inverlochy1431-1",
                "hced-Lochaber1429-1",
                "hced-Strathfleet1453-1",
            },
        )
        inventories = {
            **WAVE8_LORDSHIP_ISLES_CONTRACTS,
            **WAVE8_LORDSHIP_ISLES_NONPROMOTIONS,
        }
        for candidate_id, row in exact_rows.items():
            self.assertEqual(
                canonical_hced_row_sha256(row),
                inventories[candidate_id]["raw_row_sha256"],
            )
            exact_sides = sum(
                normalize_label(row.get(field)) == EXACT_LABEL
                for field in ("side_1_raw", "side_2_raw")
            )
            self.assertEqual(exact_sides, 1)

        for candidate_id in sorted(WAVE8_LORDSHIP_ISLES_RESERVED_IDS):
            changed = copy.deepcopy(self.hced_rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "name"
            ] += " tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_lordship_isles_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Lochaber1429-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_lordship_isles_queue_contracts(missing)

        duplicated = [
            *self.hced_rows,
            copy.deepcopy(exact_rows["hced-Inverlochy1431-1"]),
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_lordship_isles_queue_contracts(duplicated)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureLordship1490-1",
                "side_1_raw": "Lordship of the Isles",
                "side_2_raw": "Unreviewed opponent",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            validate_wave8_lordship_isles_queue_contracts(future)

    def test_sources_parse_and_cover_archival_scholarly_and_primary_evidence(
        self,
    ) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
        self.assertEqual(len(source_by_id), 11)
        self.assertEqual(
            len(
                {
                    source["source_family_id"]
                    for source in WAVE8_LORDSHIP_ISLES_SOURCES
                }
            ),
            11,
        )
        publishers = " ".join(
            source["publisher"] for source in WAVE8_LORDSHIP_ISLES_SOURCES
        )
        self.assertIn("Historic Environment Scotland", publishers)
        self.assertIn("National Library of Scotland", publishers)
        self.assertIn("University of Glasgow", publishers)
        source_types = {
            source["source_type"] for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
        self.assertIn("official_battlefield_designation", source_types)
        self.assertIn("doctoral_dissertation", source_types)
        self.assertIn("digitized_early_modern_primary_narrative", source_types)
        self.assertIn("scholarly_calendar_of_primary_acts", source_types)
        for source in WAVE8_LORDSHIP_ISLES_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertEqual(source["accessed"], "2026-07-16")

    def test_entities_parse_and_never_open_dynastic_clan_or_crown_bridges(self) -> None:
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_LORDSHIP_ISLES_ENTITIES
        }
        self.assertEqual(
            set(entity_by_id),
            {
                ALEXANDER_REGIME,
                LOCHABER_ROYAL,
                INVERLOCHY_ISLANDS,
                INVERLOCHY_ROYAL,
                STRATHFLEET_SUTHERLAND,
                STRATHFLEET_ISLANDS,
            },
        )
        for entity in WAVE8_LORDSHIP_ISLES_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            note = entity["continuity_note"].casefold()
            for phrase in (
                "no rating is inherited",
                "clan",
                "dynasty",
                "coalition",
                "another campaign",
            ):
                self.assertIn(phrase, note)
            self.assertNotIn(
                entity["name"].casefold(),
                {
                    "lordship of the isles",
                    "clan donald",
                    "clan macdonald",
                    "scotland",
                    "scottish crown",
                    "earldom of sutherland",
                },
            )
        self.assertEqual(
            (
                entity_by_id[ALEXANDER_REGIME]["start_year"],
                entity_by_id[ALEXANDER_REGIME]["end_year"],
            ),
            (1423, 1449),
        )
        for entity_id, entity in entity_by_id.items():
            if entity_id != ALEXANDER_REGIME:
                self.assertEqual(entity["start_year"], entity["end_year"])

        island_names = " ".join(
            entity_by_id[entity_id]["name"]
            for entity_id in (
                ALEXANDER_REGIME,
                INVERLOCHY_ISLANDS,
                STRATHFLEET_ISLANDS,
            )
        )
        self.assertIn("regime", island_names)
        self.assertIn("coalition", island_names)
        self.assertIn("detachment", island_names)

    def test_installers_are_idempotent_copy_fixtures_and_reject_collisions(
        self,
    ) -> None:
        entities, sources, _ = self._installed()
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_LORDSHIP_ISLES_ENTITIES
        }
        source_by_id = {
            str(source["id"]): source for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
        install_wave8_lordship_isles_entities(entities)
        install_wave8_lordship_isles_sources(sources)
        for entity_id, fixture in entity_by_id.items():
            self.assertEqual(entities[entity_id], fixture)
            self.assertIsNot(entities[entity_id], fixture)
        for source_id, fixture in source_by_id.items():
            self.assertEqual(sources[source_id], fixture)
            self.assertIsNot(sources[source_id], fixture)

        installed_name = entities[ALEXANDER_REGIME]["name"]
        entities[ALEXANDER_REGIME]["name"] = "local mutation"
        self.assertNotEqual(
            entities[ALEXANDER_REGIME]["name"],
            entity_by_id[ALEXANDER_REGIME]["name"],
        )
        entities[ALEXANDER_REGIME]["name"] = installed_name

        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_lordship_isles_entities(
                {ALEXANDER_REGIME: {"id": ALEXANDER_REGIME, "name": "collision"}}
            )
        first_source_id = next(iter(source_by_id))
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_lordship_isles_sources(
                {first_source_id: {"id": first_source_id, "title": "collision"}}
            )

    def test_contracts_pin_dates_bounded_sides_and_source_attested_winners(
        self,
    ) -> None:
        expected = {
            "hced-Lochaber1429-1": (
                "Battle of Lochaber",
                "day",
                "23 June 1429",
                1429,
            ),
            "hced-Inverlochy1431-1": (
                "Battle of Inverlochy I",
                "month",
                "September 1431",
                1431,
            ),
            "hced-Strathfleet1453-1": (
                "Battle on the Sands of Strathfleet",
                "year",
                "1453 (exact day unresolved)",
                1453,
            ),
        }
        row_by_id = {str(row.get("candidate_id")): row for row in self.hced_rows}
        source_by_id = {
            str(source["id"]): source for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
        used_entities: set[str] = set()
        for candidate_id, contract in WAVE8_LORDSHIP_ISLES_CONTRACTS.items():
            canonical = contract["canonical_event"]
            name, precision, date_text, year = expected[candidate_id]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(
                (
                    canonical["date_precision"],
                    canonical["date_text"],
                    canonical["year_low"],
                    canonical["year_high"],
                ),
                (precision, date_text, year, year),
            )
            self.assertEqual(
                (
                    contract["disposition"],
                    contract["result_type"],
                    contract["winner_side"],
                    contract["actor_override"],
                ),
                ("promote", "win", 1, "bounded_exact_opposing_forces"),
            )
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertEqual(
                row_by_id[candidate_id]["winner_raw"],
                row_by_id[candidate_id]["side_1_raw"],
            )
            self.assertEqual(
                row_by_id[candidate_id]["loser_raw"],
                row_by_id[candidate_id]["side_2_raw"],
            )
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )
            used_entities.update(contract["side_1_entity_ids"])
            used_entities.update(contract["side_2_entity_ids"])
        self.assertEqual(
            used_entities,
            {str(entity["id"]) for entity in WAVE8_LORDSHIP_ISLES_ENTITIES},
        )
        self.assertFalse(WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES)

    def test_emission_rates_only_three_tactical_wins_with_exact_participants(
        self,
    ) -> None:
        events, entities, sources, _ = self._emit()
        self.assertEqual(len(events), 3)
        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            [
                "hced-Lochaber1429-1",
                "hced-Inverlochy1431-1",
                "hced-Strathfleet1453-1",
            ],
        )
        emitted_ids = {event["hced_candidate_id"] for event in events}
        self.assertEqual(emitted_ids, WAVE8_LORDSHIP_ISLES_CONTRACT_IDS)
        self.assertFalse(emitted_ids & WAVE8_LORDSHIP_ISLES_HOLD_IDS)
        self.assertFalse(emitted_ids & WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS)
        expected_aliases = {
            "hced-Lochaber1429-1": ["Lochaber"],
            "hced-Inverlochy1431-1": ["Inverlochy"],
            "hced-Strathfleet1453-1": ["Strathfleet"],
        }
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
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
                (winners, losers),
                EXPECTED_WINNERS_AND_LOSERS[candidate_id],
            )
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["aliases"], expected_aliases[candidate_id])
            self.assertNotIn("hced_dataset", event["outcome_source_ids"])
            self.assertLessEqual(set(event["outcome_source_ids"]), set(sources))
            self.assertTrue(
                all(
                    participant["entity_id"] in entities
                    for participant in event["participants"]
                )
            )
            self.assertIn("no generic label fallback", event["summary"])

    def test_harlaw_is_an_explicit_unknown_hold_never_a_draw(self) -> None:
        self.assertEqual(WAVE8_LORDSHIP_ISLES_HOLD_IDS, {"hced-Harlaw1411-1"})
        hold = WAVE8_LORDSHIP_ISLES_HOLDS["hced-Harlaw1411-1"]
        self.assertEqual(
            (hold["disposition"], hold["result_type"], hold["reviewed_outcome"]),
            ("hold", "unknown", "tactical_winner_not_source_attested"),
        )
        self.assertTrue(hold["unknown_is_never_draw"])
        reason = hold["hold_reason"].casefold()
        self.assertIn("inconclusive", reason)
        self.assertIn("both sides claimed victory", reason)
        self.assertIn("not promoted", reason)
        self.assertIn("never encoded as a draw", reason)
        actors = " ".join(hold["reviewed_actor_description"])
        self.assertIn("Donald", actors)
        self.assertIn("Earl of Mar", actors)
        self.assertIn("wave8_lordship_isles_hes_harlaw", hold["evidence_refs"])
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            self.assertNotIn(forbidden, hold)

    def test_bloody_bay_is_terminally_excluded_for_wrong_actors_and_year(self) -> None:
        self.assertIs(
            WAVE8_LORDSHIP_ISLES_EXCLUSIONS,
            WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS,
            {"hced-Bloody Bay1480-1"},
        )
        item = WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS[
            "hced-Bloody Bay1480-1"
        ]
        self.assertEqual(item["disposition"], "terminal_exclusion")
        self.assertEqual(item["result_type"], "unknown")
        self.assertTrue(item["unknown_is_never_draw"])
        self.assertEqual(item["canonical_event"]["year_low"], 1481)
        self.assertEqual(item["canonical_event"]["date_precision"], "circa_year")
        actors = " ".join(item["reviewed_actor_description"])
        self.assertIn("John II", actors)
        self.assertIn("Angus Og", actors)
        reason = item["hold_reason"].casefold()
        for phrase in (
            "early 1480s",
            "scottish crown",
            "unitary lordship",
            "both actor semantics",
            "terminally excluded",
            "drawn",
        ):
            self.assertIn(phrase, reason)
        row = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Bloody Bay1480-1"
        )
        self.assertEqual(
            (row["year_best"], row["winner_raw"]),
            (1480, "Scotland"),
        )
        self.assertNotIn("winner_side", item)
        self.assertNotIn("side_1_entity_ids", item)
        self.assertNotIn("side_2_entity_ids", item)

    def test_strathfleet_shared_label_is_owned_once_with_bounded_both_sides(
        self,
    ) -> None:
        disposition = WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS[
            "hced-Strathfleet1453-1"
        ]
        self.assertEqual(
            disposition["disposition"],
            "canonical_owner_here_for_shared_exact_row",
        )
        self.assertEqual(disposition["other_exact_label"], "earldom of sutherland")
        self.assertEqual(disposition["owner_module"], "wave8_lordship_isles")
        self.assertIn("must not emit a second event", disposition["reason"])
        row = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Strathfleet1453-1"
        )
        self.assertEqual(row["side_1_raw"], "Earldom of Sutherland")
        self.assertEqual(
            canonical_hced_row_sha256(row), disposition["raw_row_sha256"]
        )
        contract = WAVE8_LORDSHIP_ISLES_CONTRACTS["hced-Strathfleet1453-1"]
        self.assertEqual(contract["side_1_entity_ids"], [STRATHFLEET_SUTHERLAND])
        self.assertEqual(contract["side_2_entity_ids"], [STRATHFLEET_ISLANDS])
        self.assertNotIn("earldom of sutherland", contract["side_1_entity_ids"])
        self.assertNotIn("lordship of the isles", contract["side_2_entity_ids"])

    def test_dee_related_composite_is_not_split_or_bridged_backward(self) -> None:
        self.assertEqual(
            set(WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS),
            {"hced-Dee1308-1"},
        )
        item = WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS["hced-Dee1308-1"]
        row = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Dee1308-1"
        )
        self.assertEqual(
            row["side_2_raw"],
            "Galloway, Lordship of the Isles",
        )
        self.assertNotEqual(normalize_label(row["side_2_raw"]), EXACT_LABEL)
        self.assertEqual(canonical_hced_row_sha256(row), item["raw_row_sha256"])
        self.assertIsNone(item["owner_module"])
        self.assertTrue(item["unknown_is_never_draw"])
        reason = item["reason"].casefold()
        for phrase in (
            "1336",
            "internally inconsistent",
            "neither splits the composite",
            "dynastic",
            "clan bridge",
            "never a draw",
        ):
            self.assertIn(phrase, reason)
        self.assertNotIn("hced-Dee1308-1", WAVE8_LORDSHIP_ISLES_RESERVED_IDS)

    def test_location_reviews_and_quarantines_are_promoted_only_and_local(self) -> None:
        expected = frozenset(
            {
                "hced-Inverlochy1431-1",
                "hced-Lochaber1429-1",
                "hced-Strathfleet1453-1",
            }
        )
        self.assertEqual(
            wave8_lordship_isles_location_quarantine_additions(),
            {"country": frozenset(), "point": expected},
        )
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_LOCATION_QUARANTINE_ADDITIONS,
            {
                "country": WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS,
            WAVE8_LORDSHIP_ISLES_CONTRACT_IDS,
        )
        self.assertEqual(
            set(WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS),
            WAVE8_LORDSHIP_ISLES_CONTRACT_IDS,
        )
        self.assertFalse(
            set(WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS)
            & (
                WAVE8_LORDSHIP_ISLES_HOLD_IDS
                | WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS
            )
        )
        for review in WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS.values():
            self.assertTrue(review["point_disposition"].startswith("quarantine_"))
            self.assertEqual(review["country_disposition"], "retain_united_kingdom")
            self.assertGreaterEqual(len(review["evidence_refs"]), 2)

        events, _, _, _ = self._emit()
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United Kingdom")
            self.assertIn("location_provenance", event)
            Event.from_dict(event)

    def test_duplicate_dispositions_are_explicitly_empty_and_audit_is_complete(
        self,
    ) -> None:
        self.assertFalse(WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)
        self.assertEqual(
            set(WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_LORDSHIP_ISLES_RESERVED_IDS,
        )
        self.assertEqual(
            set(WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS),
            {
                "cross_lane:hced-Strathfleet1453-1",
                "related_hced:hced-Dee1308-1",
            },
        )
        for item in WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT.values():
            aliases = list(item["aliases"])
            self.assertEqual(aliases, sorted(set(aliases)))
            self.assertTrue(all(alias == normalize_label(alias) for alias in aliases))
            self.assertLessEqual(item["years"][0], item["years"][1])
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT[
                "hced-Bloody Bay1480-1"
            ]["years"],
            (1480, 1483),
        )

    def test_related_and_all_duplicate_surfaces_fail_closed(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_lordship_isles_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "related_hced_dispositions": 1,
            },
        )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row for row in changed if row.get("candidate_id") == "hced-Dee1308-1"
        )["name"] += " tampered"
        with self.assertRaisesRegex(ValueError, "related HCED fingerprint changed"):
            validate_wave8_lordship_isles_integration_dispositions(
                changed,
                self.iwbd_rows,
                existing,
            )

        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureFirstInverlochy1431-1",
                "name": "First Battle of Inverlochy",
                "year_best": 1431,
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_lordship_isles_integration_dispositions(
                future_hced,
                self.iwbd_rows,
                existing,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-bloody-bay",
                "name": "Battle of Bloody Bay",
                "start_date": "1482-01-01",
                "end_date": "1482-12-31",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_lordship_isles_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        future_release = [
            *existing,
            {
                "id": "future_strathfleet",
                "name": "Unrelated display name",
                "year": 1453,
                "end_year": 1453,
                "aliases": ["Sands of Strathfleet"],
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_lordship_isles_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

        ownership_collision = [
            *existing,
            {
                "id": "future_owned_candidate",
                "name": "Unrelated",
                "year": 1900,
                "hced_candidate_id": "hced-Harlaw1411-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidate ownership collision"):
            validate_wave8_lordship_isles_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                ownership_collision,
            )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        owned = {
            str(event.get("hced_candidate_id")): event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in WAVE8_LORDSHIP_ISLES_RESERVED_IDS
        }
        prefixed = [
            event
            for event in self.release_events
            if str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        self.assertFalse(
            set(owned)
            & (
                WAVE8_LORDSHIP_ISLES_HOLD_IDS
                | WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS
            ),
            "held or terminally excluded candidates must never reach the release",
        )
        if not owned and not prefixed:
            return
        self.assertEqual(set(owned), set(WAVE8_LORDSHIP_ISLES_CONTRACT_IDS))
        self.assertEqual(
            sorted(str(event["id"]) for event in prefixed),
            sorted(str(event["id"]) for event in owned.values()),
        )
        for event in owned.values():
            Event.from_dict(event)

    def test_promotion_rejects_candidate_name_and_identity_collisions(self) -> None:
        events, entities, _, existing = self._emit()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_lordship_isles_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        duplicate_name = {
            "id": "future_duplicate_name",
            "name": "Battle of Inverlochy I",
            "year": 1431,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_lordship_isles_contracts(
                self.hced_rows,
                entities,
                [*existing, duplicate_name],
            )

        duplicate_raw_name = {
            "id": "future_duplicate_raw_name",
            "name": "Strathfleet",
            "year": 1453,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_lordship_isles_contracts(
                self.hced_rows,
                entities,
                [*existing, duplicate_raw_name],
            )

        missing_entity = dict(entities)
        missing_entity.pop(INVERLOCHY_ISLANDS)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_lordship_isles_contracts(
                self.hced_rows,
                missing_entity,
                existing,
            )

        bad_window = copy.deepcopy(entities)
        bad_window[ALEXANDER_REGIME]["start_year"] = 1430
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_lordship_isles_contracts(
                self.hced_rows,
                bad_window,
                existing,
            )

    def test_every_source_and_new_entity_is_consumed_by_signed_metadata(self) -> None:
        used_sources: set[str] = set()
        used_entities: set[str] = set()
        for contract in WAVE8_LORDSHIP_ISLES_CONTRACTS.values():
            used_sources.update(contract["evidence_refs"])
            used_entities.update(contract["side_1_entity_ids"])
            used_entities.update(contract["side_2_entity_ids"])
        for item in WAVE8_LORDSHIP_ISLES_NONPROMOTIONS.values():
            used_sources.update(item["evidence_refs"])
        for item in WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS.values():
            used_sources.update(item["evidence_refs"])
        for item in WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS.values():
            used_sources.update(item["evidence_refs"])
        for entity in WAVE8_LORDSHIP_ISLES_ENTITIES:
            used_sources.update(entity["source_ids"])
        self.assertEqual(
            used_sources,
            {str(source["id"]) for source in WAVE8_LORDSHIP_ISLES_SOURCES},
        )
        self.assertEqual(
            used_entities,
            {str(entity["id"]) for entity in WAVE8_LORDSHIP_ISLES_ENTITIES},
        )
        self.assertEqual(
            WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS,
            {
                "hced-Bloody Bay1480-1": "terminal_exclusion",
                "hced-Harlaw1411-1": "hold",
                "hced-Inverlochy1431-1": "promote",
                "hced-Lochaber1429-1": "promote",
                "hced-Strathfleet1453-1": "promote",
            },
        )


if __name__ == "__main__":
    unittest.main()
