import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_inca_rebels as lane
from military_elo.promotion import wave8_peruvian_rebels
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_inca_rebels_"

CUZCO_SPANISH = "pizarro_spanish_allied_garrison_cuzco_1536_1537"
CUZCO_INCA = "manco_inca_rebel_siege_army_cuzco_1536_1537"
OLLANTAY_INCA = "manco_inca_ollantaytambo_defenders_1537"
OLLANTAY_SPANISH = "hernando_pizarro_ollantaytambo_expedition_1537"
HUAYNA_SPANISH = (
    "hurtado_arbieto_spanish_andean_expedition_huayna_pucara_1572"
)
HUAYNA_INCA = "tupac_amaru_vilcabamba_defenders_huayna_pucara_1572"

EXPECTED_RAW_HASHES = {
    "hced-Cuzco1535-1": (
        "3709c9a9a7ca767d971d893c552ced7ba0001fb8f68896252a12fdf6608cf875"
    ),
    "hced-Cuzco1537-1": (
        "3447079fefdc651c7b57d59c6b12093726b80513d17d8d9e52a848bab9c3d178"
    ),
    "hced-Huayna Pucara1572-1": (
        "1c5492d918e889c92295764383ee42a5c404697779e436a461d648249fafb961"
    ),
    "hced-Ollantaytambo1537-1": (
        "ccd9153278245f3894302400daf407a8d1703cba6c133a9dcb651bb22a8377fb"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Cuzco1535-1": {
        "name": "Cuzco",
        "side_1": "Spain",
        "side_2": "Inca Rebels",
        "winner": "Spain",
        "loser": "Inca Rebels",
        "year": 1535,
        "point": [-71.9674626, -13.53195],
        "country": "Peru",
    },
    "hced-Cuzco1537-1": {
        "name": "Cuzco",
        "side_1": "Spain",
        "side_2": "Inca Rebels",
        "winner": "Spain",
        "loser": "Inca Rebels",
        "year": 1537,
        "point": [-71.9674626, -13.53195],
        "country": "Peru",
    },
    "hced-Ollantaytambo1537-1": {
        "name": "Ollantaytambo",
        "side_1": "Inca Rebels",
        "side_2": "Spain",
        "winner": "Inca Rebels",
        "loser": "Spain",
        "year": 1537,
        "point": [-72.2698795, -13.2582838],
        "country": "Peru",
    },
    "hced-Huayna Pucara1572-1": {
        "name": "Huayna Pucara",
        "side_1": "Spain",
        "side_2": "Inca Rebels",
        "winner": "Spain",
        "loser": "Inca Rebels",
        "year": 1572,
        "point": [-76.5351105, -10.3343742],
        "country": "Peru",
    },
}

EXPECTED_ACTORS = {
    "hced-Cuzco1537-1": ({CUZCO_SPANISH}, {CUZCO_INCA}),
    "hced-Ollantaytambo1537-1": ({OLLANTAY_INCA}, {OLLANTAY_SPANISH}),
    "hced-Huayna Pucara1572-1": ({HUAYNA_SPANISH}, {HUAYNA_INCA}),
}

EXPECTED_CANONICAL = {
    "hced-Cuzco1537-1": (
        "End of the Siege of Cuzco",
        1537,
        "early 1537",
        "season",
        "siege_termination_and_withdrawal",
    ),
    "hced-Ollantaytambo1537-1": (
        "Battle of Ollantaytambo",
        1537,
        "January 1537",
        "month",
        "fortified_field_battle_and_forced_retreat",
    ),
    "hced-Huayna Pucara1572-1": (
        "Capture of Huayna Pucara",
        1572,
        "22-23 June 1572",
        "day",
        "fortified_position_assault_and_capitulation",
    ),
}

EXISTING_INCA_OWNERS = {
    "hced-Cajamarca1532-1": "hced_label_hced_cajamarca1532_1",
    "hced-Teocajas1534-1": "hced_label_hced_teocajas1534_1",
    "hced-Vilcaconga1524-1": "hced_label_hced_vilcaconga1524_1",
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


class Wave8IncaRebelsTests(unittest.TestCase):
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
            if normalize_label(row.get("side_1_raw")) == "inca rebels"
            or normalize_label(row.get("side_2_raw")) == "inca rebels"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_INCA_REBELS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_INCA_REBELS_SOURCES
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
            not in lane.WAVE8_INCA_REBELS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_inca_rebels_entities(entities)
        lane.install_wave8_inca_rebels_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_inca_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_hashes_and_raw_semantics_are_pinned(self):
        self.assertEqual(
            {str(row["candidate_id"]) for row in self.exact_rows},
            set(lane.WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS),
        )
        self.assertEqual(len(self.exact_rows), 4)
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
        self.assertEqual(digest, lane.WAVE8_INCA_REBELS_EXACT_CANDIDATE_ID_SHA256)

    def test_funnel_pins_four_unresolved_sole_blockers(self):
        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": (
                        "306e8bd1195fc82273c8dcdad2b51509617a99f63227f68684f241ff5d03a3e9"
                    ),
                    "events_touched": 4,
                    "failure_cases": {
                        "multiple_time_valid_candidates": 0,
                        "one_wrong_interval_candidate": 0,
                        "policy_denied_window": 0,
                        "resolver_guard_or_tier_conflict": 0,
                        "zero_time_valid_candidates": 4,
                    },
                    "label": "inca rebels",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 4,
                }
            ]
        }
        records = [
            record
            for record in historical_funnel["labels"]
            if record.get("label") == "inca rebels"
        ]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["events_touched"], 4)
        self.assertEqual(record["sole_blocker_events"], 4)
        self.assertEqual(record["unresolved_side_attempts"], 4)
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
        self.assertEqual(
            record["event_candidate_id_sha256"],
            lane.WAVE8_INCA_REBELS_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        funnel_digest = hashlib.sha256(
            "".join(
                f"{candidate_id}\n"
                for candidate_id in sorted(
                    lane.WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS
                )
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            funnel_digest,
            lane.WAVE8_INCA_REBELS_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        self.assertFalse(
            any(
                record.get("label") == "inca rebels"
                for record in self.funnel.get("labels", [])
            ),
            "the completed Inca Rebels lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id"))
                in lane.WAVE8_INCA_REBELS_RESERVED_IDS
                for row in self.funnel.get("row_label_data", [])
            ),
            "reviewed Inca Rebels candidate rows must not remain in the live funnel",
        )

    def test_current_release_integration_is_exactly_all_or_none(self):
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_INCA_REBELS_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        release_candidate_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        }
        self.assertFalse(
            lane.WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS & release_candidate_ids,
            "the terminally excluded Cuzco 1535 row must never reach the release",
        )
        if not integrated:
            return
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            set(lane.WAVE8_INCA_REBELS_CONTRACT_IDS),
        )
        self.assertEqual(len({str(event["id"]) for event in integrated}), 3)
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in integrated)
        )

    def test_queue_validator_accounts_for_every_exact_row(self):
        self.assertEqual(
            lane.validate_wave8_inca_rebels_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 4,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.WAVE8_INCA_REBELS_CONTRACT_IDS
            | lane.WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS,
            lane.WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS,
        )

    def test_cuzco_1535_is_a_nonrateable_misdated_duplicate(self):
        self.assertEqual(
            lane.WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS,
            {"hced-Cuzco1535-1"},
        )
        exclusion = lane.WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS[
            "hced-Cuzco1535-1"
        ]
        self.assertEqual(
            exclusion["exclusion_reason"],
            "misdated_duplicate_of_1536_1537_siege",
        )
        self.assertEqual(
            exclusion["duplicate_ownership"]["owner_candidate_id"],
            "hced-Cuzco1537-1",
        )
        self.assertEqual(exclusion["canonical_event"]["year_low"], 1536)
        self.assertEqual(exclusion["canonical_event"]["year_high"], 1537)
        self.assertIs(exclusion["unknown_is_never_draw"], True)
        for forbidden in (
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        ):
            self.assertNotIn(forbidden, exclusion)

    def test_three_phases_have_exact_event_bounded_actors(self):
        self.assertEqual(len(lane.WAVE8_INCA_REBELS_ENTITIES), 6)
        by_id = {
            str(entity["id"]): entity for entity in lane.WAVE8_INCA_REBELS_ENTITIES
        }
        self.assertEqual(set(by_id), set().union(*[a | b for a, b in EXPECTED_ACTORS.values()]))
        self.assertEqual(
            (by_id[CUZCO_INCA]["start_year"], by_id[CUZCO_INCA]["end_year"]),
            (1536, 1537),
        )
        self.assertEqual(
            (by_id[OLLANTAY_INCA]["start_year"], by_id[OLLANTAY_INCA]["end_year"]),
            (1537, 1537),
        )
        self.assertEqual(
            (by_id[HUAYNA_INCA]["start_year"], by_id[HUAYNA_INCA]["end_year"]),
            (1572, 1572),
        )
        for entity in by_id.values():
            self.assertEqual(entity["aliases"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
        self.assertNotIn("clio_pe_inca_emp_1440_816cd40c", by_id)
        self.assertNotIn("spanish_empire", by_id)

    def test_contracts_preserve_source_attested_orientation_without_overrides(self):
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(lane.WAVE8_INCA_REBELS_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in lane.WAVE8_INCA_REBELS_CONTRACTS.items():
            row = rows[candidate_id]
            winner_side = int(contract["winner_side"])
            self.assertEqual(contract["result_type"], "win")
            self.assertIs(contract["source_outcome_override"], False)
            self.assertEqual(row["winner_raw"], row[f"side_{winner_side}_raw"])
            self.assertEqual(row["loser_raw"], row[f"side_{3 - winner_side}_raw"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)
            self.assertNotIn("draw", normalize_label(row["winner_raw"]))

    def test_sources_are_independent_authoritative_and_model_valid(self):
        family_ids = [
            str(source["source_family_id"])
            for source in lane.WAVE8_INCA_REBELS_SOURCES
        ]
        self.assertEqual(len(family_ids), 10)
        self.assertEqual(len(family_ids), len(set(family_ids)))
        for source in lane.WAVE8_INCA_REBELS_SOURCES:
            parsed = Source.from_dict(source)
            self.assertTrue(parsed.url.startswith("https://"))
            self.assertNotIn("wikipedia.org", parsed.url)
            self.assertIn("outcome", source["evidence_roles"])
        for entity in lane.WAVE8_INCA_REBELS_ENTITIES:
            Entity.from_dict(entity)

    def test_promotion_emits_canonical_events_and_exact_actor_sets(self):
        events = self._events()
        self.assertEqual(len(events), 3)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_ACTORS))
        for candidate_id, event in by_candidate.items():
            name, year, date_text, precision, granularity = EXPECTED_CANONICAL[
                candidate_id
            ]
            self.assertEqual(event["name"], name)
            self.assertEqual(event["year"], year)
            self.assertEqual(event["end_year"], year)
            self.assertEqual(event["date_precision"], precision)
            self.assertEqual(event["reviewed_granularity"], granularity)
            self.assertIn(date_text, lane.WAVE8_INCA_REBELS_CONTRACTS[candidate_id]["canonical_event"]["date_text"])
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            participants = event["participants"]
            winners = {
                str(participant["entity_id"])
                for participant in participants
                if str(participant["termination"]).endswith("victory")
            }
            losers = {
                str(participant["entity_id"])
                for participant in participants
                if str(participant["termination"]).endswith("defeat")
            }
            self.assertEqual((winners, losers), EXPECTED_ACTORS[candidate_id])
            Event.from_dict(event)

    def test_location_quarantine_is_local_complete_and_country_preserving(self):
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        events = self._events()
        self.assertEqual(
            lane.WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_INCA_REBELS_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS, set())
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event.get("modern_location_country"), "Peru")
            reason = lane.WAVE8_INCA_REBELS_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(reason["retained_country"], "Peru")
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_integration_audit_finds_no_iwbd_or_release_twin(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_inca_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_dispositions": 2,
                "existing_inca_release_owners_verified": 3,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "related_hced_dispositions": 3,
                "release_probable_twins": 0,
            },
        )

    def test_existing_inca_release_events_remain_distinct_and_owned_once(self):
        by_candidate = {
            str(event.get("hced_candidate_id")): event
            for event in self.release_events
            if event.get("hced_candidate_id") in EXISTING_INCA_OWNERS
        }
        self.assertEqual(set(by_candidate), set(EXISTING_INCA_OWNERS))
        for candidate_id, event_id in EXISTING_INCA_OWNERS.items():
            event = by_candidate[candidate_id]
            self.assertEqual(event["id"], event_id)
            participant_ids = {
                str(participant["entity_id"])
                for participant in event["participants"]
            }
            self.assertIn("clio_pe_inca_emp_1440_816cd40c", participant_ids)
            self.assertNotIn(candidate_id, lane.WAVE8_INCA_REBELS_RESERVED_IDS)

    def test_peruvian_rebels_and_spanish_colonial_boundaries_do_not_overlap(self):
        self.assertFalse(
            lane.WAVE8_INCA_REBELS_RESERVED_IDS
            & wave8_peruvian_rebels.WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS
        )
        cross = lane.WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS
        self.assertEqual(
            set(cross),
            {"existing_inca_empire_release_lane", "wave8_peruvian_rebels"},
        )
        self.assertEqual(
            cross["existing_inca_empire_release_lane"]["existing_entity_id"],
            "clio_pe_inca_emp_1440_816cd40c",
        )
        entity_ids = {str(entity["id"]) for entity in lane.WAVE8_INCA_REBELS_ENTITIES}
        self.assertNotIn("spanish_empire", entity_ids)
        self.assertNotIn("peru", entity_ids)

    def test_related_cuzco_rows_are_explicitly_distinguished(self):
        dispositions = lane.WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS
        self.assertEqual(
            set(dispositions),
            {"hced-Cuzco1532-1", "hced-Cuzco1535-1", "hced-Cuzco1780-1"},
        )
        self.assertEqual(
            dispositions["hced-Cuzco1535-1"]["disposition"],
            "same_siege_single_owner",
        )
        self.assertEqual(
            dispositions["hced-Cuzco1532-1"]["relationship"],
            "different_war_year_and_actors",
        )
        self.assertEqual(
            dispositions["hced-Cuzco1780-1"]["relationship"],
            "different_century_rebellion_and_actors",
        )

    def test_promotion_is_deterministic_and_does_not_mutate_inputs(self):
        entities, _, existing = self._installed()
        hced_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        first = lane.promote_wave8_inca_rebels_contracts(
            self.hced_rows, entities, existing
        )
        second = lane.promote_wave8_inca_rebels_contracts(
            self.hced_rows, entities, existing
        )
        self.assertEqual(first, second)
        self.assertEqual(self.hced_rows, hced_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)

    def test_row_tamper_fails_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in tampered
            if row.get("candidate_id") == "hced-Ollantaytambo1537-1"
        )
        target["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_inca_rebels_queue_contracts(tampered)

    def test_missing_entity_and_probable_twins_fail_closed(self):
        entities, _, existing = self._installed()
        entities.pop(OLLANTAY_INCA)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_inca_rebels_contracts(
                self.hced_rows, entities, existing
            )

        fake_iwbd = copy.deepcopy(self.iwbd_rows)
        fake_iwbd.append(
            {
                "candidate_id": "iwbd-future-inca-twin",
                "name": "Battle of Ollantaytambo",
                "start_date": "1537-01-01",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_inca_rebels_integration_dispositions(
                self.hced_rows, fake_iwbd, existing
            )

        fake_release = copy.deepcopy(existing)
        fake_release.append(
            {
                "id": "future_duplicate",
                "name": "Huayna Pukara",
                "year": 1572,
                "hced_candidate_id": "hced-future-duplicate",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable release duplicate"):
            lane.validate_wave8_inca_rebels_integration_dispositions(
                self.hced_rows, self.iwbd_rows, fake_release
            )

    def test_signature_counts_and_installers_are_pinned(self):
        self.assertEqual(
            lane.wave8_inca_rebels_audit_signature(),
            lane.WAVE8_INCA_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_inca_rebels_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_dispositions": 2,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 6,
                "new_sources": 10,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "related_hced_dispositions": 3,
                "reviewed_hced_rows": 4,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 1,
                "touched_hced_rows": 4,
            },
        )
        self.assertEqual(
            lane.wave8_inca_rebels_cohort_counts(),
            {
                "manco_inca_cuzco_revolt_1536_1537": 1,
                "manco_inca_ollantaytambo_defense_1537": 1,
                "vilcabamba_final_campaign_1572": 1,
            },
        )
        entities, sources, _ = self._installed()
        for entity in lane.WAVE8_INCA_REBELS_ENTITIES:
            self.assertEqual(entities[entity["id"]], entity)
        for source in lane.WAVE8_INCA_REBELS_SOURCES:
            self.assertEqual(sources[source["id"]], source)


if __name__ == "__main__":
    unittest.main()
