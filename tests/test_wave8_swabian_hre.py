import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_swabian_hre as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_swabian_hre_"

EXPECTED_HASHES = {
    "hced-Calven1499-1": (
        "24873e0203c606b02f0b3e6a014851e48a3e6916c07a3cc8256f7fceb71a0a9d"
    ),
    "hced-Doffingen1388-1": (
        "7705f95a5039588352dd22517239bfb50a82f6bda18019c4aed8b8ff0f2d6801"
    ),
    "hced-Frastenz1499-1": (
        "102eee9198f6f228061989318060d05880ac5260bf3c6f58307c1872876e49c5"
    ),
    "hced-Hard1499-1": (
        "0144c09102942d33fb65533b3c8a2c29986e0dc8a7e92b9b1a8bed449695940c"
    ),
    "hced-Reutlingen1377-1": (
        "72dc18e36339f54002521a36f34fe795395b562285f439ba7a11584cbbc7a127"
    ),
    "hced-Schwaderloch1499-1": (
        "4ad58e960545dd867167658fd9381052306cc5627229531d2ce9d8e1ef063350"
    ),
    "hced-Triesen1499-1": (
        "7a7a4d2fc6e9da5a50aa3e2c4f3b1f44f3f4e12ccef7c6e0f07537f5677f459f"
    ),
    "hced-Ulm1376-1": (
        "db337ec870aaed28d9899c17ef2cc52bc159846e31c1dbe7f3922badfe9455cc"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q136753967": (
        "2eb9bac5113cf1449b8596b4a19f234ae94839181b4110282c23dc76c5340e0f"
    ),
    "Q1398703": (
        "a4dba9e0486c514437e658dd2218465069092dd117b6a31398fca61a6bf08a55"
    ),
    "Q319467": (
        "39d2b0ccdf7f8217553ab1dafdfa780d8e90b469b2f51d7d056fe2dd8c95cce7"
    ),
    "Q462099": (
        "8fb34162342eb9b06ecaa9580d733b466ba9ebec7e4c781c9820fd1c0d590f28"
    ),
    "Q477778": (
        "be417acab0266d10dff4883228b0ed1b0d0cd556949bbf349ecf6f3b0f005bbf"
    ),
    "Q873286": (
        "1da9222368aac0e65e9e35befc3534ffeff8c2fb0971a6be52add45d0589f717"
    ),
}

EXPECTED_SIDES = {
    "hced-Calven1499-1": (
        "three_leagues_confederate_field_host_calven_1499",
        "maximilianian_tyrolean_vinschgau_host_calven_1499",
    ),
    "hced-Doffingen1388-1": (
        "wurttemberg_princely_coalition_doffingen_1388",
        "swabian_city_league_field_host_doffingen_1388",
    ),
    "hced-Frastenz1499-1": (
        "confederate_field_host_frastenz_1499",
        "maximilianian_tyrolean_vorderoesterreich_host_frastenz_1499",
    ),
    "hced-Hard1499-1": (
        "confederate_field_host_hard_1499",
        "habsburg_swabian_field_host_hard_1499",
    ),
    "hced-Reutlingen1377-1": (
        "reutlingen_city_force_1377",
        "ulrich_wurttemberg_field_force_reutlingen_1377",
    ),
    "hced-Schwaderloch1499-1": (
        "confederate_thurgau_field_host_schwaderloh_1499",
        "imperial_swabian_konstanz_host_schwaderloh_1499",
    ),
    "hced-Triesen1499-1": (
        "buendner_confederate_field_host_triesen_1499",
        "habsburg_allied_swabian_landsknechts_triesen_1499",
    ),
    "hced-Ulm1376-1": (
        "ulm_city_defenders_1376",
        "charles_iv_imperial_princely_siege_host_ulm_1376",
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


class Wave8SwabianHreTests(unittest.TestCase):
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

    def _base_artifacts(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_SWABIAN_HRE_ENTITIES
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_SWABIAN_HRE_SOURCES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        events = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_SWABIAN_HRE_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, sources, events

    def _installed(self):
        entities, sources, events = self._base_artifacts()
        lane.install_wave8_swabian_hre_entities(entities)
        lane.install_wave8_swabian_hre_sources(sources)
        return entities, sources, events

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_swabian_hre_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_swabian_label_inventory_and_semantic_hashes_are_pinned(self):
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "swabian league"
            or normalize_label(row.get("side_2_raw")) == "swabian league"
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            set(EXPECTED_HASHES),
        )
        self.assertEqual(lane.WAVE8_SWABIAN_HRE_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_SWABIAN_HRE_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_HASHES),
        )
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

    def test_queue_and_historical_funnel_accounting_are_exact(self):
        self.assertEqual(
            lane.validate_wave8_swabian_hre_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 8,
                "holds": 0,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 8,
            },
        )
        integrated_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        } & lane.WAVE8_SWABIAN_HRE_CONTRACT_IDS
        if not integrated_ids:
            self.assertEqual(
                lane.validate_wave8_swabian_hre_funnel(self.funnel),
                {
                    "events_touched": 8,
                    "sole_blocker_events": 0,
                    "unresolved_side_attempts": 8,
                    "zero_time_valid_candidates": 8,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_swabian_hre_exact_label_funnel_audit"
                ],
                lane.WAVE8_SWABIAN_HRE_FUNNEL_AUDIT,
            )

    def test_contracts_pin_dates_names_granularity_and_source_side_one_wins(self):
        expected = {
            "hced-Calven1499-1": (
                "Battle of Calven",
                "1499-05-22",
                "1499-05-22",
                0.98,
            ),
            "hced-Doffingen1388-1": (
                "Battle of Döffingen",
                "1388-08-23",
                "1388-08-23",
                0.98,
            ),
            "hced-Frastenz1499-1": (
                "Battle of Frastanz",
                "1499-04-20",
                "1499-04-20",
                0.99,
            ),
            "hced-Hard1499-1": (
                "Battle of Hard",
                "1499-02-20",
                "1499-02-22",
                0.91,
            ),
            "hced-Reutlingen1377-1": (
                "Battle of Reutlingen",
                "1377-05-14",
                "1377-05-21",
                0.92,
            ),
            "hced-Schwaderloch1499-1": (
                "Battle of Schwaderloh",
                "1499-04-11",
                "1499-04-11",
                0.99,
            ),
            "hced-Triesen1499-1": (
                "Battle of Triesen",
                "1499-02-12",
                "1499-02-12",
                0.98,
            ),
            "hced-Ulm1376-1": (
                "Siege of Ulm (1376)",
                "1376-09-30",
                "1376-10-09",
                0.93,
            ),
        }
        self.assertEqual(lane.WAVE8_SWABIAN_HRE_CONTRACT_IDS, set(expected))
        self.assertEqual(lane.WAVE8_SWABIAN_HRE_RESERVED_IDS, set(expected))
        self.assertFalse(lane.WAVE8_SWABIAN_HRE_HOLDS)
        for candidate_id, values in expected.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_SWABIAN_HRE_CONTRACTS[candidate_id]
                canonical = contract["canonical_event"]
                self.assertEqual(
                    (
                        canonical["name"],
                        canonical["start_date"],
                        canonical["end_date"],
                        contract["confidence"],
                    ),
                    values,
                )
                self.assertIn("calendar_unspecified", canonical["date_precision"])
                self.assertTrue(canonical["date_text"])
                self.assertTrue(canonical["granularity"])
                self.assertEqual(contract["winner_side"], 1)
                self.assertEqual(contract["result_type"], "win")
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertFalse(contract["source_date_override"])
                self.assertEqual(contract["expected_scale_level"], 2)

    def test_every_contract_uses_two_alias_free_event_bounded_identities(self):
        entities = {
            str(entity["id"]): entity
            for entity in lane.WAVE8_SWABIAN_HRE_ENTITIES
        }
        self.assertEqual(len(entities), 16)
        self.assertEqual(
            set(entities),
            {entity_id for pair in EXPECTED_SIDES.values() for entity_id in pair},
        )
        forbidden = {
            "german princes",
            "habsburg",
            "holy roman empire",
            "hre",
            "swabian league",
            "switzerland",
            "swiss confederation",
        }
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                Entity.from_dict(entity)
                self.assertEqual(entity["start_year"], entity["end_year"])
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertFalse(
                    {normalize_label(alias) for alias in entity["aliases"]}
                    & forbidden
                )
                self.assertIn("Bounded", entity["continuity_note"])
        for candidate_id, (winner, loser) in EXPECTED_SIDES.items():
            contract = lane.WAVE8_SWABIAN_HRE_CONTRACTS[candidate_id]
            self.assertEqual(contract["side_1_entity_ids"], [winner])
            self.assertEqual(contract["side_2_entity_ids"], [loser])

    def test_source_provenance_is_closed_and_independently_familied(self):
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_SWABIAN_HRE_SOURCES
        }
        self.assertEqual(len(sources), 16)
        used = set()
        for source in sources.values():
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
            self.assertTrue(source["source_family_id"])
            self.assertTrue(source["url"].startswith("https://"))
        for candidate_id, contract in lane.WAVE8_SWABIAN_HRE_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                outcome_ids = contract["outcome_source_ids"]
                self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
                self.assertEqual(contract["evidence_refs"], outcome_ids)
                self.assertEqual(contract["date_source_ids"], outcome_ids)
                self.assertEqual(
                    set(contract["event_evidence_roles"]), set(outcome_ids)
                )
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]), 2
                )
                self.assertLessEqual(set(outcome_ids), set(sources))
                used.update(outcome_ids)
        self.assertEqual(used, set(sources))

    def test_installers_are_idempotent_and_fail_closed_on_collisions(self):
        entities, sources, _ = self._installed()
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        lane.install_wave8_swabian_hre_entities(entities)
        lane.install_wave8_swabian_hre_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)

        entity_id = lane.WAVE8_SWABIAN_HRE_ENTITIES[0]["id"]
        bad_entities = copy.deepcopy(first_entities)
        bad_entities[entity_id]["name"] = "Collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_swabian_hre_entities(bad_entities)

        source_id = lane.WAVE8_SWABIAN_HRE_SOURCES[0]["id"]
        bad_sources = copy.deepcopy(first_sources)
        bad_sources[source_id]["title"] = "Collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_swabian_hre_sources(bad_sources)

    def test_emitted_events_are_exact_tactical_wins_with_no_draws(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_SIDES))
        for candidate_id, (winner, loser) in EXPECTED_SIDES.items():
            with self.subTest(candidate_id=candidate_id):
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
                self.assertFalse(
                    any(
                        "inconclusive" in participant["termination"]
                        for participant in event["participants"]
                    )
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], "interstate_limited")
                self.assertEqual(event["scale"], "battle")
                self.assertEqual(event["source_ids"][0], "hced_dataset")
                Event.from_dict(event)

    def test_emitted_names_dates_confidence_and_aliases_match_contracts(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        raw_names = {
            str(row["candidate_id"]): str(row["name"])
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_SWABIAN_HRE_CONTRACTS[candidate_id]
                canonical = contract["canonical_event"]
                self.assertEqual(event["name"], canonical["name"])
                self.assertEqual(event["date_precision"], canonical["date_precision"])
                self.assertEqual(
                    event["reviewed_granularity"], canonical["granularity"]
                )
                self.assertEqual(event["confidence"], contract["confidence"])
                self.assertEqual(event["aliases"], [raw_names[candidate_id]])
                self.assertEqual(
                    event["outcome_source_ids"], contract["outcome_source_ids"]
                )
                self.assertEqual(
                    event["outcome_source_family_ids"],
                    contract["outcome_source_family_ids"],
                )

    def test_location_quarantines_withhold_all_points_and_only_calven_country(self):
        self.assertEqual(
            lane.WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Calven1499-1"},
        )
        self.assertEqual(
            set(lane.WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_REASONS),
            set(EXPECTED_HASHES),
        )
        retained = {
            "hced-Doffingen1388-1": "Germany",
            "hced-Frastenz1499-1": "Austria",
            "hced-Hard1499-1": "Austria",
            "hced-Reutlingen1377-1": "Germany",
            "hced-Schwaderloch1499-1": "Switzerland",
            "hced-Triesen1499-1": "Liechtenstein",
            "hced-Ulm1376-1": "Germany",
        }
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertNotIn("geometry", event)
                if candidate_id == "hced-Calven1499-1":
                    self.assertNotIn("modern_location_country", event)
                    self.assertNotIn("location_provenance", event)
                else:
                    self.assertEqual(
                        event["modern_location_country"], retained[candidate_id]
                    )
                    self.assertIn("location_provenance", event)

    def test_six_wikidata_twins_are_hash_pinned_and_unknown_never_draw(self):
        self.assertEqual(
            lane.WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        self.assertEqual(
            set(lane.WAVE8_SWABIAN_HRE_DISCOVERY_TWINS.values()),
            set(EXPECTED_DISCOVERY_HASHES),
        )
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
                    lane.WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED[candidate_id][
                        "outcome_disposition"
                    ],
                    "unknown_never_draw",
                )
        self.assertEqual(
            lane.validate_wave8_swabian_hre_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_twins": 6,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 6,
            },
        )

    def test_discovery_winner_or_automatic_rating_drift_fails_closed(self):
        rows = copy.deepcopy(self.wikidata_rows)
        target = next(row for row in rows if row.get("candidate_id") == "Q462099")
        target["winners"] = [
            {"label": "Swiss Confederacy", "uri": "http://example.invalid/winner"}
        ]
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_swabian_hre_discovery_dispositions(rows)

        rows = copy.deepcopy(self.wikidata_rows)
        target = next(row for row in rows if row.get("candidate_id") == "Q462099")
        target["do_not_rate_automatically"] = False
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_swabian_hre_discovery_dispositions(rows)

    def test_cross_dataset_and_release_duplicate_audit_is_closed(self):
        result = lane.validate_wave8_swabian_hre_integration_dispositions(
            self.hced_rows,
            self.iwd_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(result["discovery_nonrating_dispositions"], 6)
        self.assertEqual(result["hced_probable_twins"], 0)
        self.assertEqual(result["iwd_probable_twins"], 0)
        self.assertEqual(result["iwbd_probable_twins"], 0)
        self.assertEqual(result["existing_release_probable_twins"], 0)

        injected = [
            *self.iwd_rows,
            {
                "candidate_id": "iwd-injected-calven",
                "name": "Battle of Calven",
                "start_year": 1499,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_swabian_hre_integration_dispositions(
                self.hced_rows,
                injected,
                self.iwbd_rows,
                self.release_events,
            )

    def test_queue_row_mutation_or_duplicate_fails_closed(self):
        rows = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in rows if row.get("candidate_id") == "hced-Hard1499-1"
        )
        target["winner_raw"] = ""
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_swabian_hre_queue_contracts(rows)

        rows = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in rows if row.get("candidate_id") == "hced-Hard1499-1"
        )
        rows.append(copy.deepcopy(target))
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_swabian_hre_queue_contracts(rows)

    def test_missing_or_out_of_window_entity_fails_closed(self):
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(EXPECTED_SIDES["hced-Calven1499-1"][0])
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_swabian_hre_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        out_of_window = copy.deepcopy(entities)
        out_of_window[EXPECTED_SIDES["hced-Calven1499-1"][0]][
            "start_year"
        ] = 1500
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_swabian_hre_contracts(
                self.hced_rows,
                out_of_window,
                existing,
            )

    def test_rerun_and_name_year_duplicate_fail_closed(self):
        entities, _, existing = self._installed()
        emitted = lane.promote_wave8_swabian_hre_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_swabian_hre_contracts(
                self.hced_rows,
                entities,
                [*existing, *emitted],
            )

        collision = [
            *existing,
            {"id": "collision", "name": "Battle of Calven", "year": 1499},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_swabian_hre_contracts(
                self.hced_rows,
                entities,
                collision,
            )

    def test_current_artifact_validator_accepts_only_absent_or_complete_state(self):
        base_entities, base_sources, base_events = self._base_artifacts()
        self.assertEqual(
            lane.validate_wave8_swabian_hre_current_artifact_state(
                base_events,
                base_entities.values(),
                base_sources.values(),
            ),
            {
                "artifact_state": "absent",
                "installed_entities": 0,
                "installed_sources": 0,
                "promoted_events": 0,
            },
        )

        entities, sources, existing = self._installed()
        emitted = lane.promote_wave8_swabian_hre_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(
            lane.validate_wave8_swabian_hre_current_artifact_state(
                [*existing, *emitted],
                entities.values(),
                sources.values(),
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 16,
                "installed_sources": 16,
                "promoted_events": 8,
            },
        )

        partial_entities = copy.deepcopy(base_entities)
        fixture = copy.deepcopy(lane.WAVE8_SWABIAN_HRE_ENTITIES[0])
        partial_entities[str(fixture["id"])] = fixture
        with self.assertRaisesRegex(ValueError, "artifacts are partial"):
            lane.validate_wave8_swabian_hre_current_artifact_state(
                base_events,
                partial_entities.values(),
                base_sources.values(),
            )

    def test_current_artifact_validator_detects_participant_and_location_drift(self):
        entities, sources, existing = self._installed()
        emitted = lane.promote_wave8_swabian_hre_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        bad = copy.deepcopy(emitted)
        bad[0]["participants"][0]["termination"] = "engagement_defeat"
        with self.assertRaisesRegex(ValueError, "participant drift"):
            lane.validate_wave8_swabian_hre_current_artifact_state(
                [*existing, *bad],
                entities.values(),
                sources.values(),
            )

        bad = copy.deepcopy(emitted)
        calven = next(
            event
            for event in bad
            if event["hced_candidate_id"] == "hced-Calven1499-1"
        )
        calven["modern_location_country"] = "Netherlands"
        with self.assertRaisesRegex(ValueError, "Calven location quarantine drift"):
            lane.validate_wave8_swabian_hre_current_artifact_state(
                [*existing, *bad],
                entities.values(),
                sources.values(),
            )

    def test_signature_counts_cohorts_and_metadata_are_sealed(self):
        self.assertEqual(
            lane.wave8_swabian_hre_audit_signature(),
            lane.WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_swabian_hre_cohort_counts(),
            {
                "swabian_city_league_wars_1376_1388": 3,
                "swabian_war_1499": 5,
            },
        )
        self.assertEqual(
            lane.wave8_swabian_hre_counts(),
            {
                "country_quarantine_additions": 1,
                "discovery_nonrating_records": 6,
                "holds": 0,
                "integration_dispositions": 6,
                "new_entities": 16,
                "new_sources": 16,
                "newly_rated_events": 8,
                "outcome_overrides": 0,
                "point_quarantine_additions": 8,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 8,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 6,
            },
        )
        metadata = lane.wave8_swabian_hre_metadata()
        self.assertEqual(
            metadata["promoted_candidate_ids"], sorted(EXPECTED_HASHES)
        )
        self.assertEqual(len(metadata["discovery_dispositions"]), 6)
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
