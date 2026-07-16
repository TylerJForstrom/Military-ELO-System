import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_muslim_forces import (
    WAVE8_MUSLIM_FORCES_CONTRACT_IDS,
    WAVE8_MUSLIM_FORCES_CONTRACTS,
    WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS,
    WAVE8_MUSLIM_FORCES_ENTITIES,
    WAVE8_MUSLIM_FORCES_EXCLUSION_IDS,
    WAVE8_MUSLIM_FORCES_EXPECTED_CANDIDATE_IDS,
    WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE,
    WAVE8_MUSLIM_FORCES_HOLD_IDS,
    WAVE8_MUSLIM_FORCES_HOLDS,
    WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS,
    WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MUSLIM_FORCES_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_MUSLIM_FORCES_NONPROMOTIONS,
    WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES,
    WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MUSLIM_FORCES_RESERVED_IDS,
    WAVE8_MUSLIM_FORCES_SOURCES,
    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS,
    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS,
    install_wave8_muslim_forces_entities,
    install_wave8_muslim_forces_sources,
    promote_wave8_muslim_forces_contracts,
    validate_wave8_muslim_forces_queue_contracts,
    wave8_muslim_forces_audit_signature,
    wave8_muslim_forces_cohort_counts,
    wave8_muslim_forces_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict]:
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_MUSLIM_FORCES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "duplicate_dispositions": WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS,
        "entities": WAVE8_MUSLIM_FORCES_ENTITIES,
        "holds": WAVE8_MUSLIM_FORCES_HOLDS,
        "integration_dispositions": WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "outcome_overrides": WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_MUSLIM_FORCES_SOURCES,
        "terminal_exclusions": WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class Wave8MuslimForcesTests(unittest.TestCase):
    def _entities_and_existing(self):
        lane_ids = {str(entity["id"]) for entity in WAVE8_MUSLIM_FORCES_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
            if entity["id"] not in lane_ids
        }
        install_wave8_muslim_forces_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id")
            not in WAVE8_MUSLIM_FORCES_CONTRACT_IDS
        ]
        return entities, existing

    def _events(self) -> list[dict]:
        entities, existing = self._entities_and_existing()
        return promote_wave8_muslim_forces_contracts(_rows(), entities, existing)

    def test_counts_dispositions_and_pinned_signature(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_MUSLIM_FORCES_CONTRACT_IDS),
                len(WAVE8_MUSLIM_FORCES_HOLD_IDS),
                len(WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS),
            ),
            (14, 4, 5),
        )
        disposition_sets = (
            WAVE8_MUSLIM_FORCES_CONTRACT_IDS,
            WAVE8_MUSLIM_FORCES_HOLD_IDS,
            WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS,
        )
        for index, left in enumerate(disposition_sets):
            for right in disposition_sets[index + 1 :]:
                self.assertFalse(left & right)
        self.assertEqual(
            WAVE8_MUSLIM_FORCES_RESERVED_IDS,
            WAVE8_MUSLIM_FORCES_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(WAVE8_MUSLIM_FORCES_EXCLUSION_IDS, WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS)
        self.assertEqual(_independent_signature(), WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_muslim_forces_audit_signature(), WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_muslim_forces_cohort_counts(),
            {
                "byzantine_arab_wars": 3,
                "ceuta": 1,
                "crusades": 2,
                "early_caliphal_armies": 3,
                "iberia": 2,
                "mongol_era_actors": 1,
                "sicily": 2,
            },
        )
        self.assertEqual(
            wave8_muslim_forces_counts(),
            {
                "duplicate_dispositions": 4,
                "greedy_eligible_rows": 18,
                "greedy_marginal_rows": 13,
                "holds": 4,
                "integration_dispositions": 23,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 24,
                "new_sources": 25,
                "newly_rated_events": 14,
                "outcome_overrides": 0,
                "promotion_contracts": 14,
                "reviewed_hced_rows": 23,
                "terminal_exclusions": 5,
                "touched_rows": 23,
            },
        )

    def test_funnel_scope_is_exact_and_every_row_was_audited(self) -> None:
        funnel_path = ROOT / "build" / "hced-unresolved-label-funnel.json"
        if not funnel_path.exists():
            raise unittest.SkipTest("HCED unresolved-label funnel is unavailable")
        funnel = _json(funnel_path)
        scoped = {
            row["candidate_id"]: row
            for row in funnel["row_label_data"]
            if "muslims" in row.get("blocker_labels", [])
        }
        self.assertEqual(set(scoped), WAVE8_MUSLIM_FORCES_RESERVED_IDS)
        self.assertEqual(len(scoped), 23)
        self.assertEqual(sum(bool(row["greedy_eligible"]) for row in scoped.values()), 18)
        self.assertEqual(
            sum(row.get("sole_blocker_label") == "muslims" for row in scoped.values()),
            13,
        )
        for candidate_id, row in scoped.items():
            disposition = WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS[candidate_id]
            self.assertTrue(disposition["full_row_audited"])
            self.assertEqual(disposition["blocker_labels"], row["blocker_labels"])
            self.assertEqual(disposition["greedy_eligible"], row["greedy_eligible"])
            self.assertEqual(disposition["sole_blocker_label"], row["sole_blocker_label"])
            self.assertEqual(disposition["other_blockers"], row["other_blockers"])

    def test_raw_hashes_and_queue_validation_are_fail_closed(self) -> None:
        rows = _rows()
        indexed = {row["candidate_id"]: row for row in rows}
        inventory = {
            **WAVE8_MUSLIM_FORCES_CONTRACTS,
            **WAVE8_MUSLIM_FORCES_NONPROMOTIONS,
        }
        for candidate_id, item in inventory.items():
            self.assertEqual(
                canonical_hced_row_sha256(indexed[candidate_id]),
                item["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_muslim_forces_queue_contracts(rows),
            {
                "promotion_contracts": 14,
                "holds": 4,
                "reviewed_hced_rows": 23,
                "terminal_exclusions": 5,
            },
        )

        mutated = copy.deepcopy(rows)
        target = next(row for row in mutated if row["candidate_id"] == "hced-Beirut1110-1")
        target["winner_raw"] = "changed"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_muslim_forces_queue_contracts(mutated)

        missing = [row for row in rows if row["candidate_id"] != "hced-Aleppo639-1"]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_muslim_forces_queue_contracts(missing)

    def test_canonical_events_and_direct_dates_are_pinned(self) -> None:
        expected_keys = {
            "hced-Aleppo639-1": "reported_submission_of_aleppo:639:639",
            "hced-Aleppo962-1": "capture_of_aleppo:962:962",
            "hced-Aleppo969-1": "aleppo_protectorate_transition:969:969",
            "hced-Aleppo1260-1": "capture_of_aleppo_city:1260:1260",
            "hced-Alexandria641-642-1": "first_siege_and_treaty_of_alexandria:641:641",
            "hced-Alexandria645-1": "alexandria_reconquest_assertion:645:645",
            "hced-Amida973-1": "battle_of_amida:973:973",
            "hced-Amorium669-1": "reported_byzantine_recovery_of_amorium:669:669",
            "hced-Antioch, Syria969-1": "capture_of_antioch:969:969",
            "hced-Arqa1098-1": "siege_of_arqa_assertion:1098:1098",
            "hced-Babylon, Egypt640-1": "siege_of_babylon_fortress_assertion:640:640",
            "hced-Babylon, Iraq634-1": "reported_battle_at_babylon_in_iraq:634:634",
            "hced-Beirut1110-1": "siege_and_capture_of_beirut:1110:1110",
            "hced-Bosra634-1": "siege_and_capitulation_of_bostra:634:634",
            "hced-Bridge634-1": "battle_of_the_bridge:634:634",
            "hced-Buwayb635-1": "reported_battle_of_buwayb:635:635",
            "hced-Buzakha632-1": "battle_of_buzakha:632:632",
            "hced-Castrogiovanni859-1": "capture_of_enna_castrogiovanni:859:859",
            "hced-Cerami1063-1": "battle_of_cerami:1063:1063",
            "hced-Ceuta1415-1": "capture_of_ceuta:1415:1415",
            "hced-Ecija711-1": "battle_near_ecija:711:711",
            "hced-Guadalete711-1": "battle_traditionally_called_guadalete:711:711",
            "hced-Harenc1098-1": "battle_of_the_lake_of_antioch_harenc:1098:1098",
        }
        inventory = {
            **WAVE8_MUSLIM_FORCES_CONTRACTS,
            **WAVE8_MUSLIM_FORCES_NONPROMOTIONS,
        }
        self.assertEqual(set(inventory), set(expected_keys))
        self.assertEqual(
            {
                candidate_id: item["canonical_event"]["canonical_key"]
                for candidate_id, item in inventory.items()
            },
            expected_keys,
        )
        for contract in WAVE8_MUSLIM_FORCES_CONTRACTS.values():
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(canonical["date_precision"], "year")
            self.assertEqual(canonical["granularity"], "engagement")
            provenance = contract["direct_provenance"]
            self.assertEqual(
                set(provenance),
                {"event_boundary", "reviewed_date", "reviewed_outcome", "reviewed_sides"},
            )
            self.assertTrue(all(provenance.values()))
        for item in WAVE8_MUSLIM_FORCES_NONPROMOTIONS.values():
            self.assertTrue(item["historical_event"]["reviewed_date"])
            self.assertTrue(item["historical_event"]["reviewed_outcome"])

    def test_entities_are_exactly_bounded_and_never_generic_muslims(self) -> None:
        expected_ids = {
            "african_reinforcement_contingent_cerami_1063",
            "al_abbas_aghlabid_enna_force_859",
            "ayyubid_aleppo_city_garrison_1260",
            "az_zughayli_antioch_garrison_969",
            "baldwin_i_beirut_siege_force_1110",
            "bertrand_tripoli_beirut_force_1110",
            "bohemond_lake_antioch_cavalry_1098",
            "cilician_armenian_aleppo_contingent_1260",
            "ecija_visigothic_defenders_711",
            "fatimid_beirut_garrison_1110",
            "fatimid_coastal_relief_fleet_beirut_1110",
            "genoese_beirut_blockade_fleet_1110",
            "georgian_aleppo_contingent_1260",
            "hamdanid_mosul_amida_relief_force_973",
            "pisan_beirut_blockade_fleet_1110",
            "ridwan_aleppo_relief_army_1098",
            "roderic_visigothic_royal_army_711",
            "roger_i_norman_force_cerami_1063",
            "rum_seljuq_aleppo_contingent_1260",
            "salah_ben_salah_ceuta_defenders_1415",
            "sayf_al_dawla_aleppo_force_962",
            "sicilian_defending_force_cerami_1063",
            "tariq_ibn_ziyad_invasion_army_711",
            "tulayha_asad_ghatafan_force_buzakha_632",
        }
        self.assertEqual(
            {entity["id"] for entity in WAVE8_MUSLIM_FORCES_ENTITIES},
            expected_ids,
        )
        for entity in WAVE8_MUSLIM_FORCES_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertNotIn(entity["name"].casefold(), {"muslim", "muslims"})
            self.assertNotIn(entity["id"].casefold(), {"muslim", "muslims"})

        new_ids = {entity["id"] for entity in WAVE8_MUSLIM_FORCES_ENTITIES}
        used_ids = {
            entity_id
            for contract in WAVE8_MUSLIM_FORCES_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
            if entity_id in new_ids
        }
        self.assertEqual(used_ids, new_ids)

    def test_sources_and_outcome_provenance_are_direct(self) -> None:
        source_by_id = {source["id"]: source for source in WAVE8_MUSLIM_FORCES_SOURCES}
        self.assertEqual(len(source_by_id), 25)
        for source in WAVE8_MUSLIM_FORCES_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["license"], "linked_reference")
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertIn(
                "identity_boundary_or_context_reference",
                source["evidence_roles"],
            )
        for contract in WAVE8_MUSLIM_FORCES_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])
            self.assertTrue(contract["outcome_source_ids"])
            self.assertNotIn("hced_dataset", contract["outcome_source_ids"])
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )

    def test_holds_and_exclusions_never_invent_outcomes(self) -> None:
        self.assertEqual(
            {item["hold_category"] for item in WAVE8_MUSLIM_FORCES_HOLDS.values()},
            {
                "chronology_and_event_sequence_unresolved",
                "historicity_and_granularity_disputed",
                "recovery_date_unresolved",
                "single_tradition_event_binding",
            },
        )
        self.assertEqual(
            {item["hold_category"] for item in WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS.values()},
            {
                "event_year_mismatch",
                "locked_interval_truncates_siege",
                "locked_interval_truncates_treaty_execution",
                "negotiated_transition_not_binary_engagement",
                "winner_and_conquest_phase_mismatch",
            },
        )
        for item in WAVE8_MUSLIM_FORCES_HOLDS.values():
            self.assertEqual(item["disposition"], "hold")
            self.assertFalse(item["terminal_exclusion"])
            self.assertTrue(item["full_row_audited"])
            self.assertNotIn("result_type", item)
            self.assertNotIn("winner_side", item)
        for item in WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS.values():
            self.assertEqual(item["disposition"], "terminal_exclusion")
            self.assertTrue(item["terminal_exclusion"])
            self.assertTrue(item["full_row_audited"])
        self.assertFalse(WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES)

    def test_coblocked_promotions_have_every_actor_resolved(self) -> None:
        coblocked = {
            candidate_id
            for candidate_id, item in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.items()
            if len(item["blocker_labels"]) > 1 or item["other_blockers"]
        }
        self.assertEqual(len(coblocked), 10)
        promoted_coblocked = coblocked & WAVE8_MUSLIM_FORCES_CONTRACT_IDS
        self.assertEqual(
            promoted_coblocked,
            {
                "hced-Aleppo1260-1",
                "hced-Beirut1110-1",
                "hced-Bridge634-1",
                "hced-Buzakha632-1",
                "hced-Cerami1063-1",
                "hced-Ecija711-1",
                "hced-Guadalete711-1",
                "hced-Harenc1098-1",
            },
        )
        for candidate_id in promoted_coblocked:
            disposition = WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS[candidate_id]
            self.assertTrue(disposition["all_opposing_actors_resolved"])
            contract = WAVE8_MUSLIM_FORCES_CONTRACTS[candidate_id]
            self.assertTrue(contract["side_1_entity_ids"])
            self.assertTrue(contract["side_2_entity_ids"])

        self.assertEqual(
            WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS["hced-Buwayb635-1"]["disposition"],
            "HOLD",
        )
        self.assertEqual(
            WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS["hced-Arqa1098-1"]["disposition"],
            "EXCLUDE",
        )

    def test_duplicate_dispositions_preserve_exact_event_granularity(self) -> None:
        self.assertEqual(
            set(WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS),
            {
                "aleppo_antioch_969",
                "alexandria_phases_641_645",
                "guadalete_ecija_711",
                "harenc_orontes_1098",
            },
        )
        harenc = WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS["harenc_orontes_1098"]
        self.assertEqual(harenc["disposition"], "distinct_engagements_same_campaign")
        self.assertIn("9 February", harenc["reason"])
        self.assertIn("28 June", harenc["reason"])
        self.assertFalse(WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS)

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_muslim_forces_entities(entities)
        install_wave8_muslim_forces_sources(sources)
        self.assertEqual(set(entities), {entity["id"] for entity in WAVE8_MUSLIM_FORCES_ENTITIES})
        self.assertEqual(set(sources), {source["id"] for source in WAVE8_MUSLIM_FORCES_SOURCES})
        original_entities = copy.deepcopy(entities)
        original_sources = copy.deepcopy(sources)
        install_wave8_muslim_forces_entities(entities)
        install_wave8_muslim_forces_sources(sources)
        self.assertEqual(entities, original_entities)
        self.assertEqual(sources, original_sources)

        bad_entities = copy.deepcopy(entities)
        entity_id = next(iter(bad_entities))
        bad_entities[entity_id]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_muslim_forces_entities(bad_entities)

        bad_sources = copy.deepcopy(sources)
        source_id = next(iter(bad_sources))
        bad_sources[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_muslim_forces_sources(bad_sources)

    def test_promoted_events_are_exact_wins_with_no_generic_identity(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 14)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_MUSLIM_FORCES_CONTRACT_IDS,
        )
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        for event in events:
            Event.from_dict(event)
            contract = WAVE8_MUSLIM_FORCES_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            self.assertEqual((event["year"], event["end_year"]), (contract["canonical_event"]["year_low"], contract["canonical_event"]["year_high"]))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            participant_ids = {participant["entity_id"] for participant in event["participants"]}
            self.assertTrue(participant_ids)
            self.assertTrue({"muslim", "muslims"}.isdisjoint({value.casefold() for value in participant_ids}))
            self.assertTrue(all(participant["outcome"] != "draw" for participant in event["participants"]))

        self.assertEqual(
            [participant["entity_id"] for participant in by_candidate["hced-Aleppo1260-1"]["participants"]],
            [
                "mongol_empire",
                "georgian_aleppo_contingent_1260",
                "cilician_armenian_aleppo_contingent_1260",
                "rum_seljuq_aleppo_contingent_1260",
                "ayyubid_aleppo_city_garrison_1260",
            ],
        )
        self.assertEqual(
            len(by_candidate["hced-Beirut1110-1"]["participants"]),
            6,
        )
        self.assertEqual(
            len(by_candidate["hced-Cerami1063-1"]["participants"]),
            3,
        )

    def test_location_quarantine_additions_are_applied_locally(self) -> None:
        self.assertEqual(
            WAVE8_MUSLIM_FORCES_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": frozenset(
                    {"hced-Bridge634-1", "hced-Guadalete711-1", "hced-Harenc1098-1"}
                ),
                "country": frozenset({"hced-Harenc1098-1"}),
            },
        )
        by_candidate = {event["hced_candidate_id"]: event for event in self._events()}
        for candidate_id in WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_candidate[candidate_id])
        self.assertEqual(by_candidate["hced-Bridge634-1"]["modern_location_country"], "Iraq")
        self.assertEqual(by_candidate["hced-Guadalete711-1"]["modern_location_country"], "Spain")
        harenc = by_candidate["hced-Harenc1098-1"]
        self.assertNotIn("modern_location_country", harenc)
        self.assertNotIn("location_provenance", harenc)
        self.assertIn("geometry", by_candidate["hced-Ceuta1415-1"])

    def test_existing_candidate_or_event_name_collision_fails_closed(self) -> None:
        rows = _rows()
        entities, existing = self._entities_and_existing()
        promoted = promote_wave8_muslim_forces_contracts(rows, entities, existing)
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_muslim_forces_contracts(
                rows,
                entities,
                [*existing, promoted[0]],
            )
        colliding = copy.deepcopy(existing)
        colliding.append(
            {
                "id": "synthetic_collision",
                "name": "Battle of Cerami",
                "year": 1063,
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_muslim_forces_contracts(rows, entities, colliding)


if __name__ == "__main__":
    unittest.main()
