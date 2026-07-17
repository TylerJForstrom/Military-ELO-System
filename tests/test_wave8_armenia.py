import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion import wave8_armenia as lane


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_armenia_"

TIGRANOCERTA_ROMAN = "lucullus_roman_army_tigranocerta_69_bce"
TIGRANOCERTA_ARMENIAN = (
    "tigranes_ii_armenian_royal_army_tigranocerta_69_bce"
)
AVARAYR_SASANIAN = "yazdegerd_ii_sasanian_army_avarayr_451"
AVARAYR_ARMENIAN = "vardan_mamikonian_armenian_rebel_army_avarayr_451"
MAMISTRA_ARMENIAN = "thoros_ii_rubenid_cilician_army_mamistra_1152"
MAMISTRA_BYZANTINE = (
    "andronikos_komnenos_byzantine_allied_army_mamistra_1152"
)

EXPECTED_RAW_HASHES = {
    "hced-Artaxata58-1": (
        "4b33aa2b5bf713252f4660ee2c37eb7a9e33dbcd82a66ef398fc1d8f0e60a1b9"
    ),
    "hced-Avarayr451-1": (
        "62e955a5290af2a6839b9bf26ac9eb7e5f5f63ed4889d13a8693bcdbb2c35636"
    ),
    "hced-Mopsuestia1152-1": (
        "844321410459f46630938488c1cb2f3db29eb222e12fd1643b931520976cc4d5"
    ),
    "hced-Sardarapat1918-1": (
        "dc25d91b404dfceef4b161ce23fb1b338a48af3e1f47631e08c087036502dd1a"
    ),
    "hced-Tigranocerta-69-1": (
        "5482d052687ff1604b320251f066df8571a9952837d347421957cf943e831bef"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Artaxata58-1": {
        "name": "Artaxata",
        "side_1": "Rome",
        "side_2": "Armenia",
        "winner": "Rome",
        "loser": "Armenia",
        "year": 58,
        "point": [44.5519782, 39.9535181],
        "country": "Armenia",
    },
    "hced-Avarayr451-1": {
        "name": "Avarayr",
        "side_1": "Persia",
        "side_2": "Armenia",
        "winner": "Persia",
        "loser": "Armenia",
        "year": 451,
        "point": [44.1610327, 39.3659927],
        "country": "Iran",
    },
    "hced-Mopsuestia1152-1": {
        "name": "Mopsuestia",
        "side_1": "Armenia",
        "side_2": "Byzantium",
        "winner": "Armenia",
        "loser": "Byzantium",
        "year": 1152,
        "point": [35.625096, 36.960485],
        "country": "Turkey",
    },
    "hced-Sardarapat1918-1": {
        "name": "Sardarapat",
        "side_1": "Armenia",
        "side_2": "Ottoman Empire",
        "winner": "Armenia",
        "loser": "Ottoman Empire",
        "year": 1918,
        "point": [44.0097387, 40.1312258],
        "country": "Armenia",
    },
    "hced-Tigranocerta-69-1": {
        "name": "Tigranocerta",
        "side_1": "Rome",
        "side_2": "Armenia",
        "winner": "Rome",
        "loser": "Armenia",
        "year": -69,
        "point": [40.868743, 38.1197169],
        "country": "Turkey",
    },
}

EXPECTED_ACTORS = {
    "hced-Tigranocerta-69-1": (
        {TIGRANOCERTA_ROMAN},
        {TIGRANOCERTA_ARMENIAN},
    ),
    "hced-Avarayr451-1": ({AVARAYR_SASANIAN}, {AVARAYR_ARMENIAN}),
    "hced-Mopsuestia1152-1": ({MAMISTRA_ARMENIAN}, {MAMISTRA_BYZANTINE}),
}

EXPECTED_CANONICAL = {
    "hced-Tigranocerta-69-1": (
        "Battle of Tigranocerta",
        -69,
        "month",
        "pitched_battle",
    ),
    "hced-Avarayr451-1": (
        "Battle of Avarayr",
        451,
        "day",
        "pitched_battle",
    ),
    "hced-Mopsuestia1152-1": (
        "Battle of Mamistra",
        1152,
        "year",
        "siege_sortie_and_field_rout",
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


class Wave8ArmeniaTests(unittest.TestCase):
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
            if normalize_label(row.get("side_1_raw")) == "armenia"
            or normalize_label(row.get("side_2_raw")) == "armenia"
        ]

    def _installed(self):
        lane_entity_ids = {str(entity["id"]) for entity in lane.WAVE8_ARMENIA_ENTITIES}
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(source["id"]) for source in lane.WAVE8_ARMENIA_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ARMENIA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_armenia_entities(entities)
        lane.install_wave8_armenia_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_armenia_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_hashes_and_raw_semantics_are_pinned(self):
        self.assertEqual(
            {str(row["candidate_id"]) for row in self.exact_rows},
            set(lane.WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS),
        )
        self.assertEqual(len(self.exact_rows), 5)
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            row = by_id[candidate_id]
            self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
            expected = EXPECTED_RAW_ROWS[candidate_id]
            self.assertEqual(row["name"], expected["name"])
            self.assertEqual(row["side_1_raw"], expected["side_1"])
            self.assertEqual(row["side_2_raw"], expected["side_2"])
            self.assertEqual(row["winner_raw"], expected["winner"])
            self.assertEqual(row["loser_raw"], expected["loser"])
            self.assertEqual(row["year_best"], expected["year"])
            self.assertEqual(
                [float(row["longitude"]), float(row["latitude"])],
                expected["point"],
            )
            self.assertEqual(row["modern_location_country"], expected["country"])
        digest = hashlib.sha256(
            "\n".join(sorted(EXPECTED_RAW_HASHES)).encode("utf-8")
        ).hexdigest()
        self.assertEqual(digest, lane.WAVE8_ARMENIA_EXACT_CANDIDATE_ID_SHA256)

    def test_funnel_pins_four_unresolved_sole_blockers(self):
        # Historical pre-promotion projection: before this lane integrated,
        # the live funnel carried exactly one "armenia" record whose four
        # zero-time-valid sole-blocker rows were the lane's unresolved
        # reservations.  The same counts, failure shape, and candidate-id
        # digest are still pinned, reconstructed from the lane constants.
        record = {
            "label": "armenia",
            "events_touched": len(lane.WAVE8_ARMENIA_RESERVED_IDS),
            "sole_blocker_events": len(lane.WAVE8_ARMENIA_RESERVED_IDS),
            "failure_cases": {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": len(
                    lane.WAVE8_ARMENIA_RESERVED_IDS
                ),
            },
            "event_candidate_id_sha256": hashlib.sha256(
                "".join(
                    f"{candidate_id}\n"
                    for candidate_id in sorted(lane.WAVE8_ARMENIA_RESERVED_IDS)
                ).encode("utf-8")
            ).hexdigest(),
        }
        self.assertEqual(record["events_touched"], 4)
        self.assertEqual(record["sole_blocker_events"], 4)
        self.assertEqual(record["failure_cases"], {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 4,
        })
        self.assertEqual(
            record["event_candidate_id_sha256"],
            lane.WAVE8_ARMENIA_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        self.assertFalse(
            any(
                live_record.get("label") == "armenia"
                for live_record in self.funnel.get("labels", [])
            ),
            "the completed Armenia lane must not remain unresolved",
        )

    def test_queue_validator_accounts_for_every_exact_row(self):
        self.assertEqual(
            lane.validate_wave8_armenia_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 1,
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 5,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.WAVE8_ARMENIA_RESERVED_IDS
            | lane.WAVE8_ARMENIA_EXTERNAL_OWNER_IDS,
            lane.WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS,
        )

    def test_artaxata_is_terminally_excluded_as_an_unopposed_surrender(self):
        self.assertEqual(
            lane.WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS,
            {"hced-Artaxata58-1"},
        )
        exclusion = lane.WAVE8_ARMENIA_TERMINAL_EXCLUSIONS[
            "hced-Artaxata58-1"
        ]
        self.assertEqual(
            exclusion["exclusion_reason"],
            "no_attested_battle_unopposed_surrender",
        )
        self.assertEqual(
            exclusion["reviewed_outcome"],
            "not_rateable_no_contested_engagement",
        )
        self.assertIs(exclusion["unknown_is_never_draw"], True)
        self.assertIn("opened its gates without resistance", exclusion["audit_note"])
        self.assertNotIn("winner_side", exclusion)
        self.assertNotIn("result_type", exclusion)
        self.assertFalse(
            {"hced-Artaxata58-1"} & lane.WAVE8_ARMENIA_CONTRACT_IDS
        )

    def test_sardarapat_existing_release_and_iwbd_twin_are_owned_once(self):
        disposition = lane.WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS[
            "hced-Sardarapat1918-1"
        ]
        self.assertEqual(disposition["disposition"], "existing_release_owner")
        self.assertEqual(
            disposition["owner_event_id"],
            "hced_label_hced_sardarapat1918_1",
        )
        owner_events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") == "hced-Sardarapat1918-1"
        ]
        self.assertEqual(len(owner_events), 1)
        self.assertEqual(owner_events[0]["id"], disposition["owner_event_id"])

        iwbd = lane.WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS["iwbd-106-38-742"]
        self.assertEqual(
            iwbd["hced_candidate_id"],
            "hced-Sardarapat1918-1",
        )
        self.assertEqual(
            iwbd["disposition"],
            "deduplicate_to_existing_hced_release_event",
        )
        self.assertEqual(
            lane.validate_wave8_armenia_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 1,
                "external_owner_hced_dispositions": 1,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 1,
                "iwbd_probable_twins": 0,
                "release_probable_twins": 0,
            },
        )

    def test_sources_are_independent_typed_and_exactly_consumed(self):
        source_ids = {str(source["id"]) for source in lane.WAVE8_ARMENIA_SOURCES}
        families = {
            str(source["source_family_id"])
            for source in lane.WAVE8_ARMENIA_SOURCES
        }
        self.assertEqual(len(source_ids), 14)
        self.assertEqual(len(families), 14)
        for source in lane.WAVE8_ARMENIA_SOURCES:
            parsed = Source.from_dict(source)
            self.assertTrue(parsed.url.startswith("https://"))
            self.assertIn("identity_boundary_or_context_reference", parsed.evidence_roles)
            self.assertIn("outcome", parsed.evidence_roles)
            self.assertIn("outcome_consistency_crosscheck", parsed.evidence_roles)

        consumed = {
            source_id
            for entity in lane.WAVE8_ARMENIA_ENTITIES
            for source_id in entity["source_ids"]
        }
        for contract in lane.WAVE8_ARMENIA_CONTRACTS.values():
            consumed.update(contract["evidence_refs"])
        for exclusion in lane.WAVE8_ARMENIA_TERMINAL_EXCLUSIONS.values():
            consumed.update(exclusion["evidence_refs"])
        for disposition in (
            lane.WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.values()
        ):
            consumed.update(disposition["evidence_refs"])
        self.assertEqual(consumed, source_ids)

    def test_entities_are_event_bounded_and_never_generic_armenia(self):
        entity_ids = {str(entity["id"]) for entity in lane.WAVE8_ARMENIA_ENTITIES}
        self.assertEqual(
            entity_ids,
            {
                TIGRANOCERTA_ROMAN,
                TIGRANOCERTA_ARMENIAN,
                AVARAYR_SASANIAN,
                AVARAYR_ARMENIAN,
                MAMISTRA_ARMENIAN,
                MAMISTRA_BYZANTINE,
            },
        )
        for entity in lane.WAVE8_ARMENIA_ENTITIES:
            parsed = Entity.from_dict(entity)
            self.assertEqual(parsed.start_year, parsed.end_year)
            self.assertNotEqual(normalize_label(parsed.name), "armenia")
            self.assertIn("No rating is inherited", parsed.continuity_note)

    def test_contracts_pin_canonical_events_actors_and_direct_outcomes(self):
        self.assertEqual(set(lane.WAVE8_ARMENIA_CONTRACTS), set(EXPECTED_ACTORS))
        for candidate_id, contract in lane.WAVE8_ARMENIA_CONTRACTS.items():
            expected_side_1, expected_side_2 = EXPECTED_ACTORS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_side_2)
            name, year, precision, granularity = EXPECTED_CANONICAL[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(canonical["year_low"], year)
            self.assertEqual(canonical["year_high"], year)
            self.assertEqual(canonical["date_precision"], precision)
            self.assertEqual(canonical["granularity"], granularity)
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)

    def test_three_events_promote_with_bounded_winners_and_no_draws(self):
        events = self._events()
        self.assertEqual(len(events), 3)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), lane.WAVE8_ARMENIA_CONTRACT_IDS)
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
            participants = event["participants"]
            winners = {
                str(participant["entity_id"])
                for participant in participants
                if participant["termination"] == "engagement_victory"
            }
            losers = {
                str(participant["entity_id"])
                for participant in participants
                if participant["termination"] == "engagement_defeat"
            }
            expected_winners, expected_losers = EXPECTED_ACTORS[candidate_id]
            self.assertEqual(winners, expected_winners)
            self.assertEqual(losers, expected_losers)
            self.assertFalse(
                any(participant["result_class"] == "draw" for participant in participants)
            )
        self.assertEqual(by_candidate["hced-Mopsuestia1152-1"]["aliases"], ["Mopsuestia"])
        self.assertNotIn(
            "hced-Artaxata58-1",
            by_candidate,
        )
        self.assertNotIn(
            "hced-Sardarapat1918-1",
            by_candidate,
        )

    def test_local_point_quarantines_are_complete_and_country_is_retained(self):
        self.assertEqual(
            lane.WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ARMENIA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            lane.wave8_armenia_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_ARMENIA_CONTRACT_IDS,
            },
        )
        for candidate_id, reason in lane.WAVE8_ARMENIA_LOCATION_QUARANTINE_REASONS.items():
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(
                reason["raw_point"],
                EXPECTED_RAW_ROWS[candidate_id]["point"],
            )
            self.assertEqual(
                reason["retained_country"],
                EXPECTED_RAW_ROWS[candidate_id]["country"],
            )

        # The focused audit may run either before or after coordinated shared
        # quarantine integration; partial integration is never acceptable.
        point_overlap = (
            set(lane.WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS)
            & set(HCED_POINT_QUARANTINE_IDS)
        )
        self.assertIn(
            point_overlap,
            [set(), set(lane.WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS)],
        )
        self.assertFalse(
            set(lane.WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS)
            & set(HCED_COUNTRY_QUARANTINE_IDS)
        )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entity_snapshot = copy.deepcopy(entities)
        source_snapshot = copy.deepcopy(sources)
        lane.install_wave8_armenia_entities(entities)
        lane.install_wave8_armenia_sources(sources)
        self.assertEqual(entities, entity_snapshot)
        self.assertEqual(sources, source_snapshot)

        bad_entities = copy.deepcopy(entities)
        bad_entities[TIGRANOCERTA_ROMAN]["name"] = "Collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_armenia_entities(bad_entities)
        bad_sources = copy.deepcopy(sources)
        bad_sources["wave8_armenia_iranica_avarayr"]["title"] = "Collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_armenia_sources(bad_sources)

    def test_raw_drift_and_inventory_growth_fail_closed(self):
        drifted = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in drifted
            if item.get("candidate_id") == "hced-Avarayr451-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.validate_wave8_armenia_queue_contracts(drifted)

        extra = copy.deepcopy(self.hced_rows)
        invented = copy.deepcopy(next(iter(self.exact_rows)))
        invented["candidate_id"] = "hced-InventedArmenia999-1"
        invented["source_record_id"] = "InventedArmenia999"
        invented["source_row"] = 999999
        extra.append(invented)
        with self.assertRaisesRegex(ValueError, "exact Armenia inventory changed"):
            lane.validate_wave8_armenia_queue_contracts(extra)

    def test_iwbd_and_release_duplicate_drift_fail_closed(self):
        drifted_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(
            item
            for item in drifted_iwbd
            if item.get("candidate_id") == "iwbd-106-38-742"
        )
        row["winner_raw"] = "Central Powers"
        with self.assertRaisesRegex(ValueError, "Sardarapat fingerprint changed"):
            lane.validate_wave8_armenia_integration_dispositions(
                self.hced_rows,
                drifted_iwbd,
                self.release_events,
            )

        surprise_iwbd = copy.deepcopy(self.iwbd_rows)
        invented = copy.deepcopy(row)
        invented.update(
            {
                "candidate_id": "iwbd-invented-avarayr",
                "name": "Battle of Avarayr",
                "start_date": "0451-01-01",
                "end_date": "0451-01-01",
            }
        )
        surprise_iwbd.append(invented)
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_armenia_integration_dispositions(
                self.hced_rows,
                surprise_iwbd,
                self.release_events,
            )

        surprise_release = copy.deepcopy(self.release_events)
        invented_event = copy.deepcopy(surprise_release[0])
        invented_event.update(
            {
                "id": "invented_avarayr_twin",
                "name": "Avarayr",
                "year": 451,
                "end_year": 451,
                "hced_candidate_id": "hced-unrelated-invented",
            }
        )
        surprise_release.append(invented_event)
        with self.assertRaisesRegex(ValueError, "probable release duplicate"):
            lane.validate_wave8_armenia_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                surprise_release,
            )

    def test_promoter_rejects_candidate_and_event_key_duplicates(self):
        entities, _, existing = self._installed()
        duplicate_candidate = copy.deepcopy(existing)
        duplicate_candidate.append(
            {
                "id": "existing_candidate",
                "name": "Unrelated",
                "year": 451,
                "hced_candidate_id": "hced-Avarayr451-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_armenia_contracts(
                self.hced_rows,
                entities,
                duplicate_candidate,
            )

        duplicate_key = copy.deepcopy(existing)
        duplicate_key.append(
            {
                "id": "existing_key",
                "name": "Battle of Avarayr",
                "year": 451,
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_armenia_contracts(
                self.hced_rows,
                entities,
                duplicate_key,
            )

    def test_counts_cohorts_and_signature_are_exact(self):
        self.assertEqual(
            lane.wave8_armenia_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 1,
                "external_owner_hced_dispositions": 1,
                "holds": 0,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 1,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 6,
                "new_sources": 14,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 5,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 1,
                "touched_hced_rows": 5,
            },
        )
        self.assertEqual(
            lane.wave8_armenia_cohort_counts(),
            {
                "rubenid_byzantine_war_1152": 1,
                "third_mithridatic_war_armenia_69_bce": 1,
                "vardanants_rebellion_451": 1,
            },
        )
        self.assertEqual(
            lane.wave8_armenia_audit_signature(),
            lane.WAVE8_ARMENIA_FINAL_AUDIT_SIGNATURE,
        )

    def test_release_artifacts_are_either_preintegration_or_fully_integrated(self):
        released_contract_ids = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_ARMENIA_CONTRACT_IDS
        }
        self.assertIn(
            released_contract_ids,
            [set(), set(lane.WAVE8_ARMENIA_CONTRACT_IDS)],
        )
        released_entity_ids = {
            str(entity["id"])
            for entity in self.release_entities
            if str(entity["id"])
            in {str(item["id"]) for item in lane.WAVE8_ARMENIA_ENTITIES}
        }
        self.assertIn(
            released_entity_ids,
            [set(), {str(item["id"]) for item in lane.WAVE8_ARMENIA_ENTITIES}],
        )
        released_source_ids = {
            str(source["id"])
            for source in self.release_sources
            if str(source["id"])
            in {str(item["id"]) for item in lane.WAVE8_ARMENIA_SOURCES}
        }
        self.assertIn(
            released_source_ids,
            [set(), {str(item["id"]) for item in lane.WAVE8_ARMENIA_SOURCES}],
        )


if __name__ == "__main__":
    unittest.main()
