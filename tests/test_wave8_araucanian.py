import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_araucanian as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_araucanian_"

TUCAPEL_ALLIANCE = "lautaro_tucapel_lineage_alliance_1553_1554"
VALDIVIA_COLUMN = "valdivia_tucapel_column_1553_1554"
MARIGUENU_FORCE = "lautaro_mariguenu_force_1554"
VILLAGRA_MARIGUENU = "villagra_mariguenu_column_1554"
MATAQUITO_ASSAULT = "villagra_godinez_mataquito_assault_force_1557"
MATAQUITO_DEFENDERS = "lautaro_mataquito_fort_force_1557"
CURALABA_STRIKE = "pelantaro_curalaba_strike_force_1598"
CURALABA_COLUMN = "onez_de_loyola_curalaba_column_1598"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _full_row_sha256(row) -> str:
    payload = json.dumps(
        row,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Wave8AraucanianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata_battles = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.wikidata_generic = _jsonl(
            ROOT / "data/review/wikidata-candidates.jsonl"
        )
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.iwd = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.cliopatria = _jsonl(
            ROOT / "data/review/cliopatria-entity-candidates.jsonl"
        )
        cls.brecke = _jsonl(ROOT / "data/reference/brecke-wars.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.seed_entities = _json(ROOT / "data/seed/entities.json")
        cls.seed_events = _json(ROOT / "data/seed/events.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item.get("id"))
            not in {entity["id"] for entity in lane.WAVE8_ARAUCANIAN_ENTITIES}
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item.get("id"))
            not in {source["id"] for source in lane.WAVE8_ARAUCANIAN_SOURCES}
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_ARAUCANIAN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        lane.install_wave8_araucanian_entities(entities)
        lane.install_wave8_araucanian_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_araucanian_contracts(
            self.hced, entities, existing
        )

    def test_input_snapshot_hashes_are_pinned(self):
        paths = {
            "brecke": ROOT / "data/reference/brecke-wars.jsonl",
            "cliopatria": ROOT / "data/review/cliopatria-entity-candidates.jsonl",
            "hced": ROOT / "data/review/hced-candidates.jsonl",
            "iwbd": ROOT / "data/review/iwbd-candidates.jsonl",
            "iwd": ROOT / "data/review/iwd-1.21-candidates.jsonl",
            "wikidata_battles": ROOT
            / "data/review/wikidata-battle-candidates.jsonl",
            "wikidata_generic": ROOT / "data/review/wikidata-candidates.jsonl",
        }
        self.assertEqual(
            {name: _sha256(path) for name, path in paths.items()},
            lane.WAVE8_ARAUCANIAN_INPUT_SHA256,
        )

    def test_hced_inventory_is_exactly_four_promote_one_hold_one_exclude(self):
        self.assertEqual(
            lane.validate_wave8_araucanian_queue_contracts(self.hced),
            {
                "exact_and_adjacent_label_rows": 6,
                "hced_homonym_records": 1,
                "holds": 1,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.WAVE8_ARAUCANIAN_CONTRACT_IDS,
            {
                "hced-Tucapel1553-1",
                "hced-Mariguenu1554-1",
                "hced-Mataquito1557-1",
                "hced-Curalaba1598-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_ARAUCANIAN_HOLD_IDS,
            {"hced-Tapalque Creek1856-1"},
        )
        self.assertEqual(
            lane.WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS,
            {"hced-Apeleg1883-1"},
        )

    def test_all_seven_hced_hashes_and_decisive_semantics_are_pinned(self):
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_ARAUCANIAN_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_ARAUCANIAN_ROW_HASHES))
        for candidate_id, expected_hash in lane.WAVE8_ARAUCANIAN_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                expected = lane.WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS[candidate_id]
                self.assertEqual(
                    {field: row.get(field) for field in expected}, expected
                )

    def test_five_funnel_labels_are_pinned(self):
        prepromotion_funnel = {
            "labels": list(lane.WAVE8_ARAUCANIAN_FUNNEL_AUDIT.values())
        }
        self.assertEqual(
            lane.validate_wave8_araucanian_funnel(prepromotion_funnel),
            {
                "events_touched": 6,
                "labels": 5,
                "sole_blocker_events": 6,
                "zero_time_valid_candidates": 6,
            },
        )
        exact = lane.WAVE8_ARAUCANIAN_FUNNEL_AUDIT["araucanian indians"]
        self.assertEqual(exact["events_touched"], 2)
        self.assertEqual(
            exact["event_candidate_id_sha256"],
            "1c9a29db0d3878a26055292613894a7069e937929404f6dc62a00a0c854e414a",
        )
        self.assertFalse(
            set(lane.WAVE8_ARAUCANIAN_FUNNEL_AUDIT)
            & {str(row.get("label")) for row in self.funnel.get("labels", [])}
        )

    def test_sources_parse_and_preserve_source_families(self):
        self.assertEqual(len(lane.WAVE8_ARAUCANIAN_SOURCES), 14)
        families = Counter(
            source["source_family_id"]
            for source in lane.WAVE8_ARAUCANIAN_SOURCES
        )
        self.assertEqual(families["memoria_chilena_lautaro_minisite"], 3)
        for source in lane.WAVE8_ARAUCANIAN_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertNotIn("wikipedia.org", source["url"])
        for contract in lane.WAVE8_ARAUCANIAN_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)

    def test_exactly_eight_alias_free_event_bounded_entities(self):
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_ARAUCANIAN_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {
                TUCAPEL_ALLIANCE,
                VALDIVIA_COLUMN,
                MARIGUENU_FORCE,
                VILLAGRA_MARIGUENU,
                MATAQUITO_ASSAULT,
                MATAQUITO_DEFENDERS,
                CURALABA_STRIKE,
                CURALABA_COLUMN,
            },
        )
        use = Counter(
            entity_id
            for contract in lane.WAVE8_ARAUCANIAN_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        )
        self.assertEqual(use, Counter({entity_id: 1 for entity_id in entities}))
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("inherits no Elo", entity["continuity_note"])
            Entity.from_dict(entity)

    def test_identity_windows_are_minimal_and_no_existing_window_changes(self):
        entities = {entity["id"]: entity for entity in lane.WAVE8_ARAUCANIAN_ENTITIES}
        self.assertEqual(
            (entities[TUCAPEL_ALLIANCE]["start_year"], entities[TUCAPEL_ALLIANCE]["end_year"]),
            (1553, 1554),
        )
        self.assertEqual(
            (entities[VALDIVIA_COLUMN]["start_year"], entities[VALDIVIA_COLUMN]["end_year"]),
            (1553, 1554),
        )
        for entity_id in set(entities) - {TUCAPEL_ALLIANCE, VALDIVIA_COLUMN}:
            self.assertEqual(entities[entity_id]["start_year"], entities[entity_id]["end_year"])

        before = {str(item["id"]): copy.deepcopy(item) for item in self.release_entities}
        installed = copy.deepcopy(before)
        lane.install_wave8_araucanian_entities(installed)
        for entity_id, entity in before.items():
            self.assertEqual(installed[entity_id], entity)

    def test_no_generic_mapuche_araucanian_or_spain_identity_leaks(self):
        forbidden = {
            "araucania",
            "araucanian indians",
            "araucanians",
            "mapuche",
            "mapuche rebels",
            "spain",
            "spanish empire",
        }
        aliases = {
            normalize_label(alias)
            for entity in lane.WAVE8_ARAUCANIAN_ENTITIES
            for alias in entity["aliases"]
        }
        self.assertFalse(aliases)
        participant_ids = {
            entity_id
            for contract in lane.WAVE8_ARAUCANIAN_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertFalse(forbidden & set(map(normalize_label, participant_ids)))
        self.assertNotIn("spanish_empire", participant_ids)

    def test_promoted_dates_names_and_granularities_are_exact(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Tucapel1553-1": (
                "Battle of Tucapel",
                1553,
                1554,
                "disputed_day",
                "single_field_battle_at_historic_fort_tucapel_not_capture_or_execution",
            ),
            "hced-Mariguenu1554-1": (
                "Battle of Mariguenu",
                1554,
                1554,
                "month",
                "single_field_battle_not_post_battle_massacre",
            ),
            "hced-Mataquito1557-1": (
                "Battle of Mataquito",
                1557,
                1557,
                "day",
                "single_dawn_assault_on_fortified_armed_camp_not_campaign_or_civilian_harm",
            ),
            "hced-Curalaba1598-1": (
                "Battle of Curalaba",
                1598,
                1598,
                "day",
                "single_dawn_attack_on_governor_marching_camp_not_1598_1604_uprising",
            ),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, values in expected.items():
            event = events[candidate_id]
            self.assertEqual(
                (
                    event["name"],
                    event["year"],
                    event["end_year"],
                    event["date_precision"],
                    event["reviewed_granularity"],
                ),
                values,
            )
            self.assertEqual(event["aliases"], [])
            parsed = Event.from_dict(event)
            self.assertEqual(parsed.date_interval.validation_errors(), [])

    def test_tucapel_and_mariguenu_uncertainty_cannot_gain_best_day(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        tucapel = events["hced-Tucapel1553-1"]
        mariguenu = events["hced-Mariguenu1554-1"]
        self.assertEqual(
            tucapel["date_interval"]["start"],
            {
                "best": None,
                "high": "1554-01-01",
                "low": "1553-12-25",
                "precision": "disputed_day",
            },
        )
        self.assertEqual(
            mariguenu["date_interval"]["start"],
            {
                "best": None,
                "high": "1554-02-26",
                "low": "1554-02-23",
                "precision": "month_disputed_day",
            },
        )
        self.assertEqual(mariguenu["date_precision"], "month")

        drifted = copy.deepcopy(self.hced)
        row = next(
            row
            for row in drifted
            if row.get("candidate_id") == "hced-Mariguenu1554-1"
        )
        row["start_date"] = "1554-02-26"
        with self.assertRaisesRegex(ValueError, "increased date precision"):
            lane.validate_wave8_araucanian_queue_contracts(drifted)

    def test_four_outcomes_are_decisive_and_unknown_never_draw(self):
        events = self._events()
        self.assertEqual(len(events), 4)
        self.assertEqual(sum(len(event["participants"]) for event in events), 8)
        for event in events:
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertEqual(
                terminations, {"engagement_victory", "engagement_defeat"}
            )
            self.assertFalse(
                any("inconclusive" in termination for termination in terminations)
            )
        self.assertEqual(
            lane.validate_wave8_araucanian_emissions(events),
            {
                "events": 4,
                "participants": 8,
                "retained_countries": 4,
                "retained_points": 0,
            },
        )

    def test_mataquito_is_only_the_armed_fortified_camp_boundary(self):
        contract = lane.WAVE8_ARAUCANIAN_CONTRACTS["hced-Mataquito1557-1"]
        self.assertEqual(contract["side_1_entity_ids"], [MATAQUITO_ASSAULT])
        self.assertEqual(contract["side_2_entity_ids"], [MATAQUITO_DEFENDERS])
        self.assertIn("armed_camp", contract["canonical_event"]["granularity"])
        self.assertIn("Civilians, captives", contract["audit_note"])
        self.assertFalse(contract["source_outcome_override"])
        self.assertFalse(contract["outcome_reversal"])

    def test_tapalque_hold_and_apeleg_exclusion_cannot_emit_results(self):
        tapalque = lane.WAVE8_ARAUCANIAN_HOLDS["hced-Tapalque Creek1856-1"]
        apeleg = lane.WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS["hced-Apeleg1883-1"]
        self.assertEqual(tapalque["canonical_event"]["date_assertions"], ["1855-10-29", "1856"])
        self.assertIn("Maica Indigenous lancers", tapalque["hold_reason"])
        self.assertEqual(apeleg["reviewed_outcome"], "not_rateable_civilian_mass_violence")
        self.assertIn("women and children", apeleg["exclusion_reason"])
        forbidden = {"result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids"}
        self.assertFalse(forbidden & set(tapalque))
        self.assertFalse(forbidden & set(apeleg))
        self.assertFalse(tapalque["automatic_rating"])
        self.assertFalse(apeleg["automatic_rating"])

    def test_duplicate_and_nesting_ownership_is_closed(self):
        owners = {
            candidate_id: item["canonical_owner"]
            for candidate_id, item in lane.WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.items()
            if item["canonical_owner"] is not None
        }
        self.assertEqual(
            owners,
            {
                "Q2338555": "hced-Mariguenu1554-1",
                "Q1617667": "hced-Mataquito1557-1",
                "Q645257": "hced-Tucapel1553-1",
                "Q1629355": "hced-Curalaba1598-1",
                "Q51077807": "hced-Tapalque Creek1856-1",
                "Q4872274": "hced_label_hced_san_jacinto1899_1",
            },
        )
        self.assertIn(
            "not capture or execution".replace(" ", "_"),
            lane.WAVE8_ARAUCANIAN_CONTRACTS["hced-Tucapel1553-1"]
            ["canonical_event"]["granularity"],
        )
        self.assertIn(
            "not_post_battle_massacre",
            lane.WAVE8_ARAUCANIAN_CONTRACTS["hced-Mariguenu1554-1"]
            ["canonical_event"]["granularity"],
        )

    def test_four_points_are_quarantined_and_no_country_is_quarantined(self):
        self.assertEqual(
            lane.WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ARAUCANIAN_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            lane.wave8_araucanian_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_ARAUCANIAN_CONTRACT_IDS,
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Chile")
            self.assertIn("location_provenance", event)

    def test_wikidata_inventory_is_33_nonrating_records(self):
        self.assertEqual(
            lane.validate_wave8_araucanian_discovery_dispositions(
                self.wikidata_battles
            ),
            {
                "discovery_nonrating_records": 33,
                "duplicate_discovery_records": 6,
                "held_discovery_records": 24,
                "unrelated_homonym_records": 3,
                "unknown_never_draw_rows": 33,
            },
        )
        rows = {
            str(row["candidate_id"]): row
            for row in self.wikidata_battles
            if str(row.get("candidate_id"))
            in lane.WAVE8_ARAUCANIAN_WIKIDATA_ROW_HASHES
        }
        self.assertEqual(len(rows), 33)
        for candidate_id, expected_hash in lane.WAVE8_ARAUCANIAN_WIKIDATA_ROW_HASHES.items():
            self.assertEqual(_full_row_sha256(rows[candidate_id]), expected_hash)

    def test_all_wikidata_unknowns_remain_unknown_not_draws(self):
        for candidate_id, disposition in lane.WAVE8_ARAUCANIAN_WIKIDATA_DISPOSITIONS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertFalse(disposition["automatic_rating"])
                self.assertEqual(
                    disposition["outcome_disposition"], "unknown_never_draw"
                )
        self.assertNotIn(
            "draw",
            {
                item["outcome_disposition"]
                for item in lane.WAVE8_ARAUCANIAN_WIKIDATA_DISPOSITIONS.values()
            },
        )

    def test_discovery_semantic_drift_fails_even_if_hash_is_mocked(self):
        rows = copy.deepcopy(self.wikidata_battles)
        target = next(row for row in rows if row.get("candidate_id") == "Q645257")
        target["winners"] = [{"uri": "http://www.wikidata.org/entity/Q0"}]

        def pinned_hash(row):
            candidate_id = str(row.get("candidate_id"))
            return lane.WAVE8_ARAUCANIAN_WIKIDATA_ROW_HASHES.get(
                candidate_id, _full_row_sha256(row)
            )

        with patch.object(lane, "_full_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "nonrating guard changed"):
                lane.validate_wave8_araucanian_discovery_dispositions(rows)

    def test_brecke_iwbd_iwd_generic_and_cliopatria_dispositions_are_exhaustive(self):
        iwbd = next(
            row for row in self.iwbd if row.get("candidate_id") == "iwbd-40-14-142"
        )
        brecke = next(
            row for row in self.brecke if row.get("brecke_id") == "brecke-2719"
        )
        self.assertEqual(
            _full_row_sha256(iwbd),
            lane.WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS["iwbd-40-14-142"]
            ["raw_row_sha256"],
        )
        self.assertEqual(
            _full_row_sha256(brecke),
            lane.WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS["brecke-2719"]
            ["raw_row_sha256"],
        )
        self.assertFalse(
            lane.WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS["iwbd-40-14-142"]
            ["automatic_rating"]
        )
        self.assertEqual(
            lane.WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS["brecke-2719"]
            ["outcome_disposition"],
            "unknown_never_draw",
        )

    def test_cross_source_inventory_is_exactly_42_with_4_25_13(self):
        self.assertEqual(
            lane.validate_wave8_araucanian_cross_source_inventory(
                self.hced,
                self.wikidata_battles,
                self.brecke,
                self.iwbd,
                self.iwd,
                self.wikidata_generic,
                self.cliopatria,
            ),
            {
                "audited_records": 42,
                "brecke_records": 1,
                "cliopatria_records": 0,
                "excluded_records": 13,
                "hced_records": 7,
                "held_records": 25,
                "iwbd_records": 1,
                "iwd_records": 0,
                "promoted_records": 4,
                "wikidata_battle_records": 33,
                "wikidata_generic_records": 0,
            },
        )
        self.assertEqual(len(lane.WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS), 42)
        payload = "\n".join(sorted(lane.WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS)) + "\n"
        self.assertEqual(
            hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "d35423568a77931b8436a45bc3c7bffe1ecd280baf5c883aaf8d15ab99d40a60",
        )

    def test_new_near_candidate_in_zero_inventory_fails_closed(self):
        iwd = [
            *copy.deepcopy(self.iwd),
            {"candidate_id": "future-mapuche", "name": "Mapuche discovery"},
        ]
        with self.assertRaisesRegex(ValueError, "zero-overlap"):
            lane.validate_wave8_araucanian_cross_source_inventory(
                self.hced,
                self.wikidata_battles,
                self.brecke,
                self.iwbd,
                iwd,
                self.wikidata_generic,
                self.cliopatria,
            )

    def test_hced_semantic_drift_fails_even_if_canonical_hash_is_mocked(self):
        rows = copy.deepcopy(self.hced)
        target = next(
            row
            for row in rows
            if row.get("candidate_id") == "hced-Apeleg1883-1"
        )
        target["massacre_raw"] = "Yes"

        def pinned_hash(row):
            candidate_id = str(row.get("candidate_id"))
            return lane.WAVE8_ARAUCANIAN_ROW_HASHES.get(
                candidate_id, canonical_hced_row_sha256(row)
            )

        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "locked row semantics changed"):
                lane.validate_wave8_araucanian_queue_contracts(rows)

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_araucanian_entities(entities)
        lane.install_wave8_araucanian_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entity_collision = copy.deepcopy(entities)
        entity_collision[TUCAPEL_ALLIANCE]["end_year"] = 1555
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_araucanian_entities(entity_collision)

        source_collision = copy.deepcopy(sources)
        source_id = lane.WAVE8_ARAUCANIAN_SOURCES[0]["id"]
        source_collision[source_id]["title"] = "drifted"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_araucanian_sources(source_collision)

    def test_promoter_rejects_missing_entity_and_duplicate_event(self):
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(CURALABA_STRIKE)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_araucanian_contracts(
                self.hced, missing, existing
            )

        events = lane.promote_wave8_araucanian_contracts(
            self.hced, entities, existing
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_araucanian_contracts(
                self.hced, entities, [*existing, *events]
            )

    def test_current_release_state_is_integrated_and_external_owner_is_exact(self):
        self.assertEqual(
            lane.validate_wave8_araucanian_current_artifact_state(
                self.release_events,
                self.release_entities,
                self.release_sources,
                self.seed_events,
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 8,
                "installed_sources": 14,
                "promoted_events": 4,
                "san_jacinto_external_owner": 1,
            },
        )
        released_candidates = {
            event.get("hced_candidate_id")
            for event in (*self.seed_events, *self.release_events)
        }
        self.assertTrue(lane.WAVE8_ARAUCANIAN_CONTRACT_IDS <= released_candidates)
        self.assertFalse(
            released_candidates
            & (
                lane.WAVE8_ARAUCANIAN_HOLD_IDS
                | lane.WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS
            )
        )

    def test_integrated_state_is_all_or_none_and_hold_leak_fails(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_araucanian_contracts(
            self.hced, entities, existing
        )
        san_jacinto = next(
            event
            for event in self.release_events
            if event.get("hced_candidate_id") == "hced-San Jacinto1899-1"
        )
        self.assertEqual(
            lane.validate_wave8_araucanian_current_artifact_state(
                [san_jacinto, *events], entities.values(), sources.values()
            )["artifact_state"],
            "integrated",
        )
        with self.assertRaisesRegex(ValueError, "partial"):
            lane.validate_wave8_araucanian_current_artifact_state(
                [san_jacinto, *events[:3]], entities.values(), sources.values()
            )
        leaked = {
            "id": "bad-tapalque",
            "hced_candidate_id": "hced-Tapalque Creek1856-1",
        }
        with self.assertRaisesRegex(ValueError, "hold/exclusion leaked"):
            lane.validate_wave8_araucanian_current_artifact_state(
                [san_jacinto, leaked], self.release_entities, self.release_sources
            )

    def test_no_other_promotion_module_owns_the_six_core_rows(self):
        promotion_dir = ROOT / "src/military_elo/promotion"
        core_ids = set(lane.WAVE8_ARAUCANIAN_RESERVED_IDS)
        collisions = {}
        for path in promotion_dir.glob("*.py"):
            if path.name in {"hced_location.py", "wave8_araucanian.py"}:
                continue
            text = path.read_text(encoding="utf-8")
            found = sorted(candidate_id for candidate_id in core_ids if candidate_id in text)
            if found:
                collisions[path.name] = found
        self.assertEqual(collisions, {})
        policy = (promotion_dir / "policy.py").read_text(encoding="utf-8")
        self.assertIn("hced-San Jacinto1899-1", policy)

    def test_counts_metadata_and_audit_signature_are_sealed(self):
        self.assertEqual(
            lane.wave8_araucanian_counts(),
            {
                "audited_source_records": 42,
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 35,
                "excluded_records": 13,
                "held_discovery_records": 24,
                "held_records": 25,
                "holds": 1,
                "new_entities": 8,
                "new_sources": 14,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promoted_records": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
                "unknown_discovery_outcomes": 34,
                "wikidata_nonrating_records": 33,
            },
        )
        self.assertEqual(
            lane.wave8_araucanian_audit_signature(),
            "2166530e7abd1e4f5c2d6e41cb61638ab17b2658eb4104feb6e1b4e064243c51",
        )
        self.assertEqual(
            lane.wave8_araucanian_audit_signature(),
            lane.WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_araucanian_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_araucanian_counts())
        self.assertEqual(len(metadata["wikidata_dispositions"]), 33)
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(lane.WAVE8_ARAUCANIAN_CONTRACT_IDS))

    def test_material_contract_or_signature_drift_fails_closed(self):
        contract = lane.WAVE8_ARAUCANIAN_CONTRACTS["hced-Mataquito1557-1"]
        with patch.dict(contract, {"confidence": 0.10}):
            with self.assertRaisesRegex(ValueError, "final audit signature changed"):
                lane.wave8_araucanian_counts()
        with patch.object(
            lane,
            "WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE",
            "0" * 64,
        ):
            with self.assertRaisesRegex(ValueError, "final audit signature changed"):
                lane.wave8_araucanian_counts()


if __name__ == "__main__":
    unittest.main()
