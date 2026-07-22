import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_cuban as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_cuban_"
REPUBLIC = "clio_cu_cuba_rep_1_1905_9c789e65"
JULY_26 = "cuban_26_july_movement"
MONCADA_GROUP = "moncada_assault_group_1953"
CIENFUEGOS_COALITION = "cienfuegos_naval_civilian_uprising_coalition_1957"

EXPECTED_HASHES = {
    "hced-Cienfuegos1957-1": (
        "4a8b96f2c126c62f26d8f664c08de4d77084f335481c856cae212b530c029747"
    ),
    "hced-Moncada1953-1": (
        "0cb81e3b5335b537b0b031141969aaaf087546ce143fc2c3f5ae17cea5ec02e1"
    ),
    "hced-Sierra Maestra1958-1": (
        "300074a1319c5f29274449bbbf77e52e9d187e052b90d270a229e75c5dab78aa"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q11211553": (
        "29556145498096bc7e0694bf64a557a8f5af155aef1f466a8fd951602e7965f8"
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


class Wave8CubanTests(unittest.TestCase):
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
        source_ids = {str(source["id"]) for source in lane.WAVE8_CUBAN_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_CUBAN_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_cuban_entities(entities)
        lane.install_wave8_cuban_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_cuban_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_cuban_government_inventory_and_row_hashes_are_pinned(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "cuban government"
            or normalize_label(row.get("side_2_raw")) == "cuban government"
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(lane.WAVE8_CUBAN_ROW_HASHES, EXPECTED_HASHES)
        by_id = {str(row["candidate_id"]): row for row in exact}
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertNotIn(
                    normalize_label(row["winner_raw"]),
                    {"draw", "inconclusive", "stalemate", "unknown"},
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_cuban_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 3,
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
            },
        )
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        if "cuban government" in labels:
            self.assertEqual(
                lane.validate_wave8_cuban_funnel(self.funnel),
                {
                    "events_touched": 3,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 3,
                    "zero_time_valid_candidates": 3,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_cuban_exact_label_funnel_audit"
                ],
                lane.WAVE8_CUBAN_FUNNEL_AUDIT,
            )

    def test_contracts_pin_exact_dates_sides_and_republic_wins(self) -> None:
        expected = {
            "hced-Moncada1953-1": (
                "Attack on the Moncada Barracks",
                "26 July 1953",
                "1953-07-26",
                "1953-07-26",
                "single_barracks_assault",
                MONCADA_GROUP,
            ),
            "hced-Cienfuegos1957-1": (
                "Cienfuegos uprising",
                "5-6 September 1957",
                "1957-09-05",
                "1957-09-06",
                "single_naval_civilian_urban_uprising",
                CIENFUEGOS_COALITION,
            ),
        }
        self.assertEqual(
            lane.WAVE8_CUBAN_CONTRACT_IDS,
            {"hced-Moncada1953-1", "hced-Cienfuegos1957-1"},
        )
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_CUBAN_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["start_date"],
                    canonical["end_date"],
                    canonical["granularity"],
                    contract["side_2_entity_ids"][0],
                ),
                values,
            )
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(contract["side_1_entity_ids"], [REPUBLIC])
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["confidence"], 0.96)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_sierra_maestra_is_explicit_unknown_campaign_hold(self) -> None:
        self.assertEqual(
            lane.WAVE8_CUBAN_HOLD_IDS,
            {"hced-Sierra Maestra1958-1"},
        )
        hold = lane.WAVE8_CUBAN_HOLDS["hced-Sierra Maestra1958-1"]
        self.assertEqual(
            hold["hold_category"],
            "campaign_umbrella_constituent_ambiguity",
        )
        self.assertEqual(hold["result_type"], "unknown")
        self.assertEqual(hold["reviewed_outcome"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertNotIn("winner_side", hold)
        self.assertEqual(hold["side_1_entity_ids"], [JULY_26])
        self.assertEqual(hold["side_2_entity_ids"], [REPUBLIC])
        self.assertIn("El Jigüe", hold["hold_reason"])
        self.assertIn("never a draw", hold["hold_reason"])
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "campaign_umbrella_with_el_jigue_constituent_ambiguity",
        )
        self.assertNotIn(
            "hced-Sierra Maestra1958-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_sources_are_closed_and_each_win_has_two_independent_families(self) -> None:
        sources = {str(source["id"]): source for source in lane.WAVE8_CUBAN_SOURCES}
        self.assertEqual(len(sources), 5)
        for source in sources.values():
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_CUBAN_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                outcome_ids = contract["outcome_source_ids"]
                self.assertEqual(len(outcome_ids), 2)
                self.assertEqual(contract["evidence_refs"], outcome_ids)
                self.assertEqual(contract["date_source_ids"], outcome_ids)
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(set(contract["event_evidence_roles"]), set(outcome_ids))
                self.assertTrue(set(outcome_ids) <= set(sources))
                for source_id in outcome_ids:
                    self.assertIn("outcome", sources[source_id]["evidence_roles"])

    def test_new_identities_are_alias_free_and_event_bounded(self) -> None:
        entities = {str(entity["id"]): entity for entity in lane.WAVE8_CUBAN_ENTITIES}
        self.assertEqual(set(entities), {MONCADA_GROUP, CIENFUEGOS_COALITION})
        expected_years = {MONCADA_GROUP: 1953, CIENFUEGOS_COALITION: 1957}
        for entity_id, entity in entities.items():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                (expected_years[entity_id], expected_years[entity_id]),
            )
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())

    def test_existing_identity_and_label_policy_boundaries_are_unchanged(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        self.assertEqual(
            {
                key: entities[REPUBLIC][key]
                for key in ("name", "kind", "start_year", "end_year", "aliases")
            },
            lane.WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES[REPUBLIC],
        )
        self.assertEqual(
            {
                key: entities[JULY_26][key]
                for key in ("name", "kind", "start_year", "end_year", "aliases")
            },
            lane.WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES[JULY_26],
        )
        self.assertNotIn("cuban government", HCED_LABEL_POLICIES)
        self.assertEqual(
            HCED_LABEL_POLICIES["cuban rebels"],
            (
                (1868, 1878, "cuban_insurgent_army_1868"),
                (1895, 1898, "cuban_liberation_army_1895"),
                (1955, 1959, "cuban_26_july_movement"),
            ),
        )

    def test_emitted_events_are_exact_two_side_republic_wins(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_CUBAN_CONTRACT_IDS)
        opponents = {
            "hced-Moncada1953-1": MONCADA_GROUP,
            "hced-Cienfuegos1957-1": CIENFUEGOS_COALITION,
        }
        for candidate_id, event in events.items():
            contract = lane.WAVE8_CUBAN_CONTRACTS[candidate_id]
            terminations = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {
                    REPUBLIC: "engagement_victory",
                    opponents[candidate_id]: "engagement_defeat",
                },
            )
            self.assertEqual(len(event["participants"]), 2)
            self.assertEqual(event["name"], contract["canonical_event"]["name"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "internal_rebellion")
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(event["confidence"], 0.96)
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            Event.from_dict(event)

    def test_source_point_country_and_location_provenance_are_retained(self) -> None:
        self.assertFalse(lane.WAVE8_CUBAN_POINT_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_CUBAN_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_CUBAN_LOCATION_QUARANTINE_REASONS)
        expected = {
            "hced-Moncada1953-1": [-75.8189458, 20.02586],
            "hced-Cienfuegos1957-1": [-80.4437781, 22.1599753],
        }
        for event in self._events():
            self.assertEqual(
                event["geometry"],
                {"type": "Point", "coordinates": expected[event["hced_candidate_id"]]},
            )
            self.assertEqual(event["modern_location_country"], "Cuba")
            self.assertIn("location_provenance", event)

    def test_wikidata_moncada_twin_is_discovery_only_unknown(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        row = by_id["Q11211553"]
        self.assertEqual(_full_row_sha256(row), EXPECTED_DISCOVERY_HASHES["Q11211553"])
        self.assertIs(row["do_not_rate_automatically"], True)
        self.assertEqual(row["winners"], [])
        self.assertEqual(row["participants"], [])
        self.assertEqual(
            lane.WAVE8_CUBAN_DISCOVERY_EXPECTED["Q11211553"][
                "outcome_disposition"
            ],
            "unknown_never_draw",
        )
        self.assertEqual(
            lane.validate_wave8_cuban_discovery_dispositions(self.wikidata_rows),
            {
                "discovery_nonrating_records": 1,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 1,
            },
        )
        self.assertEqual(len(self._events()), 2)

    def test_cross_source_inventory_and_artifact_state_are_fail_closed(self) -> None:
        owned_count = sum(
            event.get("hced_candidate_id") in lane.WAVE8_CUBAN_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_cuban_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "discovery_nonrating_dispositions": 1,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        artifact = lane.validate_wave8_cuban_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        self.assertEqual(artifact["promoted_events"], owned_count)
        self.assertEqual(
            artifact["artifact_state"],
            "integrated" if owned_count else "absent",
        )

    def test_queue_drift_extra_label_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Moncada1953-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_cuban_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-Cienfuegos1957-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_cuban_queue_contracts(duplicated)

        future_label = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-cuban-government",
                "side_1_raw": "Cuban Government",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_cuban_queue_contracts(future_label)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_cuban_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_cuban_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_entity_source_collisions_and_partial_artifacts_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(REPUBLIC)
        with self.assertRaisesRegex(ValueError, "missing existing identity"):
            lane.promote_wave8_cuban_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        colliding_entities = copy.deepcopy(entities)
        colliding_entities[MONCADA_GROUP]["name"] = "drifted name"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_cuban_entities(colliding_entities)

        colliding_sources = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_CUBAN_SOURCES[0]["id"])
        colliding_sources[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_cuban_sources(colliding_sources)

        promoted = lane.promote_wave8_cuban_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "artifacts are partial"):
            lane.validate_wave8_cuban_current_artifact_state(
                [*existing, promoted[0]],
                entities.values(),
                sources.values(),
            )

    def test_future_iwd_iwbd_and_release_twins_fail_closed(self) -> None:
        future_iwd = [
            *copy.deepcopy(self.iwd_rows),
            {
                "candidate_id": "iwd-future-moncada",
                "name": "Attack on the Moncada Barracks",
                "year": 1953,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_cuban_integration_dispositions(
                self.hced_rows,
                future_iwd,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-cienfuegos",
                "name": "Cienfuegos naval revolt",
                "start_date": "1957-09-05",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_cuban_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_el_jigue_twin",
                "name": "Battle of El Jigüe",
                "year": 1958,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_cuban_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_counts_metadata_signature_and_installers_are_pinned(self) -> None:
        entities, sources, _ = self._installed()
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_cuban_entities(entities)
        lane.install_wave8_cuban_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)
        self.assertEqual(
            lane.wave8_cuban_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 1,
                "holds": 1,
                "integration_dispositions": 1,
                "new_entities": 2,
                "new_sources": 5,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 1,
            },
        )
        self.assertEqual(
            lane.wave8_cuban_cohort_counts(),
            {"cuban_revolution_exact_rows_1953_1958": 3},
        )
        self.assertEqual(
            lane.wave8_cuban_audit_signature(),
            lane.WAVE8_CUBAN_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_cuban_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_cuban_counts())
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(lane.WAVE8_CUBAN_CONTRACT_IDS))
        self.assertEqual(metadata["hold_candidate_ids"], ["hced-Sierra Maestra1958-1"])
        self.assertEqual(len(metadata["discovery_dispositions"]), 1)


if __name__ == "__main__":
    unittest.main()
