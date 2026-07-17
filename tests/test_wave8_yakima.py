import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_yakima as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_yakima_"

TOPPENISH_INDIGENOUS_ID = (
    "kamiakin_yakama_palouse_coalition_toppenish_creek_1855"
)
TOPPENISH_US_ID = "haller_fourth_infantry_column_toppenish_creek_1855"
UNION_GAP_US_ID = "rains_regular_volunteer_force_union_gap_1855"
UNION_GAP_INDIGENOUS_ID = (
    "kamiakin_yakama_allied_defenders_union_gap_1855"
)


EXPECTED_RAW_ROWS = {
    "hced-Grande Ronde Valley1856-1": {
        "name": "Grande Ronde Valley",
        "side_1_raw": "United States",
        "side_2_raw": "Yakima Indians",
        "winner_raw": "United States",
        "loser_raw": "Yakima Indians",
        "year": 1856,
        "massacre_raw": "Yes",
    },
    "hced-Satus1856-1": {
        "name": "Satus",
        "side_1_raw": "Yakima Indians",
        "side_2_raw": "United States",
        "winner_raw": "Yakima Indians",
        "loser_raw": "United States",
        "year": 1856,
        "massacre_raw": "No",
    },
    "hced-Toppenish1855-1": {
        "name": "Toppenish",
        "side_1_raw": "Yakima Indians",
        "side_2_raw": "United States",
        "winner_raw": "Yakima Indians",
        "loser_raw": "United States",
        "year": 1855,
        "massacre_raw": "No",
    },
    "hced-Union Gap1855-1": {
        "name": "Union Gap",
        "side_1_raw": "United States",
        "side_2_raw": "Yakima Indians",
        "winner_raw": "United States",
        "loser_raw": "Yakima Indians",
        "year": 1855,
        "massacre_raw": "No",
    },
}


EXPECTED_ADJACENT_ROWS = {
    "hced-Cascades1856-1": {
        "name": "Cascades",
        "side_1_raw": "Yakima, Klikitat, Chinook",
        "side_2_raw": "United States",
        "year": 1856,
    },
    "hced-Four Lakes1858-1": {
        "name": "Four Lakes",
        "side_1_raw": "United States",
        "side_2_raw": "Coer d'Alanes Indians, Spokane Indians, Palouses Indians",
        "year": 1858,
    },
    "hced-Pine Creek1858-1": {
        "name": "Pine Creek",
        "side_1_raw": "Coer d'Alane Indians, Spokane Indians, Palouse Indians",
        "side_2_raw": "United States",
        "year": 1858,
    },
    "hced-Spokane Plain1858-1": {
        "name": "Spokane Plain",
        "side_1_raw": "United States",
        "side_2_raw": (
            "Coeur d'Alane Indians, Spokane Indians, Yakima Indians, "
            "Palouse Indians"
        ),
        "year": 1858,
    },
}


EXPECTED_PROMOTIONS = {
    "hced-Toppenish1855-1": {
        "name": "Battle of Toppenish Creek (Haller's Defeat)",
        "date_text": "5-8 October 1855",
        "date_precision": "day_range",
        "granularity": "multi_day_battle_and_fighting_retreat",
        "winner": {TOPPENISH_INDIGENOUS_ID},
        "loser": {TOPPENISH_US_ID},
        "confidence": 0.96,
    },
    "hced-Union Gap1855-1": {
        "name": "Battle of Union Gap (Two Buttes)",
        "date_text": "9-10 November 1855",
        "date_precision": "day_range",
        "granularity": "two_day_breastwork_assault_and_field_withdrawal",
        "winner": {UNION_GAP_US_ID},
        "loser": {UNION_GAP_INDIGENOUS_ID},
        "confidence": 0.82,
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sorted_newline_sha256(values) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _dicts(value):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _dicts(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _dicts(nested)


class Wave8YakimaTests(unittest.TestCase):
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
        cls.exact_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in lane.WAVE8_YAKIMA_RESERVED_IDS
        }
        cls.adjacent_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in lane.WAVE8_YAKIMA_ADJACENT_ROW_HASHES
        }

    def _installed(self):
        new_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_YAKIMA_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        lane.install_wave8_yakima_entities(entities)

        new_source_ids = {
            str(source["id"]) for source in lane.WAVE8_YAKIMA_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        lane.install_wave8_yakima_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_YAKIMA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self) -> list[dict]:
        entities, _, existing = self._installed()
        return lane.promote_wave8_yakima_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_public_api_exports_lane_contract(self) -> None:
        required = {
            "WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS",
            "WAVE8_YAKIMA_CONTRACTS",
            "WAVE8_YAKIMA_ENTITIES",
            "WAVE8_YAKIMA_FINAL_AUDIT_SIGNATURE",
            "WAVE8_YAKIMA_HOLDS",
            "WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS",
            "WAVE8_YAKIMA_LOCATION_QUARANTINE_ADDITIONS",
            "WAVE8_YAKIMA_SOURCES",
            "WAVE8_YAKIMA_TERMINAL_EXCLUSIONS",
            "install_wave8_yakima_entities",
            "install_wave8_yakima_sources",
            "promote_wave8_yakima_contracts",
            "validate_wave8_yakima_integration_dispositions",
            "validate_wave8_yakima_queue_contracts",
            "wave8_yakima_audit_signature",
            "wave8_yakima_cohort_counts",
            "wave8_yakima_counts",
            "wave8_yakima_location_quarantine_additions",
        }
        self.assertTrue(required <= set(lane.__all__))
        self.assertTrue(all(hasattr(lane, name) for name in lane.__all__))
        self.assertFalse(any(name.startswith("_") for name in lane.__all__))

    def test_locked_queue_file_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_YAKIMA_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_YAKIMA_IWBD_QUEUE_SHA256,
        )

    def test_candidate_id_digests_cover_exact_and_complete_war_family(self) -> None:
        self.assertEqual(
            _sorted_newline_sha256(lane.WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS),
            lane.WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(
            lane.WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
            lane.WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(
            _sorted_newline_sha256(lane.WAVE8_YAKIMA_WAR_CANDIDATE_IDS),
            lane.WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256,
        )

    def test_unresolved_funnel_entry_and_four_rows_are_pinned(self) -> None:
        historical_funnel = {
            "labels": [
                {
                    "candidate_ids": [],
                    "centuries": {"CE_19": 4},
                    "event_candidate_id_sha256": (
                        "65081d0328a98785942285646c7fccc6738acd1239"
                        "f6acaa759337dc143a7519"
                    ),
                    "events_touched": 4,
                    "failure_cases": {
                        "multiple_time_valid_candidates": 0,
                        "one_wrong_interval_candidate": 0,
                        "policy_denied_window": 0,
                        "resolver_guard_or_tier_conflict": 0,
                        "zero_time_valid_candidates": 4,
                    },
                    "label": "yakima indians",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 4,
                }
            ],
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "sole_blocker_label": "yakima indians",
                }
                for candidate_id in sorted(EXPECTED_RAW_ROWS)
            ],
        }
        summaries = [
            item
            for item in _dicts(historical_funnel)
            if item.get("label") == "yakima indians"
            and "unresolved_side_attempts" in item
        ]
        self.assertEqual(len(summaries), 1)
        summary = summaries[0]
        self.assertEqual(summary["events_touched"], 4)
        self.assertEqual(summary["sole_blocker_events"], 4)
        self.assertEqual(summary["unresolved_side_attempts"], 4)
        self.assertEqual(summary["centuries"], {"CE_19": 4})
        self.assertEqual(
            summary["failure_cases"],
            {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": 4,
            },
        )
        self.assertEqual(
            summary["event_candidate_id_sha256"],
            lane.WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        funnel_rows = {
            str(item["candidate_id"])
            for item in _dicts(historical_funnel)
            if item.get("sole_blocker_label") == "yakima indians"
        }
        self.assertEqual(funnel_rows, lane.WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(
            _sorted_newline_sha256(funnel_rows),
            lane.WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        self.assertFalse(
            any(
                item.get("label") == "yakima indians"
                for item in _dicts(self.funnel)
            ),
            "the completed Yakima Indians lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                item.get("sole_blocker_label") == "yakima indians"
                or str(item.get("candidate_id"))
                in lane.WAVE8_YAKIMA_RESERVED_IDS
                for item in _dicts(self.funnel)
            ),
            "reviewed Yakima Indians rows must be absent from the live funnel",
        )

    def test_complete_exact_label_inventory_is_four_rows(self) -> None:
        exact_ids = {
            str(row.get("candidate_id"))
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "yakima indians"
            or normalize_label(row.get("side_2_raw")) == "yakima indians"
        }
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, lane.WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(len(exact_ids), 4)

    def test_every_exact_raw_field_and_fingerprint_is_pinned(self) -> None:
        self.assertEqual(set(self.exact_rows), set(EXPECTED_RAW_ROWS))
        self.assertEqual(set(lane.WAVE8_YAKIMA_ROW_HASHES), set(EXPECTED_RAW_ROWS))
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = self.exact_rows[candidate_id]
                for field in (
                    "name",
                    "side_1_raw",
                    "side_2_raw",
                    "winner_raw",
                    "loser_raw",
                    "massacre_raw",
                ):
                    self.assertEqual(row[field], expected[field])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(row["year_low"], expected["year"])
                self.assertEqual(row["year_high"], expected["year"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    lane.WAVE8_YAKIMA_ROW_HASHES[candidate_id],
                )

    def test_disposition_partition_is_complete_disjoint_and_owned(self) -> None:
        self.assertEqual(
            lane.WAVE8_YAKIMA_CONTRACT_IDS,
            {"hced-Toppenish1855-1", "hced-Union Gap1855-1"},
        )
        self.assertEqual(lane.WAVE8_YAKIMA_HOLD_IDS, {"hced-Satus1856-1"})
        self.assertEqual(
            lane.WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
            {"hced-Grande Ronde Valley1856-1"},
        )
        partitions = (
            lane.WAVE8_YAKIMA_CONTRACT_IDS,
            lane.WAVE8_YAKIMA_HOLD_IDS,
            lane.WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
        )
        for index, values in enumerate(partitions):
            for other in partitions[index + 1 :]:
                self.assertFalse(values & other)
        self.assertEqual(
            set().union(*partitions),
            lane.WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            set(lane.WAVE8_YAKIMA_NONPROMOTIONS),
            lane.WAVE8_YAKIMA_HOLD_IDS
            | lane.WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(
            lane.WAVE8_YAKIMA_EXCLUSIONS,
            lane.WAVE8_YAKIMA_TERMINAL_EXCLUSIONS,
        )

    def test_complete_yakima_war_family_and_adjacent_boundaries_are_pinned(
        self,
    ) -> None:
        war_ids = {
            str(row.get("candidate_id"))
            for row in self.hced_rows
            if any(
                normalize_label(name) in {"yakima war", "yakima indian wars"}
                for name in row.get("war_names", [])
            )
        }
        self.assertEqual(war_ids, lane.WAVE8_YAKIMA_WAR_CANDIDATE_IDS)
        self.assertEqual(len(war_ids), 8)
        self.assertEqual(set(self.adjacent_rows), set(EXPECTED_ADJACENT_ROWS))
        self.assertEqual(
            set(lane.WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS),
            set(EXPECTED_ADJACENT_ROWS),
        )
        for candidate_id, expected in EXPECTED_ADJACENT_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = self.adjacent_rows[candidate_id]
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1_raw"])
                self.assertEqual(row["side_2_raw"], expected["side_2_raw"])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    lane.WAVE8_YAKIMA_ADJACENT_ROW_HASHES[candidate_id],
                )
                disposition = lane.WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS[
                    candidate_id
                ]
                self.assertEqual(
                    disposition["disposition"],
                    "distinct_composite_coalition_event",
                )
                self.assertIn("separate", disposition["owner_scope"])

    def test_complete_audit_signature_is_independently_reproducible(self) -> None:
        payload = {
            "adjacent_hced_dispositions": (
                lane.WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS
            ),
            "adjacent_row_hashes": lane.WAVE8_YAKIMA_ADJACENT_ROW_HASHES,
            "contracts": lane.WAVE8_YAKIMA_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS,
            "entities": lane.WAVE8_YAKIMA_ENTITIES,
            "exact_candidate_id_sha256": (
                lane.WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256
            ),
            "funnel_event_candidate_id_sha256": (
                lane.WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256
            ),
            "existing_release_duplicate_dispositions": (
                lane.WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                lane.WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS
            ),
            "hced_queue_sha256": lane.WAVE8_YAKIMA_HCED_QUEUE_SHA256,
            "holds": lane.WAVE8_YAKIMA_HOLDS,
            "integration_dispositions": (
                lane.WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS
            ),
            "iwbd_duplicate_dispositions": (
                lane.WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_queue_sha256": lane.WAVE8_YAKIMA_IWBD_QUEUE_SHA256,
            "iwbd_zero_overlap_audit": (
                lane.WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT
            ),
            "location_quarantine_reasons": (
                lane.WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": lane.WAVE8_YAKIMA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                lane.WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS
            ),
            "row_hashes": lane.WAVE8_YAKIMA_ROW_HASHES,
            "sources": lane.WAVE8_YAKIMA_SOURCES,
            "terminal_exclusions": lane.WAVE8_YAKIMA_TERMINAL_EXCLUSIONS,
            "war_candidate_id_sha256": (
                lane.WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256
            ),
            "war_candidate_ids": sorted(lane.WAVE8_YAKIMA_WAR_CANDIDATE_IDS),
        }
        measured = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(measured, lane.WAVE8_YAKIMA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, lane.wave8_yakima_audit_signature())
        self.assertEqual(len(measured), 64)

    def test_counts_and_cohort_are_exact(self) -> None:
        self.assertEqual(
            lane.wave8_yakima_counts(),
            {
                "adjacent_hced_dispositions": 4,
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 3,
                "existing_release_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 7,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 4,
                "new_sources": 16,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
                "yakima_war_rows_audited": 8,
            },
        )
        self.assertEqual(
            lane.wave8_yakima_cohort_counts(),
            {"yakama_war_1855_1856": 4},
        )

    def test_sources_parse_are_independent_and_span_authoritative_types(self) -> None:
        ids = [str(source["id"]) for source in lane.WAVE8_YAKIMA_SOURCES]
        families = [
            str(source["source_family_id"])
            for source in lane.WAVE8_YAKIMA_SOURCES
        ]
        self.assertEqual(len(ids), 16)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(families), len(set(families)))
        source_types = {
            str(source["source_type"])
            for source in lane.WAVE8_YAKIMA_SOURCES
        }
        publishers = {
            str(source["publisher"])
            for source in lane.WAVE8_YAKIMA_SOURCES
        }
        for fixture in lane.WAVE8_YAKIMA_SOURCES:
            parsed = Source.from_dict(fixture)
            self.assertEqual(parsed.id, fixture["id"])
            self.assertTrue(fixture["url"].startswith("https://"))
            self.assertEqual(fixture["accessed"], "2026-07-16")
            self.assertEqual(
                fixture["evidence_roles"],
                sorted(set(fixture["evidence_roles"])),
            )
        self.assertTrue(any("dissertation" in value for value in source_types))
        self.assertTrue(any("participant" in value for value in source_types))
        self.assertTrue(any("archival" in value for value in source_types))
        self.assertTrue(any("federal" in value for value in source_types))
        self.assertIn("University of Oregon", publishers)
        self.assertIn("U.S. National Archives and Records Administration", publishers)
        self.assertIn("Washington State Parks", publishers)

    def test_every_source_is_consumed_by_a_signed_audit_decision(self) -> None:
        used: set[str] = set()
        for entity in lane.WAVE8_YAKIMA_ENTITIES:
            used.update(map(str, entity["source_ids"]))
        for contract in lane.WAVE8_YAKIMA_CONTRACTS.values():
            used.update(map(str, contract["evidence_refs"]))
        for item in lane.WAVE8_YAKIMA_NONPROMOTIONS.values():
            used.update(map(str, item["evidence_refs"]))
        for item in lane.WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS.values():
            used.update(map(str, item["evidence_refs"]))
        for item in lane.WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS.values():
            used.update(map(str, item["evidence_refs"]))
        for item in lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS.values():
            used.update(map(str, item["evidence_refs"]))
        self.assertEqual(
            used,
            {str(source["id"]) for source in lane.WAVE8_YAKIMA_SOURCES},
        )

    def test_entities_are_event_bounded_and_open_no_generic_rating_bridge(self) -> None:
        entity_ids = [str(entity["id"]) for entity in lane.WAVE8_YAKIMA_ENTITIES]
        self.assertEqual(len(entity_ids), 4)
        self.assertEqual(len(entity_ids), len(set(entity_ids)))
        forbidden_ids = {
            "yakama",
            "yakama_nation",
            "yakima",
            "yakima_indians",
            "united_states",
            "us_antebellum",
            "us_army",
        }
        forbidden_names = {
            "palouse",
            "united states",
            "yakama",
            "yakama nation",
            "yakima",
            "yakima indians",
        }
        self.assertFalse(set(entity_ids) & forbidden_ids)
        for fixture in lane.WAVE8_YAKIMA_ENTITIES:
            parsed = Entity.from_dict(fixture)
            self.assertEqual(parsed.start_year, 1855)
            self.assertEqual(parsed.end_year, 1855)
            self.assertEqual(parsed.aliases, ())
            self.assertEqual(parsed.predecessors, ())
            self.assertNotIn(normalize_label(parsed.name), forbidden_names)
            note = parsed.continuity_note.casefold()
            self.assertIn("only for the named 1855 event", note)
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern yakama nation", note)
            self.assertIn("united states", note)
            self.assertIn("noncombatants", note)

    def test_contracts_pin_event_dates_actors_outcomes_and_corroboration(self) -> None:
        entities = {str(entity["id"]) for entity in lane.WAVE8_YAKIMA_ENTITIES}
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_YAKIMA_SOURCES
        }
        consumed: set[str] = set()
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = lane.WAVE8_YAKIMA_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(canonical["year_low"], 1855)
            self.assertEqual(canonical["year_high"], 1855)
            self.assertEqual(canonical["date_text"], expected["date_text"])
            self.assertEqual(
                canonical["date_precision"], expected["date_precision"]
            )
            self.assertEqual(canonical["granularity"], expected["granularity"])
            self.assertEqual(set(contract["side_1_entity_ids"]), expected["winner"])
            self.assertEqual(set(contract["side_2_entity_ids"]), expected["loser"])
            self.assertFalse(expected["winner"] & expected["loser"])
            consumed.update(expected["winner"] | expected["loser"])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["confidence"], expected["confidence"])
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertIs(contract["actor_override"], True)
            row = self.exact_rows[candidate_id]
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
            outcomes = list(contract["outcome_source_ids"])
            families = list(contract["outcome_source_family_ids"])
            self.assertGreaterEqual(len(outcomes), 3)
            self.assertEqual(outcomes, sorted(set(outcomes)))
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in outcomes
                )
            )
            self.assertEqual(
                families,
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in outcomes
                    }
                ),
            )
            self.assertGreaterEqual(len(families), 3)
        self.assertEqual(consumed, entities)
        self.assertEqual(lane.WAVE8_YAKIMA_OUTCOME_OVERRIDES, {})

    def test_toppenish_is_bounded_yakama_palouse_victory(self) -> None:
        contract = lane.WAVE8_YAKIMA_CONTRACTS["hced-Toppenish1855-1"]
        self.assertEqual(
            contract["side_1_entity_ids"],
            [TOPPENISH_INDIGENOUS_ID],
        )
        self.assertEqual(contract["side_2_entity_ids"], [TOPPENISH_US_ID])
        note = contract["audit_note"].casefold()
        self.assertIn("yakama and palouse", note)
        self.assertIn("forced its retreat", note)
        self.assertIn("howitzer", note)
        self.assertIn("bounded battle", note)
        entity = next(
            item
            for item in lane.WAVE8_YAKIMA_ENTITIES
            if item["id"] == TOPPENISH_INDIGENOUS_ID
        )
        self.assertIn("kamiakin", entity["name"].casefold())
        self.assertIn("yakama-palouse", entity["name"].casefold())

    def test_union_gap_is_tactical_displacement_not_strategic_victory(self) -> None:
        union = lane.WAVE8_YAKIMA_CONTRACTS["hced-Union Gap1855-1"]
        toppenish = lane.WAVE8_YAKIMA_CONTRACTS["hced-Toppenish1855-1"]
        self.assertLess(union["confidence"], toppenish["confidence"])
        self.assertEqual(union["side_1_entity_ids"], [UNION_GAP_US_ID])
        self.assertEqual(
            union["side_2_entity_ids"],
            [UNION_GAP_INDIGENOUS_ID],
        )
        note = union["audit_note"].casefold()
        self.assertIn("dislodge", note)
        self.assertIn("tactical displacement only", note)
        self.assertIn("failed to suppress", note)
        self.assertIn("no strategic victory", note)

    def test_satus_stays_unknown_and_is_never_converted_to_draw(self) -> None:
        item = lane.WAVE8_YAKIMA_HOLDS["hced-Satus1856-1"]
        self.assertEqual(item["disposition"], "hold")
        self.assertIs(item["terminal_exclusion"], False)
        self.assertEqual(item["reviewed_outcome"], "unknown")
        self.assertIs(item["unknown_is_never_draw"], True)
        self.assertEqual(
            item["hold_category"],
            "outcome_not_uniquely_defensible",
        )
        review = item["historical_review"]
        self.assertIn("Yakama and Klickitat", review["attested_indigenous_side"])
        self.assertEqual(review["whole_event_winner"], "not uniquely defensible")
        self.assertIn("ambushed", item["hold_reason"])
        self.assertIn("counterattacked", item["hold_reason"])
        self.assertIn("unknown is never a draw", item["hold_reason"].casefold())
        forbidden = {
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        self.assertFalse(forbidden & set(item))

    def test_grande_ronde_is_wrong_actor_civilian_massacre_exclusion(self) -> None:
        item = lane.WAVE8_YAKIMA_TERMINAL_EXCLUSIONS[
            "hced-Grande Ronde Valley1856-1"
        ]
        self.assertEqual(item["disposition"], "terminal_exclusion")
        self.assertIs(item["terminal_exclusion"], True)
        self.assertEqual(
            item["reviewed_outcome"],
            "not_rateable_wrong_actor_massacre",
        )
        self.assertEqual(
            item["hold_category"],
            "wrong_actor_and_noncompetitive_civilian_massacre",
        )
        review = item["historical_review"]
        self.assertEqual(review["raw_opposing_label"], "Yakima Indians")
        self.assertEqual(
            review["attested_communities"],
            ["Cayuse families", "Umatilla families", "Walla Walla families"],
        )
        self.assertIs(review["competitive_event"], False)
        self.assertIn("rate civilian victims", review["repair_risk"])
        self.assertEqual(
            self.exact_rows["hced-Grande Ronde Valley1856-1"]["massacre_raw"],
            "Yes",
        )
        forbidden = {
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        self.assertFalse(forbidden & set(item))

    def test_queue_validator_reports_two_one_one(self) -> None:
        self.assertEqual(
            lane.validate_wave8_yakima_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )

    def test_queue_validator_fails_on_each_exact_raw_row_tamper(self) -> None:
        for candidate_id in sorted(lane.WAVE8_YAKIMA_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.hced_rows)
                row = next(
                    item
                    for item in changed
                    if item.get("candidate_id") == candidate_id
                )
                row["participants_raw"] = [
                    *row.get("participants_raw", []),
                    "audit drift",
                ]
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    lane.validate_wave8_yakima_queue_contracts(changed)

    def test_queue_validator_fails_on_missing_duplicate_or_future_exact_row(
        self,
    ) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Satus1856-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_yakima_queue_contracts(missing)

        duplicate = copy.deepcopy(self.hced_rows)
        duplicate.append(copy.deepcopy(self.exact_rows["hced-Toppenish1855-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_yakima_queue_contracts(duplicate)

        future = copy.deepcopy(self.hced_rows)
        added = copy.deepcopy(self.exact_rows["hced-Toppenish1855-1"])
        added.update(
            {
                "candidate_id": "hced-Future Yakima1900-1",
                "name": "Future Yakima",
                "source_record_id": "Future Yakima1900",
                "source_row": 999999,
                "side_1_raw": "YAKIMA INDIANS",
                "side_2_raw": "Future opponent",
                "winner_raw": "YAKIMA INDIANS",
                "loser_raw": "Future opponent",
                "year_best": 1900,
                "year_low": 1900,
                "year_high": 1900,
                "war_names": [],
            }
        )
        future.append(added)
        with self.assertRaisesRegex(ValueError, "exact Yakima Indians inventory"):
            lane.validate_wave8_yakima_queue_contracts(future)

    def test_unrelated_nonfamily_row_does_not_change_exact_inventory(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        rows.append(
            {
                "candidate_id": "hced-Unrelated1900-1",
                "name": "Unrelated",
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
                "year_low": 1900,
                "year_high": 1900,
                "war_names": [],
            }
        )
        self.assertEqual(
            lane.validate_wave8_yakima_queue_contracts(rows)[
                "reviewed_hced_rows"
            ],
            4,
        )

    def test_integration_validator_pins_current_war_and_duplicate_inventory(
        self,
    ) -> None:
        release_overlap = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_YAKIMA_CONTRACT_IDS
        }
        self.assertIn(
            release_overlap,
            (set(), set(lane.WAVE8_YAKIMA_CONTRACT_IDS)),
        )
        result = lane.validate_wave8_yakima_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(
            result,
            {
                "adjacent_hced_dispositions": 4,
                "cross_lane_hced_dispositions": 3,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 7,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
                "release_overlap": len(release_overlap),
                "yakima_war_rows_audited": 8,
            },
        )

    def test_integration_validator_fails_on_adjacent_drift_missing_or_new_family_row(
        self,
    ) -> None:
        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row.get("candidate_id") == "hced-Cascades1856-1"
        )["participants_raw"].append("drift")
        with self.assertRaisesRegex(ValueError, "adjacent HCED fingerprint"):
            lane.validate_wave8_yakima_integration_dispositions(
                changed,
                self.iwbd_rows,
            )

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Four Lakes1858-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected one adjacent HCED row"):
            lane.validate_wave8_yakima_integration_dispositions(
                missing,
                self.iwbd_rows,
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-Future Yakima War1860-1",
                "name": "Future distinct family event",
                "side_1_raw": "Different coalition",
                "side_2_raw": "Different opponent",
                "year_low": 1860,
                "year_high": 1860,
                "war_names": ["Yakima War"],
            }
        )
        with self.assertRaisesRegex(ValueError, "Yakima War inventory changed"):
            lane.validate_wave8_yakima_integration_dispositions(
                future,
                self.iwbd_rows,
            )

    def test_duplicate_alias_audit_is_complete_canonical_and_currently_empty(
        self,
    ) -> None:
        self.assertEqual(lane.WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(
            set(lane.WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_YAKIMA_RESERVED_IDS,
        )
        audited_pairs: set[tuple[int, str]] = set()
        for candidate_id, item in lane.WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT.items():
            aliases = list(item["aliases"])
            years = list(item["years"])
            self.assertEqual(aliases, sorted(set(aliases)))
            self.assertTrue(
                all(alias == normalize_label(alias) for alias in aliases)
            )
            self.assertEqual(years, sorted(set(years)))
            audited_pairs.update(
                (year, alias) for year in years for alias in aliases
            )
            audited = lane.WAVE8_YAKIMA_CONTRACTS.get(candidate_id) or (
                lane.WAVE8_YAKIMA_NONPROMOTIONS[candidate_id]
            )
            canonical = audited["canonical_event"]
            self.assertIn(
                (
                    canonical["year_low"],
                    normalize_label(canonical["name"]),
                ),
                audited_pairs,
            )

    def test_integration_validator_rejects_future_hced_iwbd_and_release_twins(
        self,
    ) -> None:
        hced = copy.deepcopy(self.hced_rows)
        hced.append(
            {
                "candidate_id": "hced-Future Haller Twin1855-1",
                "name": "Haller's Defeat",
                "side_1_raw": "Different A",
                "side_2_raw": "Different B",
                "year_low": 1855,
                "year_high": 1855,
                "war_names": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_yakima_integration_dispositions(
                hced,
                self.iwbd_rows,
            )

        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-future-two-buttes",
                "name": "Battle of Two Buttes",
                "start_date": "1855-11-09",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_yakima_integration_dispositions(
                self.hced_rows,
                iwbd,
            )

        for event in (
            {"id": "future-name", "name": "Haller's Defeat", "year": 1855},
            {
                "id": "future-alias",
                "name": "Different title",
                "aliases": ["Pah-Qy-Ti-Koot"],
                "year": 1855,
            },
        ):
            with self.subTest(event=event["id"]):
                with self.assertRaisesRegex(ValueError, "existing-release twin"):
                    lane.validate_wave8_yakima_integration_dispositions(
                        self.hced_rows,
                        self.iwbd_rows,
                        [event],
                    )

    def test_release_candidate_overlap_is_all_or_none(self) -> None:
        partial = [
            {
                "id": "existing-toppenish",
                "name": "Different title",
                "year": 1855,
                "hced_candidate_id": "hced-Toppenish1855-1",
            }
        ]
        with self.assertRaisesRegex(ValueError, "partial release overlap"):
            lane.validate_wave8_yakima_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                partial,
            )

        full = [
            {
                "id": f"existing-{index}",
                "name": "Different title",
                "year": 1855,
                "hced_candidate_id": candidate_id,
            }
            for index, candidate_id in enumerate(
                sorted(lane.WAVE8_YAKIMA_CONTRACT_IDS),
                start=1,
            )
        ]
        self.assertEqual(
            lane.validate_wave8_yakima_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                full,
            )["release_overlap"],
            2,
        )

    def test_installers_are_idempotent_deep_copy_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        lane.install_wave8_yakima_entities(entities)
        first_entities = copy.deepcopy(entities)
        lane.install_wave8_yakima_entities(entities)
        self.assertEqual(entities, first_entities)

        sources: dict[str, dict] = {}
        lane.install_wave8_yakima_sources(sources)
        first_sources = copy.deepcopy(sources)
        lane.install_wave8_yakima_sources(sources)
        self.assertEqual(sources, first_sources)

        entity_id = str(lane.WAVE8_YAKIMA_ENTITIES[0]["id"])
        source_id = str(lane.WAVE8_YAKIMA_SOURCES[0]["id"])
        entities[entity_id]["name"] = "mutated copy"
        sources[source_id]["title"] = "mutated copy"
        self.assertNotEqual(entities[entity_id], lane.WAVE8_YAKIMA_ENTITIES[0])
        self.assertNotEqual(sources[source_id], lane.WAVE8_YAKIMA_SOURCES[0])

        entity_collision = copy.deepcopy(lane.WAVE8_YAKIMA_ENTITIES[0])
        entity_collision["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_yakima_entities(
                {str(entity_collision["id"]): entity_collision}
            )

        source_collision = copy.deepcopy(lane.WAVE8_YAKIMA_SOURCES[0])
        source_collision["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_yakima_sources(
                {str(source_collision["id"]): source_collision}
            )

    def test_promoter_emits_only_two_schema_valid_unique_wins(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_YAKIMA_CONTRACT_IDS,
        )
        self.assertFalse(
            {str(event["hced_candidate_id"]) for event in events}
            & set(lane.WAVE8_YAKIMA_NONPROMOTIONS)
        )
        self.assertEqual(len({str(event["id"]) for event in events}), 2)
        for event in events:
            Event.from_dict(event)
            expected = EXPECTED_PROMOTIONS[event["hced_candidate_id"]]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual(event["year"], 1855)
            self.assertEqual(event["end_year"], 1855)
            self.assertEqual(event["date_precision"], expected["date_precision"])
            self.assertEqual(event["reviewed_granularity"], expected["granularity"])
            self.assertEqual(event["confidence"], expected["confidence"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
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
            draws = {
                participant["entity_id"]
                for participant in event["participants"]
                if "draw" in participant["result_class"]
            }
            self.assertEqual(winners, expected["winner"])
            self.assertEqual(losers, expected["loser"])
            self.assertFalse(draws)

    def test_promoted_participants_are_only_the_four_bounded_entities(self) -> None:
        participants = {
            str(participant["entity_id"])
            for event in self._events()
            for participant in event["participants"]
        }
        bounded = {
            str(entity["id"]) for entity in lane.WAVE8_YAKIMA_ENTITIES
        }
        self.assertEqual(participants, bounded)
        self.assertFalse(
            participants
            & {
                "united_states",
                "us_antebellum",
                "us_army",
                "yakama",
                "yakama_nation",
                "yakima",
                "yakima_indians",
            }
        )

    def test_promoted_provenance_matches_installed_sources(self) -> None:
        _, sources, _ = self._installed()
        for event in self._events():
            contract = lane.WAVE8_YAKIMA_CONTRACTS[event["hced_candidate_id"]]
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

    def test_local_location_quarantine_withholds_points_and_retains_country(
        self,
    ) -> None:
        self.assertEqual(
            lane.WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_YAKIMA_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            lane.WAVE8_YAKIMA_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": lane.WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            lane.wave8_yakima_location_quarantine_additions(),
            lane.WAVE8_YAKIMA_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertFalse(
            lane.WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS
            & set(lane.WAVE8_YAKIMA_NONPROMOTIONS)
        )
        for candidate_id, review in (
            lane.WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS.items()
        ):
            row = self.exact_rows[candidate_id]
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(
                review["raw_point"],
                [float(row["longitude"]), float(row["latitude"])],
            )
            self.assertEqual(review["retained_country"], "United States")
            self.assertTrue(review["evidence_refs"])
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertEqual(
                event["location_provenance"]["source_id"],
                "hced_dataset",
            )

    def test_cross_lane_ownership_blocks_modern_generic_and_composite_aliases(
        self,
    ) -> None:
        self.assertEqual(
            set(lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS),
            {
                "modern_yakama_nation",
                "united_states_and_territorial_volunteers",
                "yakima_war_composite_labels",
            },
        )
        modern = lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS[
            "modern_yakama_nation"
        ]
        self.assertEqual(
            modern["disposition"],
            "modern_and_treaty_identity_not_retroactive_rating_alias",
        )
        self.assertIn("yakama_nation", modern["forbidden_generic_entity_ids"])
        us = lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS[
            "united_states_and_territorial_volunteers"
        ]
        self.assertEqual(
            us["disposition"],
            "event_bounded_formations_not_generic_state_or_service",
        )
        family = lane.WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS[
            "yakima_war_composite_labels"
        ]
        self.assertEqual(
            set(family["adjacent_candidate_ids"]),
            set(EXPECTED_ADJACENT_ROWS),
        )
        self.assertEqual(
            set(lane.WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS),
            {
                *(f"related_hced:{item}" for item in EXPECTED_ADJACENT_ROWS),
                "cross_lane:modern_yakama_nation",
                "cross_lane:united_states_and_territorial_volunteers",
                "cross_lane:yakima_war_composite_labels",
            },
        )

    def test_promoter_rejects_missing_or_out_of_window_entity(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(TOPPENISH_INDIGENOUS_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_yakima_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        drifted = copy.deepcopy(entities)
        drifted[UNION_GAP_US_ID]["end_year"] = 1854
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_yakima_contracts(
                self.hced_rows,
                drifted,
                existing,
            )

    def test_promoter_rejects_existing_candidate_or_event_twin(self) -> None:
        entities, _, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_yakima_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing-candidate",
                        "name": "Different name",
                        "year": 1855,
                        "hced_candidate_id": "hced-Toppenish1855-1",
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_yakima_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing-event",
                        "name": "Battle of Union Gap (Two Buttes)",
                        "year": 1855,
                    }
                ],
            )

    def test_promoter_does_not_mutate_inputs(self) -> None:
        entities, _, existing = self._installed()
        rows = copy.deepcopy(self.hced_rows)
        entity_copy = copy.deepcopy(entities)
        existing_copy = copy.deepcopy(existing)
        lane.promote_wave8_yakima_contracts(
            rows,
            entity_copy,
            existing_copy,
        )
        self.assertEqual(rows, self.hced_rows)
        self.assertEqual(entity_copy, entities)
        self.assertEqual(existing_copy, existing)


if __name__ == "__main__":
    unittest.main()
