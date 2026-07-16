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
from military_elo.promotion.wave8_dagestan import (
    WAVE8_DAGESTAN_CONTRACT_IDS,
    WAVE8_DAGESTAN_CONTRACTS,
    WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS,
    WAVE8_DAGESTAN_ENTITIES,
    WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS,
    WAVE8_DAGESTAN_FINAL_AUDIT_SIGNATURE,
    WAVE8_DAGESTAN_HOLD_IDS,
    WAVE8_DAGESTAN_HOLDS,
    WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS,
    WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_DAGESTAN_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_DAGESTAN_OUTCOME_OVERRIDES,
    WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_DAGESTAN_RESERVED_IDS,
    WAVE8_DAGESTAN_SOURCES,
    install_wave8_dagestan_entities,
    install_wave8_dagestan_sources,
    promote_wave8_dagestan_contracts,
    validate_wave8_dagestan_integration_dispositions,
    validate_wave8_dagestan_queue_contracts,
    wave8_dagestan_audit_signature,
    wave8_dagestan_cohort_counts,
    wave8_dagestan_counts,
    wave8_dagestan_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_dagestan_"
GHAZI_IMAMATE_ID = "dagestani_imamate_ghazi_muhammad_1829_1832"
SHAMIL_IMAMATE_ID = "caucasian_imamate_shamil_1834_1859"


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


EXPECTED_RAW_LABELS = {
    "hced-Aghdash Awkh1831-1": ("Dagestan", "Russia", "Dagestan", "Russia"),
    "hced-Akhulgo1839-1": ("Russia", "Dagestan", "Russia", "Dagestan"),
    "hced-Burtinah1839-1": ("Russia", "Dagestan", "Russia", "Dagestan"),
    "hced-Girgil1847-1": ("Russia", "Dagestan", "Russia", "Dagestan"),
    "hced-Saltah1847-1": ("Russia", "Dagestan", "Russia", "Dagestan"),
    "hced-Zakataly1853-1": ("Russia", "Dagestan", "Russia", "Dagestan"),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Aghdash Awkh1831-1": ({GHAZI_IMAMATE_ID}, {"russian_empire"}),
    "hced-Akhulgo1839-1": ({"russian_empire"}, {SHAMIL_IMAMATE_ID}),
    "hced-Burtinah1839-1": ({"russian_empire"}, {SHAMIL_IMAMATE_ID}),
    "hced-Girgil1847-1": ({SHAMIL_IMAMATE_ID}, {"russian_empire"}),
    "hced-Saltah1847-1": ({"russian_empire"}, {SHAMIL_IMAMATE_ID}),
    "hced-Zakataly1853-1": ({"russian_empire"}, {SHAMIL_IMAMATE_ID}),
}


EXPECTED_DATES = {
    "hced-Aghdash Awkh1831-1": ("day", "13 July 1831"),
    "hced-Akhulgo1839-1": ("day_range", "24 June-11 September 1839"),
    "hced-Burtinah1839-1": ("day", "5 June 1839"),
    "hced-Girgil1847-1": ("day_range", "13-20 June 1847"),
    "hced-Saltah1847-1": ("day_range", "6 August-27 September 1847"),
    "hced-Zakataly1853-1": (
        "day",
        "25 August 1853 Old Style (6 September New Style)",
    ),
}


class Wave8DagestanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_DAGESTAN_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_dagestan_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_DAGESTAN_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_dagestan_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_DAGESTAN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_dagestan_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_DAGESTAN_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_DAGESTAN_ENTITIES,
            "expected_candidate_ids": sorted(WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS),
            "holds": WAVE8_DAGESTAN_HOLDS,
            "integration_dispositions": WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_DAGESTAN_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_DAGESTAN_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_DAGESTAN_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_dagestan_audit_signature(), independent_signature)
        self.assertEqual(WAVE8_DAGESTAN_CONTRACT_IDS, set(EXPECTED_RAW_LABELS))
        self.assertEqual(WAVE8_DAGESTAN_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_DAGESTAN_RESERVED_IDS, WAVE8_DAGESTAN_CONTRACT_IDS)
        self.assertEqual(
            wave8_dagestan_counts(),
            {
                "country_quarantine_additions": 2,
                "cross_lane_hced_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 2,
                "new_sources": 8,
                "newly_rated_events": 6,
                "outcome_overrides": 1,
                "point_quarantine_additions": 4,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_dagestan_cohort_counts(),
            {
                "ghazi_muhammad_northern_dagestan_campaign_1831": 1,
                "grabbe_northern_dagestan_campaign_1839": 2,
                "shamil_zaqatala_campaign_1853": 1,
                "vorontsov_dagestan_campaign_1847": 2,
            },
        )

    def test_all_and_only_six_exact_dagestan_labels_are_pinned_fail_closed(self) -> None:
        exact_label_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Dagestan"
            or row.get("side_2_raw") == "Dagestan"
        }
        self.assertEqual(set(exact_label_rows), set(EXPECTED_RAW_LABELS))
        for candidate_id, row in exact_label_rows.items():
            expected = EXPECTED_RAW_LABELS[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                ),
                expected,
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                WAVE8_DAGESTAN_CONTRACTS[candidate_id]["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_dagestan_queue_contracts(self.hced_rows),
            {"promotion_contracts": 6, "holds": 0, "reviewed_hced_rows": 6},
        )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Girgil1847-1"
        )["winner_raw"] = "Dagestan"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_dagestan_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Akhulgo1839-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_dagestan_queue_contracts(missing)

    def test_sources_and_regime_bounded_entities_parse_and_install(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_DAGESTAN_SOURCES}
        self.assertEqual(len(source_by_id), 8)
        for source in WAVE8_DAGESTAN_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_DAGESTAN_ENTITIES}
        self.assertEqual(
            {entity_id: (entity["start_year"], entity["end_year"])
             for entity_id, entity in entity_by_id.items()},
            {
                GHAZI_IMAMATE_ID: (1829, 1832),
                SHAMIL_IMAMATE_ID: (1834, 1859),
            },
        )
        for entity in WAVE8_DAGESTAN_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotEqual(entity["name"].casefold(), "dagestan")
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])

    def test_dates_sides_and_single_outcome_reversal_are_explicit(self) -> None:
        self.assertEqual(set(WAVE8_DAGESTAN_OUTCOME_OVERRIDES), {"hced-Girgil1847-1"})
        for candidate_id, contract in WAVE8_DAGESTAN_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                EXPECTED_DATES[candidate_id],
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertNotEqual(contract["result_type"], "draw")
            self.assertTrue(contract["actor_override"])
            self.assertEqual(
                contract["source_outcome_override"],
                candidate_id == "hced-Girgil1847-1",
            )
            self.assertEqual(
                contract["outcome_reversal"],
                candidate_id == "hced-Girgil1847-1",
            )
        self.assertEqual(WAVE8_DAGESTAN_HOLDS, {})

    def test_outcome_sources_and_family_independence_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_DAGESTAN_SOURCES}
        for candidate_id, contract in WAVE8_DAGESTAN_CONTRACTS.items():
            outcome_ids = list(contract["outcome_source_ids"])
            self.assertTrue(outcome_ids, candidate_id)
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
            self.assertTrue(set(outcome_ids) <= set(contract["evidence_refs"]))
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted({source_by_id[item]["source_family_id"] for item in outcome_ids}),
            )
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
        self.assertEqual(
            len(WAVE8_DAGESTAN_CONTRACTS["hced-Aghdash Awkh1831-1"][
                "outcome_source_family_ids"
            ]),
            1,
        )
        self.assertGreaterEqual(
            len(WAVE8_DAGESTAN_CONTRACTS["hced-Girgil1847-1"][
                "outcome_source_family_ids"
            ]),
            2,
        )

    def test_emission_is_parseable_tactical_and_never_invents_a_draw(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 6)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["event_type"], "engagement")
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
            self.assertFalse(
                any("draw" in participant["termination"] for participant in event["participants"])
            )
            self.assertNotIn("dagestan", winners | losers)
            self.assertNotIn("clio_q2088141_1828_1df83370", winners | losers)
            contract = WAVE8_DAGESTAN_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

        entities, _, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_dagestan_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_location_audit_is_declared_applied_and_non_mutating(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}

        expected_points = {
            "hced-Aghdash Awkh1831-1",
            "hced-Akhulgo1839-1",
            "hced-Burtinah1839-1",
            "hced-Girgil1847-1",
        }
        expected_countries = {
            "hced-Aghdash Awkh1831-1",
            "hced-Burtinah1839-1",
        }
        self.assertEqual(WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS, expected_countries)
        self.assertEqual(
            WAVE8_DAGESTAN_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": expected_countries},
        )
        self.assertEqual(
            wave8_dagestan_location_quarantine_additions(),
            {"point": expected_points, "country": expected_countries},
        )
        for candidate_id in expected_points:
            self.assertNotIn("geometry", by_candidate[candidate_id])
        for candidate_id in expected_countries:
            self.assertNotIn("modern_location_country", by_candidate[candidate_id])
        self.assertEqual(
            by_candidate["hced-Akhulgo1839-1"]["modern_location_country"],
            "Russia",
        )
        self.assertEqual(
            by_candidate["hced-Girgil1847-1"]["modern_location_country"],
            "Russia",
        )
        self.assertIn("geometry", by_candidate["hced-Saltah1847-1"])
        self.assertEqual(
            by_candidate["hced-Saltah1847-1"]["modern_location_country"],
            "Russia",
        )
        self.assertIn("geometry", by_candidate["hced-Zakataly1853-1"])
        self.assertEqual(
            by_candidate["hced-Zakataly1853-1"]["modern_location_country"],
            "Azerbaijan",
        )
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_iwbd_and_cross_lane_zero_overlap_audits_fail_closed(self) -> None:
        self.assertEqual(WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_dagestan_integration_dispositions(
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

        future_iwbd = copy.deepcopy(self.iwbd_rows)
        future_iwbd.append(
            {
                "candidate_id": "iwbd-future-akhulgo",
                "name": "Akhoulgo",
                "start_date": "1839-06-24",
                "end_date": "1839-09-11",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_dagestan_integration_dispositions(
                self.hced_rows,
                future_iwbd,
            )


if __name__ == "__main__":
    unittest.main()
