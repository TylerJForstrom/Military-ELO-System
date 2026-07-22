import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_lower_canada as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import (
    expected_exact_hced_win_participants,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_lower_canada_"

CROWN = "lower_canada_crown_suppression_force_1837_1838"
SAINT_DENIS = "wolfred_nelson_saint_denis_force_1837"
SAINT_CHARLES = "thomas_storrow_brown_saint_charles_force_1837"
SAINT_EUSTACHE = "jean_olivier_chenier_saint_eustache_force_1837"
FRERES_CHASSEURS = "robert_nelson_freres_chasseurs_force_1838"

EXPECTED_HASHES = {
    "hced-Odelltown1838-1": (
        "644eb772027a9e7792adf559e91d8ca12956a829a6ab923bef0fcb90aca9df96"
    ),
    "hced-St Charles, Quebec1837-1": (
        "f668d63b5a94ced666576e36d99b88bea4ea183f4975da88297b8c5d26a93df0"
    ),
    "hced-St Denis, Quebec1837-1": (
        "6fb079ad496b4510d7c1e3fbac32a503462d8b8487340792fb90743e70b673de"
    ),
    "hced-St Eustache1837-1": (
        "0e5934860263ed51760fa0e9e7315d02cc1ed485d70b4760115f86557705a16e"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q2888006": (
        "017680f57e11d5a5cf7147e72f683d165dff76547b9beb19656bc790887f3860"
    ),
    "Q2889850": (
        "fcec2ee76c9450ed4c9ca29c80068a91d77ba0ffd9720c4c05474d07c8b91fb1"
    ),
    "Q2889862": (
        "4f5bd2157d311183adc4e15196801784195631fd8c70c40163b46759db294177"
    ),
    "Q862220": (
        "f818f33589748893106c806ffd2d18e9cce6bdb25e00ce143263f88c0edb6736"
    ),
}

EXPECTED_ACTORS = {
    "hced-Odelltown1838-1": ([CROWN], [FRERES_CHASSEURS]),
    "hced-St Charles, Quebec1837-1": ([CROWN], [SAINT_CHARLES]),
    "hced-St Denis, Quebec1837-1": ([SAINT_DENIS], [CROWN]),
    "hced-St Eustache1837-1": ([CROWN], [SAINT_EUSTACHE]),
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


def _contains_mapping(value, expected):
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(_contains_mapping(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(_contains_mapping(item, expected) for item in value)
    return False


class Wave8LowerCanadaTests(unittest.TestCase):
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
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_LOWER_CANADA_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_LOWER_CANADA_SOURCES
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
            not in lane.WAVE8_LOWER_CANADA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_lower_canada_entities(entities)
        lane.install_wave8_lower_canada_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_lower_canada_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_queue_inventory_semantic_hashes_and_raw_results_are_pinned(
        self,
    ) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "quebecois rebels"
            or normalize_label(row.get("side_2_raw")) == "quebecois rebels"
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(lane.WAVE8_LOWER_CANADA_ROW_HASHES, EXPECTED_HASHES)
        by_id = {str(row["candidate_id"]): row for row in exact}
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(row["scale_raw"], "1")
                self.assertNotIn(
                    normalize_label(row["winner_raw"]),
                    {"draw", "inconclusive", "stalemate", "unknown"},
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_lower_canada_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
            },
        )
        funnel_rows = [
            row
            for row in self.funnel.get("labels", [])
            if row.get("label") == "quebecois rebels"
        ]
        if funnel_rows:
            self.assertEqual(
                lane.validate_wave8_lower_canada_funnel(self.funnel),
                {
                    "events_touched": 4,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 4,
                    "zero_time_valid_candidates": 4,
                },
            )
        else:
            owned = {
                event.get("hced_candidate_id")
                for event in self.release_events
                if event.get("hced_candidate_id")
                in lane.WAVE8_LOWER_CANADA_CONTRACT_IDS
            }
            self.assertEqual(owned, lane.WAVE8_LOWER_CANADA_CONTRACT_IDS)
            self.assertTrue(
                _contains_mapping(
                    self.release_metadata.get("promotion", {}),
                    lane.WAVE8_LOWER_CANADA_FUNNEL_AUDIT,
                )
            )

    def test_contracts_pin_exact_days_sides_and_source_aligned_wins(self) -> None:
        expected = {
            "hced-Odelltown1838-1": (
                "Battle of Odelltown",
                1838,
                "9 November 1838",
                "1838-11-09",
                "lower_canada_rebellion_1838",
            ),
            "hced-St Charles, Quebec1837-1": (
                "Battle of Saint-Charles",
                1837,
                "25 November 1837",
                "1837-11-25",
                "lower_canada_rebellion_1837",
            ),
            "hced-St Denis, Quebec1837-1": (
                "Battle of Saint-Denis",
                1837,
                "23 November 1837",
                "1837-11-23",
                "lower_canada_rebellion_1837",
            ),
            "hced-St Eustache1837-1": (
                "Battle of Saint-Eustache",
                1837,
                "14 December 1837",
                "1837-12-14",
                "lower_canada_rebellion_1837",
            ),
        }
        self.assertEqual(lane.WAVE8_LOWER_CANADA_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_LOWER_CANADA_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_LOWER_CANADA_HOLDS)
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_LOWER_CANADA_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            name, year, date_text, exact_date, cohort = values
            self.assertEqual(canonical["name"], name)
            self.assertEqual(canonical["canonical_key"], f"{normalize_label(name).replace(' ', '_')}:{year}:{year}")
            self.assertEqual(canonical["date_text"], date_text)
            self.assertEqual(canonical["start_date"], exact_date)
            self.assertEqual(canonical["end_date"], exact_date)
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(
                canonical["granularity"],
                "single_battle_in_lower_canada_rebellion",
            )
            self.assertEqual(contract["cohort"], cohort)
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
            self.assertEqual(contract["expected_scale_level"], 1)
            self.assertEqual(
                contract["parent_conflict_id"],
                "lower_canada_rebellions_1837_1838",
            )
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertFalse(contract["source_date_override"])

    def test_entities_are_alias_free_event_or_conflict_bounded_actors(self) -> None:
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_LOWER_CANADA_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {
                CROWN,
                SAINT_DENIS,
                SAINT_CHARLES,
                SAINT_EUSTACHE,
                FRERES_CHASSEURS,
            },
        )
        self.assertEqual(
            (entities[CROWN]["start_year"], entities[CROWN]["end_year"]),
            (1837, 1838),
        )
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertTrue(entity["source_ids"])
                Entity.from_dict(entity)
        normalized_names = {
            normalize_label(alias)
            for entity in entities.values()
            for alias in entity["aliases"]
        }
        self.assertFalse(
            normalized_names
            & {
                "canada",
                "parti canadien",
                "parti patriote",
                "patriote movement",
                "quebecois rebels",
                "united kingdom",
            }
        )

    def test_source_provenance_is_closed_and_independently_familied(self) -> None:
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_LOWER_CANADA_SOURCES
        }
        self.assertEqual(len(sources), 13)
        self.assertEqual(
            {source["source_family_id"] for source in sources.values()},
            {
                "canadian_military_history_battle_series",
                "dictionary_canadian_biography",
                "lower_canada_state_trials_1839",
                "parks_canada_saint_eustache",
                "quebec_cultural_heritage_lower_canada_rebellions",
                "veterans_affairs_canada_odelltown",
            },
        )
        used = set()
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
        for candidate_id, contract in lane.WAVE8_LOWER_CANADA_CONTRACTS.items():
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
        self.assertEqual(used, set(sources))

    def test_emitted_events_have_exact_tactical_participant_polarity(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_HASHES))
        for candidate_id, event in events.items():
            contract = lane.WAVE8_LOWER_CANADA_CONTRACTS[candidate_id]
            expected = expected_exact_hced_win_participants(
                *EXPECTED_ACTORS[candidate_id],
                confidence=0.96,
                scale_level=1,
                lane_name="Wave 8 exact Lower Canada Rebellion audit",
            )
            self.assertEqual(event["participants"], expected)
            self.assertEqual(
                [participant["termination"] for participant in event["participants"]],
                ["engagement_victory", "engagement_defeat"],
            )
            self.assertEqual(event["name"], contract["canonical_event"]["name"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "internal_rebellion")
            self.assertEqual(event["scale"], "skirmish")
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(event["confidence"], 0.96)
            self.assertEqual(
                event["reviewed_granularity"],
                "single_battle_in_lower_canada_rebellion",
            )
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            Event.from_dict(event)

    def test_no_state_or_political_shortcut_is_a_rated_participant(self) -> None:
        participant_ids = {
            participant["entity_id"]
            for event in self._events()
            for participant in event["participants"]
        }
        self.assertEqual(
            participant_ids,
            {
                CROWN,
                SAINT_DENIS,
                SAINT_CHARLES,
                SAINT_EUSTACHE,
                FRERES_CHASSEURS,
            },
        )
        self.assertFalse(
            participant_ids
            & {
                "ca_canada_dominion",
                "gb_british_emp_1",
                "united_kingdom",
                "canada",
                "parti_canadien",
                "parti_patriote",
            }
        )

    def test_all_points_are_withheld_but_canada_and_provenance_are_retained(
        self,
    ) -> None:
        self.assertEqual(
            lane.WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_LOWER_CANADA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_LOWER_CANADA_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_LOWER_CANADA_CONTRACT_IDS,
        )
        self.assertEqual(
            lane.wave8_lower_canada_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_LOWER_CANADA_CONTRACT_IDS,
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Canada")
            self.assertIn("location_provenance", event)

    def test_wikidata_twins_are_discovery_only_unknowns_never_draws(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        self.assertEqual(
            lane.WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(_full_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["winners"], [])
                self.assertEqual(
                    lane.WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED[candidate_id][
                        "outcome_disposition"
                    ],
                    "unknown_never_draw",
                )
        self.assertEqual(
            lane.validate_wave8_lower_canada_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_twins": 4,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 4,
            },
        )
        self.assertEqual(
            lane.WAVE8_LOWER_CANADA_DISCOVERY_TWINS,
            {
                "hced-Odelltown1838-1": "Q2888006",
                "hced-St Charles, Quebec1837-1": "Q2889850",
                "hced-St Denis, Quebec1837-1": "Q2889862",
                "hced-St Eustache1837-1": "Q862220",
            },
        )

    def test_cross_source_twins_and_current_artifact_state_are_fail_closed(
        self,
    ) -> None:
        owned_count = sum(
            event.get("hced_candidate_id")
            in lane.WAVE8_LOWER_CANADA_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_lower_canada_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "discovery_nonrating_dispositions": 4,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        artifact = lane.validate_wave8_lower_canada_current_artifact_state(
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
            lane.validate_wave8_lower_canada_current_artifact_state(
                events,
                list(entities.values()),
                list(sources.values()),
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 5,
                "installed_sources": 13,
                "promoted_events": 4,
            },
        )

        tampered = copy.deepcopy(events)
        tampered[0]["participants"][0]["termination"] = "engagement_defeat"
        with self.assertRaisesRegex(ValueError, "participant drift"):
            lane.validate_wave8_lower_canada_current_artifact_state(
                tampered,
                list(entities.values()),
                list(sources.values()),
            )

    def test_queue_row_drift_extra_label_and_duplicate_promotion_fail_closed(
        self,
    ) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Odelltown1838-1"
        )
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_lower_canada_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-Odelltown1838-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_lower_canada_queue_contracts(duplicated)

        future_label = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-quebecois",
                "side_1_raw": "Quebecois Rebels",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_lower_canada_queue_contracts(future_label)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_lower_canada_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_lower_canada_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_missing_identity_collisions_and_partial_artifacts_fail_closed(
        self,
    ) -> None:
        entities, sources, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(CROWN)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_lower_canada_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        colliding_entities = copy.deepcopy(entities)
        colliding_entities[CROWN]["name"] = "drifted actor"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_lower_canada_entities(colliding_entities)

        colliding_sources = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_LOWER_CANADA_SOURCES[0]["id"])
        colliding_sources[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_lower_canada_sources(colliding_sources)

        events = self._events()
        with self.assertRaisesRegex(ValueError, "partial"):
            lane.validate_wave8_lower_canada_current_artifact_state(
                events[:1],
                list(entities.values()),
                list(sources.values()),
            )

    def test_installers_are_atomic_when_a_late_fixture_collides(self) -> None:
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_LOWER_CANADA_ENTITIES
        }
        entities = {
            "preexisting": {
                "id": "preexisting",
                "name": "Preexisting",
                "kind": "test",
                "start_year": 1,
            },
            FRERES_CHASSEURS: {
                **copy.deepcopy(
                    next(
                        entity
                        for entity in lane.WAVE8_LOWER_CANADA_ENTITIES
                        if entity["id"] == FRERES_CHASSEURS
                    )
                ),
                "name": "collision",
            },
        }
        before_entities = copy.deepcopy(entities)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_lower_canada_entities(entities)
        self.assertEqual(entities, before_entities)
        self.assertFalse((set(entities) & lane_entity_ids) - {FRERES_CHASSEURS})

        last_source = str(lane.WAVE8_LOWER_CANADA_SOURCES[-1]["id"])
        sources = {
            last_source: {
                **copy.deepcopy(lane.WAVE8_LOWER_CANADA_SOURCES[-1]),
                "title": "collision",
            }
        }
        before_sources = copy.deepcopy(sources)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_lower_canada_sources(sources)
        self.assertEqual(sources, before_sources)

    def test_discovery_drift_and_invented_winner_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.wikidata_rows)
        row = next(item for item in tampered if item.get("candidate_id") == "Q2888006")
        row["winners"] = [
            {
                "label": "United Kingdom of Great Britain and Ireland",
                "uri": "http://www.wikidata.org/entity/Q174193",
            }
        ]
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_lower_canada_discovery_dispositions(tampered)

        duplicated = copy.deepcopy(self.wikidata_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.wikidata_rows
                    if row.get("candidate_id") == "Q2888006"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "expected once"):
            lane.validate_wave8_lower_canada_discovery_dispositions(duplicated)

    def test_future_iwd_iwbd_hced_and_release_twins_fail_closed(self) -> None:
        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-odelltown-twin",
                "name": "Battle of Odelltown",
                "year_best": 1838,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_lower_canada_integration_dispositions(
                future_hced,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwd = [
            *copy.deepcopy(self.iwd_rows),
            {
                "candidate_id": "iwd-future-saint-charles",
                "name": "Battle of Saint-Charles",
                "year": 1837,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_lower_canada_integration_dispositions(
                self.hced_rows,
                future_iwd,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-saint-eustache",
                "name": "Battle of Saint-Eustache",
                "start_date": "1837-12-14",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_lower_canada_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_saint_denis_twin",
                "name": "Battle of Saint-Denis",
                "year": 1837,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_lower_canada_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_the_1567_saint_denis_release_namesake_is_not_a_twin(self) -> None:
        namesakes = [
            event
            for event in self.release_events
            if normalize_label(event.get("name")) == "battle of saint denis"
            and event.get("hced_candidate_id")
            not in lane.WAVE8_LOWER_CANADA_CONTRACT_IDS
        ]
        self.assertTrue(namesakes)
        self.assertTrue(all(int(event["year"]) != 1837 for event in namesakes))
        result = lane.validate_wave8_lower_canada_integration_dispositions(
            self.hced_rows,
            self.iwd_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(result["existing_release_probable_twins"], 0)

    def test_counts_metadata_signature_and_dispositions_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_lower_canada_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_twins": 4,
                "holds": 0,
                "integration_dispositions": 4,
                "new_entities": 5,
                "new_sources": 13,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 4,
            },
        )
        self.assertEqual(
            lane.wave8_lower_canada_cohort_counts(),
            {
                "lower_canada_rebellion_1837": 3,
                "lower_canada_rebellion_1838": 1,
            },
        )
        self.assertEqual(
            lane.wave8_lower_canada_audit_signature(),
            lane.WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_lower_canada_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_lower_canada_counts())
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(EXPECTED_HASHES))
        self.assertEqual(
            metadata["discovery_nonrating_candidate_ids"],
            sorted(EXPECTED_DISCOVERY_HASHES),
        )
        self.assertFalse(metadata["hold_candidate_ids"])
        for discovery_id, disposition in (
            lane.WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS.items()
        ):
            self.assertIn(discovery_id, EXPECTED_DISCOVERY_HASHES)
            self.assertEqual(disposition["disposition"], "discovery_only_duplicate")
            self.assertEqual(
                disposition["outcome_disposition"],
                "unknown_never_draw",
            )


if __name__ == "__main__":
    unittest.main()
