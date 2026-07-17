import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_zulu_forces as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_zulu_forces_"

USUTHU = "usuthu_dinuzulu_rebellion_force_1888"
MANDLAKAZI = "mandlakazi_zibhebhu_force_ivuna_1888"
BRITISH_ZULULAND = "british_zululand_hlophekhulu_force_1888"
NATAL_COLONIAL = "natal_led_bambatha_suppression_force_1906"
BAMBATHA_INSURGENTS = "bambatha_sigananda_insurgent_coalition_1906"

EXPECTED_HASHES = {
    "hced-Bobe1906-1": (
        "dbe7b2a6abed9451af55f4d47e00dfca62b79419234ad7fde19c7d3e1f9f0db1"
    ),
    "hced-Hlophekhulu1888-1": (
        "18e84445a5a96a2c9d4a6719503a2c84edca9f8effaa3a449edcf421d14261c6"
    ),
    "hced-Ivuna1888-1": (
        "082e506dc869dbd1468e29584928317218e4adcd4b52674992fe486422c15b50"
    ),
    "hced-Mome1906-1": (
        "b123f46e10af8cb741e47e62b660d5bf5069c285453f20581e55b68457e9916b"
    ),
    "hced-Mpukonyoni1906-1": (
        "eb6e1eb8ec31367dbd434f875011418261b026391f7218dafec18303022cfaa5"
    ),
}

EXPECTED_EVENTS = {
    "hced-Hlophekhulu1888-1": {
        "name": "Battle of Hlophekhulu",
        "confidence": 0.92,
        "winner": {BRITISH_ZULULAND},
        "loser": {USUTHU},
    },
    "hced-Ivuna1888-1": {
        "name": "Battle of Ivuna (Ndunu Hill)",
        "confidence": 0.94,
        "winner": {USUTHU},
        "loser": {MANDLAKAZI},
    },
    "hced-Bobe1906-1": {
        "name": "Battle of Bobe Ridge",
        "confidence": 0.90,
        "winner": {NATAL_COLONIAL},
        "loser": {BAMBATHA_INSURGENTS},
    },
    "hced-Mpukonyoni1906-1": {
        "name": "Battle of Mpukunyoni",
        "confidence": 0.92,
        "winner": {NATAL_COLONIAL},
        "loser": {BAMBATHA_INSURGENTS},
    },
    "hced-Mome1906-1": {
        "name": "Battle of Mome Gorge",
        "confidence": 0.96,
        "winner": {NATAL_COLONIAL},
        "loser": {BAMBATHA_INSURGENTS},
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8ZuluForcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "zulu rebels"
            or normalize_label(row.get("side_2_raw")) == "zulu rebels"
        ]

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_ZULU_FORCES_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_ZULU_FORCES_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ZULU_FORCES_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_zulu_forces_entities(entities)
        lane.install_wave8_zulu_forces_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_zulu_forces_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_row_fingerprints_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_ZULU_FORCES_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(row["modern_location_country"], "South Africa")

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_zulu_forces_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 5,
                "holds": 0,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 5,
            },
        )
        self.assertEqual(
            lane.validate_wave8_zulu_forces_funnel(self.funnel),
            {
                "events_touched": 5,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 5,
            },
        )

    def test_all_rows_promote_and_unknown_is_not_manufactured(self) -> None:
        self.assertEqual(set(lane.WAVE8_ZULU_FORCES_CONTRACTS), set(EXPECTED_EVENTS))
        self.assertFalse(lane.WAVE8_ZULU_FORCES_HOLDS)
        for contract in lane.WAVE8_ZULU_FORCES_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_entities_are_conflict_bounded_and_open_no_generic_alias(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_ZULU_FORCES_ENTITIES}
        self.assertEqual(
            set(entities),
            {
                USUTHU,
                MANDLAKAZI,
                BRITISH_ZULULAND,
                NATAL_COLONIAL,
                BAMBATHA_INSURGENTS,
            },
        )
        self.assertTrue(all(not item["aliases"] for item in entities.values()))
        for entity_id in {USUTHU, MANDLAKAZI, BRITISH_ZULULAND}:
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (1888, 1888),
            )
        for entity_id in {NATAL_COLONIAL, BAMBATHA_INSURGENTS}:
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (1906, 1906),
            )
        self.assertIn("not the pre-1879 Zulu Kingdom", entities[USUTHU]["continuity_note"])
        self.assertIn("does not claim every component", entities[NATAL_COLONIAL]["continuity_note"])
        self.assertIn("does not represent all Zulu people", entities[BAMBATHA_INSURGENTS]["continuity_note"])

    def test_sources_and_models_are_parseable_with_independent_outcome_families(self) -> None:
        for source in lane.WAVE8_ZULU_FORCES_SOURCES:
            Source.from_dict(source)
        for entity in lane.WAVE8_ZULU_FORCES_ENTITIES:
            Entity.from_dict(entity)
        for candidate_id, contract in lane.WAVE8_ZULU_FORCES_CONTRACTS.items():
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

    def test_promoted_events_have_exact_actors_and_tactical_results(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["confidence"], expected["confidence"])
                self.assertEqual(event["date_precision"], "day")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                winners = {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_victory"
                }
                losers = {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_defeat"
                }
                self.assertEqual(winners, expected["winner"])
                self.assertEqual(losers, expected["loser"])
                Event.from_dict(event)

    def test_ivuna_excludes_the_bypassed_british_garrison(self) -> None:
        ivuna = lane.WAVE8_ZULU_FORCES_CONTRACTS["hced-Ivuna1888-1"]
        self.assertEqual(ivuna["side_1_entity_ids"], [USUTHU])
        self.assertEqual(ivuna["side_2_entity_ids"], [MANDLAKAZI])
        self.assertNotIn(BRITISH_ZULULAND, ivuna["side_2_entity_ids"])
        self.assertIn("deliberately bypassed", ivuna["audit_note"])

    def test_1906_rows_share_campaign_sides_without_modern_south_africa(self) -> None:
        for candidate_id in (
            "hced-Bobe1906-1",
            "hced-Mome1906-1",
            "hced-Mpukonyoni1906-1",
        ):
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_ZULU_FORCES_CONTRACTS[candidate_id]
                self.assertEqual(contract["side_1_entity_ids"], [NATAL_COLONIAL])
                self.assertEqual(contract["side_2_entity_ids"], [BAMBATHA_INSURGENTS])
                self.assertNotIn("south_africa", {*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]})

    def test_mpukonyoni_date_uses_the_correlated_28_may_record(self) -> None:
        contract = lane.WAVE8_ZULU_FORCES_CONTRACTS["hced-Mpukonyoni1906-1"]
        self.assertEqual(contract["canonical_event"]["date_text"], "28 May 1906")
        self.assertIn("25 May typo", contract["audit_note"])
        self.assertNotIn("wave8_zulu_coghlan_harte", contract["outcome_source_ids"])

    def test_points_are_withheld_but_country_is_retained(self) -> None:
        events = self._events()
        self.assertEqual(
            lane.WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ZULU_FORCES_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS)
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "South Africa")
            self.assertIn("location_provenance", event)

    def test_queue_tampering_duplicate_rows_and_massacre_drift_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        target = next(row for row in tampered if row.get("candidate_id") == "hced-Mome1906-1")
        target["winner_raw"] = "Zulu Rebels"
        with self.assertRaises(ValueError):
            lane.validate_wave8_zulu_forces_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(row for row in duplicated if row.get("candidate_id") == "hced-Ivuna1888-1")
            )
        )
        with self.assertRaises(ValueError):
            lane.validate_wave8_zulu_forces_queue_contracts(duplicated)

        massacre = copy.deepcopy(self.hced_rows)
        target = next(row for row in massacre if row.get("candidate_id") == "hced-Bobe1906-1")
        target["massacre_raw"] = "Massacre"
        with self.assertRaises(ValueError):
            lane.validate_wave8_zulu_forces_queue_contracts(massacre)

    def test_duplicate_audit_is_zero_and_future_spelling_twins_fail_closed(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_zulu_forces_integration_dispositions(
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
        future = [
            *copy.deepcopy(self.iwbd_rows),
            {"candidate_id": "iwbd-future", "batname": "Mhome Gorge", "batyear": 1906},
        ]
        with self.assertRaises(ValueError):
            lane.validate_wave8_zulu_forces_integration_dispositions(
                self.hced_rows,
                future,
                existing,
            )

    def test_installers_and_existing_candidate_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        lane.install_wave8_zulu_forces_entities(entities)
        lane.install_wave8_zulu_forces_sources(sources)
        events = lane.promote_wave8_zulu_forces_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaises(ValueError):
            lane.promote_wave8_zulu_forces_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_counts_cohorts_and_final_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_zulu_forces_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 5,
                "new_sources": 11,
                "newly_rated_events": 5,
                "outcome_overrides": 0,
                "point_quarantine_additions": 5,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_zulu_forces_cohort_counts(),
            {"bambatha_rebellion_1906": 3, "usuthu_rebellion_1888": 2},
        )
        self.assertEqual(
            lane.wave8_zulu_forces_audit_signature(),
            lane.WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
