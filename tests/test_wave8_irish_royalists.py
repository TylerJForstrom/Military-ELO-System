import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_irish_royalists as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_irish_royalists_"

DUNGAN_PARLIAMENTARIANS = "dungans_hill_parliamentarian_field_army_1647"
DUNGAN_CONFEDERATES = (
    "dungans_hill_confederate_leinster_redshank_force_1647"
)
CLONMEL_NEW_MODEL = "clonmel_new_model_army_siege_force_1650"
CLONMEL_GARRISON = "clonmel_ormond_aligned_ulster_garrison_1650"

EXPECTED_HASHES = {
    "hced-Clonmel1650-1": (
        "9ef0c7f42df58a29f9081dfb5cee76b5af19b0edfa885a24f64c13639db1540d"
    ),
    "hced-Dungan Hill1647-1": (
        "774169d7d2da48902968f03a05c2b72ed4875558f5e1aedee9b7506e52e4f9a2"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q494896": (
        "e283bbbd7894bc607ad261a8d8c25fa16d8b582b3134870f82f0b2a6b020e921"
    ),
    "Q815132": (
        "223794d7a350e3a27f244bde539beb4552add8b6fea0a46d6fac6b37f415a944"
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


class Wave8IrishRoyalistsTests(unittest.TestCase):
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
        entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_IRISH_ROYALISTS_ENTITIES
        }
        source_ids = {
            str(source["id"]) for source in lane.WAVE8_IRISH_ROYALISTS_SOURCES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in entity_ids
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_irish_royalists_entities(entities)
        lane.install_wave8_irish_royalists_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_irish_royalists_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_candidate_hashes_are_pinned(self):
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "irish royalists"
            or normalize_label(row.get("side_2_raw")) == "irish royalists"
        ]
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(len(exact), 2)
        self.assertEqual(lane.WAVE8_IRISH_ROYALISTS_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])

    def test_queue_and_historical_funnel_accounting_are_exact(self):
        self.assertEqual(
            lane.validate_wave8_irish_royalists_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 2,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        integrated_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        } & lane.WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
        if not integrated_ids:
            self.assertEqual(
                lane.validate_wave8_irish_royalists_funnel(self.funnel),
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
                    "wave8_irish_royalists_exact_label_funnel_audit"
                ],
                lane.WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT,
            )

    def test_contracts_pin_exact_dates_sides_and_outcomes(self):
        expected = {
            "hced-Dungan Hill1647-1": (
                "Battle of Dungan's Hill",
                "8 August 1647",
                "1647-08-08",
                "1647-08-08",
                "day",
                [DUNGAN_PARLIAMENTARIANS],
                [DUNGAN_CONFEDERATES],
                0.96,
            ),
            "hced-Clonmel1650-1": (
                "Siege of Clonmel",
                "27 April–18 May 1650",
                "1650-04-27",
                "1650-05-18",
                "day_range",
                [CLONMEL_NEW_MODEL],
                [CLONMEL_GARRISON],
                0.94,
            ),
        }
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_CONTRACT_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertFalse(lane.WAVE8_IRISH_ROYALISTS_HOLDS)
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_IRISH_ROYALISTS_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["start_date"],
                    canonical["end_date"],
                    canonical["date_precision"],
                    contract["side_1_entity_ids"],
                    contract["side_2_entity_ids"],
                    contract["confidence"],
                ),
                values,
            )
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_clonmel_is_full_siege_and_nested_assault_is_explicitly_excluded(self):
        contract = lane.WAVE8_IRISH_ROYALISTS_CONTRACTS["hced-Clonmel1650-1"]
        self.assertEqual(
            contract["canonical_event"]["granularity"],
            "full_siege_operation_excluding_nested_17_may_assault",
        )
        self.assertEqual(contract["nested_assault_date"], "1650-05-17")
        self.assertEqual(
            contract["nested_assault_disposition"],
            "excluded_constituent_defender_tactical_victory",
        )
        self.assertEqual(
            contract["full_siege_outcome_basis"],
            "town_surrendered_after_ormond_aligned_garrison_withdrawal",
        )
        self.assertIn("17 May assault", contract["audit_note"])
        self.assertIn("defender tactical victory", contract["audit_note"])
        events = self._events()
        self.assertEqual(len(events), 2)
        self.assertEqual(
            sum(event["name"] == "Siege of Clonmel" for event in events),
            1,
        )
        self.assertFalse(any("17 May" in event["name"] for event in events))

    def test_four_entities_are_alias_free_event_bounded_and_parse(self):
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_IRISH_ROYALISTS_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {
                DUNGAN_PARLIAMENTARIANS,
                DUNGAN_CONFEDERATES,
                CLONMEL_NEW_MODEL,
                CLONMEL_GARRISON,
            },
        )
        expected_years = {
            DUNGAN_PARLIAMENTARIANS: 1647,
            DUNGAN_CONFEDERATES: 1647,
            CLONMEL_NEW_MODEL: 1650,
            CLONMEL_GARRISON: 1650,
        }
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    (expected_years[entity_id], expected_years[entity_id]),
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("inherits no Elo", entity["continuity_note"])
                self.assertGreaterEqual(len(entity["source_ids"]), 2)
                Entity.from_dict(entity)

    def test_no_generic_royalist_parliamentarian_or_state_alias_is_created(self):
        forbidden = {
            "irish royalists",
            "parliamentarians",
            "commonwealth of england",
            "kingdom of england",
            "irish confederation",
            "new model army",
            "ulster army",
            "ireland",
        }
        aliases = {
            normalize_label(alias)
            for entity in lane.WAVE8_IRISH_ROYALISTS_ENTITIES
            for alias in entity["aliases"]
        }
        self.assertFalse(aliases)
        self.assertFalse(forbidden & aliases)
        participant_ids = {
            entity_id
            for contract in lane.WAVE8_IRISH_ROYALISTS_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertEqual(
            participant_ids,
            {entity["id"] for entity in lane.WAVE8_IRISH_ROYALISTS_ENTITIES},
        )

    def test_sources_parse_and_each_outcome_has_independent_families(self):
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_IRISH_ROYALISTS_SOURCES
        }
        self.assertEqual(len(sources), 5)
        self.assertEqual(len({source["source_family_id"] for source in sources.values()}), 5)
        for source in sources.values():
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
        consumed = set()
        for contract in lane.WAVE8_IRISH_ROYALISTS_CONTRACTS.values():
            self.assertEqual(
                contract["outcome_source_ids"],
                sorted(set(contract["outcome_source_ids"])),
            )
            self.assertEqual(contract["evidence_refs"], contract["outcome_source_ids"])
            self.assertEqual(contract["date_source_ids"], contract["outcome_source_ids"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                set(contract["event_evidence_roles"]),
                set(contract["outcome_source_ids"]),
            )
            consumed.update(contract["outcome_source_ids"])
        self.assertEqual(consumed, set(sources))

    def test_emitted_events_have_exact_winners_losers_and_no_draws(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Dungan Hill1647-1": (
                DUNGAN_PARLIAMENTARIANS,
                DUNGAN_CONFEDERATES,
            ),
            "hced-Clonmel1650-1": (CLONMEL_NEW_MODEL, CLONMEL_GARRISON),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winner, loser) in expected.items():
            event = events[candidate_id]
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                outcomes,
                {
                    winner: "engagement_victory",
                    loser: "engagement_defeat",
                },
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["scale"], "battle")
            self.assertFalse(
                any(
                    "inconclusive" in participant["termination"]
                    for participant in event["participants"]
                )
            )
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            Event.from_dict(event)

    def test_emission_validator_pins_all_four_participants(self):
        events = self._events()
        self.assertEqual(
            lane.validate_wave8_irish_royalists_emissions(events),
            {
                "events": 2,
                "participants": 4,
                "retained_countries": 1,
                "retained_points": 0,
            },
        )
        drifted = copy.deepcopy(events)
        drifted[0]["participants"][0]["termination"] = "inconclusive_engagement"
        with self.assertRaisesRegex(ValueError, "emitted contract drift"):
            lane.validate_wave8_irish_royalists_emissions(drifted)

    def test_location_quarantine_withholds_both_points_and_only_dungan_country(self):
        dungan = "hced-Dungan Hill1647-1"
        clonmel = "hced-Clonmel1650-1"
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS,
            {dungan, clonmel},
        )
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS,
            {dungan},
        )
        self.assertEqual(
            lane.wave8_irish_royalists_location_quarantine_additions(),
            {"country": {dungan}, "point": {dungan, clonmel}},
        )
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertNotIn("geometry", events[dungan])
        self.assertNotIn("modern_location_country", events[dungan])
        self.assertNotIn("location_provenance", events[dungan])
        self.assertNotIn("geometry", events[clonmel])
        self.assertEqual(events[clonmel]["modern_location_country"], "Ireland")
        self.assertIn("location_provenance", events[clonmel])
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS[dungan][
                "actions"
            ],
            ["withhold_country", "withhold_point"],
        )
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS[clonmel][
                "actions"
            ],
            ["withhold_point"],
        )

    def test_wikidata_twins_are_fingerprinted_discovery_only_unknowns(self):
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            row = by_id[candidate_id]
            self.assertEqual(_full_row_sha256(row), expected_hash)
            self.assertIs(row["do_not_rate_automatically"], True)
            self.assertEqual(row["winners"], [])
            self.assertEqual(
                lane.WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED[candidate_id][
                    "outcome_disposition"
                ],
                "unknown_never_draw",
            )
        self.assertEqual(
            lane.validate_wave8_irish_royalists_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_twins": 2,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 2,
            },
        )
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS,
            {
                "hced-Dungan Hill1647-1": "Q494896",
                "hced-Clonmel1650-1": "Q815132",
            },
        )

    def test_discovery_rows_cannot_supply_dates_or_rate_automatically(self):
        expected = lane.WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED
        self.assertIn("not_used", expected["Q494896"]["date_disposition"])
        self.assertIn("not_used", expected["Q815132"]["date_disposition"])
        self.assertNotEqual(
            expected["Q494896"]["date"],
            "1647-08-08T00:00:00Z",
        )
        self.assertEqual(
            lane.WAVE8_IRISH_ROYALISTS_CONTRACTS["hced-Dungan Hill1647-1"][
                "canonical_event"
            ]["start_date"],
            "1647-08-08",
        )
        emitted = self._events()
        self.assertTrue(
            all(event["hced_candidate_id"].startswith("hced-") for event in emitted)
        )
        self.assertFalse(
            any(
                source_id.startswith("Q")
                for event in emitted
                for source_id in event["source_ids"]
            )
        )

    def test_cross_source_twin_inventory_is_empty_and_future_twins_fail(self):
        owned_count = sum(
            event.get("hced_candidate_id")
            in lane.WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_irish_royalists_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "discovery_nonrating_dispositions": 2,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        fixtures = {
            "hced": (
                [
                    *copy.deepcopy(self.hced_rows),
                    {
                        "candidate_id": "hced-future-dungan-twin",
                        "name": "Dungan's Hill",
                        "year_low": 1647,
                    },
                ],
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            "iwd": (
                self.hced_rows,
                [
                    *copy.deepcopy(self.iwd_rows),
                    {
                        "candidate_id": "iwd-future-clonmel",
                        "name": "Siege of Clonmel",
                        "year": 1650,
                    },
                ],
                self.iwbd_rows,
                self.release_events,
            ),
            "iwbd": (
                self.hced_rows,
                self.iwd_rows,
                [
                    *copy.deepcopy(self.iwbd_rows),
                    {
                        "candidate_id": "iwbd-future-dungan",
                        "batname": "Battle of Dungan's Hill",
                        "batyear": 1647,
                    },
                ],
                self.release_events,
            ),
            "release": (
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                [
                    *copy.deepcopy(self.release_events),
                    {
                        "id": "future-clonmel-twin",
                        "name": "Clonmel",
                        "year": 1650,
                    },
                ],
            ),
        }
        for view, args in fixtures.items():
            with self.subTest(view=view):
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_irish_royalists_integration_dispositions(
                        *args
                    )

    def test_queue_fingerprint_extra_label_and_semantic_drift_fail_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item["candidate_id"] == "hced-Dungan Hill1647-1"
        )
        row["winner_raw"] = "Irish Royalists"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_irish_royalists_queue_contracts(tampered)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-irish-royalists",
                "side_1_raw": "Irish Royalists",
                "side_2_raw": "Unknown",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_irish_royalists_queue_contracts(future)

        def pinned_hash(candidate):
            candidate_id = str(candidate.get("candidate_id"))
            if candidate_id in EXPECTED_HASHES:
                return EXPECTED_HASHES[candidate_id]
            return canonical_hced_row_sha256(candidate)

        semantic = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in semantic
            if item["candidate_id"] == "hced-Clonmel1650-1"
        )
        row["winner_loser_complete"] = False
        with patch.object(
            lane,
            "canonical_hced_row_sha256",
            side_effect=pinned_hash,
        ):
            with self.assertRaisesRegex(ValueError, "locked outcome/actor row drift"):
                lane.validate_wave8_irish_royalists_queue_contracts(semantic)

    def test_nested_assault_guard_and_final_signature_fail_closed(self):
        contract = lane.WAVE8_IRISH_ROYALISTS_CONTRACTS["hced-Clonmel1650-1"]
        with patch.dict(
            contract,
            {"nested_assault_disposition": "besieger_victory"},
        ):
            with self.assertRaisesRegex(ValueError, "nested Clonmel assault guard"):
                lane.wave8_irish_royalists_counts()

        with patch.object(
            lane,
            "WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE",
            "0" * 64,
        ):
            with self.assertRaisesRegex(ValueError, "final audit signature changed"):
                lane.wave8_irish_royalists_counts()

    def test_promoter_rejects_missing_identity_duplicate_candidate_and_name(self):
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(CLONMEL_GARRISON)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_irish_royalists_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        promoted = lane.promote_wave8_irish_royalists_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_irish_royalists_contracts(
                self.hced_rows,
                entities,
                [*existing, promoted[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_irish_royalists_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-clonmel-name-collision",
                        "name": "Siege of Clonmel",
                        "year": 1650,
                    },
                ],
            )

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_irish_royalists_entities(entities)
        lane.install_wave8_irish_royalists_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entity_collision = copy.deepcopy(entities)
        entity_collision[DUNGAN_PARLIAMENTARIANS]["end_year"] = 1648
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_irish_royalists_entities(entity_collision)

        source_collision = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_IRISH_ROYALISTS_SOURCES[0]["id"])
        source_collision[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_irish_royalists_sources(source_collision)

    def test_current_artifact_state_is_all_or_none(self):
        current_owned = sum(
            event.get("hced_candidate_id")
            in lane.WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
            for event in self.release_events
        )
        current = lane.validate_wave8_irish_royalists_current_artifact_state(
            self.release_events,
            self.release_entities,
            self.release_sources,
        )
        self.assertEqual(current["promoted_events"], current_owned)
        self.assertEqual(
            current["artifact_state"],
            "integrated" if current_owned else "absent",
        )

        entities, sources, existing = self._installed()
        events = lane.promote_wave8_irish_royalists_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(
            lane.validate_wave8_irish_royalists_current_artifact_state(
                events,
                entities.values(),
                sources.values(),
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 4,
                "installed_sources": 5,
                "promoted_events": 2,
            },
        )
        with self.assertRaisesRegex(ValueError, "artifacts are partial"):
            lane.validate_wave8_irish_royalists_current_artifact_state(
                events[:1],
                entities.values(),
                sources.values(),
            )

    def test_counts_metadata_and_audit_signature_are_pinned(self):
        self.assertEqual(
            lane.wave8_irish_royalists_counts(),
            {
                "country_quarantine_additions": 1,
                "discovery_nonrating_records": 2,
                "holds": 0,
                "integration_dispositions": 2,
                "new_entities": 4,
                "new_sources": 5,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 2,
            },
        )
        self.assertEqual(
            lane.wave8_irish_royalists_cohort_counts(),
            {"irish_confederate_wars_exact_1647_1650": 2},
        )
        self.assertEqual(
            lane.wave8_irish_royalists_audit_signature(),
            "63ef1b61661d017baada9704ff49f7146b4800014cc9bf6170450fb84101f684",
        )
        self.assertEqual(
            lane.wave8_irish_royalists_audit_signature(),
            lane.WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_irish_royalists_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_irish_royalists_counts())
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(EXPECTED_HASHES))
        self.assertEqual(len(metadata["discovery_dispositions"]), 2)
        self.assertEqual(
            metadata["country_quarantine_additions"],
            ["hced-Dungan Hill1647-1"],
        )
        self.assertEqual(
            metadata["point_quarantine_additions"],
            ["hced-Clonmel1650-1", "hced-Dungan Hill1647-1"],
        )


if __name__ == "__main__":
    unittest.main()
