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
from military_elo.promotion.wave8_rajputs import (
    WAVE8_RAJPUTS_CONTRACT_IDS,
    WAVE8_RAJPUTS_CONTRACTS,
    WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS,
    WAVE8_RAJPUTS_ENTITIES,
    WAVE8_RAJPUTS_EXCLUSION_IDS,
    WAVE8_RAJPUTS_EXCLUSIONS,
    WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS,
    WAVE8_RAJPUTS_FINAL_AUDIT_SIGNATURE,
    WAVE8_RAJPUTS_FUNNEL_SUMMARY,
    WAVE8_RAJPUTS_GREEDY_AUDIT,
    WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_HOLD_IDS,
    WAVE8_RAJPUTS_HOLDS,
    WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS,
    WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_RAJPUTS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS,
    WAVE8_RAJPUTS_NONPROMOTIONS,
    WAVE8_RAJPUTS_OUTCOME_OVERRIDES,
    WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_RAJPUTS_RESERVED_IDS,
    WAVE8_RAJPUTS_ROW_DISPOSITIONS,
    WAVE8_RAJPUTS_SOURCES,
    WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS,
    WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS,
    install_wave8_rajputs_entities,
    install_wave8_rajputs_sources,
    promote_wave8_rajputs_contracts,
    validate_wave8_rajputs_funnel,
    validate_wave8_rajputs_integration_dispositions,
    validate_wave8_rajputs_queue_contracts,
    wave8_rajputs_audit_signature,
    wave8_rajputs_cohort_counts,
    wave8_rajputs_counts,
    wave8_rajputs_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_rajputs_"

GHAGHRA_MUGHAL = "babur_mughal_field_army_ghaghra_1529"
GHAGHRA_DEFENSE = "afghan_bengal_river_defense_ghaghra_1529"
FATEHPUR_EXPEDITION = "vaman_rao_george_thomas_fatehpur_expedition_1799"
FATEHPUR_JAIPUR = "sawai_pratap_singh_jaipur_army_fatehpur_1799"
SCINDIA_CAMPAIGN = "scindia_de_boigne_rajputana_campaign_army_1790"
PATAN_COALITION = "jaipur_jodhpur_ismail_beg_coalition_patan_1790"
MERTA_MARWAR = "vijai_singh_marwar_rathor_army_merta_1790"
CHAHAMANA_REGIME = "prithviraja_iii_chahamana_regime_and_army_1178_1192"
GHURID_EASTERN_ARMY = "muizz_al_din_ghurid_eastern_army_1173_1206"


EXPECTED_RAW_ROWS = {
    "hced-Chitor1567-1": (
        "Mughal Empire",
        "Rajputs",
        "Mughal Empire",
        "Rajputs",
        True,
        1567,
    ),
    "hced-Fatehpur1799-1": (
        "Hariana",
        "Rajputs",
        "Hariana",
        "Rajputs",
        True,
        1799,
    ),
    "hced-Gogra1529-1": (
        "Mughal Empire",
        "Rajputs",
        "Mughal Empire",
        "Rajputs",
        True,
        1529,
    ),
    "hced-Merta1790-1": (
        "Rajputs",
        "Marathas",
        "Draw",
        None,
        False,
        1790,
    ),
    "hced-Patan1790-1": (
        "Marathas",
        "Rajputs",
        "Marathas",
        "Rajputs",
        True,
        1790,
    ),
    "hced-Taraori1191-1": (
        "Rajputs",
        "Ghor",
        "Rajputs",
        "Ghor",
        True,
        1191,
    ),
    "hced-Taraori1192-1": (
        "Ghor",
        "Rajputs",
        "Ghor",
        "Rajputs",
        True,
        1192,
    ),
}


EXPECTED_EVENTS = {
    "hced-Fatehpur1799-1": {
        "name": "Battle of Fatehpur, Shekhawati",
        "date": ("month", "March 1799"),
        "winner": {FATEHPUR_JAIPUR},
        "loser": {FATEHPUR_EXPEDITION},
        "override": True,
        "reversal": True,
    },
    "hced-Gogra1529-1": {
        "name": "Battle of Ghaghra",
        "date": ("month", "May 1529"),
        "winner": {GHAGHRA_MUGHAL},
        "loser": {GHAGHRA_DEFENSE},
        "override": False,
        "reversal": False,
    },
    "hced-Merta1790-1": {
        "name": "Battle of Merta",
        "date": ("month", "September 1790 (published day varies)"),
        "winner": {SCINDIA_CAMPAIGN},
        "loser": {MERTA_MARWAR},
        "override": True,
        "reversal": False,
    },
    "hced-Patan1790-1": {
        "name": "Battle of Patan",
        "date": ("month", "June 1790 (published day varies)"),
        "winner": {SCINDIA_CAMPAIGN},
        "loser": {PATAN_COALITION},
        "override": False,
        "reversal": False,
    },
    "hced-Taraori1191-1": {
        "name": "First Battle of Tarain",
        "date": ("year", "1191"),
        "winner": {CHAHAMANA_REGIME},
        "loser": {GHURID_EASTERN_ARMY},
        "override": False,
        "reversal": False,
    },
    "hced-Taraori1192-1": {
        "name": "Second Battle of Tarain",
        "date": ("year", "1192"),
        "winner": {GHURID_EASTERN_ARMY},
        "loser": {CHAHAMANA_REGIME},
        "override": False,
        "reversal": False,
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8RajputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "wave8-funnel-current.json")
        cls.lane_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_RAJPUTS_RESERVED_IDS
        }

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_RAJPUTS_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_rajputs_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_RAJPUTS_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_rajputs_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_RAJPUTS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_rajputs_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_signature_counts_cohorts_and_all_dispositions_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_RAJPUTS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_RAJPUTS_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS
            ),
            "funnel_summary": WAVE8_RAJPUTS_FUNNEL_SUMMARY,
            "greedy_audit": WAVE8_RAJPUTS_GREEDY_AUDIT,
            "hced_duplicate_dispositions": WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS,
            "holds": WAVE8_RAJPUTS_HOLDS,
            "integration_dispositions": WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_RAJPUTS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS
            ),
            "row_dispositions": WAVE8_RAJPUTS_ROW_DISPOSITIONS,
            "sources": WAVE8_RAJPUTS_SOURCES,
            "terminal_exclusions": WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            independent,
            "dabc16f4566a9bd287dff08dd9a4eac35b7e2fb76f30fa9539c390601b43ddaf",
        )
        self.assertEqual(independent, WAVE8_RAJPUTS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_rajputs_audit_signature(), independent)

        self.assertEqual(WAVE8_RAJPUTS_CONTRACT_IDS, frozenset(EXPECTED_EVENTS))
        self.assertEqual(WAVE8_RAJPUTS_HOLDS, {})
        self.assertEqual(WAVE8_RAJPUTS_HOLD_IDS, frozenset())
        self.assertEqual(
            WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS,
            {"hced-Chitor1567-1"},
        )
        self.assertEqual(WAVE8_RAJPUTS_EXCLUSION_IDS, {"hced-Chitor1567-1"})
        self.assertIs(WAVE8_RAJPUTS_EXCLUSIONS, WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            WAVE8_RAJPUTS_RESERVED_IDS,
            WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(set(WAVE8_RAJPUTS_ROW_DISPOSITIONS), set(EXPECTED_RAW_ROWS))
        self.assertEqual(
            WAVE8_RAJPUTS_ROW_DISPOSITIONS["hced-Chitor1567-1"],
            "TERMINAL_EXCLUSION",
        )
        self.assertTrue(
            all(
                disposition == "PROMOTE"
                for candidate_id, disposition in WAVE8_RAJPUTS_ROW_DISPOSITIONS.items()
                if candidate_id != "hced-Chitor1567-1"
            )
        )
        self.assertEqual(
            wave8_rajputs_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "greedy_eligible_rows": 7,
                "hced_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 7,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 7,
                "new_entities": 9,
                "new_sources": 15,
                "newly_rated_events": 6,
                "outcome_overrides": 2,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 7,
                "sole_blocker_promotions": 3,
                "sole_blocker_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_rajputs_cohort_counts(),
            {
                "babur_eastern_campaign_1529": 1,
                "jaipur_maratha_fatehpur_1799": 1,
                "scindia_rajputana_campaign_1790": 2,
                "tarain_ghurid_chahamana_wars_1191_1192": 2,
            },
        )

    def test_authoritative_funnel_pins_seven_rows_and_four_sole_blockers(self) -> None:
        self.assertEqual(
            validate_wave8_rajputs_funnel(self.funnel),
            {
                "events_touched": 7,
                "greedy_eligible_rows": 7,
                "sole_blocker_promotions": 3,
                "sole_blocker_rows": 4,
            },
        )
        sole_ids = {
            candidate_id
            for candidate_id, item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.items()
            if item["sole_blocker_label"] == "rajputs"
        }
        self.assertEqual(
            sole_ids,
            {
                "hced-Chitor1567-1",
                "hced-Gogra1529-1",
                "hced-Merta1790-1",
                "hced-Patan1790-1",
            },
        )
        self.assertEqual(
            WAVE8_RAJPUTS_FUNNEL_SUMMARY["event_candidate_id_sha256"],
            "c39bff610c71388f144308649e960ed193ae0dfce339bdd678f8746be1e04264",
        )
        self.assertEqual(
            WAVE8_RAJPUTS_GREEDY_AUDIT["newly_unblocked_candidate_id_sha256"],
            "0f9809cbae3d23bea7a0afd8aa0f8011d1cd2dc5efb058f0c675243413a35cae",
        )
        for candidate_id, item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.items():
            self.assertTrue(item["full_row_audited"], candidate_id)
            self.assertTrue(item["greedy_eligible"], candidate_id)
            self.assertTrue(item["all_opposing_actors_resolved"], candidate_id)
            self.assertEqual(
                item["disposition"],
                WAVE8_RAJPUTS_ROW_DISPOSITIONS[candidate_id],
            )

        changed = copy.deepcopy(self.funnel)
        label = next(item for item in changed["labels"] if item["label"] == "rajputs")
        label["sole_blocker_events"] = 5
        with self.assertRaisesRegex(ValueError, "funnel summary changed"):
            validate_wave8_rajputs_funnel(changed)

    def test_complete_exact_queue_and_all_raw_hashes_fail_closed(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "rajputs"
            or normalize_label(row.get("side_2_raw")) == "rajputs"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_ROWS))
        self.assertEqual(set(self.lane_rows), WAVE8_RAJPUTS_RESERVED_IDS)
        self.assertEqual(
            validate_wave8_rajputs_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 6,
                "holds": 0,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )
        inventories = {
            **WAVE8_RAJPUTS_CONTRACTS,
            **WAVE8_RAJPUTS_NONPROMOTIONS,
        }
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            row = exact_rows[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                    row["winner_loser_complete"],
                    row["year_best"],
                ),
                expected,
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                inventories[candidate_id]["raw_row_sha256"],
            )

        for candidate_id in sorted(WAVE8_RAJPUTS_RESERVED_IDS):
            changed = copy.deepcopy(list(self.lane_rows.values()))
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "name"
            ] += " tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_rajputs_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Chitor1567-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_rajputs_queue_contracts(missing)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureRajputs1800-1",
                "side_1_raw": "Rajputs",
                "side_2_raw": "Unreviewed opponent",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Rajputs inventory changed"):
            validate_wave8_rajputs_queue_contracts(future)

    def test_sources_and_bounded_entities_parse_without_an_ethnic_bridge(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_RAJPUTS_SOURCES}
        self.assertEqual(len(source_by_id), 15)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_RAJPUTS_SOURCES}),
            15,
        )
        for source in WAVE8_RAJPUTS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_RAJPUTS_ENTITIES}
        self.assertEqual(
            set(entity_by_id),
            {
                GHAGHRA_MUGHAL,
                GHAGHRA_DEFENSE,
                FATEHPUR_EXPEDITION,
                FATEHPUR_JAIPUR,
                SCINDIA_CAMPAIGN,
                PATAN_COALITION,
                MERTA_MARWAR,
                CHAHAMANA_REGIME,
                GHURID_EASTERN_ARMY,
            },
        )
        for entity in WAVE8_RAJPUTS_ENTITIES:
            Entity.from_dict(entity)
            self.assertIn("bounded", entity["kind"])
            self.assertLessEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn(
                normalize_label(entity["name"]),
                {"rajput", "rajput army", "rajput kingdom", "rajput kingdoms", "rajputs"},
            )
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("generic rajput", note)
            self.assertIn("modern", note)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        self.assertEqual(
            (
                entity_by_id[CHAHAMANA_REGIME]["start_year"],
                entity_by_id[CHAHAMANA_REGIME]["end_year"],
            ),
            (1178, 1192),
        )
        self.assertEqual(
            (
                entity_by_id[GHURID_EASTERN_ARMY]["start_year"],
                entity_by_id[GHURID_EASTERN_ARMY]["end_year"],
            ),
            (1173, 1206),
        )
        self.assertEqual(
            (
                entity_by_id[SCINDIA_CAMPAIGN]["start_year"],
                entity_by_id[SCINDIA_CAMPAIGN]["end_year"],
            ),
            (1790, 1790),
        )

        entities, sources, _ = self._installed()
        install_wave8_rajputs_entities(entities)
        install_wave8_rajputs_sources(sources)
        self.assertTrue(set(entity_by_id) <= set(entities))
        self.assertTrue(set(source_by_id) <= set(sources))

    def test_contract_dates_actors_outcomes_and_families_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_RAJPUTS_SOURCES}
        events = self._events()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_EVENTS))
        self.assertEqual(len(events), 6)

        for candidate_id, expected in EXPECTED_EVENTS.items():
            contract = WAVE8_RAJPUTS_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                expected["date"],
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(canonical["granularity"], "engagement")
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertNotEqual(contract["result_type"], "draw")
            self.assertEqual(contract["actor_override"], "bounded_exact_opposing_forces")
            self.assertEqual(
                contract["source_outcome_override"], expected["override"]
            )
            self.assertEqual(contract["outcome_reversal"], expected["reversal"])
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
            self.assertTrue(
                set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"])
            )
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )

            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["canonical_event_key"], canonical["canonical_key"])
            self.assertEqual(event["date_precision"], canonical["date_precision"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertIn("hced_dataset", event["source_ids"])
            self.assertEqual(
                event["outcome_source_ids"], contract["outcome_source_ids"]
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
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
            self.assertEqual(winners, expected["winner"])
            self.assertEqual(losers, expected["loser"])

        participant_ids = {
            participant["entity_id"]
            for event in events
            for participant in event["participants"]
        }
        self.assertNotIn("rajputs", participant_ids)
        self.assertNotIn("rajput", participant_ids)
        self.assertNotIn("mughal_empire", participant_ids)
        self.assertNotIn("maratha_confederacy", participant_ids)

    def test_fatehpur_reversal_and_merta_unknown_placeholder_are_explicit(self) -> None:
        self.assertEqual(
            set(WAVE8_RAJPUTS_OUTCOME_OVERRIDES),
            {"hced-Fatehpur1799-1", "hced-Merta1790-1"},
        )
        fatehpur = WAVE8_RAJPUTS_OUTCOME_OVERRIDES["hced-Fatehpur1799-1"]
        self.assertEqual(
            (
                fatehpur["raw_winner_raw"],
                fatehpur["raw_loser_raw"],
                fatehpur["raw_winner_loser_complete"],
            ),
            ("Hariana", "Rajputs", True),
        )
        self.assertTrue(fatehpur["outcome_reversal"])
        self.assertEqual(fatehpur["override_kind"], "sourced_tactical_outcome_reversal")
        self.assertEqual(fatehpur["corrected_winner_entity_ids"], [FATEHPUR_JAIPUR])
        self.assertEqual(fatehpur["corrected_loser_entity_ids"], [FATEHPUR_EXPEDITION])

        merta = WAVE8_RAJPUTS_OUTCOME_OVERRIDES["hced-Merta1790-1"]
        self.assertEqual(
            (
                merta["raw_winner_raw"],
                merta["raw_loser_raw"],
                merta["raw_winner_loser_complete"],
            ),
            ("Draw", None, False),
        )
        self.assertFalse(merta["outcome_reversal"])
        self.assertIn("unknown_draw_placeholder", merta["override_kind"])
        self.assertEqual(merta["corrected_winner_entity_ids"], [SCINDIA_CAMPAIGN])
        self.assertEqual(merta["corrected_loser_entity_ids"], [MERTA_MARWAR])
        self.assertEqual(merta["corrected_result_type"], "win")

        for candidate_id, override in WAVE8_RAJPUTS_OUTCOME_OVERRIDES.items():
            contract = WAVE8_RAJPUTS_CONTRACTS[candidate_id]
            self.assertTrue(contract["source_outcome_override"])
            self.assertEqual(
                override["outcome_source_ids"], contract["outcome_source_ids"]
            )
            self.assertEqual(
                override["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

    def test_chitor_is_owned_terminally_without_a_rated_or_draw_assertion(self) -> None:
        self.assertEqual(set(WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS), {"hced-Chitor1567-1"})
        exclusion = WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS["hced-Chitor1567-1"]
        raw = self.lane_rows["hced-Chitor1567-1"]
        self.assertEqual((raw["year_low"], raw["year_high"]), (1567, 1567))
        self.assertEqual(
            (
                exclusion["canonical_event"]["year_low"],
                exclusion["canonical_event"]["year_high"],
                exclusion["canonical_event"]["date_text"],
            ),
            (1567, 1568, "October 1567-February 1568"),
        )
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertEqual(exclusion["exclusion_category"], "locked_interval_truncates_siege")
        self.assertEqual(exclusion["result_type"], "unknown")
        self.assertTrue(exclusion["unknown_is_never_draw"])
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            self.assertNotIn(forbidden, exclusion)
        reason = exclusion["exclusion_reason"].casefold()
        self.assertIn("1568", reason)
        self.assertIn("truncate", reason)
        self.assertIn("not promoted", reason)
        self.assertIn("never encoded as a draw", reason)
        self.assertNotIn("hced-Chitor1567-1", WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS)
        self.assertNotIn(
            "hced-Chitor1567-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_location_quarantines_are_promoted_only_and_do_not_mutate_globals(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(
            WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS,
            WAVE8_RAJPUTS_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_RAJPUTS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_RAJPUTS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_rajputs_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": WAVE8_RAJPUTS_CONTRACT_IDS,
            },
        )
        self.assertEqual(
            set(WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS),
            WAVE8_RAJPUTS_CONTRACT_IDS,
        )

        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "India")
            self.assertIn("location_provenance", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_duplicate_audit_is_zero_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_RAJPUTS_RESERVED_IDS,
        )
        self.assertEqual(
            validate_wave8_rajputs_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "hced_duplicate_dispositions": 0,
                "integration_dispositions": 7,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 7,
            },
        )

        hced_twin = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-ghaghra-1529",
                "name": "Battle of Ghaghra",
                "side_1_raw": "Future actor one",
                "side_2_raw": "Future actor two",
                "year_best": 1529,
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_rajputs_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-tarain",
                "name": "Second Battle of Tarain",
                "start_date": "1192-01-01",
                "end_date": "1192-12-31",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_rajputs_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {"id": "future-merta-twin", "name": "Battle of Merta", "year": 1790},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_rajputs_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_entity_window_event_duplicates_and_installer_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short[CHAHAMANA_REGIME]["end_year"] = 1190
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_rajputs_contracts(self.hced_rows, short, existing)

        events = promote_wave8_rajputs_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_rajputs_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_rajputs_contracts(
                self.hced_rows,
                entities,
                [*existing, {"name": "Battle of Patan", "year": 1790}],
            )

        installed_entities: dict[str, dict] = {}
        installed_sources: dict[str, dict] = {}
        install_wave8_rajputs_entities(installed_entities)
        install_wave8_rajputs_sources(installed_sources)
        installed_entities[CHAHAMANA_REGIME]["name"] = "tampered"
        installed_sources["wave8_rajputs_ignou_tarain"]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_rajputs_entities(installed_entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_rajputs_sources(installed_sources)


if __name__ == "__main__":
    unittest.main()
