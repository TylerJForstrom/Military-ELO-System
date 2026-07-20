import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_followup_b as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_followup_b_"

BALAPUR = "hced-Balapur1720-1"
KHARDA = "hced-Kharda1795-1"
RATANPUR = "hced-Ratanpur1720-1"
SIKASSO = "hced-Sikasso1887-1888-1"

MARATHA = "maratha_confederacy"
HYDERABAD = "hyderabad_asaf_jahi_state_1724"
KENEDOUGOU = "tieba_led_kenedougou_defense_sikasso_1887_1888"
WASSOULOU = "wassoulou_empire_samori_ture"
NIZAM_FORCE = "nizam_ul_mulk_deccan_campaign_force_1720"
ALAM_ALI_FORCE = "alam_ali_khan_sayyid_aligned_coalition_balapur_1720"
DILAWAR_ALI_FORCE = "dilawar_ali_khan_sayyid_aligned_force_ratanpur_1720"

EXPECTED_HASHES = {
    BALAPUR: "6c8a5c665b336e0bacd5602d1bb923b1267ea6a0b2f97e8ef8e96186823f42a2",
    KHARDA: "83be482c4b3d480c1339f7e7d5d3b551742322f23a551c10fca992562b2d12eb",
    RATANPUR: "692aad2edf66fc1ea31585e2900fee5990ac92c7df626fb2a4a2d2c08d3e476f",
    SIKASSO: "2787ccfe72f8d8b9dc04323dd69ad8b175a57047f3622102d8ab9c89b5684c4b",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8FollowupBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        new_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_FOLLOWUP_B_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        new_source_ids = set(lane.WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS)
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_FOLLOWUP_B_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        lane.install_wave8_followup_b_entities(entities)
        lane.install_wave8_followup_b_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_followup_b_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def _materialized(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_followup_b_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, [*existing, *events], events

    def test_exact_candidate_inventory_row_hashes_and_raw_contracts(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") in EXPECTED_HASHES
        ]
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_FOLLOWUP_B_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                raw_contract = lane.WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[
                    candidate_id
                ]
                self.assertEqual(
                    {key: row.get(key) for key in raw_contract},
                    raw_contract,
                )
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_funnel_and_reservation_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_followup_b_queue_contracts(self.hced_rows),
            {
                "exact_candidate_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
            },
        )
        self.assertEqual(
            lane.validate_wave8_followup_b_funnel(self.funnel),
            {
                "leaked_labels": 0,
                "required_absent_labels": 2,
                "reserved_candidate_ids": 4,
                "reserved_candidate_rows_present": 0,
            },
        )
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_B_RESERVED_IDS,
            frozenset(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_B_RESERVED_IDS,
            lane.WAVE8_FOLLOWUP_B_CONTRACT_IDS,
        )

    def test_contracts_are_wins_with_exact_confidence_and_no_fallback(self) -> None:
        expected_confidence = {
            BALAPUR: 0.92,
            KHARDA: 0.90,
            RATANPUR: 0.90,
            SIKASSO: 0.94,
        }
        for candidate_id, contract in lane.WAVE8_FOLLOWUP_B_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(contract["disposition"], "promote")
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertEqual(contract["confidence"], expected_confidence[candidate_id])
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertFalse(contract["source_date_override"])
                self.assertTrue(contract["candidate_key_required"])
                self.assertFalse(contract["generic_label_fallback"])
                self.assertEqual(contract["unknown_outcome_policy"], "reject")

    def test_new_entities_are_alias_free_and_exactly_bounded(self) -> None:
        entities = {
            str(entity["id"]): entity for entity in lane.WAVE8_FOLLOWUP_B_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {KENEDOUGOU, NIZAM_FORCE, ALAM_ALI_FORCE, DILAWAR_ALI_FORCE},
        )
        self.assertEqual(
            (entities[KENEDOUGOU]["start_year"], entities[KENEDOUGOU]["end_year"]),
            (1887, 1888),
        )
        self.assertEqual(
            (entities[NIZAM_FORCE]["start_year"], entities[NIZAM_FORCE]["end_year"]),
            (1720, 1720),
        )
        self.assertEqual(
            (entities[ALAM_ALI_FORCE]["start_year"], entities[ALAM_ALI_FORCE]["end_year"]),
            (1720, 1720),
        )
        self.assertEqual(
            (
                entities[DILAWAR_ALI_FORCE]["start_year"],
                entities[DILAWAR_ALI_FORCE]["end_year"],
            ),
            (1720, 1720),
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            Entity.from_dict(entity)
        self.assertIn(
            "asserts neither a reign date nor the state's historical lifetime",
            entities[KENEDOUGOU]["continuity_note"],
        )
        self.assertIn(
            "never be extended to or merged with Hyderabad State",
            entities[NIZAM_FORCE]["continuity_note"],
        )

    def test_installation_does_not_mutate_existing_identity_records(self) -> None:
        existing_ids = set(lane.WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS)
        before = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) in existing_ids
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        lane.install_wave8_followup_b_entities(entities)
        self.assertEqual({entity_id: entities[entity_id] for entity_id in existing_ids}, before)
        for entity_id, contract in lane.WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS.items():
            self.assertEqual(
                {key: entities[entity_id].get(key) for key in contract},
                contract,
            )
        composite = "marathas tukaji hulkar berar"
        all_aliases = {
            alias.lower()
            for entity in lane.WAVE8_FOLLOWUP_B_ENTITIES
            for alias in entity["aliases"]
        }
        self.assertNotIn(composite, all_aliases)

    def test_sources_parse_and_role_family_provenance_is_closed(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_FOLLOWUP_B_SOURCES
        }
        self.assertEqual(len(source_by_id), 10)
        self.assertEqual(lane.WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS, {"telangana_asaf_jahi"})
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS), 9)
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertTrue(source["source_family_id"])
            self.assertTrue(source["url"].startswith("https://"))
        for candidate_id, contract in lane.WAVE8_FOLLOWUP_B_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    set(contract["evidence_refs"]),
                    set(contract["identity_source_ids"])
                    | set(contract["outcome_source_ids"])
                    | set(contract["boundary_source_ids"]),
                )
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                for source_id in contract["identity_source_ids"]:
                    self.assertIn(
                        "identity_boundary_or_context_reference",
                        source_by_id[source_id]["evidence_roles"],
                    )
                for source_id in contract["outcome_source_ids"]:
                    self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

    def test_promoted_events_have_exact_actors_outcomes_and_confidence(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            BALAPUR: ({NIZAM_FORCE}, {ALAM_ALI_FORCE}, 0.92),
            KHARDA: ({MARATHA}, {HYDERABAD}, 0.90),
            RATANPUR: ({NIZAM_FORCE}, {DILAWAR_ALI_FORCE}, 0.90),
            SIKASSO: ({KENEDOUGOU}, {WASSOULOU}, 0.94),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winners, losers, confidence) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                Event.from_dict(event)
                self.assertEqual(event["confidence"], confidence)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(
                    {
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["side"] == "side_a"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["side"] == "side_b"
                    },
                    losers,
                )
                self.assertFalse(
                    any(
                        "inconclusive" in participant["termination"]
                        or "inconclusive" in participant["result_class"]
                        for participant in event["participants"]
                    )
                )

    def test_point_quarantine_is_exactly_balapur_and_ratanpur(self) -> None:
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS,
            {BALAPUR, RATANPUR},
        )
        self.assertFalse(lane.WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS),
            {BALAPUR, RATANPUR},
        )
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                if candidate_id in {BALAPUR, RATANPUR}:
                    self.assertNotIn("geometry", event)
                    self.assertEqual(event["modern_location_country"], "India")
                else:
                    self.assertIn("geometry", event)

    def test_release_inventory_and_final_audit_are_exact(self) -> None:
        entities, sources, release_events, _ = self._materialized()
        expected_inventory = {
            "lane_entities": 4,
            "lane_events": 4,
            "new_source_records": 9,
            "outside_entity_uses": 0,
            "point_quarantines": 2,
            "reused_source_records": 1,
            "source_contracts": 10,
        }
        self.assertEqual(
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                release_events,
            ),
            expected_inventory,
        )
        audit = lane.validate_wave8_followup_b_final_audit(
            entities,
            sources,
            release_events,
            lane.wave8_followup_b_metadata(),
        )
        self.assertEqual(audit["release_inventory"], expected_inventory)
        self.assertEqual(
            audit["measured_audit_signature"],
            lane.WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(audit["candidate_ids"], sorted(EXPECTED_HASHES))

    def test_final_audit_signature_is_independently_reproducible(self) -> None:
        payload = {
            "contracts": lane.WAVE8_FOLLOWUP_B_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": lane.WAVE8_FOLLOWUP_B_ENTITIES,
            "existing_entity_contracts": lane.WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS,
            "expected_release_event_ids": lane.WAVE8_FOLLOWUP_B_EXPECTED_RELEASE_EVENT_IDS,
            "expected_scale_levels": lane._EXPECTED_SCALE_LEVELS,
            "event_aliases": {
                candidate_id: sorted(aliases)
                for candidate_id, aliases in sorted(lane._EVENT_ALIASES.items())
            },
            "funnel": lane.WAVE8_FOLLOWUP_B_FUNNEL_AUDIT,
            "holds": lane.WAVE8_FOLLOWUP_B_HOLDS,
            "location_reasons": lane.WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS,
            "new_source_ids": sorted(lane.WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS),
            "point_quarantine_additions": sorted(
                lane.WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS
            ),
            "raw_row_contracts": lane.WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS,
            "reserved_ids": sorted(lane.WAVE8_FOLLOWUP_B_RESERVED_IDS),
            "reused_source_ids": sorted(lane.WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS),
            "row_hashes": lane.WAVE8_FOLLOWUP_B_ROW_HASHES,
            "sources": lane.WAVE8_FOLLOWUP_B_SOURCES,
            "twin_match_keys": sorted(
                [year, normalized_name]
                for year, normalized_name in lane._DUPLICATE_MATCH_KEYS
            ),
        }
        independent = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertNotEqual(lane.WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE, "__PENDING__")
        self.assertEqual(independent, lane.WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(lane.wave8_followup_b_audit_signature(), independent)

    def test_counts_cohorts_and_metadata_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_followup_b_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 4,
                "new_sources": 9,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 4,
                "reused_sources": 1,
                "reviewed_hced_rows": 4,
                "source_contracts": 10,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_followup_b_cohort_counts(),
            {
                "maratha_nizam_war_1795": 1,
                "nizam_ul_mulk_1720_deccan_campaign": 2,
                "tieba_kenedougou_wassoulou_war": 1,
            },
        )
        metadata = lane.wave8_followup_b_metadata()
        self.assertEqual(metadata["promoted_candidate_ids"], sorted(EXPECTED_HASHES))
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE,
        )

    def test_integration_duplicate_audit_is_closed(self) -> None:
        self.assertEqual(
            lane.validate_wave8_followup_b_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        duplicate = {"candidate_id": "iwbd-copy", "name": "Kharda", "year": 1795}
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_followup_b_integration_dispositions(
                self.hced_rows,
                [*self.iwbd_rows, duplicate],
                self.release_events,
            )

    def test_installers_are_idempotent_and_fail_on_collision(self) -> None:
        entities, sources, _ = self._installed()
        lane.install_wave8_followup_b_entities(entities)
        lane.install_wave8_followup_b_sources(sources)
        entities[KENEDOUGOU]["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_followup_b_entities(entities)
        sources["wave8_followup_b_ird_etats_kong"]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_followup_b_sources(sources)

    def test_row_hash_tampering_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(row for row in tampered if row.get("candidate_id") == KHARDA)
        row["side_1_raw"] = "Marathas"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_followup_b_queue_contracts(tampered)

    def test_source_role_tampering_fails_closed(self) -> None:
        source = next(
            source
            for source in lane.WAVE8_FOLLOWUP_B_SOURCES
            if source["id"] == "wave8_followup_b_maharashtra_kharda_places"
        )
        original = list(source["evidence_roles"])
        try:
            source["evidence_roles"] = ["identity_boundary_or_context_reference"]
            with self.assertRaisesRegex(ValueError, "outcome source role"):
                lane.wave8_followup_b_counts()
        finally:
            source["evidence_roles"] = original
        self.assertEqual(
            lane.wave8_followup_b_audit_signature(),
            lane.WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE,
        )

    def test_source_family_tampering_fails_closed(self) -> None:
        source = next(
            source
            for source in lane.WAVE8_FOLLOWUP_B_SOURCES
            if source["id"] == "wave8_followup_b_openedition_ird_cotton"
        )
        original = source["source_family_id"]
        try:
            source["source_family_id"] = "tampered_family"
            with self.assertRaisesRegex(ValueError, "source family"):
                lane.wave8_followup_b_counts()
        finally:
            source["source_family_id"] = original

    def test_chronology_tampering_fails_closed(self) -> None:
        canonical = lane.WAVE8_FOLLOWUP_B_CONTRACTS[RATANPUR]["canonical_event"]
        original = canonical["year_low"]
        try:
            canonical["year_low"] = 1721
            with self.assertRaisesRegex(ValueError, "chronology"):
                lane.wave8_followup_b_counts()
        finally:
            canonical["year_low"] = original

    def test_unknown_or_draw_outcome_tampering_fails_closed(self) -> None:
        tampered_rows = copy.deepcopy(self.hced_rows)
        row = next(row for row in tampered_rows if row.get("candidate_id") == SIKASSO)
        row["winner_raw"] = "Unknown"
        with self.assertRaises(ValueError):
            lane.validate_wave8_followup_b_queue_contracts(tampered_rows)

        contract = lane.WAVE8_FOLLOWUP_B_CONTRACTS[SIKASSO]
        original = contract["result_type"]
        try:
            contract["result_type"] = "draw"
            with self.assertRaisesRegex(ValueError, "outcome or exact-key"):
                lane.wave8_followup_b_counts()
        finally:
            contract["result_type"] = original

    def test_identity_bound_and_hyderabad_back_projection_tampering_fails(self) -> None:
        entities, _, existing = self._installed()
        entities[KENEDOUGOU]["start_year"] = 1888
        with self.assertRaisesRegex(ValueError, "exact entity drift"):
            lane.promote_wave8_followup_b_contracts(
                self.hced_rows,
                entities,
                existing,
            )

        entities, _, existing = self._installed()
        entities[HYDERABAD]["start_year"] = 1720
        with self.assertRaisesRegex(ValueError, "existing entity drift"):
            lane.promote_wave8_followup_b_contracts(
                self.hced_rows,
                entities,
                existing,
            )

    def test_release_outcome_and_quarantine_tampering_fails_closed(self) -> None:
        entities, sources, release_events, emitted = self._materialized()
        tampered = copy.deepcopy(release_events)
        sikasso = next(event for event in tampered if event.get("hced_candidate_id") == SIKASSO)
        sikasso["participants"][0]["termination"] = "inconclusive_engagement"
        with self.assertRaisesRegex(ValueError, "release outcome drift"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                tampered,
            )

        for field, value in (
            ("side", "side_b"),
            ("result_class", "stalemate_or_inconclusive"),
            ("evidence_confidence", 0.10),
            (
                "outcome",
                {
                    "battlefield_control": 0.5,
                    "mission_objective": 0.5,
                    "force_preservation": 0.5,
                    "positional_gain": 0.5,
                },
            ),
        ):
            with self.subTest(field=field):
                tampered = copy.deepcopy(release_events)
                event = next(
                    item
                    for item in tampered
                    if item.get("hced_candidate_id") == SIKASSO
                )
                event["participants"][0][field] = value
                with self.assertRaisesRegex(ValueError, "release outcome drift"):
                    lane.validate_wave8_followup_b_release_inventory(
                        entities,
                        sources,
                        tampered,
                    )

        for field, value in (
            ("event_type", "campaign"),
            ("war_type", "interstate"),
            ("aliases", []),
        ):
            with self.subTest(event_field=field):
                tampered = copy.deepcopy(release_events)
                event = next(
                    item
                    for item in tampered
                    if item.get("hced_candidate_id") == BALAPUR
                )
                event[field] = value
                with self.assertRaisesRegex(ValueError, "release event drift"):
                    lane.validate_wave8_followup_b_release_inventory(
                        entities,
                        sources,
                        tampered,
                    )

        tampered = copy.deepcopy(release_events)
        balapur = next(event for event in tampered if event.get("hced_candidate_id") == BALAPUR)
        balapur["geometry"] = {"type": "Point", "coordinates": [76.0, 20.0]}
        with self.assertRaisesRegex(ValueError, "quarantined point leaked"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                tampered,
            )
        tampered = copy.deepcopy(release_events)
        kharda = next(
            event for event in tampered if event.get("hced_candidate_id") == KHARDA
        )
        kharda["geometry"] = None
        with self.assertRaisesRegex(ValueError, "unexpected point quarantine"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                tampered,
            )
        self.assertEqual(len(emitted), 4)

    def test_release_inventory_missing_or_extra_lane_event_fails_closed(self) -> None:
        entities, sources, release_events, emitted = self._materialized()
        missing = [event for event in release_events if event is not emitted[0]]
        with self.assertRaisesRegex(ValueError, "release event inventory"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                missing,
            )

        extra = copy.deepcopy(emitted[0])
        extra["id"] = f"{EVENT_PREFIX}unexpected"
        with self.assertRaisesRegex(ValueError, "release event inventory"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                [*release_events, extra],
            )

    def test_new_identity_use_outside_exact_candidates_fails_closed(self) -> None:
        entities, sources, release_events, _ = self._materialized()
        leaked = {
            "id": "uncontracted_kenedougou_rate",
            "name": "Uncontracted Kenedougou event",
            "year": 1889,
            "participants": [{"entity_id": KENEDOUGOU}],
        }
        with self.assertRaisesRegex(ValueError, "outside exact contracts"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                sources,
                [*release_events, leaked],
            )

    def test_release_entity_source_and_partial_final_audit_tampering_fails(self) -> None:
        entities, sources, release_events, _ = self._materialized()
        bad_entities = copy.deepcopy(entities)
        bad_entities[NIZAM_FORCE]["end_year"] = 1724
        with self.assertRaisesRegex(ValueError, "exact entity drift"):
            lane.validate_wave8_followup_b_release_inventory(
                bad_entities,
                sources,
                release_events,
            )

        bad_sources = copy.deepcopy(sources)
        bad_sources["telangana_asaf_jahi"]["source_family_id"] = "tampered"
        with self.assertRaisesRegex(ValueError, "release source drift"):
            lane.validate_wave8_followup_b_release_inventory(
                entities,
                bad_sources,
                release_events,
            )
        bad_metadata = lane.wave8_followup_b_metadata()
        bad_metadata["counts"]["newly_rated_events"] = 5
        with self.assertRaisesRegex(ValueError, "metadata drift"):
            lane.validate_wave8_followup_b_final_audit(
                entities,
                sources,
                release_events,
                bad_metadata,
            )

    def test_installers_are_atomic_on_late_collision(self) -> None:
        new_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_FOLLOWUP_B_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        entities[NIZAM_FORCE] = {
            **copy.deepcopy(lane.WAVE8_FOLLOWUP_B_ENTITIES[1]),
            "name": "late collision",
        }
        before_entities = copy.deepcopy(entities)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_followup_b_entities(entities)
        self.assertEqual(entities, before_entities)

        new_source_ids = set(lane.WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS)
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        late_source = lane.WAVE8_FOLLOWUP_B_SOURCES[-1]
        sources[str(late_source["id"])] = {
            **copy.deepcopy(late_source),
            "title": "late collision",
        }
        before_sources = copy.deepcopy(sources)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_followup_b_sources(sources)
        self.assertEqual(sources, before_sources)


if __name__ == "__main__":
    unittest.main()
