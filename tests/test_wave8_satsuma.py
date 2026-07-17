import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_satsuma import (
    WAVE8_SATSUMA_CONTRACT_IDS,
    WAVE8_SATSUMA_CONTRACTS,
    WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
    WAVE8_SATSUMA_ENTITIES,
    WAVE8_SATSUMA_EXCLUSION_IDS,
    WAVE8_SATSUMA_EXCLUSIONS,
    WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS,
    WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE,
    WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_HOLD_IDS,
    WAVE8_SATSUMA_HOLDS,
    WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS,
    WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SATSUMA_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS,
    WAVE8_SATSUMA_NONPROMOTIONS,
    WAVE8_SATSUMA_OUTCOME_OVERRIDES,
    WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SATSUMA_RESERVED_IDS,
    WAVE8_SATSUMA_SOURCES,
    WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS,
    WAVE8_SATSUMA_TERMINAL_EXCLUSIONS,
    install_wave8_satsuma_entities,
    install_wave8_satsuma_sources,
    promote_wave8_satsuma_contracts,
    validate_wave8_satsuma_integration_dispositions,
    validate_wave8_satsuma_queue_contracts,
    wave8_satsuma_audit_signature,
    wave8_satsuma_cohort_counts,
    wave8_satsuma_counts,
    wave8_satsuma_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_satsuma_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "d9dc778913c01bc8bb80441541d06e51bf76ea6620e8a6819a010e6834585ab1"
)
SHIROYAMA_ID = "hced-Shiroyama1877-1"
SHIROYAMA_HASH = (
    "8afa15c8db32ca76099ffdd8b8d03c180f5d7d361dac7824d84a6a5b92dfa4d3"
)

SHIMAZU_ID = "shimazu_kyushu_war_army_1586_1587"
OTOMO_ID = "otomo_bungo_army_1586_1587"
TOYOTOMI_RELIEF_ID = "toyotomi_shikoku_relief_contingent_1586_1587"
TOYOTOMI_EXPEDITION_ID = "toyotomi_kyushu_expedition_army_1587"
SATSUMA_DOMAIN_ID = "satsuma_domain_kagoshima_batteries_1863"
SAIGO_REBELS_ID = "saigo_satsuma_rebel_army_1877"

EXPECTED_RAW_HASHES = {
    "hced-Kagoshima1863-1": "6bee09eb88e940e057c9ec14aee79864cc0c4994d596fc87508c4e6cf4da236e",
    "hced-Kagoshima1877-1": "e77f5c4f437e05c55403d16fdc81e38ef10d8dbee6f8d6d196863375e6a2216c",
    "hced-Kumamoto1877-1": "59fc818753c71c76b8852fefacb0e0d46b4417790829d0bad0f0e327bbdd1b04",
    "hced-Sendaigawa1587-1": "e24d408a3dbb99c45f9c476b53725ab501ec6168036319735c0d1193bce925d1",
    "hced-Tabaruzaka1877-1": "83efe46bc348b667b504b51151fe7d99e9ef3672c60c87c76adb91c10bb9e5b2",
    "hced-Takashiro1587-1": "a5a93f1cc2b70a99405c7f7bfe4b8b4364626bcd0b69d92dbd12e8de5c51f4f4",
    "hced-Toshimitsu1587-1": "f36557443b419ea5c254eedc7c068fd6af35709f855a7213acd7eac235d0ad78",
}

EXPECTED_EVENT_METADATA = {
    "hced-Toshimitsu1587-1": (
        "Battle of Hetsugigawa (Toshimitsu)",
        1587,
        "day",
        "win",
    ),
    "hced-Takashiro1587-1": (
        "Second Battle of Takajo (Nejirozaka)",
        1587,
        "year",
        "win",
    ),
    "hced-Sendaigawa1587-1": (
        "Battle near the Sendai River",
        1587,
        "year",
        "win",
    ),
    "hced-Kagoshima1863-1": (
        "Bombardment of Kagoshima",
        1863,
        "day_range",
        "draw",
    ),
    "hced-Kumamoto1877-1": (
        "Siege of Kumamoto Castle",
        1877,
        "day_range",
        "win",
    ),
    "hced-Tabaruzaka1877-1": (
        "Battle of Tabaruzaka",
        1877,
        "month",
        "win",
    ),
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Toshimitsu1587-1": (
        {SHIMAZU_ID},
        {OTOMO_ID, TOYOTOMI_RELIEF_ID},
    ),
    "hced-Takashiro1587-1": ({TOYOTOMI_EXPEDITION_ID}, {SHIMAZU_ID}),
    "hced-Sendaigawa1587-1": ({TOYOTOMI_EXPEDITION_ID}, {SHIMAZU_ID}),
    "hced-Kumamoto1877-1": ({"empire_japan"}, {SAIGO_REBELS_ID}),
    "hced-Tabaruzaka1877-1": ({"empire_japan"}, {SAIGO_REBELS_ID}),
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Wave8SatsumaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _load_jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _load_jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = json.loads(
            (ROOT / "build/hced-unresolved-label-funnel.json").read_text(encoding="utf-8")
        )
        cls.release_entities = {
            str(entity["id"]): entity
            for entity in json.loads((ROOT / "data/release/entities.json").read_text(encoding="utf-8"))
        }
        cls.release_events = json.loads((ROOT / "data/release/events.json").read_text(encoding="utf-8"))
        cls.release_metadata = json.loads(
            (ROOT / "data/release/metadata.json").read_text(encoding="utf-8")
        )
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "satsuma"
            or normalize_label(row.get("side_2_raw")) == "satsuma"
        ]

    def _installed(self) -> tuple[dict, dict]:
        entities = copy.deepcopy(self.release_entities)
        sources: dict[str, dict] = {}
        install_wave8_satsuma_entities(entities)
        install_wave8_satsuma_sources(sources)
        return entities, sources

    def _preintegration_events(self) -> list[dict]:
        return [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_SATSUMA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]

    def _emit(self, existing_events=None) -> tuple[dict, dict, list]:
        entities, sources = self._installed()
        existing = (
            self._preintegration_events()
            if existing_events is None
            else copy.deepcopy(existing_events)
        )
        events = promote_wave8_satsuma_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_funnel_and_queue_lock_the_complete_seven_row_exact_cohort(self) -> None:
        # Historical pre-promotion projection of the unresolved-label funnel;
        # the live file correctly drops the cohort once the lane is integrated.
        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": FUNNEL_CANDIDATE_ID_SHA256,
                    "events_touched": 7,
                    "failure_cases": {"zero_time_valid_candidates": 7},
                    "label": "satsuma",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 7,
                }
            ],
            "row_label_data": [
                {"blocker_labels": ["satsuma"], "candidate_id": candidate_id}
                for candidate_id in sorted(EXPECTED_RAW_HASHES)
            ],
        }
        scoped_rows = {
            str(row["candidate_id"]): row
            for row in historical_funnel["row_label_data"]
            if "satsuma" in row.get("blocker_labels", [])
        }
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(len(scoped_rows), 7)
        self.assertEqual(exact_ids, set(EXPECTED_RAW_HASHES))
        self.assertEqual(set(scoped_rows), exact_ids)
        self.assertEqual(WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS, exact_ids)

        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(scoped_rows))
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), FUNNEL_CANDIDATE_ID_SHA256)
        label_rows = [
            row for row in historical_funnel["labels"] if row.get("label") == "satsuma"
        ]
        self.assertEqual(len(label_rows), 1)
        label = label_rows[0]
        self.assertEqual(label["event_candidate_id_sha256"], FUNNEL_CANDIDATE_ID_SHA256)
        self.assertEqual(label["events_touched"], 7)
        self.assertEqual(label["unresolved_side_attempts"], 7)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 7)

        self.assertFalse(
            any(
                row.get("label") == "satsuma"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Satsuma lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id")) in WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS
                or "satsuma" in row.get("blocker_labels", [])
                for row in self.funnel.get("row_label_data", [])
            ),
            "resolved Satsuma candidate ids must be absent from the live funnel",
        )

    def test_exact_label_is_literal_and_each_locked_row_has_one_satsuma_side(self) -> None:
        for row in self.exact_rows:
            with self.subTest(candidate_id=row["candidate_id"]):
                labels = [
                    normalize_label(row.get("side_1_raw")),
                    normalize_label(row.get("side_2_raw")),
                ]
                self.assertEqual(labels.count("satsuma"), 1)
        variant = copy.deepcopy(self.hced_rows[0])
        variant["candidate_id"] = "hced-Satsuma-Domain-variant"
        variant["side_1_raw"] = "Satsuma Domain"
        variant["side_2_raw"] = "Test opponent"
        validate_wave8_satsuma_queue_contracts([*self.hced_rows, variant])

    def test_every_locked_row_hash_and_queue_disposition_is_exact(self) -> None:
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(rows), set(EXPECTED_RAW_HASHES))
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected_hash)
                disposition = WAVE8_SATSUMA_CONTRACTS.get(candidate_id) or (
                    WAVE8_SATSUMA_NONPROMOTIONS[candidate_id]
                )
                self.assertEqual(disposition["raw_row_sha256"], expected_hash)
        self.assertEqual(
            validate_wave8_satsuma_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )

    def test_each_raw_row_fingerprint_tamper_fails_closed(self) -> None:
        index = {
            str(row["candidate_id"]): position
            for position, row in enumerate(self.hced_rows)
        }
        for candidate_id in sorted(EXPECTED_RAW_HASHES):
            with self.subTest(candidate_id=candidate_id):
                rows = copy.deepcopy(self.hced_rows)
                rows[index[candidate_id]]["name"] += " changed"
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    validate_wave8_satsuma_queue_contracts(rows)

    def test_missing_duplicate_and_future_exact_rows_fail_closed(self) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Kumamoto1877-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            validate_wave8_satsuma_queue_contracts(missing)

        duplicate = [*self.hced_rows, copy.deepcopy(self.exact_rows[0])]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            validate_wave8_satsuma_queue_contracts(duplicate)

        future = copy.deepcopy(self.exact_rows[0])
        future["candidate_id"] = "hced-FutureSatsuma1900-1"
        future["source_record_id"] = "FutureSatsuma1900"
        future["year_best"] = future["year_low"] = future["year_high"] = 1900
        with self.assertRaisesRegex(ValueError, "exact Satsuma inventory changed"):
            validate_wave8_satsuma_queue_contracts([*self.hced_rows, future])

    def test_final_signature_covers_every_material_fixture_and_disposition(self) -> None:
        payload = {
            "contracts": WAVE8_SATSUMA_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_SATSUMA_ENTITIES,
            "expected_candidate_ids": sorted(WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS),
            "hced_duplicate_dispositions": WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS,
            "holds": WAVE8_SATSUMA_HOLDS,
            "integration_dispositions": WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_SATSUMA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_SATSUMA_SOURCES,
            "terminal_exclusions": WAVE8_SATSUMA_TERMINAL_EXCLUSIONS,
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_satsuma_audit_signature(), WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE,
            "719ebd1ac11732998e2a2b2490b055518e3da616596fa2c859d366825fa92076",
        )

    def test_disposition_sets_are_complete_disjoint_and_non_rateable_where_required(self) -> None:
        self.assertEqual(len(WAVE8_SATSUMA_CONTRACT_IDS), 6)
        self.assertEqual(WAVE8_SATSUMA_HOLD_IDS, frozenset())
        self.assertEqual(
            WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS,
            {"hced-Kagoshima1877-1"},
        )
        self.assertIs(WAVE8_SATSUMA_EXCLUSIONS, WAVE8_SATSUMA_TERMINAL_EXCLUSIONS)
        self.assertEqual(WAVE8_SATSUMA_EXCLUSION_IDS, WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS)
        self.assertEqual(WAVE8_SATSUMA_RESERVED_IDS, set(EXPECTED_RAW_HASHES))
        self.assertFalse(WAVE8_SATSUMA_CONTRACT_IDS & WAVE8_SATSUMA_EXCLUSION_IDS)
        self.assertEqual(set(WAVE8_SATSUMA_NONPROMOTIONS), WAVE8_SATSUMA_EXCLUSION_IDS)

        exclusion = WAVE8_SATSUMA_TERMINAL_EXCLUSIONS["hced-Kagoshima1877-1"]
        forbidden = {
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
            "losers",
        }
        self.assertFalse(forbidden & set(exclusion))
        self.assertTrue(exclusion["terminal_exclusion"])
        self.assertTrue(exclusion["full_row_audited"])

    def test_sources_are_independent_authoritative_parseable_and_exactly_consumed(self) -> None:
        source_ids = {str(source["id"]) for source in WAVE8_SATSUMA_SOURCES}
        families = {str(source["source_family_id"]) for source in WAVE8_SATSUMA_SOURCES}
        self.assertEqual(len(source_ids), 14)
        self.assertEqual(len(families), 14)
        for source in WAVE8_SATSUMA_SOURCES:
            with self.subTest(source_id=source["id"]):
                parsed = Source.from_dict(source)
                self.assertEqual(parsed.id, source["id"])
                self.assertTrue(source["url"].startswith("https://"))
                self.assertEqual(source["accessed"], "2026-07-16")
                self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))

        consumed = {
            source_id
            for contract in WAVE8_SATSUMA_CONTRACTS.values()
            for source_id in contract["evidence_refs"]
        }
        consumed.update(
            source_id
            for item in WAVE8_SATSUMA_NONPROMOTIONS.values()
            for source_id in item["evidence_refs"]
        )
        consumed.update(
            source_id
            for entity in WAVE8_SATSUMA_ENTITIES
            for source_id in entity["source_ids"]
        )
        self.assertEqual(consumed, source_ids)
        publishers = " ".join(str(source["publisher"]) for source in WAVE8_SATSUMA_SOURCES)
        self.assertIn("University of Tokyo", publishers)
        self.assertIn("National Archives of Japan", publishers)
        self.assertIn("Agency for Cultural Affairs", publishers)

    def test_entities_are_time_bounded_parseable_and_do_not_bridge_satsumas(self) -> None:
        entities = {str(entity["id"]): entity for entity in WAVE8_SATSUMA_ENTITIES}
        self.assertEqual(
            set(entities),
            {
                SHIMAZU_ID,
                OTOMO_ID,
                TOYOTOMI_RELIEF_ID,
                TOYOTOMI_EXPEDITION_ID,
                SATSUMA_DOMAIN_ID,
                SAIGO_REBELS_ID,
            },
        )
        self.assertEqual(
            (entities[SHIMAZU_ID]["start_year"], entities[SHIMAZU_ID]["end_year"]),
            (1586, 1587),
        )
        self.assertEqual(
            (entities[SATSUMA_DOMAIN_ID]["start_year"], entities[SATSUMA_DOMAIN_ID]["end_year"]),
            (1863, 1863),
        )
        self.assertEqual(
            (entities[SAIGO_REBELS_ID]["start_year"], entities[SAIGO_REBELS_ID]["end_year"]),
            (1877, 1877),
        )
        for entity in WAVE8_SATSUMA_ENTITIES:
            with self.subTest(entity_id=entity["id"]):
                parsed = Entity.from_dict(entity)
                self.assertEqual(parsed.id, entity["id"])
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn(
                    "no rating is inherited",
                    entity["continuity_note"].casefold(),
                )
        self.assertIn("abolished in 1871", entities[SAIGO_REBELS_ID]["continuity_note"])
        self.assertIn("abolished domain after 1871", entities[SATSUMA_DOMAIN_ID]["continuity_note"])
        self.assertNotEqual(SHIMAZU_ID, SATSUMA_DOMAIN_ID)
        self.assertNotEqual(SATSUMA_DOMAIN_ID, SAIGO_REBELS_ID)

    def test_installers_are_idempotent_copy_safe_and_fail_on_collisions(self) -> None:
        entities, sources = self._installed()
        install_wave8_satsuma_entities(entities)
        install_wave8_satsuma_sources(sources)
        fixture_entity_ids = {entity["id"] for entity in WAVE8_SATSUMA_ENTITIES}
        self.assertEqual(len([key for key in entities if key in fixture_entity_ids]), 6)
        self.assertEqual(set(sources), {source["id"] for source in WAVE8_SATSUMA_SOURCES})

        installed_name = entities[SHIMAZU_ID]["name"]
        entities[SHIMAZU_ID]["name"] = "locally mutated"
        fixture = next(item for item in WAVE8_SATSUMA_ENTITIES if item["id"] == SHIMAZU_ID)
        self.assertEqual(fixture["name"], installed_name)

        entity_collision = copy.deepcopy(self.release_entities)
        entity_collision[SHIMAZU_ID] = {"id": SHIMAZU_ID, "name": "collision"}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_satsuma_entities(entity_collision)

        source_collision = {WAVE8_SATSUMA_SOURCES[0]["id"]: {"id": WAVE8_SATSUMA_SOURCES[0]["id"]}}
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_satsuma_sources(source_collision)

    def test_contract_metadata_dates_outcomes_and_provenance_are_exact(self) -> None:
        self.assertEqual(set(WAVE8_SATSUMA_CONTRACTS), set(EXPECTED_EVENT_METADATA))
        source_by_id = {source["id"]: source for source in WAVE8_SATSUMA_SOURCES}
        for candidate_id, expected in EXPECTED_EVENT_METADATA.items():
            with self.subTest(candidate_id=candidate_id):
                contract = WAVE8_SATSUMA_CONTRACTS[candidate_id]
                canonical = contract["canonical_event"]
                self.assertEqual(
                    (
                        canonical["name"],
                        canonical["year"],
                        canonical["date_precision"],
                        contract["result_type"],
                    ),
                    expected,
                )
                self.assertEqual(canonical["year_low"], canonical["year_high"])
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertTrue(contract["actor_override"])
                self.assertEqual(
                    contract["direct_provenance"]["reviewed_date"],
                    canonical["date_text"],
                )
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                expected_families = sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                )
                self.assertEqual(contract["outcome_source_family_ids"], expected_families)
                self.assertGreaterEqual(len(expected_families), 2)
        self.assertEqual(WAVE8_SATSUMA_OUTCOME_OVERRIDES, {})

    def test_promoter_emits_exact_ids_names_and_valid_event_models(self) -> None:
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_SATSUMA_CONTRACT_IDS)
        self.assertEqual(len(events), 6)
        self.assertNotIn("hced-Kagoshima1877-1", by_candidate)
        for candidate_id, event in by_candidate.items():
            with self.subTest(candidate_id=candidate_id):
                model = Event.from_dict(event)
                self.assertEqual(model.hced_candidate_id, candidate_id)
                self.assertEqual(event["name"], EXPECTED_EVENT_METADATA[candidate_id][0])
                self.assertEqual(event["year"], EXPECTED_EVENT_METADATA[candidate_id][1])
                slug = normalize_label(candidate_id).replace(" ", "_")
                self.assertEqual(event["id"], f"{EVENT_ID_PREFIX}{slug}")
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["status"], "complete")
                self.assertTrue(set(event["outcome_source_ids"]) <= set(event["source_ids"]))

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_SATSUMA_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        if not integrated:
            return
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            set(WAVE8_SATSUMA_CONTRACT_IDS),
        )
        self.assertEqual(
            len({str(event["id"]) for event in integrated}),
            len(WAVE8_SATSUMA_CONTRACT_IDS),
        )
        self.assertLessEqual(
            {str(entity["id"]) for entity in WAVE8_SATSUMA_ENTITIES},
            set(self.release_entities),
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_satsuma_hced_events"], 6)
        self.assertEqual(
            promotion["wave8_satsuma_candidate_ids"],
            sorted(WAVE8_SATSUMA_CONTRACT_IDS),
        )
        self.assertEqual(
            promotion["wave8_satsuma_queue_validation"],
            {
                "holds": 0,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )

    def test_promoted_winners_losers_and_toshimitsu_coalition_are_mechanical(self) -> None:
        _, _, events = self._emit(existing_events=[])
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        for candidate_id, expected_sides in EXPECTED_WINNERS_AND_LOSERS.items():
            with self.subTest(candidate_id=candidate_id):
                expected_winners, expected_losers = expected_sides
                participants = by_candidate[candidate_id]["participants"]
                winners = {
                    participant["entity_id"]
                    for participant in participants
                    if "victory" in participant["result_class"]
                }
                losers = {
                    participant["entity_id"]
                    for participant in participants
                    if "defeat" in participant["result_class"]
                }
                self.assertEqual(winners, expected_winners)
                self.assertEqual(losers, expected_losers)

        toshimitsu = by_candidate["hced-Toshimitsu1587-1"]
        self.assertEqual(len(toshimitsu["participants"]), 3)
        self.assertEqual(
            {participant["entity_id"] for participant in toshimitsu["participants"]},
            {SHIMAZU_ID, OTOMO_ID, TOYOTOMI_RELIEF_ID},
        )
        toshimitsu_entities = {
            participant["entity_id"] for participant in toshimitsu["participants"]
        }
        self.assertNotIn(TOYOTOMI_EXPEDITION_ID, toshimitsu_entities)

    def test_kagoshima_1863_remains_a_draw_without_invented_winner(self) -> None:
        raw = next(row for row in self.exact_rows if row["candidate_id"] == "hced-Kagoshima1863-1")
        self.assertEqual(raw["winner_raw"], "Draw")
        self.assertIsNone(raw["loser_raw"])
        self.assertFalse(raw["winner_loser_complete"])
        contract = WAVE8_SATSUMA_CONTRACTS["hced-Kagoshima1863-1"]
        self.assertEqual(contract["result_type"], "draw")
        self.assertNotIn("winner_side", contract)
        self.assertFalse(contract["source_outcome_override"])

        _, _, events = self._emit(existing_events=[])
        event = next(
            item for item in events if item["hced_candidate_id"] == "hced-Kagoshima1863-1"
        )
        self.assertEqual(
            {participant["entity_id"] for participant in event["participants"]},
            {"united_kingdom", SATSUMA_DOMAIN_ID},
        )
        self.assertEqual(
            {participant["result_class"] for participant in event["participants"]},
            {"stalemate_or_inconclusive"},
        )
        self.assertTrue(
            all(
                participant["termination"] == "inconclusive_engagement"
                for participant in event["participants"]
            )
        )

    def test_kagoshima_1877_is_terminally_excluded_to_pinned_shiroyama(self) -> None:
        exclusion = WAVE8_SATSUMA_TERMINAL_EXCLUSIONS["hced-Kagoshima1877-1"]
        self.assertEqual(exclusion["duplicate_of_hced_candidate_id"], SHIROYAMA_ID)
        self.assertEqual(exclusion["duplicate_raw_row_sha256"], SHIROYAMA_HASH)
        self.assertIn("double-rate", exclusion["hold_reason"])

        duplicate = WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS["hced-Kagoshima1877-1"]
        self.assertEqual(duplicate["related_hced_candidate_id"], SHIROYAMA_ID)
        self.assertEqual(duplicate["related_raw_row_sha256"], SHIROYAMA_HASH)
        self.assertEqual(set(WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS), {SHIROYAMA_ID})
        cross_lane = WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS[SHIROYAMA_ID]
        self.assertIsNone(cross_lane["owner_module"])
        self.assertEqual(cross_lane["raw_row_sha256"], SHIROYAMA_HASH)
        self.assertNotIn(SHIROYAMA_ID, WAVE8_SATSUMA_RESERVED_IDS)

        row = next(item for item in self.hced_rows if item["candidate_id"] == SHIROYAMA_ID)
        self.assertEqual(canonical_hced_row_sha256(row), SHIROYAMA_HASH)
        self.assertEqual(row["name"], "Shiroyama")
        self.assertEqual(row["side_2_raw"], "Saiga Takamori")

    def test_integration_pins_shiroyama_and_records_zero_iwbd_or_release_twins(self) -> None:
        result = validate_wave8_satsuma_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(
            result,
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "hced_duplicate_dispositions": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 7,
            },
        )
        self.assertEqual(WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS,
            WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
        )

        missing = [row for row in self.hced_rows if row.get("candidate_id") != SHIROYAMA_ID]
        with self.assertRaisesRegex(ValueError, "expected one cross-lane Shiroyama"):
            validate_wave8_satsuma_integration_dispositions(missing, self.iwbd_rows)

        changed = copy.deepcopy(self.hced_rows)
        row = next(item for item in changed if item.get("candidate_id") == SHIROYAMA_ID)
        row["name"] = "Changed Shiroyama"
        with self.assertRaisesRegex(ValueError, "Shiroyama fingerprint changed"):
            validate_wave8_satsuma_integration_dispositions(changed, self.iwbd_rows)

    def test_duplicate_negative_audit_fails_on_future_hced_iwbd_and_release_twins(self) -> None:
        self.assertEqual(set(WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT), set(EXPECTED_RAW_HASHES))

        hced_twin = copy.deepcopy(self.hced_rows[0])
        hced_twin.update(
            {
                "candidate_id": "hced-FutureHetsugigawa1587-1",
                "name": "Hetsugigawa",
                "side_1_raw": "Shimazu",
                "side_2_raw": "Otomo",
                "year_best": 1587,
                "year_low": 1587,
                "year_high": 1587,
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed cross-lane HCED twin"):
            validate_wave8_satsuma_integration_dispositions(
                [*self.hced_rows, hced_twin],
                self.iwbd_rows,
            )

        iwbd_twin = {
            "candidate_id": "iwbd-future-tabaruzaka",
            "name": "Battle of Tabaruzaka",
            "start_date": "1877-03-04",
            "end_date": "1877-03-20",
        }
        with self.assertRaisesRegex(ValueError, "plausible IWBD overlap"):
            validate_wave8_satsuma_integration_dispositions(
                self.hced_rows,
                [*self.iwbd_rows, iwbd_twin],
            )

        release_twin = {
            "id": "future_release_kumamoto",
            "name": "Kumamoto Castle",
            "year": 1877,
            "end_year": 1877,
        }
        with self.assertRaisesRegex(ValueError, "existing-release duplicate"):
            validate_wave8_satsuma_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*self.release_events, release_twin],
            )

    def test_promoted_location_points_are_all_withheld_but_country_is_retained(self) -> None:
        global_points_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        global_countries_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit(existing_events=[])
        self.assertEqual(WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS, WAVE8_SATSUMA_CONTRACT_IDS)
        self.assertEqual(WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            set(WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS),
            WAVE8_SATSUMA_CONTRACT_IDS,
        )
        for event in events:
            with self.subTest(candidate_id=event["hced_candidate_id"]):
                self.assertNotIn("geometry", event)
                self.assertEqual(event["modern_location_country"], "Japan")
                self.assertIn("location_provenance", event)
                review = WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS[
                    event["hced_candidate_id"]
                ]
                self.assertEqual(review["actions"], ["withhold_point"])
                self.assertTrue(review["reason"])
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), global_points_before)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), global_countries_before)
        self.assertEqual(
            wave8_satsuma_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": WAVE8_SATSUMA_CONTRACT_IDS,
            },
        )
        self.assertEqual(
            WAVE8_SATSUMA_LOCATION_QUARANTINE_ADDITIONS,
            wave8_satsuma_location_quarantine_additions(),
        )

    def test_promoter_fails_on_missing_or_out_of_window_entities(self) -> None:
        entities, _ = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(SHIMAZU_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_satsuma_contracts(self.hced_rows, missing, [])

        bad_uk = copy.deepcopy(entities)
        bad_uk["united_kingdom"]["start_year"] = 1900
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_satsuma_contracts(self.hced_rows, bad_uk, [])

        bad_japan = copy.deepcopy(entities)
        bad_japan["empire_japan"]["end_year"] = 1876
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_satsuma_contracts(self.hced_rows, bad_japan, [])

    def test_promoter_fails_on_candidate_and_event_key_collisions(self) -> None:
        entities, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_satsuma_contracts(
                self.hced_rows,
                entities,
                [{"hced_candidate_id": "hced-Kumamoto1877-1", "name": "Other", "year": 1877}],
            )

        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_satsuma_contracts(
                self.hced_rows,
                entities,
                [{"id": "existing", "name": "Battle of Tabaruzaka", "year": 1877}],
            )

        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_satsuma_contracts(
                self.hced_rows,
                entities,
                [{"id": "existing", "name": "Tabaruzak", "year": 1877}],
            )

    def test_metadata_helpers_report_all_seven_rows_and_three_historical_cohorts(self) -> None:
        self.assertEqual(
            wave8_satsuma_cohort_counts(),
            {
                "anglo_satsuma_war_1863": 1,
                "satsuma_rebellion_1877": 3,
                "shimazu_toyotomi_kyushu_campaign_1586_1587": 3,
            },
        )
        self.assertEqual(
            wave8_satsuma_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "hced_duplicate_dispositions": 1,
                "holds": 0,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 7,
                "new_entities": 6,
                "new_sources": 14,
                "newly_rated_events": 6,
                "outcome_overrides": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
