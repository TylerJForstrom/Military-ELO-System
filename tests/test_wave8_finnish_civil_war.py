import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_finnish_civil_war as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_finnish_civil_war_"
WHITE = "finnish_white_army_1918"
RED = "finnish_red_guard_1918"
OULU_GARRISON = "oulu_russian_garrison_1918"
RAUTU_DETACHMENTS = "petrograd_red_detachments_rautu_1918"

EXPECTED_HASHES = {
    "hced-Aland1918-1": (
        "038ee0befb47d722d931f2a84c3492811cdeb8223d783298b7b24fe1ac5b5f52"
    ),
    "hced-Oulo1918-1": (
        "f5c755515b1f381fac6a4eff4dfd4892bd92096e16a6728becd154da2af47a63"
    ),
    "hced-Rautu1918-1": (
        "ab2a0a02f6a2c2cbf7afcb2c9237a539d637aeefcba08fb8bebf159164d979d5"
    ),
    "hced-Ruovesi1918-1": (
        "9771543cc768a823bbdd58147c3df523d8a84a45584ca08250d415851071c37c"
    ),
    "hced-Sigurds1918-1": (
        "00088d1db647599f7ef6aa70a66ec79e9bf67956cac2e3cf48a4b7ee2cd1857b"
    ),
    "hced-Tampere1918-1": (
        "1231b94b6ac2165ac0594913db6f135bc12cbdebd57f25a1e8346a1c827804e3"
    ),
    "hced-Vilppula1918-1": (
        "39b3bd4b9458573ccd494812f56bf76be55c7de902d00642a87e0f580758b869"
    ),
    "hced-Vyborg1918-1": (
        "30c5358629858af1a854221739d5dab7185ec0d9ba59a729f69f229623626a4d"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q10681754": (
        "a0967b46697774017ad330a25a95354bef77e2f46062f655d358c5e1829c266f"
    ),
    "Q18661133": (
        "a72ac94d73997f92a3e116f53b741079c5b4777ff2eede134eaa8d3fe9cdc8e1"
    ),
    "Q2043711": (
        "a58630f4a212bba77170322fc15a93189bb886d7d776fbabfb31340209dfebad"
    ),
    "Q27839492": (
        "1c731c305c26d57faa4b797856f93f605b8ce34bac13c251b6ab1b8acf1ebdae"
    ),
    "Q28721640": (
        "9029477ddab08b44335b43fdd61bbb7b816a9caee7b9d2f0adf25e4742a877a9"
    ),
    "Q4060498": (
        "e9268a7d4f7f02cc48e2ae4d127fe1aede62a63de9b7c0b592cf77d51326ef15"
    ),
    "Q4411911": (
        "6cc0fa9582d11522a3e203942dfa015b8b07d9d2f82e8f6beb56595943317ed4"
    ),
}


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


def _historical_funnel():
    return {
        "labels": [
            copy.deepcopy(row)
            for _, row in sorted(lane.WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT.items())
        ]
    }


class Wave8FinnishCivilWarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd_rows = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_FINNISH_CIVIL_WAR_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_finnish_civil_war_entities(entities)
        lane.install_wave8_finnish_civil_war_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_finnish_civil_war_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_eight_row_inventory_and_semantic_hashes_are_pinned(self):
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("year_best") == 1918
            and set(row.get("war_names", []))
            & {"Finnish War", "Finnish War of Independence"}
            and normalize_label(row.get("side_1_raw"))
            in {
                "bolsheviks",
                "finland",
                "finnish reds",
                "finnish whites",
                "russian bolsheviks",
                "ussr",
            }
            and normalize_label(row.get("side_2_raw"))
            in {
                "bolsheviks",
                "finland",
                "finnish reds",
                "finnish whites",
                "russian bolsheviks",
                "ussr",
            }
        }
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(
                    (row["year_low"], row["year_best"], row["year_high"]),
                    (1918, 1918, 1918),
                )

    def test_queue_partition_is_exact_four_promotions_four_holds(self):
        self.assertEqual(
            lane.validate_wave8_finnish_civil_war_queue_contracts(self.hced_rows),
            {
                "exact_cohort_rows": 8,
                "holds": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 8,
            },
        )
        self.assertEqual(
            lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS,
            {
                "hced-Oulo1918-1",
                "hced-Rautu1918-1",
                "hced-Tampere1918-1",
                "hced-Vyborg1918-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS,
            {
                "hced-Aland1918-1",
                "hced-Ruovesi1918-1",
                "hced-Sigurds1918-1",
                "hced-Vilppula1918-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
            | lane.WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS,
            lane.WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS,
        )
        self.assertFalse(
            lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
            & lane.WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS
        )

    def test_promoted_raw_outcome_orientation_is_locked_without_override(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        expected = {
            "hced-Oulo1918-1": ("Finland", "Bolsheviks"),
            "hced-Rautu1918-1": ("Finland", "Russian Bolsheviks"),
            "hced-Tampere1918-1": ("Finnish Whites", "Finnish Reds"),
            "hced-Vyborg1918-1": ("Finnish Whites", "Russian Bolsheviks"),
        }
        for candidate_id, (winner, loser) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                contract = lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACTS[candidate_id]
                self.assertEqual((row["winner_raw"], row["loser_raw"]), (winner, loser))
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(contract["winner_side"], 1)
                self.assertEqual(contract["result_type"], "win")
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])

    def test_four_identities_are_alias_free_1918_only_and_state_firewalled(self):
        entities = {
            str(item["id"]): item
            for item in lane.WAVE8_FINNISH_CIVIL_WAR_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {WHITE, RED, OULU_GARRISON, RAUTU_DETACHMENTS},
        )
        banned = {
            "clio_su_finland_rep_1918_31f8394b",
            "russian_sfsr",
            "ru_soviet_union",
            "soviet_union",
        }
        self.assertFalse(set(entities) & banned)
        for entity in entities.values():
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                (1918, 1918),
            )
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("rating", entity["continuity_note"].casefold())
            Entity.from_dict(entity)

    def test_nineteen_sources_parse_and_event_results_have_independent_families(self):
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_FINNISH_CIVIL_WAR_SOURCES
        }
        self.assertEqual(len(sources), 19)
        consumed = {
            str(source_id)
            for entity in lane.WAVE8_FINNISH_CIVIL_WAR_ENTITIES
            for source_id in entity["source_ids"]
        }
        for source in sources.values():
            Source.from_dict(source)
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        for contract in lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACTS.values():
            self.assertTrue(
                set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"])
            )
            self.assertEqual(contract["date_source_ids"], contract["evidence_refs"])
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", sources[source_id]["evidence_roles"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )
            consumed.update(contract["evidence_refs"])
        for hold in lane.WAVE8_FINNISH_CIVIL_WAR_HOLDS.values():
            consumed.update(hold["evidence_refs"])
        for reason in lane.WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS.values():
            consumed.update(reason["evidence_refs"])
        self.assertEqual(consumed, set(sources))

    def test_canonical_names_exact_dates_and_tactical_scope_are_pinned(self):
        expected = {
            "hced-Oulo1918-1": (
                "Battle of Oulu",
                "1918-02-02",
                "1918-02-03",
                "city_battle_and_garrison_surrender",
            ),
            "hced-Rautu1918-1": (
                "Battle of Rautu",
                "1918-02-21",
                "1918-04-05",
                "prolonged_station_centered_battle_and_failed_breakout",
            ),
            "hced-Tampere1918-1": (
                "Battle of Tampere",
                "1918-03-15",
                "1918-04-06",
                "major_urban_battle_and_capture",
            ),
            "hced-Vyborg1918-1": (
                "Battle of Viipuri",
                "1918-04-24",
                "1918-04-29",
                "urban_encirclement_assault_and_red_surrender",
            ),
        }
        for candidate_id, values in expected.items():
            with self.subTest(candidate_id=candidate_id):
                canonical = lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACTS[candidate_id][
                    "canonical_event"
                ]
                self.assertEqual(
                    (
                        canonical["name"],
                        canonical["start_date"],
                        canonical["end_date"],
                        canonical["granularity"],
                    ),
                    values,
                )
                self.assertEqual(canonical["date_precision"], "day_range")
                self.assertEqual(
                    (canonical["year_low"], canonical["year_high"]),
                    (1918, 1918),
                )
        self.assertIn(
            "massacre",
            lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACTS["hced-Vyborg1918-1"][
                "audit_note"
            ].casefold(),
        )
        self.assertIn(
            "executions",
            lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACTS["hced-Rautu1918-1"][
                "audit_note"
            ].casefold(),
        )

    def test_emitted_winners_losers_and_bounded_coalitions_are_exact(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Oulo1918-1": ({WHITE}, {RED, OULU_GARRISON}),
            "hced-Rautu1918-1": ({WHITE}, {RED, RAUTU_DETACHMENTS}),
            "hced-Tampere1918-1": ({WHITE}, {RED}),
            "hced-Vyborg1918-1": ({WHITE}, {RED}),
        }
        self.assertEqual(set(events), set(expected))
        banned = {
            "clio_su_finland_rep_1918_31f8394b",
            "russian_sfsr",
            "ru_soviet_union",
            "soviet_union",
        }
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
                    {item["entity_id"] for item in event["participants"]} & banned
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], "civil_war")
                Event.from_dict(event)
        self.assertEqual(
            lane.validate_wave8_finnish_civil_war_emissions(events.values()),
            {
                "coalition_events": 2,
                "events": 4,
                "participants": 10,
                "retained_countries": 4,
                "retained_points": 3,
            },
        )

    def test_only_promoted_rautu_point_is_quarantined_and_countries_are_retained(self):
        self.assertEqual(
            lane.WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS,
            {"hced-Rautu1918-1"},
        )
        self.assertFalse(lane.WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS)
        reason = lane.WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS[
            "hced-Rautu1918-1"
        ]
        self.assertEqual(reason["actions"], ["withhold_point"])
        self.assertEqual(reason["raw_point"], [30.2293083, 60.552312])

        events = {event["hced_candidate_id"]: event for event in self._events()}
        rautu = events["hced-Rautu1918-1"]
        self.assertNotIn("geometry", rautu)
        self.assertEqual(rautu["modern_location_country"], "Russia")
        retained = {
            "hced-Oulo1918-1": ("Finland", [25.4650772, 65.0120888]),
            "hced-Tampere1918-1": ("Finland", [23.7609535, 61.4977524]),
            "hced-Vyborg1918-1": ("Russia", [28.7571571, 60.7139529]),
        }
        for candidate_id, (country, point) in retained.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(events[candidate_id]["modern_location_country"], country)
                self.assertEqual(events[candidate_id]["geometry"]["coordinates"], point)

    def test_four_coarse_rows_are_unknown_holds_never_draws_and_never_emit(self):
        expected_categories = {
            "hced-Aland1918-1": (
                "multilateral_sequence_has_no_single_competitive_result"
            ),
            "hced-Ruovesi1918-1": (
                "multi_engagement_front_cannot_supply_one_tactical_winner"
            ),
            "hced-Sigurds1918-1": (
                "multiple_sites_opponents_and_results_cannot_be_one_red_victory"
            ),
            "hced-Vilppula1918-1": (
                "static_front_not_a_unified_battle_and_ussr_is_anachronistic"
            ),
        }
        for candidate_id, category in expected_categories.items():
            with self.subTest(candidate_id=candidate_id):
                hold = lane.WAVE8_FINNISH_CIVIL_WAR_HOLDS[candidate_id]
                self.assertEqual(hold["hold_category"], category)
                self.assertEqual(hold["disposition"], "hold")
                self.assertIs(hold["emit_rated_event"], False)
                self.assertEqual(hold["result_type"], "unknown")
                self.assertEqual(hold["reviewed_outcome"], "unknown_not_draw")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertEqual(hold["bound_scoring_sides"], [])
                self.assertIn("hold_metadata_only", hold["location_review"]["point"])
        events = self._events()
        self.assertFalse(
            lane.WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS
            & {event["hced_candidate_id"] for event in events}
        )
        self.assertFalse(
            any(
                "inconclusive" in item["termination"]
                for event in events
                for item in event["participants"]
            )
        )

    def test_aland_raw_draw_is_explicitly_rejected_as_unknown(self):
        row = next(
            item
            for item in self.hced_rows
            if item["candidate_id"] == "hced-Aland1918-1"
        )
        hold = lane.WAVE8_FINNISH_CIVIL_WAR_HOLDS["hced-Aland1918-1"]
        self.assertEqual(row["winner_raw"], "Draw")
        self.assertIs(row["winner_loser_complete"], False)
        self.assertIsNone(row["loser_raw"])
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIn("raw Draw is rejected", hold["hold_reason"])
        self.assertNotIn("winner_side", hold)

    def test_seven_wikidata_matches_are_fingerprinted_discovery_only_unknowns(self):
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        self.assertEqual(
            lane.WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(_full_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["winners"], [])
                self.assertEqual(
                    lane.WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED[candidate_id][
                        "outcome_disposition"
                    ],
                    "unknown_never_draw",
                )
        self.assertNotIn(
            "hced-Sigurds1918-1",
            set(lane.WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES.values()),
        )
        self.assertEqual(
            lane.validate_wave8_finnish_civil_war_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_records": 7,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 7,
            },
        )

    def test_historical_funnel_pins_three_shared_unresolved_labels(self):
        expected = {
            "events_touched": 12,
            "labels": 3,
            "sole_blocker_events": 2,
            "unresolved_side_attempts": 12,
            "zero_time_valid_candidates": 12,
        }
        self.assertEqual(
            lane.validate_wave8_finnish_civil_war_funnel(_historical_funnel()),
            expected,
        )
        integrated = {
            event.get("hced_candidate_id") for event in self.release_events
        } & lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
        if not integrated:
            self.assertEqual(
                lane.validate_wave8_finnish_civil_war_funnel(self.funnel),
                expected,
            )

    def test_preintegration_duplicate_audit_is_zero_and_future_twins_fail(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_finnish_civil_war_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "discovery_nonrating_dispositions": 7,
                "existing_release_owned_events": 0,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        fixtures = {
            "hced": (
                [
                    *copy.deepcopy(self.hced_rows),
                    {
                        "candidate_id": "hced-future-oulu-twin",
                        "name": "Battle of Oulu",
                        "year_low": 1918,
                    },
                ],
                self.iwd_rows,
                self.iwbd_rows,
                existing,
            ),
            "iwd": (
                self.hced_rows,
                [
                    *copy.deepcopy(self.iwd_rows),
                    {
                        "candidate_id": "iwd-future-tampere-twin",
                        "name": "Battle of Tampere",
                        "year": 1918,
                    },
                ],
                self.iwbd_rows,
                existing,
            ),
            "iwbd": (
                self.hced_rows,
                self.iwd_rows,
                [
                    *copy.deepcopy(self.iwbd_rows),
                    {
                        "candidate_id": "iwbd-future-viipuri-twin",
                        "batname": "Battle of Viipuri",
                        "batyear": 1918,
                    },
                ],
                existing,
            ),
            "release": (
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                [
                    *copy.deepcopy(existing),
                    {
                        "id": "future-rautu-twin",
                        "name": "Battle of Rautu",
                        "year": 1918,
                    },
                ],
            ),
        }
        for view, args in fixtures.items():
            with self.subTest(view=view):
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_finnish_civil_war_integration_dispositions(
                        *args
                    )

    def test_queue_inventory_fingerprint_and_semantic_guards_fail_closed(self):
        extra = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(
            next(
                item
                for item in extra
                if item["candidate_id"] == "hced-Oulo1918-1"
            )
        )
        row["candidate_id"] = "hced-future-finnish-civil-war-row"
        extra.append(row)
        with self.assertRaisesRegex(ValueError, "exact cohort inventory changed"):
            lane.validate_wave8_finnish_civil_war_queue_contracts(extra)

        fingerprint = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in fingerprint
            if item["candidate_id"] == "hced-Rautu1918-1"
        )
        row["participants_raw"].append("future drift")
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_finnish_civil_war_queue_contracts(fingerprint)

        def pinned_hash(item):
            candidate_id = str(item.get("candidate_id"))
            if candidate_id in EXPECTED_HASHES:
                return EXPECTED_HASHES[candidate_id]
            return canonical_hced_row_sha256(item)

        outcome = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in outcome
            if item["candidate_id"] == "hced-Tampere1918-1"
        )
        row["winner_raw"] = "Finnish Reds"
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "promoted outcome alignment drift"):
                lane.validate_wave8_finnish_civil_war_queue_contracts(outcome)

        held = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in held
            if item["candidate_id"] == "hced-Aland1918-1"
        )
        row["winner_loser_complete"] = True
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "unknown-hold guard drift"):
                lane.validate_wave8_finnish_civil_war_queue_contracts(held)

    def test_discovery_fingerprint_and_empty_winner_guards_fail_closed(self):
        fingerprint = copy.deepcopy(self.wikidata_rows)
        row = next(item for item in fingerprint if item["candidate_id"] == "Q2043711")
        row["end_date"] = "1918-04-07T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_finnish_civil_war_discovery_dispositions(fingerprint)

        def pinned_hash(item):
            candidate_id = str(item.get("candidate_id"))
            if candidate_id in EXPECTED_DISCOVERY_HASHES:
                return EXPECTED_DISCOVERY_HASHES[candidate_id]
            return _full_row_sha256(item)

        winners = copy.deepcopy(self.wikidata_rows)
        row = next(item for item in winners if item["candidate_id"] == "Q4411911")
        row["winners"] = [{"label": "Whites", "uri": "future"}]
        with patch.object(lane, "_full_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "discovery non-rating guard"):
                lane.validate_wave8_finnish_civil_war_discovery_dispositions(winners)

    def test_promoter_and_emission_validator_fail_closed_on_drift(self):
        entities, _, existing = self._installed()
        events = lane.promote_wave8_finnish_civil_war_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_finnish_civil_war_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_finnish_civil_war_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-tampere-duplicate",
                        "name": "Battle of Tampere",
                        "year": 1918,
                    },
                ],
            )
        missing = dict(entities)
        missing.pop(OULU_GARRISON)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_finnish_civil_war_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        drifted = copy.deepcopy(events)
        drifted[0]["participants"][0]["termination"] = "inconclusive_engagement"
        with self.assertRaisesRegex(ValueError, "emitted contract drift"):
            lane.validate_wave8_finnish_civil_war_emissions(drifted)

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_finnish_civil_war_entities(entities)
        lane.install_wave8_finnish_civil_war_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entities[WHITE]["end_year"] = 1919
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_finnish_civil_war_entities(entities)
        source_id = str(lane.WAVE8_FINNISH_CIVIL_WAR_SOURCES[0]["id"])
        sources[source_id]["title"] = "future drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_finnish_civil_war_sources(sources)

    def test_counts_metadata_cohort_and_final_signature_are_pinned(self):
        expected_counts = {
            "country_quarantine_additions": 0,
            "discovery_nonrating_records": 7,
            "holds": 4,
            "integration_dispositions": 7,
            "new_entities": 4,
            "new_sources": 19,
            "newly_rated_events": 4,
            "outcome_overrides": 0,
            "point_quarantine_additions": 1,
            "promotion_contracts": 4,
            "reviewed_hced_rows": 8,
            "terminal_exclusions": 0,
            "unknown_discovery_outcomes": 7,
        }
        self.assertEqual(lane.wave8_finnish_civil_war_counts(), expected_counts)
        self.assertEqual(
            lane.wave8_finnish_civil_war_cohort_counts(),
            {"finnish_civil_war_exact_1918": 8},
        )
        self.assertEqual(
            lane.wave8_finnish_civil_war_audit_signature(),
            "5649dc15a7bf9f8982eca6c7847814f418da4e6f9a0023b531a208dd0a3fbab9",
        )
        self.assertEqual(
            lane.wave8_finnish_civil_war_audit_signature(),
            lane.WAVE8_FINNISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_finnish_civil_war_metadata()
        self.assertEqual(metadata["counts"], expected_counts)
        self.assertEqual(metadata["held_candidate_ids"], sorted(lane.WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS))
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS),
        )
        self.assertEqual(metadata["point_quarantine_additions"], ["hced-Rautu1918-1"])
        self.assertEqual(len(metadata["discovery_dispositions"]), 7)

    def test_current_release_is_all_or_none_for_future_integration(self):
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        self.assertIn(
            owned_ids,
            (set(), set(lane.WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS)),
        )
        if owned_ids:
            self.assertEqual(
                lane.validate_wave8_finnish_civil_war_emissions(owned),
                {
                    "coalition_events": 2,
                    "events": 4,
                    "participants": 10,
                    "retained_countries": 4,
                    "retained_points": 3,
                },
            )


if __name__ == "__main__":
    unittest.main()
