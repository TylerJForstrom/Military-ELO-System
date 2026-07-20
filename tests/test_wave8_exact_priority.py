import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_exact_priority as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_exact_priority_"

HAMET_DERNA = "hamet_karamanli_claimant_contingent_derna_1805"
EATON_AUXILIARIES = "eaton_hamet_arab_greek_auxiliaries_derna_1805"
WALKER_LA_VIRGEN = "walker_expeditionary_force_la_virgen_1855"
NICARAGUAN_DEMOCRATS = "nicaraguan_democratic_force_la_virgen_1855"
NICARAGUAN_LEGITIMISTS = "nicaraguan_legitimist_force_la_virgen_1855"
COSTA_RICAN_ARMY = "costa_rican_national_army_santa_rosa_1856"
SCHLESSINGER_DETACHMENT = (
    "schlessinger_walker_filibuster_detachment_santa_rosa_1856"
)
ARMINIUS_COALITION = "arminius_led_germanic_coalition_teutoburg_9"
TWIN_VILLAGES_COALITION = (
    "taovaya_fort_defending_coalition_twin_villages_1759"
)
ORTIZ_PARRILLA_EXPEDITION = "ortiz_parrilla_spanish_led_expedition_1759"

EXPECTED_HASHES = {
    "hced-Calpulalpam1860-1": (
        "f7e420f15234141959bd92b6cd103a4b82d15b0b4b33a4394fa01002c583a32d"
    ),
    "hced-Derna1805-1": (
        "821591e6a4733f91c25f30a2aba17cb199537c3941cf2b55840125a1ff716f87"
    ),
    "hced-Granada, Nicaragua1856-1": (
        "e00e51d575246bdd94bf6c25cb010d389c5fb90536c73168313973f2f49f7d74"
    ),
    "hced-La Virgen1855-1": (
        "22a82e98c7f20f21e1135ba5801acdc65c66765477614a18b800c27682367314"
    ),
    "hced-Red River1759-1": (
        "80dd300e8e760766faed4944f672fb597944822d850551f00506f0979876a083"
    ),
    "hced-Santa Rosa de Copan1856-1": (
        "0ca5fb235b393560bd5fef08cc2c13f4b39c3659c88209fc6f74a1b38f1fbc49"
    ),
    "hced-Teutoburgwald9-1": (
        "5eb0ca0863620e7f8cf42e3f64f2cd98744313e61d2d3bd18933096521389330"
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


class Wave8ExactPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_EXACT_PRIORITY_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_EXACT_PRIORITY_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_exact_priority_entities(entities)
        lane.install_wave8_exact_priority_sources(sources)
        return entities, sources, existing

    def _projection(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_exact_priority_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, existing, events

    def test_all_seven_rows_and_sha256_contracts_are_exact(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("candidate_id") in lane.WAVE8_EXACT_PRIORITY_TARGET_IDS
        }
        self.assertEqual(lane.WAVE8_EXACT_PRIORITY_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(
            lane.validate_wave8_exact_priority_queue_contracts(self.hced_rows),
            {
                "audited_candidate_rows": 7,
                "automated_discovery_rows": 7,
                "holds": 1,
                "promotion_contracts": 6,
                "reserved_hced_rows": 7,
                "reviewed_hced_rows": 7,
            },
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["winner_loser_complete"], True)

    def test_reservation_partition_holds_granada_without_inventing_a_draw(self) -> None:
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS,
            {
                "hced-Calpulalpam1860-1",
                "hced-Derna1805-1",
                "hced-La Virgen1855-1",
                "hced-Red River1759-1",
                "hced-Santa Rosa de Copan1856-1",
                "hced-Teutoburgwald9-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_HOLD_IDS,
            {"hced-Granada, Nicaragua1856-1"},
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS,
            lane.WAVE8_EXACT_PRIORITY_TARGET_IDS,
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS,
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS
            | lane.WAVE8_EXACT_PRIORITY_HOLD_IDS,
        )
        hold = lane.WAVE8_EXACT_PRIORITY_HOLDS[
            "hced-Granada, Nicaragua1856-1"
        ]
        self.assertEqual(hold["disposition"], "hold")
        self.assertNotIn("result_type", hold)
        self.assertNotIn("winner_side", hold)
        self.assertIn("not converted to a draw", hold["audit_note"])
        self.assertFalse(
            any(
                "central_american" in str(entity["id"])
                for entity in lane.WAVE8_EXACT_PRIORITY_ENTITIES
            )
        )
        for contract in lane.WAVE8_EXACT_PRIORITY_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_new_identities_are_alias_free_and_event_bounded(self) -> None:
        entities = {
            str(item["id"]): item for item in lane.WAVE8_EXACT_PRIORITY_ENTITIES
        }
        expected_windows = {
            HAMET_DERNA: (1805, 1805),
            EATON_AUXILIARIES: (1805, 1805),
            WALKER_LA_VIRGEN: (1855, 1855),
            NICARAGUAN_DEMOCRATS: (1855, 1855),
            NICARAGUAN_LEGITIMISTS: (1855, 1855),
            COSTA_RICAN_ARMY: (1856, 1856),
            SCHLESSINGER_DETACHMENT: (1856, 1856),
            ARMINIUS_COALITION: (9, 9),
            TWIN_VILLAGES_COALITION: (1759, 1759),
            ORTIZ_PARRILLA_EXPEDITION: (1759, 1759),
        }
        self.assertEqual(set(entities), set(expected_windows))
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    expected_windows[entity_id],
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("No rating is inherited", entity["continuity_note"])
                Entity.from_dict(entity)

    def test_sources_parse_and_pin_role_and_family_provenance(self) -> None:
        self.assertEqual(len(lane.WAVE8_EXACT_PRIORITY_SOURCES), 15)
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_EXACT_PRIORITY_SOURCES
        }
        for source_id, source in sources.items():
            with self.subTest(source_id=source_id):
                Source.from_dict(source)
                self.assertTrue(source["source_family_id"])
                self.assertEqual(
                    source["evidence_roles"],
                    sorted(set(source["evidence_roles"])),
                )
        for candidate_id, contract in lane.WAVE8_EXACT_PRIORITY_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]), 2
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
        hold = lane.WAVE8_EXACT_PRIORITY_HOLDS[
            "hced-Granada, Nicaragua1856-1"
        ]
        self.assertEqual(len(hold["evidence_source_family_ids"]), 2)

    def test_promotions_emit_exact_candidate_keyed_coalitions_and_wins(self) -> None:
        _, _, _, emitted = self._projection()
        events = {str(event["hced_candidate_id"]): event for event in emitted}
        expected = {
            "hced-Calpulalpam1860-1": (
                "Battle of Calpulalpan",
                {"mexican_liberal_forces"},
                {"mexican_conservative_forces"},
            ),
            "hced-Derna1805-1": (
                "Battle of Derna",
                {"united_states", HAMET_DERNA, EATON_AUXILIARIES},
                {"yusuf_karamanli_regency_of_tripoli_1795_1832"},
            ),
            "hced-La Virgen1855-1": (
                "Battle of La Virgen",
                {WALKER_LA_VIRGEN, NICARAGUAN_DEMOCRATS},
                {NICARAGUAN_LEGITIMISTS},
            ),
            "hced-Santa Rosa de Copan1856-1": (
                "Battle of Santa Rosa (Costa Rica)",
                {COSTA_RICAN_ARMY},
                {SCHLESSINGER_DETACHMENT},
            ),
            "hced-Teutoburgwald9-1": (
                "Battle of the Teutoburg Forest",
                {ARMINIUS_COALITION},
                {"roman_empire"},
            ),
            "hced-Red River1759-1": (
                "Battle of the Twin Villages",
                {TWIN_VILLAGES_COALITION},
                {ORTIZ_PARRILLA_EXPEDITION},
            ),
        }
        self.assertEqual(set(events), set(expected))
        self.assertNotIn("hced-Granada, Nicaragua1856-1", events)
        for candidate_id, (name, winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                self.assertFalse(
                    any(
                        token in item["termination"]
                        for item in event["participants"]
                        for token in ("draw", "inconclusive", "unknown")
                    )
                )
                Event.from_dict(event)

    def test_chronology_and_event_types_are_pinned(self) -> None:
        expected = {
            "hced-Calpulalpam1860-1": (
                "22 December 1860",
                "day",
                "civil_war",
            ),
            "hced-Derna1805-1": (
                "27 April 1805",
                "day",
                "interstate_claimant_intervention",
            ),
            "hced-La Virgen1855-1": (
                "3 September 1855",
                "day",
                "civil_war_foreign_intervention",
            ),
            "hced-Santa Rosa de Copan1856-1": (
                "20 March 1856",
                "day",
                "foreign_filibuster_intervention",
            ),
            "hced-Teutoburgwald9-1": (
                "9 CE",
                "year",
                "anti_imperial_revolt",
            ),
            "hced-Red River1759-1": (
                "7 October 1759",
                "day",
                "colonial_anti_colonial",
            ),
        }
        events = {
            str(event["hced_candidate_id"]): event
            for event in self._projection()[3]
        }
        for candidate_id, (date_text, precision, war_type) in expected.items():
            contract = lane.WAVE8_EXACT_PRIORITY_CONTRACTS[candidate_id]
            self.assertEqual(contract["canonical_event"]["date_text"], date_text)
            self.assertEqual(
                contract["canonical_event"]["date_precision"], precision
            )
            self.assertEqual(events[candidate_id]["date_precision"], precision)
            self.assertEqual(events[candidate_id]["war_type"], war_type)

    def test_all_promoted_points_are_quarantined_and_countries_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS)
        expected_countries = {
            "hced-Calpulalpam1860-1": "Mexico",
            "hced-Derna1805-1": "Libya",
            "hced-La Virgen1855-1": "Nicaragua",
            "hced-Red River1759-1": "United States",
            "hced-Santa Rosa de Copan1856-1": "Costa Rica",
            "hced-Teutoburgwald9-1": "Germany",
        }
        for event in self._projection()[3]:
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"], expected_countries[candidate_id]
            )
            self.assertIn("location_provenance", event)

    def test_projected_release_inventory_and_final_audit_validate(self) -> None:
        entities, sources, existing, emitted = self._projection()
        release = [*existing, *emitted]
        self.assertEqual(
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                release,
            ),
            {
                "held_candidate_events": 0,
                "lane_entities": 10,
                "lane_events": 6,
                "lane_sources": 15,
                "outside_entity_uses": 0,
                "reserved_candidate_ids": 7,
            },
        )
        self.assertEqual(
            lane.validate_wave8_exact_priority_final_audit(
                entities,
                sources,
                release,
                lane.wave8_exact_priority_metadata(),
            ),
            {
                "held_candidate_events": 0,
                "lane_entities": 10,
                "lane_events": 6,
                "lane_sources": 15,
                "outside_entity_uses": 0,
                "reserved_candidate_ids": 7,
                "final_audit_signature": (
                    lane.WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE
                ),
            },
        )

    def test_hash_and_automated_discovery_tampering_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Calpulalpam1860-1"
        )
        row["winner_raw"] = "Mexican Government"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_exact_priority_queue_contracts(tampered)

        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Derna1805-1"
        )
        row["do_not_rate_automatically"] = False
        with self.assertRaises(ValueError):
            lane.promote_wave8_exact_priority_contracts(
                tampered,
                self._installed()[0],
                self._installed()[2],
            )

    def test_release_source_family_and_role_tampering_fail_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        source_id = "wave8_exact_priority_tsha_ortiz_parrilla"
        sources[source_id]["source_family_id"] = "tampered_family"
        with self.assertRaisesRegex(ValueError, "source provenance"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        sources[source_id]["evidence_roles"] = [
            "identity_boundary_or_context_reference"
        ]
        with self.assertRaisesRegex(ValueError, "source provenance"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_outcome_tampering_and_unknown_as_draw_fail_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        event = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
        )
        event["participants"][0]["termination"] = "engagement_inconclusive"
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
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
                entities, sources, existing, emitted = self._projection()
                event = next(
                    item
                    for item in emitted
                    if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
                )
                event["participants"][0][field] = value
                with self.assertRaisesRegex(ValueError, "release outcome"):
                    lane.validate_wave8_exact_priority_release_inventory(
                        entities,
                        sources,
                        [*existing, *emitted],
                    )

    def test_identity_window_tampering_fails_promotion_and_release(self) -> None:
        entities, sources, existing = self._installed()
        entities[HAMET_DERNA]["end_year"] = 1804
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_exact_priority_contracts(
                self.hced_rows,
                entities,
                existing,
            )

        entities, sources, existing, emitted = self._projection()
        entities[COSTA_RICAN_ARMY]["start_year"] = 1857
        with self.assertRaisesRegex(ValueError, "release entity drift"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_coalition_decomposition_tampering_fails_release_audit(self) -> None:
        entities, sources, existing, emitted = self._projection()
        derna = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Derna1805-1"
        )
        derna["participants"] = [
            item
            for item in derna["participants"]
            if item["entity_id"] != EATON_AUXILIARIES
        ]
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        la_virgen = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-La Virgen1855-1"
        )
        la_virgen["participants"][0]["entity_id"] = COSTA_RICAN_ARMY
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_release_inventory_hold_leak_partial_inventory_and_metadata_fail(self) -> None:
        entities, sources, existing, emitted = self._projection()
        with self.assertRaisesRegex(ValueError, "event inventory"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted[:-1]],
            )

        hold_leak = copy.deepcopy(emitted[0])
        hold_leak["id"] = f"{EVENT_ID_PREFIX}held_granada"
        hold_leak["hced_candidate_id"] = "hced-Granada, Nicaragua1856-1"
        with self.assertRaisesRegex(ValueError, "held Granada"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted, hold_leak],
            )

        entities, sources, existing, emitted = self._projection()
        teutoburg = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
        )
        teutoburg["aliases"].append("Germanic Tribes")
        with self.assertRaisesRegex(ValueError, "event alias drift"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        metadata = copy.deepcopy(lane.wave8_exact_priority_metadata())
        metadata["final_audit_signature"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "metadata drift"):
            lane.validate_wave8_exact_priority_final_audit(
                entities,
                sources,
                [*existing, *emitted],
                metadata,
            )

    def test_event_bounded_identity_use_outside_lane_fails_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        leaked = {
            "id": "uncontracted_hamet_rate",
            "name": "Uncontracted Hamet event",
            "year": 1805,
            "participants": [{"entity_id": HAMET_DERNA}],
        }
        with self.assertRaisesRegex(ValueError, "outside exact contracts"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted, leaked],
            )

    def test_duplicate_and_probable_twin_guards_fail_closed(self) -> None:
        _, _, existing, emitted = self._projection()
        self.assertEqual(
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "held_release_events": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
            },
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_exact_priority_contracts(
                self.hced_rows,
                self._installed()[0],
                [*existing, emitted[0]],
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-varus",
                "batname": "Varus Battle",
                "batyear": 9,
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable twin"):
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        with self.assertRaisesRegex(ValueError, "overlap is partial"):
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, emitted[0]],
            )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        lane.install_wave8_exact_priority_entities(entities)
        lane.install_wave8_exact_priority_entities(entities)
        self.assertEqual(len(entities), 10)
        entities[HAMET_DERNA]["end_year"] = 1804
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_exact_priority_entities(entities)

        sources: dict[str, dict] = {}
        lane.install_wave8_exact_priority_sources(sources)
        lane.install_wave8_exact_priority_sources(sources)
        self.assertEqual(len(sources), 15)
        source_id = "wave8_exact_priority_kalkriese_varus"
        sources[source_id]["source_family_id"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_exact_priority_sources(sources)

    def test_installers_are_atomic_on_late_collision(self) -> None:
        late_entity = lane.WAVE8_EXACT_PRIORITY_ENTITIES[-1]
        entities = {
            str(late_entity["id"]): {
                **copy.deepcopy(late_entity),
                "name": "late collision",
            }
        }
        before_entities = copy.deepcopy(entities)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_exact_priority_entities(entities)
        self.assertEqual(entities, before_entities)

        late_source = lane.WAVE8_EXACT_PRIORITY_SOURCES[-1]
        sources = {
            str(late_source["id"]): {
                **copy.deepcopy(late_source),
                "title": "late collision",
            }
        }
        before_sources = copy.deepcopy(sources)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_exact_priority_sources(sources)
        self.assertEqual(sources, before_sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_exact_priority_audit_signature(),
            lane.WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_exact_priority_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 1,
                "new_entities": 10,
                "new_sources": 15,
                "newly_rated_events": 6,
                "outcome_overrides": 0,
                "outcome_reversals": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reserved_hced_rows": 7,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_exact_priority_cohort_counts(),
            {
                "first_barbary_war": 1,
                "mexican_war_of_reform": 1,
                "nicaragua_filibuster_conflict": 3,
                "roman_germania_conflict": 1,
                "spanish_northern_frontier": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
