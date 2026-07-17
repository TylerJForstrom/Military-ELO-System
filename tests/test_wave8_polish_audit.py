import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_polish_audit import (
    WAVE8_POLISH_AUDIT_CONTRACT_IDS,
    WAVE8_POLISH_AUDIT_CONTRACTS,
    WAVE8_POLISH_AUDIT_CORRECTION_COUNT,
    WAVE8_POLISH_AUDIT_CORRECTION_IDS,
    WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE,
    WAVE8_POLISH_AUDIT_CORRECTIONS,
    WAVE8_POLISH_AUDIT_ENTITIES,
    WAVE8_POLISH_AUDIT_FINAL_AUDIT_SIGNATURE,
    WAVE8_POLISH_AUDIT_HOLD_IDS,
    WAVE8_POLISH_AUDIT_HOLDS,
    WAVE8_POLISH_AUDIT_RESERVED_IDS,
    WAVE8_POLISH_AUDIT_SOURCES,
    apply_wave8_polish_audit_corrections,
    install_wave8_polish_audit_entities,
    install_wave8_polish_audit_sources,
    promote_wave8_polish_audit_contracts,
    validate_wave8_polish_audit_correction_inputs,
    validate_wave8_polish_audit_queue_contracts,
    wave8_polish_audit_correction_signature,
    wave8_polish_audit_counts,
    wave8_polish_audit_signature,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _pre_polish_audit_events(events):
    """Reconstruct the pinned pre-migration fixture from either artifact state."""

    materialized = copy.deepcopy(events)
    materialized = [
        event
        for event in materialized
        if event.get("hced_candidate_id") not in WAVE8_POLISH_AUDIT_CONTRACT_IDS
    ]
    by_candidate = {
        event.get("hced_candidate_id"): event
        for event in materialized
        if event.get("hced_candidate_id") in WAVE8_POLISH_AUDIT_CORRECTION_IDS
    }
    for candidate_id, correction in WAVE8_POLISH_AUDIT_CORRECTIONS.items():
        event = by_candidate[candidate_id]
        if not event.get("wave8_polish_audit_correction"):
            continue
        template = copy.deepcopy(event["participants"][0])
        participants = []
        for entity_id, side, termination, result_class in correction[
            "expected_orientation"
        ]:
            participant = copy.deepcopy(template)
            participant.update(
                {
                    "entity_id": entity_id,
                    "side": side,
                    "termination": termination,
                    "result_class": result_class,
                }
            )
            participants.append(participant)
        event["participants"] = participants
        event["outcome_source_ids"] = ["hced_dataset"]
        event["outcome_source_family_ids"] = ["hced"]
        event.pop("wave8_polish_audit_correction", None)
        event.pop("historical_outcome_correction", None)
    return materialized


class Wave8PolishAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.pre_audit_events = _pre_polish_audit_events(cls.release_events)
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def test_inventory_counts_signatures_and_reserved_ids_are_exact(self) -> None:
        self.assertEqual(len(WAVE8_POLISH_AUDIT_CONTRACT_IDS), 1)
        self.assertEqual(len(WAVE8_POLISH_AUDIT_HOLD_IDS), 4)
        self.assertEqual(WAVE8_POLISH_AUDIT_CORRECTION_COUNT, 4)
        self.assertEqual(len(WAVE8_POLISH_AUDIT_CORRECTION_IDS), 4)
        self.assertEqual(
            WAVE8_POLISH_AUDIT_RESERVED_IDS,
            WAVE8_POLISH_AUDIT_CONTRACT_IDS | WAVE8_POLISH_AUDIT_HOLD_IDS,
        )
        self.assertEqual(
            wave8_polish_audit_correction_signature(),
            WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE,
        )
        self.assertEqual(
            wave8_polish_audit_signature(),
            WAVE8_POLISH_AUDIT_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_polish_audit_counts(),
            {
                "correction_targets": 4,
                "holds": 4,
                "newly_rated_events": 1,
                "promotion_contracts": 1,
                "reviewed_hced_rows": 9,
            },
        )

    def test_entities_sources_hashes_and_queue_inventory_validate(self) -> None:
        self.assertEqual((len(WAVE8_POLISH_AUDIT_ENTITIES), len(WAVE8_POLISH_AUDIT_SOURCES)), (1, 7))
        for entity in WAVE8_POLISH_AUDIT_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
        for source in WAVE8_POLISH_AUDIT_SOURCES:
            Source.from_dict(source)

        indexed = {row["candidate_id"]: row for row in self.rows}
        for inventory in (WAVE8_POLISH_AUDIT_CONTRACTS, WAVE8_POLISH_AUDIT_HOLDS):
            for candidate_id, contract in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    contract["raw_row_sha256"],
                )
        self.assertEqual(
            validate_wave8_polish_audit_queue_contracts(self.rows),
            {
                "promotion_contracts": 1,
                "holds": 4,
                "reviewed_hced_rows": 5,
            },
        )

        sources = {source["id"]: source for source in self.release_sources}
        install_wave8_polish_audit_sources(sources)
        for fixture in WAVE8_POLISH_AUDIT_SOURCES:
            self.assertEqual(sources[fixture["id"]], fixture)

    def test_hash_bound_holds_include_duplicate_nonbattle_and_identity_gates(self) -> None:
        duplicate = WAVE8_POLISH_AUDIT_HOLDS["hced-Brest-Litovsk1794-1"]
        self.assertEqual(duplicate["hold_category"], "duplicate_of_reviewed_event")
        self.assertEqual(
            duplicate["duplicate_of_candidate_id"], "hced-Terespol1794-1"
        )
        self.assertEqual(
            WAVE8_POLISH_AUDIT_HOLDS["hced-Janowiec1606-1"]["hold_category"],
            "agreement_not_battle",
        )
        for candidate_id in ("hced-Domazlice1431-1", "hced-Grotniki1439-1"):
            self.assertEqual(
                WAVE8_POLISH_AUDIT_HOLDS[candidate_id]["hold_category"],
                "exact_belligerent_identities_unresolved",
            )

        changed = copy.deepcopy(self.rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Brest-Litovsk1794-1"
        )["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_polish_audit_queue_contracts(changed)

    def test_guzow_promotes_with_exact_event_bounded_sides_and_direct_source(self) -> None:
        entities = {entity["id"]: entity for entity in self.release_entities}
        install_wave8_polish_audit_entities(entities)
        events = promote_wave8_polish_audit_contracts(
            self.rows,
            entities,
            self.pre_audit_events,
        )
        self.assertEqual(len(events), 1)
        event = events[0]
        Event.from_dict(event)
        self.assertEqual(event["hced_candidate_id"], "hced-Guzow1607-1")
        self.assertEqual(event["name"], "Battle of Guzów")
        self.assertEqual(event["war_type"], "civil_war")
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            },
            {"polish_lithuanian_commonwealth"},
        )
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_defeat"
            },
            {"guzow_rokosz_forces_1607"},
        )
        self.assertEqual(
            event["outcome_source_ids"],
            ["wave8_polish_zpe_rokosz_1606_1607"],
        )
        self.assertEqual(event["outcome_source_family_ids"], ["polish_zpe_history"])

    def test_four_corrections_preserve_event_ids_count_and_apply_exact_results(self) -> None:
        before_ids = [event["id"] for event in self.pre_audit_events]
        corrected = apply_wave8_polish_audit_corrections(self.pre_audit_events)
        self.assertEqual(len(corrected), len(self.pre_audit_events))
        self.assertEqual([event["id"] for event in corrected], before_ids)
        self.assertEqual(
            sum(bool(event.get("wave8_polish_audit_correction")) for event in corrected),
            4,
        )
        by_candidate = {
            event.get("hced_candidate_id"): event
            for event in corrected
            if event.get("hced_candidate_id") in WAVE8_POLISH_AUDIT_CORRECTION_IDS
        }
        self.assertEqual(set(by_candidate), WAVE8_POLISH_AUDIT_CORRECTION_IDS)

        def terminations(candidate_id: str, termination: str) -> set[str]:
            return {
                participant["entity_id"]
                for participant in by_candidate[candidate_id]["participants"]
                if participant["termination"] == termination
            }

        self.assertEqual(
            terminations("hced-Cracow1772-1", "engagement_victory"),
            {"russian_empire"},
        )
        self.assertEqual(
            terminations("hced-Cracow1772-1", "engagement_defeat"),
            {"kingdom_france", "bar_confederation_forces"},
        )
        self.assertEqual(
            terminations("hced-Bydgoszcz1794-1", "engagement_defeat"),
            {"kingdom_prussia"},
        )
        self.assertEqual(
            terminations("hced-Szczekociny1794-1", "engagement_victory"),
            {"kingdom_prussia", "russian_empire"},
        )
        grochow = by_candidate["hced-Grochow1831-1"]
        self.assertEqual(grochow["decisiveness"], 0.32)
        self.assertEqual(
            {participant["termination"] for participant in grochow["participants"]},
            {"inconclusive_engagement"},
        )
        self.assertEqual(
            {participant["result_class"] for participant in grochow["participants"]},
            {"stalemate_or_inconclusive"},
        )

        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_POLISH_AUDIT_CORRECTIONS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertTrue(set(event["outcome_source_ids"]) <= set(event["source_ids"]))
            self.assertTrue(event["historical_outcome_correction"])
            self.assertEqual(
                event["identity_resolution"],
                "candidate_keyed_exact_wave8_correction",
            )
            self.assertEqual(
                event["wave8_polish_audit_correction"]["correction_signature"],
                WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE,
            )

    def test_correction_preconditions_fail_closed_before_any_change(self) -> None:
        changed = copy.deepcopy(self.pre_audit_events)
        target = next(
            event
            for event in changed
            if event.get("hced_candidate_id") == "hced-Bydgoszcz1794-1"
        )
        target["participants"][1]["entity_id"] = "kingdom_prussia"
        with self.assertRaisesRegex(ValueError, "participant orientation changed"):
            validate_wave8_polish_audit_correction_inputs(changed)
        with self.assertRaisesRegex(ValueError, "participant orientation changed"):
            apply_wave8_polish_audit_corrections(changed)

        missing = [
            event
            for event in self.pre_audit_events
            if event.get("hced_candidate_id") != "hced-Grochow1831-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one published event"):
            validate_wave8_polish_audit_correction_inputs(missing)

    def test_no_generic_polish_rebels_identity_is_created_or_used(self) -> None:
        all_entity_ids = {
            str(entity["id"]) for entity in WAVE8_POLISH_AUDIT_ENTITIES
        }
        for contract in WAVE8_POLISH_AUDIT_CONTRACTS.values():
            all_entity_ids.update(map(str, contract["side_1_entity_ids"]))
            all_entity_ids.update(map(str, contract["side_2_entity_ids"]))
        for correction in WAVE8_POLISH_AUDIT_CORRECTIONS.values():
            all_entity_ids.update(map(str, correction["side_a_entity_ids"]))
            all_entity_ids.update(map(str, correction["side_b_entity_ids"]))
        self.assertNotIn("polish_rebels", all_entity_ids)
        self.assertFalse(any(entity_id.endswith("polish_rebels") for entity_id in all_entity_ids))


if __name__ == "__main__":
    unittest.main()
