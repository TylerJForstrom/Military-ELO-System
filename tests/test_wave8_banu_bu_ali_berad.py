import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_banu_bu_ali_berad as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_banu_berad_"

EXPECTED_HASHES = {
    "hced-Bani Bu Ali1821-1": (
        "71b69d563942cd10c8b296420c06ce6931ae92e8f016df4c2e48512a3c930e49"
    ),
    "hced-Sagar1680-1": (
        "6b6ede291b02b5cb709f6e2073587ca29ad41c3afd728c333740dea3f37ce8e2"
    ),
    "hced-Sur1820-1": (
        "0ecbbf80b4876af3eaf31daf7dac31991bc006c0e3a9f8e85e432291a9100d4c"
    ),
    "hced-Wagingera1705-1": (
        "13e8b37410eb1167bc36cc194b95ae4fb6e877e6aa4e6b42b5d62daa09f1af20"
    ),
}
EXPECTED_DISCOVERY_HASHES = {
    "Q16931469": (
        "2e30bd1f0eaeb64120e305b3966c379734d63e0996166aaa157903b455442ac9"
    ),
    "Q4870440": (
        "ca46b0d1ad3d907f318e7ddbee1ff6d90177029525920e47dc02ac6f1b2e94ea"
    ),
}

MUHAMMAD_JALAN = "muhammad_bin_ali_jalan_defenders_1820"
THOMPSON_COLUMN = "thompson_eic_jalan_column_1820"
SAID_LEVY = "sayyid_said_jalan_levy_1820"
SMITH_EXPEDITION = "lionel_smith_bombay_expedition_bani_bu_ali_1821"
MUHAMMAD_1821 = "muhammad_bin_ali_bani_bu_ali_defenders_1821"
PAM_NAYAK = "pam_nayak_sagar_defenders_1680"
PIDIA_NAYAK = "pidia_nayak_wagingera_garrison_1705"
DHANA_JADAV = "dhana_jadav_hindu_rao_wagingera_relief_force_1705"
MUGHAL = "mughal_empire"


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


class Wave8BanuBuAliBeradTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        fixture_entity_ids = {
            str(entity["id"])
            for entity in lane.WAVE8_BANU_BU_ALI_BERAD_ENTITIES
        }
        fixture_source_ids = {
            str(source["id"])
            for source in lane.WAVE8_BANU_BU_ALI_BERAD_SOURCES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_banu_bu_ali_berad_entities(entities)
        lane.install_wave8_banu_bu_ali_berad_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_banu_bu_ali_berad_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_canonical_hashes_are_pinned(self):
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw"))
            in {"banu bu ali", "berad tribes"}
            or normalize_label(row.get("side_2_raw"))
            in {"banu bu ali", "berad tribes"}
        ]
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(len(exact), 4)
        self.assertEqual(lane.WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])

    def test_queue_validation_promotes_four_and_keeps_ras_separate(self):
        self.assertEqual(
            lane.validate_wave8_banu_bu_ali_berad_queue_contracts(
                self.hced_rows
            ),
            {
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "separate_lane_holds": 1,
            },
        )
        self.assertEqual(
            lane.WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertNotIn(
            "hced-Ras al-Khaimah1809-1",
            lane.WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS,
        )
        self.assertFalse(lane.WAVE8_BANU_BU_ALI_BERAD_HOLDS)

    def test_ras_al_khaimah_is_a_fingerprinted_separate_lane_hold(self):
        holds = lane.WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS
        self.assertEqual(set(holds), {"hced-Ras al-Khaimah1809-1"})
        row = next(
            item
            for item in self.hced_rows
            if item["candidate_id"] == "hced-Ras al-Khaimah1809-1"
        )
        hold = holds[row["candidate_id"]]
        self.assertEqual(
            canonical_hced_row_sha256(row),
            "8c8ff4497f3b7e6a2a0f88a105576b65746f322628fa112dad7f5fa4747361eb",
        )
        self.assertEqual(hold["disposition"], "hold_separate_lane")
        self.assertEqual(hold["label"], "bani bu ali")
        self.assertTrue(hold["unknown_is_never_draw"])
        self.assertIn("Qawasim", hold["reason"])

    def test_historical_funnel_pins_both_two_event_lanes(self):
        historical_rows = []
        for label, expected in lane.WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT.items():
            row = {"label": label, **copy.deepcopy(expected)}
            historical_rows.append(row)
        self.assertEqual(
            lane.validate_wave8_banu_bu_ali_berad_funnel(
                {"labels": historical_rows}
            ),
            {
                "banu bu ali": {
                    "events_touched": 2,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 2,
                    "zero_time_valid_candidates": 2,
                },
                "berad tribes": {
                    "events_touched": 2,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 2,
                    "zero_time_valid_candidates": 2,
                },
            },
        )
        live_labels = {
            str(row.get("label")) for row in self.funnel.get("labels", [])
        }
        self.assertTrue(
            set(lane.WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT).isdisjoint(
                live_labels
            )
        )

    def test_contracts_pin_dates_granularity_sides_and_known_winners(self):
        expected = {
            "hced-Sur1820-1": (
                "Battle near Bilad Bani Bu Ali",
                "1820-11-09",
                "1820-11-09",
                [MUHAMMAD_JALAN],
                [THOMPSON_COLUMN, SAID_LEVY],
                1,
            ),
            "hced-Bani Bu Ali1821-1": (
                "Battle and capture of Bani Bu Ali",
                "1821-03-02",
                "1821-03-02",
                [SMITH_EXPEDITION],
                [MUHAMMAD_1821],
                1,
            ),
            "hced-Sagar1680-1": (
                "Battle of Sagar (Shahpur)",
                "1680-02-20",
                "1680-02-21",
                [PAM_NAYAK],
                [MUGHAL],
                2,
            ),
            "hced-Wagingera1705-1": (
                "Siege and capture of Wagingera",
                "1705-02-08",
                "1705-04-27",
                [MUGHAL],
                [PIDIA_NAYAK, DHANA_JADAV],
                2,
            ),
        }
        self.assertEqual(
            lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS,
            set(expected),
        )
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["start_date"],
                    canonical["end_date"],
                    contract["side_1_entity_ids"],
                    contract["side_2_entity_ids"],
                    contract["expected_scale_level"],
                ),
                values,
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["source_date_refinement"])

    def test_siege_and_campaign_granularity_guards_are_explicit(self):
        sur = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS["hced-Sur1820-1"]
        bani = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[
            "hced-Bani Bu Ali1821-1"
        ]
        wagingera = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[
            "hced-Wagingera1705-1"
        ]
        self.assertIn("not_sur_landing", sur["canonical_event"]["granularity"])
        self.assertIn("not_full_campaign", bani["canonical_event"]["granularity"])
        self.assertEqual(
            wagingera["canonical_event"]["granularity"],
            "full_three_month_siege_not_separate_final_assault",
        )
        self.assertIn("neither surrender nor annihilation", wagingera["audit_note"])

    def test_eight_new_entities_are_alias_free_and_only_mughal_is_reused(self):
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_BANU_BU_ALI_BERAD_ENTITIES
        }
        expected_new = {
            MUHAMMAD_JALAN,
            THOMPSON_COLUMN,
            SAID_LEVY,
            SMITH_EXPEDITION,
            MUHAMMAD_1821,
            PAM_NAYAK,
            PIDIA_NAYAK,
            DHANA_JADAV,
        }
        self.assertEqual(set(entities), expected_new)
        participants = {
            entity_id
            for contract in lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertEqual(participants - expected_new, {MUGHAL})
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(entity["start_year"], entity["end_year"])
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("inherits no Elo", entity["continuity_note"])
                Entity.from_dict(entity)

    def test_no_broad_tribal_state_or_successor_alias_is_created(self):
        forbidden = {
            "banu bu ali",
            "bani bu ali",
            "berad tribes",
            "berad",
            "muscat",
            "oman",
            "maratha confederacy",
            "bijapur",
            "united kingdom",
        }
        aliases = {
            normalize_label(alias)
            for entity in lane.WAVE8_BANU_BU_ALI_BERAD_ENTITIES
            for alias in entity["aliases"]
        }
        self.assertFalse(aliases)
        self.assertFalse(forbidden & aliases)
        for contract in lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.values():
            self.assertNotIn("united_kingdom", contract["side_1_entity_ids"])
            self.assertNotIn("united_kingdom", contract["side_2_entity_ids"])

    def test_twelve_sources_parse_and_outcomes_have_independent_families(self):
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_BANU_BU_ALI_BERAD_SOURCES
        }
        self.assertEqual(len(sources), 12)
        self.assertEqual(
            len({source["source_family_id"] for source in sources.values()}),
            9,
        )
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
        consumed = set()
        for contract in lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_ids"],
                sorted(set(contract["outcome_source_ids"])),
            )
            self.assertTrue(
                set(contract["outcome_source_ids"])
                <= set(contract["evidence_refs"])
            )
            consumed.update(contract["evidence_refs"])
        self.assertEqual(consumed, set(sources))

    def test_emitted_events_have_exact_dates_participants_and_no_draws(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_HASHES))
        expected_winners = {
            "hced-Sur1820-1": {MUHAMMAD_JALAN},
            "hced-Bani Bu Ali1821-1": {SMITH_EXPEDITION},
            "hced-Sagar1680-1": {PAM_NAYAK},
            "hced-Wagingera1705-1": {MUGHAL},
        }
        for candidate_id, event in events.items():
            contract = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
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
            self.assertEqual(winners, expected_winners[candidate_id])
            self.assertTrue(losers)
            self.assertEqual(
                event["date_interval"],
                {
                    "start": canonical["start_date"],
                    "end": canonical["end_date"],
                },
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["aliases"], [])
            self.assertFalse(
                any(
                    "inconclusive" in participant["termination"]
                    for participant in event["participants"]
                )
            )
            Event.from_dict(event)

    def test_emission_validator_pins_all_ten_participant_assignments(self):
        events = self._events()
        self.assertEqual(
            lane.validate_wave8_banu_bu_ali_berad_emissions(events),
            {
                "events": 4,
                "participants": 10,
                "retained_countries": 4,
                "retained_points": 0,
            },
        )
        drifted = copy.deepcopy(events)
        drifted[0]["participants"][0]["termination"] = "inconclusive_engagement"
        with self.assertRaisesRegex(ValueError, "emitted contract drift"):
            lane.validate_wave8_banu_bu_ali_berad_emissions(drifted)

    def test_all_four_points_are_quarantined_and_countries_are_retained(self):
        self.assertEqual(
            lane.WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS,
            set(EXPECTED_HASHES),
        )
        self.assertFalse(
            lane.WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS
        )
        self.assertEqual(
            lane.wave8_banu_bu_ali_berad_location_quarantine_additions(),
            {"country": set(), "point": set(EXPECTED_HASHES)},
        )
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected_countries = {
            "hced-Sur1820-1": "Oman",
            "hced-Bani Bu Ali1821-1": "Oman",
            "hced-Sagar1680-1": "India",
            "hced-Wagingera1705-1": "India",
        }
        for candidate_id, event in events.items():
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"], expected_countries[candidate_id]
            )
            self.assertIn("location_provenance", event)
            self.assertEqual(
                lane.WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS[
                    candidate_id
                ]["actions"],
                ["withhold_point"],
            )

    def test_discovery_duplicate_and_false_positive_are_nonrating_unknowns(self):
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            row = by_id[candidate_id]
            self.assertEqual(_full_row_sha256(row), expected_hash)
            self.assertIs(row["do_not_rate_automatically"], True)
            self.assertEqual(row["winners"], [])
            disposition = lane.WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS[
                candidate_id
            ]
            self.assertFalse(disposition["automatic_rating"])
            self.assertEqual(
                disposition["outcome_disposition"], "unknown_never_draw"
            )
        self.assertEqual(
            lane.validate_wave8_banu_bu_ali_berad_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_records": 2,
                "duplicate_superseded_records": 1,
                "lexical_false_positives": 1,
                "unknown_never_draw_rows": 2,
            },
        )

    def test_wagingera_discovery_date_and_bedara_lexical_match_never_import(self):
        q169 = lane.WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED["Q16931469"]
        q487 = lane.WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED["Q4870440"]
        wagingera = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[
            "hced-Wagingera1705-1"
        ]["canonical_event"]
        self.assertEqual(q169["disposition"], "duplicate_superseded_discovery")
        self.assertEqual(q169["canonical_owner"], "hced-Wagingera1705-1")
        self.assertTrue(q169["date"].startswith("1704-"))
        self.assertTrue(wagingera["start_date"].startswith("1705-"))
        self.assertEqual(q487["disposition"], "lexical_false_positive")
        self.assertIsNone(q487["canonical_owner"])

    def test_queue_hash_semantic_and_future_label_drift_fail_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in tampered if item["candidate_id"] == "hced-Sagar1680-1"
        )
        row["winner_raw"] = "Mughal Empire"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_banu_bu_ali_berad_queue_contracts(tampered)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-berad",
                "side_1_raw": "Berad Tribes",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_banu_bu_ali_berad_queue_contracts(future)

        semantic = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in semantic if item["candidate_id"] == "hced-Sur1820-1"
        )
        row["winner_loser_complete"] = False

        def pinned_hash(candidate):
            candidate_id = str(candidate.get("candidate_id"))
            return EXPECTED_HASHES.get(
                candidate_id, canonical_hced_row_sha256(candidate)
            )

        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "locked outcome/actor row drift"):
                lane.validate_wave8_banu_bu_ali_berad_queue_contracts(semantic)

    def test_discovery_semantic_drift_fails_even_with_fingerprint_mocked(self):
        rows = copy.deepcopy(self.wikidata_rows)
        row = next(item for item in rows if item["candidate_id"] == "Q16931469")
        row["winners"] = [{"id": "Q0", "label": "Invented winner"}]

        def pinned_hash(candidate):
            return EXPECTED_DISCOVERY_HASHES.get(
                str(candidate.get("candidate_id")), _full_row_sha256(candidate)
            )

        with patch.object(lane, "_full_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "non-rating guard changed"):
                lane.validate_wave8_banu_bu_ali_berad_discovery_dispositions(rows)

    def test_promoter_rejects_missing_identity_duplicate_candidate_and_name(self):
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(PIDIA_NAYAK)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_banu_bu_ali_berad_contracts(
                self.hced_rows, missing, existing
            )

        promoted = lane.promote_wave8_banu_bu_ali_berad_contracts(
            self.hced_rows, entities, existing
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_banu_bu_ali_berad_contracts(
                self.hced_rows, entities, [*existing, promoted[0]]
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_banu_bu_ali_berad_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-wagingera-collision",
                        "name": "Siege and capture of Wagingera",
                        "year": 1705,
                    },
                ],
            )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_banu_bu_ali_berad_entities(entities)
        lane.install_wave8_banu_bu_ali_berad_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entity_collision = copy.deepcopy(entities)
        entity_collision[PAM_NAYAK]["end_year"] = 1681
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_banu_bu_ali_berad_entities(entity_collision)

        source_collision = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_BANU_BU_ALI_BERAD_SOURCES[0]["id"])
        source_collision[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_banu_bu_ali_berad_sources(source_collision)

    def test_current_artifact_state_is_absent_or_complete_never_partial(self):
        current_owned = sum(
            event.get("hced_candidate_id")
            in lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
            for event in self.release_events
        )
        current = lane.validate_wave8_banu_bu_ali_berad_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        self.assertEqual(current["promoted_events"], current_owned)
        self.assertEqual(
            current["artifact_state"], "integrated" if current_owned else "absent"
        )

        entities, sources, existing = self._installed()
        events = lane.promote_wave8_banu_bu_ali_berad_contracts(
            self.hced_rows, entities, existing
        )
        self.assertEqual(
            lane.validate_wave8_banu_bu_ali_berad_current_artifact_state(
                events, entities.values(), sources.values()
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 8,
                "installed_sources": 12,
                "promoted_events": 4,
            },
        )
        with self.assertRaisesRegex(ValueError, "artifacts are partial"):
            lane.validate_wave8_banu_bu_ali_berad_current_artifact_state(
                events[:3], entities.values(), sources.values()
            )

    def test_signature_counts_cohorts_and_metadata_are_sealed(self):
        self.assertEqual(
            lane.wave8_banu_bu_ali_berad_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 2,
                "holds": 0,
                "new_entities": 8,
                "new_sources": 12,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "separate_lane_holds": 1,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 2,
            },
        )
        self.assertEqual(
            lane.wave8_banu_bu_ali_berad_cohort_counts(),
            {
                "bani_bu_ali_expeditions_1820_1821": 2,
                "mughal_nayak_wars_1680_1705": 2,
            },
        )
        self.assertEqual(
            lane.wave8_banu_bu_ali_berad_audit_signature(),
            "e56bf90fd868b654a8345e5a546ac799dfde773d216e1089022fde5de75c6361",
        )
        self.assertEqual(
            lane.wave8_banu_bu_ali_berad_audit_signature(),
            lane.WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_banu_bu_ali_berad_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_banu_bu_ali_berad_counts())
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(EXPECTED_HASHES))
        self.assertEqual(metadata["reserved_candidate_ids"], sorted(EXPECTED_HASHES))
        self.assertEqual(len(metadata["discovery_dispositions"]), 2)
        self.assertEqual(len(metadata["outside_lane_holds"]), 1)

    def test_final_signature_rejects_material_contract_or_seal_drift(self):
        contract = lane.WAVE8_BANU_BU_ALI_BERAD_CONTRACTS["hced-Sagar1680-1"]
        with patch.dict(contract, {"confidence": 0.10}):
            with self.assertRaisesRegex(ValueError, "final audit signature changed"):
                lane.wave8_banu_bu_ali_berad_counts()
        with patch.object(
            lane,
            "WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE",
            "0" * 64,
        ):
            with self.assertRaisesRegex(ValueError, "final audit signature changed"):
                lane.wave8_banu_bu_ali_berad_counts()


if __name__ == "__main__":
    unittest.main()
