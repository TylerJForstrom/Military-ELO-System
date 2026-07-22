import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_honduran_rebels as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import (
    expected_exact_hced_win_participants,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_honduran_rebels_"

HONDURAS = "clio_q783_1840_cd44c8fd"
DANLI_GOVERNMENT = "ferrera_division_of_operations_danli_1844"
DANLI_LIBERATOR = "patricio_jimenez_liberator_division_danli_1844"
ORTIZ_EXPEDITION = "anastasio_ortiz_nicaraguan_expedition_1893_1894"
BONILLA_LIBERALS = "policarpo_bonilla_liberal_revolutionary_force_1893_1894"
VASQUEZ_DEFENDERS = "domingo_vasquez_tegucigalpa_defense_force_1894"
REVOLUTIONARY_COLUMNS_1924 = (
    "ferrera_tosta_martinez_funes_tegucigalpa_force_1924"
)
COUNCIL_DEFENDERS_1924 = (
    "council_of_ministers_tegucigalpa_defense_force_1924"
)

EXPECTED_HASHES = {
    "hced-Choluteca1894-1": (
        "a56d0d5710c6179db1bed371af4792c01db969757a518c9577428c3ac1b9ea71"
    ),
    "hced-Danli1844-1": (
        "c78a8296542fdb0c6c54bf49cee1243ca7cb428c8249062e706717286e80b9fe"
    ),
    "hced-San Marcos, Honduras1876-1": (
        "925128e76d54310d6d22fdc18e26b66e80801169d19e0fd4e29c24759bb3afcb"
    ),
    "hced-Tegucicalpa1894-1": (
        "07be61d8d8887f09cf4957f4e0113d72fafbdf3a2aa7be0e318e53caf181edc8"
    ),
    "hced-Tegucicalpa1924-1": (
        "11d7a09cf923c6278be801f9fba863841277ac4521caa7213657b24a49b319f2"
    ),
}
EXPECTED_HCED_DISCOVERY_HASHES = {
    "hced-La Esperanza1876-1": (
        "c67368cdc6a33be130b03bd68495cb44694183fcab127a57c2e4922d73a38e3e"
    )
}
EXPECTED_IWBD_DISCOVERY_HASHES = {
    "iwbd-60-21-271": (
        "bd8188b8687536e2672d7e7ef59518e3b8b25ea71ea259029812d870b8a0439a"
    ),
    "iwbd-60-21-272": (
        "a9be2ea59c1e0e3ed32f82943834b594571621fb9c7f7f124e519effcb51a25d"
    ),
}
EXPECTED_PARENT_HASHES = {
    "brecke-2299": (
        "3d2439fb92ebabb9476ae34ed8115ce588b2bdfc515362fba7a1dae4f4803175"
    ),
    "brecke-3146": (
        "81264bcbaba8be51abfe84e291e6f867c0e8bd3477f819ac5cbe787dc0a9feb2"
    ),
}

EXPECTED_ACTORS = {
    "hced-Danli1844-1": ([DANLI_GOVERNMENT], [DANLI_LIBERATOR]),
    "hced-Tegucicalpa1894-1": (
        [ORTIZ_EXPEDITION, BONILLA_LIBERALS],
        [VASQUEZ_DEFENDERS],
    ),
    "hced-Tegucicalpa1924-1": (
        [REVOLUTIONARY_COLUMNS_1924],
        [COUNCIL_DEFENDERS_1924],
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


class Wave8HonduranRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd_rows = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.brecke_rows = _jsonl(ROOT / "data/reference/brecke-wars.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"])
            for entity in lane.WAVE8_HONDURAN_REBELS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"])
            for source in lane.WAVE8_HONDURAN_REBELS_SOURCES
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
            not in lane.WAVE8_HONDURAN_REBELS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_honduran_rebels_entities(entities)
        lane.install_wave8_honduran_rebels_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_honduran_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_two_label_inventory_row_hashes_and_dispositions_are_pinned(
        self,
    ) -> None:
        audited_labels = {"honduran rebels", "nicaragua honduran rebels"}
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) in audited_labels
            or normalize_label(row.get("side_2_raw")) in audited_labels
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(lane.WAVE8_HONDURAN_REBELS_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS,
            {
                "hced-Danli1844-1",
                "hced-Tegucicalpa1894-1",
                "hced-Tegucicalpa1924-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_HOLD_IDS,
            {
                "hced-Choluteca1894-1",
                "hced-San Marcos, Honduras1876-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        by_id = {str(row["candidate_id"]): row for row in exact}
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(row["modern_location_country"], "Honduras")
                self.assertEqual(row["theatre_raw"], "Land")

    def test_queue_and_both_historical_funnel_rows_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_queue_contracts(self.hced_rows),
            {
                "audited_label_rows": 5,
                "audited_labels": 2,
                "holds": 2,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 5,
            },
        )
        historical = {
            "labels": [
                copy.deepcopy(audit)
                for audit in lane.WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS.values()
            ]
        }
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_funnel(historical),
            {
                "audited_labels": 2,
                "events_touched": 5,
                "sole_blocker_events": 4,
                "unresolved_side_attempts": 5,
                "zero_time_valid_candidates": 5,
            },
        )
        live_labels = {
            str(row.get("label")) for row in self.funnel.get("labels", [])
        }
        self.assertTrue(
            set(lane.WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS).isdisjoint(live_labels)
        )
        self.assertEqual(
            {
                label: audit["event_candidate_id_sha256"]
                for label, audit in lane.WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS.items()
            },
            {
                "honduran rebels": (
                    "9a5e364cbe3cb795aa6211b084c9ef26afc3f6ebde627a54215f6ea874f1708b"
                ),
                "nicaragua honduran rebels": (
                    "8f7255804d49d90e81cad91277a71a702b082a94578022d32196ea002079195d"
                ),
            },
        )

    def test_promotions_pin_dates_granularity_sides_and_winners(self) -> None:
        expected = {
            "hced-Danli1844-1": (
                "Battle of Danlí",
                "battle_of_danli:1844:1844",
                "20 December 1844",
                "1844-12-20",
                "1844-12-20",
                "day",
                "single_decisive_battle",
                "internal_rebellion",
            ),
            "hced-Tegucicalpa1894-1": (
                "Siege and capture of Tegucigalpa",
                "siege_and_capture_of_tegucigalpa:1894:1894",
                "23 January-22 February 1894",
                "1894-01-23",
                "1894-02-22",
                "day_range",
                "siege_and_capital_capture",
                "intrastate_with_foreign_intervention",
            ),
            "hced-Tegucicalpa1924-1": (
                "Final assault and capture of Tegucigalpa",
                "final_assault_and_capture_of_tegucigalpa:1924:1924",
                "27-28 April 1924",
                "1924-04-27",
                "1924-04-28",
                "day_range",
                "terminal_urban_assault_and_capital_capture",
                "civil_war",
            ),
        }
        for candidate_id, values in expected.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_HONDURAN_REBELS_CONTRACTS[candidate_id]
                canonical = contract["canonical_event"]
                self.assertEqual(
                    (
                        canonical["name"],
                        canonical["canonical_key"],
                        canonical["date_text"],
                        canonical["start_date"],
                        canonical["end_date"],
                        canonical["date_precision"],
                        canonical["granularity"],
                        contract["war_type"],
                    ),
                    values,
                )
                self.assertEqual(
                    (
                        contract["side_1_entity_ids"],
                        contract["side_2_entity_ids"],
                    ),
                    EXPECTED_ACTORS[candidate_id],
                )
                self.assertEqual(contract["winner_side"], 1)
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["confidence"], 0.96)
                self.assertEqual(contract["expected_scale_level"], 2)
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertFalse(contract["source_date_override"])

    def test_choluteca_and_san_marcos_are_unknown_never_draw_holds(self) -> None:
        choluteca = lane.WAVE8_HONDURAN_REBELS_HOLDS[
            "hced-Choluteca1894-1"
        ]
        self.assertEqual(
            choluteca["hold_category"],
            (
                "year_place_row_collapses_multiple_actions_and_source_outcome_"
                "contradiction"
            ),
        )
        self.assertEqual(
            [
                (
                    item["name"],
                    item["start_date"],
                    item["end_date"],
                    item["reviewed_outcome"],
                )
                for item in choluteca["reviewed_components"]
            ],
            [
                (
                    "Siege and capture of Choluteca",
                    "1893-12-30",
                    "1894-01-03",
                    "liberal_nicaraguan_victory",
                ),
                (
                    "Second Battle of Choluteca",
                    "1894-01-15",
                    "1894-01-17",
                    "liberal_nicaraguan_victory",
                ),
            ],
        )
        san_marcos = lane.WAVE8_HONDURAN_REBELS_HOLDS[
            "hced-San Marcos, Honduras1876-1"
        ]
        self.assertEqual(
            san_marcos["hold_category"],
            "unresolved_san_marcos_naranjo_identity_and_date_conflict",
        )
        self.assertEqual(
            [item["date"] for item in san_marcos["date_candidates"]],
            ["1876-02-13", "1876-02-14", "1876-02-22"],
        )
        for candidate_id, hold in lane.WAVE8_HONDURAN_REBELS_HOLDS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(hold["disposition"], "hold")
                self.assertEqual(hold["reviewed_outcome"], "unknown")
                self.assertEqual(hold["result_type"], "unknown")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertNotIn("winner_side", hold)
                self.assertIn("never a draw", hold["hold_reason"])
                self.assertNotIn(
                    candidate_id,
                    {event["hced_candidate_id"] for event in self._events()},
                )

    def test_seven_identities_are_exact_alias_free_and_bounded(self) -> None:
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_HONDURAN_REBELS_ENTITIES
        }
        expected = {
            DANLI_GOVERNMENT: (
                "Ferrera government Division of Operations at Danlí",
                1844,
                1844,
            ),
            DANLI_LIBERATOR: (
                "Patricio Jiménez’s Ejército Libertador division at Danlí",
                1844,
                1844,
            ),
            ORTIZ_EXPEDITION: (
                "Nicaraguan expeditionary force under Anastasio Ortiz in Honduras",
                1893,
                1894,
            ),
            BONILLA_LIBERALS: (
                "Policarpo Bonilla’s Honduran Liberal revolutionary force",
                1893,
                1894,
            ),
            VASQUEZ_DEFENDERS: (
                "Domingo Vásquez government force defending Tegucigalpa",
                1894,
                1894,
            ),
            REVOLUTIONARY_COLUMNS_1924: (
                "Ferrera–Tosta–Martínez Funes revolutionary columns at Tegucigalpa",
                1924,
                1924,
            ),
            COUNCIL_DEFENDERS_1924: (
                "Council of Ministers loyalist defense force at Tegucigalpa",
                1924,
                1924,
            ),
        }
        self.assertEqual(set(entities), set(expected))
        for entity_id, (name, start, end) in expected.items():
            with self.subTest(entity_id=entity_id):
                entity = entities[entity_id]
                self.assertEqual(
                    (entity["name"], entity["start_year"], entity["end_year"]),
                    (name, start, end),
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertTrue(entity["source_ids"])
                self.assertIn("no rating", entity["continuity_note"].casefold())
                Entity.from_dict(entity)
        self.assertEqual(
            {
                normalize_label(alias)
                for entity in entities.values()
                for alias in entity["aliases"]
            },
            set(),
        )

    def test_existing_honduras_and_broad_alias_boundaries_are_unchanged(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        self.assertEqual(
            {
                key: entities[HONDURAS].get(key)
                for key in ("name", "kind", "start_year", "end_year", "aliases")
            },
            lane.WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES[HONDURAS],
        )
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_existing_entities(entities),
            {"required_existing_entities": 1},
        )
        self.assertNotIn("honduran rebels", HCED_LABEL_POLICIES)
        self.assertNotIn("honduran government", HCED_LABEL_POLICIES)
        self.assertNotIn("nicaragua honduran rebels", HCED_LABEL_POLICIES)
        broad = {
            normalize_label(alias)
            for entity in self.release_entities
            for alias in entity.get("aliases", []) or []
        }
        self.assertFalse(
            broad
            & {
                "honduran rebels",
                "honduran government",
                "nicaragua honduran rebels",
            }
        )

    def test_eleven_sources_ten_families_and_outcome_closure_are_pinned(self) -> None:
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_HONDURAN_REBELS_SOURCES
        }
        expected_families = {
            "bancroft_central_america",
            "becerra_honduran_history",
            "honduras_secapph",
            "sedesol_chepes_1924",
            "ucr_intercambio",
            "unah_archival_facsimiles",
            "unah_departmental_monographs",
            "us_navy_expedition_records",
            "us_state_frus_1894",
            "us_state_frus_1924",
        }
        self.assertEqual(len(sources), 11)
        self.assertEqual(
            {source["source_family_id"] for source in sources.values()},
            expected_families,
        )
        for source in sources.values():
            self.assertTrue(source["url"].startswith("https://"))
            Source.from_dict(source)
        used = set()
        for candidate_id, contract in lane.WAVE8_HONDURAN_REBELS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                evidence = contract["evidence_refs"]
                outcomes = contract["outcome_source_ids"]
                dates = contract["date_source_ids"]
                self.assertEqual(evidence, sorted(set(evidence)))
                self.assertEqual(outcomes, sorted(set(outcomes)))
                self.assertEqual(dates, sorted(set(dates)))
                self.assertTrue(set(outcomes) <= set(evidence))
                self.assertTrue(set(dates) <= set(evidence))
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]),
                    2,
                )
                self.assertEqual(set(contract["event_evidence_roles"]), set(evidence))
                for source_id in outcomes:
                    self.assertIn("outcome", sources[source_id]["evidence_roles"])
                used.update(evidence)
        for hold in lane.WAVE8_HONDURAN_REBELS_HOLDS.values():
            used.update(hold["evidence_refs"])
        self.assertEqual(used, set(sources))

    def test_emissions_have_exact_tactical_polarity_and_only_seven_actors(
        self,
    ) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS)
        participant_ids = set()
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_HONDURAN_REBELS_CONTRACTS[candidate_id]
                expected = expected_exact_hced_win_participants(
                    *EXPECTED_ACTORS[candidate_id],
                    confidence=0.96,
                    scale_level=2,
                    lane_name="Wave 8 exact Honduran rebels audit",
                )
                self.assertEqual(event["participants"], expected)
                self.assertEqual(
                    {participant["termination"] for participant in event["participants"]},
                    {"engagement_victory", "engagement_defeat"},
                )
                participant_ids.update(
                    participant["entity_id"] for participant in event["participants"]
                )
                self.assertEqual(event["name"], contract["canonical_event"]["name"])
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], contract["war_type"])
                self.assertEqual(event["scale"], "battle")
                self.assertEqual(
                    event["date_precision"],
                    contract["canonical_event"]["date_precision"],
                )
                self.assertEqual(
                    event["reviewed_granularity"],
                    contract["canonical_event"]["granularity"],
                )
                self.assertEqual(event["confidence"], 0.96)
                self.assertEqual(event["source_ids"][0], "hced_dataset")
                self.assertEqual(
                    event["outcome_source_ids"],
                    contract["outcome_source_ids"],
                )
                self.assertEqual(
                    event["outcome_source_family_ids"],
                    contract["outcome_source_family_ids"],
                )
                Event.from_dict(event)
        self.assertEqual(
            participant_ids,
            {
                DANLI_GOVERNMENT,
                DANLI_LIBERATOR,
                ORTIZ_EXPEDITION,
                BONILLA_LIBERALS,
                VASQUEZ_DEFENDERS,
                REVOLUTIONARY_COLUMNS_1924,
                COUNCIL_DEFENDERS_1924,
            },
        )
        self.assertNotIn(HONDURAS, participant_ids)
        self.assertNotIn("united_states", participant_ids)

    def test_1924_united_states_token_is_explicitly_non_belligerent(self) -> None:
        contract = lane.WAVE8_HONDURAN_REBELS_CONTRACTS[
            "hced-Tegucicalpa1924-1"
        ]
        self.assertEqual(
            contract["excluded_participant_labels"],
            ["The United States", "United States"],
        )
        self.assertIn(
            "united_states_non_belligerent_boundary",
            contract["event_evidence_roles"][
                "wave8_honduran_rebels_us_navy_expeditions_1901_1929"
            ],
        )
        event = next(
            event
            for event in self._events()
            if event["hced_candidate_id"] == "hced-Tegucicalpa1924-1"
        )
        self.assertNotIn(
            "united_states",
            {participant["entity_id"] for participant in event["participants"]},
        )

    def test_three_points_are_withheld_and_no_country_is_quarantined(self) -> None:
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        )
        self.assertEqual(
            set(lane.WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS,
        )
        self.assertEqual(
            lane.wave8_honduran_rebels_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS,
            },
        )
        expected_points = {
            "hced-Danli1844-1": [-86.5703554, 14.0410953],
            "hced-Tegucicalpa1894-1": [-87.192136, 14.0722751],
            "hced-Tegucicalpa1924-1": [-87.192136, 14.0722751],
        }
        for candidate_id, reason in (
            lane.WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS.items()
        ):
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(reason["raw_point"], expected_points[candidate_id])
            self.assertEqual(reason["retained_country"], "Honduras")
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Honduras")
            self.assertIn("location_provenance", event)

    def test_la_esperanza_and_iwbd_twins_are_fingerprinted_nonrating_records(
        self,
    ) -> None:
        hced_by_id = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HCED_DISCOVERY_HASHES
        }
        self.assertEqual(set(hced_by_id), set(EXPECTED_HCED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_HCED_DISCOVERY_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(hced_by_id[candidate_id]),
                expected_hash,
            )
        iwbd_by_id = {
            str(row["candidate_id"]): row
            for row in self.iwbd_rows
            if str(row.get("candidate_id")) in EXPECTED_IWBD_DISCOVERY_HASHES
        }
        self.assertEqual(set(iwbd_by_id), set(EXPECTED_IWBD_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_IWBD_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = iwbd_by_id[candidate_id]
                self.assertEqual(_full_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(
                    lane.WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED[candidate_id][
                        "outcome_disposition"
                    ],
                    "unknown_never_draw",
                )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS,
            {
                "hced-La Esperanza1876-1": "iwbd-60-21-271",
                "hced-San Marcos, Honduras1876-1": "iwbd-60-21-272",
            },
        )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS[
                "iwbd-60-21-272"
            ]["disposition"],
            "deduplicate_to_hced_review_hold",
        )

    def test_brecke_parent_rows_are_coverage_only_not_event_duplicates(self) -> None:
        by_id = {
            str(row["brecke_id"]): row
            for row in self.brecke_rows
            if str(row.get("brecke_id")) in EXPECTED_PARENT_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_PARENT_HASHES))
        for brecke_id, expected_hash in EXPECTED_PARENT_HASHES.items():
            with self.subTest(brecke_id=brecke_id):
                row = by_id[brecke_id]
                self.assertEqual(_full_row_sha256(row), expected_hash)
                self.assertFalse(row["outcome_available"])
                self.assertEqual(row["rating_use"], "coverage_cross_check_only")
                self.assertEqual(
                    lane.WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS[
                        brecke_id
                    ]["disposition"],
                    "coverage_only_parent_not_engagement_duplicate",
                )
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_parent_coverage(
                self.brecke_rows
            ),
            {
                "parent_coverage_records": 2,
                "parent_event_duplicates": 0,
                "parent_outcomes_used": 0,
            },
        )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED[
                "brecke-3146"
            ]["end_month"],
            3,
        )
        self.assertEqual(
            lane.WAVE8_HONDURAN_REBELS_CONTRACTS[
                "hced-Tegucicalpa1924-1"
            ]["canonical_event"]["start_date"],
            "1924-04-27",
        )

    def test_all_discovery_and_related_event_boundaries_are_explicit(self) -> None:
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_discovery_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.brecke_rows,
            ),
            {
                "discovery_nonrating_records": 5,
                "discovery_promotions": 0,
                "discovery_twins": 2,
                "hced_discovery_records": 1,
                "iwbd_discovery_records": 2,
                "parent_coverage_records": 2,
                "unknown_never_draw_rows": 3,
            },
        )
        boundaries = lane.WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES
        self.assertEqual(
            boundaries["choluteca_vs_tegucigalpa_1894"]["disposition"],
            "distinct_events_in_same_revolution",
        )
        self.assertEqual(
            boundaries["la_esperanza_vs_san_marcos_1876"]["disposition"],
            "distinct_earlier_and_later_actions",
        )
        self.assertEqual(
            boundaries["san_marcos_vs_naranjo_1876"]["disposition"],
            "identity_unresolved_review_hold",
        )
        emitted_ids = {event["hced_candidate_id"] for event in self._events()}
        self.assertFalse(
            emitted_ids
            & {
                "hced-La Esperanza1876-1",
                "hced-San Marcos, Honduras1876-1",
            }
        )

    def test_cross_source_inventory_and_current_artifact_state_fail_closed(
        self,
    ) -> None:
        owned_count = sum(
            event.get("hced_candidate_id")
            in lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.brecke_rows,
                self.release_events,
            ),
            {
                "discovery_nonrating_dispositions": 5,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_discovery_dispositions": 1,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_discovery_dispositions": 2,
                "iwbd_probable_twins": 0,
                "parent_coverage_dispositions": 2,
            },
        )
        artifact = lane.validate_wave8_honduran_rebels_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        self.assertEqual(artifact["promoted_events"], owned_count)
        self.assertEqual(
            artifact["artifact_state"],
            "integrated" if owned_count else "absent",
        )

    def test_emitted_artifact_projection_is_independently_validated(self) -> None:
        entities, sources, _ = self._installed()
        events = self._events()
        self.assertEqual(
            lane.validate_wave8_honduran_rebels_current_artifact_state(
                events,
                list(entities.values()),
                list(sources.values()),
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 7,
                "installed_sources": 11,
                "promoted_events": 3,
            },
        )
        tampered = copy.deepcopy(events)
        tampered[0]["participants"][0]["termination"] = "engagement_defeat"
        with self.assertRaisesRegex(ValueError, "participant drift"):
            lane.validate_wave8_honduran_rebels_current_artifact_state(
                tampered,
                list(entities.values()),
                list(sources.values()),
            )
        tampered = copy.deepcopy(events)
        tampered[0]["geometry"] = {"type": "Point", "coordinates": [0, 0]}
        with self.assertRaisesRegex(ValueError, "location drift"):
            lane.validate_wave8_honduran_rebels_current_artifact_state(
                tampered,
                list(entities.values()),
                list(sources.values()),
            )

    def test_queue_drift_extra_label_and_duplicate_promotion_fail_closed(
        self,
    ) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Danli1844-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_honduran_rebels_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-Tegucicalpa1894-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_honduran_rebels_queue_contracts(duplicated)

        future_label = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-honduran-rebels",
                "side_1_raw": "Honduran Rebels",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_honduran_rebels_queue_contracts(future_label)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_honduran_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_honduran_rebels_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_discovery_and_parent_fingerprint_drift_fail_closed(self) -> None:
        drifted_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(
            item
            for item in drifted_iwbd
            if item.get("candidate_id") == "iwbd-60-21-272"
        )
        row["winner_raw"] = "El Salvador (Medina)"
        with self.assertRaisesRegex(ValueError, "IWBD discovery fingerprint changed"):
            lane.validate_wave8_honduran_rebels_discovery_dispositions(
                self.hced_rows,
                drifted_iwbd,
                self.brecke_rows,
            )

        duplicate_hced = copy.deepcopy(self.hced_rows)
        duplicate_hced.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-La Esperanza1876-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "HCED discovery.*expected once"):
            lane.validate_wave8_honduran_rebels_discovery_dispositions(
                duplicate_hced,
                self.iwbd_rows,
                self.brecke_rows,
            )

        drifted_parent = copy.deepcopy(self.brecke_rows)
        parent = next(
            row for row in drifted_parent if row.get("brecke_id") == "brecke-3146"
        )
        parent["end_month"] = 4
        with self.assertRaisesRegex(ValueError, "parent coverage fingerprint changed"):
            lane.validate_wave8_honduran_rebels_parent_coverage(drifted_parent)

        duplicate_parent = copy.deepcopy(self.brecke_rows)
        duplicate_parent.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.brecke_rows
                    if row.get("brecke_id") == "brecke-2299"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "parent coverage.*expected once"):
            lane.validate_wave8_honduran_rebels_parent_coverage(duplicate_parent)

    def test_future_hced_iwd_iwbd_and_release_twins_fail_closed(self) -> None:
        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-danli-twin",
                "name": "Battle of Danlí",
                "year_best": 1844,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_honduran_rebels_integration_dispositions(
                future_hced,
                self.iwd_rows,
                self.iwbd_rows,
                self.brecke_rows,
                self.release_events,
            )

        future_iwd = [
            *copy.deepcopy(self.iwd_rows),
            {
                "candidate_id": "iwd-future-choluteca",
                "name": "Second Battle of Choluteca",
                "year": 1894,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_honduran_rebels_integration_dispositions(
                self.hced_rows,
                future_iwd,
                self.iwbd_rows,
                self.brecke_rows,
                self.release_events,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-tegucigalpa",
                "name": "Capture of Tegucigalpa",
                "start_date": "1924-04-28",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_honduran_rebels_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                future_iwbd,
                self.brecke_rows,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_naranjo_1876_twin",
                "name": "Battle of Naranjo",
                "year": 1876,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_honduran_rebels_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.brecke_rows,
                future_release,
            )

    def test_san_marcos_de_colon_1907_namesake_is_not_a_twin(self) -> None:
        namesakes = [
            event
            for event in self.release_events
            if "san marcos" in normalize_label(event.get("name"))
        ]
        self.assertTrue(
            any(
                normalize_label(event.get("name")) == "san marcos de colon"
                and int(event["year"]) == 1907
                for event in namesakes
            )
        )
        result = lane.validate_wave8_honduran_rebels_integration_dispositions(
            self.hced_rows,
            self.iwd_rows,
            self.iwbd_rows,
            self.brecke_rows,
            self.release_events,
        )
        self.assertEqual(result["existing_release_probable_twins"], 0)

    def test_identity_source_collisions_missing_actors_and_atomicity_fail_closed(
        self,
    ) -> None:
        entities, sources, existing = self._installed()
        missing_honduras = copy.deepcopy(entities)
        missing_honduras.pop(HONDURAS)
        with self.assertRaisesRegex(ValueError, "missing existing identity"):
            lane.promote_wave8_honduran_rebels_contracts(
                self.hced_rows,
                missing_honduras,
                existing,
            )

        missing_actor = copy.deepcopy(entities)
        missing_actor.pop(DANLI_GOVERNMENT)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_honduran_rebels_contracts(
                self.hced_rows,
                missing_actor,
                existing,
            )

        colliding_entities = copy.deepcopy(entities)
        colliding_entities[DANLI_GOVERNMENT]["name"] = "drifted actor"
        before_entities = copy.deepcopy(colliding_entities)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_honduran_rebels_entities(colliding_entities)
        self.assertEqual(colliding_entities, before_entities)

        colliding_sources = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_HONDURAN_REBELS_SOURCES[-1]["id"])
        colliding_sources[source_id]["title"] = "drifted title"
        before_sources = copy.deepcopy(colliding_sources)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_honduran_rebels_sources(colliding_sources)
        self.assertEqual(colliding_sources, before_sources)

    def test_partial_artifacts_and_broad_alias_injection_fail_closed(self) -> None:
        entities, sources, _ = self._installed()
        events = self._events()
        with self.assertRaisesRegex(ValueError, "partial"):
            lane.validate_wave8_honduran_rebels_current_artifact_state(
                events[:1],
                list(entities.values()),
                list(sources.values()),
            )

        partial_entities = [
            entity
            for entity_id, entity in entities.items()
            if entity_id != DANLI_LIBERATOR
        ]
        with self.assertRaisesRegex(ValueError, "partial"):
            lane.validate_wave8_honduran_rebels_current_artifact_state(
                events,
                partial_entities,
                list(sources.values()),
            )

        broad_alias = copy.deepcopy(entities)
        broad_alias[HONDURAS]["aliases"].append("Honduran Government")
        with self.assertRaisesRegex(ValueError, "existing identity drift"):
            lane.validate_wave8_honduran_rebels_existing_entities(broad_alias)

        unrelated_alias = copy.deepcopy(entities)
        unrelated_alias["united_states"]["aliases"].append("Honduran Rebels")
        with self.assertRaisesRegex(ValueError, "broad Honduran alias introduced"):
            lane.validate_wave8_honduran_rebels_existing_entities(unrelated_alias)

    def test_counts_cohorts_metadata_signature_and_idempotent_installers(self) -> None:
        entities, sources, _ = self._installed()
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_honduran_rebels_entities(entities)
        lane.install_wave8_honduran_rebels_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)

        expected_counts = {
            "country_quarantine_additions": 0,
            "discovery_nonrating_records": 5,
            "discovery_twins": 2,
            "hced_discovery_records": 1,
            "holds": 2,
            "integration_dispositions": 5,
            "iwbd_discovery_records": 2,
            "new_entities": 7,
            "new_source_families": 10,
            "new_sources": 11,
            "newly_rated_events": 3,
            "outcome_overrides": 0,
            "parent_coverage_records": 2,
            "point_quarantine_additions": 3,
            "promotion_contracts": 3,
            "reviewed_hced_rows": 5,
            "terminal_exclusions": 0,
            "unknown_discovery_outcomes": 3,
        }
        self.assertEqual(lane.wave8_honduran_rebels_counts(), expected_counts)
        self.assertEqual(
            lane.wave8_honduran_rebels_cohort_counts(),
            {
                "honduran_civil_war_1924": 1,
                "honduran_internal_conflict_1844": 1,
                "honduran_liberal_revolution_1893_1894": 2,
                "honduran_medina_revolt_1876": 1,
            },
        )
        self.assertEqual(
            lane.wave8_honduran_rebels_audit_signature(),
            lane.WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_honduran_rebels_metadata()
        self.assertEqual(metadata["counts"], expected_counts)
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS),
        )
        self.assertEqual(
            metadata["hold_candidate_ids"],
            sorted(lane.WAVE8_HONDURAN_REBELS_HOLD_IDS),
        )
        self.assertEqual(metadata["source_family_count"], 10)
        self.assertEqual(len(metadata["discovery_dispositions"]), 5)
        self.assertEqual(metadata["country_quarantine_candidate_ids"], [])
        self.assertEqual(
            metadata["point_quarantine_candidate_ids"],
            sorted(lane.WAVE8_HONDURAN_REBELS_CONTRACT_IDS),
        )


if __name__ == "__main__":
    unittest.main()
