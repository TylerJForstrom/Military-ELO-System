import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest import mock

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_somali_rebels as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_somali_rebels_"

USC = "united_somali_congress_mogadishu_force_1990_1991"
BARRE = "siad_barre_loyalist_forces_mogadishu_1990_1991"
SNA = "somali_national_alliance_aidid_force_mogadishu_1993"
RANGER = "task_force_ranger_mogadishu_1993"
RELIEF = "mogadishu_multinational_relief_force_1993"
DERVISH = "somali_dervish_movement_1899_1920"
SOMALIA = "clio_q1045_1960_b5c3f32e"


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


class Wave8SomaliRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.ucdp = []
        for filename in (
            "ucdp-actor-26.1-candidates.jsonl",
            "ucdp-conflict-26.1-candidates.jsonl",
            "ucdp-dyadic-26.1-candidates.jsonl",
            "ucdp-termination-dyad-candidates.jsonl",
        ):
            cls.ucdp.extend(_jsonl(ROOT / "data/review" / filename))
        cls.wikidata_audited = [
            row
            for row in cls.wikidata
            if row.get("candidate_id")
            in lane.WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES
        ]
        cls.ucdp_audited = [
            row
            for row in cls.ucdp
            if row.get("candidate_id")
            in lane.WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES
        ]
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SOMALI_REBELS_ENTITIES
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SOMALI_REBELS_SOURCES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
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
            not in lane.WAVE8_SOMALI_REBELS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        lane.install_wave8_somali_rebels_entities(entities)
        lane.install_wave8_somali_rebels_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_somali_rebels_contracts(
            self.hced,
            entities,
            existing,
        )

    def _is_integrated(self) -> bool:
        released = {
            event.get("hced_candidate_id") for event in self.release_events
        }
        return lane.WAVE8_SOMALI_REBELS_CONTRACT_IDS <= released

    def test_exact_label_inventory_and_both_row_hash_layers_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if normalize_label(row.get("side_1_raw")) == "somali rebels"
            or normalize_label(row.get("side_2_raw")) == "somali rebels"
        }
        self.assertEqual(set(relevant), lane.WAVE8_SOMALI_REBELS_RESERVED_IDS)
        self.assertEqual(len(relevant), 3)
        for candidate_id, row in relevant.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    lane.WAVE8_SOMALI_REBELS_ROW_HASHES[candidate_id],
                )
                self.assertEqual(
                    _full_row_sha256(row),
                    lane.WAVE8_SOMALI_REBELS_FULL_ROW_HASHES[candidate_id],
                )

    def test_queue_contracts_pin_three_rows_and_two_promotions(self) -> None:
        self.assertEqual(
            lane.validate_wave8_somali_rebels_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
            },
        )

    def test_historical_funnel_pin_is_exact_until_integration(self) -> None:
        historical = {
            "labels": [copy.deepcopy(lane.WAVE8_SOMALI_REBELS_FUNNEL_AUDIT)]
        }
        self.assertEqual(
            lane.validate_wave8_somali_rebels_funnel(historical),
            {
                "events_touched": 3,
                "sole_blocker_events": 2,
                "unresolved_side_attempts": 3,
                "zero_time_valid_candidates": 3,
            },
        )
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        self.assertNotIn("somali rebels", labels)

    def test_contracts_pin_dates_granularity_and_outcome_layers(self) -> None:
        campaign = lane.WAVE8_SOMALI_REBELS_CONTRACTS[
            "hced-Mogadishu1990-1991-1"
        ]
        battle = lane.WAVE8_SOMALI_REBELS_CONTRACTS["hced-Mogadishu1993-1"]
        self.assertEqual(
            (
                campaign["canonical_event"]["name"],
                campaign["canonical_event"]["start_date"],
                campaign["canonical_event"]["end_date"],
                campaign["canonical_event"]["granularity"],
                campaign["side_1_entity_ids"],
                campaign["side_2_entity_ids"],
                campaign["winner_side"],
                campaign["event_type"],
            ),
            (
                "Mogadishu urban campaign",
                "1990-12-30",
                "1991-01-26",
                "urban_campaign_ending_in_barre_expulsion",
                [USC],
                [BARRE],
                1,
                "campaign",
            ),
        )
        self.assertFalse(campaign["source_outcome_override"])
        self.assertFalse(campaign["outcome_reversal"])
        self.assertEqual(
            (
                battle["canonical_event"]["name"],
                battle["canonical_event"]["start_date"],
                battle["canonical_event"]["end_date"],
                battle["canonical_event"]["granularity"],
                battle["canonical_event"]["approximate_local_times"],
                battle["side_1_entity_ids"],
                battle["side_2_entity_ids"],
                battle["winner_side"],
                battle["event_type"],
            ),
            (
                "Battle of Mogadishu",
                "1993-10-03",
                "1993-10-04",
                "direct_action_raid_relief_and_extraction_battle",
                {"end": "06:30 on 4 October", "start": "15:30 on 3 October"},
                [SNA],
                [RANGER, RELIEF],
                2,
                "engagement",
            ),
        )
        self.assertTrue(battle["source_outcome_override"])
        self.assertTrue(battle["outcome_reversal"])
        self.assertEqual(battle["reviewed_decisiveness"], 0.34)

    def test_dul_madoba_is_unknown_not_draw_and_never_emits(self) -> None:
        self.assertEqual(
            lane.WAVE8_SOMALI_REBELS_HOLD_IDS,
            {"hced-Dul Madoba1913-1"},
        )
        hold = lane.WAVE8_SOMALI_REBELS_HOLDS["hced-Dul Madoba1913-1"]
        self.assertEqual(hold["reviewed_outcome"], "unknown_not_draw")
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertIs(hold["emit_rated_event"], False)
        self.assertEqual(hold["bound_scoring_sides"], [])
        self.assertNotIn("winner_side", hold)
        self.assertEqual(
            hold["canonical_event"]["start_date"],
            "1913-08-09",
        )
        self.assertIn("unknown is not a draw", hold["hold_reason"].casefold())
        self.assertNotIn(
            "hced-Dul Madoba1913-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_exactly_five_alias_free_bounded_identities_are_installed(self) -> None:
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_SOMALI_REBELS_ENTITIES
        }
        self.assertEqual(set(entities), {USC, BARRE, SNA, RANGER, RELIEF})
        self.assertEqual(len(entities), 5)
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                Entity.from_dict(entity)
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertNotEqual(normalize_label(entity["name"]), "somali rebels")
                self.assertIn("rating", entity["continuity_note"].casefold())
        self.assertEqual(
            (entities[USC]["start_year"], entities[USC]["end_year"]),
            (1990, 1991),
        )
        self.assertEqual(
            (entities[BARRE]["start_year"], entities[BARRE]["end_year"]),
            (1990, 1991),
        )
        for entity_id in (SNA, RANGER, RELIEF):
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (1993, 1993),
            )

    def test_existing_dervish_and_somalia_windows_are_unchanged(self) -> None:
        entities = {
            str(entity["id"]): entity for entity in self.release_entities
        }
        self.assertEqual(
            lane.validate_wave8_somali_rebels_existing_boundaries(entities),
            {"forbidden_generic_aliases": 0, "required_existing_entities": 2},
        )
        for entity_id in (DERVISH, SOMALIA):
            expected = lane.WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES[
                entity_id
            ]
            self.assertEqual(
                {key: entities[entity_id].get(key) for key in expected},
                expected,
            )

    def test_no_generic_somali_rebels_alias_can_be_introduced(self) -> None:
        entities, _, _ = self._installed()
        bad = copy.deepcopy(entities)
        bad[USC]["aliases"] = ["Somali Rebels"]
        with self.assertRaisesRegex(ValueError, "generic Somali Rebels alias"):
            lane.validate_wave8_somali_rebels_existing_boundaries(bad)

    def test_eight_new_and_two_required_sources_are_closed(self) -> None:
        self.assertEqual(len(lane.WAVE8_SOMALI_REBELS_SOURCES), 8)
        for source in lane.WAVE8_SOMALI_REBELS_SOURCES:
            Source.from_dict(source)
        release_sources = {
            str(source["id"]): source for source in self.release_sources
        }
        self.assertEqual(
            lane.validate_wave8_somali_rebels_required_sources(release_sources),
            {"required_existing_sources": 2},
        )
        for contract in lane.WAVE8_SOMALI_REBELS_CONTRACTS.values():
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            self.assertEqual(
                len(contract["outcome_source_family_ids"]),
                2 if contract["winner_side"] == 1 else 3,
            )

    def test_entity_and_source_installers_are_atomic_and_collision_safe(self) -> None:
        entities, sources, _ = self._installed()
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_somali_rebels_entities(entities)
        lane.install_wave8_somali_rebels_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)

        bad_entities = copy.deepcopy(entities)
        bad_entities[USC]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_somali_rebels_entities(bad_entities)
        source_id = lane.WAVE8_SOMALI_REBELS_SOURCES[0]["id"]
        bad_sources = copy.deepcopy(sources)
        bad_sources[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_somali_rebels_sources(bad_sources)

    def test_two_events_emit_and_parse_with_closed_sources(self) -> None:
        events = self._events()
        self.assertEqual(
            lane.validate_wave8_somali_rebels_emissions(events),
            {
                "campaign_events": 1,
                "events": 2,
                "outcome_overrides": 1,
                "participants": 5,
                "retained_countries": 2,
                "retained_points": 0,
            },
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_SOMALI_REBELS_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            self.assertTrue(set(event["outcome_source_ids"]) <= set(event["source_ids"]))

    def test_1990_1991_is_operational_city_campaign_not_whole_war(self) -> None:
        event = {
            item["hced_candidate_id"]: item for item in self._events()
        }["hced-Mogadishu1990-1991-1"]
        self.assertEqual(event["event_type"], "campaign")
        self.assertEqual(event["scale"], "campaign")
        self.assertEqual(event["date_interval"], {
            "start": "1990-12-30",
            "end": "1991-01-26",
        })
        self.assertEqual(event["decisiveness"], 0.76)
        participants = {item["entity_id"]: item for item in event["participants"]}
        self.assertEqual(set(participants), {USC, BARRE})
        self.assertEqual(participants[USC]["termination"], "campaign_victory")
        self.assertEqual(participants[BARRE]["termination"], "campaign_defeat")
        self.assertEqual(
            set(participants[USC]["outcome"]),
            {
                "campaign_objective",
                "theater_control",
                "force_preservation",
                "tempo_initiative",
                "logistics_sustainment",
            },
        )
        self.assertIn("no constituent engagement", event["summary"].casefold())
        self.assertIn("whole-war result", event["summary"].casefold())

    def test_1993_reversal_is_limited_tactical_not_strategic(self) -> None:
        event = {
            item["hced_candidate_id"]: item for item in self._events()
        }["hced-Mogadishu1993-1"]
        self.assertEqual(event["event_type"], "engagement")
        self.assertEqual(event["date_interval"], {
            "start": "1993-10-03",
            "end": "1993-10-04",
        })
        self.assertEqual(event["decisiveness"], 0.34)
        participants = {item["entity_id"]: item for item in event["participants"]}
        self.assertEqual(set(participants), {SNA, RANGER, RELIEF})
        self.assertEqual(participants[RANGER]["side"], "side_a")
        self.assertEqual(participants[RELIEF]["side"], "side_a")
        self.assertEqual(participants[SNA]["side"], "side_b")
        self.assertEqual(participants[RANGER]["contribution"], 0.5)
        self.assertEqual(participants[RELIEF]["contribution"], 0.5)
        self.assertEqual(participants[SNA]["termination"], "engagement_defeat")
        self.assertIn("limited tactical assertion", event["summary"].casefold())
        self.assertIn("wider intervention", event["summary"].casefold())

    def test_three_points_are_quarantined_and_no_country_is_quarantined(self) -> None:
        self.assertEqual(
            lane.WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SOMALI_REBELS_RESERVED_IDS,
        )
        self.assertEqual(
            lane.WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
            frozenset(),
        )
        self.assertEqual(
            set(lane.WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_SOMALI_REBELS_RESERVED_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Somalia")
            self.assertIn("location_provenance", event)

    def test_wikidata_twins_are_fingerprinted_unknown_nonratings(self) -> None:
        self.assertEqual(len(self.wikidata_audited), 2)
        self.assertEqual(
            lane.validate_wave8_somali_rebels_discovery_dispositions(
                self.wikidata_audited
            ),
            {
                "automated_promotions": 0,
                "discovery_date_quarantines": 1,
                "ucdp_dispositions": 0,
                "unknown_never_draw_wikidata_rows": 2,
                "wikidata_nonrating_records": 2,
            },
        )
        by_id = {row["candidate_id"]: row for row in self.wikidata_audited}
        for candidate_id, expected_hash in (
            lane.WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES.items()
        ):
            self.assertEqual(_full_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertEqual(by_id[candidate_id]["winners"], [])
            self.assertIs(by_id[candidate_id]["do_not_rate_automatically"], True)
        self.assertEqual(
            lane.WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES["Q109561628"][
                "reviewed_date"
            ],
            "1913-08-09",
        )

    def test_ten_ucdp_rows_are_context_only_and_never_auto_rate(self) -> None:
        self.assertEqual(len(self.ucdp_audited), 10)
        self.assertEqual(
            lane.validate_wave8_somali_rebels_ucdp_dispositions(
                self.ucdp_audited
            ),
            {
                "actor_identity_records": 2,
                "automated_promotions": 0,
                "broader_or_distinct_context_records": 8,
                "ucdp_dispositions": 10,
            },
        )
        by_id = {row["candidate_id"]: row for row in self.ucdp_audited}
        for candidate_id, expected_hash in (
            lane.WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES.items()
        ):
            self.assertEqual(_full_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertIs(by_id[candidate_id]["do_not_rate_automatically"], True)
            self.assertIs(
                lane.WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS[candidate_id][
                    "automated_rating"
                ],
                False,
            )

    def test_combined_discovery_validation_accounts_for_all_twelve_rows(self) -> None:
        self.assertEqual(
            lane.validate_wave8_somali_rebels_discovery_dispositions(
                self.wikidata_audited,
                self.ucdp_audited,
            ),
            {
                "automated_promotions": 0,
                "discovery_date_quarantines": 1,
                "ucdp_dispositions": 10,
                "unknown_never_draw_wikidata_rows": 2,
                "wikidata_nonrating_records": 2,
            },
        )
        self.assertEqual(
            len(lane.WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS),
            12,
        )

    def test_discovery_fingerprints_fail_closed_on_missing_or_mutated_rows(self) -> None:
        with self.assertRaisesRegex(ValueError, "Q52226 expected once"):
            lane.validate_wave8_somali_rebels_discovery_dispositions(
                [
                    row
                    for row in self.wikidata_audited
                    if row["candidate_id"] != "Q52226"
                ]
            )
        mutated_wikidata = copy.deepcopy(self.wikidata_audited)
        next(
            row for row in mutated_wikidata if row["candidate_id"] == "Q52226"
        )["winners"] = [{"label": "Somalia"}]
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_somali_rebels_discovery_dispositions(
                mutated_wikidata
            )
        mutated_ucdp = copy.deepcopy(self.ucdp_audited)
        next(
            row
            for row in mutated_ucdp
            if row["candidate_id"] == "ucdp-termination-dyad-337-2158"
        )["raw"]["d_outcome"] = "3"
        with self.assertRaisesRegex(ValueError, "UCDP fingerprint changed"):
            lane.validate_wave8_somali_rebels_ucdp_dispositions(mutated_ucdp)

    def test_cross_dataset_duplicate_audit_has_no_unreviewed_twin(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_somali_rebels_integration_dispositions(
                self.hced,
                self.iwd,
                self.iwbd,
                existing,
                wikidata_rows=self.wikidata_audited,
                ucdp_rows=self.ucdp_audited,
            ),
            {
                "existing_release_owned_events": 0,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "integration_dispositions": 12,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "ucdp_overlap_dispositions": 10,
                "wikidata_dispositions": 2,
            },
        )

    def test_integration_guard_rejects_hold_twin_and_ucdp_rating(self) -> None:
        _, _, existing = self._installed()
        released_hold = {
            "id": "bad_dul_madoba",
            "name": "Dul Madoba",
            "year": 1913,
            "hced_candidate_id": "hced-Dul Madoba1913-1",
        }
        with self.assertRaisesRegex(ValueError, "unknown hold entered release"):
            lane.validate_wave8_somali_rebels_integration_dispositions(
                self.hced,
                self.iwd,
                self.iwbd,
                [*existing, released_hold],
            )
        released_ucdp = {
            "id": "bad_ucdp_mogadishu",
            "name": "unrelated",
            "year": 1990,
            "ucdp_candidate_id": "ucdp-termination-dyad-337-2158",
        }
        with self.assertRaisesRegex(ValueError, "ucdp_release"):
            lane.validate_wave8_somali_rebels_integration_dispositions(
                self.hced,
                self.iwd,
                self.iwbd,
                [*existing, released_ucdp],
            )

    def test_queue_and_entity_mutations_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.hced)
        next(
            row
            for row in mutated
            if row["candidate_id"] == "hced-Mogadishu1993-1"
        )["winner_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_somali_rebels_queue_contracts(mutated)

        entities, _, existing = self._installed()
        bad_entities = copy.deepcopy(entities)
        bad_entities[USC]["end_year"] = 1990
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_somali_rebels_contracts(
                self.hced,
                bad_entities,
                existing,
            )

    def test_duplicate_candidate_cannot_be_promoted_twice(self) -> None:
        entities, _, existing = self._installed()
        events = lane.promote_wave8_somali_rebels_contracts(
            self.hced,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_somali_rebels_contracts(
                self.hced,
                entities,
                [*existing, events[0]],
            )

    def test_current_artifact_state_is_absent_or_atomically_integrated(self) -> None:
        current = lane.validate_wave8_somali_rebels_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        if self._is_integrated():
            self.assertEqual(
                current,
                {
                    "artifact_state": "integrated",
                    "installed_entities": 5,
                    "installed_sources": 8,
                    "promoted_events": 2,
                },
            )
        else:
            self.assertEqual(
                current,
                {
                    "artifact_state": "absent",
                    "installed_entities": 0,
                    "installed_sources": 0,
                    "promoted_events": 0,
                },
            )

        entities, sources, existing = self._installed()
        events = lane.promote_wave8_somali_rebels_contracts(
            self.hced,
            entities,
            existing,
        )
        self.assertEqual(
            lane.validate_wave8_somali_rebels_current_artifact_state(
                [*existing, *events],
                entities.values(),
                sources.values(),
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 5,
                "installed_sources": 8,
                "promoted_events": 2,
            },
        )

    def test_partial_artifact_state_fails_closed(self) -> None:
        lane_ids = {item["id"] for item in lane.WAVE8_SOMALI_REBELS_ENTITIES}
        entities = [
            copy.deepcopy(item)
            for item in self.release_entities
            if item["id"] not in lane_ids
        ]
        entities.append(copy.deepcopy(lane.WAVE8_SOMALI_REBELS_ENTITIES[0]))
        with self.assertRaisesRegex(ValueError, "artifacts are partial"):
            lane.validate_wave8_somali_rebels_current_artifact_state(
                [
                    event
                    for event in self.release_events
                    if event.get("hced_candidate_id")
                    not in lane.WAVE8_SOMALI_REBELS_RESERVED_IDS
                ],
                entities,
                self.release_sources,
            )

    def test_counts_and_metadata_are_exact(self) -> None:
        self.assertEqual(
            lane.wave8_somali_rebels_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_date_quarantines": 1,
                "holds": 1,
                "integration_dispositions": 12,
                "new_entities": 5,
                "new_sources": 8,
                "newly_rated_events": 2,
                "outcome_overrides": 1,
                "point_quarantine_additions": 3,
                "promotion_contracts": 2,
                "required_existing_sources": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
                "ucdp_nonrating_records": 10,
                "unknown_holds": 1,
                "wikidata_nonrating_records": 2,
            },
        )
        metadata = lane.wave8_somali_rebels_metadata()
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_SOMALI_REBELS_CONTRACT_IDS),
        )
        self.assertEqual(
            metadata["held_candidate_ids"],
            ["hced-Dul Madoba1913-1"],
        )
        self.assertEqual(len(metadata["discovery_dispositions"]), 12)
        self.assertEqual(
            lane.wave8_somali_rebels_cohort_counts(),
            {"somali_rebels_exact_1913_1993": 3},
        )

    def test_final_signature_is_sealed_and_sensitive_to_contract_drift(self) -> None:
        self.assertNotEqual(
            lane.WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE,
            "TO_BE_SEALED",
        )
        self.assertEqual(
            lane.wave8_somali_rebels_audit_signature(),
            lane.WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        mutated = copy.deepcopy(lane.WAVE8_SOMALI_REBELS_CONTRACTS)
        mutated["hced-Mogadishu1993-1"]["reviewed_decisiveness"] = 0.35
        with mock.patch.object(lane, "WAVE8_SOMALI_REBELS_CONTRACTS", mutated):
            self.assertNotEqual(
                lane.wave8_somali_rebels_audit_signature(),
                lane.WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE,
            )


if __name__ == "__main__":
    unittest.main()
