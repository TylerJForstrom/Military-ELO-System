import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_haiti_regimes as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_haiti_regimes_"

FIRST_EMPIRE = "first_empire_haiti_1804_1806"
REPUBLIC = "republic_haiti_reunified_1820_1849"
SECOND_EMPIRE = "second_empire_haiti_1849_1859"
DOMINICAN_FIRST_REPUBLIC = "first_dominican_republic_1844_1861"
SANTO_DOMINGO_DEFENSE = "ferrand_santo_domingo_defense_1805"

EXPECTED_HASHES = {
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
    "hced-Santo Domingo1805-1": (
        "100b9326b4d08e44f7e10a2bc51ab70346637df2d57ffa692e551cf4033f36fe"
    ),
}

EXPECTED_EVENTS = {
    "hced-Santo Domingo1805-1": {
        "name": "Siege of Santo Domingo (1805)",
        "date_precision": "day_range",
        "confidence": 0.88,
        "winner": {SANTO_DOMINGO_DEFENSE},
        "loser": {FIRST_EMPIRE},
    },
    "hced-Azua1844-1": {
        "name": "Battle of Azua (19 March 1844)",
        "date_precision": "day",
        "confidence": 0.88,
        "winner": {DOMINICAN_FIRST_REPUBLIC},
        "loser": {REPUBLIC},
    },
    "hced-El Numero1849-1": {
        "name": "Battle of El Numero",
        "date_precision": "day",
        "confidence": 0.92,
        "winner": {DOMINICAN_FIRST_REPUBLIC},
        "loser": {REPUBLIC},
    },
    "hced-Sabana Larga1856-1": {
        "name": "Battle of Sabana Larga",
        "date_precision": "day",
        "confidence": 0.94,
        "winner": {DOMINICAN_FIRST_REPUBLIC},
        "loser": {SECOND_EMPIRE},
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


class Wave8HaitiRegimesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "haiti"
            or normalize_label(row.get("side_2_raw")) == "haiti"
        ]

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_HAITI_REGIMES_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_HAITI_REGIMES_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_haiti_regimes_entities(entities)
        lane.install_wave8_haiti_regimes_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_haiti_regimes_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_row_fingerprints_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_HAITI_REGIMES_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(by_id[candidate_id]), expected_hash)
                self.assertIs(by_id[candidate_id]["winner_loser_complete"], True)
                self.assertEqual(
                    by_id[candidate_id]["modern_location_country"],
                    "Dominican Republic",
                )

    def test_queue_and_funnel_accounting_is_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_haiti_regimes_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 5,
                "holds": 1,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
            },
        )
        self.assertEqual(
            lane.WAVE8_HAITI_REGIMES_FUNNEL_AUDIT,
            {
                "event_candidate_id_sha256": (
                    "d335346c74accdde228bcbb518484d8edb67019c67eb69a90c7f2720d1253baf"
                ),
                "events_touched": 5,
                "label": "haiti",
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 5,
            },
        )
        self.assertFalse(
            any(row.get("label") == "haiti" for row in self.funnel.get("labels", [])),
            "the completed Haiti lane must not remain in the live unresolved funnel",
        )

    def test_dispositions_are_four_promotions_and_one_unknown_hold(self) -> None:
        self.assertEqual(set(lane.WAVE8_HAITI_REGIMES_CONTRACTS), set(EXPECTED_EVENTS))
        self.assertEqual(
            lane.WAVE8_HAITI_REGIMES_HOLD_IDS,
            frozenset({"hced-Cabeza de las Marias and las Hicoteas1844-1"}),
        )
        hold = next(iter(lane.WAVE8_HAITI_REGIMES_HOLDS.values()))
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertIn("multiple", hold["canonical_event"]["granularity"])
        self.assertIn("not a draw", hold["hold_reason"].casefold())
        for forbidden in ("winner_side", "side_1_entity_ids", "side_2_entity_ids"):
            self.assertNotIn(forbidden, hold)

    def test_entities_close_generic_aliases_and_pin_regime_boundaries(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_HAITI_REGIMES_ENTITIES}
        self.assertEqual(
            set(entities),
            {
                FIRST_EMPIRE,
                REPUBLIC,
                SECOND_EMPIRE,
                DOMINICAN_FIRST_REPUBLIC,
                SANTO_DOMINGO_DEFENSE,
            },
        )
        self.assertTrue(all(not item["aliases"] for item in entities.values()))
        self.assertEqual(
            (entities[FIRST_EMPIRE]["start_year"], entities[FIRST_EMPIRE]["end_year"]),
            (1804, 1806),
        )
        self.assertEqual(
            (entities[REPUBLIC]["start_year"], entities[REPUBLIC]["end_year"]),
            (1820, 1849),
        )
        self.assertEqual(
            (entities[SECOND_EMPIRE]["start_year"], entities[SECOND_EMPIRE]["end_year"]),
            (1849, 1859),
        )
        self.assertEqual(
            (
                entities[DOMINICAN_FIRST_REPUBLIC]["start_year"],
                entities[DOMINICAN_FIRST_REPUBLIC]["end_year"],
            ),
            (1844, 1861),
        )
        self.assertIn("26 August", entities[REPUBLIC]["continuity_note"])
        self.assertIn("mechanical", entities[SECOND_EMPIRE]["continuity_note"])

    def test_el_numero_uses_republic_before_exact_1849_empire_boundary(self) -> None:
        contract = lane.WAVE8_HAITI_REGIMES_CONTRACTS["hced-El Numero1849-1"]
        self.assertEqual(contract["canonical_event"]["date_text"], "17 April 1849")
        self.assertEqual(contract["side_2_entity_ids"], [REPUBLIC])
        self.assertNotIn(SECOND_EMPIRE, contract["side_2_entity_ids"])
        sabana = lane.WAVE8_HAITI_REGIMES_CONTRACTS["hced-Sabana Larga1856-1"]
        self.assertEqual(sabana["side_2_entity_ids"], [SECOND_EMPIRE])

    def test_sources_have_canonical_roles_and_independent_outcome_families(self) -> None:
        for source in lane.WAVE8_HAITI_REGIMES_SOURCES:
            Source.from_dict(source)
        for entity in lane.WAVE8_HAITI_REGIMES_ENTITIES:
            Entity.from_dict(entity)
        for candidate_id, contract in lane.WAVE8_HAITI_REGIMES_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )

    def test_promoted_events_have_expected_exact_actors_and_tactical_results(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["date_precision"], expected["date_precision"])
                self.assertEqual(event["confidence"], expected["confidence"])
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

    def test_promoted_points_are_withheld_but_country_is_retained(self) -> None:
        events = self._events()
        self.assertEqual(
            lane.WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS)
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Dominican Republic")
            self.assertIn("location_provenance", event)

    def test_current_release_artifacts_include_the_lane_exactly_once(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS
        ]
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS,
        )
        self.assertEqual(len(events), len(lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS))
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in events)
        )
        self.assertFalse(
            lane.WAVE8_HAITI_REGIMES_HOLD_IDS
            & {str(event.get("hced_candidate_id")) for event in self.release_events}
        )
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Dominican Republic")
            Event.from_dict(event)

        entity_ids = {str(item["id"]) for item in lane.WAVE8_HAITI_REGIMES_ENTITIES}
        release_entities = {str(item["id"]): item for item in self.release_entities}
        self.assertLessEqual(entity_ids, set(release_entities))
        self.assertTrue(all(not release_entities[entity_id]["aliases"] for entity_id in entity_ids))

        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        self.assertLessEqual(entity_ids, set(registry_entities))
        self.assertTrue(
            all(registry_entities[entity_id]["status"] == "rated" for entity_id in entity_ids)
        )

        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_haiti_regimes_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_haiti_regimes_candidate_ids"],
            sorted(lane.WAVE8_HAITI_REGIMES_CONTRACT_IDS),
        )
        self.assertEqual(
            [item["candidate_id"] for item in promotion["wave8_haiti_regimes_holds"]],
            sorted(lane.WAVE8_HAITI_REGIMES_HOLD_IDS),
        )
        self.assertEqual(
            promotion["wave8_haiti_regimes_final_audit_signature"],
            lane.WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE,
        )

        coverage = self.registry["coverage"]
        self.assertEqual(coverage["candidate_keyed_wave8_haiti_regimes_hced_events"], 4)
        self.assertEqual(coverage["rated_events"], len(self.release_events))
        self.assertEqual(coverage["registry_polities"], len(self.registry["entities"]))
        self.assertEqual(
            coverage["rated_entities"],
            len(
                {
                    participant["entity_id"]
                    for event in self.release_events
                    for participant in event["participants"]
                }
            ),
        )

    def test_queue_tampering_and_duplicate_rows_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        target = next(row for row in tampered if row.get("candidate_id") == "hced-El Numero1849-1")
        target["winner_raw"] = "Haiti"
        with self.assertRaises(ValueError):
            lane.validate_wave8_haiti_regimes_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(copy.deepcopy(next(row for row in duplicated if row.get("candidate_id") == "hced-Azua1844-1")))
        with self.assertRaises(ValueError):
            lane.validate_wave8_haiti_regimes_queue_contracts(duplicated)

    def test_duplicate_audit_is_zero_and_rejects_a_future_iwbd_twin(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_haiti_regimes_integration_dispositions(
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
        future = [*copy.deepcopy(self.iwbd_rows), {"candidate_id": "iwbd-future", "batname": "Azua", "batyear": 1844}]
        with self.assertRaises(ValueError):
            lane.validate_wave8_haiti_regimes_integration_dispositions(
                self.hced_rows,
                future,
                existing,
            )

    def test_installers_and_existing_candidate_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        lane.install_wave8_haiti_regimes_entities(entities)
        lane.install_wave8_haiti_regimes_sources(sources)
        events = lane.promote_wave8_haiti_regimes_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaises(ValueError):
            lane.promote_wave8_haiti_regimes_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_counts_and_final_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_haiti_regimes_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 1,
                "new_entities": 5,
                "new_sources": 12,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_haiti_regimes_cohort_counts(),
            {
                "first_empire_haiti": 1,
                "republic_haiti_dominican_first_republic": 3,
                "second_empire_haiti_dominican_first_republic": 1,
            },
        )
        self.assertEqual(
            lane.wave8_haiti_regimes_audit_signature(),
            lane.WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
