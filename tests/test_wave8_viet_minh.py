import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_viet_minh as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_viet_minh_"
VIET_MINH = "viet_minh_first_indochina_war_forces_1950_1954"
MUONG_GARRISON = "muong_khoua_lao_french_garrison_1953"
FRANCE = "clio_fr_france_modern_2_1945_396ed149"

EXPECTED_HASHES = {
    "hced-Cao-Bang1950-1": (
        "4c506cebadcead570cb678750e80ae8606f50e52b0d1f2efa9be55401f45523b"
    ),
    "hced-Day River1951-1": (
        "e2bdb5afb898df2c847422e630969fb8c7a8852ea127e7bffb77053861033c1c"
    ),
    "hced-Dien Bien Phu1953-1": (
        "e4161cf4e0b2864c610932214f2bb2863498413848e320c1b0bdf125786db4a8"
    ),
    "hced-Dong-Khe1950-1": (
        "299dab6330de54f62cf41dbe14697bb6d407effae559ed676f710e04f586e360"
    ),
    "hced-Hoa Binh1951-1": (
        "a8b1e3cc9ebc9616514fa54f64e37bf127e45d083f2cf976db473a2c1652d2a1"
    ),
    "hced-Mao Khe1951-1": (
        "07699487709f2dce9ea0662a37489ca9e1d90940951f98fdaa0f2cfa9956bfc2"
    ),
    "hced-Muong-Khoua1953-1": (
        "424d78e9383e3143932d9a5b949a5f328c9e7c8338545450b9f7b5aa36dc56a2"
    ),
    "hced-Nghia Lo1951-1": (
        "cd7024ef52f7bb7eed9a56c83e47f42d753ba2e05419e72afa31adbd521bf453"
    ),
    "hced-Nghia Lo1952-1": (
        "ffa5c456b4ec7d680e62fe5e425264a1f2cb4f130f30b82d8d29ec1f6adb17e4"
    ),
    "hced-Red River Delta1950-1": (
        "69ccef8acc2dd36c828ddfdaaeed47a95c0a35f4b5af1f21c8ff59fff94fc15b"
    ),
    "hced-Viet Bac1946-1": (
        "3fa5921cf32077c451c26a389e459a96732f61651a1dcaa342017c0c01272bf3"
    ),
    "hced-Vinh Yen1951-1": (
        "132772b394826b56a9b22d540a3f9f5d1b04612b57d0cccddb89f841cf8ba436"
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


def _historical_funnel():
    projection = copy.deepcopy(lane.WAVE8_VIET_MINH_FUNNEL_AUDIT)
    zero = projection.pop("zero_time_valid_candidates")
    projection["failure_cases"] = {"zero_time_valid_candidates": zero}
    return {"labels": [projection]}


class Wave8VietMinhTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        funnel_path = ROOT / "build/hced-unresolved-label-funnel.json"
        cls.funnel = _json(funnel_path) if funnel_path.exists() else {"labels": []}
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "viet minh"
            or normalize_label(row.get("side_2_raw")) == "viet minh"
        ]

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_VIET_MINH_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_VIET_MINH_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_viet_minh_entities(entities)
        lane.install_wave8_viet_minh_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_viet_minh_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_fingerprints_and_review_partition_are_pinned(self):
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_VIET_MINH_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, row in by_id.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_HASHES[candidate_id],
                )
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")
        self.assertEqual(
            lane.validate_wave8_viet_minh_queue_contracts(self.hced_rows),
            {
                "date_overrides": 1,
                "exact_label_rows": 12,
                "holds": 3,
                "promotion_contracts": 9,
                "reviewed_hced_rows": 12,
            },
        )

    def test_nine_promotions_and_three_holds_are_disjoint_and_exhaustive(self):
        self.assertEqual(len(lane.WAVE8_VIET_MINH_CONTRACT_IDS), 9)
        self.assertEqual(
            set(lane.WAVE8_VIET_MINH_HOLDS),
            {
                "hced-Hoa Binh1951-1",
                "hced-Red River Delta1950-1",
                "hced-Viet Bac1946-1",
            },
        )
        self.assertFalse(
            lane.WAVE8_VIET_MINH_CONTRACT_IDS & set(lane.WAVE8_VIET_MINH_HOLDS)
        )
        self.assertEqual(
            lane.WAVE8_VIET_MINH_CONTRACT_IDS | set(lane.WAVE8_VIET_MINH_HOLDS),
            lane.WAVE8_VIET_MINH_RESERVED_IDS,
        )

    def test_holds_never_become_draws_or_rated_events(self):
        expected_categories = {
            "hced-Hoa Binh1951-1": "mixed_campaign_outcome",
            "hced-Red River Delta1950-1": "unbounded_regional_campaign",
            "hced-Viet Bac1946-1": "wrong_year_bundled_campaign",
        }
        for candidate_id, category in expected_categories.items():
            hold = lane.WAVE8_VIET_MINH_HOLDS[candidate_id]
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["hold_category"], category)
            self.assertIn("draw", hold["hold_reason"].casefold())
        events = self._events()
        self.assertFalse(
            set(expected_categories)
            & {str(event["hced_candidate_id"]) for event in events}
        )
        self.assertTrue(
            all(
                contract["result_type"] == "win"
                for contract in lane.WAVE8_VIET_MINH_CONTRACTS.values()
            )
        )
        self.assertFalse(
            any(
                "inconclusive" in str(participant["termination"])
                for event in events
                for participant in event["participants"]
            )
        )

    def test_identities_are_exact_alias_free_and_time_bounded(self):
        entities, _, _ = self._installed()
        self.assertNotIn("viet minh", HCED_LABEL_POLICIES)
        self.assertEqual(
            (entities[VIET_MINH]["start_year"], entities[VIET_MINH]["end_year"]),
            (1950, 1954),
        )
        self.assertEqual(
            (
                entities[MUONG_GARRISON]["start_year"],
                entities[MUONG_GARRISON]["end_year"],
            ),
            (1953, 1953),
        )
        self.assertEqual(
            (entities[FRANCE]["start_year"], entities[FRANCE]["end_year"]),
            (1946, 1958),
        )
        for entity_id in (VIET_MINH, MUONG_GARRISON, FRANCE):
            with self.subTest(entity_id=entity_id):
                self.assertFalse(entities[entity_id]["aliases"])
                Entity.from_dict(entities[entity_id])

    def test_sources_are_closed_and_every_promoted_outcome_has_two_families(self):
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_VIET_MINH_SOURCES
        }
        self.assertEqual(
            set(source_by_id),
            {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
                "wave8_viet_minh_gras_nghia_lo_1951",
                "wave8_viet_minh_us_army_advice_support",
                "wave8_viet_minh_wolfson_ford_laos",
            },
        )
        for source in source_by_id.values():
            Source.from_dict(source)
        expected_sources = {
            "hced-Cao-Bang1950-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
            "hced-Day River1951-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
            "hced-Dien Bien Phu1953-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
            "hced-Dong-Khe1950-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
            "hced-Mao Khe1951-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
            "hced-Muong-Khoua1953-1": {
                "wave8_viet_minh_clodfelter_warfare",
                "wave8_viet_minh_wolfson_ford_laos",
            },
            "hced-Nghia Lo1951-1": {
                "wave8_viet_minh_clodfelter_warfare",
                "wave8_viet_minh_gras_nghia_lo_1951",
            },
            "hced-Nghia Lo1952-1": {
                "wave8_viet_minh_clodfelter_warfare",
                "wave8_viet_minh_us_army_advice_support",
            },
            "hced-Vinh Yen1951-1": {
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            },
        }
        for candidate_id, contract in lane.WAVE8_VIET_MINH_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    set(contract["outcome_source_ids"]),
                    expected_sources[candidate_id],
                )
                self.assertEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertTrue(
                    all(
                        "outcome" in source_by_id[source_id]["evidence_roles"]
                        for source_id in contract["outcome_source_ids"]
                    )
                )

    def test_promoted_events_have_exact_winners_losers_and_tactical_results(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Cao-Bang1950-1": (VIET_MINH, FRANCE),
            "hced-Day River1951-1": (FRANCE, VIET_MINH),
            "hced-Dien Bien Phu1953-1": (VIET_MINH, FRANCE),
            "hced-Dong-Khe1950-1": (VIET_MINH, FRANCE),
            "hced-Mao Khe1951-1": (FRANCE, VIET_MINH),
            "hced-Muong-Khoua1953-1": (VIET_MINH, MUONG_GARRISON),
            "hced-Nghia Lo1951-1": (FRANCE, VIET_MINH),
            "hced-Nghia Lo1952-1": (VIET_MINH, FRANCE),
            "hced-Vinh Yen1951-1": (FRANCE, VIET_MINH),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winner, loser) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], "colonial_anti_colonial")
                self.assertEqual(event["confidence"], 0.92)
                self.assertEqual(
                    [
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["termination"] == "engagement_victory"
                    ],
                    [winner],
                )
                self.assertEqual(
                    [
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["termination"] == "engagement_defeat"
                    ],
                    [loser],
                )
                Event.from_dict(event)

    def test_dien_bien_phu_is_source_corrected_to_1954_only(self):
        staged = next(
            row
            for row in self.exact_rows
            if row["candidate_id"] == "hced-Dien Bien Phu1953-1"
        )
        self.assertEqual((staged["year_low"], staged["year_high"]), (1953, 1953))
        contract = lane.WAVE8_VIET_MINH_CONTRACTS["hced-Dien Bien Phu1953-1"]
        self.assertIs(contract["source_date_override"], True)
        self.assertEqual(
            contract["date_source_ids"],
            [
                "wave8_viet_minh_australian_war_memorial",
                "wave8_viet_minh_clodfelter_warfare",
            ],
        )
        events = {event["hced_candidate_id"]: event for event in self._events()}
        dien = events["hced-Dien Bien Phu1953-1"]
        self.assertEqual((dien["year"], dien["end_year"]), (1954, 1954))
        self.assertEqual(dien["name"], "Battle of Dien Bien Phu (1954)")
        self.assertEqual(dien["aliases"], ["Dien Bien Phu"])

    def test_all_nine_points_are_withheld_while_reviewed_countries_are_retained(self):
        self.assertEqual(
            lane.WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_VIET_MINH_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_VIET_MINH_COUNTRY_QUARANTINE_ADDITIONS)
        events = self._events()
        self.assertEqual(len(events), 9)
        for event in events:
            with self.subTest(candidate_id=event["hced_candidate_id"]):
                self.assertNotIn("geometry", event)
                self.assertIn(event["modern_location_country"], {"Laos", "Vietnam"})
                self.assertIn("location_provenance", event)
                reason = lane.WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS[
                    event["hced_candidate_id"]
                ]
                self.assertEqual(reason["actions"], ["withhold_point"])
                self.assertEqual(
                    reason["retained_country"],
                    event["modern_location_country"],
                )

    def test_historical_funnel_projection_is_pinned(self):
        self.assertEqual(
            lane.validate_wave8_viet_minh_funnel(_historical_funnel()),
            {
                "events_touched": 12,
                "sole_blocker_events": 0,
                "zero_time_valid_candidates": 12,
            },
        )
        live = [
            row for row in self.funnel.get("labels", []) if row.get("label") == "viet minh"
        ]
        promotion = self.release_metadata.get("promotion", {})
        if "accepted_wave8_viet_minh_hced_events" in promotion:
            self.assertEqual(len(live), 1)
            self.assertEqual(live[0]["events_touched"], 3)
            self.assertEqual(live[0]["sole_blocker_events"], 0)
            self.assertEqual(
                live[0]["failure_cases"]["zero_time_valid_candidates"],
                3,
            )
            self.assertEqual(
                live[0]["event_candidate_id_sha256"],
                "439c32c30ceb4840e0ba09596b5dfb9c83b1f57bfdfc68dd35788e7cdec4ec7b",
            )
        elif live:
            self.assertEqual(
                lane.validate_wave8_viet_minh_funnel(self.funnel),
                {
                    "events_touched": 12,
                    "sole_blocker_events": 0,
                    "zero_time_valid_candidates": 12,
                },
            )

    def test_current_duplicate_audit_is_zero_and_future_twins_fail_closed(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_viet_minh_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-vinh-yen-twin",
                "name": "Battle of Vinh Yen",
                "start_date": "1951-01-13",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_viet_minh_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

    def test_queue_drift_discovery_flag_and_unknown_outcome_fail_closed(self):
        future = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(
            next(item for item in future if item["candidate_id"] == "hced-Vinh Yen1951-1")
        )
        row["candidate_id"] = "hced-future-viet-minh-row"
        future.append(row)
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_viet_minh_queue_contracts(future)

        discovery = copy.deepcopy(self.hced_rows)
        row = next(item for item in discovery if item["candidate_id"] == "hced-Day River1951-1")
        row["do_not_rate_automatically"] = False
        with self.assertRaisesRegex(ValueError, "discovery safety flag changed"):
            lane.validate_wave8_viet_minh_queue_contracts(discovery)

        def pinned_hash(row):
            candidate_id = str(row.get("candidate_id"))
            if candidate_id in EXPECTED_HASHES:
                return EXPECTED_HASHES[candidate_id]
            return canonical_hced_row_sha256(row)

        unknown = copy.deepcopy(self.hced_rows)
        row = next(item for item in unknown if item["candidate_id"] == "hced-Day River1951-1")
        row["winner_raw"] = "Unknown"
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "named outcome drift"):
                lane.validate_wave8_viet_minh_queue_contracts(unknown)

    def test_promoter_rejects_existing_candidate_duplicate_and_window_collision(self):
        entities, _, existing = self._installed()
        events = lane.promote_wave8_viet_minh_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_viet_minh_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_viet_minh_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-vinh-yen-duplicate",
                        "name": "Battle of Vinh Yen (1951)",
                        "year": 1951,
                    },
                ],
            )
        missing = dict(entities)
        missing.pop(VIET_MINH)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_viet_minh_contracts(
                self.hced_rows,
                missing,
                existing,
            )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_viet_minh_entities(entities)
        lane.install_wave8_viet_minh_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entities[VIET_MINH]["end_year"] = 1955
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_viet_minh_entities(entities)
        source_id = str(lane.WAVE8_VIET_MINH_SOURCES[0]["id"])
        sources[source_id]["title"] = "tampered title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_viet_minh_sources(sources)

    def test_counts_metadata_and_final_signature_are_pinned(self):
        self.assertEqual(
            lane.wave8_viet_minh_counts(),
            {
                "country_quarantine_additions": 0,
                "date_overrides": 1,
                "holds": 3,
                "new_entities": 2,
                "new_sources": 5,
                "newly_rated_events": 9,
                "outcome_overrides": 0,
                "point_quarantine_additions": 9,
                "promotion_contracts": 9,
                "reviewed_hced_rows": 12,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_viet_minh_cohort_counts(),
            {
                "first_indochina_war_viet_minh_engagements_1946_1954": 3,
                "first_indochina_war_viet_minh_engagements_1950_1954": 9,
            },
        )
        self.assertEqual(
            lane.wave8_viet_minh_audit_signature(),
            "b70b8bdb751435802c41898a27e198e8e8f89f643b1ca1144c5ec3a4f92f4c7f",
        )
        self.assertEqual(
            lane.wave8_viet_minh_audit_signature(),
            lane.WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_viet_minh_metadata(),
            {
                "counts": lane.wave8_viet_minh_counts(),
                "cohorts": lane.wave8_viet_minh_cohort_counts(),
                "final_audit_signature": lane.WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE,
                "promoted_candidate_ids": sorted(lane.WAVE8_VIET_MINH_CONTRACT_IDS),
            },
        )

    def test_current_release_is_all_or_none_for_the_lane(self):
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_VIET_MINH_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        self.assertIn(owned_ids, (set(), set(lane.WAVE8_VIET_MINH_CONTRACT_IDS)))
        if not owned_ids:
            self.assertNotIn(
                "accepted_wave8_viet_minh_hced_events",
                self.release_metadata.get("promotion", {}),
            )
            return
        self.assertEqual(len(owned), 9)
        self.assertEqual(
            self.release_metadata["promotion"]["accepted_wave8_viet_minh_hced_events"],
            9,
        )
        self.assertEqual(
            self.registry["coverage"][
                "candidate_keyed_wave8_viet_minh_hced_events"
            ],
            9,
        )
        entity_ids = {str(entity["id"]) for entity in self.release_entities}
        source_ids = {str(source["id"]) for source in self.release_sources}
        registry = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        self.assertLessEqual({VIET_MINH, MUONG_GARRISON}, entity_ids)
        self.assertLessEqual(
            {str(source["id"]) for source in lane.WAVE8_VIET_MINH_SOURCES},
            source_ids,
        )
        for entity_id in (VIET_MINH, MUONG_GARRISON):
            self.assertEqual(registry[entity_id]["status"], "rated")
            self.assertEqual(registry[entity_id]["identity_status"], "curated")


if __name__ == "__main__":
    unittest.main()
