import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_sertorian as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_sertorian_"
ROMAN_REPUBLIC = "roman_republic"
SERTORIAN_FACTION = "sertorian_faction_hispania_80_72_bce"

EXPECTED_HASHES = {
    "hced-Baetis-80-1": (
        "e4bfa0914c69aa63ab8106b93454124e1823f19646f5e6cb8af679454fc4c00f"
    ),
    "hced-Calahorra-74-1": (
        "15a3db557af851255251e16fcdafb7ebf7edde27d9253972dac3059096b7a7d3"
    ),
    "hced-Lauron-76-1": (
        "38948074d54e19f89c12ad25a68d00c39c43f20513569eb69cdf68ec863d5f57"
    ),
    "hced-Murviedro-75-1": (
        "beb212f1a76123b4fc87e19017756f4f80e90abac9dc44569862a9614b9d8e6b"
    ),
    "hced-Sucro-75-1": (
        "eb4290476a96903ee66ce926ea8091c15c1875fc2349f1bc1a9aef1d724b4dd8"
    ),
    "hced-Turia-75-1": (
        "26573cc773383c3d86f8fcbd7d3935024b3a1d00a4d3523af816d96eb95bb557"
    ),
}

EXPECTED_PROMOTIONS = {
    "hced-Baetis-80-1": {
        "name": "Battle on the Baetis",
        "years": (-80, -80),
        "date_precision": "year",
        "confidence": 0.94,
        "winner": SERTORIAN_FACTION,
        "loser": ROMAN_REPUBLIC,
    },
    "hced-Lauron-76-1": {
        "name": "Lauron siege-relief operation",
        "years": (-77, -76),
        "date_precision": "year_conflict",
        "confidence": 0.88,
        "winner": SERTORIAN_FACTION,
        "loser": ROMAN_REPUBLIC,
    },
    "hced-Turia-75-1": {
        "name": "Battle of Segontia (Turia/Saguntum tradition)",
        "years": (-76, -75),
        "date_precision": "year_conflict",
        "confidence": 0.72,
        "winner": ROMAN_REPUBLIC,
        "loser": SERTORIAN_FACTION,
    },
    "hced-Calahorra-74-1": {
        "name": "Sertorian relief of Calagurris",
        "years": (-75, -74),
        "date_precision": "year_conflict",
        "confidence": 0.88,
        "winner": SERTORIAN_FACTION,
        "loser": ROMAN_REPUBLIC,
    },
}

EXPECTED_DISCOVERY_HASHES = {
    "Q60524412": (
        "4c4f0ae442491e3cd752c420ed3b21efca75c548f75fb6b1d908a28e97f97824"
    ),
    "Q60524449": (
        "bf8ba315fea27fd64b5fe1dc0290dc4eb7446b910f26ec514ec9584ac4fc6616"
    ),
    "Q9173528": (
        "e5182d2f4fdc8c828f66f5869aa5a436d060b3d858f54735ba7a6906c33c4686"
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


class Wave8SertorianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SERTORIAN_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SERTORIAN_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_SERTORIAN_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_sertorian_entities(entities)
        lane.install_wave8_sertorian_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_sertorian_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_final_signature_counts_and_disposition_sets_are_exact(self) -> None:
        self.assertEqual(
            lane.wave8_sertorian_audit_signature(),
            lane.WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(lane.WAVE8_SERTORIAN_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_SERTORIAN_CONTRACT_IDS,
            frozenset(EXPECTED_PROMOTIONS),
        )
        self.assertEqual(
            lane.WAVE8_SERTORIAN_HOLD_IDS,
            {"hced-Sucro-75-1"},
        )
        self.assertEqual(
            lane.WAVE8_SERTORIAN_TERMINAL_EXCLUSION_IDS,
            {"hced-Murviedro-75-1"},
        )
        self.assertEqual(
            lane.WAVE8_SERTORIAN_RESERVED_IDS,
            frozenset(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.wave8_sertorian_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_twins": 3,
                "holds": 1,
                "new_entities": 1,
                "new_sources": 10,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.wave8_sertorian_cohort_counts(),
            {"sertorian_war_80_72_bce": 6},
        )

    def test_all_six_locked_rows_are_fully_fingerprinted(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("candidate_id") in lane.WAVE8_SERTORIAN_RESERVED_IDS
        }
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(
            lane.validate_wave8_sertorian_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 4,
                "holds": 1,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 1,
            },
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertTrue(row["do_not_rate_automatically"])
                self.assertEqual(row["review_status"], "needs_review")
                self.assertEqual(row["war_names"], ["Sertorian War"])

    def test_identity_is_conflict_bounded_alias_free_and_nonhereditary(self) -> None:
        self.assertEqual(len(lane.WAVE8_SERTORIAN_ENTITIES), 1)
        entity = lane.WAVE8_SERTORIAN_ENTITIES[0]
        Entity.from_dict(entity)
        self.assertEqual(entity["id"], SERTORIAN_FACTION)
        self.assertEqual((entity["start_year"], entity["end_year"]), (-80, -72))
        self.assertEqual(entity["kind"], "civil_war_faction")
        self.assertEqual(entity["aliases"], [])
        self.assertEqual(entity["predecessors"], [])
        note = entity["continuity_note"].casefold()
        for forbidden_bridge in (
            "roman republic",
            "populares",
            "lusitanians",
            "celtiberians",
            "individual commander",
        ):
            self.assertIn(forbidden_bridge, note)
        self.assertIn("no rating is inherited", note)
        self.assertIn("candidate-keyed contracts", note)

    def test_sources_parse_and_outcomes_have_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_SERTORIAN_SOURCES), 10)
        source_ids = set()
        for source in lane.WAVE8_SERTORIAN_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            source_ids.add(source["id"])
        self.assertEqual(len(source_ids), 10)
        for candidate_id, contract in lane.WAVE8_SERTORIAN_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]),
                    2,
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )
                self.assertLessEqual(set(contract["evidence_refs"]), source_ids)
                self.assertLessEqual(set(contract["date_source_ids"]), source_ids)

    def test_four_events_have_exact_names_ranges_confidence_and_provenance(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_PROMOTIONS))
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                contract = lane.WAVE8_SERTORIAN_CONTRACTS[candidate_id]
                self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(
                    (event["year"], event["end_year"]),
                    expected["years"],
                )
                self.assertEqual(event["date_precision"], expected["date_precision"])
                self.assertEqual(event["confidence"], expected["confidence"])
                self.assertEqual(event["war_type"], "civil_war")
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(
                    event["canonical_event_key"],
                    contract["canonical_event"]["canonical_key"],
                )
                self.assertEqual(
                    event["outcome_source_ids"],
                    contract["outcome_source_ids"],
                )
                self.assertEqual(
                    event["outcome_source_family_ids"],
                    contract["outcome_source_family_ids"],
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(event["source_ids"]),
                )
                Event.from_dict(event)

    def test_participants_and_outcomes_are_exact_and_never_draws(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            with self.subTest(candidate_id=candidate_id):
                outcomes = {
                    participant["entity_id"]: participant["termination"]
                    for participant in events[candidate_id]["participants"]
                }
                self.assertEqual(
                    outcomes,
                    {
                        expected["winner"]: "engagement_victory",
                        expected["loser"]: "engagement_defeat",
                    },
                )
                self.assertNotIn(
                    "inconclusive_engagement",
                    set(outcomes.values()),
                )
                contract = lane.WAVE8_SERTORIAN_CONTRACTS[candidate_id]
                self.assertEqual(contract["result_type"], "win")
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])

    def test_turia_is_guarded_whole_battle_roman_result_at_reduced_confidence(self) -> None:
        turia = lane.WAVE8_SERTORIAN_CONTRACTS["hced-Turia-75-1"]
        self.assertEqual(turia["side_1_entity_ids"], [ROMAN_REPUBLIC])
        self.assertEqual(turia["side_2_entity_ids"], [SERTORIAN_FACTION])
        self.assertEqual(turia["winner_side"], 1)
        self.assertEqual(turia["confidence"], 0.72)
        self.assertLess(
            turia["confidence"],
            min(
                contract["confidence"]
                for candidate_id, contract in lane.WAVE8_SERTORIAN_CONTRACTS.items()
                if candidate_id != "hced-Turia-75-1"
            ),
        )
        self.assertIn("rate_only_complete_field_battle", turia["boundary_guard"])
        self.assertIn("next-evening camp action", turia["boundary_guard"])
        self.assertIn("whole-field result", turia["audit_note"])

    def test_calahorra_is_source_supported_sertorian_relief_not_roman_win(self) -> None:
        raw = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Calahorra-74-1"
        )
        self.assertEqual(raw["winner_raw"], "Rebel Quintus Sertorius")
        self.assertEqual(raw["loser_raw"], "Rome")
        contract = lane.WAVE8_SERTORIAN_CONTRACTS["hced-Calahorra-74-1"]
        self.assertEqual(contract["side_1_entity_ids"], [SERTORIAN_FACTION])
        self.assertEqual(contract["side_2_entity_ids"], [ROMAN_REPUBLIC])
        self.assertEqual(contract["winner_side"], 1)
        self.assertFalse(contract["source_outcome_override"])
        self.assertIn("besiegers' defeat", contract["audit_note"])
        self.assertIn("72 BCE", contract["audit_note"])

    def test_sucro_stays_unknown_and_is_never_converted_to_a_draw(self) -> None:
        raw = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Sucro-75-1"
        )
        self.assertEqual(raw["winner_raw"], "Rome")
        hold = lane.WAVE8_SERTORIAN_HOLDS["hced-Sucro-75-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(hold["result_type"], "unknown")
        self.assertEqual(hold["reviewed_outcome"], "unknown")
        self.assertTrue(hold["unknown_is_never_draw"])
        self.assertNotIn("winner_side", hold)
        self.assertIn("one wing on each side", hold["hold_reason"])
        self.assertIn("never a draw", hold["hold_reason"])
        self.assertNotIn(
            "hced-Sucro-75-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_murviedro_false_draw_is_terminal_duplicate_of_turia(self) -> None:
        raw = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Murviedro-75-1"
        )
        self.assertEqual(raw["winner_raw"], "Draw")
        self.assertIsNone(raw["loser_raw"])
        self.assertFalse(raw["winner_loser_complete"])
        duplicate = lane.WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS[
            "hced-Murviedro-75-1"
        ]
        self.assertEqual(
            duplicate["disposition"],
            "exclude_duplicate_of_reviewed_candidate",
        )
        self.assertTrue(duplicate["terminal_exclusion"])
        self.assertEqual(
            duplicate["duplicate_of_candidate_id"],
            "hced-Turia-75-1",
        )
        self.assertTrue(duplicate["false_source_draw_rejected"])
        self.assertEqual(duplicate["result_type"], "unknown")
        self.assertNotIn("winner_side", duplicate)
        self.assertNotIn(
            "hced-Murviedro-75-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_all_six_points_are_quarantined_while_spain_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SERTORIAN_RESERVED_IDS,
        )
        self.assertFalse(lane.WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_SERTORIAN_RESERVED_IDS,
        )
        self.assertEqual(
            lane.wave8_sertorian_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_SERTORIAN_RESERVED_IDS,
            },
        )
        for candidate_id, reason in (
            lane.WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(reason["actions"], ["withhold_point"])
                self.assertEqual(reason["retain_modern_location_country"], "Spain")
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Spain")
            self.assertIn("location_provenance", event)

    def test_discovery_twins_are_fingerprinted_unknown_and_never_rate(self) -> None:
        self.assertEqual(
            lane.WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        rows = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if row.get("candidate_id") in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(rows), set(EXPECTED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                actual = hashlib.sha256(
                    _canonical_json(rows[candidate_id]).encode("utf-8")
                ).hexdigest()
                self.assertEqual(actual, expected_hash)
                self.assertTrue(rows[candidate_id]["do_not_rate_automatically"])
                self.assertEqual(rows[candidate_id]["winners"], [])
                disposition = lane.WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS[
                    candidate_id
                ]
                self.assertEqual(disposition["disposition"], "discovery_only_duplicate")
                self.assertEqual(
                    disposition["outcome_disposition"],
                    "unknown_never_draw",
                )
        self.assertEqual(
            lane.validate_wave8_sertorian_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_twins": 3,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 3,
            },
        )

    def test_queue_and_discovery_drift_fail_closed(self) -> None:
        for candidate_id in sorted(lane.WAVE8_SERTORIAN_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    item
                    for item in tampered
                    if item.get("candidate_id") == candidate_id
                )
                row["name"] = str(row["name"]) + " changed"
                with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                    lane.validate_wave8_sertorian_queue_contracts(tampered)

        discovery = copy.deepcopy(self.wikidata_rows)
        row = next(
            item for item in discovery if item.get("candidate_id") == "Q60524449"
        )
        row["winners"] = [{"label": "optimates", "uri": "example"}]
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_sertorian_discovery_dispositions(discovery)

    def test_entity_window_and_duplicate_event_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        shortened = copy.deepcopy(entities)
        shortened[SERTORIAN_FACTION]["start_year"] = -79
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_sertorian_contracts(
                self.hced_rows,
                shortened,
                existing,
            )

        promoted = lane.promote_wave8_sertorian_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_sertorian_contracts(
                self.hced_rows,
                entities,
                [*existing, promoted[0]],
            )
        collision = [
            *existing,
            {"name": "Battle on the Baetis", "year": -80},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_sertorian_contracts(
                self.hced_rows,
                entities,
                collision,
            )

    def test_installers_copy_and_reject_fixture_collisions(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        lane.install_wave8_sertorian_entities(entities)
        lane.install_wave8_sertorian_sources(sources)
        self.assertIn(SERTORIAN_FACTION, entities)
        self.assertEqual(len(sources), len(lane.WAVE8_SERTORIAN_SOURCES))

        entities[SERTORIAN_FACTION]["end_year"] = -71
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_sertorian_entities(entities)

        source_id = lane.WAVE8_SERTORIAN_SOURCES[0]["id"]
        sources[source_id]["title"] = "changed"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_sertorian_sources(sources)

    def test_metadata_exposes_complete_integration_inventory(self) -> None:
        metadata = lane.wave8_sertorian_metadata()
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_SERTORIAN_CONTRACT_IDS),
        )
        self.assertEqual(
            [item["candidate_id"] for item in metadata["holds"]],
            ["hced-Sucro-75-1"],
        )
        self.assertEqual(
            [item["candidate_id"] for item in metadata["terminal_exclusions"]],
            ["hced-Murviedro-75-1"],
        )
        self.assertEqual(len(metadata["discovery_dispositions"]), 3)
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
