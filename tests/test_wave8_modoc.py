import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_modoc as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_modoc_"

FIRST_MODOC = "kintpuash_modoc_stronghold_defenders_1873_01_17"
FIRST_US = "wheaton_joint_stronghold_assault_force_1873_01_17"
SECOND_US = "gillem_joint_stronghold_operation_1873_04_15_17"
SECOND_MODOC = "kintpuash_modoc_stronghold_defenders_1873_04_15_17"
SCHONCHIN_MODOC = "scarfaced_charley_modoc_ambush_party_1873_04_26"
SCHONCHIN_US = "thomas_wright_us_reconnaissance_patrol_1873_04_26"

EXPECTED_RAW_HASHES = {
    "hced-Lava Beds (1st)1873-1": (
        "2114d7ae883f25611e15469f787b31fb65448b3f43528e533e98e77eed418362"
    ),
    "hced-Lava Beds (2nd)1873-1": (
        "47d8dc6cb8d1fe5c59bf0fd8867a9abd2e02d738f56ddac206be4c34733aca80"
    ),
    "hced-Lost River, California1872-1": (
        "3cd4ed9cedaef60433d726dd2a308942c829a14b4b2f61cd5d1fca30ef542739"
    ),
    "hced-Schonchin Flow1873-1": (
        "10d95645d894fc4dcc62b9c3e19c639df5863f8e5e4ce023ae016cbdbaf0a49a"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Lava Beds (1st)1873-1": {
        "name": "Lava Beds (1st)",
        "side_1": "Modoc Indians",
        "side_2": "United States",
        "winner": "Modoc Indians",
        "loser": "United States",
        "complete": True,
        "year": 1873,
        "point": [-121.5091537, 41.7749372],
        "country": "United States",
    },
    "hced-Lava Beds (2nd)1873-1": {
        "name": "Lava Beds (2nd)",
        "side_1": "United States",
        "side_2": "Modoc Indians",
        "winner": "United States",
        "loser": "Modoc Indians",
        "complete": True,
        "year": 1873,
        "point": [-121.5091537, 41.7749372],
        "country": "United States",
    },
    "hced-Lost River, California1872-1": {
        "name": "Lost River, California",
        "side_1": "United States",
        "side_2": "Modoc Indians",
        "winner": "Draw",
        "loser": None,
        "complete": False,
        "year": 1872,
        "point": [-121.5140326, 41.9399991],
        "country": "United States",
    },
    "hced-Schonchin Flow1873-1": {
        "name": "Schonchin Flow",
        "side_1": "Modoc Indians",
        "side_2": "United States",
        "winner": "Modoc Indians",
        "loser": "United States",
        "complete": True,
        "year": 1873,
        "point": [-121.5291498, 41.7382018],
        "country": "United States",
    },
}

EXPECTED_EVENTS = {
    "hced-Lava Beds (1st)1873-1": {
        "name": "First Battle for Captain Jack's Stronghold",
        "date_text": "17 January 1873",
        "date_precision": "day",
        "granularity": "single_day_coordinated_stronghold_assault",
        "event_type": "engagement",
        "winner": {FIRST_MODOC},
        "loser": {FIRST_US},
        "confidence": 0.98,
    },
    "hced-Lava Beds (2nd)1873-1": {
        "name": "Second Battle for Captain Jack's Stronghold",
        "date_text": "15-17 April 1873",
        "date_precision": "day_range",
        "granularity": "three_day_stronghold_assault_and_position_capture",
        "event_type": "campaign",
        "winner": {SECOND_US},
        "loser": {SECOND_MODOC},
        "confidence": 0.84,
    },
    "hced-Schonchin Flow1873-1": {
        "name": "Thomas-Wright Battle at Schonchin Flow",
        "date_text": "26 April 1873",
        "date_precision": "day",
        "granularity": "reconnaissance_patrol_ambush",
        "event_type": "engagement",
        "winner": {SCHONCHIN_MODOC},
        "loser": {SCHONCHIN_US},
        "confidence": 0.98,
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


class Wave8ModocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "modoc indians"
            or normalize_label(row.get("side_2_raw")) == "modoc indians"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_MODOC_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_MODOC_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_MODOC_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_modoc_entities(entities)
        lane.install_wave8_modoc_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_modoc_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_raw_hashes_and_semantics_are_pinned(self):
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, lane.WAVE8_MODOC_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(lane.WAVE8_MODOC_ROW_HASHES, EXPECTED_RAW_HASHES)
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_RAW_HASHES[candidate_id],
                )
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1"])
                self.assertEqual(row["side_2_raw"], expected["side_2"])
                self.assertEqual(row["winner_raw"], expected["winner"])
                self.assertEqual(row["loser_raw"], expected["loser"])
                self.assertIs(row["winner_loser_complete"], expected["complete"])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )
                self.assertEqual(
                    row["modern_location_country"], expected["country"]
                )

    def test_candidate_digest_and_funnel_record_are_pinned(self):
        payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(EXPECTED_RAW_ROWS)
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(digest, lane.WAVE8_MODOC_EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(
            lane.validate_wave8_modoc_funnel(self.funnel),
            {
                "events_touched": 4,
                "release_lane_overlap": 0,
                "sole_blocker_events": 4,
            },
        )
        self.assertEqual(
            lane.WAVE8_MODOC_FUNNEL_AUDIT["failure_cases"],
            {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": 4,
            },
        )

    def test_queue_validator_pins_complete_war_and_spelling_inventory(self):
        self.assertEqual(
            lane.validate_wave8_modoc_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        war_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if any(
                normalize_label(name) == "modoc indian war"
                for name in row.get("war_names", [])
            )
        }
        self.assertEqual(war_ids, lane.WAVE8_MODOC_WAR_INVENTORY_IDS)
        self.assertEqual(
            lane.WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY,
            {
                "captain jack s band": (),
                "modoc": (),
                "modoc indian": (),
                "modoc indians": tuple(sorted(EXPECTED_RAW_ROWS)),
                "modoc nation": (),
                "modocs": (),
            },
        )

    def test_new_adjacent_modoc_spelling_or_war_row_fails_closed(self):
        changed = copy.deepcopy(self.hced_rows)
        changed.append(
            {
                "candidate_id": "hced-future-modocs-row",
                "side_1_raw": "Modocs",
                "side_2_raw": "United States",
                "war_names": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "adjacent Modoc spelling"):
            lane.validate_wave8_modoc_queue_contracts(changed)

        changed = copy.deepcopy(self.hced_rows)
        changed.append(
            {
                "candidate_id": "hced-future-modoc-war-row",
                "side_1_raw": "Captain Jack's Band",
                "side_2_raw": "United States",
                "war_names": ["Modoc Indian War"],
            }
        )
        with self.assertRaisesRegex(ValueError, "complete Modoc War inventory"):
            lane.validate_wave8_modoc_queue_contracts(changed)

    def test_lost_river_is_unknown_and_never_a_draw_contract(self):
        self.assertEqual(
            lane.WAVE8_MODOC_HOLD_IDS,
            {"hced-Lost River, California1872-1"},
        )
        hold = lane.WAVE8_MODOC_HOLDS[
            "hced-Lost River, California1872-1"
        ]
        self.assertEqual(hold["reviewed_outcome"], "unknown_at_locked_event_scope")
        self.assertEqual(
            hold["hold_reason"],
            "scope_dependent_mixed_result_not_a_defensible_draw",
        )
        self.assertEqual(hold["source_winner_raw"], "Draw")
        self.assertIs(hold["source_winner_loser_complete"], False)
        self.assertIs(hold["unknown_is_never_draw"], True)
        for forbidden in (
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        ):
            self.assertNotIn(forbidden, hold)
        self.assertNotIn(
            "hced-Lost River, California1872-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_six_formations_are_event_bounded_and_never_generic(self):
        by_id = {
            str(entity["id"]): entity for entity in lane.WAVE8_MODOC_ENTITIES
        }
        expected_ids = {
            FIRST_MODOC,
            FIRST_US,
            SECOND_US,
            SECOND_MODOC,
            SCHONCHIN_MODOC,
            SCHONCHIN_US,
        }
        self.assertEqual(set(by_id), expected_ids)
        for entity in by_id.values():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                (1873, 1873),
            )
            self.assertEqual(entity["aliases"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertTrue(
                any(token in entity["name"] for token in ("January", "April"))
            )
        for forbidden in (
            "modoc",
            "modoc_indians",
            "modoc_nation",
            "united_states",
            "united_states_of_america",
            "us_united_states_of_america_reconstruction",
        ):
            self.assertNotIn(forbidden, by_id)

    def test_sources_are_authoritative_independent_and_model_valid(self):
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_MODOC_SOURCES
        }
        self.assertEqual(len(source_by_id), 10)
        families = {
            str(source["source_family_id"]) for source in source_by_id.values()
        }
        self.assertEqual(len(families), 10)
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertNotIn("wikipedia.org", source["url"])
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        for contract in lane.WAVE8_MODOC_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

    def test_contracts_preserve_attested_orientation_without_override(self):
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(lane.WAVE8_MODOC_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in lane.WAVE8_MODOC_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertIs(contract["source_outcome_override"], False)
                self.assertIs(contract["outcome_reversal"], False)
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertNotEqual(normalize_label(row["winner_raw"]), "draw")

    def test_scope_and_opposite_result_audit_is_complete(self):
        audits = lane.WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT
        self.assertEqual(set(audits), lane.WAVE8_MODOC_RESERVED_IDS)
        self.assertEqual(
            audits["hced-Lava Beds (1st)1873-1"]["disposition"],
            "promote_modoc_defensive_victory",
        )
        self.assertEqual(
            audits["hced-Lava Beds (2nd)1873-1"]["disposition"],
            "promote_us_positional_operation_victory",
        )
        self.assertEqual(
            audits["hced-Schonchin Flow1873-1"]["disposition"],
            "promote_modoc_tactical_victory",
        )
        self.assertEqual(
            audits["hced-Lost River, California1872-1"]["disposition"],
            "hold_unknown_not_draw",
        )
        for audit in audits.values():
            self.assertTrue(audit["opposite_result_disposition"])
            self.assertTrue(audit["scope_note"])

    def test_cross_event_boundaries_prevent_same_site_and_opposite_result_merges(self):
        boundaries = lane.WAVE8_MODOC_CROSS_EVENT_BOUNDARIES
        self.assertEqual(
            set(boundaries),
            {
                "first_to_second_stronghold",
                "lost_river_to_first_stronghold",
                "second_stronghold_to_schonchin",
            },
        )
        self.assertEqual(
            boundaries["first_to_second_stronghold"]["disposition"],
            "same_position_distinct_assaults_and_results",
        )
        self.assertIn(
            "nine days",
            boundaries["second_stronghold_to_schonchin"]["reason"],
        )
        for boundary in boundaries.values():
            self.assertEqual(len(boundary["candidate_ids"]), 2)
            self.assertTrue(
                set(boundary["candidate_ids"]) <= lane.WAVE8_MODOC_RESERVED_IDS
            )

    def test_promotion_emits_three_canonical_events_and_exact_actor_sets(self):
        events = self._events()
        self.assertEqual(len(events), 3)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            with self.subTest(candidate_id=candidate_id):
                event = by_candidate[candidate_id]
                contract = lane.WAVE8_MODOC_CONTRACTS[candidate_id]
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["year"], 1873)
                self.assertEqual(event["end_year"], 1873)
                self.assertEqual(event["date_precision"], expected["date_precision"])
                self.assertEqual(
                    event["reviewed_granularity"], expected["granularity"]
                )
                self.assertEqual(
                    contract["canonical_event"]["date_text"],
                    expected["date_text"],
                )
                self.assertEqual(event["event_type"], expected["event_type"])
                self.assertEqual(event["confidence"], expected["confidence"])
                self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                winners = {
                    str(participant["entity_id"])
                    for participant in event["participants"]
                    if str(participant["termination"]).endswith("victory")
                }
                losers = {
                    str(participant["entity_id"])
                    for participant in event["participants"]
                    if str(participant["termination"]).endswith("defeat")
                    or participant["termination"] == "campaign_defeat"
                }
                self.assertEqual(winners, expected["winner"])
                self.assertEqual(losers, expected["loser"])
                parsed = Event.from_dict(event)
                self.assertEqual(parsed.event_type, expected["event_type"])

    def test_second_stronghold_is_operational_but_other_results_are_engagements(self):
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        second = by_candidate["hced-Lava Beds (2nd)1873-1"]
        self.assertEqual(second["event_type"], "campaign")
        self.assertIn("positional operation", second["summary"])
        self.assertIn("not converted into capture", second["summary"])
        self.assertEqual(
            {
                participant["result_class"]
                for participant in second["participants"]
            },
            {
                "operational_positional_victory",
                "operational_position_loss_with_force_escape",
            },
        )
        self.assertEqual(Event.from_dict(second).track, "operational")
        for candidate_id in (
            "hced-Lava Beds (1st)1873-1",
            "hced-Schonchin Flow1873-1",
        ):
            event = by_candidate[candidate_id]
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(Event.from_dict(event).track, "tactical")

    def test_location_quarantine_is_local_complete_and_country_preserving(self):
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_MODOC_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS, set())
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event.get("modern_location_country"), "United States")
            self.assertIn("location_provenance", event)
            reason = lane.WAVE8_MODOC_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(reason["retained_country"], "United States")
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_iwbd_and_existing_release_duplicate_audits_are_zero(self):
        self.assertEqual(lane.WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(
            set(lane.WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_MODOC_RESERVED_IDS,
        )
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_event_boundaries": 3,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 3,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
                "release_probable_twins": 0,
            },
        )

    def test_release_overlap_is_all_or_none(self):
        actual_overlap = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_MODOC_CONTRACT_IDS
        }
        self.assertIn(
            actual_overlap,
            (set(), set(lane.WAVE8_MODOC_CONTRACT_IDS)),
        )
        result = lane.validate_wave8_modoc_funnel(
            self.funnel,
            self.release_events,
        )
        self.assertEqual(result["release_lane_overlap"], len(actual_overlap))

        _, _, stripped = self._installed()
        full = copy.deepcopy(stripped)
        for candidate_id in sorted(lane.WAVE8_MODOC_CONTRACT_IDS):
            full.append(
                {
                    "id": f"integrated-{candidate_id}",
                    "name": f"integrated owner for {candidate_id}",
                    "year": 1873,
                    "hced_candidate_id": candidate_id,
                }
            )
        self.assertEqual(
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                full,
            )["release_lane_overlap"],
            3,
        )

        with self.assertRaisesRegex(ValueError, "release overlap is partial"):
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                full[:-1],
            )

    def test_probable_iwbd_and_release_twins_fail_closed(self):
        _, _, existing = self._installed()
        fake_iwbd = copy.deepcopy(self.iwbd_rows)
        fake_iwbd.append(
            {
                "candidate_id": "iwbd-future-stronghold-twin",
                "name": "Second Battle of the Stronghold",
                "start_date": "1873-04-15",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                fake_iwbd,
                existing,
            )

        fake_release = copy.deepcopy(existing)
        fake_release.append(
            {
                "id": "future-thomas-wright-twin",
                "name": "Battle of Sand Butte",
                "year": 1873,
                "hced_candidate_id": "hced-future-twin",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable release duplicate"):
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                fake_release,
            )

    def test_held_lost_river_row_cannot_leak_into_release(self):
        _, _, existing = self._installed()
        existing.append(
            {
                "id": "invented-lost-river-draw",
                "name": "Battle of Lost River",
                "year": 1872,
                "hced_candidate_id": "hced-Lost River, California1872-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "held Lost River row was rated"):
            lane.validate_wave8_modoc_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            )

    def test_row_tamper_and_missing_entity_fail_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in tampered
            if row.get("candidate_id") == "hced-Schonchin Flow1873-1"
        )
        target["winner_raw"] = "United States"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_modoc_queue_contracts(tampered)

        entities, _, existing = self._installed()
        entities.pop(SECOND_MODOC)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_modoc_contracts(
                self.hced_rows,
                entities,
                existing,
            )

    def test_promotion_is_deterministic_and_does_not_mutate_inputs(self):
        entities, _, existing = self._installed()
        hced_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        first = lane.promote_wave8_modoc_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        second = lane.promote_wave8_modoc_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(first, second)
        self.assertEqual(self.hced_rows, hced_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)

    def test_installers_are_idempotent_and_reject_collisions(self):
        entities, sources, _ = self._installed()
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_modoc_entities(entities)
        lane.install_wave8_modoc_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)

        bad_entities = {FIRST_MODOC: {"id": FIRST_MODOC, "name": "collision"}}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_modoc_entities(bad_entities)
        first_source_id = lane.WAVE8_MODOC_SOURCES[0]["id"]
        bad_sources = {
            first_source_id: {"id": first_source_id, "title": "collision"}
        }
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_modoc_sources(bad_sources)

    def test_signature_counts_cohorts_and_metadata_are_pinned(self):
        self.assertNotEqual(lane.WAVE8_MODOC_FINAL_AUDIT_SIGNATURE, "__PENDING__")
        self.assertEqual(
            lane.wave8_modoc_audit_signature(),
            lane.WAVE8_MODOC_FINAL_AUDIT_SIGNATURE,
        )
        expected_counts = {
            "adjacent_literal_labels_audited": 6,
            "country_quarantine_additions": 0,
            "cross_event_boundaries": 3,
            "engagement_events": 2,
            "existing_release_duplicate_dispositions": 0,
            "holds": 1,
            "integration_dispositions": 3,
            "iwbd_duplicate_dispositions": 0,
            "iwbd_zero_overlap_candidates": 4,
            "new_entities": 6,
            "new_sources": 10,
            "newly_rated_events": 3,
            "operation_events": 1,
            "outcome_overrides": 0,
            "point_quarantine_additions": 3,
            "promotion_contracts": 3,
            "reviewed_hced_rows": 4,
            "scope_audits": 4,
            "sole_blocker_rows": 4,
            "terminal_exclusions": 0,
            "touched_hced_rows": 4,
        }
        self.assertEqual(lane.wave8_modoc_counts(), expected_counts)
        self.assertEqual(
            lane.wave8_modoc_cohort_counts(),
            {
                "first_stronghold_assault_1873_01_17": 1,
                "second_stronghold_operation_1873_04_15_17": 1,
                "thomas_wright_ambush_1873_04_26": 1,
            },
        )
        self.assertEqual(
            lane.wave8_modoc_row_dispositions(),
            {
                "hced-Lava Beds (1st)1873-1": "promote",
                "hced-Lava Beds (2nd)1873-1": "promote",
                "hced-Lost River, California1872-1": "hold",
                "hced-Schonchin Flow1873-1": "promote",
            },
        )
        metadata = lane.wave8_modoc_metadata()
        self.assertEqual(metadata["counts"], expected_counts)
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_MODOC_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
