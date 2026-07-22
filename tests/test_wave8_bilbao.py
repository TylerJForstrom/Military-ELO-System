import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_bilbao as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_bilbao_"
ISABELINE = "isabeline_government_forces_first_carlist_war"
CARLIST = "carlist_army_first_war"

EXPECTED_HASHES = {
    "hced-Bilbao1835-1": (
        "be23b58ce654ee3fff6f1ba4ae945ac9e8e63d36c6d8299de0c9a0813774f76a"
    ),
    "hced-Bilbao1836-1": (
        "2092772aa3f1d7676b009c7debe4988bbba90a7c5afa7f80740371a1d97a9789"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q3310734": (
        "354ab246258dc63bd02b339e496ec81d64eff853e2a25f0557c97655fd2d6009"
    ),
    "Q3755661": (
        "0ca9b4a056bfffe11ad7bd7e846acf5e678dc1b435b0decd16c7bced52807687"
    ),
    "Q3756025": (
        "73a6867b1e9031406a7e6784ea9cc15b48fd4e5bf175e726d5a5557bd85f3395"
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


class Wave8BilbaoTests(unittest.TestCase):
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
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        source_ids = {str(source["id"]) for source in lane.WAVE8_BILBAO_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_BILBAO_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        before_entities = copy.deepcopy(entities)
        lane.install_wave8_bilbao_entities(entities)
        self.assertEqual(entities, before_entities)
        lane.install_wave8_bilbao_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_bilbao_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_christinos_inventory_and_row_hashes_are_pinned(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "christinos"
            or normalize_label(row.get("side_2_raw")) == "christinos"
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(lane.WAVE8_BILBAO_ROW_HASHES, EXPECTED_HASHES)
        by_id = {str(row["candidate_id"]): row for row in exact}
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (
                        row["side_1_raw"],
                        row["side_2_raw"],
                        row["winner_raw"],
                        row["loser_raw"],
                    ),
                    ("Christinos", "Carlists", "Christinos", "Carlists"),
                )
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_bilbao_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 2,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        integrated_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        } & lane.WAVE8_BILBAO_CONTRACT_IDS
        if not integrated_ids:
            self.assertEqual(
                lane.validate_wave8_bilbao_funnel(self.funnel),
                {
                    "events_touched": 2,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 2,
                    "zero_time_valid_candidates": 2,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_bilbao_exact_label_funnel_audit"
                ],
                lane.WAVE8_BILBAO_FUNNEL_AUDIT,
            )

    def test_contracts_pin_exact_names_dates_outcomes_and_only_two_sides(self) -> None:
        expected = {
            "hced-Bilbao1835-1": (
                "First Siege of Bilbao",
                "10 June-1 July 1835",
                "1835-06-10",
                "1835-07-01",
            ),
            "hced-Bilbao1836-1": (
                "Second Siege of Bilbao",
                "23 October-25 December 1836",
                "1836-10-23",
                "1836-12-25",
            ),
        }
        self.assertEqual(lane.WAVE8_BILBAO_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_BILBAO_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_BILBAO_HOLDS)
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_BILBAO_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["start_date"],
                    canonical["end_date"],
                ),
                values,
            )
            self.assertEqual(
                canonical["granularity"],
                "single_siege_in_the_first_carlist_war",
            )
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(contract["side_1_entity_ids"], [ISABELINE])
            self.assertEqual(contract["side_2_entity_ids"], [CARLIST])
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertNotIn("united_kingdom", contract["side_1_entity_ids"])
            self.assertNotIn("spanish_empire", contract["side_1_entity_ids"])

    def test_source_provenance_is_closed_and_independently_familied(self) -> None:
        sources = {
            str(source["id"]): source for source in lane.WAVE8_BILBAO_SOURCES
        }
        self.assertEqual(len(sources), 4)
        self.assertEqual(
            {source["url"] for source in sources.values()},
            {
                (
                    "https://dialnet.unirioja.es/descarga/articulo/"
                    "10558617.pdf"
                ),
                (
                    "https://ejercito.defensa.gob.es/museo/comun/"
                    "EL_MUSEO_DEL_EJERCITO_ES_NOTICIA/piezas/"
                    "2023.05.23_EL_ESPADON_DE_ESPARTERO"
                ),
                (
                    "https://historia-hispanica.rah.es/biografias/"
                    "45567-tomas-de-zumalacarregui-e-imaz"
                ),
                (
                    "https://www.zumalakarregimuseoa.eus/es/actividades/"
                    "investigacion-y-documentacion/historia-del-siglo-xix-"
                    "en-el-pais-vasco/batallas-y-acciones/"
                    "bilbao-vi-1835-y-x-xii-1836"
                ),
            },
        )
        for source in sources.values():
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
        for contract in lane.WAVE8_BILBAO_CONTRACTS.values():
            outcome_ids = contract["outcome_source_ids"]
            self.assertGreaterEqual(len(outcome_ids), 2)
            self.assertEqual(contract["evidence_refs"], outcome_ids)
            self.assertEqual(contract["date_source_ids"], outcome_ids)
            self.assertEqual(set(contract["event_evidence_roles"]), set(outcome_ids))
            self.assertEqual(
                len(contract["outcome_source_family_ids"]),
                len(outcome_ids),
            )
            self.assertTrue(set(outcome_ids) <= set(sources))

    def test_existing_conflict_bounded_identities_are_reused_without_alias(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        for entity_id in (ISABELINE, CARLIST):
            entity = entities[entity_id]
            self.assertLessEqual(entity["start_year"], 1835)
            self.assertGreaterEqual(entity["end_year"], 1836)
            self.assertEqual(entity["aliases"], [])
            Entity.from_dict(entity)
        self.assertFalse(lane.WAVE8_BILBAO_ENTITIES)
        self.assertNotIn(
            "christinos",
            {
                normalize_label(alias)
                for entity_id in (ISABELINE, CARLIST)
                for alias in entities[entity_id]["aliases"]
            },
        )

    def test_emitted_events_are_isabeline_wins_without_foreign_participants(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_HASHES))
        for candidate_id, event in events.items():
            contract = lane.WAVE8_BILBAO_CONTRACTS[candidate_id]
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                outcomes,
                {
                    ISABELINE: "engagement_victory",
                    CARLIST: "engagement_defeat",
                },
            )
            self.assertEqual(len(event["participants"]), 2)
            self.assertNotIn(
                "united_kingdom",
                {participant["entity_id"] for participant in event["participants"]},
            )
            self.assertEqual(event["name"], contract["canonical_event"]["name"])
            self.assertEqual(event["aliases"], ["Bilbao"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["scale"], "battle")
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(
                event["reviewed_granularity"],
                "single_siege_in_the_first_carlist_war",
            )
            self.assertEqual(event["confidence"], 0.95)
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            Event.from_dict(event)

    def test_source_point_country_and_location_provenance_are_retained(self) -> None:
        self.assertFalse(lane.WAVE8_BILBAO_POINT_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_BILBAO_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_BILBAO_LOCATION_QUARANTINE_REASONS)
        for event in self._events():
            self.assertEqual(
                event["geometry"],
                {"type": "Point", "coordinates": [-2.9349852, 43.2630126]},
            )
            self.assertEqual(event["modern_location_country"], "Spain")
            self.assertIn("location_provenance", event)

    def test_wikidata_twins_and_luchana_are_discovery_only_unknowns(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        self.assertEqual(
            lane.WAVE8_BILBAO_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            self.assertEqual(_full_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertIs(by_id[candidate_id]["do_not_rate_automatically"], True)
            self.assertEqual(by_id[candidate_id]["winners"], [])
            self.assertEqual(
                lane.WAVE8_BILBAO_DISCOVERY_EXPECTED[candidate_id][
                    "outcome_disposition"
                ],
                "unknown_never_draw",
            )
        self.assertEqual(
            lane.validate_wave8_bilbao_discovery_dispositions(self.wikidata_rows),
            {
                "discovery_nonrating_records": 3,
                "discovery_promotions": 0,
                "nested_constituents": 1,
                "unknown_never_draw_rows": 3,
            },
        )
        self.assertEqual(
            lane.WAVE8_BILBAO_DISCOVERY_NESTED,
            {"Q3310734": "hced-Bilbao1836-1"},
        )
        self.assertIn(
            "Auxiliary Legion",
            lane.WAVE8_BILBAO_DISCOVERY_EXPECTED["Q3756025"][
                "participant_labels"
            ],
        )
        self.assertNotIn(
            "united_kingdom",
            {
                participant["entity_id"]
                for event in self._events()
                for participant in event["participants"]
            },
        )

    def test_cross_source_twin_inventory_and_artifact_state_are_fail_closed(self) -> None:
        owned_count = sum(
            event.get("hced_candidate_id") in lane.WAVE8_BILBAO_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_bilbao_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "discovery_nonrating_dispositions": 3,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        artifact = lane.validate_wave8_bilbao_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        self.assertEqual(artifact["promoted_events"], owned_count)
        self.assertEqual(
            artifact["artifact_state"],
            "integrated" if owned_count else "absent",
        )

    def test_queue_row_drift_extra_label_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Bilbao1835-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_bilbao_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-Bilbao1835-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_bilbao_queue_contracts(duplicated)

        future_label = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-christinos",
                "side_1_raw": "Christinos",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_bilbao_queue_contracts(future_label)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_bilbao_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_bilbao_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_missing_identity_source_collision_and_partial_artifact_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(ISABELINE)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_bilbao_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        colliding_sources = {str(key): copy.deepcopy(value) for key, value in sources.items()}
        source_id = str(lane.WAVE8_BILBAO_SOURCES[0]["id"])
        colliding_sources[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_bilbao_sources(colliding_sources)

        events = self._events()
        with self.assertRaisesRegex(ValueError, "event inventory is partial"):
            lane.validate_wave8_bilbao_current_artifact_state(
                events[:1],
                self.release_entities,
                list(sources.values()),
            )

    def test_future_iwd_iwbd_and_release_twins_fail_closed(self) -> None:
        future_iwd = [
            *copy.deepcopy(self.iwd_rows),
            {
                "candidate_id": "iwd-future-bilbao",
                "name": "First Siege of Bilbao",
                "year": 1835,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_bilbao_integration_dispositions(
                self.hced_rows,
                future_iwd,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-bilbao",
                "name": "Siege of Bilbao",
                "start_date": "1836-11-09",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_bilbao_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_luchana_twin",
                "name": "Battle of Luchana",
                "year": 1836,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_bilbao_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_counts_metadata_signature_and_installers_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_bilbao_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 3,
                "holds": 0,
                "integration_dispositions": 3,
                "new_entities": 0,
                "new_sources": 4,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 3,
            },
        )
        self.assertEqual(
            lane.wave8_bilbao_cohort_counts(),
            {"first_carlist_war_bilbao_sieges_1835_1836": 2},
        )
        self.assertEqual(
            lane.wave8_bilbao_audit_signature(),
            lane.WAVE8_BILBAO_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_bilbao_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_bilbao_counts())
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(EXPECTED_HASHES),
        )
        self.assertEqual(len(metadata["discovery_dispositions"]), 3)


if __name__ == "__main__":
    unittest.main()
