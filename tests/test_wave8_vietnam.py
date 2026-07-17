import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_vietnam import (
    WAVE8_VIETNAM_CONTRACT_IDS,
    WAVE8_VIETNAM_CONTRACTS,
    WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_VIETNAM_ENTITIES,
    WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS,
    WAVE8_VIETNAM_FINAL_AUDIT_SIGNATURE,
    WAVE8_VIETNAM_FUNNEL_SUMMARY,
    WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_HOLD_IDS,
    WAVE8_VIETNAM_HOLDS,
    WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS,
    WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_VIETNAM_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS,
    WAVE8_VIETNAM_NONPROMOTIONS,
    WAVE8_VIETNAM_OUTCOME_OVERRIDES,
    WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS,
    WAVE8_VIETNAM_RESERVED_IDS,
    WAVE8_VIETNAM_SOURCES,
    WAVE8_VIETNAM_TERMINAL_EXCLUSIONS,
    WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
    install_wave8_vietnam_entities,
    install_wave8_vietnam_sources,
    promote_wave8_vietnam_contracts,
    validate_wave8_vietnam_funnel,
    validate_wave8_vietnam_integration_dispositions,
    validate_wave8_vietnam_queue_contracts,
    wave8_vietnam_audit_signature,
    wave8_vietnam_cohort_counts,
    wave8_vietnam_counts,
    wave8_vietnam_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_vietnam_"

TRAN_DONG_BO_DAU = "tran_dai_viet_dong_bo_dau_force_1258"
MONGOL_1258 = "uriyangkhadai_mongol_invasion_column_1258"
TRAN_BACH_DANG = "tran_dai_viet_bach_dang_force_1288"
YUAN_BACH_DANG = "omar_yuan_bach_dang_fleet_1288"
LAM_SON = "lam_son_northern_campaign_forces_1426_1427"
MING_TOT_DONG = "wang_tong_ming_tot_dong_force_1426"
MING_DONG_QUAN = "wang_tong_ming_dong_quan_garrison_1426_1427"
MING_CHI_LANG = "liu_sheng_ming_relief_column_chi_lang_1427"
TAY_SON = "quang_trung_tay_son_thang_long_force_1789"
QING_1789 = "sun_shiyi_qing_thang_long_invasion_force_1789"
DAI_VIET_VIJAYA = "le_thanh_tong_dai_viet_vijaya_force_1471"
CHAMPA_VIJAYA = "tra_toan_vijaya_champa_defenders_1471"


EXPECTED_PARTICIPANTS = {
    "hced-Thang Long1258-1": ({TRAN_DONG_BO_DAU}, {MONGOL_1258}),
    "hced-Bach Dang1288-1": ({TRAN_BACH_DANG}, {YUAN_BACH_DANG}),
    "hced-Tot-dong1426-1": ({LAM_SON}, {MING_TOT_DONG}),
    "hced-Dong-do1426-1427-1": ({LAM_SON}, {MING_DONG_QUAN}),
    "hced-Chi Lang Pass1427-1": ({LAM_SON}, {MING_CHI_LANG}),
    "hced-Vijaya1471-1": ({DAI_VIET_VIJAYA}, {CHAMPA_VIJAYA}),
    "hced-Thang Long1789-1": ({TAY_SON}, {QING_1789}),
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


class Wave8VietnamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        entity_ids = {str(entity["id"]) for entity in WAVE8_VIETNAM_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in entity_ids
        }
        install_wave8_vietnam_entities(entities)

        source_ids = {str(source["id"]) for source in WAVE8_VIETNAM_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        install_wave8_vietnam_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_VIETNAM_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_vietnam_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        payload = {
            "contracts": WAVE8_VIETNAM_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_VIETNAM_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS),
            "funnel_summary": WAVE8_VIETNAM_FUNNEL_SUMMARY,
            "hced_duplicate_dispositions": WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS,
            "holds": WAVE8_VIETNAM_HOLDS,
            "integration_dispositions": WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_VIETNAM_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_VIETNAM_SOURCES,
            "terminal_exclusions": WAVE8_VIETNAM_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_VIETNAM_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_vietnam_audit_signature(), independent)
        self.assertEqual(
            wave8_vietnam_counts(),
            {
                "country_quarantine_additions": 0,
                "greedy_eligible_rows": 6,
                "hced_duplicate_dispositions": 1,
                "holds": 1,
                "integration_dispositions": 9,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 12,
                "new_sources": 21,
                "newly_rated_events": 7,
                "outcome_overrides": 0,
                "point_quarantine_additions": 7,
                "promotion_contracts": 7,
                "reviewed_hced_rows": 9,
                "sole_blocker_promotions": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_vietnam_cohort_counts(),
            {
                "dai_viet_champa_war": 1,
                "lam_son_uprising": 3,
                "tay_son_qing_war": 1,
                "tran_mongol_wars": 2,
            },
        )

    def test_authoritative_funnel_is_the_exact_owned_cohort(self) -> None:
        self.assertEqual(
            validate_wave8_vietnam_funnel(self.funnel),
            {
                "events_touched": 9,
                "greedy_eligible_rows": 6,
                "sole_blocker_rows": 4,
            },
        )
        scoped = {
            str(row["candidate_id"]): row
            for row in self.funnel["row_label_data"]
            if "vietnam" in row.get("blocker_labels", [])
        }
        self.assertEqual(set(scoped), WAVE8_VIETNAM_RESERVED_IDS)
        self.assertEqual(len(scoped), 9)
        self.assertEqual(
            {
                candidate_id
                for candidate_id, row in scoped.items()
                if row.get("sole_blocker_label") == "vietnam"
            },
            {
                "hced-Chi Lang Pass1427-1",
                "hced-Dong-do1426-1427-1",
                "hced-Thang Long1789-1",
                "hced-Tot-dong1426-1",
            },
        )
        for candidate_id, row in scoped.items():
            disposition = WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS[candidate_id]
            self.assertTrue(disposition["full_row_audited"])
            self.assertEqual(disposition["blocker_labels"], row["blocker_labels"])
            self.assertEqual(disposition["greedy_eligible"], row["greedy_eligible"])
            self.assertEqual(
                disposition["sole_blocker_label"], row["sole_blocker_label"]
            )
            self.assertEqual(disposition["other_blockers"], row["other_blockers"])

        exact_raw_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if row.get("side_1_raw") == "Vietnam"
            or row.get("side_2_raw") == "Vietnam"
        }
        self.assertEqual(exact_raw_ids & WAVE8_VIETNAM_RESERVED_IDS, set(scoped))
        self.assertTrue(exact_raw_ids - WAVE8_VIETNAM_RESERVED_IDS)

        changed = copy.deepcopy(self.funnel)
        changed["row_label_data"].append(
            {
                "candidate_id": "hced-FutureVietnam1790-1",
                "blocker_labels": ["vietnam"],
            }
        )
        with self.assertRaisesRegex(ValueError, "exact funnel cohort changed"):
            validate_wave8_vietnam_funnel(changed)

        changed = copy.deepcopy(self.funnel)
        next(item for item in changed["labels"] if item["label"] == "vietnam")[
            "events_touched"
        ] = 10
        with self.assertRaisesRegex(ValueError, "funnel summary changed"):
            validate_wave8_vietnam_funnel(changed)

    def test_every_disposition_and_raw_hash_is_fail_closed(self) -> None:
        self.assertEqual(
            WAVE8_VIETNAM_RESERVED_IDS,
            WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            (len(WAVE8_VIETNAM_CONTRACT_IDS), len(WAVE8_VIETNAM_HOLD_IDS),
             len(WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS)),
            (7, 1, 1),
        )
        dispositions = (
            WAVE8_VIETNAM_CONTRACT_IDS,
            WAVE8_VIETNAM_HOLD_IDS,
            WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
        )
        for index, left in enumerate(dispositions):
            for right in dispositions[index + 1 :]:
                self.assertFalse(left & right)

        indexed = {str(row["candidate_id"]): row for row in self.hced_rows}
        inventory = {
            **WAVE8_VIETNAM_CONTRACTS,
            **WAVE8_VIETNAM_NONPROMOTIONS,
        }
        self.assertEqual(set(inventory), WAVE8_VIETNAM_RESERVED_IDS)
        for candidate_id, item in inventory.items():
            self.assertEqual(
                canonical_hced_row_sha256(indexed[candidate_id]),
                item["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_vietnam_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 7,
                "holds": 1,
                "reviewed_hced_rows": 9,
                "terminal_exclusions": 1,
            },
        )

        for candidate_id in sorted(WAVE8_VIETNAM_RESERVED_IDS):
            changed = copy.deepcopy(self.hced_rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "winner_raw"
            ] = "tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_vietnam_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Bach Dang1288-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_vietnam_queue_contracts(missing)

    def test_sources_and_bounded_actors_parse_and_install(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_VIETNAM_SOURCES}
        self.assertEqual(len(source_by_id), 21)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_VIETNAM_SOURCES}),
            21,
        )
        for source in WAVE8_VIETNAM_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"], sorted(set(source["evidence_roles"]))
            )

        expected_ids = {
            TRAN_DONG_BO_DAU,
            MONGOL_1258,
            TRAN_BACH_DANG,
            YUAN_BACH_DANG,
            LAM_SON,
            MING_TOT_DONG,
            MING_DONG_QUAN,
            MING_CHI_LANG,
            TAY_SON,
            QING_1789,
            DAI_VIET_VIJAYA,
            CHAMPA_VIJAYA,
        }
        self.assertEqual({entity["id"] for entity in WAVE8_VIETNAM_ENTITIES}, expected_ids)
        for entity in WAVE8_VIETNAM_ENTITIES:
            Entity.from_dict(entity)
            self.assertLessEqual(entity["end_year"] - entity["start_year"], 1)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern socialist republic of vietnam", note)
            self.assertIn("prc", note)
            self.assertIn("predecessor or successor", note)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        new_ids = {entity["id"] for entity in WAVE8_VIETNAM_ENTITIES}
        used_ids = {
            entity_id
            for contract in WAVE8_VIETNAM_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
        }
        self.assertEqual(used_ids, new_ids)

        entities, sources, _ = self._installed()
        original_entities = copy.deepcopy(entities)
        original_sources = copy.deepcopy(sources)
        install_wave8_vietnam_entities(entities)
        install_wave8_vietnam_sources(sources)
        self.assertEqual(entities, original_entities)
        self.assertEqual(sources, original_sources)

        bad_entities = copy.deepcopy(entities)
        bad_entities[TRAN_DONG_BO_DAU]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_vietnam_entities(bad_entities)
        bad_sources = copy.deepcopy(sources)
        source_id = next(iter(source_by_id))
        bad_sources[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_vietnam_sources(bad_sources)

    def test_dates_sides_outcomes_and_source_families_are_exact(self) -> None:
        expected = {
            "hced-Thang Long1258-1": (
                "Battle of Đông Bộ Đầu",
                1258,
                1258,
                "day_range",
                "Night of 28-29 January 1258",
                "engagement",
            ),
            "hced-Bach Dang1288-1": (
                "Battle of Bạch Đằng",
                1288,
                1288,
                "day",
                "9 April 1288",
                "engagement",
            ),
            "hced-Tot-dong1426-1": (
                "Battle of Tốt Động-Chúc Động",
                1426,
                1426,
                "day_range",
                "5-7 November 1426",
                "engagement",
            ),
            "hced-Dong-do1426-1427-1": (
                "Siege and evacuation of Đông Quan",
                1426,
                1427,
                "day_range",
                "22 November 1426-29 December 1427",
                "siege",
            ),
            "hced-Chi Lang Pass1427-1": (
                "Battle of Chi Lăng Pass",
                1427,
                1427,
                "day",
                "10 October 1427",
                "engagement",
            ),
            "hced-Vijaya1471-1": (
                "Capture of Vijaya",
                1471,
                1471,
                "day_range",
                "18-22 March 1471",
                "siege",
            ),
            "hced-Thang Long1789-1": (
                "Ngọc Hồi-Đống Đa offensive at Thăng Long",
                1789,
                1789,
                "day",
                "30 January 1789",
                "engagement",
            ),
        }
        source_by_id = {source["id"]: source for source in WAVE8_VIETNAM_SOURCES}
        self.assertEqual(set(WAVE8_VIETNAM_CONTRACTS), set(expected))
        for candidate_id, contract in WAVE8_VIETNAM_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["year_low"],
                    canonical["year_high"],
                    canonical["date_precision"],
                    canonical["date_text"],
                    canonical["granularity"],
                ),
                expected[candidate_id],
            )
            winners, losers = EXPECTED_PARTICIPANTS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual((contract["result_type"], contract["winner_side"]), ("win", 1))
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertLessEqual(
                set(contract["outcome_source_ids"]), set(contract["evidence_refs"])
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
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["duplicate_ownership"],
                {"owner_module": "wave8_vietnam", "status": "canonical_hced_owner"},
            )
        self.assertFalse(WAVE8_VIETNAM_OUTCOME_OVERRIDES)

    def test_siming_is_unknown_and_never_becomes_a_draw(self) -> None:
        self.assertEqual(WAVE8_VIETNAM_HOLD_IDS, {"hced-Siming1285-1"})
        hold = WAVE8_VIETNAM_HOLDS["hced-Siming1285-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertFalse(hold["terminal_exclusion"])
        self.assertEqual(
            hold["hold_category"],
            "actor_and_terminal_tactical_outcome_unresolved",
        )
        self.assertEqual((hold["reviewed_outcome"], hold["result_type"]), ("unknown", "unknown"))
        self.assertTrue(hold["unknown_is_never_draw"])
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
        ):
            self.assertNotIn(forbidden, hold)
        reason = hold["hold_reason"].casefold()
        self.assertIn("not promoted", reason)
        self.assertIn("reversed", reason)
        self.assertIn("draw", reason)
        self.assertIn("unknown remains unknown", reason)

    def test_hanoi_is_a_terminal_duplicate_not_a_modern_identity_bridge(self) -> None:
        self.assertEqual(
            WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
            {"hced-Hanoi1789-1"},
        )
        exclusion = WAVE8_VIETNAM_TERMINAL_EXCLUSIONS["hced-Hanoi1789-1"]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertTrue(exclusion["terminal_exclusion"])
        self.assertEqual(
            exclusion["duplicate_of_hced_candidate_id"],
            "hced-Thang Long1789-1",
        )
        self.assertIn("Hanoi was introduced in 1831", exclusion["hold_reason"])
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "result_type",
        ):
            self.assertNotIn(forbidden, exclusion)

        self.assertEqual(
            set(WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS),
            {"hced-Hanoi1789-1"},
        )
        duplicate = WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS[
            "hced-Hanoi1789-1"
        ]
        self.assertEqual(duplicate["canonical_owner"], "hced-Thang Long1789-1")
        self.assertEqual(duplicate["disposition"], "terminal_duplicate_exclusion")
        self.assertEqual(
            duplicate["relationship"],
            "same_ngoc_hoi_dong_da_qing_defeat_episode",
        )

    def test_all_four_sole_blockers_are_promoted(self) -> None:
        sole = {
            candidate_id
            for candidate_id, item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.items()
            if item["sole_blocker_label"] == "vietnam"
        }
        self.assertEqual(len(sole), 4)
        self.assertLessEqual(sole, WAVE8_VIETNAM_CONTRACT_IDS)
        for candidate_id, item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.items():
            expected = (
                "PROMOTE"
                if candidate_id in WAVE8_VIETNAM_CONTRACT_IDS
                else "HOLD"
                if candidate_id in WAVE8_VIETNAM_HOLD_IDS
                else "EXCLUDE"
            )
            self.assertEqual(item["disposition"], expected)
            if expected == "PROMOTE":
                self.assertTrue(item["all_opposing_actors_resolved"])
        self.assertEqual(
            WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS["hced-Siming1285-1"][
                "disposition"
            ],
            "HOLD",
        )
        self.assertEqual(
            WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS["hced-Hanoi1789-1"][
                "disposition"
            ],
            "EXCLUDE",
        )

    def test_emission_is_seven_exact_wins_without_generic_or_modern_actors(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 7)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_VIETNAM_CONTRACT_IDS)
        self.assertTrue(
            WAVE8_VIETNAM_HOLD_IDS.isdisjoint(by_candidate)
            and WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS.isdisjoint(by_candidate)
        )
        forbidden_ids = {
            "vietnam",
            "vietnamese",
            "champa",
            "china",
            "qing",
            "mongols",
            "clio_vt_vietnam_socialist_rep_1976_7f7549c0",
            "clio_cn_ming_dyn_1375_80721637",
            "clio_cn_qing_dyn_1_1645_8a50480c",
        }
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                event["canonical_event_key"],
                WAVE8_VIETNAM_CONTRACTS[candidate_id]["canonical_event"][
                    "canonical_key"
                ],
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
            self.assertEqual((winners, losers), EXPECTED_PARTICIPANTS[candidate_id])
            self.assertTrue((winners | losers).isdisjoint(forbidden_ids))
            self.assertNotIn(
                "inconclusive_engagement",
                {participant["termination"] for participant in event["participants"]},
            )
            self.assertEqual(
                event["outcome_source_ids"],
                WAVE8_VIETNAM_CONTRACTS[candidate_id]["outcome_source_ids"],
            )

        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            [
                "hced-Thang Long1258-1",
                "hced-Bach Dang1288-1",
                "hced-Dong-do1426-1427-1",
                "hced-Tot-dong1426-1",
                "hced-Chi Lang Pass1427-1",
                "hced-Vijaya1471-1",
                "hced-Thang Long1789-1",
            ],
        )

    def test_promoted_only_point_quarantines_are_local(self) -> None:
        global_points_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        global_countries_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            WAVE8_VIETNAM_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_VIETNAM_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_vietnam_location_quarantine_additions(),
            {
                "point": WAVE8_VIETNAM_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            set(WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS),
            WAVE8_VIETNAM_CONTRACT_IDS,
        )
        self.assertTrue(
            WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS
            <= WAVE8_VIETNAM_CONTRACT_IDS
        )
        self.assertFalse(WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS)

        _, _, events = self._emit()
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Vietnam")
            self.assertIn("location_provenance", event)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), global_points_before)
        self.assertEqual(
            frozenset(HCED_COUNTRY_QUARANTINE_IDS), global_countries_before
        )

    def test_duplicate_and_negative_cross_source_scans_are_pinned(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_vietnam_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "hced_duplicate_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 9,
                "existing_release_duplicate_dispositions": 0,
            },
        )
        self.assertFalse(WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)
        self.assertEqual(
            set(WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_VIETNAM_RESERVED_IDS,
        )

        hced = copy.deepcopy(self.hced_rows)
        hced.append(
            {
                "candidate_id": "hced-UnreviewedBachDang1288-2",
                "name": "Bạch Đằng",
                "year_low": 1288,
                "year_high": 1288,
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed cross-lane HCED twin"):
            validate_wave8_vietnam_integration_dispositions(
                hced,
                self.iwbd_rows,
                existing,
            )

        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-synthetic-vijaya",
                "name": "Battle of Vijaya",
                "start_date": "1471-03-18",
                "end_date": "1471-03-22",
            }
        )
        with self.assertRaisesRegex(ValueError, "plausible IWBD overlap"):
            validate_wave8_vietnam_integration_dispositions(
                self.hced_rows,
                iwbd,
                existing,
            )

        release = [
            *existing,
            {
                "id": "synthetic_chi_lang_duplicate",
                "name": "Battle of Chi Lang Pass",
                "year": 1427,
                "end_year": 1427,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing release duplicate"):
            validate_wave8_vietnam_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release,
            )

    def test_existing_candidate_or_event_collision_fails_closed(self) -> None:
        entities, _, existing = self._installed()
        promoted = promote_wave8_vietnam_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_vietnam_contracts(
                self.hced_rows,
                entities,
                [*existing, promoted[0]],
            )
        collision = [
            *existing,
            {
                "id": "synthetic_bach_dang_collision",
                "name": "Battle of Bạch Đằng",
                "year": 1288,
            },
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_vietnam_contracts(
                self.hced_rows,
                entities,
                collision,
            )


if __name__ == "__main__":
    unittest.main()
