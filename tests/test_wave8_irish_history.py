import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_irish_history import (
    WAVE8_IRISH_HISTORY_CONTRACT_IDS,
    WAVE8_IRISH_HISTORY_CONTRACTS,
    WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_ENTITIES,
    WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS,
    WAVE8_IRISH_HISTORY_FINAL_AUDIT_SIGNATURE,
    WAVE8_IRISH_HISTORY_HOLD_IDS,
    WAVE8_IRISH_HISTORY_HOLDS,
    WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS,
    WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES,
    WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS,
    WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_RESERVED_IDS,
    WAVE8_IRISH_HISTORY_SOURCES,
    WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS,
    WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS,
    install_wave8_irish_history_entities,
    install_wave8_irish_history_sources,
    promote_wave8_irish_history_contracts,
    validate_wave8_irish_history_integration_dispositions,
    validate_wave8_irish_history_queue_contracts,
    wave8_irish_history_audit_signature,
    wave8_irish_history_cohort_counts,
    wave8_irish_history_counts,
    wave8_irish_history_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class Wave8IrishHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(
            ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        )
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _entities(self):
        entities = {entity["id"]: entity for entity in self.release_entities}
        install_wave8_irish_history_entities(entities)
        return entities

    def _pre_lane_events(self):
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_IRISH_HISTORY_CONTRACT_IDS
        ]

    def _promoted(self):
        return promote_wave8_irish_history_contracts(
            self.rows,
            self._entities(),
            self._pre_lane_events(),
        )

    def test_inventory_signature_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(len(WAVE8_IRISH_HISTORY_CONTRACT_IDS), 8)
        self.assertEqual(len(WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS), 1)
        self.assertEqual(
            WAVE8_IRISH_HISTORY_HOLD_IDS,
            WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(
            WAVE8_IRISH_HISTORY_HOLDS,
            WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            WAVE8_IRISH_HISTORY_RESERVED_IDS,
            WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_irish_history_audit_signature(),
            WAVE8_IRISH_HISTORY_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_irish_history_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_source_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 1,
                "new_entities": 17,
                "new_sources": 16,
                "newly_rated_events": 8,
                "outcome_overrides": 0,
                "point_quarantine_additions": 8,
                "promotion_contracts": 8,
                "related_hced_dispositions": 1,
                "reviewed_hced_rows": 9,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_irish_history_cohort_counts(),
            {
                "anglo_norman_dublin_1171": 1,
                "battle_of_clontarf_1014": 1,
                "battle_of_tara_980": 1,
                "nine_years_war_1594_1603": 3,
                "thomond_de_clare_conflict_1318": 1,
                "wars_of_three_kingdoms_1651": 1,
            },
        )

    def test_all_nine_semantic_hashes_validate_and_drift_fails_closed(self) -> None:
        indexed = {row["candidate_id"]: row for row in self.rows}
        inventory = {
            **WAVE8_IRISH_HISTORY_CONTRACTS,
            **WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS,
        }
        self.assertEqual(set(inventory), WAVE8_IRISH_HISTORY_RESERVED_IDS)
        for candidate_id, disposition in inventory.items():
            self.assertEqual(
                canonical_hced_row_sha256(indexed[candidate_id]),
                disposition["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_irish_history_queue_contracts(self.rows),
            {"promotion_contracts": 8, "holds": 1, "reviewed_hced_rows": 9},
        )

        changed_promotion = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_promotion
            if row["candidate_id"] == "hced-Clontarf1014-1"
        )["side_2_raw"] = "generic Vikings"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_irish_history_queue_contracts(changed_promotion)

        changed_exclusion = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_exclusion
            if row["candidate_id"] == "hced-Derry1600-1"
        )["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_irish_history_queue_contracts(changed_exclusion)

    def test_complete_reservations_block_the_generic_crosswalk(self) -> None:
        owned_rows = [
            row
            for row in self.rows
            if row.get("candidate_id") in WAVE8_IRISH_HISTORY_RESERVED_IDS
        ]
        result = promote_hced_crosswalk_rows(
            owned_rows,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda _entity: None,
            reserved_candidate_ids=WAVE8_IRISH_HISTORY_RESERVED_IDS,
        )
        self.assertEqual(len(owned_rows), 9)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["label_observations"], {})
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 9)

    def test_sources_parse_and_outcomes_have_direct_provenance(self) -> None:
        self.assertEqual(len(WAVE8_IRISH_HISTORY_SOURCES), 16)
        source_by_id = {}
        for source in WAVE8_IRISH_HISTORY_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["license"], "linked_reference")
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertIn(
                "identity_boundary_or_context_reference",
                source["evidence_roles"],
            )
            source_by_id[source["id"]] = source
        self.assertEqual(len(source_by_id), 16)

        for contract in WAVE8_IRISH_HISTORY_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            self.assertTrue(outcomes)
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in outcomes
                )
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in outcomes
                    }
                ),
            )

    def test_entities_are_exact_event_forces_with_continuity_firewalls(self) -> None:
        expected_ids = {
            "amlaib_cuaran_dublin_isles_tara_host_980",
            "bagenal_blackwater_relief_army_1598",
            "bagenal_monaghan_relief_column_1595",
            "brian_boruma_clontarf_field_coalition_1014",
            "crown_enniskillen_relief_column_1594",
            "docwra_lough_foyle_expedition_1600",
            "hugh_dubh_oneill_limerick_garrison_1651",
            "hugh_oneill_clontibret_force_1595",
            "ireton_new_model_army_limerick_1651",
            "leinster_dublin_overseas_clontarf_coalition_1014",
            "mael_sechnaill_clann_cholmain_tara_host_980",
            "maguire_allied_ford_biscuits_force_1594",
            "muircheartach_obrien_thomond_dysert_coalition_1318",
            "oneill_odonnell_yellow_ford_host_1598",
            "richard_de_clare_dysert_army_1318",
            "ruaidri_ua_conchobair_dublin_siege_coalition_1171",
            "strongbow_cogan_dublin_garrison_1171",
        }
        self.assertEqual(
            {entity["id"] for entity in WAVE8_IRISH_HISTORY_ENTITIES},
            expected_ids,
        )
        source_ids = {source["id"] for source in WAVE8_IRISH_HISTORY_SOURCES}
        forbidden_names = {
            "danish dublin",
            "england",
            "english",
            "ireland",
            "irish",
            "viking",
            "vikings",
        }
        for entity in WAVE8_IRISH_HISTORY_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn(entity["name"].casefold(), forbidden_names)
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= source_ids)

        participant_ids = {
            entity_id
            for contract in WAVE8_IRISH_HISTORY_CONTRACTS.values()
            for side in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[side]
        }
        self.assertEqual(
            participant_ids,
            expected_ids - {"docwra_lough_foyle_expedition_1600"},
        )

    def test_canonical_dates_granularity_and_exact_sides_are_pinned(self) -> None:
        expected = {
            "hced-Tara980-1": (
                "battle_of_tara:980:980",
                "year",
                "engagement",
                ("mael_sechnaill_clann_cholmain_tara_host_980",),
                ("amlaib_cuaran_dublin_isles_tara_host_980",),
            ),
            "hced-Clontarf1014-1": (
                "battle_of_clontarf:1014:1014",
                "day",
                "engagement",
                ("brian_boruma_clontarf_field_coalition_1014",),
                ("leinster_dublin_overseas_clontarf_coalition_1014",),
            ),
            "hced-Dublin (2nd)1171-1": (
                "siege_of_dublin:1171:1171",
                "year",
                "siege",
                ("strongbow_cogan_dublin_garrison_1171",),
                ("ruaidri_ua_conchobair_dublin_siege_coalition_1171",),
            ),
            "hced-Dysert ODea1318-1": (
                "battle_of_dysert_o_dea:1318:1318",
                "day",
                "engagement",
                ("muircheartach_obrien_thomond_dysert_coalition_1318",),
                ("richard_de_clare_dysert_army_1318",),
            ),
            "hced-Ford of the Biscuits1594-1": (
                "battle_of_the_ford_of_the_biscuits:1594:1594",
                "day",
                "engagement",
                ("maguire_allied_ford_biscuits_force_1594",),
                ("crown_enniskillen_relief_column_1594",),
            ),
            "hced-Clontibret1595-1": (
                "battle_of_clontibret:1595:1595",
                "day",
                "engagement",
                ("hugh_oneill_clontibret_force_1595",),
                ("bagenal_monaghan_relief_column_1595",),
            ),
            "hced-Blackwater1598-1": (
                "battle_of_the_yellow_ford:1598:1598",
                "day",
                "engagement",
                ("oneill_odonnell_yellow_ford_host_1598",),
                ("bagenal_blackwater_relief_army_1598",),
            ),
            "hced-Limerick1651-1": (
                "siege_of_limerick:1651:1651",
                "day_range",
                "siege",
                ("ireton_new_model_army_limerick_1651",),
                ("hugh_dubh_oneill_limerick_garrison_1651",),
            ),
        }
        self.assertEqual(set(expected), WAVE8_IRISH_HISTORY_CONTRACT_IDS)
        for candidate_id, (
            key,
            precision,
            granularity,
            side_1,
            side_2,
        ) in expected.items():
            contract = WAVE8_IRISH_HISTORY_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["canonical_key"], key)
            self.assertEqual(canonical["date_precision"], precision)
            self.assertEqual(canonical["granularity"], granularity)
            self.assertTrue(canonical["date_text"])
            self.assertEqual(tuple(contract["side_1_entity_ids"]), side_1)
            self.assertEqual(tuple(contract["side_2_entity_ids"]), side_2)
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        self.assertEqual(WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES, {})

    def test_derry_is_terminal_unopposed_and_unknown_never_becomes_draw(self) -> None:
        self.assertEqual(
            WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS,
            {"hced-Derry1600-1"},
        )
        derry = WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS["hced-Derry1600-1"]
        self.assertEqual(derry["disposition"], "terminal_exclusion")
        self.assertEqual(
            derry["hold_category"],
            "not_an_engagement_unopposed_occupation",
        )
        self.assertEqual(derry["result_type"], "unknown")
        self.assertEqual(derry["reviewed_outcome"], "unknown")
        self.assertTrue(derry["unknown_is_never_draw"])
        self.assertNotIn("winner_side", derry)
        self.assertEqual(
            derry["side_1_entity_ids"],
            ["docwra_lough_foyle_expedition_1600"],
        )
        self.assertEqual(derry["side_2_entity_ids"], [])
        self.assertEqual(derry["opposing_force_status"], "none_evidenced")
        self.assertIn("without opposition", derry["hold_reason"])
        self.assertIn("never encoded as a draw", derry["hold_reason"])

    def test_dublin_actions_are_distinct_and_cross_source_absence_is_signed(self) -> None:
        self.assertIs(
            WAVE8_IRISH_HISTORY_IWBD_DUPLICATE_DISPOSITIONS,
            WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS,
        )
        self.assertEqual(WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(
            set(WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS),
            {"hced-Dublin (1st)1171-1"},
        )
        self.assertEqual(
            set(WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS),
            {"hced-Dublin (1st)1171-1"},
        )
        related = WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS[
            "hced-Dublin (1st)1171-1"
        ]
        self.assertEqual(
            related["hced_candidate_id"],
            "hced-Dublin (2nd)1171-1",
        )
        self.assertEqual(
            related["relationship"],
            "earlier_Ascall_counterattack_not_Ruaidri_siege",
        )
        first_dublin = next(
            row
            for row in self.rows
            if row["candidate_id"] == "hced-Dublin (1st)1171-1"
        )
        self.assertEqual(
            canonical_hced_row_sha256(first_dublin),
            related["raw_row_sha256"],
        )
        self.assertEqual(
            validate_wave8_irish_history_integration_dispositions(
                self.rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_source_duplicate_dispositions": 0,
                "integration_dispositions": 1,
                "related_hced_dispositions": 1,
            },
        )

        changed = copy.deepcopy(self.rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Dublin (1st)1171-1"
        )["name"] = "Dublin merged"
        with self.assertRaisesRegex(ValueError, "Dublin fingerprint changed"):
            validate_wave8_irish_history_integration_dispositions(
                changed,
                self.iwbd_rows,
            )

        with self.assertRaisesRegex(ValueError, "unadjudicated IWBD duplicate"):
            validate_wave8_irish_history_integration_dispositions(
                self.rows,
                [
                    {
                        "candidate_id": "iwbd-new-clontarf",
                        "name": "Clontarf",
                        "start_date": "1014-04-23",
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "unadjudicated release duplicates"):
            validate_wave8_irish_history_integration_dispositions(
                self.rows,
                [],
                [{"id": "existing-tara", "name": "Battle of Tara", "year": 980}],
            )

    def test_all_promoted_points_are_quarantined_without_changing_countries(self) -> None:
        self.assertEqual(
            WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS,
            WAVE8_IRISH_HISTORY_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            set(WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS),
            WAVE8_IRISH_HISTORY_CONTRACT_IDS,
        )
        self.assertEqual(
            wave8_irish_history_location_quarantine_additions(),
            {
                "country": WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS,
            },
        )
        source_ids = {source["id"] for source in WAVE8_IRISH_HISTORY_SOURCES}
        for record in WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS.values():
            self.assertEqual(record["action"], "withhold_point")
            self.assertTrue(set(record["evidence_refs"]) <= source_ids)
            self.assertTrue(record["reason"])

        events = self._promoted()
        self.assertEqual(len(events), 8)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_IRISH_HISTORY_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            self.assertNotIn("geometry", event)
            self.assertIn("modern_location_country", event)
            self.assertIn("location_provenance", event)
        self.assertNotIn(
            "hced-Derry1600-1",
            {event["hced_candidate_id"] for event in events},
        )

    def test_promoter_emits_only_exact_forces_and_direct_results(self) -> None:
        events = self._promoted()
        self.assertEqual(
            [event["year"] for event in events],
            [980, 1014, 1171, 1318, 1594, 1595, 1598, 1651],
        )
        self.assertEqual(len({event["id"] for event in events}), 8)
        for event in events:
            candidate_id = event["hced_candidate_id"]
            contract = WAVE8_IRISH_HISTORY_CONTRACTS[candidate_id]
            participant_ids = {item["entity_id"] for item in event["participants"]}
            self.assertEqual(
                participant_ids,
                {
                    *contract["side_1_entity_ids"],
                    *contract["side_2_entity_ids"],
                },
            )
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_victory"
            }
            losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_defeat"
            }
            self.assertEqual(winners, set(contract["side_1_entity_ids"]))
            self.assertEqual(losers, set(contract["side_2_entity_ids"]))
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

        clontarf = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Clontarf1014-1"
        )
        self.assertNotIn("viking", " ".join(
            participant["entity_id"] for participant in clontarf["participants"]
        ))
        tara = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Tara980-1"
        )
        self.assertNotIn("danish", " ".join(
            participant["entity_id"] for participant in tara["participants"]
        ))

    def test_installers_are_exact_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_irish_history_entities(entities)
        install_wave8_irish_history_sources(sources)
        self.assertEqual(
            set(entities),
            {entity["id"] for entity in WAVE8_IRISH_HISTORY_ENTITIES},
        )
        self.assertEqual(
            set(sources),
            {source["id"] for source in WAVE8_IRISH_HISTORY_SOURCES},
        )

        entity_id = next(iter(entities))
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_irish_history_entities({entity_id: {"id": entity_id}})
        source_id = next(iter(sources))
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_irish_history_sources({source_id: {"id": source_id}})

    def test_exact_promotion_rejects_existing_event_duplicate(self) -> None:
        existing = [
            *self._pre_lane_events(),
            {"id": "existing-clontarf", "name": "Battle of Clontarf", "year": 1014},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_irish_history_contracts(
                self.rows,
                self._entities(),
                existing,
            )


if __name__ == "__main__":
    unittest.main()
