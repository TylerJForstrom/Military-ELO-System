import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_saudi_arabia_exact as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_saudi_arabia_exact_"
PARENT_WAR_EVENT_ID = "iwd_war_48_saudi_arabia_yemen_1934"

HAMDH_IKHWAN = "faisal_al_duwaish_ikhwan_force_hamdh_1920"
HAMDH_KUWAITI = "duaij_al_sabah_kuwaiti_detachment_hamdh_1920"
JAHRA_IKHWAN = "faisal_al_duwaish_ikhwan_force_jahra_1920"
JAHRA_DEFENDERS = "salim_al_mubarak_jahra_defenders_1920"

EXPECTED_HASHES = {
    "hced-Hamad1920-1": (
        "8291d96904e856d55195e476e1c99fd1360fa544106dbed6ebed1c179caebf83"
    ),
    "hced-Hudayda1934-1": (
        "982b0581cd30aeebb9ba4f52f1b1c629d0a7c5e07a59e8a2b1f6b35d9642739e"
    ),
    "hced-Jahrah1920-1": (
        "2fd206a6b25d96db0af552f974e0638f251bf1f57a31c164f3dd4560a3d83cea"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q16839041": (
        "1854f4206f1eee996162b1cd19c506e8856c9d64f1182c122de00fb3987c8e1d"
    ),
    "Q4871302": (
        "0ae349ffb9300fdeb98a21f3c3ffc234ea86a654d24dc200e5fee039c9ebec41"
    ),
    "Q48735086": (
        "dc0afcf2b7260e3bc515525aed6e2e181445df339fa9aeb5f791fcb9772ff54c"
    ),
}

EXPECTED_IWBD_HASH = (
    "a2a2c654330cadc5e469c31d2875487cef692b36a4220fcef6b94507465eb5e2"
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _full_row_sha256(row):
    payload = json.dumps(
        row,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Wave8SaudiArabiaExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SAUDI_ARABIA_EXACT_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane.install_wave8_saudi_arabia_exact_entities(entities)

        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SAUDI_ARABIA_EXACT_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        lane.install_wave8_saudi_arabia_exact_sources(sources)

        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_saudi_arabia_exact_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_full_hced_hashes_are_locked(self):
        self.assertEqual(lane.WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS,
            {"hced-Hamad1920-1", "hced-Jahrah1920-1"},
        )
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS,
            {"hced-Hudayda1934-1"},
        )
        self.assertFalse(lane.WAVE8_SAUDI_ARABIA_EXACT_HOLDS)
        self.assertFalse(lane.WAVE8_SAUDI_ARABIA_EXACT_HOLD_IDS)

        exact_rows = [
            row
            for row in self.hced_rows
            if "saudi arabia"
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact_rows},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(len(exact_rows), 3)
        for row in exact_rows:
            candidate_id = str(row["candidate_id"])
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_HASHES[candidate_id],
                )
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_validator_pins_actor_polarity_dates_and_terminal_count(self):
        self.assertEqual(
            lane.validate_wave8_saudi_arabia_exact_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 3,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 1,
            },
        )
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        expected = {
            "hced-Hamad1920-1": (
                "Hamad",
                "Saudi Arabia",
                "Kuwait",
                "Saudi Arabia",
                "Kuwait",
                1920,
                "Saudi Arabia",
            ),
            "hced-Hudayda1934-1": (
                "Hudayda",
                "Saudi Arabia",
                "Yemen",
                "Saudi Arabia",
                "Yemen",
                1934,
                "Yemen",
            ),
            "hced-Jahrah1920-1": (
                "Jahrah",
                "Kuwait",
                "Saudi Arabia",
                "Kuwait",
                "Saudi Arabia",
                1920,
                "Kuwait",
            ),
        }
        for candidate_id, values in expected.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(
                    (
                        row["name"],
                        row["side_1_raw"],
                        row["side_2_raw"],
                        row["winner_raw"],
                        row["loser_raw"],
                        row["year_best"],
                        row["modern_location_country"],
                    ),
                    values,
                )
                self.assertEqual(
                    (row["year_low"], row["year_best"], row["year_high"]),
                    (values[5], values[5], values[5]),
                )

    def test_four_entities_are_alias_free_event_bounded_and_exactly_consumed(self):
        expected_ids = {
            HAMDH_IKHWAN,
            HAMDH_KUWAITI,
            JAHRA_IKHWAN,
            JAHRA_DEFENDERS,
        }
        self.assertEqual(
            {str(entity["id"]) for entity in lane.WAVE8_SAUDI_ARABIA_EXACT_ENTITIES},
            expected_ids,
        )
        self.assertEqual(len(lane.WAVE8_SAUDI_ARABIA_EXACT_ENTITIES), 4)
        for entity in lane.WAVE8_SAUDI_ARABIA_EXACT_ENTITIES:
            with self.subTest(entity_id=entity["id"]):
                Entity.from_dict(entity)
                self.assertEqual((entity["start_year"], entity["end_year"]), (1920, 1920))
                self.assertTrue(entity["kind"].startswith("event_bounded_"))
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("No rating is inherited", entity["continuity_note"])
                self.assertEqual(
                    entity["source_ids"],
                    sorted(set(entity["source_ids"])),
                )
                self.assertNotIn(
                    normalize_label(entity["name"]),
                    {
                        "house of al sabah",
                        "ikhwan",
                        "kuwait",
                        "mutayr",
                        "nejd",
                        "saudi",
                        "saudi arabia",
                    },
                )

        used = {
            entity_id
            for contract in lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
        }
        self.assertEqual(used, expected_ids)
        self.assertTrue(
            used.isdisjoint(
                {
                    "clio_q817_1757_7fca26e3",
                    "kingdom_saudi_arabia",
                    "mutawakkilite_kingdom_yemen",
                }
            )
        )

        entities, _, _ = self._installed()
        self.assertEqual(
            lane.validate_wave8_saudi_arabia_exact_entities(entities),
            {"required_bounded_entities": 4},
        )
        once = copy.deepcopy(entities)
        lane.install_wave8_saudi_arabia_exact_entities(entities)
        self.assertEqual(entities, once)

    def test_six_sources_parse_and_each_outcome_has_independent_families(self):
        self.assertEqual(len(lane.WAVE8_SAUDI_ARABIA_EXACT_SOURCES), 6)
        source_ids = set()
        family_ids = set()
        for source in lane.WAVE8_SAUDI_ARABIA_EXACT_SOURCES:
            with self.subTest(source_id=source["id"]):
                Source.from_dict(source)
                self.assertTrue(source["url"].startswith("https://"))
                self.assertEqual(
                    source["evidence_roles"],
                    sorted(set(source["evidence_roles"])),
                )
                source_ids.add(str(source["id"]))
                family_ids.add(str(source["source_family_id"]))
        self.assertEqual(len(source_ids), 6)
        self.assertEqual(len(family_ids), 6)

        used_sources = set()
        for candidate_id, contract in lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )
                self.assertLessEqual(
                    set(contract["date_source_ids"]),
                    set(contract["evidence_refs"]),
                )
                used_sources.update(contract["evidence_refs"])
        used_sources.update(
            lane.WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS[
                "hced-Hudayda1934-1"
            ]["evidence_refs"]
        )
        self.assertEqual(used_sources, source_ids)

    def test_promotions_have_exact_bounded_sides_and_no_draw(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Hamad1920-1": ({HAMDH_IKHWAN}, {HAMDH_KUWAITI}),
            "hced-Jahrah1920-1": ({JAHRA_DEFENDERS}, {JAHRA_IKHWAN}),
        }
        self.assertEqual(set(events), set(expected))
        self.assertNotIn("hced-Hudayda1934-1", events)
        for candidate_id, (winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                self.assertFalse(
                    any(
                        "inconclusive" in item["termination"]
                        for item in event["participants"]
                    )
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertNotIn(
                    "draw",
                    json.dumps(event, ensure_ascii=False).casefold(),
                )
                Event.from_dict(event)

    def test_hamdh_stays_year_only_and_jahra_is_10_through_11_october(self):
        hamdh = lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS["hced-Hamad1920-1"]
        jahra = lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS["hced-Jahrah1920-1"]
        self.assertEqual(
            hamdh["canonical_event"],
            {
                "canonical_key": "battle_of_hamdh:1920:1920",
                "date_precision": "year",
                "date_text": "1920 (source-day conflict: 16 May versus 18-24 May)",
                "granularity": "bounded_hamdh_engagement_not_the_broader_border_war",
                "name": "Battle of Hamdh",
                "year_low": 1920,
                "year_high": 1920,
            },
        )
        self.assertIs(hamdh["source_date_conflict"], True)
        self.assertIs(hamdh["source_date_refinement"], False)
        self.assertNotIn("source_date_override", hamdh)

        self.assertEqual(
            jahra["canonical_event"]["date_text"],
            "1920-10-10 through 1920-10-11",
        )
        self.assertEqual(jahra["canonical_event"]["date_precision"], "day_range")
        self.assertEqual(
            jahra["canonical_event"]["granularity"],
            "jahra_battle_and_red_fort_defense_through_11_october",
        )
        self.assertIs(jahra["source_date_conflict"], False)
        self.assertIs(jahra["source_date_refinement"], True)
        self.assertNotIn("source_date_override", jahra)

        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(
            (events["hced-Hamad1920-1"]["year"], events["hced-Hamad1920-1"]["end_year"]),
            (1920, 1920),
        )
        self.assertEqual(events["hced-Hamad1920-1"]["date_precision"], "year")
        self.assertEqual(
            (events["hced-Jahrah1920-1"]["year"], events["hced-Jahrah1920-1"]["end_year"]),
            (1920, 1920),
        )
        self.assertEqual(events["hced-Jahrah1920-1"]["date_precision"], "day_range")

    def test_hudayda_is_unopposed_terminal_exclusion_and_parent_war_duplicate(self):
        exclusion = lane.WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS[
            "hced-Hudayda1934-1"
        ]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertIs(exclusion["terminal_exclusion"], True)
        self.assertEqual(
            exclusion["exclusion_category"],
            "unopposed_occupation_duplicate_parent_war",
        )
        self.assertEqual(
            exclusion["reviewed_outcome"],
            "not_rateable_unopposed_occupation",
        )
        self.assertIs(exclusion["unknown_is_never_draw"], True)
        self.assertEqual(
            exclusion["duplicate_of_existing_event_id"],
            PARENT_WAR_EVENT_ID,
        )
        self.assertEqual(
            exclusion["canonical_event"]["date_text"],
            "1934-05-05",
        )
        self.assertIn("withdrew before Saudi forces entered", exclusion["exclusion_reason"])
        for forbidden in (
            "loser_entity_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_entity_ids",
            "winner_side",
        ):
            self.assertNotIn(forbidden, exclusion)

        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_saudi_arabia_exact_existing_parent_war(existing),
            {"existing_parent_war_owners": 1},
        )
        owner = next(event for event in existing if event["id"] == PARENT_WAR_EVENT_ID)
        self.assertEqual(owner["event_type"], "war")
        self.assertEqual(
            {
                (item["entity_id"], item["termination"])
                for item in owner["participants"]
            },
            {
                ("kingdom_saudi_arabia", "victory"),
                ("mutawakkilite_kingdom_yemen", "defeat"),
            },
        )

    def test_two_points_are_quarantined_without_country_or_window_changes(self):
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS,
            {"hced-Hamad1920-1", "hced-Jahrah1920-1"},
        )
        self.assertFalse(lane.WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            lane.wave8_saudi_arabia_exact_location_quarantine_additions(),
            {"country": 0, "point": 2},
        )
        self.assertEqual(
            set(lane.WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS),
            set(EXPECTED_HASHES),
        )

        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertNotIn("geometry", events["hced-Hamad1920-1"])
        self.assertEqual(
            events["hced-Hamad1920-1"]["modern_location_country"],
            "Saudi Arabia",
        )
        self.assertIn("location_provenance", events["hced-Hamad1920-1"])
        self.assertNotIn("geometry", events["hced-Jahrah1920-1"])
        self.assertEqual(
            events["hced-Jahrah1920-1"]["modern_location_country"],
            "Kuwait",
        )
        self.assertIn("location_provenance", events["hced-Jahrah1920-1"])

    def test_event_source_provenance_is_closed_to_each_contract(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        forbidden_aliases = {"ikhwan", "kuwait", "saudi", "saudi arabia"}
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS[candidate_id]
                self.assertEqual(
                    event["source_ids"],
                    ["hced_dataset", *contract["evidence_refs"]],
                )
                self.assertEqual(
                    event["outcome_source_ids"],
                    contract["outcome_source_ids"],
                )
                self.assertEqual(
                    event["outcome_source_family_ids"],
                    contract["outcome_source_family_ids"],
                )
                self.assertNotIn("hced_dataset", event["outcome_source_ids"])
                self.assertIn(contract["audit_note"], event["summary"])
                self.assertTrue(
                    forbidden_aliases.isdisjoint(
                        {normalize_label(alias) for alias in event.get("aliases", [])}
                    )
                )

    def test_discovery_rows_are_fully_hashed_and_strictly_nonrating(self):
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        self.assertEqual(
            set(lane.WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS),
            {"Q16839041", "Q4871302"},
        )
        self.assertEqual(
            set(lane.WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS),
            {"Q48735086"},
        )
        self.assertEqual(
            set(lane.WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS),
            {"iwbd-125-48-872"},
        )
        self.assertEqual(
            lane.validate_wave8_saudi_arabia_exact_discovery_dispositions(
                self.wikidata_rows,
                self.iwbd_rows,
            ),
            {
                "discovery_promotions": 0,
                "iwbd_discovery_duplicates": 1,
                "unknown_never_draw_wikidata_rows": 3,
                "wikidata_discovery_duplicates": 2,
                "wikidata_false_twins": 1,
            },
        )

        wikidata = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(wikidata), set(EXPECTED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(_full_row_sha256(wikidata[candidate_id]), expected_hash)
                self.assertIs(wikidata[candidate_id]["do_not_rate_automatically"], True)
                self.assertEqual(wikidata[candidate_id]["winners"], [])
        self.assertEqual(wikidata["Q16839041"]["name"], "Battle of Hamdh")
        self.assertEqual(wikidata["Q4871302"]["name"], "Battle of Jahra")
        self.assertEqual(wikidata["Q48735086"]["date"][:4], "2018")
        self.assertEqual(
            lane.WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS[
                "Q48735086"
            ]["disposition"],
            "discovery_only_false_twin",
        )

        iwbd = next(
            row
            for row in self.iwbd_rows
            if row.get("candidate_id") == "iwbd-125-48-872"
        )
        self.assertEqual(_full_row_sha256(iwbd), EXPECTED_IWBD_HASH)
        disposition = lane.WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS[
            "iwbd-125-48-872"
        ]
        self.assertEqual(disposition["rating_disposition"], "nonrating")
        self.assertEqual(disposition["hced_candidate_id"], "hced-Hudayda1934-1")
        self.assertEqual(
            disposition["existing_release_event_id"],
            PARENT_WAR_EVENT_ID,
        )

    def test_integration_audit_accepts_declared_rows_and_rejects_future_twins(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_saudi_arabia_exact_integration_dispositions(
                self.hced_rows,
                self.wikidata_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_parent_war_owners": 1,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_discovery_duplicates": 1,
                "iwbd_probable_twins": 0,
                "wikidata_discovery_duplicates": 2,
                "wikidata_false_twins": 1,
                "wikidata_probable_twins": 0,
            },
        )

        future_wikidata = [
            *copy.deepcopy(self.wikidata_rows),
            {
                "candidate_id": "Q-future-jahra-twin",
                "name": "Jahrah",
                "date": "1920-10-10T00:00:00Z",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_saudi_arabia_exact_integration_dispositions(
                self.hced_rows,
                future_wikidata,
                self.iwbd_rows,
                existing,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-hamdh-twin",
                "name": "Battle of Hamdh",
                "start_date": "1920-01-01",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_saudi_arabia_exact_integration_dispositions(
                self.hced_rows,
                self.wikidata_rows,
                future_iwbd,
                existing,
            )

    def test_row_discovery_entity_and_parent_drift_fail_closed(self):
        tampered_hced = copy.deepcopy(self.hced_rows)
        hced_row = next(
            row
            for row in tampered_hced
            if row.get("candidate_id") == "hced-Hamad1920-1"
        )
        hced_row["participants_raw"].append("invented participant")
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_saudi_arabia_exact_queue_contracts(tampered_hced)

        future_exact = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureSaudiArabia1921-1",
                "name": "Future action",
                "side_1_raw": "Saudi Arabia",
                "side_2_raw": "Kuwait",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_saudi_arabia_exact_queue_contracts(future_exact)

        tampered_wikidata = copy.deepcopy(self.wikidata_rows)
        wikidata_row = next(
            row
            for row in tampered_wikidata
            if row.get("candidate_id") == "Q4871302"
        )
        wikidata_row["winners"] = [{"label": "invented", "uri": "Q0"}]
        with self.assertRaisesRegex(ValueError, "Wikidata fingerprint changed"):
            lane.validate_wave8_saudi_arabia_exact_discovery_dispositions(
                tampered_wikidata,
                self.iwbd_rows,
            )

        entities, _, existing = self._installed()
        broken_entities = copy.deepcopy(entities)
        broken_entities[HAMDH_IKHWAN]["end_year"] = 1921
        with self.assertRaisesRegex(ValueError, "bounded entity drift"):
            lane.promote_wave8_saudi_arabia_exact_contracts(
                self.hced_rows,
                broken_entities,
                existing,
            )

        broken_parent = copy.deepcopy(existing)
        parent = next(event for event in broken_parent if event["id"] == PARENT_WAR_EVENT_ID)
        parent["event_type"] = "engagement"
        with self.assertRaisesRegex(ValueError, "parent-war owner changed"):
            lane.validate_wave8_saudi_arabia_exact_existing_parent_war(broken_parent)

    def test_install_collisions_duplicate_promotion_and_unrelated_rows_fail_safely(self):
        entities, sources, existing = self._installed()
        broken_entities = copy.deepcopy(entities)
        broken_entities[HAMDH_IKHWAN]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_saudi_arabia_exact_entities(broken_entities)

        source_id = str(lane.WAVE8_SAUDI_ARABIA_EXACT_SOURCES[0]["id"])
        broken_sources = copy.deepcopy(sources)
        broken_sources[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_saudi_arabia_exact_sources(broken_sources)

        promoted = lane.promote_wave8_saudi_arabia_exact_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_saudi_arabia_exact_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

        unrelated = {
            "candidate_id": "hced-unrelated-saudi-token",
            "name": "Unreviewed action",
            "year_low": 1920,
            "year_best": 1920,
            "year_high": 1920,
            "side_1_raw": "Saudis",
            "side_2_raw": "Rashidis",
            "winner_raw": "Draw",
            "loser_raw": None,
        }
        events = lane.promote_wave8_saudi_arabia_exact_contracts(
            [*self.hced_rows, unrelated],
            entities,
            existing,
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            {"hced-Hamad1920-1", "hced-Jahrah1920-1"},
        )

    def test_counts_metadata_signature_and_source_install_are_sealed(self):
        expected_counts = {
            "country_quarantine_additions": 0,
            "discovery_nonrating_rows": 4,
            "holds": 0,
            "integration_dispositions": 5,
            "iwbd_discovery_duplicates": 1,
            "new_entities": 4,
            "new_sources": 6,
            "newly_rated_events": 2,
            "outcome_overrides": 0,
            "point_quarantine_additions": 2,
            "promotion_contracts": 2,
            "reviewed_hced_rows": 3,
            "terminal_exclusions": 1,
            "wikidata_discovery_duplicates": 2,
            "wikidata_false_twins": 1,
        }
        self.assertEqual(lane.wave8_saudi_arabia_exact_counts(), expected_counts)
        self.assertEqual(
            lane.wave8_saudi_arabia_exact_cohort_counts(),
            {"kuwait_najd_border_war_1920": 2},
        )
        self.assertEqual(
            lane.wave8_saudi_arabia_exact_audit_signature(),
            "1345c7103f37f0b1234f63c0da8d7b9e3e4f23b8ae0372c14fa54377b50ee1f1",
        )
        self.assertEqual(
            lane.wave8_saudi_arabia_exact_audit_signature(),
            lane.WAVE8_SAUDI_ARABIA_EXACT_FINAL_AUDIT_SIGNATURE,
        )

        metadata = lane.wave8_saudi_arabia_exact_metadata()
        self.assertEqual(metadata["counts"], expected_counts)
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            ["hced-Hamad1920-1", "hced-Jahrah1920-1"],
        )
        self.assertEqual(metadata["hold_candidate_ids"], [])
        self.assertEqual(
            metadata["terminal_exclusion_candidate_ids"],
            ["hced-Hudayda1934-1"],
        )
        self.assertEqual(len(metadata["discovery_nonrating_candidate_ids"]), 4)

        _, sources, _ = self._installed()
        once = copy.deepcopy(sources)
        lane.install_wave8_saudi_arabia_exact_sources(sources)
        self.assertEqual(sources, once)
        self.assertLessEqual(
            {str(source["id"]) for source in lane.WAVE8_SAUDI_ARABIA_EXACT_SOURCES},
            set(sources),
        )


if __name__ == "__main__":
    unittest.main()
