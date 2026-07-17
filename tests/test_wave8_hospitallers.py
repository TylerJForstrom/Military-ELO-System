import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_hospitallers as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_hospitallers_"


EXPECTED_RAW = {
    "hced-Krak de Chevaliers1271-1": (
        "Mamlukes",
        "Knights Hospitallier",
        "Mamlukes",
        "Knights Hospitallier",
        1271,
    ),
    "hced-Marqab1285-1": (
        "Mamluk Sultanate",
        "Knights Hospitallier",
        "Mamluk Sultanate",
        "Knights Hospitallier",
        1285,
    ),
    "hced-Rhodes1310-1": (
        "Knights Hospitallier",
        "Byzantium",
        "Knights Hospitallier",
        "Byzantium",
        1310,
    ),
    "hced-Rhodes1480-1": (
        "Knights of St John",
        "Ottoman Empire",
        "Knights of St John",
        "Ottoman Empire",
        1480,
    ),
    "hced-Rhodes1522-1": (
        "Ottoman Empire",
        "Knights Hospitallier",
        "Ottoman Empire",
        "Knights Hospitallier",
        1522,
    ),
    "hced-Smyrna1402-1": (
        "Timurid Empire",
        "Knights of St John",
        "Timurid Empire",
        "Knights of St John",
        1402,
    ),
    "hced-Tripoli, Libya1551-1": (
        "Turkey, Corsairs",
        "Knights of St John",
        "Turkey, Corsairs",
        "Knights of St John",
        1551,
    ),
    "hced-Malta1798-1": (
        "France",
        "Knights of St John",
        "France",
        "Knights of St John",
        1798,
    ),
}

EXPECTED_ACTORS = {
    "hced-Krak de Chevaliers1271-1": (
        {"baybars_mamluk_siege_army_krak_1271"},
        {"hospitaller_krak_garrison_1271"},
    ),
    "hced-Marqab1285-1": (
        {"qalawun_mamluk_siege_army_margat_1285"},
        {"hospitaller_margat_garrison_1285"},
    ),
    "hced-Rhodes1310-1": (
        {"villaret_hospitaller_rhodes_conquest_force_1310"},
        {"byzantine_rhodes_defenders_1310"},
    ),
    "hced-Smyrna1402-1": (
        {"timur_siege_army_smyrna_1402"},
        {"hospitaller_smyrna_garrison_1402"},
    ),
    "hced-Rhodes1480-1": (
        {"hospitaller_rhodes_defenders_1480"},
        {"ottoman_rhodes_expedition_1480"},
    ),
    "hced-Rhodes1522-1": (
        {"suleiman_ottoman_siege_army_rhodes_1522"},
        {"hospitaller_rhodes_defenders_1522"},
    ),
    "hced-Tripoli, Libya1551-1": (
        {
            "sinan_pasha_ottoman_force_tripoli_1551",
            "turgut_reis_corsair_force_tripoli_1551",
        },
        {"hospitaller_tripoli_garrison_1551"},
    ),
    "hced-Malta1798-1": (
        {"french_army_orient_malta_1798"},
        {"hompesch_hospitaller_malta_garrison_1798"},
    ),
}

EXPECTED_COUNTRIES = {
    "hced-Krak de Chevaliers1271-1": "Syria",
    "hced-Marqab1285-1": "Syria",
    "hced-Rhodes1310-1": "Greece",
    "hced-Rhodes1480-1": "Greece",
    "hced-Rhodes1522-1": "Greece",
    "hced-Smyrna1402-1": "Turkey",
    "hced-Tripoli, Libya1551-1": "Libya",
    "hced-Malta1798-1": "Malta",
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
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class Wave8HospitallersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_HOSPITALLERS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_HOSPITALLERS_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_HOSPITALLERS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_hospitallers_entities(entities)
        lane.install_wave8_hospitallers_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_hospitallers_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_signature_counts_and_cohorts_are_exact(self):
        payload = {
            "adjacent_lane_dispositions": lane.WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS,
            "contracts": lane.WAVE8_HOSPITALLERS_CONTRACTS,
            "country_quarantine_additions": sorted(lane.WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS),
            "cross_lane_dispositions": lane.WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS,
            "cross_spelling_duplicate_audit": lane.WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT,
            "entities": lane.WAVE8_HOSPITALLERS_ENTITIES,
            "exact_candidate_id_sha256": lane.WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256,
            "exact_label_funnel_digests": lane.WAVE8_HOSPITALLERS_EXACT_LABEL_FUNNEL_DIGESTS,
            "existing_release_duplicate_dispositions": lane.WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            "expected_candidate_ids": sorted(lane.WAVE8_HOSPITALLERS_EXPECTED_CANDIDATE_IDS),
            "holds": lane.WAVE8_HOSPITALLERS_HOLDS,
            "integration_dispositions": lane.WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": lane.WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": lane.WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": lane.WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_REASONS,
            "opposite_result_audit": lane.WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT,
            "outcome_overrides": lane.WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(lane.WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS),
            "row_hashes": lane.WAVE8_HOSPITALLERS_ROW_HASHES,
            "sources": lane.WAVE8_HOSPITALLERS_SOURCES,
            "terminal_exclusions": lane.WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, lane.WAVE8_HOSPITALLERS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(lane.wave8_hospitallers_audit_signature(), independent)
        self.assertEqual(
            lane.wave8_hospitallers_counts(),
            {
                "adjacent_existing_release_owners": 2,
                "adjacent_hced_rows": 5,
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 5,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 8,
                "new_entities": 17,
                "new_sources": 18,
                "newly_rated_events": 8,
                "outcome_overrides": 0,
                "point_quarantine_additions": 8,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 8,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_hospitallers_cohort_counts(),
            {
                "final_levantine_hospitaller_castles": 2,
                "french_invasion_of_hospitaller_malta": 1,
                "hospitaller_acquisition_of_rhodes": 1,
                "ottoman_hospitaller_rhodes_wars": 2,
                "ottoman_hospitaller_tripoli_wars": 1,
                "rhodian_hospitaller_outposts": 1,
            },
        )

    def test_both_exact_label_inventories_and_funnel_digests_are_pinned(self):
        exact = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") in {"Knights Hospitallier", "Knights of St John"}
            or row.get("side_2_raw") in {"Knights Hospitallier", "Knights of St John"}
        }
        self.assertEqual(set(exact), set(EXPECTED_RAW))
        self.assertEqual(set(exact), lane.WAVE8_HOSPITALLERS_RESERVED_IDS)
        combined = hashlib.sha256(
            "".join(f"{candidate_id}\n" for candidate_id in sorted(exact)).encode()
        ).hexdigest()
        self.assertEqual(combined, lane.WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256)

        funnel_by_label = {
            str(record["label"]): record for record in self.funnel["labels"]
        }
        for raw_label, normalized in (
            ("Knights Hospitallier", "knights hospitallier"),
            ("Knights of St John", "knights of st john"),
        ):
            candidate_ids = sorted(
                candidate_id
                for candidate_id, row in exact.items()
                if raw_label in {row.get("side_1_raw"), row.get("side_2_raw")}
            )
            digest = hashlib.sha256(
                "".join(f"{candidate_id}\n" for candidate_id in candidate_ids).encode()
            ).hexdigest()
            record = funnel_by_label[normalized]
            self.assertEqual(len(candidate_ids), 4)
            self.assertEqual(record["events_touched"], 4)
            self.assertEqual(record["sole_blocker_events"], 4)
            self.assertEqual(record["event_candidate_id_sha256"], digest)
            self.assertEqual(
                digest,
                lane.WAVE8_HOSPITALLERS_EXACT_LABEL_FUNNEL_DIGESTS[normalized],
            )

    def test_raw_rows_and_hashes_are_exact_and_fail_closed(self):
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("candidate_id") in lane.WAVE8_HOSPITALLERS_RESERVED_IDS
        }
        self.assertEqual(
            lane.validate_wave8_hospitallers_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_rows": 5,
                "holds": 0,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 8,
                "terminal_exclusions": 0,
            },
        )
        for candidate_id, expected in EXPECTED_RAW.items():
            row = rows[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                    row["year_best"],
                ),
                expected,
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                lane.WAVE8_HOSPITALLERS_ROW_HASHES[candidate_id],
            )

        for candidate_id in sorted(lane.WAVE8_HOSPITALLERS_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    row for row in tampered if row.get("candidate_id") == candidate_id
                )
                row["winner_raw"] = "Draw"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    lane.validate_wave8_hospitallers_queue_contracts(tampered)

    def test_all_five_adjacent_spellings_are_hash_pinned_and_not_reowned(self):
        expected = {
            "hced-Acre1291-1",
            "hced-Arsouf1191-1",
            "hced-Cresson1187-1",
            "hced-Malta1565-1",
            "hced-Smyrna1344-1",
        }
        self.assertEqual(lane.WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS, expected)
        self.assertEqual(
            lane.WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS,
            lane.WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS,
        )
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for candidate_id, disposition in lane.WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS.items():
            self.assertEqual(
                canonical_hced_row_sha256(by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )

        release_by_candidate = {
            str(event["hced_candidate_id"]): event
            for event in self.release_events
            if event.get("hced_candidate_id")
        }
        self.assertEqual(
            release_by_candidate["hced-Arsouf1191-1"]["id"],
            "hced_hced_arsouf1191_1",
        )
        self.assertEqual(
            release_by_candidate["hced-Malta1565-1"]["id"],
            "hced_hced_malta1565_1",
        )
        for candidate_id in {
            "hced-Acre1291-1",
            "hced-Cresson1187-1",
            "hced-Smyrna1344-1",
        }:
            self.assertNotIn(candidate_id, release_by_candidate)

        tampered = copy.deepcopy(self.hced_rows)
        row = next(row for row in tampered if row["candidate_id"] == "hced-Acre1291-1")
        row["side_2_raw"] += ", changed"
        with self.assertRaisesRegex(ValueError, "adjacent row fingerprint changed"):
            lane.validate_wave8_hospitallers_queue_contracts(tampered)

    def test_sources_are_independent_parseable_and_fully_used(self):
        sources = {str(source["id"]): source for source in lane.WAVE8_HOSPITALLERS_SOURCES}
        self.assertEqual(len(sources), 18)
        self.assertEqual(
            len({source["source_family_id"] for source in sources.values()}),
            18,
        )
        used = set()
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
        for entity in lane.WAVE8_HOSPITALLERS_ENTITIES:
            used.update(entity["source_ids"])
        for contract in lane.WAVE8_HOSPITALLERS_CONTRACTS.values():
            used.update(contract["evidence_refs"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                set(contract["outcome_source_ids"]),
                {
                    source_id
                    for source_id in contract["outcome_source_ids"]
                    if "outcome" in sources[source_id]["evidence_roles"]
                },
            )
        self.assertEqual(used, set(sources))

    def test_seventeen_entities_are_event_bounded_and_open_no_alias(self):
        self.assertEqual(len(lane.WAVE8_HOSPITALLERS_ENTITIES), 17)
        entity_ids = set()
        for entity in lane.WAVE8_HOSPITALLERS_ENTITIES:
            Entity.from_dict(entity)
            entity_ids.add(str(entity["id"]))
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertTrue(entity["kind"].startswith("event_bounded_"))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern state", note)
        self.assertEqual(len(entity_ids), 17)
        self.assertFalse(
            {
                "byzantium",
                "france",
                "knights_hospitaller",
                "knights_of_st_john",
                "mamluk_sultanate",
                "ottoman_empire",
                "timurid_empire",
                "turkey",
            }
            & entity_ids
        )

        used = {
            entity_id
            for contract in lane.WAVE8_HOSPITALLERS_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertEqual(used, entity_ids)

    def test_all_eight_promotions_are_parseable_source_aligned_wins(self):
        events = self._events()
        self.assertEqual(len(events), 8)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_ACTORS))
        canonical_keys = set()
        for candidate_id, (winners, losers) in EXPECTED_ACTORS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual((event["year"], event["end_year"]), (EXPECTED_RAW[candidate_id][4],) * 2)
            actual_winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_victory"
            }
            actual_losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_defeat"
            }
            self.assertEqual(actual_winners, winners)
            self.assertEqual(actual_losers, losers)
            self.assertEqual(
                {item["termination"] for item in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )
            self.assertNotIn(
                "inconclusive_engagement",
                {item["termination"] for item in event["participants"]},
            )
            canonical_keys.add(event["canonical_event_key"])
            contract = lane.WAVE8_HOSPITALLERS_CONTRACTS[candidate_id]
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(contract["winner_side"], 1)
        self.assertEqual(len(canonical_keys), 8)

    def test_rhodes_1310_is_a_bounded_campaign_completion_not_an_invented_day(self):
        contract = lane.WAVE8_HOSPITALLERS_CONTRACTS["hced-Rhodes1310-1"]
        canonical = contract["canonical_event"]
        self.assertEqual(canonical["year_low"], 1310)
        self.assertEqual(canonical["year_high"], 1310)
        self.assertEqual(canonical["granularity"], "campaign_completion")
        self.assertEqual(
            canonical["date_precision"],
            "year_with_disputed_completion_chronology",
        )
        self.assertLess(contract["confidence"], 0.80)
        self.assertIn("1309 and 1310", contract["audit_note"])
        self.assertIn("not an invented single-day battle", contract["audit_note"])
        self.assertFalse(contract["source_outcome_override"])

        event = next(
            event
            for event in self._events()
            if event["hced_candidate_id"] == "hced-Rhodes1310-1"
        )
        self.assertEqual(event["reviewed_granularity"], "campaign_completion")
        self.assertEqual((event["year"], event["end_year"]), (1310, 1310))

    def test_hospitaller_eras_and_namesake_regimes_never_bridge(self):
        entities = {str(item["id"]): item for item in lane.WAVE8_HOSPITALLERS_ENTITIES}
        hospitaller_ids = {
            entity_id
            for entity_id in entities
            if "hospitaller" in entity_id
        }
        self.assertEqual(len(hospitaller_ids), 8)
        self.assertEqual(
            {entities[entity_id]["start_year"] for entity_id in hospitaller_ids},
            {1271, 1285, 1310, 1402, 1480, 1522, 1551, 1798},
        )
        for entity_id in hospitaller_ids:
            self.assertEqual(
                entities[entity_id]["start_year"],
                entities[entity_id]["end_year"],
            )
        tripoli = lane.WAVE8_HOSPITALLERS_CONTRACTS["hced-Tripoli, Libya1551-1"]
        self.assertEqual(len(tripoli["side_1_entity_ids"]), 2)
        self.assertNotIn("turkey", tripoli["side_1_entity_ids"])
        self.assertNotIn("libya", tripoli["side_1_entity_ids"])

    def test_promoted_points_are_withheld_but_reviewed_countries_remain(self):
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(
            lane.WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_HOSPITALLERS_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            lane.wave8_hospitallers_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_HOSPITALLERS_CONTRACT_IDS,
            },
        )
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], EXPECTED_COUNTRIES[candidate_id])
            self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_cross_spelling_duplicates_and_opposite_results_are_explicitly_zero(self):
        audit = lane.WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT
        self.assertEqual(
            audit["exact_source_labels"],
            ["Knights Hospitallier", "Knights of St John"],
        )
        self.assertEqual(audit["same_event_candidate_pairs"], [])
        self.assertEqual(
            lane.WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT[
                "same_event_opposite_result_pairs"
            ],
            [],
        )

        exact_rows = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") in lane.WAVE8_HOSPITALLERS_RESERVED_IDS
        ]
        keys = [
            (normalize_label(row["name"]), int(row["year_best"]))
            for row in exact_rows
        ]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(row["winner_loser_complete"] for row in exact_rows))
        self.assertTrue(all(normalize_label(row["winner_raw"]) != "draw" for row in exact_rows))

    def test_duplicate_audits_validate_current_snapshots_and_fail_on_future_twins(self):
        current_overlap = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_HOSPITALLERS_CONTRACT_IDS
        }
        self.assertIn(
            len(current_overlap),
            {0, len(lane.WAVE8_HOSPITALLERS_CONTRACT_IDS)},
        )
        result = lane.validate_wave8_hospitallers_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(
            result,
            {
                "adjacent_existing_release_owners": 2,
                "cross_lane_hced_dispositions": 5,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": len(current_overlap),
            },
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-rhodes-1480-twin",
                "name": "Siege of Rhodes",
                "year_best": 1480,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_hospitallers_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-smyrna-1402",
                "name": "Siege of Smyrna",
                "start_date": "1402-12-01",
                "end_date": "1402-12-15",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_hospitallers_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {"id": "future-margat-twin", "name": "Siege of Margat", "year": 1285},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_hospitallers_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_release_overlap_must_be_all_or_none(self):
        events = self._events()
        release_without_lane = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_HOSPITALLERS_CONTRACT_IDS
        ]
        fully_integrated = [*release_without_lane, *events]
        result = lane.validate_wave8_hospitallers_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            fully_integrated,
        )
        self.assertEqual(result["release_lane_overlap"], 8)

        partial = [*release_without_lane, events[0]]
        with self.assertRaisesRegex(ValueError, "partial release integration"):
            lane.validate_wave8_hospitallers_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                partial,
            )

    def test_entity_windows_and_duplicate_event_collisions_fail_closed(self):
        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short["hospitaller_krak_garrison_1271"]["start_year"] = 1272
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_hospitallers_contracts(
                self.hced_rows,
                short,
                existing,
            )

        events = lane.promote_wave8_hospitallers_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_hospitallers_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        collision = [
            *existing,
            {"name": "Siege of Rhodes (1480)", "year": 1480},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_hospitallers_contracts(
                self.hced_rows,
                entities,
                collision,
            )

    def test_installers_copy_and_reject_collisions(self):
        entities = {}
        sources = {}
        lane.install_wave8_hospitallers_entities(entities)
        lane.install_wave8_hospitallers_sources(sources)
        first_entity = str(lane.WAVE8_HOSPITALLERS_ENTITIES[0]["id"])
        first_source = str(lane.WAVE8_HOSPITALLERS_SOURCES[0]["id"])
        entities[first_entity]["name"] = "tampered"
        sources[first_source]["title"] = "tampered"
        self.assertNotEqual(
            entities[first_entity]["name"],
            lane.WAVE8_HOSPITALLERS_ENTITIES[0]["name"],
        )
        self.assertNotEqual(
            sources[first_source]["title"],
            lane.WAVE8_HOSPITALLERS_SOURCES[0]["title"],
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_hospitallers_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_hospitallers_sources(sources)


if __name__ == "__main__":
    unittest.main()
