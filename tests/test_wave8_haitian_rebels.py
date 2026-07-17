import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_haitian_rebels as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_haitian_rebels_"
FINAL_AUDIT_SIGNATURE = (
    "49067b26bfdc0409bdf40472144e67df57031c2a7bc979ea4b37e84056bb392f"
)
FUNNEL_CANDIDATE_ID_SHA256 = (
    "f29f50e86e7f9a7bb36ee51b166d5efc4826578d50b546f92fb66182e700a078"
)

INDIGENOUS_ARMY_ID = "dessalines_indigenous_army_arcahaie_coalition_1803"
FRENCH_EXPEDITION_ID = "rochambeau_saint_domingue_expedition_1803"

EXPECTED_RAW_HASHES = {
    "hced-Crete-a-Perriot1802-1": (
        "475b546926eed3714b697787d43ed5b58b3805b59c85408f9d9457322b539ea1"
    ),
    "hced-Gonaives1802-1": (
        "823cf0351421929b0ceddfa9ebe93d388f4fe34db3402033cb87bce96de651d4"
    ),
    "hced-Port-au-Prince1803-1": (
        "f8e6710adcdc1e997544feb0c1ab7e7c3381d81980ecb9fd4a5b6a596b4d4c16"
    ),
    "hced-Vertieres1803-1": (
        "616156618886ffae516e762ab30a9afe033045ec1d945c207b6a27930245deff"
    ),
}

EXPECTED_PROMOTIONS = {
    "hced-Port-au-Prince1803-1": (
        "Siege and evacuation of Port-au-Prince (1803)",
        "month_range",
        "siege_and_city_evacuation",
        0.82,
    ),
    "hced-Vertieres1803-1": (
        "Battle of Vertieres",
        "day",
        "engagement_and_fort_evacuation",
        0.86,
    ),
}

EXPECTED_RELATED_HASHES = {
    "hced-Azua1844-1": (
        "2c59fbed65521ed79b5d5b6004c5275db64da25638db65d2f6d97fbae1b6c4cb"
    ),
    "hced-Cabeza de las Marias and las Hicoteas1844-1": (
        "60efe67f6f9cff2c3305003890e4c01cc30ce90278fe010caa125266c99eb8b4"
    ),
    "hced-El Numero1849-1": (
        "fac408e00c7ebe0beae2880f30a8640bfa254fd48dbcb5be557256b9b92d27a2"
    ),
    "hced-Sabana Larga1856-1": (
        "b1e041908f7fcf8f14bb28f203671a43c9929f485b7b2a3e737c1d2757dfc3cf"
    ),
    "hced-Santo Domingo1802-1803-1": (
        "557c799311d8310f1c7ce76107b663d802d3f30de1d873007169bf93ecd30082"
    ),
    "hced-Santo Domingo1805-1": (
        "100b9326b4d08e44f7e10a2bc51ab70346637df2d57ffa692e551cf4033f36fe"
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


class Wave8HaitianRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "haitian rebels"
            or normalize_label(row.get("side_2_raw")) == "haitian rebels"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_HAITIAN_REBELS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_HAITIAN_REBELS_SOURCES
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
            not in lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_haitian_rebels_entities(entities)
        lane.install_wave8_haitian_rebels_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_haitian_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_queue_pins_all_and_only_four_exact_label_rows(self) -> None:
        exact_by_id = {
            str(row["candidate_id"]): row for row in self.exact_rows
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_RESERVED_IDS,
            frozenset(EXPECTED_RAW_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(exact_by_id[candidate_id]),
                expected_hash,
            )
            row = exact_by_id[candidate_id]
            self.assertEqual(row["side_1_raw"], "Haitian Rebels")
            self.assertEqual(row["side_2_raw"], "France")

        payload = "".join(f"{item}\n" for item in sorted(exact_by_id))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(
            lane.validate_wave8_haitian_rebels_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 0,
                "holds": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )

    def test_funnel_pins_four_sole_blockers_without_generic_identity(self) -> None:
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT,
            {
                "event_candidate_id_sha256": FUNNEL_CANDIDATE_ID_SHA256,
                "events_touched": 4,
                "failure_case": "zero_time_valid_candidates",
                "failure_case_count": 4,
                "label": "haitian rebels",
                "marginal_events": 4,
                "newly_unblocked_candidate_id_sha256": FUNNEL_CANDIDATE_ID_SHA256,
                "sole_blocker_events": 4,
            },
        )
        historical_funnel = {
            "greedy_batch": {
                "ranking": [
                    {
                        "events_touched": 4,
                        "label": "haitian rebels",
                        "marginal_events": 4,
                        "newly_unblocked_candidate_id_sha256": (
                            FUNNEL_CANDIDATE_ID_SHA256
                        ),
                    }
                ]
            },
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": FUNNEL_CANDIDATE_ID_SHA256,
                    "events_touched": 4,
                    "failure_cases": {"zero_time_valid_candidates": 4},
                    "label": "haitian rebels",
                    "sole_blocker_events": 4,
                    "time_valid_candidate_ids": [],
                }
            ],
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "label_failures": [
                        {
                            "failure_case": "zero_time_valid_candidates",
                            "label": "haitian rebels",
                        }
                    ],
                    "sole_blocker_label": "haitian rebels",
                }
                for candidate_id in sorted(EXPECTED_RAW_HASHES)
            ],
        }
        self.assertEqual(
            lane.validate_wave8_haitian_rebels_funnel(historical_funnel),
            {
                "exact_label_rows": 4,
                "shared_label_rows": 0,
                "sole_blocker_rows": 4,
            },
        )
        label = next(
            row
            for row in historical_funnel["labels"]
            if row["label"] == "haitian rebels"
        )
        self.assertEqual(label["event_candidate_id_sha256"], FUNNEL_CANDIDATE_ID_SHA256)
        self.assertEqual(label["events_touched"], 4)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["candidate_ids"], [])
        self.assertEqual(label["time_valid_candidate_ids"], [])
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 4)
        self.assertFalse(
            any(
                row.get("label") == "haitian rebels"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Haitian Rebels lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id"))
                in lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS
                for row in self.funnel.get("row_label_data", [])
            ),
            "promoted Haitian Rebels candidates must not remain in the live funnel",
        )

    def test_dispositions_are_two_promotions_and_two_unknown_holds(self) -> None:
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS,
            frozenset(EXPECTED_PROMOTIONS),
        )
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_HOLD_IDS,
            frozenset(
                {
                    "hced-Crete-a-Perriot1802-1",
                    "hced-Gonaives1802-1",
                }
            ),
        )
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS)
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS)
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES)

    def test_holds_never_invent_a_draw_or_opposing_entities(self) -> None:
        for hold in lane.WAVE8_HAITIAN_REBELS_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)
            self.assertIn("not promoted", hold["hold_reason"].casefold())
            self.assertIn("draw", hold["hold_reason"].casefold())
            for forbidden in (
                "winner_side",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "outcome_source_ids",
                "outcome_source_family_ids",
            ):
                self.assertNotIn(forbidden, hold)

    def test_ravine_hold_records_the_authoritative_outcome_conflict(self) -> None:
        hold = lane.WAVE8_HAITIAN_REBELS_HOLDS["hced-Gonaives1802-1"]
        reason = hold["hold_reason"].casefold()
        self.assertIn("ravine-a-couleuvres", reason)
        self.assertIn("conflict", reason)
        self.assertIn("invent certainty", reason)
        self.assertIn("wave8_haitian_rebels_ardouin_tome5", hold["evidence_refs"])
        self.assertIn(
            "wave8_haitian_rebels_fondation_land_operations",
            hold["evidence_refs"],
        )
        self.assertIn(
            "wave8_haitian_rebels_dorsainvil_manual",
            hold["evidence_refs"],
        )

    def test_crete_hold_preserves_assault_breakout_occupation_granularity(self) -> None:
        hold = lane.WAVE8_HAITIAN_REBELS_HOLDS[
            "hced-Crete-a-Perriot1802-1"
        ]
        reason = hold["hold_reason"].casefold()
        for phrase in ("assaults", "breakout", "occupation"):
            self.assertIn(phrase, reason)
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "multi_assault_siege_and_breakout",
        )
        self.assertEqual(hold["canonical_event"]["date_text"], "4-24 March 1802")

    def test_sources_are_model_valid_and_preserve_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_HAITIAN_REBELS_SOURCES), 13)
        families = {
            source["source_family_id"]
            for source in lane.WAVE8_HAITIAN_REBELS_SOURCES
        }
        self.assertGreaterEqual(len(families), 12)
        for source in lane.WAVE8_HAITIAN_REBELS_SOURCES:
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                Source.from_dict(source).to_dict(),
                source,
            )

    def test_entities_are_1803_regime_bounded_not_generic_haiti_or_france(self) -> None:
        self.assertEqual(len(lane.WAVE8_HAITIAN_REBELS_ENTITIES), 2)
        by_id = {
            entity["id"]: entity for entity in lane.WAVE8_HAITIAN_REBELS_ENTITIES
        }
        self.assertEqual(set(by_id), {INDIGENOUS_ARMY_ID, FRENCH_EXPEDITION_ID})
        for entity in by_id.values():
            self.assertEqual((entity["start_year"], entity["end_year"]), (1803, 1803))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            for boundary in ("1802", "1804", "civil-war", "no rating is inherited"):
                self.assertIn(boundary, note)
            self.assertEqual(Entity.from_dict(entity).to_dict(), entity)
        self.assertIn("independence", by_id[INDIGENOUS_ARMY_ID]["kind"])
        self.assertIn("colonial", by_id[FRENCH_EXPEDITION_ID]["kind"])

    def test_promotions_emit_only_port_au_prince_and_vertieres(self) -> None:
        events = self._events()
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = by_candidate[candidate_id]
            name, precision, granularity, confidence = expected
            self.assertEqual(event["name"], name)
            self.assertEqual(event["date_precision"], precision)
            self.assertEqual(event["reviewed_granularity"], granularity)
            self.assertEqual(event["confidence"], confidence)
            self.assertEqual(event["year"], 1803)
            self.assertEqual(event["end_year"], 1803)
            self.assertEqual(event["war_type"], "colonial_anti_colonial")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            participants = {item["entity_id"]: item for item in event["participants"]}
            self.assertEqual(set(participants), {INDIGENOUS_ARMY_ID, FRENCH_EXPEDITION_ID})
            self.assertEqual(
                participants[INDIGENOUS_ARMY_ID]["result_class"],
                "limited_victory",
            )
            self.assertEqual(
                participants[FRENCH_EXPEDITION_ID]["result_class"],
                "limited_defeat",
            )
            self.assertFalse(any(item.get("result_class") == "draw" for item in event["participants"]))

    def test_promoted_outcomes_align_with_raw_rows_without_override(self) -> None:
        for candidate_id, contract in lane.WAVE8_HAITIAN_REBELS_CONTRACTS.items():
            row = self.hced_by_id[candidate_id]
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 3)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)

    def test_promoted_points_are_withheld_and_haiti_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Haiti")
            self.assertIn("location_provenance", event)

    def test_local_promotion_does_not_mutate_global_quarantine_sets(self) -> None:
        point_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        country_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self._events()
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), country_before)

    def test_emitted_events_and_installed_fixtures_are_model_valid(self) -> None:
        entities, sources, _ = self._installed()
        for entity_id in (INDIGENOUS_ARMY_ID, FRENCH_EXPEDITION_ID):
            Entity.from_dict(entities[entity_id])
        for source in lane.WAVE8_HAITIAN_REBELS_SOURCES:
            Source.from_dict(sources[source["id"]])
        for event in self._events():
            Event.from_dict(event)

    def test_nearby_haiti_france_and_colonial_rows_are_distinct_boundaries(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS),
            set(EXPECTED_RELATED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_RELATED_HASHES.items():
            row = self.hced_by_id[candidate_id]
            disposition = lane.WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS[
                candidate_id
            ]
            self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
            self.assertEqual(disposition["raw_row_sha256"], expected_hash)
            self.assertNotIn(candidate_id, lane.WAVE8_HAITIAN_REBELS_RESERVED_IDS)
            if candidate_id == "hced-Santo Domingo1802-1803-1":
                self.assertIs(disposition["outcome_not_adjudicated"], True)
                self.assertIsNone(disposition["owner_module"])
            else:
                self.assertIs(disposition["outcome_not_adjudicated"], False)
                self.assertEqual(
                    disposition["owner_module"],
                    "military_elo.promotion.wave8_haiti_regimes",
                )
        self.assertIn(
            "delegated_to_wave8_haiti_regimes",
            lane.WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS[
                "hced-Santo Domingo1805-1"
            ]["disposition"],
        )

    def test_iwbd_release_and_cross_lane_overlap_audits_are_zero(self) -> None:
        _, _, existing = self._installed()
        result = lane.validate_wave8_haitian_rebels_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            existing,
        )
        self.assertEqual(result["iwbd_probable_twins"], 0)
        self.assertEqual(result["iwbd_zero_overlap_candidates"], 4)
        self.assertEqual(result["related_hced_dispositions"], 6)
        self.assertEqual(result["integration_dispositions"], 6)
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS)
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(
            lane.WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        )
        self.assertFalse(lane.WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS)

    def test_integration_validator_fails_closed_on_new_hced_twin(self) -> None:
        planted = copy.deepcopy(self.hced_by_id["hced-Vertieres1803-1"])
        planted["candidate_id"] = "hced-PlantedVertieres1803-1"
        planted["source_record_id"] = "PlantedVertieres1803"
        planted["side_1_raw"] = "Unrelated A"
        planted["side_2_raw"] = "Unrelated B"
        with self.assertRaisesRegex(ValueError, "unreviewed HCED twin"):
            lane.validate_wave8_haitian_rebels_integration_dispositions(
                [*self.hced_rows, planted],
                self.iwbd_rows,
                (),
            )

    def test_integration_validator_fails_closed_on_new_iwbd_twin(self) -> None:
        planted = {
            "candidate_id": "iwbd-planted-vertieres",
            "name": "Battle of Vertieres",
            "start_date": "1803-11-18",
            "end_date": "1803-11-18",
        }
        with self.assertRaisesRegex(ValueError, "unreviewed IWBD twin"):
            lane.validate_wave8_haitian_rebels_integration_dispositions(
                self.hced_rows,
                [*self.iwbd_rows, planted],
                (),
            )

    def test_integration_validator_fails_closed_on_new_release_twin(self) -> None:
        planted = {
            "id": "planted_crete_twin",
            "name": "Siege of Crete-a-Pierrot",
            "year": 1802,
        }
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_haitian_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [planted],
            )

    def test_queue_validator_fails_closed_on_raw_row_tamper(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in rows
            if row["candidate_id"] == "hced-Port-au-Prince1803-1"
        )
        target["winner_raw"] = "France"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.validate_wave8_haitian_rebels_queue_contracts(rows)

    def test_installers_are_idempotent_and_fail_on_conflicting_fixture(self) -> None:
        entities, sources, _ = self._installed()
        lane.install_wave8_haitian_rebels_entities(entities)
        lane.install_wave8_haitian_rebels_sources(sources)
        self.assertIn(INDIGENOUS_ARMY_ID, entities)
        source_id = lane.WAVE8_HAITIAN_REBELS_SOURCES[0]["id"]
        conflicting = copy.deepcopy(sources)
        conflicting[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_haitian_rebels_sources(conflicting)

    def test_current_release_is_either_unwired_or_fully_wired_never_partial(self) -> None:
        released_candidates = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
            or event.get("hced_candidate_id")
            in lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS
        }
        expected = set(lane.WAVE8_HAITIAN_REBELS_CONTRACT_IDS)
        self.assertIn(released_candidates, (set(), expected))

    def test_counts_cohorts_and_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_haitian_rebels_cohort_counts(),
            {
                "dessalines_indigenous_army_1803": 2,
                "louverture_autonomous_saint_domingue_army_1802": 2,
            },
        )
        counts = lane.wave8_haitian_rebels_counts()
        self.assertEqual(counts["reviewed_hced_rows"], 4)
        self.assertEqual(counts["promotion_contracts"], 2)
        self.assertEqual(counts["holds"], 2)
        self.assertEqual(counts["terminal_exclusions"], 0)
        self.assertEqual(counts["new_entities"], 2)
        self.assertEqual(counts["new_sources"], 13)
        self.assertEqual(counts["point_quarantine_additions"], 2)
        self.assertEqual(counts["country_quarantine_additions"], 0)
        self.assertEqual(counts["outcome_overrides"], 0)
        self.assertEqual(
            lane.wave8_haitian_rebels_audit_signature(),
            FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.WAVE8_HAITIAN_REBELS_FINAL_AUDIT_SIGNATURE,
            FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
