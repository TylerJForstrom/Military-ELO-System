import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_cordova as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.release import HCED_LABEL_POLICIES


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_cordova_"

CROWN_CASTILE = "crown_castile_1230"
CORDOBA_DEFENDERS = "cordoba_muslim_defenders_1235_1236"
KINGDOM_LEON = "clio_es_leon_k_911_229ce82d"
CASTILIAN_CONTINGENT = "fernan_gonzalez_castilian_contingent_simancas_939"
PAMPLONESE_CONTINGENT = "garcia_sanchez_i_pamplonese_contingent_simancas_939"
CALIPHATE_CORDOBA = "clio_es_cordoba_cal_936_feb4eaea"

EXPECTED_HASHES = {
    "hced-Calatanazar1002-1": (
        "25ef78d0b79342984fc0c30b4ce1956d8dc02cf72e93414536e44fc7d790c230"
    ),
    "hced-Cordova1236-1": (
        "f173450a0043074a8fe105c00fbe13f8e4453fba9eba8d09e681d60478f77ab3"
    ),
    "hced-Simancas, Valladolid939-1": (
        "570456029cf11bb7bcc50bd48a555e2c219e403c79026d59faa2903c6aad51fe"
    ),
    "hced-Zamora873-1": (
        "e727c88472ee0c477d40d482816dbf9dd7bb0eccc9ca3e5e21eaefb97a4ab13a"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q1518266": "825a2d54d2e8a15cbb66cdd37523a0a695b9f90b3ff9611378d8cddb5be2b47d",
    "Q1807089": "a26195fac9b4779d09e6cc1ec9119dd09cd9b3ec11d5f421e221e26367099374",
    "Q12216248": "8ca97deb7677c524db65b739abfefead0a31861643d94bfd9864407ee92c37c9",
    "Q125861402": "3f578f507415483787b0b4d45612a2fa696effffa88b9a8851370343226822da",
    "Q4870264": "2fef2bea67e021025f69121a1dd0c7bf56e2d3a2431bd7418155d9fc7cfb0c14",
    "Q5242957": "aa78ac15cf7439345f9e9f1dc3db800bc19d6c6cb3c7da6c01dc195147ccc6be",
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


class Wave8CordovaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {str(entity["id"]) for entity in lane.WAVE8_CORDOVA_ENTITIES}
        lane_source_ids = {str(source["id"]) for source in lane.WAVE8_CORDOVA_SOURCES}
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_CORDOVA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        lane.install_wave8_cordova_entities(entities)
        lane.install_wave8_cordova_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_cordova_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_all_four_hced_rows_and_hashes_are_pinned(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "cordova"
            or normalize_label(row.get("side_2_raw")) == "cordova"
            or normalize_label(row.get("name")) == "cordova"
        ]
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_CORDOVA_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_accounting_is_two_promotions_and_two_exclusions(self) -> None:
        self.assertEqual(
            lane.validate_wave8_cordova_queue_contracts(self.hced_rows),
            {
                "exact_rows": 4,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(
            lane.WAVE8_CORDOVA_RESERVED_IDS,
            lane.WAVE8_CORDOVA_CONTRACT_IDS
            | lane.WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS,
        )

    def test_cordova_and_andalucia_historical_funnel_pins_are_exact(self) -> None:
        historical_rows = []
        for label, expected in lane.WAVE8_CORDOVA_FUNNEL_AUDIT.items():
            row = {"label": label, **copy.deepcopy(expected)}
            zero_time_valid = row.pop("zero_time_valid_candidates")
            row["failure_cases"] = {
                "zero_time_valid_candidates": zero_time_valid
            }
            historical_rows.append(row)
        self.assertEqual(
            lane.validate_wave8_cordova_funnel({"labels": historical_rows}),
            {"events_touched": 5, "labels": 2, "sole_blocker_events": 3},
        )
        live_by_label = {
            str(row.get("label")): row for row in self.funnel.get("labels", [])
        }
        self.assertNotIn("cordova", live_by_label)
        if "andalucia" in live_by_label:
            self.assertLess(
                int(live_by_label["andalucia"]["events_touched"]),
                lane.WAVE8_CORDOVA_FUNNEL_AUDIT["andalucia"]["events_touched"],
            )
            self.assertNotEqual(
                live_by_label["andalucia"]["event_candidate_id_sha256"],
                lane.WAVE8_CORDOVA_FUNNEL_AUDIT["andalucia"][
                    "event_candidate_id_sha256"
                ],
            )
        self.assertEqual(
            lane.WAVE8_CORDOVA_FUNNEL_AUDIT["cordova"]["events_touched"],
            3,
        )
        self.assertEqual(
            lane.WAVE8_CORDOVA_FUNNEL_AUDIT["andalucia"]["events_touched"],
            2,
        )

    def test_only_cordoba_and_simancas_promote(self) -> None:
        self.assertEqual(
            lane.WAVE8_CORDOVA_CONTRACT_IDS,
            {"hced-Cordova1236-1", "hced-Simancas, Valladolid939-1"},
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in self._events()},
            lane.WAVE8_CORDOVA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_CORDOVA_HOLDS)

    def test_terminal_exclusions_emit_no_result_participants_or_dates(self) -> None:
        self.assertEqual(
            lane.WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS,
            {"hced-Calatanazar1002-1", "hced-Zamora873-1"},
        )
        forbidden = {
            "canonical_event",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        for candidate_id, exclusion in lane.WAVE8_CORDOVA_TERMINAL_EXCLUSIONS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(exclusion["disposition"], "terminal_exclusion")
                self.assertIs(exclusion["terminal_exclusion"], True)
                self.assertIs(exclusion["unknown_is_never_draw"], True)
                self.assertFalse(forbidden & set(exclusion))
        emitted = {event["hced_candidate_id"] for event in self._events()}
        self.assertFalse(emitted & lane.WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS)

    def test_ten_sources_are_independent_closed_and_parseable(self) -> None:
        sources = {str(source["id"]): source for source in lane.WAVE8_CORDOVA_SOURCES}
        self.assertEqual(len(sources), 10)
        self.assertEqual(
            len({source["source_family_id"] for source in sources.values()}),
            10,
        )
        for source in sources.values():
            Source.from_dict(source)
        used = set()
        for contract in lane.WAVE8_CORDOVA_CONTRACTS.values():
            self.assertEqual(contract["evidence_refs"], contract["outcome_source_ids"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            used.update(contract["evidence_refs"])
        for exclusion in lane.WAVE8_CORDOVA_TERMINAL_EXCLUSIONS.values():
            used.update(exclusion["evidence_refs"])
        self.assertEqual(used, set(sources))

    def test_three_new_identities_are_alias_free_and_narrowly_bounded(self) -> None:
        entities = {str(entity["id"]): entity for entity in lane.WAVE8_CORDOVA_ENTITIES}
        self.assertEqual(
            set(entities),
            {CORDOBA_DEFENDERS, CASTILIAN_CONTINGENT, PAMPLONESE_CONTINGENT},
        )
        self.assertEqual(
            (entities[CORDOBA_DEFENDERS]["start_year"], entities[CORDOBA_DEFENDERS]["end_year"]),
            (1235, 1236),
        )
        for entity_id in (CASTILIAN_CONTINGENT, PAMPLONESE_CONTINGENT):
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (939, 939),
            )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            Entity.from_dict(entity)

    def test_existing_identity_windows_are_reused_without_mutation(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        self.assertEqual(
            lane.validate_wave8_cordova_existing_entities(entities),
            {"required_existing_entities": 3},
        )
        self.assertEqual(
            (entities[CROWN_CASTILE]["start_year"], entities[CROWN_CASTILE]["end_year"]),
            (1230, 1715),
        )
        self.assertEqual(
            (entities[KINGDOM_LEON]["start_year"], entities[KINGDOM_LEON]["end_year"]),
            (911, 1235),
        )
        self.assertEqual(
            (
                entities[CALIPHATE_CORDOBA]["start_year"],
                entities[CALIPHATE_CORDOBA]["end_year"],
            ),
            (936, 1071),
        )

    def test_no_broad_cordoba_or_andalucia_alias_policy_is_added(self) -> None:
        forbidden = {"cordova", "cordoba", "andalucia"}
        self.assertFalse(forbidden & set(HCED_LABEL_POLICIES))
        for entity in lane.WAVE8_CORDOVA_ENTITIES:
            self.assertFalse(entity["aliases"])
        for event in self._events():
            self.assertEqual(event["aliases"], [])

    def test_exact_date_ranges_and_source_override_are_pinned(self) -> None:
        expected = {
            "hced-Simancas, Valladolid939-1": (
                "Battle of Simancas",
                939,
                939,
                "0939-08-11",
                "0939-08-14",
                False,
            ),
            "hced-Cordova1236-1": (
                "Siege and conquest of Córdoba",
                1235,
                1236,
                "1235-12-30",
                "1236-07-06",
                True,
            ),
        }
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_CORDOVA_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["year_low"],
                    canonical["year_high"],
                    canonical["start_date"],
                    canonical["end_date"],
                    contract["source_date_override"],
                ),
                values,
            )
            self.assertEqual(canonical["date_precision"], "day_range")
            self.assertEqual(contract["date_source_ids"], contract["evidence_refs"])

    def test_emitted_cordoba_event_has_exact_two_sides_and_date_interval(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        event = events["hced-Cordova1236-1"]
        self.assertEqual(event["id"], "hced_wave8_cordova_hced_cordova1236_1")
        self.assertEqual((event["year"], event["end_year"]), (1235, 1236))
        self.assertEqual(
            event["date_interval"],
            {"start": "1235-12-30", "end": "1236-07-06"},
        )
        self.assertEqual(
            {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            },
            {
                CROWN_CASTILE: "engagement_victory",
                CORDOBA_DEFENDERS: "engagement_defeat",
            },
        )
        Event.from_dict(event)

    def test_emitted_simancas_event_rates_one_four_actor_battle(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        event = events["hced-Simancas, Valladolid939-1"]
        self.assertEqual(
            event["id"],
            "hced_wave8_cordova_hced_simancas_valladolid939_1",
        )
        self.assertEqual(
            event["date_interval"],
            {"start": "0939-08-11", "end": "0939-08-14"},
        )
        terminations = {
            participant["entity_id"]: participant["termination"]
            for participant in event["participants"]
        }
        self.assertEqual(
            terminations,
            {
                KINGDOM_LEON: "engagement_victory",
                CASTILIAN_CONTINGENT: "engagement_victory",
                PAMPLONESE_CONTINGENT: "engagement_victory",
                CALIPHATE_CORDOBA: "engagement_defeat",
            },
        )
        self.assertNotIn("Alhándega", event["name"])
        Event.from_dict(event)

    def test_promotions_retain_tactical_results_without_overrides(self) -> None:
        for contract in lane.WAVE8_CORDOVA_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        for event in self._events():
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["war_type"], "interstate")
            self.assertNotEqual(event["decisiveness"], 0.32)

    def test_source_points_country_and_location_provenance_are_retained(self) -> None:
        self.assertFalse(lane.WAVE8_CORDOVA_POINT_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_CORDOVA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS)
        expected = {
            "hced-Cordova1236-1": [-4.7793835, 37.8881751],
            "hced-Simancas, Valladolid939-1": [-4.8300298, 41.5909697],
        }
        for event in self._events():
            self.assertEqual(
                event["geometry"],
                {"type": "Point", "coordinates": expected[event["hced_candidate_id"]]},
            )
            self.assertEqual(event["modern_location_country"], "Spain")
            self.assertIn("location_provenance", event)

    def test_all_six_wikidata_rows_are_fingerprinted_discovery_only(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(_full_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["winners"], [])
        self.assertEqual(
            lane.validate_wave8_cordova_discovery_dispositions(self.wikidata_rows),
            {
                "discovery_nonrating_records": 6,
                "discovery_promotions": 0,
                "distinct_staged_records": 1,
                "exact_twins": 3,
                "source_critical_holds": 2,
                "unknown_never_draw_rows": 6,
            },
        )

    def test_discovery_relationships_cover_twins_holds_and_distinct_zamora(self) -> None:
        dispositions = lane.WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS
        self.assertEqual(
            {key for key, value in dispositions.items() if value["disposition"] == "discovery_only_duplicate"},
            {"Q1518266", "Q12216248"},
        )
        self.assertEqual(
            {key for key, value in dispositions.items() if value["disposition"] == "discovery_only_adjudication_hold"},
            {"Q125861402", "Q4870264"},
        )
        self.assertEqual(
            dispositions["Q1807089"]["disposition"],
            "discovery_only_terminally_excluded_concept",
        )
        self.assertEqual(
            dispositions["Q5242957"]["disposition"],
            "discovery_only_distinct_staged_event",
        )
        self.assertTrue(
            all(
                value["outcome_disposition"] == "unknown_never_draw"
                for value in dispositions.values()
            )
        )

    def test_cross_source_duplicate_audit_is_clear(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_cordova_integration_dispositions(
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

    def test_unreviewed_release_twin_fails_closed(self) -> None:
        _, _, existing = self._installed()
        planted = {
            "id": "planted-simancas-twin",
            "name": "Battle of Simancas",
            "year": 939,
        }
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_cordova_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, planted],
            )

    def test_hced_and_discovery_row_drift_fail_closed(self) -> None:
        hced = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in hced if item.get("candidate_id") == "hced-Zamora873-1"
        )
        row["winner_raw"] = "unknown"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_cordova_queue_contracts(hced)

        discovery = copy.deepcopy(self.wikidata_rows)
        row = next(item for item in discovery if item.get("candidate_id") == "Q1518266")
        row["winners"] = [{"label": "Kingdom of León"}]
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_cordova_discovery_dispositions(discovery)

    def test_duplicate_promotion_and_fixture_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_cordova_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_cordova_contracts(
                self.hced_rows,
                entities,
                [*existing, *events],
            )

        colliding_sources = copy.deepcopy(sources)
        colliding_sources["wave8_cordova_simancas_kusku_2023"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_cordova_sources(colliding_sources)

    def test_signature_counts_and_metadata_are_sealed(self) -> None:
        self.assertEqual(
            lane.wave8_cordova_audit_signature(),
            "92afa442ef9e36650c43743da0d86549ed2ef9e041924bf10a194f1bb1969f66",
        )
        self.assertEqual(
            lane.wave8_cordova_audit_signature(),
            lane.WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_cordova_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 6,
                "holds": 0,
                "integration_dispositions": 6,
                "new_entities": 3,
                "new_sources": 10,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 2,
                "unknown_discovery_outcomes": 6,
            },
        )
        self.assertEqual(
            lane.wave8_cordova_cohort_counts(),
            {
                "castilian_conquest_of_cordoba_1235_1236": 1,
                "simancas_campaign_939": 1,
            },
        )
        metadata = lane.wave8_cordova_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_cordova_counts())
        self.assertEqual(metadata["final_audit_signature"], lane.WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(len(metadata["discovery_dispositions"]), 6)


if __name__ == "__main__":
    unittest.main()
