from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_uzbekistan import (
    WAVE8_UZBEKISTAN_CONTRACT_IDS,
    WAVE8_UZBEKISTAN_CONTRACTS,
    WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_UZBEKISTAN_ENTITIES,
    WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS,
    WAVE8_UZBEKISTAN_FINAL_AUDIT_SIGNATURE,
    WAVE8_UZBEKISTAN_FUNNEL_AUDIT,
    WAVE8_UZBEKISTAN_HOLD_IDS,
    WAVE8_UZBEKISTAN_HOLDS,
    WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS,
    WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS,
    WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_UZBEKISTAN_LOCATION_REVIEW,
    WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES,
    WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS,
    WAVE8_UZBEKISTAN_RESERVED_IDS,
    WAVE8_UZBEKISTAN_ROW_DISPOSITIONS,
    WAVE8_UZBEKISTAN_SOURCES,
    install_wave8_uzbekistan_entities,
    install_wave8_uzbekistan_sources,
    promote_wave8_uzbekistan_contracts,
    validate_wave8_uzbekistan_funnel,
    validate_wave8_uzbekistan_integration_dispositions,
    validate_wave8_uzbekistan_queue_contracts,
    wave8_uzbekistan_audit_signature,
    wave8_uzbekistan_cohort_counts,
    wave8_uzbekistan_counts,
    wave8_uzbekistan_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_uzbekistan_"

DAMGHAN_SAFAVID = "tahmasp_safavid_damghan_recapture_force_1528"
DAMGHAN_UZBEK = "uzbek_damghan_occupation_force_1528"
JAM_SAFAVID = "tahmasp_safavid_jam_relief_army_1528"
JAM_SHAYBANID = "ubaydallah_shaybanid_jam_army_1528"
RABAT_SAFAVID = "abbas_safavid_rebat_parian_army_1598"
RABAT_SHAYBANID = "din_muhammad_shaybanid_rebat_parian_army_1598"
PETNAK_AFSHARID = "nader_afsharid_petnak_campaign_army_1740"
PETNAK_KHIVAN = "ilbars_khivan_petnak_field_army_1740"


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Damghan1528-1": ({DAMGHAN_SAFAVID}, {DAMGHAN_UZBEK}),
    "hced-Khiva1740-1": ({PETNAK_AFSHARID}, {PETNAK_KHIVAN}),
    "hced-Rabat-i-Pariyan1598-1": ({RABAT_SAFAVID}, {RABAT_SHAYBANID}),
    "hced-Torbat-i-Jam1528-1": ({JAM_SAFAVID}, {JAM_SHAYBANID}),
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


class Wave8UzbekistanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_metadata = _json(ROOT / "data" / "release" / "metadata.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "wave8-funnel-current.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_UZBEKISTAN_RESERVED_IDS
        ]

    def _installed(self):
        entity_ids = {str(entity["id"]) for entity in WAVE8_UZBEKISTAN_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in entity_ids
        }
        install_wave8_uzbekistan_entities(entities)

        source_ids = {str(source["id"]) for source in WAVE8_UZBEKISTAN_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        install_wave8_uzbekistan_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_UZBEKISTAN_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_uzbekistan_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_UZBEKISTAN_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_UZBEKISTAN_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS
            ),
            "funnel_audit": WAVE8_UZBEKISTAN_FUNNEL_AUDIT,
            "holds": WAVE8_UZBEKISTAN_HOLDS,
            "integration_dispositions": WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS,
            "internal_relationship_dispositions": (
                WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS
            ),
            "iwbd_duplicate_dispositions": (
                WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT,
            "location_review": WAVE8_UZBEKISTAN_LOCATION_REVIEW,
            "outcome_overrides": WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS,
            "row_dispositions": WAVE8_UZBEKISTAN_ROW_DISPOSITIONS,
            "sources": WAVE8_UZBEKISTAN_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_UZBEKISTAN_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_uzbekistan_audit_signature(), independent)
        self.assertEqual(
            WAVE8_UZBEKISTAN_CONTRACT_IDS,
            frozenset(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(len(WAVE8_UZBEKISTAN_HOLD_IDS), 6)
        self.assertEqual(
            WAVE8_UZBEKISTAN_RESERVED_IDS,
            WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_uzbekistan_counts(),
            {
                "country_quarantine_additions": 1,
                "existing_release_duplicate_dispositions": 0,
                "holds": 6,
                "integration_dispositions": 4,
                "internal_relationship_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 10,
                "new_entities": 8,
                "new_sources": 15,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 3,
                "reviewed_hced_rows": 10,
                "sole_blocker_rows": 4,
            },
        )
        self.assertEqual(
            wave8_uzbekistan_cohort_counts(),
            {
                "afsharid_khwarazm_campaign_1740": 1,
                "safavid_reconquest_khorasan_1598": 1,
                "safavid_uzbek_khorasan_1528": 2,
            },
        )

    def test_authoritative_funnel_pins_ten_rows_and_four_sole_blockers(self) -> None:
        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": (
                        "46857510596b58250321ea401b73c39f1d4f643e7ac1635e6890e5dd5e7b40e4"
                    ),
                    "events_touched": 10,
                    "failure_cases": {"one_wrong_interval_candidate": 10},
                    "label": "uzbekistan",
                    "sole_blocker_events": 4,
                }
            ],
            "greedy_batch": {
                "ranking": [
                    {
                        "events_touched": 10,
                        "label": "uzbekistan",
                        "marginal_events": 4,
                        "newly_unblocked_candidate_id_sha256": (
                            "e77d2e5ab725775c715de98155e8c5186c2c6fa2064df2f8db50174477f7ca5a"
                        ),
                    }
                ]
            },
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "label_failures": [
                        {
                            "failure_case": "one_wrong_interval_candidate",
                            "label": "uzbekistan",
                        }
                    ],
                    "sole_blocker_label": (
                        "uzbekistan"
                        if candidate_id in WAVE8_UZBEKISTAN_CONTRACT_IDS
                        else None
                    ),
                }
                for candidate_id in sorted(WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS)
            ],
        }
        self.assertEqual(
            validate_wave8_uzbekistan_funnel(historical_funnel),
            {
                "exact_label_rows": 10,
                "held_other_identity_rows": 6,
                "sole_blocker_rows": 4,
            },
        )
        self.assertEqual(
            set(WAVE8_UZBEKISTAN_FUNNEL_AUDIT["sole_blocker_candidate_ids"]),
            WAVE8_UZBEKISTAN_CONTRACT_IDS,
        )
        self.assertEqual(
            set(
                WAVE8_UZBEKISTAN_FUNNEL_AUDIT[
                    "other_identity_blocker_candidate_ids"
                ]
            ),
            WAVE8_UZBEKISTAN_HOLD_IDS,
        )

        changed = copy.deepcopy(historical_funnel)
        label = next(item for item in changed["labels"] if item["label"] == "uzbekistan")
        label["sole_blocker_events"] = 5
        with self.assertRaisesRegex(ValueError, "sole_blocker_events changed"):
            validate_wave8_uzbekistan_funnel(changed)

        self.assertFalse(
            any(
                item.get("label") == "uzbekistan"
                for item in self.funnel.get("labels", [])
            ),
            "the completed Uzbekistan lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                item.get("label") == "uzbekistan"
                for item in self.funnel.get("greedy_batch", {}).get("ranking", [])
            ),
            "the completed Uzbekistan lane must not remain in the greedy batch",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id")) in WAVE8_UZBEKISTAN_CONTRACT_IDS
                or any(
                    failure.get("label") == "uzbekistan"
                    for failure in row.get("label_failures") or []
                )
                for row in self.funnel.get("row_label_data", [])
            ),
            "promoted Uzbekistan rows must not remain in the live funnel row data",
        )

    def test_complete_exact_queue_is_hash_pinned_and_drift_fails_closed(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Uzbekistan"
            or row.get("side_2_raw") == "Uzbekistan"
        }
        self.assertEqual(set(exact_rows), WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(len(self.lane_rows), 10)
        self.assertEqual(
            validate_wave8_uzbekistan_queue_contracts(self.hced_rows),
            {"promotion_contracts": 4, "holds": 6, "reviewed_hced_rows": 10},
        )
        inventories = {
            **WAVE8_UZBEKISTAN_CONTRACTS,
            **WAVE8_UZBEKISTAN_HOLDS,
        }
        for candidate_id, row in exact_rows.items():
            self.assertEqual(
                canonical_hced_row_sha256(row),
                inventories[candidate_id]["raw_row_sha256"],
            )

        for candidate_id in sorted(WAVE8_UZBEKISTAN_RESERVED_IDS):
            changed = copy.deepcopy(self.lane_rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "name"
            ] += " tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_uzbekistan_queue_contracts(changed)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Damghan1528-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_uzbekistan_queue_contracts(missing)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureUzbekistan1750-1",
                "side_1_raw": "Uzbekistan",
                "side_2_raw": "Unreviewed opponent",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Uzbekistan inventory changed"):
            validate_wave8_uzbekistan_queue_contracts(future)

    def test_sources_and_event_bounded_entities_parse_and_install(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_UZBEKISTAN_SOURCES
        }
        self.assertEqual(len(source_by_id), 15)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_UZBEKISTAN_SOURCES}),
            15,
        )
        for source in WAVE8_UZBEKISTAN_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_UZBEKISTAN_ENTITIES
        }
        self.assertEqual(
            set(entity_by_id),
            {
                DAMGHAN_SAFAVID,
                DAMGHAN_UZBEK,
                JAM_SAFAVID,
                JAM_SHAYBANID,
                RABAT_SAFAVID,
                RABAT_SHAYBANID,
                PETNAK_AFSHARID,
                PETNAK_KHIVAN,
            },
        )
        for entity in WAVE8_UZBEKISTAN_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertIn(entity["start_year"], {1528, 1598, 1740})
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern", note)
            self.assertIn("republic of uzbekistan", note)
            self.assertLessEqual(set(entity["source_ids"]), set(source_by_id))
            self.assertNotEqual(entity["name"].casefold(), "uzbekistan")

        entities, sources, _ = self._installed()
        install_wave8_uzbekistan_entities(entities)
        install_wave8_uzbekistan_sources(sources)
        for entity_id, entity in entity_by_id.items():
            self.assertEqual(entities[entity_id], entity)
        for source_id, source in source_by_id.items():
            self.assertEqual(sources[source_id], source)

    def test_all_six_nonsole_rows_are_explicit_unknown_not_draw_holds(self) -> None:
        self.assertEqual(
            WAVE8_UZBEKISTAN_HOLD_IDS,
            {
                "hced-Ghujduwan1512-1",
                "hced-Kandahar1508-1",
                "hced-Kul-i-Malik1512-1",
                "hced-Maruchak1507-1",
                "hced-Pul-i-Sanghin1511-1",
                "hced-Sar-i-Pul1501-1",
            },
        )
        for candidate_id, hold in WAVE8_UZBEKISTAN_HOLDS.items():
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertIn("not promoted", hold["hold_reason"].casefold())
            self.assertIn("draw", hold["hold_reason"].casefold())
            for forbidden in (
                "winner_side",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "outcome_source_ids",
                "outcome_source_family_ids",
            ):
                self.assertNotIn(forbidden, hold, candidate_id)

        kandahar = WAVE8_UZBEKISTAN_HOLDS["hced-Kandahar1508-1"]
        self.assertEqual(kandahar["reviewed_outcome"], "unknown")
        self.assertIn("1507", kandahar["canonical_event"]["date_text"])
        self.assertEqual(
            kandahar["hold_category"],
            "date_actor_and_outcome_conflict",
        )
        maruchak = WAVE8_UZBEKISTAN_HOLDS["hced-Maruchak1507-1"]
        self.assertEqual(maruchak["reviewed_outcome"], "unknown")
        self.assertEqual(
            maruchak["hold_category"],
            "unbounded_event_and_possible_campaign_overlap",
        )

    def test_promoted_dates_actors_outcomes_and_source_families_are_exact(self) -> None:
        expected_dates = {
            "hced-Damghan1528-1": ("year", "1528"),
            "hced-Khiva1740-1": ("year", "1740"),
            "hced-Rabat-i-Pariyan1598-1": ("month", "August 1598"),
            "hced-Torbat-i-Jam1528-1": (
                "year",
                "1528 (converted day varies across the cited scholarly chronologies)",
            ),
        }
        source_by_id = {
            str(source["id"]): source for source in WAVE8_UZBEKISTAN_SOURCES
        }
        for candidate_id, contract in WAVE8_UZBEKISTAN_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                expected_dates[candidate_id],
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(canonical["granularity"], "engagement")
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(
                (contract["disposition"], contract["result_type"], contract["winner_side"]),
                ("promote", "win", 1),
            )
            self.assertEqual(contract["war_type"], "interstate_limited")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["actor_override"],
                "bounded_exact_opposing_forces",
            )
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
        self.assertEqual(WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES, {})

    def test_emission_is_four_tactical_wins_without_a_modern_state_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertTrue(set(by_candidate).isdisjoint(WAVE8_UZBEKISTAN_HOLD_IDS))
        forbidden_ids = {
            "afsharid_iran",
            "mughal_empire",
            "safavid_empire",
            "uzbek",
            "uzbekistan",
            "republic_of_uzbekistan",
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
            self.assertEqual(
                (winners, losers),
                EXPECTED_WINNERS_AND_LOSERS[candidate_id],
            )
            self.assertTrue((winners | losers).isdisjoint(forbidden_ids))
            self.assertNotIn(
                "inconclusive_engagement",
                {participant["termination"] for participant in event["participants"]},
            )
            self.assertEqual(
                event["outcome_source_ids"],
                WAVE8_UZBEKISTAN_CONTRACTS[candidate_id]["outcome_source_ids"],
            )

    def test_location_quarantine_is_promoted_only_and_applied_locally(self) -> None:
        self.assertEqual(
            WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS,
            WAVE8_UZBEKISTAN_CONTRACT_IDS,
        )
        self.assertEqual(
            WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Rabat-i-Pariyan1598-1"},
        )
        self.assertTrue(
            WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS.isdisjoint(
                WAVE8_UZBEKISTAN_HOLD_IDS
            )
        )
        self.assertTrue(
            WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS.isdisjoint(
                WAVE8_UZBEKISTAN_HOLD_IDS
            )
        )
        self.assertEqual(
            wave8_uzbekistan_location_quarantine_additions(),
            {
                "country": WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS,
            },
        )
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        for event in events:
            self.assertNotIn("geometry", event)
        self.assertNotIn(
            "modern_location_country",
            by_candidate["hced-Rabat-i-Pariyan1598-1"],
        )
        self.assertNotIn(
            "location_provenance",
            by_candidate["hced-Rabat-i-Pariyan1598-1"],
        )
        self.assertEqual(
            by_candidate["hced-Damghan1528-1"]["modern_location_country"],
            "Iran",
        )
        self.assertEqual(
            by_candidate["hced-Torbat-i-Jam1528-1"]["modern_location_country"],
            "Iran",
        )
        self.assertEqual(
            by_candidate["hced-Khiva1740-1"]["modern_location_country"],
            "Uzbekistan",
        )

    def test_related_hced_and_duplicate_checks_fail_closed(self) -> None:
        self.assertEqual(WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_UZBEKISTAN_RESERVED_IDS,
        )
        self.assertEqual(
            set(WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS),
            {"hced-Charjui1740-1", "hced-Herat1507-1", "hced-Herat1528-1"},
        )
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_uzbekistan_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 4,
                "internal_relationship_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 10,
                "related_hced_dispositions": 3,
            },
        )

        future_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-jam",
                "name": "Battle of Jam",
                "start_date": "1528-09-01",
                "end_date": "1528-09-30",
            },
        ]
        with self.assertRaisesRegex(ValueError, "plausible IWBD overlap"):
            validate_wave8_uzbekistan_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        changed_hced = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed_hced
            if row["candidate_id"] == "hced-Herat1528-1"
        )["name"] += " tampered"
        with self.assertRaisesRegex(ValueError, "related HCED fingerprint changed"):
            validate_wave8_uzbekistan_integration_dispositions(
                changed_hced,
                self.iwbd_rows,
                existing,
            )

        future_release = [
            *existing,
            {
                "id": "future_petnak_duplicate",
                "name": "Battle near Petnak",
                "year": 1740,
                "end_year": 1740,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release overlap"):
            validate_wave8_uzbekistan_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_UZBEKISTAN_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        promotion = self.release_metadata.get("promotion", {})
        if "accepted_wave8_uzbekistan_hced_events" not in promotion:
            self.assertEqual(integrated, [])
            return
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            WAVE8_UZBEKISTAN_CONTRACT_IDS,
        )
        self.assertEqual(len(integrated), len(WAVE8_UZBEKISTAN_CONTRACT_IDS))
        self.assertEqual(
            len({str(event["id"]) for event in integrated}),
            len(WAVE8_UZBEKISTAN_CONTRACT_IDS),
        )
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in integrated)
        )
        for event in integrated:
            Event.from_dict(event)
        self.assertEqual(promotion["accepted_wave8_uzbekistan_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_uzbekistan_candidate_ids"],
            sorted(WAVE8_UZBEKISTAN_CONTRACT_IDS),
        )

    def test_internal_relationships_and_every_row_disposition_are_explicit(self) -> None:
        self.assertEqual(
            set(WAVE8_UZBEKISTAN_ROW_DISPOSITIONS),
            WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            {candidate_id for candidate_id, value in WAVE8_UZBEKISTAN_ROW_DISPOSITIONS.items() if value == "promote"},
            WAVE8_UZBEKISTAN_CONTRACT_IDS,
        )
        self.assertEqual(
            {candidate_id for candidate_id, value in WAVE8_UZBEKISTAN_ROW_DISPOSITIONS.items() if value == "hold"},
            WAVE8_UZBEKISTAN_HOLD_IDS,
        )
        relationship = WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS[
            "damghan_and_jam_1528"
        ]
        self.assertEqual(
            relationship["candidate_ids"],
            ["hced-Damghan1528-1", "hced-Torbat-i-Jam1528-1"],
        )
        self.assertEqual(
            relationship["disposition"],
            "distinct_actions_in_one_khorasan_campaign",
        )
        self.assertNotEqual(
            WAVE8_UZBEKISTAN_CONTRACTS["hced-Damghan1528-1"]["canonical_event"][
                "canonical_key"
            ],
            WAVE8_UZBEKISTAN_CONTRACTS["hced-Torbat-i-Jam1528-1"][
                "canonical_event"
            ]["canonical_key"],
        )

    def test_duplicate_and_entity_window_guards_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        collision = [
            *existing,
            {
                "id": "synthetic_duplicate",
                "name": "Battle near Petnak",
                "year": 1740,
            },
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_uzbekistan_contracts(
                self.hced_rows,
                entities,
                collision,
            )

        broken = copy.deepcopy(entities)
        broken[DAMGHAN_SAFAVID]["end_year"] = 1527
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_uzbekistan_contracts(
                self.hced_rows,
                broken,
                existing,
            )


if __name__ == "__main__":
    unittest.main()
