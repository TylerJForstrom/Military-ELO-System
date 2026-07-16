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
from military_elo.promotion.wave8_manchus import (
    WAVE8_MANCHUS_CONTRACT_IDS,
    WAVE8_MANCHUS_CONTRACTS,
    WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS,
    WAVE8_MANCHUS_ENTITIES,
    WAVE8_MANCHUS_EXCLUSION_IDS,
    WAVE8_MANCHUS_EXCLUSIONS,
    WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS,
    WAVE8_MANCHUS_FINAL_AUDIT_SIGNATURE,
    WAVE8_MANCHUS_HOLD_IDS,
    WAVE8_MANCHUS_HOLDS,
    WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS,
    WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_MANCHUS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_MANCHUS_OUTCOME_OVERRIDES,
    WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MANCHUS_RESERVED_IDS,
    WAVE8_MANCHUS_SOURCES,
    install_wave8_manchus_entities,
    install_wave8_manchus_sources,
    promote_wave8_manchus_contracts,
    validate_wave8_manchus_integration_dispositions,
    validate_wave8_manchus_queue_contracts,
    wave8_manchus_audit_signature,
    wave8_manchus_cohort_counts,
    wave8_manchus_counts,
    wave8_manchus_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_manchus_"

JIN_ID = "nurhaci_hong_taiji_jin_state_1616_1636"
HONGGUANG_ID = "southern_ming_hongguang_regime_1644_1645"
MING_ID = "clio_cn_ming_dyn_1375_80721637"
JOSEON_ID = "joseon"
QING_ID = "clio_cn_qing_dyn_1_1645_8a50480c"


EXPECTED_RAW_LABELS = {
    "hced-Ningyuan1626-1": ("Ming", "Manchus", "Ming", "Manchus"),
    "hced-Niumaozhai1619-1": (
        "Manchus",
        "Ming, Korea",
        "Manchus",
        "Ming, Korea",
    ),
    "hced-Pyongyang1627-1": ("Manchus", "Korea", "Manchus", "Korea"),
    "hced-Shenyang1621-1": (
        "Manchus",
        "Ming China",
        "Manchus",
        "Ming China",
    ),
    "hced-Xiaoling1631-1": (
        "Manchus",
        "Ming China",
        "Manchus",
        "Ming China",
    ),
    "hced-Yangzhou1645-1": (
        "Manchus",
        "Ming China",
        "Manchus",
        "Ming China",
    ),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Niumaozhai1619-1": ({JIN_ID}, {MING_ID, JOSEON_ID}),
    "hced-Shenyang1621-1": ({JIN_ID}, {MING_ID}),
    "hced-Ningyuan1626-1": ({MING_ID}, {JIN_ID}),
    "hced-Xiaoling1631-1": ({JIN_ID}, {MING_ID}),
    "hced-Yangzhou1645-1": ({QING_ID}, {HONGGUANG_ID}),
}


EXPECTED_DATES = {
    "hced-Niumaozhai1619-1": (
        "day_range",
        "17-20 April 1619 (Korean and Manchu records differ)",
    ),
    "hced-Shenyang1621-1": (
        "day",
        "10th day of the third lunar month, 1621",
    ),
    "hced-Ningyuan1626-1": ("day_range", "2-10 February 1626"),
    "hced-Xiaoling1631-1": ("month", "early October 1631"),
    "hced-Yangzhou1645-1": (
        "day",
        "city fell 20 May 1645 after a one-week siege",
    ),
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


class Wave8ManchusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_MANCHUS_RESERVED_IDS
        ]

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_MANCHUS_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_manchus_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_MANCHUS_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_manchus_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_MANCHUS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_manchus_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_MANCHUS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_MANCHUS_ENTITIES,
            "expected_candidate_ids": sorted(
                WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_MANCHUS_HOLDS,
            "integration_dispositions": WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_MANCHUS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_MANCHUS_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_MANCHUS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_manchus_audit_signature(), independent_signature)
        self.assertEqual(
            WAVE8_MANCHUS_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(WAVE8_MANCHUS_HOLD_IDS, {"hced-Pyongyang1627-1"})
        self.assertIs(WAVE8_MANCHUS_EXCLUSIONS, WAVE8_MANCHUS_HOLDS)
        self.assertEqual(WAVE8_MANCHUS_EXCLUSION_IDS, WAVE8_MANCHUS_HOLD_IDS)
        self.assertEqual(
            WAVE8_MANCHUS_RESERVED_IDS,
            WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_manchus_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 2,
                "new_sources": 11,
                "newly_rated_events": 5,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_manchus_cohort_counts(),
            {
                "jin_ming_joseon_saerhu_campaign_1619": 1,
                "jin_ming_liaodong_war_1621_1631": 3,
                "qing_southern_ming_jiangnan_campaign_1645": 1,
            },
        )

    def test_all_and_only_six_exact_manchus_rows_are_owned(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Manchus"
            or row.get("side_2_raw") == "Manchus"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_LABELS))
        self.assertEqual(
            validate_wave8_manchus_queue_contracts(self.hced_rows),
            {"promotion_contracts": 5, "holds": 1, "reviewed_hced_rows": 6},
        )
        for candidate_id, row in exact_rows.items():
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                ),
                EXPECTED_RAW_LABELS[candidate_id],
            )
            disposition = (
                WAVE8_MANCHUS_CONTRACTS.get(candidate_id)
                or WAVE8_MANCHUS_HOLDS[candidate_id]
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                disposition["raw_row_sha256"],
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-FutureManchus1700-1",
                "side_1_raw": "Manchus",
                "side_2_raw": "Unreviewed opponent",
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Manchus inventory changed"):
            validate_wave8_manchus_queue_contracts(future)

    def test_each_hash_is_pinned_and_tampering_or_missing_rows_fail_closed(self) -> None:
        self.assertEqual(
            validate_wave8_manchus_queue_contracts(self.lane_rows),
            {"promotion_contracts": 5, "holds": 1, "reviewed_hced_rows": 6},
        )
        for candidate_id in sorted(WAVE8_MANCHUS_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.lane_rows)
                next(
                    row for row in changed if row["candidate_id"] == candidate_id
                )["name"] += " tampered"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_manchus_queue_contracts(changed)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Niumaozhai1619-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_manchus_queue_contracts(missing)

        duplicated = [*self.lane_rows, copy.deepcopy(self.lane_rows[0])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_manchus_queue_contracts(duplicated)

    def test_sources_and_bounded_regimes_parse_and_install_idempotently(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_MANCHUS_SOURCES}
        self.assertEqual(len(source_by_id), 11)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_MANCHUS_SOURCES}),
            11,
        )
        for source in WAVE8_MANCHUS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_MANCHUS_ENTITIES}
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entity_by_id.items()
            },
            {JIN_ID: (1616, 1636), HONGGUANG_ID: (1644, 1645)},
        )
        for entity in WAVE8_MANCHUS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertIn("modern state", entity["continuity_note"].casefold())
            self.assertNotIn(
                entity["name"].casefold(),
                {"jurchen", "manchu", "manchus", "eight banners"},
            )
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        install_wave8_manchus_entities(entities)
        install_wave8_manchus_sources(sources)
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])
            self.assertEqual(entities[entity_id], entity_by_id[entity_id])
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])
            self.assertEqual(sources[source_id], source_by_id[source_id])

        collision = copy.deepcopy(entities)
        collision[JIN_ID] = {**collision[JIN_ID], "end_year": 1700}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_manchus_entities(collision)

    def test_pyongyang_is_terminal_noncompetitive_hold_and_never_a_draw(self) -> None:
        hold = WAVE8_MANCHUS_HOLDS["hced-Pyongyang1627-1"]
        self.assertEqual(
            hold["hold_category"],
            "noncompetitive_occupation_without_battle",
        )
        self.assertEqual(
            hold["canonical_event"],
            {
                "canonical_key": "occupation_of_pyongyang:1627:1627",
                "date_precision": "year",
                "date_text": "early 1627 (occupied without a fight)",
                "granularity": "noncompetitive_occupation",
                "name": "Occupation of Pyongyang",
                "year_low": 1627,
                "year_high": 1627,
            },
        )
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        self.assertTrue(forbidden.isdisjoint(hold))
        reason = hold["hold_reason"].casefold()
        self.assertIn("without a fight", reason)
        self.assertIn("cannot produce an elo result", reason)
        self.assertIn("not converted into a battlefield opponent", reason)
        self.assertIn("never made a draw", reason)
        self.assertEqual(
            set(hold["evidence_refs"]),
            {
                "wave8_manchus_kci_first_invasion_1627",
                "wave8_manchus_swope_military_collapse",
            },
        )

    def test_dates_sides_and_independent_outcome_families_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_MANCHUS_SOURCES}
        for candidate_id, contract in WAVE8_MANCHUS_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                EXPECTED_DATES[candidate_id],
            )
            expected_winners, expected_losers = EXPECTED_WINNERS_AND_LOSERS[
                candidate_id
            ]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["war_type"], "interstate_limited")
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

            outcome_ids = list(contract["outcome_source_ids"])
            self.assertGreaterEqual(len(outcome_ids), 2)
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
            self.assertTrue(set(outcome_ids) <= set(contract["evidence_refs"]))
            expected_families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcome_ids}
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                expected_families,
            )
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        self.assertEqual(WAVE8_MANCHUS_OUTCOME_OVERRIDES, {})

    def test_emission_is_five_parseable_tactical_wins_with_no_ethnic_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 5)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertNotIn("hced-Pyongyang1627-1", by_candidate)

        forbidden_participant_ids = {
            "jurchen",
            "manchu",
            "manchus",
            "clio_q1062546_1619_e59e2589",
        }
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                event["date_precision"],
                WAVE8_MANCHUS_CONTRACTS[candidate_id]["canonical_event"][
                    "date_precision"
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
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            self.assertTrue((winners | losers).isdisjoint(forbidden_participant_ids))
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            contract = WAVE8_MANCHUS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )

    def test_yangzhou_corrects_the_bad_actor_code_without_reversing_outcome(self) -> None:
        raw = next(
            row
            for row in self.lane_rows
            if row["candidate_id"] == "hced-Yangzhou1645-1"
        )
        self.assertEqual(raw["seshat_side_2_candidates"], ["cn_qing_dyn_1"])
        self.assertEqual(raw["massacre_raw"], "Battle followed by massacre")
        contract = WAVE8_MANCHUS_CONTRACTS["hced-Yangzhou1645-1"]
        self.assertEqual(contract["side_1_entity_ids"], [QING_ID])
        self.assertEqual(contract["side_2_entity_ids"], [HONGGUANG_ID])
        self.assertEqual(contract["winner_side"], 1)
        self.assertFalse(contract["source_outcome_override"])

        _, _, events = self._emit()
        event = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Yangzhou1645-1"
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
        self.assertEqual((winners, losers), ({QING_ID}, {HONGGUANG_ID}))
        self.assertIn("subsequent massacre", event["summary"])

    def test_entity_windows_and_existing_candidate_duplicates_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        too_short = copy.deepcopy(entities)
        too_short[JIN_ID]["end_year"] = 1620
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_manchus_contracts(
                self.hced_rows,
                too_short,
                existing,
            )

        events = promote_wave8_manchus_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_manchus_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_location_audit_quarantines_three_points_and_retains_two(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}

        expected_points = {
            "hced-Ningyuan1626-1",
            "hced-Niumaozhai1619-1",
            "hced-Xiaoling1631-1",
        }
        self.assertEqual(WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_MANCHUS_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": frozenset()},
        )
        self.assertEqual(
            wave8_manchus_location_quarantine_additions(),
            {"point": expected_points, "country": frozenset()},
        )
        for candidate_id in expected_points:
            self.assertNotIn("geometry", by_candidate[candidate_id])
            self.assertEqual(by_candidate[candidate_id]["modern_location_country"], "China")
            self.assertIn("location_provenance", by_candidate[candidate_id])

        self.assertEqual(
            by_candidate["hced-Shenyang1621-1"]["geometry"],
            {"type": "Point", "coordinates": [123.431472, 41.805699]},
        )
        self.assertEqual(
            by_candidate["hced-Yangzhou1645-1"]["geometry"],
            {"type": "Point", "coordinates": [119.412939, 32.394209]},
        )
        for candidate_id in ("hced-Shenyang1621-1", "hced-Yangzhou1645-1"):
            self.assertEqual(by_candidate[candidate_id]["modern_location_country"], "China")
            self.assertIn("location_provenance", by_candidate[candidate_id])

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_iwbd_and_cross_lane_zero_overlap_audits_fail_closed(self) -> None:
        self.assertEqual(WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_manchus_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )

        # Existing IWBD Pyongyang rows are 1894 and 1950, so name alone cannot
        # create a duplicate. A same-name/same-year future row must stop release.
        future_iwbd = copy.deepcopy(self.iwbd_rows)
        future_iwbd.append(
            {
                "candidate_id": "iwbd-future-xiaolinghe",
                "name": "Battle of Xiaolinghe",
                "start_date": "1631-10-01",
                "end_date": "1631-10-02",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_manchus_integration_dispositions(
                self.hced_rows,
                future_iwbd,
            )


if __name__ == "__main__":
    unittest.main()
