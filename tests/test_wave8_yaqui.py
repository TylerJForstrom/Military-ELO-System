import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_yaqui as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_yaqui_"

TAMBOR_MEXICAN = "vildosola_provincial_force_cerro_tambor_1740"
TAMBOR_YAQUI_MAYO = "yaqui_mayo_rebel_force_cerro_tambor_1740"
ANIL_MEXICAN = "carrillo_mexican_anil_operation_force_1886_05_03_05"
ANIL_YAQUI = "cajeme_yaqui_anil_defenders_1886_05_05"
BUATACHIVE_MEXICAN = (
    "martinez_mexican_buatachive_assault_force_1886_05_09_12"
)
BUATACHIVE_YAQUI = "cajeme_yaqui_buatachive_defenders_1886_05_09_12"

EXPECTED_RAW_HASHES = {
    "hced-Anil1886-1": (
        "2e16f7706564f593fd6915ca26486962a5c1edac5c5f8d6a28c6ef6977115c11"
    ),
    "hced-Bacum1868-1": (
        "62df82df26a541d4328a19319e00d7050a3c6715e503e330e5c0e24b4f51db54"
    ),
    "hced-Buatachive1886-1": (
        "1d43b67a765e1d1bc33f553f914ce62edb81abba68510c9beaa29b6ad098b9bf"
    ),
    "hced-Mount Tambor1740-1": (
        "c8054c87809f483ba39889f50fd7d472d535c714e4ca7da316da10bbbbc28f83"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Anil1886-1": {
        "name": "Anil",
        "side_1": "Mexico",
        "side_2": "Yaqui",
        "winner": "Mexico",
        "loser": "Yaqui",
        "year": 1886,
        "point": [-109.0571847, 25.9664053],
        "massacre": "Battle followed by massacre",
        "war_names": ["Mexico-Yaqui War"],
    },
    "hced-Bacum1868-1": {
        "name": "Bacum",
        "side_1": "Mexico",
        "side_2": "Yaqui",
        "winner": "Mexico",
        "loser": "Yaqui",
        "year": 1868,
        "point": [-110.091967, 27.5506671],
        "massacre": "Yes",
        "war_names": ["Mexican-Yaqui War"],
    },
    "hced-Buatachive1886-1": {
        "name": "Buatachive",
        "side_1": "Mexico",
        "side_2": "Yaqui",
        "winner": "Mexico",
        "loser": "Yaqui",
        "year": 1886,
        "point": [-110.2488105, 27.6337884],
        "massacre": "No",
        "war_names": ["Mexico-Yaqui War"],
    },
    "hced-Mount Tambor1740-1": {
        "name": "Mount Tambor",
        "side_1": "Spain",
        "side_2": "Yaqui",
        "winner": "Spain",
        "loser": "Yaqui",
        "year": 1740,
        "point": [-105.0745437, 19.510535],
        "massacre": "No",
        "war_names": ["Spanish-Yaqui War"],
    },
}

EXPECTED_EVENTS = {
    "hced-Mount Tambor1740-1": {
        "name": "Battle of Cerro del Tambor",
        "year": 1740,
        "date_text": (
            "1740, before the later Otancahui battle; exact day not established"
        ),
        "date_precision": "year",
        "granularity": "single_battle_at_cerro_del_tambor",
        "winner": {TAMBOR_MEXICAN},
        "loser": {TAMBOR_YAQUI_MAYO},
        "confidence": 0.90,
    },
    "hced-Anil1886-1": {
        "name": "Battle of El Anil",
        "year": 1886,
        "date_text": "5 May 1886",
        "date_precision": "day",
        "granularity": "fortification_attack_withdrawal_and_occupation",
        "winner": {ANIL_MEXICAN},
        "loser": {ANIL_YAQUI},
        "confidence": 0.92,
    },
    "hced-Buatachive1886-1": {
        "name": "Battle of Buatachive",
        "year": 1886,
        "date_text": "9-12 May 1886",
        "date_precision": "day_range",
        "granularity": "four_day_siege_and_three_hour_final_assault",
        "winner": {BUATACHIVE_MEXICAN},
        "loser": {BUATACHIVE_YAQUI},
        "confidence": 0.96,
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


class Wave8YaquiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data" / "review" / "hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "yaqui"
            or normalize_label(row.get("side_2_raw")) == "yaqui"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_YAQUI_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_YAQUI_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_YAQUI_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_yaqui_entities(entities)
        lane.install_wave8_yaqui_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_yaqui_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_queue_and_row_fingerprints_are_pinned(self):
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_YAQUI_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_YAQUI_IWBD_QUEUE_SHA256,
        )
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, lane.WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(lane.WAVE8_YAQUI_ROW_HASHES, EXPECTED_RAW_HASHES)
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_RAW_HASHES[candidate_id],
                )
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1"])
                self.assertEqual(row["side_2_raw"], expected["side_2"])
                self.assertEqual(row["winner_raw"], expected["winner"])
                self.assertEqual(row["loser_raw"], expected["loser"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )
                self.assertEqual(row["massacre_raw"], expected["massacre"])
                self.assertEqual(row["war_names"], expected["war_names"])
                self.assertEqual(row["modern_location_country"], "Mexico")

    def test_task_label_mismatch_digest_funnel_and_queue_are_pinned(self):
        literal_task_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "yaqui indians"
            or normalize_label(row.get("side_2_raw")) == "yaqui indians"
        }
        self.assertEqual(literal_task_ids, set())
        self.assertEqual(
            lane.WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY["yaqui indians"],
            (),
        )
        payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(EXPECTED_RAW_ROWS)
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(digest, lane.WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(
            digest,
            lane.WAVE8_YAQUI_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(
            lane.validate_wave8_yaqui_funnel(self.funnel),
            {
                "events_touched": 4,
                "release_lane_overlap": 0,
                "sole_blocker_events": 4,
            },
        )
        self.assertEqual(
            lane.validate_wave8_yaqui_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.WAVE8_YAQUI_WAR_LABEL_INVENTORY,
            {
                "mexican yaqui war": ("hced-Bacum1868-1",),
                "mexico yaqui war": (
                    "hced-Anil1886-1",
                    "hced-Buatachive1886-1",
                ),
                "spanish yaqui war": ("hced-Mount Tambor1740-1",),
            },
        )

    def test_new_adjacent_spelling_or_yaqui_war_row_fails_closed(self):
        changed = copy.deepcopy(self.hced_rows)
        changed.append(
            {
                "candidate_id": "hced-future-yaquis-row",
                "side_1_raw": "Yaquis",
                "side_2_raw": "Mexico",
                "war_names": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "adjacent Yaqui spelling"):
            lane.validate_wave8_yaqui_queue_contracts(changed)

        changed = copy.deepcopy(self.hced_rows)
        changed.append(
            {
                "candidate_id": "hced-future-yaqui-war-row",
                "side_1_raw": "Sonoran rebels",
                "side_2_raw": "Mexico",
                "war_names": ["Spanish-Yaqui War"],
            }
        )
        with self.assertRaisesRegex(ValueError, "complete Yaqui war inventory"):
            lane.validate_wave8_yaqui_queue_contracts(changed)

    def test_bacum_massacre_is_terminally_excluded_and_never_a_draw(self):
        self.assertEqual(lane.WAVE8_YAQUI_HOLDS, {})
        self.assertEqual(
            lane.WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS,
            {"hced-Bacum1868-1"},
        )
        exclusion = lane.WAVE8_YAQUI_TERMINAL_EXCLUSIONS[
            "hced-Bacum1868-1"
        ]
        self.assertEqual(
            exclusion["reviewed_outcome"],
            "not_rateable_prisoner_massacre",
        )
        self.assertEqual(
            exclusion["exclusion_category"],
            "noncompetitive_massacre_of_prisoners",
        )
        self.assertIs(exclusion["terminal_exclusion"], True)
        self.assertIs(exclusion["unknown_is_never_draw"], True)
        self.assertIs(exclusion["historical_review"]["competitive_event"], False)
        self.assertEqual(
            exclusion["historical_review"]["distinct_bacum_battle"],
            "10 January 1868",
        )
        for forbidden in (
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        ):
            self.assertNotIn(forbidden, exclusion)
        self.assertNotIn(
            "hced-Bacum1868-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_six_formations_are_time_bounded_and_never_generic(self):
        by_id = {
            str(entity["id"]): entity for entity in lane.WAVE8_YAQUI_ENTITIES
        }
        expected_ids = {
            TAMBOR_MEXICAN,
            TAMBOR_YAQUI_MAYO,
            ANIL_MEXICAN,
            ANIL_YAQUI,
            BUATACHIVE_MEXICAN,
            BUATACHIVE_YAQUI,
        }
        self.assertEqual(set(by_id), expected_ids)
        for entity_id, entity in by_id.items():
            Entity.from_dict(entity)
            expected_year = 1740 if "tambor_1740" in entity_id else 1886
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                (expected_year, expected_year),
            )
            self.assertEqual(entity["aliases"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
        for forbidden in (
            "mayo",
            "mexico",
            "sonora",
            "spain",
            "yaqui",
            "yaqui_indians",
            "yaqui_nation",
        ):
            self.assertNotIn(forbidden, by_id)
        self.assertFalse(any("bacum1868" in entity_id for entity_id in by_id))

    def test_sources_are_independent_authoritative_and_model_valid(self):
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_YAQUI_SOURCES
        }
        self.assertEqual(len(source_by_id), 9)
        families = {
            str(source["source_family_id"]) for source in source_by_id.values()
        }
        self.assertEqual(len(families), 9)
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertNotIn("wikipedia.org", source["url"])
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        for contract in lane.WAVE8_YAQUI_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

    def test_contracts_preserve_source_orientation_and_harm_boundaries(self):
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(lane.WAVE8_YAQUI_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in lane.WAVE8_YAQUI_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertIs(contract["source_outcome_override"], False)
                self.assertIs(contract["outcome_reversal"], False)
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertNotEqual(normalize_label(row["winner_raw"]), "draw")
        self.assertIn(
            "not_corroborated",
            lane.WAVE8_YAQUI_CONTRACTS["hced-Anil1886-1"][
                "massacre_disposition"
            ],
        )
        self.assertIn(
            "civilian_harm_attested",
            lane.WAVE8_YAQUI_CONTRACTS["hced-Buatachive1886-1"][
                "massacre_disposition"
            ],
        )
        self.assertIn(
            "Families confined within the position are not made combatants",
            next(
                entity["continuity_note"]
                for entity in lane.WAVE8_YAQUI_ENTITIES
                if entity["id"] == BUATACHIVE_YAQUI
            ),
        )

    def test_scope_event_and_cross_lane_ownership_audits_are_complete(self):
        audits = lane.WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT
        self.assertEqual(set(audits), lane.WAVE8_YAQUI_RESERVED_IDS)
        self.assertEqual(
            audits["hced-Anil1886-1"]["disposition"],
            "promote_mexican_1886_anil_victory",
        )
        self.assertIn(
            "1885",
            audits["hced-Anil1886-1"]["opposite_result_disposition"],
        )
        self.assertEqual(
            audits["hced-Bacum1868-1"]["disposition"],
            "terminally_exclude_noncompetitive_massacre",
        )
        self.assertEqual(
            set(lane.WAVE8_YAQUI_EVENT_BOUNDARIES),
            {
                "anil_to_buatachive_1886",
                "bacum_battle_to_church_massacre_1868",
                "tambor_to_otancahui_1740",
            },
        )
        self.assertEqual(
            set(lane.WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS),
            {
                "exact_label_boundary",
                "modern_tribal_governments",
                "raw_state_and_coalition_labels",
            },
        )
        self.assertEqual(len(lane.WAVE8_YAQUI_INTEGRATION_DISPOSITIONS), 6)
        for audit in audits.values():
            self.assertTrue(audit["opposite_result_disposition"])
            self.assertTrue(audit["scope_note"])

    def test_promotion_emits_three_canonical_events_with_exact_actor_sets(self):
        events = self._events()
        self.assertEqual(len(events), 3)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            with self.subTest(candidate_id=candidate_id):
                event = by_candidate[candidate_id]
                contract = lane.WAVE8_YAQUI_CONTRACTS[candidate_id]
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["year"], expected["year"])
                self.assertEqual(event["end_year"], expected["year"])
                self.assertEqual(event["date_precision"], expected["date_precision"])
                self.assertEqual(
                    event["reviewed_granularity"], expected["granularity"]
                )
                self.assertEqual(
                    contract["canonical_event"]["date_text"],
                    expected["date_text"],
                )
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["confidence"], expected["confidence"])
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
                winners = {
                    str(participant["entity_id"])
                    for participant in event["participants"]
                    if str(participant["termination"]).endswith("victory")
                }
                losers = {
                    str(participant["entity_id"])
                    for participant in event["participants"]
                    if str(participant["termination"]).endswith("defeat")
                }
                self.assertEqual(winners, expected["winner"])
                self.assertEqual(losers, expected["loser"])
                self.assertEqual(Event.from_dict(event).track, "tactical")

    def test_location_quarantine_is_local_complete_and_country_preserving(self):
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_YAQUI_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS, set())
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event.get("modern_location_country"), "Mexico")
            self.assertIn("location_provenance", event)
            reason = lane.WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(reason["retained_country"], "Mexico")
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_duplicate_audits_and_current_integration_are_zero_overlap(self):
        self.assertEqual(lane.WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(lane.WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(
            set(lane.WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_YAQUI_RESERVED_IDS,
        )
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_event_boundaries": 3,
                "cross_lane_dispositions": 3,
                "existing_release_duplicate_dispositions": 0,
                "hced_duplicate_dispositions": 0,
                "hced_probable_twins": 0,
                "integration_dispositions": 6,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
                "release_probable_twins": 0,
            },
        )

    def test_release_overlap_is_all_or_none(self):
        actual_overlap = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_YAQUI_CONTRACT_IDS
        }
        self.assertIn(
            actual_overlap,
            (set(), set(lane.WAVE8_YAQUI_CONTRACT_IDS)),
        )
        self.assertEqual(
            lane.validate_wave8_yaqui_funnel(
                self.funnel,
                self.release_events,
            )["release_lane_overlap"],
            len(actual_overlap),
        )

        _, _, stripped = self._installed()
        full = copy.deepcopy(stripped)
        for candidate_id in sorted(lane.WAVE8_YAQUI_CONTRACT_IDS):
            full.append(
                {
                    "id": f"integrated-{candidate_id}",
                    "name": f"integrated owner for {candidate_id}",
                    "year": 1886,
                    "hced_candidate_id": candidate_id,
                }
            )
        self.assertEqual(
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                full,
            )["release_lane_overlap"],
            3,
        )
        with self.assertRaisesRegex(ValueError, "release overlap is partial"):
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                full[:-1],
            )

    def test_probable_twins_and_terminal_exclusion_leak_fail_closed(self):
        _, _, existing = self._installed()
        fake_hced = copy.deepcopy(self.hced_rows)
        fake_hced.append(
            {
                "candidate_id": "hced-future-anil-twin",
                "name": "Battle of El Anil",
                "year_best": 1886,
                "side_1_raw": "Unrelated actor A",
                "side_2_raw": "Unrelated actor B",
                "war_names": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "probable HCED duplicate"):
            lane.validate_wave8_yaqui_integration_dispositions(
                fake_hced,
                self.iwbd_rows,
                existing,
            )

        fake_iwbd = copy.deepcopy(self.iwbd_rows)
        fake_iwbd.append(
            {
                "candidate_id": "iwbd-future-buatachive-twin",
                "name": "Battle of Buatachive",
                "start_date": "1886-05-09",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                fake_iwbd,
                existing,
            )

        fake_release = copy.deepcopy(existing)
        fake_release.append(
            {
                "id": "future-tambor-twin",
                "name": "Battle of Cerro del Tambor",
                "year": 1740,
                "hced_candidate_id": "hced-future-tambor-twin",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable release duplicate"):
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                fake_release,
            )

        exclusion_leak = copy.deepcopy(existing)
        exclusion_leak.append(
            {
                "id": "invented-bacum-result",
                "name": "Bacum church massacre",
                "year": 1868,
                "hced_candidate_id": "hced-Bacum1868-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "Bacum massacre was rated"):
            lane.validate_wave8_yaqui_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                exclusion_leak,
            )

    def test_row_tamper_and_missing_entity_fail_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in tampered
            if row.get("candidate_id") == "hced-Buatachive1886-1"
        )
        target["massacre_raw"] = "Yes"
        with self.assertRaisesRegex(ValueError, "source semantics changed"):
            lane.validate_wave8_yaqui_queue_contracts(tampered)

        entities, _, existing = self._installed()
        entities.pop(BUATACHIVE_YAQUI)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_yaqui_contracts(
                self.hced_rows,
                entities,
                existing,
            )

    def test_promotion_and_installers_are_deterministic_and_collision_safe(self):
        entities, sources, existing = self._installed()
        hced_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        sources_before = copy.deepcopy(sources)
        existing_before = copy.deepcopy(existing)
        first = lane.promote_wave8_yaqui_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        second = lane.promote_wave8_yaqui_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(first, second)
        self.assertEqual(self.hced_rows, hced_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(sources, sources_before)
        self.assertEqual(existing, existing_before)

        lane.install_wave8_yaqui_entities(entities)
        lane.install_wave8_yaqui_sources(sources)
        self.assertEqual(entities, entities_before)
        self.assertEqual(sources, sources_before)

        bad_entities = {
            ANIL_YAQUI: {"id": ANIL_YAQUI, "name": "collision"}
        }
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_yaqui_entities(bad_entities)
        first_source_id = lane.WAVE8_YAQUI_SOURCES[0]["id"]
        bad_sources = {
            first_source_id: {"id": first_source_id, "title": "collision"}
        }
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_yaqui_sources(bad_sources)

    def test_signature_counts_cohorts_dispositions_and_metadata_are_pinned(self):
        self.assertNotEqual(lane.WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE, "__PENDING__")
        self.assertEqual(
            lane.wave8_yaqui_audit_signature(),
            lane.WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE,
        )
        expected_counts = {
            "adjacent_literal_labels_audited": 8,
            "country_quarantine_additions": 0,
            "cross_event_boundaries": 3,
            "cross_lane_dispositions": 3,
            "engagement_events": 3,
            "existing_release_duplicate_dispositions": 0,
            "hced_duplicate_dispositions": 0,
            "holds": 0,
            "integration_dispositions": 6,
            "iwbd_duplicate_dispositions": 0,
            "iwbd_zero_overlap_candidates": 4,
            "new_entities": 6,
            "new_sources": 9,
            "newly_rated_events": 3,
            "outcome_overrides": 0,
            "point_quarantine_additions": 3,
            "promotion_contracts": 3,
            "reviewed_hced_rows": 4,
            "scope_audits": 4,
            "sole_blocker_rows": 4,
            "terminal_exclusions": 1,
            "touched_hced_rows": 4,
            "war_labels_audited": 3,
            "war_rows_audited": 4,
        }
        self.assertEqual(lane.wave8_yaqui_counts(), expected_counts)
        self.assertEqual(
            lane.wave8_yaqui_cohort_counts(),
            {
                "cajeme_campaign_1886": 2,
                "yaqui_mayo_revolt_1740": 1,
                "yaqui_war_1867_1868": 1,
            },
        )
        self.assertEqual(
            lane.wave8_yaqui_row_dispositions(),
            {
                "hced-Anil1886-1": "promote",
                "hced-Bacum1868-1": "terminal_exclusion",
                "hced-Buatachive1886-1": "promote",
                "hced-Mount Tambor1740-1": "promote",
            },
        )
        metadata = lane.wave8_yaqui_metadata()
        self.assertEqual(metadata["counts"], expected_counts)
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
