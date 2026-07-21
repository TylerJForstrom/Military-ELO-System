import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_republic_formosa as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
REPUBLIC_FORMOSA = "republic_of_formosa_1895"
JAPAN = "empire_japan"

EXPECTED_HASHES = {
    "hced-Baguashan1895-1": (
        "0fd6d74272e4d966b21945b43f06e379430fd5df8fdccd55850746519a9cddff"
    ),
    "hced-Keelung1895-1": (
        "970d4f5910dffe14462d32c48e4907a15fc468aa557ff0ccb7fcacc87d964ac2"
    ),
}
EXPECTED_CANONICAL = {
    "hced-Baguashan1895-1": (
        "Battle of Baguashan",
        "27 August 1895",
        "day",
        "single_day_pitched_battle_and_fort_capture",
    ),
    "hced-Keelung1895-1": (
        "Battle of Keelung (1895)",
        "2-3 June 1895",
        "day_range",
        "two_day_battle_and_port_capture",
    ),
}
EXPECTED_SOURCE_URLS = {
    "wave8_republic_formosa_davidson_campaign": (
        "https://archive.org/details/islandofformosap00davi"
    ),
    "wave8_republic_formosa_jacar_campaign": (
        "https://www.jacar.go.jp/english/exhibition/"
        "jacarbl-fsjwar-e/smart/about/p005.html"
    ),
    "wave8_republic_formosa_ntm_flag": (
        "https://www.ntm.gov.tw/en/News_Content2.aspx?n=5699&s=149444"
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


class Wave8RepublicFormosaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced
        }

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) != REPUBLIC_FORMOSA
        }
        lane.install_wave8_republic_formosa_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(
                "hced_wave8_republic_formosa_"
            )
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_republic_formosa_contracts(
            self.hced,
            entities,
            existing,
        )

    def test_full_exact_adjacent_and_campaign_inventory_is_pinned(self) -> None:
        self.assertEqual(
            lane.validate_wave8_republic_formosa_queue_contracts(self.hced),
            {
                "adjacent_campaign_rows": 1,
                "adjacent_literal_label_rows": 0,
                "exact_label_rows": 2,
                "full_1895_taiwan_campaign_rows": 3,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        exact_ids = {
            str(row["candidate_id"])
            for row in self.hced
            if "republic of formosa"
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        }
        self.assertEqual(exact_ids, lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS)
        self.assertEqual(exact_ids, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_REPUBLIC_FORMOSA_HOLDS)
        self.assertFalse(lane.WAVE8_REPUBLIC_FORMOSA_HOLD_IDS)
        self.assertEqual(
            lane.WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY,
            {
                "formosa republic": (),
                "formosan republic": (),
                "republic of taiwan": (),
                "taiwan republic": (),
            },
        )

    def test_raw_hashes_years_and_actor_orientation_are_immutable(self) -> None:
        self.assertEqual(lane.WAVE8_REPUBLIC_FORMOSA_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = self.hced_by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (row["year_low"], row["year_best"], row["year_high"]),
                    (1895, 1895, 1895),
                )
                self.assertEqual(
                    (row["side_1_raw"], row["side_2_raw"]),
                    ("Japan", "Republic of Formosa"),
                )
                self.assertEqual(
                    (row["winner_raw"], row["loser_raw"]),
                    ("Japan", "Republic of Formosa"),
                )
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")
                self.assertNotIn(
                    normalize_label(row["winner_raw"]),
                    {"draw", "inconclusive", "stalemate"},
                )

    def test_pescadores_is_pinned_to_its_pre_republic_owner(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS),
            {"hced-Pescadores1895-1"},
        )
        disposition = lane.WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS[
            "hced-Pescadores1895-1"
        ]
        row = self.hced_by_id["hced-Pescadores1895-1"]
        self.assertEqual(
            canonical_hced_row_sha256(row),
            "10726f66b36555d7f1601238b18b4f40c55fe821b14b62776cddb2d3492986a5",
        )
        self.assertEqual(
            disposition["disposition"],
            "pre_republic_existing_release_owner",
        )
        self.assertEqual(
            disposition["owner_event_id"],
            "hced_hced_pescadores1895_1",
        )
        owner = next(
            event
            for event in self.release_events
            if event.get("hced_candidate_id") == "hced-Pescadores1895-1"
        )
        self.assertEqual(owner["id"], disposition["owner_event_id"])
        self.assertNotIn(
            "hced-Pescadores1895-1",
            lane.WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS,
        )
        self.assertIn("preceded", disposition["reason"])

    def test_funnel_pin_or_integrated_metadata_is_exact(self) -> None:
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        if "republic of formosa" in labels:
            self.assertEqual(
                lane.validate_wave8_republic_formosa_funnel(self.funnel),
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
                    "wave8_republic_formosa_exact_label_funnel_audit"
                ],
                lane.WAVE8_REPUBLIC_FORMOSA_FUNNEL_AUDIT,
            )

    def test_identity_is_exact_alias_free_and_windowed_only_to_1895(self) -> None:
        self.assertEqual(len(lane.WAVE8_REPUBLIC_FORMOSA_ENTITIES), 1)
        entity = lane.WAVE8_REPUBLIC_FORMOSA_ENTITIES[0]
        self.assertEqual(entity["id"], REPUBLIC_FORMOSA)
        self.assertEqual(entity["name"], "Republic of Formosa")
        self.assertEqual((entity["start_year"], entity["end_year"]), (1895, 1895))
        self.assertFalse(entity["aliases"])
        self.assertFalse(entity["predecessors"])
        self.assertIn("25 May 1895", entity["continuity_note"])
        self.assertIn("21 October", entity["continuity_note"])
        self.assertIn("No rating is inherited", entity["continuity_note"])
        Entity.from_dict(entity)

        japan = next(
            item for item in self.release_entities if item["id"] == JAPAN
        )
        self.assertLessEqual(japan["start_year"], 1895)
        self.assertGreaterEqual(japan["end_year"], 1895)

    def test_sources_are_stable_role_explicit_and_independent(self) -> None:
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_REPUBLIC_FORMOSA_SOURCES
        }
        self.assertEqual(set(sources), set(EXPECTED_SOURCE_URLS))
        self.assertEqual(
            {source_id: source["url"] for source_id, source in sources.items()},
            EXPECTED_SOURCE_URLS,
        )
        self.assertTrue(
            all(source["accessed"] == "2026-07-20" for source in sources.values())
        )
        self.assertTrue(all(source["url"].startswith("https://") for source in sources.values()))
        for source in sources.values():
            Source.from_dict(source)

        identity_only = sources["wave8_republic_formosa_ntm_flag"]
        self.assertEqual(
            identity_only["evidence_roles"],
            ["identity_boundary_or_context_reference"],
        )
        self.assertNotIn("outcome", identity_only["evidence_roles"])
        for contract in lane.WAVE8_REPUBLIC_FORMOSA_CONTRACTS.values():
            self.assertEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertNotIn(
                "wave8_republic_formosa_ntm_flag",
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        sources[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
            self.assertTrue(
                all(
                    "outcome" in sources[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )

    def test_reviewed_dates_outcomes_and_granularity_are_pinned(self) -> None:
        for candidate_id, expected in EXPECTED_CANONICAL.items():
            contract = lane.WAVE8_REPUBLIC_FORMOSA_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["date_precision"],
                    canonical["granularity"],
                ),
                expected,
            )
            self.assertEqual((canonical["year_low"], canonical["year_high"]), (1895, 1895))
            self.assertEqual(
                contract["direct_provenance"]["reviewed_date"],
                canonical["date_text"],
            )
            self.assertTrue(contract["direct_provenance"]["reviewed_outcome"])
            self.assertTrue(contract["direct_provenance"]["event_boundary"])
            self.assertEqual(contract["side_1_entity_ids"], [JAPAN])
            self.assertEqual(contract["side_2_entity_ids"], [REPUBLIC_FORMOSA])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_exactly_two_tactical_events_promote_with_correct_polarity(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS)
        self.assertEqual(len({event["id"] for event in events.values()}), 2)
        for candidate_id, event in events.items():
            contract = lane.WAVE8_REPUBLIC_FORMOSA_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith("hced_wave8_republic_formosa_"))
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["year"], 1895)
            self.assertEqual(event["end_year"], 1895)
            self.assertEqual(
                event["reviewed_granularity"],
                contract["canonical_event"]["granularity"],
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                set(event["outcome_source_ids"]),
                set(contract["outcome_source_ids"]),
            )
            terminations = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {
                    JAPAN: "engagement_victory",
                    REPUBLIC_FORMOSA: "engagement_defeat",
                },
            )
            Event.from_dict(event)

    def test_promoted_points_are_withheld_but_country_and_provenance_remain(self) -> None:
        self.assertEqual(
            lane.WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_REPUBLIC_FORMOSA_COUNTRY_QUARANTINE_ADDITIONS
        )
        self.assertEqual(
            set(lane.WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS,
        )
        for candidate_id, event in {
            event["hced_candidate_id"]: event for event in self._events()
        }.items():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Taiwan")
            self.assertTrue(event["location_provenance"])
            review = lane.WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS[
                candidate_id
            ]
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertIn("unexplained place centroid", review["reason"])

    def test_cross_source_duplicate_and_partial_integration_guards(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_republic_formosa_integration_dispositions(
                self.hced,
                self.iwbd,
                existing,
            ),
            {
                "adjacent_existing_release_owners": 1,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
            },
        )

        fake_iwbd = [
            *self.iwbd,
            {
                "candidate_id": "iwbd-formosa-twin",
                "name": "Kelung",
                "start_date": "1895-06-02",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_republic_formosa_integration_dispositions(
                self.hced,
                fake_iwbd,
                existing,
            )

        fake_hced = {
            "candidate_id": "hced-formosa-twin",
            "name": "Changwha",
            "year_low": 1895,
            "year_best": 1895,
            "year_high": 1895,
            "side_1_raw": "Japan",
            "side_2_raw": "Local force",
            "modern_location_country": "Japan",
            "war_names": [],
        }
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_republic_formosa_integration_dispositions(
                [*self.hced, fake_hced],
                self.iwbd,
                existing,
            )

        fake_release = {
            "id": "release-formosa-twin",
            "name": "Battle of Baguashan",
            "year": 1895,
            "participants": [],
        }
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_republic_formosa_integration_dispositions(
                self.hced,
                self.iwbd,
                [*existing, fake_release],
            )

        without_pescadores = [
            event
            for event in existing
            if event.get("hced_candidate_id") != "hced-Pescadores1895-1"
        ]
        with self.assertRaisesRegex(ValueError, "adjacent release owner drift"):
            lane.validate_wave8_republic_formosa_integration_dispositions(
                self.hced,
                self.iwbd,
                without_pescadores,
            )

        entities, existing = self._installed()
        promoted = lane.promote_wave8_republic_formosa_contracts(
            self.hced,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "partial release integration"):
            lane.validate_wave8_republic_formosa_integration_dispositions(
                self.hced,
                self.iwbd,
                [*existing, promoted[0]],
            )

    def test_installers_are_idempotent_and_reject_collisions(self) -> None:
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        entities.pop(REPUBLIC_FORMOSA, None)
        lane.install_wave8_republic_formosa_entities(entities)
        once = copy.deepcopy(entities[REPUBLIC_FORMOSA])
        lane.install_wave8_republic_formosa_entities(entities)
        self.assertEqual(entities[REPUBLIC_FORMOSA], once)
        entities[REPUBLIC_FORMOSA]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_republic_formosa_entities(entities)

        sources = {}
        lane.install_wave8_republic_formosa_sources(sources)
        lane.install_wave8_republic_formosa_sources(sources)
        self.assertEqual(set(sources), set(EXPECTED_SOURCE_URLS))
        first_id = sorted(sources)[0]
        sources[first_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_republic_formosa_sources(sources)

    def test_row_drift_new_adjacent_label_and_duplicate_event_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Keelung1895-1"
        )
        row["winner_raw"] = "Republic of Formosa"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_republic_formosa_queue_contracts(tampered)

        new_adjacent = copy.deepcopy(self.hced_by_id["hced-Keelung1895-1"])
        new_adjacent["candidate_id"] = "hced-new-formosan-republic-row"
        new_adjacent["side_2_raw"] = "Formosan Republic"
        new_adjacent["modern_location_country"] = "Japan"
        new_adjacent["war_names"] = []
        with self.assertRaisesRegex(ValueError, "adjacent-label inventory"):
            lane.validate_wave8_republic_formosa_queue_contracts(
                [*self.hced, new_adjacent]
            )

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Keelung (1895)",
                "year": 1895,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_republic_formosa_contracts(
                self.hced,
                entities,
                existing,
            )

    def test_current_artifacts_are_strictly_all_or_none(self) -> None:
        state = lane.validate_wave8_republic_formosa_current_artifact_state(
            self.release_entities,
            self.release_events,
            self.release_sources,
            self.release_metadata,
        )
        self.assertIn(state["integration_state"], {"preintegration", "integrated"})
        if state["integration_state"] == "preintegration":
            self.assertEqual(
                state,
                {
                    "entity_records": 0,
                    "event_records": 0,
                    "integration_state": "preintegration",
                    "metadata_marker": 0,
                    "source_records": 0,
                },
            )
        else:
            self.assertEqual(state["entity_records"], 1)
            self.assertEqual(state["event_records"], 2)
            self.assertEqual(state["metadata_marker"], 1)
            self.assertEqual(state["source_records"], 3)

        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) != REPUBLIC_FORMOSA
        }
        lane.install_wave8_republic_formosa_entities(entities)
        with self.assertRaisesRegex(ValueError, "partial current-artifact"):
            lane.validate_wave8_republic_formosa_current_artifact_state(
                entities.values(),
                [
                    event
                    for event in self.release_events
                    if event.get("hced_candidate_id")
                    not in lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
                ],
                [
                    source
                    for source in self.release_sources
                    if source["id"] not in EXPECTED_SOURCE_URLS
                ],
                self.release_metadata,
            )

    def test_synthetic_fully_integrated_artifact_passes_all_or_none_guard(self) -> None:
        entities, existing = self._installed()
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in EXPECTED_SOURCE_URLS
        }
        lane.install_wave8_republic_formosa_sources(sources)
        promoted = lane.promote_wave8_republic_formosa_contracts(
            self.hced,
            entities,
            existing,
        )
        metadata = copy.deepcopy(self.release_metadata)
        metadata.setdefault("promotion", {}).update(
            {
                "accepted_wave8_republic_formosa_hced_events": 2,
                "wave8_republic_formosa_candidate_ids": sorted(
                    lane.WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
                ),
            }
        )
        self.assertEqual(
            lane.validate_wave8_republic_formosa_current_artifact_state(
                entities.values(),
                [*existing, *promoted],
                sources.values(),
                metadata,
            ),
            {
                "entity_records": 1,
                "event_records": 2,
                "integration_state": "integrated",
                "metadata_marker": 1,
                "source_records": 3,
            },
        )

    def test_counts_cohort_metadata_and_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_republic_formosa_counts(),
            {
                "adjacent_campaign_dispositions": 1,
                "adjacent_literal_label_rows": 0,
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 1,
                "new_sources": 3,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_republic_formosa_cohort_counts(),
            {"japanese_invasion_of_taiwan_1895": 2},
        )
        self.assertEqual(
            lane.wave8_republic_formosa_audit_signature(),
            "4bde800edb6ad6d43c105eb9f008161db7620ec80e9f1de61c6c60512f29858c",
        )
        self.assertEqual(
            lane.wave8_republic_formosa_audit_signature(),
            lane.WAVE8_REPUBLIC_FORMOSA_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_republic_formosa_metadata()
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            ["hced-Baguashan1895-1", "hced-Keelung1895-1"],
        )
        self.assertEqual(metadata["hold_candidate_ids"], [])
        self.assertEqual(len(metadata["adjacent_hced_dispositions"]), 1)


if __name__ == "__main__":
    unittest.main()
