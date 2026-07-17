import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_kingdom_kandy as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_kingdom_kandy_"

HANWELLA_BRITISH = "british_ceylon_hanwella_defense_force_1803"
HANWELLA_KANDYAN = "sri_vikrama_kandyan_hanwella_field_force_1803"
KANDY_KANDYAN = "sri_vikrama_kandyan_kandy_counterattack_force_1803"
KANDY_BRITISH = "davie_british_ceylon_garrison_kandy_1803"

EXPECTED_RAW_HASHES = {
    "hced-Balane1594-1": (
        "83daa0566d2bbda3bf7d675c7327c957269073e2d020f0937ec81e3469684d8e"
    ),
    "hced-Gannoruwa1638-1": (
        "ac98a1cbd242c2013a47c364154b3cdce3e0ebb794662fc67141f400ddfdc88c"
    ),
    "hced-Hanwella1803-1": (
        "ae1addc255ca5f638c66efb18a261a75f04f3badcafdabcaf3ca83109d9f78a5"
    ),
    "hced-Kandy1803-1": (
        "738947c6d1791bf96bb2ff44f72ce4e9d9ee6c975b3b3f1831bfb97db84bd0d9"
    ),
    "hced-Kandy1815-1": (
        "362cabcf4a7cf955492a31a473ff40022e05dc7880ca96d9542c16be408223f2"
    ),
    "hced-Kandy1818-1": (
        "fcbb39119bd5c3502f6b6a5cba515d22e3585f5aa49a4c6c66b80852c3578243"
    ),
    "hced-Radenivela1630-1": (
        "0ddf33d14eaba4c3120532aea883bc5bd0caea3936863a26c14e95edf57fe73e"
    ),
}

EXPECTED_UNRESOLVED_IDS = {
    "hced-Hanwella1803-1",
    "hced-Kandy1803-1",
    "hced-Kandy1815-1",
    "hced-Kandy1818-1",
}

EXPECTED_RAW_ROWS = {
    "hced-Hanwella1803-1": {
        "name": "Hanwella",
        "side_1": "United Kingdom",
        "side_2": "Kingdom of Kandy",
        "winner": "United Kingdom",
        "loser": "Kingdom of Kandy",
        "year": 1803,
        "point": [80.0814292, 6.8978344],
        "country": "Sri Lanka",
        "source_row": 6787,
    },
    "hced-Kandy1803-1": {
        "name": "Kandy",
        "side_1": "Kingdom of Kandy",
        "side_2": "United Kingdom",
        "winner": "Kingdom of Kandy",
        "loser": "United Kingdom",
        "year": 1803,
        "point": [80.6337262, 7.2905715],
        "country": "Sri Lanka",
        "source_row": 8001,
    },
    "hced-Kandy1815-1": {
        "name": "Kandy",
        "side_1": "United Kingdom",
        "side_2": "Kingdom of Kandy",
        "winner": "United Kingdom",
        "loser": "Kingdom of Kandy",
        "year": 1815,
        "point": [80.6337262, 7.2905715],
        "country": "Sri Lanka",
        "source_row": 8003,
    },
    "hced-Kandy1818-1": {
        "name": "Kandy",
        "side_1": "United Kingdom",
        "side_2": "Kingdom of Kandy",
        "winner": "United Kingdom",
        "loser": "Kingdom of Kandy",
        "year": 1818,
        "point": [80.6337262, 7.2905715],
        "country": "Sri Lanka",
        "source_row": 8005,
    },
}

EXPECTED_CANONICAL = {
    "hced-Hanwella1803-1": (
        "Battle of Hanwella (1803)",
        "6 September 1803",
        "day",
        "fort_defense_and_relief_action",
    ),
    "hced-Kandy1803-1": (
        "Siege and surrender of the British garrison at Kandy",
        "24-26 June 1803",
        "day_range",
        "siege_capitulation_and_force_destruction",
    ),
}

EXPECTED_WINNERS_LOSERS = {
    "hced-Hanwella1803-1": ({HANWELLA_BRITISH}, {HANWELLA_KANDYAN}),
    "hced-Kandy1803-1": ({KANDY_KANDYAN}, {KANDY_BRITISH}),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked queue unavailable: {path.name}")
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


class Wave8KingdomKandyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data" / "review" / "hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "kingdom of kandy"
            or normalize_label(row.get("side_2_raw")) == "kingdom of kandy"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_KINGDOM_KANDY_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_KINGDOM_KANDY_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_kingdom_kandy_entities(entities)
        lane.install_wave8_kingdom_kandy_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_kingdom_kandy_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_queue_files_and_all_row_hashes_are_pinned(self):
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_KINGDOM_KANDY_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_KINGDOM_KANDY_IWBD_QUEUE_SHA256,
        )
        exact = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(exact), set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            lane.WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(lane.WAVE8_KINGDOM_KANDY_ROW_HASHES, EXPECTED_RAW_HASHES)
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(exact[candidate_id]),
                    expected_hash,
                )
        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(exact))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            lane.WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256,
        )

    def test_funnel_lock_pins_the_four_currently_unresolved_rows(self):
        records = [
            record
            for record in self.funnel["labels"]
            if record.get("label") == "kingdom of kandy"
        ]
        release_ids = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS
        }
        if not records:
            self.assertEqual(release_ids, set(lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS))
            return
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(
            record["event_candidate_id_sha256"],
            lane.WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(record["events_touched"], 4)
        self.assertEqual(record["sole_blocker_events"], 4)
        self.assertEqual(record["unresolved_side_attempts"], 4)
        self.assertEqual(record["centuries"], {"CE_19": 4})
        self.assertEqual(
            record["failure_cases"],
            {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": 4,
            },
        )
        funnel_ids = {
            str(row["candidate_id"])
            for row in self.funnel["row_label_data"]
            if "kingdom of kandy" in row.get("blocker_labels", [])
        }
        self.assertEqual(funnel_ids, EXPECTED_UNRESOLVED_IDS)
        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(funnel_ids))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            lane.WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )

    def test_four_unresolved_raw_rows_are_fully_pinned(self):
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = self.hced_by_id[candidate_id]
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1"])
                self.assertEqual(row["side_2_raw"], expected["side_2"])
                self.assertEqual(row["winner_raw"], expected["winner"])
                self.assertEqual(row["loser_raw"], expected["loser"])
                self.assertTrue(row["winner_loser_complete"])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(row["source_row"], expected["source_row"])
                self.assertEqual(row["modern_location_country"], expected["country"])
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )

    def test_disposition_partition_is_complete_and_disjoint(self):
        self.assertEqual(
            lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
            {"hced-Hanwella1803-1", "hced-Kandy1803-1"},
        )
        self.assertFalse(lane.WAVE8_KINGDOM_KANDY_HOLDS)
        self.assertFalse(lane.WAVE8_KINGDOM_KANDY_HOLD_IDS)
        self.assertEqual(
            lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS,
            {"hced-Kandy1815-1", "hced-Kandy1818-1"},
        )
        self.assertEqual(
            lane.WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS,
            {
                "hced-Balane1594-1",
                "hced-Gannoruwa1638-1",
                "hced-Radenivela1630-1",
            },
        )
        partitions = (
            lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
            lane.WAVE8_KINGDOM_KANDY_HOLD_IDS,
            lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS,
            lane.WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS,
        )
        for index, left in enumerate(partitions):
            for right in partitions[index + 1 :]:
                self.assertFalse(set(left) & set(right))
        self.assertEqual(set().union(*map(set, partitions)), set(EXPECTED_RAW_HASHES))

    def test_1815_and_1818_are_exclusions_not_invented_battles_or_draws(self):
        forbidden = {"result_type", "winner_entity_ids", "winner_side"}
        exclusion_1815 = lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS[
            "hced-Kandy1815-1"
        ]
        self.assertEqual(
            exclusion_1815["reviewed_outcome"],
            "not_rateable_no_contested_engagement",
        )
        self.assertIn("unopposed", exclusion_1815["exclusion_reason"])
        exclusion_1818 = lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS[
            "hced-Kandy1818-1"
        ]
        self.assertIn("wrong_actor", exclusion_1818["exclusion_reason"])
        self.assertIn("post_annexation", exclusion_1818["exclusion_reason"])
        for exclusion in (exclusion_1815, exclusion_1818):
            self.assertTrue(exclusion["unknown_is_never_draw"])
            self.assertFalse(forbidden & set(exclusion))
            self.assertGreaterEqual(len(exclusion["evidence_refs"]), 4)
        self.assertIn("without resistance", exclusion_1815["audit_note"])
        self.assertIn("neither one engagement", exclusion_1818["audit_note"])

    def test_wave6_owners_and_balane_exclusion_are_explicit(self):
        dispositions = lane.WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS
        self.assertEqual(
            dispositions["hced-Balane1594-1"]["disposition"],
            "external_wave6_terminal_exclusion",
        )
        self.assertIn("Danture", dispositions["hced-Balane1594-1"]["reason"])
        self.assertIn("Balana", dispositions["hced-Balane1594-1"]["reason"])
        expected_owners = {
            "hced-Gannoruwa1638-1": "hced_wave6_hced_gannoruwa1638_1",
            "hced-Radenivela1630-1": "hced_wave6_hced_radenivela1630_1",
        }
        for candidate_id, event_id in expected_owners.items():
            disposition = dispositions[candidate_id]
            self.assertEqual(disposition["disposition"], "existing_release_owner")
            self.assertEqual(disposition["owner_event_id"], event_id)
            owners = [
                event
                for event in self.release_events
                if event.get("hced_candidate_id") == candidate_id
            ]
            self.assertEqual(len(owners), 1)
            self.assertEqual(owners[0]["id"], event_id)
        self.assertFalse(
            any(
                event.get("hced_candidate_id") == "hced-Balane1594-1"
                for event in self.release_events
            )
        )

    def test_composite_trincomalee_row_is_pinned_outside_the_literal_lane(self):
        self.assertIs(
            lane.WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS,
            lane.WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS,
        )
        disposition = lane.WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS[
            "hced-Trincomalee1639-1"
        ]
        row = self.hced_by_id["hced-Trincomalee1639-1"]
        self.assertEqual(
            canonical_hced_row_sha256(row),
            disposition["raw_row_sha256"],
        )
        self.assertEqual(row["side_1_raw"], "Netherlands, Kingdom of Kandy")
        self.assertEqual(
            disposition["disposition"],
            "adjacent_composite_label_outside_exact_lane",
        )
        self.assertIn("own Dutch-Kandyan coalition", disposition["reason"])

    def test_sources_are_independent_typed_and_model_valid(self):
        self.assertEqual(len(lane.WAVE8_KINGDOM_KANDY_SOURCES), 13)
        source_ids = [str(source["id"]) for source in lane.WAVE8_KINGDOM_KANDY_SOURCES]
        families = [
            str(source["source_family_id"])
            for source in lane.WAVE8_KINGDOM_KANDY_SOURCES
        ]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(len(families), len(set(families)))
        for source in lane.WAVE8_KINGDOM_KANDY_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        outcome_sources = {
            source["id"]
            for source in lane.WAVE8_KINGDOM_KANDY_SOURCES
            if "outcome" in source["evidence_roles"]
        }
        self.assertGreaterEqual(len(outcome_sources), 7)
        self.assertIn("wave8_kingdom_kandy_national_archives_1815", source_ids)
        self.assertIn("wave8_kingdom_kandy_national_archives_1818", source_ids)

    def test_entities_are_event_bounded_and_open_no_generic_alias(self):
        self.assertEqual(len(lane.WAVE8_KINGDOM_KANDY_ENTITIES), 4)
        entity_ids = {str(entity["id"]) for entity in lane.WAVE8_KINGDOM_KANDY_ENTITIES}
        self.assertEqual(
            entity_ids,
            {HANWELLA_BRITISH, HANWELLA_KANDYAN, KANDY_KANDYAN, KANDY_BRITISH},
        )
        for entity in lane.WAVE8_KINGDOM_KANDY_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["start_year"], entity["end_year"]), (1803, 1803))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("post-1815", note)
            self.assertNotEqual(normalize_label(entity["name"]), "kingdom of kandy")
            self.assertNotEqual(normalize_label(entity["name"]), "united kingdom")

    def test_contracts_pin_dates_sides_sources_and_raw_outcomes(self):
        for candidate_id, contract in lane.WAVE8_KINGDOM_KANDY_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                canonical = contract["canonical_event"]
                expected = EXPECTED_CANONICAL[candidate_id]
                self.assertEqual(
                    (
                        canonical["name"],
                        canonical["date_text"],
                        canonical["date_precision"],
                        canonical["granularity"],
                    ),
                    expected,
                )
                self.assertEqual((canonical["year_low"], canonical["year_high"]), (1803, 1803))
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertTrue(contract["actor_override"])
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 4)
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 4)
                raw = self.hced_by_id[candidate_id]
                self.assertEqual(raw["winner_raw"], raw["side_1_raw"])
                self.assertEqual(raw["loser_raw"], raw["side_2_raw"])
        self.assertEqual(
            set(lane.WAVE8_KINGDOM_KANDY_CONTRACTS["hced-Hanwella1803-1"]["side_1_entity_ids"]),
            {HANWELLA_BRITISH},
        )
        self.assertEqual(
            set(lane.WAVE8_KINGDOM_KANDY_CONTRACTS["hced-Hanwella1803-1"]["side_2_entity_ids"]),
            {HANWELLA_KANDYAN},
        )
        self.assertEqual(
            set(lane.WAVE8_KINGDOM_KANDY_CONTRACTS["hced-Kandy1803-1"]["side_1_entity_ids"]),
            {KANDY_KANDYAN},
        )
        self.assertEqual(
            set(lane.WAVE8_KINGDOM_KANDY_CONTRACTS["hced-Kandy1803-1"]["side_2_entity_ids"]),
            {KANDY_BRITISH},
        )

    def test_promoter_emits_two_victories_and_no_exclusions(self):
        events = self._events()
        self.assertEqual(len(events), 2)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS)
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertEqual(event["domain"], "land")
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Sri Lanka")
            self.assertIn("location_provenance", event)
            winners = {
                str(participant["entity_id"])
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            losers = {
                str(participant["entity_id"])
                for participant in event["participants"]
                if participant["termination"] == "engagement_defeat"
            }
            self.assertEqual((winners, losers), EXPECTED_WINNERS_LOSERS[candidate_id])
            self.assertFalse(
                any(participant["result_class"] == "draw" for participant in event["participants"])
            )
        self.assertEqual(by_candidate["hced-Hanwella1803-1"]["aliases"], ["Hanwella"])
        self.assertEqual(by_candidate["hced-Kandy1803-1"]["aliases"], ["Kandy"])
        self.assertFalse(
            lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS & set(by_candidate)
        )

    def test_kandy_1803_rates_defeat_not_a_second_massacre_event(self):
        contract = lane.WAVE8_KINGDOM_KANDY_CONTRACTS["hced-Kandy1803-1"]
        self.assertIn("military defeat", contract["audit_note"])
        self.assertIn("not a separately invented battle", contract["audit_note"])
        self.assertIn("post-capitulation", next(
            entity["continuity_note"]
            for entity in lane.WAVE8_KINGDOM_KANDY_ENTITIES
            if entity["id"] == KANDY_BRITISH
        ))
        self.assertEqual(contract["confidence"], 0.95)

    def test_1815_boundary_and_persistent_wave6_entity_are_not_bridged(self):
        adjacent = lane.WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS
        boundary = adjacent["1815_sovereignty_boundary"]
        self.assertEqual(boundary["boundary_year"], 1815)
        self.assertEqual(boundary["post_boundary_candidate_ids"], ["hced-Kandy1818-1"])
        persistent = adjacent["wave6_persistent_identity"]
        self.assertEqual(persistent["existing_entity_id"], "kingdom_kandy_1590")
        used = {
            entity_id
            for contract in lane.WAVE8_KINGDOM_KANDY_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertNotIn("kingdom_kandy_1590", used)
        self.assertNotIn("united_kingdom", used)

    def test_location_quarantine_is_local_point_only_and_all_or_none_global(self):
        self.assertEqual(
            lane.WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            lane.wave8_kingdom_kandy_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
            },
        )
        for candidate_id, review in lane.WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS.items():
            expected = EXPECTED_RAW_ROWS[candidate_id]
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(review["raw_point"], expected["point"])
            self.assertEqual(review["retained_country"], expected["country"])
        point_overlap = set(lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS) & set(
            HCED_POINT_QUARANTINE_IDS
        )
        self.assertIn(point_overlap, (set(), set(lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS)))
        self.assertFalse(
            set(lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS)
            & set(HCED_COUNTRY_QUARANTINE_IDS)
        )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entity_snapshot = copy.deepcopy(entities)
        source_snapshot = copy.deepcopy(sources)
        lane.install_wave8_kingdom_kandy_entities(entities)
        lane.install_wave8_kingdom_kandy_sources(sources)
        self.assertEqual(entities, entity_snapshot)
        self.assertEqual(sources, source_snapshot)

        bad_entities = copy.deepcopy(entities)
        bad_entities[HANWELLA_BRITISH]["name"] = "Collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_kingdom_kandy_entities(bad_entities)
        bad_sources = copy.deepcopy(sources)
        bad_sources["wave8_kingdom_kandy_powell_wars"]["title"] = "Collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_kingdom_kandy_sources(bad_sources)

    def test_queue_and_integration_validators_report_exact_counts(self):
        self.assertEqual(
            lane.validate_wave8_kingdom_kandy_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 3,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 7,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 2,
                "external_owner_hced_dispositions": 3,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
                "related_hced_dispositions": 1,
            },
        )

    def test_probable_iwbd_and_release_twins_fail_closed(self):
        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-invented-hanwella-1803",
                "name": "Battle of Hanwella",
                "start_date": "1803-09-06",
                "end_date": "1803-09-06",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                self.hced_rows,
                iwbd,
                self.release_events,
            )

        release = copy.deepcopy(self.release_events)
        release.append(
            {
                "id": "invented_kandy_1818_twin",
                "name": "Uva-Wellassa Rebellion",
                "year": 1818,
                "hced_candidate_id": "hced-unrelated-invented",
            }
        )
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release,
            )

    def test_partial_release_overlap_and_changed_wave6_ownership_fail_closed(self):
        entities, _, existing = self._installed()
        emitted = lane.promote_wave8_kingdom_kandy_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        partial = [*existing, emitted[0]]
        with self.assertRaisesRegex(ValueError, "integration is partial"):
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                partial,
            )
        changed_owner = copy.deepcopy(self.release_events)
        owner = next(
            event
            for event in changed_owner
            if event.get("hced_candidate_id") == "hced-Gannoruwa1638-1"
        )
        owner["id"] = "wrong_owner"
        with self.assertRaisesRegex(ValueError, "Wave 6 ownership changed"):
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                changed_owner,
            )

    def test_raw_related_and_inventory_drift_fail_closed(self):
        drifted = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in drifted if row.get("candidate_id") == "hced-Hanwella1803-1"
        )
        target["winner_raw"] = "Draw"
        target["loser_raw"] = None
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.validate_wave8_kingdom_kandy_queue_contracts(drifted)

        external = copy.deepcopy(self.hced_rows)
        balane = next(
            row for row in external if row.get("candidate_id") == "hced-Balane1594-1"
        )
        balane["name"] = "Danture"
        with self.assertRaisesRegex(ValueError, "external row fingerprint changed"):
            lane.validate_wave8_kingdom_kandy_queue_contracts(external)

        related = copy.deepcopy(self.hced_rows)
        trincomalee = next(
            row
            for row in related
            if row.get("candidate_id") == "hced-Trincomalee1639-1"
        )
        trincomalee["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "related HCED fingerprint changed"):
            lane.validate_wave8_kingdom_kandy_integration_dispositions(
                related,
                self.iwbd_rows,
                self.release_events,
            )

        extra = copy.deepcopy(self.hced_rows)
        invented = copy.deepcopy(self.exact_rows[0])
        invented["candidate_id"] = "hced-InventedKandy9999-1"
        invented["source_record_id"] = "InventedKandy9999"
        invented["source_row"] = 999999
        extra.append(invented)
        with self.assertRaisesRegex(ValueError, "exact label inventory changed"):
            lane.validate_wave8_kingdom_kandy_queue_contracts(extra)

    def test_promoter_rejects_candidate_and_event_key_duplicates(self):
        entities, _, existing = self._installed()
        duplicate_candidate = copy.deepcopy(existing)
        duplicate_candidate.append(
            {
                "id": "existing_candidate",
                "name": "Unrelated",
                "year": 1803,
                "hced_candidate_id": "hced-Hanwella1803-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_kingdom_kandy_contracts(
                self.hced_rows,
                entities,
                duplicate_candidate,
            )

        duplicate_key = copy.deepcopy(existing)
        duplicate_key.append(
            {
                "id": "existing_key",
                "name": "Battle of Hanwella (1803)",
                "year": 1803,
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_kingdom_kandy_contracts(
                self.hced_rows,
                entities,
                duplicate_key,
            )

    def test_release_artifact_is_preintegration_or_fully_integrated(self):
        lane_events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS
        ]
        lane_ids = {str(event["hced_candidate_id"]) for event in lane_events}
        self.assertIn(lane_ids, (set(), set(lane.WAVE8_KINGDOM_KANDY_CONTRACT_IDS)))
        if lane_ids:
            self.assertEqual(len(lane_events), 2)
            self.assertTrue(all(event["id"].startswith(EVENT_ID_PREFIX) for event in lane_events))
            self.assertTrue(all("geometry" not in event for event in lane_events))
        self.assertFalse(
            any(
                event.get("hced_candidate_id")
                in lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS
                for event in self.release_events
            )
        )

    def test_signature_counts_and_cohort_are_exact(self):
        payload = {
            "adjacent_lane_dispositions": lane.WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS,
            "contracts": lane.WAVE8_KINGDOM_KANDY_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": lane.WAVE8_KINGDOM_KANDY_ENTITIES,
            "exact_candidate_id_sha256": lane.WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256,
            "expected_candidate_ids": sorted(
                lane.WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS
            ),
            "external_owner_dispositions": lane.WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS,
            "funnel_candidate_id_sha256": (
                lane.WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256
            ),
            "hced_queue_sha256": lane.WAVE8_KINGDOM_KANDY_HCED_QUEUE_SHA256,
            "holds": lane.WAVE8_KINGDOM_KANDY_HOLDS,
            "integration_dispositions": lane.WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": lane.WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_queue_sha256": lane.WAVE8_KINGDOM_KANDY_IWBD_QUEUE_SHA256,
            "iwbd_zero_overlap_audit": lane.WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": lane.WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": lane.WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES,
            "related_hced_dispositions": lane.WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS,
            "sources": lane.WAVE8_KINGDOM_KANDY_SOURCES,
            "terminal_exclusions": lane.WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            independent,
            "e82a63efa89efb1603c41bad435154a9918ea544d65cb6dd53ecc1b1bb0975e0",
        )
        self.assertEqual(
            independent,
            lane.WAVE8_KINGDOM_KANDY_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(independent, lane.wave8_kingdom_kandy_audit_signature())
        self.assertEqual(
            lane.wave8_kingdom_kandy_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 2,
                "external_owner_hced_dispositions": 3,
                "holds": 0,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 4,
                "new_sources": 13,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "related_hced_dispositions": 1,
                "reviewed_hced_rows": 7,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(
            lane.wave8_kingdom_kandy_cohort_counts(),
            {"first_kandyan_war_1803": 2},
        )


if __name__ == "__main__":
    unittest.main()
