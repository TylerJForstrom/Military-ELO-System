import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_libya as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_libya_"
LIBYA = "libyan_arab_jamahiriya"
CHAD = "republic_chad"
FAYA_GUNT = "gunt_faya_largeau_assault_force_1983"

EXPECTED_HASHES = {
    "hced-Aozou1987-1": (
        "7f972cd9cf50ca7a68c757194cb4a379c4f10c6aad20c89f03b89ffe5b8a1c7f"
    ),
    "hced-Faya Largeau1983-1": (
        "632d34a58b407b31fc8d7bbee9e89e8ad91f824cba437d95ff9a5b3e0ca9b6e0"
    ),
    "hced-Zouar1986-1987-1": (
        "5e45a4627804bb2f967845a7a410883774054fcd2cdde5f2decfb0ea93a6f1af"
    ),
}
EXISTING_HASHES = {
    "hced-Fada1987-1": (
        "63a7cc4122190f20ce9af413fc9ebb56f47d470625164615b75db636e4701981"
    ),
    "hced-Maaten-as-Sarra1987-1": (
        "2add7231c5894860d7bca804c09140162e8f3db388e2f28f2d2a775a8dcc17b8"
    ),
    "hced-Ouadi Doum1987-1": (
        "bc281cbb67c6f63ee838035ce8529007ad390df10061995989998f17b177a0db"
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


def _historical_funnel():
    projection = copy.deepcopy(lane.WAVE8_LIBYA_FUNNEL_AUDIT)
    wrong_interval = projection.pop("one_wrong_interval_candidate")
    projection["failure_cases"] = {
        "one_wrong_interval_candidate": wrong_interval,
    }
    return {"labels": [projection]}


class Wave8LibyaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "libya"
            or normalize_label(row.get("side_2_raw")) == "libya"
        ]

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        source_ids = {str(item["id"]) for item in lane.WAVE8_LIBYA_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_LIBYA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_libya_entities(entities)
        lane.install_wave8_libya_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_libya_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_partitions_all_six_rows_and_hashes(self):
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES) | set(EXISTING_HASHES))
        self.assertEqual(lane.WAVE8_LIBYA_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            set(lane.WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS),
            set(EXISTING_HASHES),
        )
        for candidate_id, row in by_id.items():
            with self.subTest(candidate_id=candidate_id):
                expected = (
                    EXPECTED_HASHES[candidate_id]
                    if candidate_id in EXPECTED_HASHES
                    else EXISTING_HASHES[candidate_id]
                )
                self.assertEqual(canonical_hced_row_sha256(row), expected)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")
        self.assertEqual(
            lane.validate_wave8_libya_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 6,
                "existing_release_dispositions": 3,
                "holds": 0,
                "outcome_reversals": 2,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
            },
        )

    def test_historical_funnel_is_pinned_and_live_libya_label_is_absent(self):
        self.assertEqual(
            lane.validate_wave8_libya_funnel(_historical_funnel()),
            {
                "events_touched": 3,
                "one_wrong_interval_candidate": 3,
                "sole_blocker_events": 3,
            },
        )
        self.assertFalse(
            [row for row in self.funnel.get("labels", []) if row.get("label") == "libya"]
        )

    def test_discovery_rows_stay_nonautomatic_and_only_contracts_rate(self):
        self.assertEqual(lane.WAVE8_LIBYA_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_LIBYA_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_LIBYA_HOLDS)
        self.assertTrue(
            all(
                row.get("do_not_rate_automatically") is True
                for row in self.exact_rows
                if row["candidate_id"] in lane.WAVE8_LIBYA_RESERVED_IDS
            )
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in self._events()},
            lane.WAVE8_LIBYA_CONTRACT_IDS,
        )

    def test_identity_windows_and_alias_firewalls_are_unchanged(self):
        entities = {str(item["id"]): item for item in self.release_entities}
        self.assertEqual(
            (entities[LIBYA]["start_year"], entities[LIBYA]["end_year"]),
            (1977, 2011),
        )
        self.assertEqual(entities[LIBYA]["aliases"], [])
        self.assertEqual(
            (entities[CHAD]["start_year"], entities[CHAD]["end_year"]),
            (1960, None),
        )
        self.assertEqual(entities[CHAD]["aliases"], [])
        self.assertNotIn("libya", HCED_LABEL_POLICIES)
        gunt = entities[FAYA_GUNT]
        self.assertEqual((gunt["start_year"], gunt["end_year"]), (1983, 1983))
        self.assertEqual(gunt["aliases"], [])
        self.assertEqual(gunt["predecessors"], [])
        for entity_id in (LIBYA, CHAD, FAYA_GUNT):
            Entity.from_dict(entities[entity_id])

    def test_faya_is_a_high_confidence_aligned_coalition_victory(self):
        contract = lane.WAVE8_LIBYA_CONTRACTS["hced-Faya Largeau1983-1"]
        self.assertEqual(contract["confidence"], 0.92)
        self.assertEqual(contract["winner_side"], 1)
        self.assertFalse(contract["source_outcome_override"])
        self.assertFalse(contract["outcome_reversal"])
        self.assertEqual(contract["side_1_entity_ids"], [LIBYA, FAYA_GUNT])
        self.assertEqual(contract["side_2_entity_ids"], [CHAD])
        row = next(
            item
            for item in self.exact_rows
            if item["candidate_id"] == "hced-Faya Largeau1983-1"
        )
        self.assertEqual(row["winner_raw"], row["side_1_raw"])
        event = next(
            item
            for item in self._events()
            if item["hced_candidate_id"] == "hced-Faya Largeau1983-1"
        )
        winners = {
            participant["entity_id"]
            for participant in event["participants"]
            if participant["termination"] == "engagement_victory"
        }
        self.assertEqual(winners, {LIBYA, FAYA_GUNT})

    def test_aozou_and_zouar_are_explicit_medium_confidence_reversals(self):
        expected = {
            "hced-Aozou1987-1": (LIBYA, "Chad", "Libya"),
            "hced-Zouar1986-1987-1": (CHAD, "Libya", "Chad"),
        }
        events = {event["hced_candidate_id"]: event for event in self._events()}
        for candidate_id, (winner, raw_winner, reviewed_winner) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_LIBYA_CONTRACTS[candidate_id]
                self.assertEqual(contract["confidence"], 0.78)
                self.assertEqual(contract["winner_side"], 2)
                self.assertIs(contract["source_outcome_override"], True)
                self.assertIs(contract["outcome_reversal"], True)
                conflict = contract["source_conflict_disposition"]
                self.assertEqual(conflict["raw_winner"], raw_winner)
                self.assertEqual(conflict["reviewed_winner"], reviewed_winner)
                terminations = {
                    item["entity_id"]: item["termination"]
                    for item in events[candidate_id]["participants"]
                }
                self.assertEqual(terminations[winner], "engagement_victory")

    def test_unknown_is_never_a_draw_and_every_emission_is_tactical(self):
        self.assertTrue(
            all(
                contract["result_type"] == "win"
                for contract in lane.WAVE8_LIBYA_CONTRACTS.values()
            )
        )
        for event in self._events():
            self.assertEqual(event["event_type"], "engagement")
            self.assertIn("engagement_victory", {
                item["termination"] for item in event["participants"]
            })
            self.assertFalse(
                any(
                    "inconclusive" in item["termination"]
                    for item in event["participants"]
                )
            )
            Event.from_dict(event)

    def test_iwbd_rows_are_dispositioned_without_duplicate_emissions(self):
        self.assertEqual(
            set(lane.WAVE8_LIBYA_IWBD_DISPOSITIONS),
            {"iwbd-207-80-1651", "iwbd-207-80-1654"},
        )
        self.assertIs(
            lane.WAVE8_LIBYA_IWBD_DISPOSITIONS["iwbd-207-80-1654"][
                "date_alignment_claimed"
            ],
            False,
        )
        self.assertIs(
            lane.WAVE8_LIBYA_IWBD_DISPOSITIONS["iwbd-207-80-1651"][
                "date_alignment_claimed"
            ],
            True,
        )
        released_iwbd_ids = {
            event.get("iwbd_candidate_id") for event in self.release_events
        }
        self.assertNotIn("iwbd-207-80-1651", released_iwbd_ids)
        self.assertNotIn("iwbd-207-80-1654", released_iwbd_ids)

    def test_existing_fada_ouadi_doum_and_maaten_owners_are_exact(self):
        events = {str(event["id"]): event for event in self.release_events}
        for disposition in lane.WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS.values():
            with self.subTest(owner_event_id=disposition["owner_event_id"]):
                event = events[disposition["owner_event_id"]]
                self.assertEqual(event["name"], disposition["expected_name"])
                self.assertEqual(event["year"], 1987)
                self.assertEqual(
                    {item["entity_id"] for item in event["participants"]},
                    {LIBYA, CHAD},
                )

    def test_chadian_rebels_lane_is_frozen_before_and_after_promotion(self):
        before = lane.validate_wave8_libya_frozen_chadian_rebels()
        self._events()
        after = lane.validate_wave8_libya_frozen_chadian_rebels()
        self.assertEqual(before, after)
        self.assertEqual(before, lane.WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE)

    def test_sources_parse_and_every_outcome_has_two_families(self):
        self.assertEqual(len(lane.WAVE8_LIBYA_SOURCES), 6)
        source_ids = {str(source["id"]) for source in lane.WAVE8_LIBYA_SOURCES}
        consumed = set(lane.WAVE8_LIBYA_ENTITIES[0]["source_ids"])
        for source in lane.WAVE8_LIBYA_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_LIBYA_CONTRACTS.values():
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            consumed.update(contract["evidence_refs"])
        self.assertEqual(consumed, source_ids)

    def test_source_locations_are_retained_as_unreviewed_assertions(self):
        self.assertFalse(lane.WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS)
        expected = {
            "hced-Aozou1987-1": ("Chad", [17.4307172, 21.8163242]),
            "hced-Faya Largeau1983-1": ("Libya", [19.1107114, 17.9236623]),
            "hced-Zouar1986-1987-1": ("Chad", [16.52865, 20.45155]),
        }
        for event in self._events():
            country, coordinates = expected[event["hced_candidate_id"]]
            self.assertEqual(event["modern_location_country"], country)
            self.assertEqual(event["geometry"]["coordinates"], coordinates)
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )

    def test_integration_dispositions_are_zero_twin_and_all_or_none(self):
        self.assertEqual(
            lane.validate_wave8_libya_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "existing_release_dispositions": 3,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_dispositions": 2,
                "iwbd_probable_twins": 0,
            },
        )

    def test_future_cross_source_twins_and_owner_drift_fail_closed(self):
        fixtures = {
            "hced": (
                [
                    *copy.deepcopy(self.hced_rows),
                    {
                        "candidate_id": "hced-future-aozou-twin",
                        "name": "Aozou",
                        "year_low": 1987,
                        "side_1_raw": "Future A",
                        "side_2_raw": "Future B",
                    },
                ],
                self.iwbd_rows,
                self.release_events,
            ),
            "iwbd": (
                self.hced_rows,
                [
                    *copy.deepcopy(self.iwbd_rows),
                    {
                        "candidate_id": "iwbd-future-zouar-twin",
                        "batname": "Zouar",
                        "batyear": 1987,
                    },
                ],
                self.release_events,
            ),
            "release": (
                self.hced_rows,
                self.iwbd_rows,
                [
                    *copy.deepcopy(self.release_events),
                    {"id": "future-faya-twin", "name": "Faya Largeau", "year": 1983},
                ],
            ),
        }
        for view, (hced, iwbd, events) in fixtures.items():
            with self.subTest(view=view):
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_libya_integration_dispositions(
                        hced,
                        iwbd,
                        events,
                    )

        drifted = copy.deepcopy(self.release_events)
        event = next(
            item for item in drifted if item["id"] == "iwbd_iwbd_207_80_1652_fada"
        )
        event["name"] = "Fada drift"
        with self.assertRaisesRegex(ValueError, "existing IWBD owner drift"):
            lane.validate_wave8_libya_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                drifted,
            )

    def test_probable_twin_title_variants_and_aouzou_spelling_fail_closed(self):
        for name in ("Battle of Aozou", "Battle of Aouzou"):
            with self.subTest(name=name):
                future = {
                    "candidate_id": f"hced-future-{name.lower().replace(' ', '-')}",
                    "name": name,
                    "year_low": 1987,
                    "side_1_raw": "Future A",
                    "side_2_raw": "Future B",
                }
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_libya_integration_dispositions(
                        [*copy.deepcopy(self.hced_rows), future],
                        self.iwbd_rows,
                        self.release_events,
                    )

    def test_duplicate_existing_owner_ids_fail_closed(self):
        owner = next(
            event
            for event in self.release_events
            if event["id"] == "iwbd_iwbd_207_80_1652_fada"
        )
        with self.assertRaisesRegex(
            ValueError,
            "missing or duplicate existing IWBD owner",
        ):
            lane.validate_wave8_libya_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*copy.deepcopy(self.release_events), copy.deepcopy(owner)],
            )

    def test_queue_iwbd_fingerprints_and_duplicate_promotion_fail_closed(self):
        drifted_hced = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in drifted_hced if item["candidate_id"] == "hced-Aozou1987-1"
        )
        row["winner_raw"] = "Libya"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_libya_queue_contracts(drifted_hced)

        drifted_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(
            item for item in drifted_iwbd if item["candidate_id"] == "iwbd-207-80-1654"
        )
        row["winner_raw"] = "Chad"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint changed"):
            lane.validate_wave8_libya_integration_dispositions(
                self.hced_rows,
                drifted_iwbd,
                self.release_events,
            )

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_libya_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_libya_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_counts_cohorts_metadata_and_signature_are_pinned(self):
        self.assertEqual(
            lane.wave8_libya_counts(),
            {
                "country_quarantine_additions": 0,
                "existing_release_dispositions": 3,
                "holds": 0,
                "iwbd_dispositions": 2,
                "new_entities": 1,
                "new_sources": 6,
                "newly_rated_events": 3,
                "outcome_overrides": 2,
                "point_quarantine_additions": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_libya_cohort_counts(),
            {"chadian_libyan_war_1983_1987": 3},
        )
        self.assertEqual(
            lane.wave8_libya_audit_signature(),
            "430735c63fd4b67ae76900b9f8f775343335896303cc8e7cbaf52fa52695dfa3",
        )
        self.assertEqual(
            lane.wave8_libya_audit_signature(),
            lane.WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_libya_metadata(),
            {
                "counts": lane.wave8_libya_counts(),
                "cohorts": lane.wave8_libya_cohort_counts(),
                "final_audit_signature": lane.WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE,
                "promoted_candidate_ids": sorted(lane.WAVE8_LIBYA_CONTRACT_IDS),
            },
        )

    def test_current_release_and_registry_match_lane_three_pins(self):
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_LIBYA_CONTRACT_IDS
        ]
        self.assertEqual(len(owned), 3)
        self.assertEqual(
            {event["hced_candidate_id"] for event in owned},
            lane.WAVE8_LIBYA_CONTRACT_IDS,
        )
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in owned)
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_libya_hced_events"], 3)
        self.assertEqual(
            promotion["wave8_libya_metadata"],
            lane.wave8_libya_metadata(),
        )
        self.assertEqual(
            promotion["wave8_libya_queue_validation"],
            lane.validate_wave8_libya_queue_contracts(self.hced_rows),
        )
        self.assertEqual(
            promotion["wave8_libya_frozen_chadian_rebels_pre_validation"],
            promotion["wave8_libya_frozen_chadian_rebels_post_validation"],
        )
        self.assertEqual(len(self.release_events), 5_526)
        self.assertEqual(len(self.release_entities), 1_084)
        self.assertEqual(len(self.release_sources), 1_580)

        coverage = self.registry["coverage"]
        self.assertEqual(coverage["rated_events"], 5_526)
        self.assertEqual(coverage["rated_entities"], 1_077)
        self.assertEqual(coverage["registry_polities"], 2_423)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_817)
        self.assertEqual(coverage["candidate_keyed_wave8_libya_hced_events"], 3)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_259)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 847)
        self.assertEqual(location["geojson_points"], 4_843)
        self.assertEqual(location["modern_location_country_assertions"], 5_163)
        self.assertEqual(location["location_provenance_objects"], 5_212)
        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        self.assertEqual(registry_entities[FAYA_GUNT]["status"], "rated")
        self.assertEqual(
            registry_entities[FAYA_GUNT]["identity_status"],
            "curated",
        )


if __name__ == "__main__":
    unittest.main()
