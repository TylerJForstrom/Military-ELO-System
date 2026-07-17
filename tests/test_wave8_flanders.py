import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_flanders as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_flanders_"

COURTRAI_FLEMISH = "flemish_communal_army_courtrai_1302"
COURTRAI_FRENCH = "robert_artois_french_royal_army_courtrai_1302"
MONS_FRENCH = "philip_iv_french_royal_army_mons_en_pevele_1304"
MONS_FLEMISH = "flemish_resistance_army_mons_en_pevele_1304"
ZIERIKZEE_FRANCO_GENOESE = (
    "rainier_grimaldi_french_genoese_fleet_zierikzee_1304"
)
ZIERIKZEE_HOLLAND = "william_avesnes_holland_zeeland_force_zierikzee_1304"
ZIERIKZEE_FLEMISH = "guy_namur_flemish_fleet_zierikzee_1304"
CASSEL_FRENCH = "philip_vi_french_royal_army_cassel_1328"
CASSEL_FLEMISH = "zannekin_flemish_coast_rebel_army_cassel_1328"


EXPECTED_RAW_HASHES = {
    "hced-Cassel1328-1": (
        "b9fbf94bf147838713bbcc9c5523281e98b8b0b0e68d91be4b08bbb2f783905b"
    ),
    "hced-Courtrai1302-1": (
        "96c9568e26b8c6bd93186cf415c2e811bd978d1146792947b0f0a8464c0fc9aa"
    ),
    "hced-Mons-en-Pevele1304-1": (
        "59e4182daa03c314845e5dc76d09c83fd7e0931ca264c622eba98d6fce1c7f09"
    ),
    "hced-Zieriksee1304-1": (
        "7a671a835ba8d4c6d9c192d4a6b41571ce4280b5b7ac9bdfab99dd40b0853838"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Courtrai1302-1": {
        "name": "Courtrai",
        "side_1": "Flanders",
        "side_2": "France",
        "winner": "Flanders",
        "loser": "France",
        "year": 1302,
        "point": [3.2577263, 50.8194776],
        "country": "Belgium",
    },
    "hced-Zieriksee1304-1": {
        "name": "Zieriksee",
        "side_1": "France",
        "side_2": "Flanders",
        "winner": "France",
        "loser": "Flanders",
        "year": 1304,
        "point": [3.9184977, 51.6501218],
        "country": "Netherlands",
    },
    "hced-Mons-en-Pevele1304-1": {
        "name": "Mons-en-Pevele",
        "side_1": "France",
        "side_2": "Flanders",
        "winner": "France",
        "loser": "Flanders",
        "year": 1304,
        "point": [3.099575, 50.480352],
        "country": "France",
    },
    "hced-Cassel1328-1": {
        "name": "Cassel",
        "side_1": "France",
        "side_2": "Flanders",
        "winner": "France",
        "loser": "Flanders",
        "year": 1328,
        "point": [2.486235, 50.8000619],
        "country": "France",
    },
}

EXPECTED_ACTORS = {
    "hced-Courtrai1302-1": ({COURTRAI_FLEMISH}, {COURTRAI_FRENCH}),
    "hced-Zieriksee1304-1": (
        {ZIERIKZEE_FRANCO_GENOESE, ZIERIKZEE_HOLLAND},
        {ZIERIKZEE_FLEMISH},
    ),
    "hced-Mons-en-Pevele1304-1": ({MONS_FRENCH}, {MONS_FLEMISH}),
    "hced-Cassel1328-1": ({CASSEL_FRENCH}, {CASSEL_FLEMISH}),
}

EXPECTED_CANONICAL = {
    "hced-Courtrai1302-1": (
        "Battle of the Golden Spurs",
        "11 July 1302",
        "day",
        "pitched_battle",
    ),
    "hced-Zieriksee1304-1": (
        "Battle of Zierikzee",
        "10-11 August 1304",
        "day_range",
        "naval_battle_and_siege_relief",
    ),
    "hced-Mons-en-Pevele1304-1": (
        "Battle of Mons-en-Pévèle",
        "18 August 1304",
        "day",
        "pitched_battle",
    ),
    "hced-Cassel1328-1": (
        "Battle of Cassel (1328)",
        "23 August 1328",
        "day",
        "pitched_battle",
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
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class Wave8FlandersTests(unittest.TestCase):
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
            if normalize_label(row.get("side_1_raw")) == "flanders"
            or normalize_label(row.get("side_2_raw")) == "flanders"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_FLANDERS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_FLANDERS_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_FLANDERS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_flanders_entities(entities)
        lane.install_wave8_flanders_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_flanders_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_funnel_and_candidate_digest_are_pinned(self):
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, lane.WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS)
        candidate_payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(exact_ids)
        )
        digest = hashlib.sha256(candidate_payload.encode()).hexdigest()
        self.assertEqual(digest, lane.WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(
            digest,
            lane.WAVE8_FLANDERS_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )

        records = [
            record
            for record in self.funnel["labels"]
            if record.get("label") == "flanders"
        ]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["event_candidate_id_sha256"], digest)
        self.assertEqual(record["events_touched"], 4)
        self.assertEqual(record["sole_blocker_events"], 4)
        self.assertEqual(record["unresolved_side_attempts"], 4)
        self.assertEqual(record["centuries"], {"CE_14": 4})
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
            if "flanders" in row.get("blocker_labels", [])
        }
        self.assertEqual(funnel_ids, exact_ids)

    def test_raw_rows_and_outcomes_are_fully_pinned(self):
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1"])
                self.assertEqual(row["side_2_raw"], expected["side_2"])
                self.assertEqual(row["winner_raw"], expected["winner"])
                self.assertEqual(row["loser_raw"], expected["loser"])
                self.assertTrue(row["winner_loser_complete"])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(row["modern_location_country"], expected["country"])
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_RAW_HASHES[candidate_id],
                )
                self.assertEqual(
                    lane.WAVE8_FLANDERS_CONTRACTS[candidate_id][
                        "raw_row_sha256"
                    ],
                    EXPECTED_RAW_HASHES[candidate_id],
                )

    def test_queue_validator_accounts_for_all_and_only_exact_flanders(self):
        self.assertEqual(
            lane.validate_wave8_flanders_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.WAVE8_FLANDERS_RESERVED_IDS,
            lane.WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertFalse(lane.WAVE8_FLANDERS_HOLDS)
        self.assertFalse(lane.WAVE8_FLANDERS_TERMINAL_EXCLUSIONS)
        self.assertFalse(lane.WAVE8_FLANDERS_NONPROMOTIONS)
        self.assertFalse(lane.WAVE8_FLANDERS_OUTCOME_OVERRIDES)

        # Similar but non-exact labels remain owned elsewhere.
        exact_ids = set(lane.WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS)
        self.assertNotIn("hced-Furnes1297-1", exact_ids)
        self.assertNotIn("hced-Bruges1302-1", exact_ids)
        self.assertTrue(
            any(
                row.get("candidate_id") == "hced-Furnes1297-1"
                and row.get("side_2_raw") == "County of Flanders"
                for row in self.hced_rows
            )
        )
        self.assertTrue(
            any(
                row.get("candidate_id") == "hced-Bruges1302-1"
                and row.get("side_1_raw") == "Flemish Rebels"
                for row in self.hced_rows
            )
        )

    def test_sources_and_nine_event_bounded_entities_parse(self):
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_FLANDERS_SOURCES
        }
        entity_by_id = {
            str(entity["id"]): entity for entity in lane.WAVE8_FLANDERS_ENTITIES
        }
        self.assertEqual(len(source_by_id), 15)
        self.assertEqual(
            len({source["source_family_id"] for source in source_by_id.values()}),
            15,
        )
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        expected_entity_ids = set().union(
            *(side_1 | side_2 for side_1, side_2 in EXPECTED_ACTORS.values())
        )
        self.assertEqual(set(entity_by_id), expected_entity_ids)
        self.assertEqual(len(entity_by_id), 9)
        for entity in entity_by_id.values():
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("county of flanders", note)
            self.assertIn("burgundian", note)
            self.assertIn("dutch republic", note)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        forbidden = {
            "belgium",
            "burgundy",
            "county of flanders",
            "dutch republic",
            "flanders",
            "france",
            "netherlands",
        }
        self.assertTrue(forbidden.isdisjoint(entity_by_id))

        consumed = {
            source_id
            for entity in lane.WAVE8_FLANDERS_ENTITIES
            for source_id in entity["source_ids"]
        }
        for contract in lane.WAVE8_FLANDERS_CONTRACTS.values():
            consumed.update(contract["evidence_refs"])
        for review in lane.WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS.values():
            consumed.update(review["evidence_refs"])
        for disposition in lane.WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.values():
            consumed.update(disposition["evidence_refs"])
        for disposition in lane.WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS.values():
            consumed.update(disposition["evidence_refs"])
        self.assertEqual(consumed, set(source_by_id))

    def test_contracts_pin_canonical_events_actors_and_direct_results(self):
        self.assertEqual(set(lane.WAVE8_FLANDERS_CONTRACTS), set(EXPECTED_ACTORS))
        for candidate_id, contract in lane.WAVE8_FLANDERS_CONTRACTS.items():
            expected_side_1, expected_side_2 = EXPECTED_ACTORS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_side_2)
            name, date_text, precision, granularity = EXPECTED_CANONICAL[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(canonical["date_text"], date_text)
            self.assertEqual(canonical["date_precision"], precision)
            self.assertEqual(canonical["granularity"], granularity)
            self.assertEqual(
                canonical["year_low"], EXPECTED_RAW_ROWS[candidate_id]["year"]
            )
            self.assertEqual(canonical["year_high"], canonical["year_low"])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 3)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)

    def test_mons_is_a_bounded_tactical_win_not_an_invented_strategic_result(self):
        candidate_id = "hced-Mons-en-Pevele1304-1"
        contract = lane.WAVE8_FLANDERS_CONTRACTS[candidate_id]
        self.assertEqual(contract["confidence"], 0.88)
        self.assertIn("competing victory claims", contract["audit_note"])
        self.assertIn("held the battlefield", contract["audit_note"])
        self.assertIn("reduced confidence", contract["audit_note"])
        self.assertIn("does not infer", contract["audit_note"])
        self.assertFalse(contract["source_outcome_override"])
        raw = next(
            row for row in self.hced_rows if row.get("candidate_id") == candidate_id
        )
        self.assertEqual(raw["winner_raw"], raw["side_1_raw"])
        self.assertEqual(raw["loser_raw"], raw["side_2_raw"])

    def test_zierikzee_resolves_the_actual_allied_fleet_not_dutch_republic(self):
        contract = lane.WAVE8_FLANDERS_CONTRACTS["hced-Zieriksee1304-1"]
        self.assertEqual(
            set(contract["side_1_entity_ids"]),
            {ZIERIKZEE_FRANCO_GENOESE, ZIERIKZEE_HOLLAND},
        )
        self.assertEqual(contract["side_2_entity_ids"], [ZIERIKZEE_FLEMISH])
        self.assertIn("not a Dutch Republic event", contract["audit_note"])
        dutch = lane.WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS["dutch"]
        self.assertEqual(dutch["candidate_ids"], ["hced-Zieriksee1304-1"])
        self.assertEqual(
            dutch["disposition"],
            "medieval_holland_zeeland_not_dutch_republic",
        )

    def test_cassel_is_rebels_against_valois_not_county_or_burgundy(self):
        contract = lane.WAVE8_FLANDERS_CONTRACTS["hced-Cassel1328-1"]
        self.assertEqual(contract["side_1_entity_ids"], [CASSEL_FRENCH])
        self.assertEqual(contract["side_2_entity_ids"], [CASSEL_FLEMISH])
        self.assertIn("1328 rebels", contract["audit_note"])
        self.assertIn("later Burgundian state", contract["audit_note"])
        self.assertNotIn(
            "clio_fr_capetian_k_1_990_39dc2541",
            {*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]},
        )

    def test_four_events_promote_without_draws_or_generic_identity_fallback(self):
        events = self._events()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), lane.WAVE8_FLANDERS_CONTRACT_IDS)
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                EXPECTED_RAW_ROWS[candidate_id]["country"],
            )
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
            self.assertEqual((winners, losers), EXPECTED_ACTORS[candidate_id])
            self.assertFalse(
                any(
                    participant["result_class"] == "draw"
                    for participant in event["participants"]
                )
            )
        self.assertEqual(by_candidate["hced-Zieriksee1304-1"]["domain"], "naval")
        self.assertEqual(
            by_candidate["hced-Zieriksee1304-1"]["aliases"],
            ["Zieriksee"],
        )
        self.assertEqual(
            by_candidate["hced-Courtrai1302-1"]["aliases"],
            ["Courtrai"],
        )

    def test_france_county_burgundy_and_dutch_overlap_audits_are_explicit(self):
        adjacent = lane.WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS
        self.assertIs(lane.WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS, adjacent)
        self.assertEqual(
            set(adjacent),
            {"burgundy", "dutch", "france", "medieval_county_of_flanders"},
        )
        self.assertEqual(
            adjacent["france"]["candidate_ids"],
            sorted(lane.WAVE8_FLANDERS_CONTRACT_IDS),
        )
        self.assertEqual(
            adjacent["france"]["forbidden_generic_entity_ids"],
            ["kingdom_france"],
        )
        self.assertEqual(
            adjacent["medieval_county_of_flanders"]["existing_entity_id"],
            "clio_fr_capetian_k_1_990_39dc2541",
        )
        self.assertEqual(
            adjacent["medieval_county_of_flanders"]["related_existing_event_id"],
            "hced_label_hced_furnes1297_1",
        )
        self.assertEqual(
            adjacent["burgundy"]["burgundian_flanders_start_year"],
            1384,
        )
        self.assertLess(
            max(item["canonical_event"]["year_high"] for item in lane.WAVE8_FLANDERS_CONTRACTS.values()),
            adjacent["burgundy"]["burgundian_flanders_start_year"],
        )

        actor_ids = {
            entity_id
            for contract in lane.WAVE8_FLANDERS_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertTrue(
            actor_ids.isdisjoint(
                {
                    "kingdom_france",
                    "clio_fr_capetian_k_1_990_39dc2541",
                    "dutch_republic",
                }
            )
        )

    def test_related_but_distinct_hced_and_release_owners_are_pinned(self):
        related = lane.WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS
        self.assertEqual(set(related), {"hced-Bruges1302-1", "hced-Furnes1297-1"})
        self.assertEqual(
            related["hced-Bruges1302-1"]["disposition"],
            "related_distinct_hced_event",
        )
        furnes = related["hced-Furnes1297-1"]
        self.assertEqual(
            furnes["disposition"],
            "related_distinct_existing_release_event",
        )
        self.assertEqual(furnes["owner_event_id"], "hced_label_hced_furnes1297_1")
        self.assertEqual(
            furnes["owner_entity_id"],
            "clio_fr_capetian_k_1_990_39dc2541",
        )
        owner = [
            event
            for event in self.release_events
            if event.get("id") == furnes["owner_event_id"]
            and event.get("hced_candidate_id") == "hced-Furnes1297-1"
        ]
        self.assertEqual(len(owner), 1)
        self.assertFalse(lane.WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)

    def test_integration_validator_accepts_audited_distinctions_and_old_namesakes(self):
        self.assertEqual(
            lane.validate_wave8_flanders_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 4,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 6,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
                "related_hced_dispositions": 2,
            },
        )
        # Same place-name battles in 1576, 1677, 1794, 1813, and 1918 are
        # deliberately not swept into the medieval duplicate window.
        namesakes = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if normalize_label(event.get("name"))
            in {"cassel", "courtrai", "zieriksee"}
        }
        self.assertTrue(
            {
                "hced-Cassel1677-1",
                "hced-Cassel1813-1",
                "hced-Courtrai1794-1",
                "hced-Courtrai1918-1",
                "hced-Zieriksee1575-1576-1",
            }
            <= namesakes
        )

    def test_duplicate_guards_fail_closed_for_hced_iwbd_and_release(self):
        hced = copy.deepcopy(self.hced_rows)
        duplicate = copy.deepcopy(
            next(
                row
                for row in hced
                if row.get("candidate_id") == "hced-Courtrai1302-1"
            )
        )
        duplicate["candidate_id"] = "hced-invented-golden-spurs-twin"
        duplicate["source_record_id"] = "invented"
        duplicate["source_row"] = 999999
        duplicate["side_1_raw"] = "Flemish Rebels"
        duplicate["winner_raw"] = "Flemish Rebels"
        hced.append(duplicate)
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_flanders_integration_dispositions(
                hced,
                self.iwbd_rows,
                self.release_events,
            )

        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-invented-zierikzee",
                "name": "Battle of Zierikzee",
                "start_date": "1304-08-10",
                "end_date": "1304-08-11",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_flanders_integration_dispositions(
                self.hced_rows,
                iwbd,
                self.release_events,
            )

        release = copy.deepcopy(self.release_events)
        release.append(
            {
                "id": "invented_cassel_1328_twin",
                "name": "Battle of Cassel",
                "year": 1328,
                "hced_candidate_id": "hced-unrelated-invented",
            }
        )
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_flanders_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release,
            )

    def test_raw_and_related_row_drift_fail_closed(self):
        drifted = copy.deepcopy(self.hced_rows)
        exact = next(
            row
            for row in drifted
            if row.get("candidate_id") == "hced-Mons-en-Pevele1304-1"
        )
        exact["winner_raw"] = "Draw"
        exact["loser_raw"] = None
        exact["winner_loser_complete"] = False
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.validate_wave8_flanders_queue_contracts(drifted)

        related = copy.deepcopy(self.hced_rows)
        furnes = next(
            row
            for row in related
            if row.get("candidate_id") == "hced-Furnes1297-1"
        )
        furnes["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "related HCED fingerprint changed"):
            lane.validate_wave8_flanders_integration_dispositions(
                related,
                self.iwbd_rows,
                self.release_events,
            )

        extra = copy.deepcopy(self.hced_rows)
        invented = copy.deepcopy(self.exact_rows[0])
        invented["candidate_id"] = "hced-InventedFlanders999-1"
        invented["source_record_id"] = "InventedFlanders999"
        invented["source_row"] = 999999
        extra.append(invented)
        with self.assertRaisesRegex(ValueError, "exact Flanders inventory changed"):
            lane.validate_wave8_flanders_queue_contracts(extra)

    def test_promoter_rejects_candidate_and_event_key_duplicates(self):
        entities, _, existing = self._installed()
        duplicate_candidate = copy.deepcopy(existing)
        duplicate_candidate.append(
            {
                "id": "existing_candidate",
                "name": "Unrelated",
                "year": 1302,
                "hced_candidate_id": "hced-Courtrai1302-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_flanders_contracts(
                self.hced_rows,
                entities,
                duplicate_candidate,
            )

        duplicate_key = copy.deepcopy(existing)
        duplicate_key.append(
            {
                "id": "existing_key",
                "name": "Battle of Zierikzee",
                "year": 1304,
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_flanders_contracts(
                self.hced_rows,
                entities,
                duplicate_key,
            )

    def test_local_location_quarantines_withhold_only_points(self):
        self.assertEqual(
            lane.WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_FLANDERS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            lane.wave8_flanders_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_FLANDERS_CONTRACT_IDS,
            },
        )
        for candidate_id, review in lane.WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS.items():
            expected = EXPECTED_RAW_ROWS[candidate_id]
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(review["raw_point"], expected["point"])
            self.assertEqual(review["retained_country"], expected["country"])

        point_overlap = (
            set(lane.WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS)
            & set(HCED_POINT_QUARANTINE_IDS)
        )
        self.assertIn(
            point_overlap,
            [set(), set(lane.WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS)],
        )
        self.assertFalse(
            set(lane.WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS)
            & set(HCED_COUNTRY_QUARANTINE_IDS)
        )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entity_snapshot = copy.deepcopy(entities)
        source_snapshot = copy.deepcopy(sources)
        lane.install_wave8_flanders_entities(entities)
        lane.install_wave8_flanders_sources(sources)
        self.assertEqual(entities, entity_snapshot)
        self.assertEqual(sources, source_snapshot)

        bad_entities = copy.deepcopy(entities)
        bad_entities[COURTRAI_FLEMISH]["name"] = "Collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_flanders_entities(bad_entities)
        bad_sources = copy.deepcopy(sources)
        bad_sources["wave8_flanders_sayers_zierikzee"]["title"] = "Collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_flanders_sources(bad_sources)

    def test_signature_counts_and_cohorts_are_exact(self):
        payload = {
            "adjacent_lane_dispositions": (
                lane.WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS
            ),
            "contracts": lane.WAVE8_FLANDERS_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": lane.WAVE8_FLANDERS_ENTITIES,
            "exact_candidate_id_sha256": (
                lane.WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256
            ),
            "existing_release_duplicate_dispositions": (
                lane.WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                lane.WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS
            ),
            "holds": lane.WAVE8_FLANDERS_HOLDS,
            "integration_dispositions": (
                lane.WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS
            ),
            "iwbd_duplicate_dispositions": (
                lane.WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": (
                lane.WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT
            ),
            "location_quarantine_reasons": (
                lane.WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": lane.WAVE8_FLANDERS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                lane.WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": (
                lane.WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS
            ),
            "sources": lane.WAVE8_FLANDERS_SOURCES,
            "terminal_exclusions": lane.WAVE8_FLANDERS_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            independent,
            "034bfa92592342b07bfe8eed76ef2663063c7a2f7d2d165f952247c02458a0f3",
        )
        self.assertEqual(independent, lane.WAVE8_FLANDERS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(independent, lane.wave8_flanders_audit_signature())
        self.assertEqual(
            lane.wave8_flanders_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 4,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 6,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 9,
                "new_sources": 15,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_flanders_cohort_counts(),
            {
                "flemish_coast_revolt_1323_1328": 1,
                "franco_flemish_war_1297_1305": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
