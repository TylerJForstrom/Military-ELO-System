import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_raichur_udayagiri_la_forbie as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_egypt_forces import (
    WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_raichur_udayagiri_la_forbie_"
VIJAYANAGARA = "clio_in_vijayanagara_emp_1344_0fe07dd4"
BIJAPUR = "clio_in_bijapur_sultanate_1492_49a19c59"
UDAYAGIRI_GARRISON = (
    "tirumala_routaraya_gajapati_udayagiri_garrison_1513_1514"
)
EGYPTIAN_AYYUBID = "al_salih_ayyub_egyptian_field_army_la_forbie_1244"
KHWARAZMIAN_MERCENARIES = "khwarazmian_mercenary_contingent_la_forbie_1244"
FRANKISH_HOST = "frankish_jerusalem_military_orders_host_la_forbie_1244"
SYRIAN_AYYUBID_COALITION = (
    "ayyubid_damascus_homs_kerak_coalition_la_forbie_1244"
)

EXPECTED_PROMOTIONS = {
    "hced-La Forbie1244-1": ("Battle of La Forbie", 1244, 1244),
    "hced-Raichur1520-1": ("Battle of Raichur (1520)", 1520, 1520),
    "hced-Udayagiri1513-1514-1": (
        "Siege and Capture of Udayagiri",
        1513,
        1514,
    ),
}
EXPECTED_SOURCE_URLS = {
    "wave8_rulf_asi_udayagiri_epigraphy": (
        "https://ignca.gov.in/Asi_data/35371.pdf"
    ),
    "wave8_rulf_eaton_raichur": (
        "https://doi.org/10.1017/S0026749X07003289"
    ),
    "wave8_rulf_jackson_la_forbie": (
        "https://doi.org/10.1017/S0041977X00053180"
    ),
    "wave8_rulf_karakus_demirci_la_forbie": (
        "https://dergipark.org.tr/en/pub/did/article/1551219"
    ),
    "wave8_rulf_rao_shulman_subrahmanyam": (
        "https://books.openedition.org/ifp/7916"
    ),
    "wave8_rulf_sewell_paes_nuniz": (
        "https://www.gutenberg.org/ebooks/3310"
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


class Wave8RaichurUdayagiriLaForbieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.iwd = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced
        }
        cls.lane_entity_ids = {
            str(entity["id"])
            for entity in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
        }
        cls.lane_source_ids = {
            str(source["id"])
            for source in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES
        }

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in self.lane_entity_ids
        }
        lane.install_wave8_raichur_udayagiri_la_forbie_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_raichur_udayagiri_la_forbie_contracts(
            self.hced,
            entities,
            existing,
        )

    def test_exact_queue_hashes_and_all_boundaries_are_pinned(self) -> None:
        self.assertEqual(
            lane.validate_wave8_raichur_udayagiri_la_forbie_queue_contracts(
                self.hced
            ),
            {
                "adjacent_hced_rows": 3,
                "holds": 10,
                "literal_label_inventories": 9,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 13,
                "reviewed_hced_rows_with_adjacency": 16,
            },
        )
        self.assertEqual(
            set(lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES),
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS,
        )
        for candidate_id, expected_hash in (
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                    expected_hash,
                )

    def test_literal_label_inventory_is_complete_without_resolver_changes(self) -> None:
        expected = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY
        for label, candidate_ids in expected.items():
            actual = tuple(
                sorted(
                    str(row["candidate_id"])
                    for row in self.hced
                    if label
                    in {
                        normalize_label(row.get("side_1_raw")),
                        normalize_label(row.get("side_2_raw")),
                    }
                )
            )
            self.assertEqual(actual, candidate_ids, label)
        source = (
            ROOT
            / "src/military_elo/promotion/wave8_raichur_udayagiri_la_forbie.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("HCED_LABEL_POLICIES", source)
        self.assertNotIn("SEED_CODE_POLICIES", source)
        self.assertNotIn("resolve_", source)

    def test_sources_are_exact_role_explicit_and_independent(self) -> None:
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES
        }
        self.assertEqual(
            {source_id: source["url"] for source_id, source in sources.items()},
            EXPECTED_SOURCE_URLS,
        )
        self.assertEqual(
            len({source["source_family_id"] for source in sources.values()}),
            6,
        )
        for source in sources.values():
            self.assertEqual(source["accessed"], "2026-07-20")
            self.assertEqual(
                source["evidence_roles"],
                ["identity_boundary_or_context_reference", "outcome"],
            )
            Source.from_dict(source)
        for contract in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS.values():
            self.assertEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                set(contract["event_evidence_roles"]),
                set(contract["outcome_source_ids"]),
            )
            self.assertTrue(
                all(role.strip() for role in contract["event_evidence_roles"].values())
            )

    def test_entities_are_alias_free_and_windows_are_not_widened(self) -> None:
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
        }
        self.assertEqual(len(entities), 6)
        self.assertEqual(
            (entities[VIJAYANAGARA]["start_year"], entities[VIJAYANAGARA]["end_year"]),
            (1344, 1571),
        )
        self.assertEqual(
            (
                entities[UDAYAGIRI_GARRISON]["start_year"],
                entities[UDAYAGIRI_GARRISON]["end_year"],
            ),
            (1513, 1514),
        )
        for entity_id in {
            EGYPTIAN_AYYUBID,
            KHWARAZMIAN_MERCENARIES,
            FRANKISH_HOST,
            SYRIAN_AYYUBID_COALITION,
        }:
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (1244, 1244),
            )
        for entity in entities.values():
            self.assertFalse(entity["aliases"])
            self.assertFalse(entity["predecessors"])
            self.assertNotIn("abasid", normalize_label(entity["name"]))
            Entity.from_dict(entity)

        registry_entity = next(
            item
            for item in self.registry["entities"]
            if item["id"] == VIJAYANAGARA
        )
        self.assertEqual(
            (registry_entity["start_year"], registry_entity["end_year"]),
            (1344, 1571),
        )
        released_bijapur = next(
            item for item in self.release_entities if item["id"] == BIJAPUR
        )
        self.assertLessEqual(released_bijapur["start_year"], 1520)
        self.assertGreaterEqual(released_bijapur["end_year"], 1520)

    def test_contract_dates_actors_and_raw_polarity_are_exact(self) -> None:
        expected_actors = {
            "hced-Raichur1520-1": ({VIJAYANAGARA}, {BIJAPUR}),
            "hced-Udayagiri1513-1514-1": (
                {VIJAYANAGARA},
                {UDAYAGIRI_GARRISON},
            ),
            "hced-La Forbie1244-1": (
                {EGYPTIAN_AYYUBID, KHWARAZMIAN_MERCENARIES},
                {FRANKISH_HOST, SYRIAN_AYYUBID_COALITION},
            ),
        }
        for candidate_id, contract in (
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS.items()
        ):
            raw = self.hced_by_id[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["year_low"], canonical["year_high"]),
                (raw["year_low"], raw["year_high"]),
            )
            self.assertEqual(
                (
                    set(contract["side_1_entity_ids"]),
                    set(contract["side_2_entity_ids"]),
                ),
                expected_actors[candidate_id],
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_date_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(raw["winner_raw"], raw["side_1_raw"])
            self.assertEqual(raw["loser_raw"], raw["side_2_raw"])
            self.assertNotIn(
                normalize_label(raw["winner_raw"]),
                {"draw", "inconclusive", "stalemate"},
            )

    def test_exactly_three_events_emit_with_expected_tactical_polarity(self) -> None:
        events = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        self.assertEqual(set(events), set(EXPECTED_PROMOTIONS))
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = events[candidate_id]
            self.assertEqual(
                (event["name"], event["year"], event["end_year"]),
                expected,
            )
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertNotIn("inconclusive", event["summary"].casefold())
            contract = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS[
                candidate_id
            ]
            terminations = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                {
                    entity_id
                    for entity_id, termination in terminations.items()
                    if termination == "engagement_victory"
                },
                set(contract["side_1_entity_ids"]),
            )
            self.assertEqual(
                {
                    entity_id
                    for entity_id, termination in terminations.items()
                    if termination == "engagement_defeat"
                },
                set(contract["side_2_entity_ids"]),
            )
            Event.from_dict(event)

    def test_raichur_bahmani_noise_and_la_forbie_coding_error_do_not_map(self) -> None:
        raichur = self.hced_by_id["hced-Raichur1520-1"]
        self.assertIn("Bahmani", raichur["participants_raw"])
        contract = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS[
            "hced-Raichur1520-1"
        ]
        self.assertEqual(contract["side_2_entity_ids"], [BIJAPUR])
        self.assertNotIn("bahmani", " ".join(contract["side_2_entity_ids"]))

        forbie = self.hced_by_id["hced-La Forbie1244-1"]
        self.assertIn("Abasid", forbie["side_1_raw"])
        self.assertIn("Abasid", forbie["side_2_raw"])
        for entity in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES:
            self.assertNotIn("abasid", normalize_label(entity["name"]))
            self.assertFalse(entity["aliases"])
        canonical = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS[
            "hced-La Forbie1244-1"
        ]["canonical_event"]
        self.assertEqual(canonical["date_text"], "1244")
        self.assertEqual(canonical["date_precision"], "year")

    def test_all_ten_holds_are_explicit_unknown_never_draw(self) -> None:
        self.assertEqual(
            len(lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS),
            10,
        )
        self.assertTrue(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS.isdisjoint(
                lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS
            )
        )
        for candidate_id, hold in (
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(hold["disposition"], "hold")
                self.assertEqual(hold["result_type"], "unknown")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertFalse(hold["evidence_refs"])
                self.assertTrue(hold["hold_category"])
                self.assertTrue(hold["hold_reason"])
        emitted = {event["hced_candidate_id"] for event in self._events()}
        self.assertTrue(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS.isdisjoint(emitted)
        )

    def test_south_pathan_and_terminal_khwarazm_hold_cohorts_are_complete(self) -> None:
        cohorts = lane.wave8_raichur_udayagiri_la_forbie_cohort_counts()
        self.assertEqual(
            cohorts,
            {
                "khwarazm_adjacent_terminal_holds_1221_1222": 2,
                "la_forbie_exact_promotion_1244": 1,
                "pathan_campaign_scope_holds_1750_1751": 3,
                "south_india_bahmani_scope_holds_1367_1443": 5,
                "south_india_exact_promotions_1513_1520": 2,
            },
        )
        herat = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS[
            "hced-Herat1221-1222-1"
        ]
        nishapur = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS[
            "hced-Nishapur1221-1"
        ]
        self.assertIn("missing_sides", herat["hold_category"])
        self.assertIn("massacre", nishapur["hold_category"])
        self.assertIsNone(self.hced_by_id["hced-Herat1221-1222-1"]["winner_raw"])
        self.assertFalse(
            self.hced_by_id["hced-Herat1221-1222-1"]["winner_loser_complete"]
        )

    def test_discovery_twins_are_fingerprinted_unknown_winner_nonowners(self) -> None:
        self.assertEqual(
            lane.validate_wave8_raichur_udayagiri_la_forbie_discovery_dispositions(
                self.wikidata
            ),
            {
                "discovery_nonrating_twins": 2,
                "discovery_promotions": 0,
                "unknown_winner_rows": 2,
            },
        )
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata
            if str(row.get("candidate_id"))
            in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES
        }
        self.assertEqual(set(by_id), {"Q4872151", "Q578201"})
        for row in by_id.values():
            self.assertEqual(row["winners"], [])
            self.assertIs(row["do_not_rate_automatically"], True)
            self.assertEqual(row["review_status"], "needs_review")
        self.assertEqual(by_id["Q578201"]["date"], "1244-10-24T00:00:00Z")
        self.assertEqual(by_id["Q578201"]["end_date"], "1244-10-25T00:00:00Z")
        self.assertEqual(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS[
                "hced-La Forbie1244-1"
            ]["canonical_event"]["date_text"],
            "1244",
        )

    def test_egypt_and_khwarazm_adjacencies_are_distinguished(self) -> None:
        dispositions = (
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS
        )
        self.assertEqual(
            set(dispositions),
            {"hced-Ascalon1247-1", "hced-Kuban1222-1", "hced-Otranto1917-1"},
        )
        self.assertEqual(
            WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES["hced-La Forbie1244-1"],
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES[
                "hced-La Forbie1244-1"
            ],
        )
        event_by_candidate = {
            str(event.get("hced_candidate_id")): event
            for event in self.release_events
            if event.get("hced_candidate_id") is not None
        }
        self.assertEqual(
            event_by_candidate["hced-Ascalon1247-1"]["id"],
            dispositions["hced-Ascalon1247-1"]["owner_event_id"],
        )
        self.assertEqual(
            event_by_candidate["hced-Otranto1917-1"]["id"],
            dispositions["hced-Otranto1917-1"]["owner_event_id"],
        )
        self.assertNotIn("hced-Kuban1222-1", event_by_candidate)

    def test_current_iwd_iwbd_hced_and_release_have_no_other_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                self.iwbd,
                existing,
                self.iwd,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
            },
        )

    def test_injected_twins_partial_integration_and_adjacent_drift_fail_closed(self) -> None:
        _, existing = self._installed()
        fake_hced = {
            "candidate_id": "hced-future-raichur-twin",
            "name": "Battle of Raichur",
            "year_low": 1520,
            "year_best": 1520,
            "year_high": 1520,
            "side_1_raw": "unrelated",
            "side_2_raw": "unrelated",
        }
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                [*self.hced, fake_hced],
                self.iwbd,
                existing,
                self.iwd,
            )

        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                [*self.iwbd, {"candidate_id": "iwbd-twin", "name": "Forbie", "year": 1244}],
                existing,
                self.iwd,
            )
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                self.iwbd,
                existing,
                [*self.iwd, {"candidate_id": "iwd-twin", "name": "Siege of Udayagiri", "year": 1514}],
            )
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                self.iwbd,
                [*existing, {"id": "release-twin", "name": "Battle of La Forbie", "year": 1244}],
                self.iwd,
            )

        promoted = self._events()
        with self.assertRaisesRegex(ValueError, "partial release integration"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                self.iwbd,
                [*existing, promoted[0]],
                self.iwd,
            )
        without_ascalon = [
            event
            for event in existing
            if event.get("hced_candidate_id") != "hced-Ascalon1247-1"
        ]
        with self.assertRaisesRegex(ValueError, "adjacent release owner drift"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
                self.hced,
                self.iwbd,
                without_ascalon,
                self.iwd,
            )

    def test_installers_are_idempotent_copy_safe_and_collision_safe(self) -> None:
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in self.lane_entity_ids
        }
        lane.install_wave8_raichur_udayagiri_la_forbie_entities(entities)
        lane.install_wave8_raichur_udayagiri_la_forbie_entities(entities)
        self.assertLessEqual(self.lane_entity_ids, set(entities))
        entities[VIJAYANAGARA]["name"] = "drift"
        self.assertEqual(
            next(
                entity["name"]
                for entity in lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
                if entity["id"] == VIJAYANAGARA
            ),
            "Vijayanagara Empire",
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_raichur_udayagiri_la_forbie_entities(entities)

        sources = {}
        lane.install_wave8_raichur_udayagiri_la_forbie_sources(sources)
        lane.install_wave8_raichur_udayagiri_la_forbie_sources(sources)
        self.assertEqual(set(sources), self.lane_source_ids)
        source_id = sorted(sources)[0]
        sources[source_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_raichur_udayagiri_la_forbie_sources(sources)

    def test_row_window_candidate_and_duplicate_event_guards_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-La Forbie1244-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_raichur_udayagiri_la_forbie_queue_contracts(
                tampered
            )

        entities, existing = self._installed()
        short = copy.deepcopy(entities)
        short[VIJAYANAGARA]["end_year"] = 1513
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_raichur_udayagiri_la_forbie_contracts(
                self.hced,
                short,
                existing,
            )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_raichur_udayagiri_la_forbie_contracts(
                self.hced,
                entities,
                [
                    *existing,
                    {
                        "id": "already-owned",
                        "name": "unrelated",
                        "year": 1520,
                        "hced_candidate_id": "hced-Raichur1520-1",
                    },
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_raichur_udayagiri_la_forbie_contracts(
                self.hced,
                entities,
                [
                    *existing,
                    {"id": "name-twin", "name": "Battle of La Forbie", "year": 1244},
                ],
            )

    def test_all_three_points_are_withheld_but_country_and_provenance_remain(self) -> None:
        self.assertEqual(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_COUNTRY_QUARANTINE_ADDITIONS
        )
        expected_countries = {
            "hced-La Forbie1244-1": "Israel",
            "hced-Raichur1520-1": "India",
            "hced-Udayagiri1513-1514-1": "India",
        }
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                expected_countries[candidate_id],
            )
            self.assertTrue(event["location_provenance"])
            review = lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LOCATION_QUARANTINE_REASONS[
                candidate_id
            ]
            self.assertEqual(review["actions"], ["withhold_point"])

    def test_current_artifacts_and_constructed_integration_are_all_or_none(self) -> None:
        state = lane.validate_wave8_raichur_udayagiri_la_forbie_current_artifact_state(
            self.release_entities,
            self.release_events,
            self.release_sources,
            self.release_metadata,
        )
        self.assertIn(state["integration_state"], {"preintegration", "integrated"})

        entities, existing = self._installed()
        events = lane.promote_wave8_raichur_udayagiri_la_forbie_contracts(
            self.hced,
            entities,
            existing,
        )
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in self.lane_source_ids
        }
        lane.install_wave8_raichur_udayagiri_la_forbie_sources(sources)
        metadata = copy.deepcopy(self.release_metadata)
        promotion = metadata.setdefault("promotion", {})
        promotion["accepted_wave8_raichur_udayagiri_la_forbie_hced_events"] = 3
        promotion["wave8_raichur_udayagiri_la_forbie_candidate_ids"] = sorted(
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
        )
        integrated = lane.validate_wave8_raichur_udayagiri_la_forbie_current_artifact_state(
            list(entities.values()),
            [*existing, *events],
            list(sources.values()),
            metadata,
        )
        self.assertEqual(
            integrated,
            {
                "entity_records": 6,
                "event_records": 3,
                "integration_state": "integrated",
                "metadata_marker": 1,
                "source_records": 6,
            },
        )
        with self.assertRaisesRegex(ValueError, "partial current-artifact integration"):
            missing_source_id = sorted(self.lane_source_ids)[0]
            lane.validate_wave8_raichur_udayagiri_la_forbie_current_artifact_state(
                list(entities.values()),
                [*existing, *events],
                [
                    source
                    for source_id, source in sources.items()
                    if source_id != missing_source_id
                ],
                metadata,
            )

    def test_funnel_pin_or_integrated_metadata_is_exact(self) -> None:
        integrated_ids = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
        } & lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
        if not integrated_ids:
            self.assertEqual(
                lane.validate_wave8_raichur_udayagiri_la_forbie_funnel(
                    self.funnel
                ),
                {
                    "audited_labels": 6,
                    "events_touched": 20,
                    "sole_blocker_events": 5,
                    "unresolved_side_attempts": 20,
                },
            )
            return
        promotion = self.release_metadata["promotion"]
        self.assertEqual(
            promotion["wave8_raichur_udayagiri_la_forbie_label_funnel_audit"],
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT,
        )

    def test_signature_counts_and_metadata_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_raichur_udayagiri_la_forbie_audit_signature(),
            lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_raichur_udayagiri_la_forbie_counts(),
            {
                "activated_existing_registry_entities": 1,
                "adjacent_hced_dispositions": 3,
                "country_quarantine_additions": 0,
                "discovery_nonrating_twins": 2,
                "holds": 10,
                "identity_window_changes": 0,
                "new_aliases": 0,
                "new_event_bounded_entities": 5,
                "new_sources": 6,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "release_entity_additions": 6,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 0,
            },
        )
        metadata = lane.wave8_raichur_udayagiri_la_forbie_metadata()
        self.assertEqual(
            metadata["counts"],
            lane.wave8_raichur_udayagiri_la_forbie_counts(),
        )
        self.assertEqual(
            metadata["cohorts"],
            lane.wave8_raichur_udayagiri_la_forbie_cohort_counts(),
        )
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS),
        )
        self.assertEqual(
            metadata["hold_candidate_ids"],
            sorted(lane.WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS),
        )


if __name__ == "__main__":
    unittest.main()
