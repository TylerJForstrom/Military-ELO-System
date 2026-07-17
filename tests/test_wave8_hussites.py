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
from military_elo.promotion.wave8_hussites import (
    WAVE8_HUSSITES_CONTRACT_IDS,
    WAVE8_HUSSITES_CONTRACTS,
    WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS,
    WAVE8_HUSSITES_ENTITIES,
    WAVE8_HUSSITES_EXCLUSION_IDS,
    WAVE8_HUSSITES_EXCLUSIONS,
    WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS,
    WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_HUSSITES_EXTERNAL_OWNER_IDS,
    WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE,
    WAVE8_HUSSITES_HOLD_IDS,
    WAVE8_HUSSITES_HOLDS,
    WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS,
    WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_HUSSITES_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS,
    WAVE8_HUSSITES_NONPROMOTIONS,
    WAVE8_HUSSITES_OUTCOME_OVERRIDES,
    WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_HUSSITES_RESERVED_IDS,
    WAVE8_HUSSITES_SOURCES,
    WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS,
    WAVE8_HUSSITES_TERMINAL_EXCLUSIONS,
    install_wave8_hussites_entities,
    install_wave8_hussites_sources,
    promote_wave8_hussites_contracts,
    validate_wave8_hussites_integration_dispositions,
    validate_wave8_hussites_queue_contracts,
    wave8_hussites_audit_signature,
    wave8_hussites_cohort_counts,
    wave8_hussites_counts,
    wave8_hussites_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_hussites_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "794b3500c15791d514778c0a76e742e60bc83925d42e685b7ecf408120543cd3"
)

PORICI_HUSSITE_ID = "zizka_tabor_marching_force_porici_1420"
PORICI_ROYALIST_ID = "sternberg_bohemian_royalist_interception_force_porici_1420"
VITKOV_HUSSITE_ID = "zizka_prague_vitkov_defensive_force_1420"
VITKOV_CRUSADER_ID = "meissen_austrian_crusader_assault_force_vitkov_1420"
BOR_HUSSITE_ID = "zizka_tabor_field_force_pansky_bor_1420"
BOR_ROYALIST_ID = "rosenberg_svamberk_plauen_royalist_coalition_pansky_bor_1420"
VYSEHRAD_HUSSITE_ID = "prague_orebite_tabor_field_coalition_vysehrad_1420"
VYSEHRAD_CRUSADER_ID = "sigismund_crusader_relief_army_vysehrad_1420"
ZATEC_HUSSITE_ID = "zatec_hussite_garrison_and_civic_defenders_1421"
ZATEC_CRUSADER_ID = "western_second_crusade_besieging_army_zatec_1421"
VLADAR_HUSSITE_ID = "zizka_hussite_retreating_force_vladar_1421"
VLADAR_LANDFRIED_ID = "pilsen_landfrieden_pursuit_force_vladar_1421"
KUTNA_CAMPAIGN_HUSSITE_ID = "prague_tabor_hussite_counteroffensive_army_1422"
NEBOVIDY_CRUSADER_ID = "sigismund_crusader_resistance_force_nebovidy_1422"
HABRY_CRUSADER_ID = "sigismund_crusader_rear_guard_habry_1422"
BROD_CRUSADER_ID = "sigismund_crusader_defenders_nemecky_brod_1422"
HORICE_HUSSITE_ID = "zizka_orebite_field_army_horice_1423"
HORICE_LORDS_ID = "cenek_vartenberk_lords_union_force_horice_1423"
SKALICE_HUSSITE_ID = "zizka_hradec_field_force_ceska_skalice_1424"
SKALICE_LORDS_ID = "eastern_bohemian_catholic_lords_force_skalice_1424"
AUSSIG_HUSSITE_ID = "hussite_field_coalition_aussig_1426"
AUSSIG_RELIEF_ID = "saxon_meissen_thuringian_lusatian_relief_army_aussig_1426"


EXPECTED_RAW_HASHES = {
    "hced-Aussig1426-1": "9c13e1a73ff676dce63ce047175186d9a6ea667932c9f1309095d27a0ba0418a",
    "hced-Bor Pansky1420-1": "bdc250c918919b6e78024f7f82afe8770b19e2dbc6a2fd2f8c8621d2a019cea0",
    "hced-Habry1422-1": "f4c479cbec3400776a625b3283f567d76d03c07e54b9acdf1f27d367f675b322",
    "hced-Horice1423-1": "62a97f84db55d81bf317a4f4e3fc8cecc2821bb57639737c86016bc76a8d19f1",
    "hced-Kutna Hora1421-1": "1dfaeed1298adef4f1f2884d2bf194138daa81060df1613740560ecc9e013069",
    "hced-Nebovidy1422-1": "533cf7f274b37ccd55306483d1b9934b9ef2ae2dd5d5fb338c0cf8a535181b1f",
    "hced-Nemecky Brod1422-1": "e611517f7a12b77a0c7fd371fe36d932634d77af32e79265008a3e7ba040010a",
    "hced-Porici1420-1": "dac2bf7ba4f20d570116dfe9ddc643639d0a72abf33669d9e6d07a768f9b4105",
    "hced-Skalice1424-1": "1536af2f8b8e123203e3e42588043726b9e977fce622c96131bc2233dc488661",
    "hced-Vitkov Hill1420-1": "d395932b8ff1c9e470ca879f1fab796792df1058c8aeb852dc8729e6f14c4a5d",
    "hced-Vladar1421-1": "bd1647e64134313eafe30d855b2553bb3a77d31cb91af97735ebe1c8b647834e",
    "hced-Vysehrad1420-1": "8831cd0aa7c47920cbae1e51bd69e6ac9692c9bdaa34404ad101cf43db80f598",
    "hced-Zatec1421-1": "1e99ddf6f96f2cf434b6f5d75c05590fad0f85f017e1de9c5261c23cb88114e3",
    "hced-Zwettl-1": "ae3514bdfa173cb574a252cc1b4cac70398e97b10e1d1acfea006ec73324e3e5",
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Porici1420-1": ({PORICI_HUSSITE_ID}, {PORICI_ROYALIST_ID}),
    "hced-Vitkov Hill1420-1": ({VITKOV_HUSSITE_ID}, {VITKOV_CRUSADER_ID}),
    "hced-Bor Pansky1420-1": ({BOR_HUSSITE_ID}, {BOR_ROYALIST_ID}),
    "hced-Vysehrad1420-1": ({VYSEHRAD_HUSSITE_ID}, {VYSEHRAD_CRUSADER_ID}),
    "hced-Zatec1421-1": ({ZATEC_HUSSITE_ID}, {ZATEC_CRUSADER_ID}),
    "hced-Vladar1421-1": ({VLADAR_HUSSITE_ID}, {VLADAR_LANDFRIED_ID}),
    "hced-Nebovidy1422-1": (
        {KUTNA_CAMPAIGN_HUSSITE_ID},
        {NEBOVIDY_CRUSADER_ID},
    ),
    "hced-Habry1422-1": ({KUTNA_CAMPAIGN_HUSSITE_ID}, {HABRY_CRUSADER_ID}),
    "hced-Nemecky Brod1422-1": (
        {KUTNA_CAMPAIGN_HUSSITE_ID},
        {BROD_CRUSADER_ID},
    ),
    "hced-Horice1423-1": ({HORICE_HUSSITE_ID}, {HORICE_LORDS_ID}),
    "hced-Skalice1424-1": ({SKALICE_HUSSITE_ID}, {SKALICE_LORDS_ID}),
    "hced-Aussig1426-1": ({AUSSIG_HUSSITE_ID}, {AUSSIG_RELIEF_ID}),
}

EXPECTED_DATES = {
    "hced-Porici1420-1": (1420, "night of 19-20 May 1420", "day_range"),
    "hced-Vitkov Hill1420-1": (1420, "14 July 1420", "day"),
    "hced-Bor Pansky1420-1": (1420, "12 October 1420", "day"),
    "hced-Vysehrad1420-1": (1420, "1 November 1420", "day"),
    "hced-Zatec1421-1": (1421, "September-2 October 1421", "month_to_day_range"),
    "hced-Vladar1421-1": (1421, "mid-November 1421", "month_uncertain"),
    "hced-Nebovidy1422-1": (1422, "6 January 1422", "day"),
    "hced-Habry1422-1": (1422, "8 January 1422", "day"),
    "hced-Nemecky Brod1422-1": (1422, "9-10 January 1422", "day_range"),
    "hced-Horice1423-1": (1423, "April 1423", "month"),
    "hced-Skalice1424-1": (1424, "6 January 1424", "day"),
    "hced-Aussig1426-1": (1426, "16 June 1426", "day"),
}

VARIANT_LABEL_IDS = {
    "hced-Domazlice1431-1",
    "hced-Grotniki1439-1",
    "hced-Kromeriz1423-1",
    "hced-Lipany1434-1",
    "hced-Malesov1424-1",
    "hced-Strachuv1423-1",
    "hced-Sudomer1420-1",
    "hced-Tachov1427-1",
    "hced-Tynec1423-1",
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Wave8HussitesTests(unittest.TestCase):
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
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "hussites"
            or normalize_label(row.get("side_2_raw")) == "hussites"
        ]

    def _installed(self) -> tuple[dict, dict]:
        entities = copy.deepcopy(self.release_entities)
        sources: dict[str, dict] = {}
        install_wave8_hussites_entities(entities)
        install_wave8_hussites_sources(sources)
        return entities, sources

    def _emit(self, existing_events=None) -> tuple[dict, dict, list]:
        entities, sources = self._installed()
        existing = (
            copy.deepcopy(self.release_events)
            if existing_events is None
            else copy.deepcopy(existing_events)
        )
        events = promote_wave8_hussites_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_funnel_and_queue_lock_the_complete_fourteen_row_exact_cohort(self) -> None:
        scoped_rows = {
            str(row["candidate_id"]): row
            for row in self.funnel["row_label_data"]
            if "hussites" in row.get("blocker_labels", [])
        }
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(len(scoped_rows), 14)
        self.assertEqual(exact_ids, set(EXPECTED_RAW_HASHES))
        self.assertEqual(set(scoped_rows), exact_ids)
        self.assertEqual(WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS, exact_ids)

        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(scoped_rows))
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), FUNNEL_CANDIDATE_ID_SHA256)
        label_rows = [
            row for row in self.funnel["labels"] if row.get("label") == "hussites"
        ]
        self.assertEqual(len(label_rows), 1)
        label_row = label_rows[0]
        self.assertEqual(label_row["event_candidate_id_sha256"], FUNNEL_CANDIDATE_ID_SHA256)
        self.assertEqual(label_row["events_touched"], 14)
        self.assertEqual(label_row["unresolved_side_attempts"], 14)
        self.assertEqual(label_row["sole_blocker_events"], 4)
        self.assertEqual(label_row["failure_cases"]["zero_time_valid_candidates"], 14)
        sole_ids = {
            candidate_id
            for candidate_id, row in scoped_rows.items()
            if row.get("sole_blocker_label") == "hussites"
        }
        self.assertEqual(
            sole_ids,
            {
                "hced-Kutna Hora1421-1",
                "hced-Nebovidy1422-1",
                "hced-Nemecky Brod1422-1",
                "hced-Vitkov Hill1420-1",
            },
        )
        for row in scoped_rows.values():
            self.assertTrue(
                any(
                    failure.get("label") == "hussites"
                    for failure in row.get("label_failures", [])
                )
            )

    def test_hashes_dispositions_counts_and_ownership_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(canonical_hced_row_sha256(by_id[candidate_id]), expected_hash)

        self.assertEqual(len(WAVE8_HUSSITES_CONTRACT_IDS), 12)
        self.assertEqual(
            WAVE8_HUSSITES_HOLD_IDS,
            {"hced-Kutna Hora1421-1", "hced-Zwettl-1"},
        )
        self.assertEqual(WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_HUSSITES_EXTERNAL_OWNER_IDS, frozenset())
        self.assertEqual(WAVE8_HUSSITES_EXCLUSION_IDS, frozenset())
        self.assertIs(WAVE8_HUSSITES_EXCLUSIONS, WAVE8_HUSSITES_TERMINAL_EXCLUSIONS)
        self.assertIs(
            WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS,
            WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS,
        )
        self.assertEqual(set(WAVE8_HUSSITES_NONPROMOTIONS), WAVE8_HUSSITES_HOLD_IDS)
        self.assertEqual(WAVE8_HUSSITES_RESERVED_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            WAVE8_HUSSITES_RESERVED_IDS | WAVE8_HUSSITES_EXTERNAL_OWNER_IDS,
            WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS,
        )

        self.assertEqual(
            validate_wave8_hussites_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 0,
                "holds": 2,
                "promotion_contracts": 12,
                "reviewed_hced_rows": 14,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_hussites_counts(),
            {
                "country_quarantine_additions": 1,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "holds": 2,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 14,
                "new_entities": 22,
                "new_sources": 16,
                "newly_rated_events": 12,
                "outcome_overrides": 0,
                "point_quarantine_additions": 12,
                "promotion_contracts": 12,
                "reviewed_hced_rows": 14,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_hussites_cohort_counts(),
            {
                "aussig_campaign_1426": 1,
                "hussite_war_1420": 4,
                "kutna_brod_counteroffensive_1422": 3,
                "second_crusade_zatec_1421": 1,
                "western_bohemian_campaign_1421": 1,
                "zizka_internal_campaigns_1423_1424": 2,
            },
        )

    def test_semantic_signature_is_pinned_and_sha256_shaped(self) -> None:
        self.assertEqual(
            WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE,
            "1450fa3f575c25c8b53a3a65dd92781d41547641241f05e8e6dcb22dcc1b39bf",
        )
        self.assertEqual(
            wave8_hussites_audit_signature(),
            WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(len(bytes.fromhex(WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE)), 32)

    def test_sources_and_entities_are_parseable_bounded_and_non_generic(self) -> None:
        self.assertEqual(len(WAVE8_HUSSITES_SOURCES), 16)
        self.assertEqual(len(WAVE8_HUSSITES_ENTITIES), 22)
        source_ids = {str(source["id"]) for source in WAVE8_HUSSITES_SOURCES}
        source_families = {
            str(source["source_family_id"]) for source in WAVE8_HUSSITES_SOURCES
        }
        self.assertEqual(len(source_ids), 16)
        self.assertEqual(len(source_families), 16)
        for source in WAVE8_HUSSITES_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))

        entity_ids = {str(entity["id"]) for entity in WAVE8_HUSSITES_ENTITIES}
        self.assertTrue(entity_ids.isdisjoint(self.release_entities))
        used_ids = {
            str(entity_id)
            for contract in WAVE8_HUSSITES_CONTRACTS.values()
            for side in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[side]
        }
        self.assertEqual(used_ids, entity_ids)
        for entity in WAVE8_HUSSITES_ENTITIES:
            parsed = Entity.from_dict(entity)
            self.assertEqual(parsed.start_year, parsed.end_year)
            self.assertIn(parsed.start_year, range(1420, 1427))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertIn("modern state", entity["continuity_note"].casefold())
            self.assertNotIn(normalize_label(entity["name"]), {"hussite", "hussites"})
            self.assertTrue(set(entity["source_ids"]) <= source_ids)

    def test_contract_dates_actors_outcomes_provenance_and_ownership_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_HUSSITES_SOURCES}
        queue_by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, contract in WAVE8_HUSSITES_CONTRACTS.items():
            year, date_text, precision = EXPECTED_DATES[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual((canonical["year_low"], canonical["year_high"]), (year, year))
            self.assertEqual(canonical["date_text"], date_text)
            self.assertEqual(canonical["date_precision"], precision)
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "military_elo.promotion.wave8_hussites",
                    "status": "canonical_hced_owner",
                },
            )
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(
                set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"])
            )
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
            row = queue_by_id[candidate_id]
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])

        self.assertEqual(
            WAVE8_HUSSITES_CONTRACTS["hced-Zatec1421-1"]["canonical_event"][
                "granularity"
            ],
            "siege",
        )
        self.assertEqual(
            WAVE8_HUSSITES_CONTRACTS["hced-Vladar1421-1"]["canonical_event"][
                "granularity"
            ],
            "defensive_breakout",
        )
        self.assertEqual(
            WAVE8_HUSSITES_CONTRACTS["hced-Nemecky Brod1422-1"]["canonical_event"][
                "granularity"
            ],
            "battle_and_storm",
        )
        self.assertEqual(WAVE8_HUSSITES_OUTCOME_OVERRIDES, {})

    def test_january_1422_campaign_actor_is_shared_but_opponents_are_not(self) -> None:
        campaign_ids = {
            "hced-Nebovidy1422-1",
            "hced-Habry1422-1",
            "hced-Nemecky Brod1422-1",
        }
        for candidate_id in campaign_ids:
            self.assertEqual(
                WAVE8_HUSSITES_CONTRACTS[candidate_id]["side_1_entity_ids"],
                [KUTNA_CAMPAIGN_HUSSITE_ID],
            )
        self.assertEqual(
            {
                WAVE8_HUSSITES_CONTRACTS[candidate_id]["side_2_entity_ids"][0]
                for candidate_id in campaign_ids
            },
            {NEBOVIDY_CRUSADER_ID, HABRY_CRUSADER_ID, BROD_CRUSADER_ID},
        )
        other_contracts = set(WAVE8_HUSSITES_CONTRACTS) - campaign_ids
        self.assertFalse(
            any(
                KUTNA_CAMPAIGN_HUSSITE_ID
                in (
                    set(WAVE8_HUSSITES_CONTRACTS[candidate_id]["side_1_entity_ids"])
                    | set(WAVE8_HUSSITES_CONTRACTS[candidate_id]["side_2_entity_ids"])
                )
                for candidate_id in other_contracts
            )
        )

    def test_kutna_hora_and_zwettl_are_unknown_holds_never_draws(self) -> None:
        self.assertEqual(
            set(WAVE8_HUSSITES_HOLDS),
            {"hced-Kutna Hora1421-1", "hced-Zwettl-1"},
        )
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        for hold in WAVE8_HUSSITES_HOLDS.values():
            self.assertTrue(forbidden.isdisjoint(hold))
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["reviewed_outcome"], "unknown")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertIn("never a draw", hold["hold_reason"].casefold())
            self.assertEqual(
                hold["duplicate_ownership"]["status"],
                "held_hced_owner",
            )

        kutna = WAVE8_HUSSITES_HOLDS["hced-Kutna Hora1421-1"]
        self.assertEqual(
            kutna["hold_category"],
            "row_conflates_distinct_actors_and_opposed_tactical_phases",
        )
        self.assertIn("was not defeated", kutna["hold_reason"])
        self.assertEqual(
            kutna["canonical_event"]["granularity"],
            "composite_battle_occupation_breakout",
        )
        zwettl = WAVE8_HUSSITES_HOLDS["hced-Zwettl-1"]
        self.assertEqual(
            zwettl["hold_category"],
            "reciprocal_two_phase_tactical_outcome",
        )
        self.assertIn("counterattacked", zwettl["hold_reason"])
        self.assertEqual(zwettl["canonical_event"]["date_text"], "25 March 1427")
        self.assertEqual(WAVE8_HUSSITES_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS, {})

    def test_emission_is_twelve_parseable_wins_without_generic_actors_or_draws(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 12)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertFalse(WAVE8_HUSSITES_HOLD_IDS & set(by_candidate))
        forbidden_ids = {
            "hussite",
            "hussites",
            "habsburg_empire",
            "holy_roman_empire",
            "hungary",
            "pilsen",
            "royalist_barons",
        }
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_defeat"
            }
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            self.assertFalse((winners | losers) & forbidden_ids)
            terminations = {item["termination"] for item in event["participants"]}
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            contract = WAVE8_HUSSITES_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

    def test_promotions_are_deterministic_and_installs_are_idempotent(self) -> None:
        entities, sources = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        install_wave8_hussites_entities(entities)
        install_wave8_hussites_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        events_1 = promote_wave8_hussites_contracts(
            self.hced_rows,
            entities,
            copy.deepcopy(self.release_events),
        )
        events_2 = promote_wave8_hussites_contracts(
            self.hced_rows,
            entities,
            copy.deepcopy(self.release_events),
        )
        self.assertEqual(events_1, events_2)
        self.assertEqual(len({event["id"] for event in events_1}), 12)
        self.assertEqual(
            [(event["year"], event["hced_candidate_id"]) for event in events_1],
            sorted((event["year"], event["hced_candidate_id"]) for event in events_1),
        )

        colliding_entities = copy.deepcopy(self.release_entities)
        colliding_entities[PORICI_HUSSITE_ID] = {"id": PORICI_HUSSITE_ID}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_hussites_entities(colliding_entities)
        colliding_sources = {"wave8_hussites_fudge_chronicle": {"id": "wrong"}}
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_hussites_sources(colliding_sources)

    def test_queue_hash_inventory_entity_window_and_duplicate_guards_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in mutated if item["candidate_id"] == "hced-Vitkov Hill1420-1"
        )
        row["name"] = "Vitkov Hill drifted"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave8_hussites_queue_contracts(mutated)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Aussig1426-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_hussites_queue_contracts(missing)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row["candidate_id"] == "hced-Aussig1426-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_hussites_queue_contracts(duplicated)

        expanded = copy.deepcopy(self.hced_rows)
        expanded.append(
            {
                "candidate_id": "hced-future-hussites-row",
                "side_1_raw": "Hussites",
                "side_2_raw": "Future opponent",
                "name": "Future exact row",
                "year_low": 1425,
                "year_high": 1425,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Hussites inventory changed"):
            validate_wave8_hussites_queue_contracts(expanded)

        entities, _ = self._installed()
        missing_entity = copy.deepcopy(entities)
        missing_entity.pop(VITKOV_HUSSITE_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_hussites_contracts(
                self.hced_rows,
                missing_entity,
                self.release_events,
            )
        wrong_window = copy.deepcopy(entities)
        wrong_window[VITKOV_HUSSITE_ID]["start_year"] = 1421
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_hussites_contracts(
                self.hced_rows,
                wrong_window,
                self.release_events,
            )

        candidate_collision = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_owner",
                "name": "Unrelated",
                "year": 1420,
                "hced_candidate_id": "hced-Vitkov Hill1420-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_hussites_contracts(
                self.hced_rows,
                entities,
                candidate_collision,
            )
        name_collision = [
            *copy.deepcopy(self.release_events),
            {"id": "future_twin", "name": "Battle of Vitkov Hill", "year": 1420},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_hussites_contracts(
                self.hced_rows,
                entities,
                name_collision,
            )

    def test_duplicate_audit_is_complete_and_integration_twins_fail_closed(self) -> None:
        self.assertEqual(
            set(WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT),
            set(EXPECTED_RAW_HASHES),
        )
        dispositions = {
            **WAVE8_HUSSITES_CONTRACTS,
            **WAVE8_HUSSITES_NONPROMOTIONS,
        }
        for candidate_id, audit in WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT.items():
            aliases = audit["aliases"]
            self.assertEqual(aliases, sorted(set(aliases)))
            self.assertTrue(all(alias == normalize_label(alias) for alias in aliases))
            canonical = dispositions[candidate_id]["canonical_event"]
            self.assertIn(normalize_label(canonical["name"]), aliases)
            self.assertEqual(
                audit["years"],
                [canonical["year_low"], canonical["year_high"]],
            )

        self.assertEqual(WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_hussites_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 14,
            },
        )

        hced_twin = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-vitkov-twin",
                "name": "Battle of Vitkov Hill",
                "year_best": 1420,
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_hussites_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
                self.release_events,
            )

        iwbd_twin = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-aussig-twin",
                "name": "Aussig",
                "start_date": "1426-06-16",
                "end_date": "1426-06-16",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_hussites_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
                self.release_events,
            )

        release_twin = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_release_skalice_twin",
                "name": "Battle of Ceska Skalice",
                "year": 1424,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_hussites_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_location_quarantines_are_promoted_only_and_do_not_mutate_globals(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS, WAVE8_HUSSITES_CONTRACT_IDS)
        self.assertEqual(
            WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Nemecky Brod1422-1"},
        )
        point_overlap = (
            WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS
            & HCED_POINT_QUARANTINE_IDS
        )
        country_overlap = (
            WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS
            & HCED_COUNTRY_QUARANTINE_IDS
        )
        self.assertIn(
            point_overlap,
            (frozenset(), WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS),
        )
        self.assertIn(
            country_overlap,
            (frozenset(), WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS),
        )
        self.assertEqual(
            WAVE8_HUSSITES_LOCATION_QUARANTINE_ADDITIONS,
            {
                "country": WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            wave8_hussites_location_quarantine_additions(),
            WAVE8_HUSSITES_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            set(WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS),
            WAVE8_HUSSITES_CONTRACT_IDS,
        )
        for candidate_id, review in WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS.items():
            expected_actions = {"withhold_point"}
            if candidate_id == "hced-Nemecky Brod1422-1":
                expected_actions.add("withhold_country")
            self.assertEqual(set(review["actions"]), expected_actions)
            self.assertTrue(review["reason"])

        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        for candidate_id, event in by_candidate.items():
            self.assertNotIn("geometry", event)
            if candidate_id == "hced-Nemecky Brod1422-1":
                self.assertNotIn("modern_location_country", event)
                self.assertNotIn("location_provenance", event)
            else:
                self.assertEqual(event["modern_location_country"], "Czechia")
                self.assertIn("location_provenance", event)
        self.assertFalse(WAVE8_HUSSITES_HOLD_IDS & WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_composite_and_factional_hussite_variants_do_not_creep_into_exact_lane(self) -> None:
        variant_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if any(
                "hussit" in normalize_label(row.get(field))
                for field in ("side_1_raw", "side_2_raw")
            )
            and all(
                normalize_label(row.get(field)) != "hussites"
                for field in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(variant_ids, VARIANT_LABEL_IDS)
        self.assertTrue(variant_ids.isdisjoint(WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS))
        self.assertTrue(variant_ids.isdisjoint(WAVE8_HUSSITES_RESERVED_IDS))


if __name__ == "__main__":
    unittest.main()
