import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_murids as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_murids_"

RUSSIAN_EMPIRE = "russian_empire"
GHAZI_IMAMATE = "dagestani_imamate_ghazi_muhammad_1829_1832"
SHAMIL_IMAMATE = "caucasian_imamate_shamil_1834_1859"


EXPECTED_RAW_HASHES = {
    "hced-Darghiyya1842-1": (
        "52e36312d55cd70376d75d7f778a8c4aa8b78ed7c6e05bb1e616934d1b23bc57"
    ),
    "hced-Darghiyya1845-1": (
        "960268777a79c16d34cf5d2fcff751f7d41036594faf3c59c2be3ceffe5ff80e"
    ),
    "hced-Gimrah1832-1": (
        "ab038040242931609ed8d2784a32fbd7ff129266a68ad7c84da298a00ba7db2b"
    ),
    "hced-Gunib1859-1": (
        "cdf06a3969b21eac601427b0a2ec2be893a081642b4009b1cb80b28fd4b9abc2"
    ),
}


EXPECTED_RAW_ROWS = {
    "hced-Gimrah1832-1": {
        "name": "Gimrah",
        "side_1": "Russia",
        "side_2": "Murids",
        "winner": "Russia",
        "loser": "Murids",
        "year": 1832,
        "point": [46.8402047, 42.7573939],
        "country": "Russia",
    },
    "hced-Darghiyya1842-1": {
        "name": "Darghiyya",
        "side_1": "Murids",
        "side_2": "Russia",
        "winner": "Murids",
        "loser": "Russia",
        "year": 1842,
        "point": [46.0937628, 42.9629516],
        "country": "Russia",
    },
    "hced-Darghiyya1845-1": {
        "name": "Darghiyya",
        "side_1": "Murids",
        "side_2": "Russia",
        "winner": "Murids",
        "loser": "Russia",
        "year": 1845,
        "point": [46.0937628, 42.9629516],
        "country": "Russia",
    },
    "hced-Gunib1859-1": {
        "name": "Gunib",
        "side_1": "Russia",
        "side_2": "Murids",
        "winner": "Russia",
        "loser": "Murids",
        "year": 1859,
        "point": [46.9626296, 42.3861283],
        "country": "Russia",
    },
}


EXPECTED_EVENTS = {
    "hced-Gimrah1832-1": {
        "name": "Assault of Gimry",
        "event_type": "engagement",
        "granularity": "fortified_village_assault",
        "winner": {RUSSIAN_EMPIRE},
        "loser": {GHAZI_IMAMATE},
    },
    "hced-Darghiyya1842-1": {
        "name": "Ichkeria Expedition toward Dargo (1842)",
        "event_type": "campaign",
        "granularity": "multi_day_operational_expedition",
        "winner": {SHAMIL_IMAMATE},
        "loser": {RUSSIAN_EMPIRE},
    },
    "hced-Darghiyya1845-1": {
        "name": "Dargo Expedition (1845)",
        "event_type": "campaign",
        "granularity": "multi_week_operational_expedition",
        "winner": {SHAMIL_IMAMATE},
        "loser": {RUSSIAN_EMPIRE},
    },
    "hced-Gunib1859-1": {
        "name": "Assault and surrender of Gunib",
        "event_type": "engagement",
        "granularity": "blockade_assault_and_capitulation",
        "winner": {RUSSIAN_EMPIRE},
        "loser": {SHAMIL_IMAMATE},
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


class Wave8MuridsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "murids"
            or normalize_label(row.get("side_2_raw")) == "murids"
        ]

    def _installed(self):
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_MURIDS_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_MURIDS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_murids_entities(entities)
        lane.install_wave8_murids_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_murids_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_hashes_and_funnel_are_pinned(self) -> None:
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, lane.WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS)
        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(exact_ids))
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(digest, lane.WAVE8_MURIDS_EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(
            digest,
            lane.WAVE8_MURIDS_FUNNEL_AUDIT["event_candidate_id_sha256"],
        )
        self.assertEqual(
            lane.validate_wave8_murids_funnel(self.funnel, self.release_events),
            {"events_touched": 4, "sole_blocker_events": 4},
        )

    def test_raw_rows_and_canonical_fingerprints_are_exact(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(lane.WAVE8_MURIDS_ROW_HASHES, EXPECTED_RAW_HASHES)
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), EXPECTED_RAW_HASHES[candidate_id])
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["side_1_raw"], expected["side_1"])
                self.assertEqual(row["side_2_raw"], expected["side_2"])
                self.assertEqual(row["winner_raw"], expected["winner"])
                self.assertEqual(row["loser_raw"], expected["loser"])
                self.assertEqual(row["year_best"], expected["year"])
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )
                self.assertEqual(row["modern_location_country"], expected["country"])
                self.assertTrue(row["winner_loser_complete"])

    def test_signature_counts_and_public_metadata_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_murids_audit_signature(),
            lane.WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE,
            "6b312e21d254917756958209cf5a136072231b88b9a3e52c2c2139849ae318d8",
        )
        counts = lane.wave8_murids_counts()
        expected_counts = {
            "reviewed_hced_rows": 4,
            "promotion_contracts": 4,
            "newly_rated_events": 4,
            "campaign_events": 2,
            "engagement_events": 2,
            "holds": 0,
            "terminal_exclusions": 0,
            "new_entities": 0,
            "required_existing_entities": 3,
            "new_sources": 9,
            "point_quarantine_additions": 4,
            "country_quarantine_additions": 0,
            "outcome_overrides": 0,
            "dagestan_lane_dispositions": 6,
            "adjacent_hced_dispositions": 3,
            "integration_dispositions": 9,
            "iwbd_duplicate_dispositions": 0,
            "existing_release_duplicate_dispositions": 0,
        }
        for key, value in expected_counts.items():
            self.assertEqual(counts[key], value, key)
        self.assertEqual(
            lane.wave8_murids_cohort_counts(),
            {
                "ghazi_muhammad_final_gimry_1832": 1,
                "shamil_dargo_operations_1842_1845": 2,
                "shamil_final_gunib_1859": 1,
            },
        )
        metadata = lane.wave8_murids_metadata()
        self.assertEqual(metadata["counts"], counts)
        self.assertEqual(metadata["row_dispositions"], {
            candidate_id: "promote"
            for candidate_id in sorted(EXPECTED_RAW_ROWS)
        })

    def test_sources_are_independent_canonical_and_model_valid(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_MURIDS_SOURCES
        }
        self.assertEqual(len(source_by_id), 9)
        self.assertEqual(
            len({source["source_family_id"] for source in source_by_id.values()}),
            9,
        )
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"], sorted(set(source["evidence_roles"]))
            )
        for candidate_id, contract in lane.WAVE8_MURIDS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                outcomes = contract["outcome_source_ids"]
                families = contract["outcome_source_family_ids"]
                self.assertGreaterEqual(len(outcomes), 2)
                self.assertGreaterEqual(len(families), 2)
                self.assertEqual(
                    families,
                    sorted(
                        {
                            source_by_id[source_id]["source_family_id"]
                            for source_id in outcomes
                        }
                    ),
                )
                self.assertTrue(
                    all(
                        "outcome" in source_by_id[source_id]["evidence_roles"]
                        for source_id in outcomes
                    )
                )

    def test_existing_regime_boundaries_and_continuity_firewalls_are_pinned(self) -> None:
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        self.assertEqual(
            lane.validate_wave8_murids_existing_entities(entities),
            {"new_entities": 0, "reused_time_bounded_entities": 3},
        )
        for entity_id in lane.WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS:
            Entity.from_dict(entities[entity_id])
        self.assertEqual(
            lane.WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS,
            {RUSSIAN_EMPIRE, GHAZI_IMAMATE, SHAMIL_IMAMATE},
        )
        for entity_id in (GHAZI_IMAMATE, SHAMIL_IMAMATE):
            self.assertIn(
                "no rating is inherited",
                entities[entity_id]["continuity_note"].casefold(),
            )
            self.assertFalse(entities[entity_id]["aliases"])

        changed = copy.deepcopy(entities)
        changed[SHAMIL_IMAMATE]["end_year"] = 1864
        with self.assertRaisesRegex(ValueError, "boundary changed"):
            lane.validate_wave8_murids_existing_entities(changed)
        changed = copy.deepcopy(entities)
        changed[GHAZI_IMAMATE]["aliases"] = ["Murids"]
        with self.assertRaisesRegex(ValueError, "generic alias"):
            lane.validate_wave8_murids_existing_entities(changed)
        changed = copy.deepcopy(entities)
        changed[SHAMIL_IMAMATE]["continuity_note"] = "continuous"
        with self.assertRaisesRegex(ValueError, "continuity firewall"):
            lane.validate_wave8_murids_existing_entities(changed)

    def test_entity_installer_is_an_intentional_noop(self) -> None:
        self.assertEqual(lane.WAVE8_MURIDS_ENTITIES, ())
        entities = {"sentinel": {"id": "sentinel"}}
        before = copy.deepcopy(entities)
        lane.install_wave8_murids_entities(entities)
        self.assertEqual(entities, before)

    def test_all_four_contracts_emit_with_exact_actors_and_results(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 4)
        by_id = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_id), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            with self.subTest(candidate_id=candidate_id):
                event = by_id[candidate_id]
                Event.from_dict(event)
                self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["event_type"], expected["event_type"])
                self.assertEqual(event["reviewed_granularity"], expected["granularity"])
                self.assertEqual(event["year"], EXPECTED_RAW_ROWS[candidate_id]["year"])
                winners = {
                    participant["entity_id"]
                    for participant in event["participants"]
                    if participant["side"] == "side_a"
                }
                losers = {
                    participant["entity_id"]
                    for participant in event["participants"]
                    if participant["side"] == "side_b"
                }
                self.assertEqual(winners, expected["winner"])
                self.assertEqual(losers, expected["loser"])
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["status"], "complete")

    def test_campaign_rows_preserve_operational_scope_and_nested_results(self) -> None:
        by_id = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        self.assertEqual(
            lane.WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS,
            {"hced-Darghiyya1842-1", "hced-Darghiyya1845-1"},
        )
        for candidate_id in lane.WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS:
            event = by_id[candidate_id]
            audit = lane.WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT[candidate_id]
            self.assertEqual(event["event_type"], "campaign")
            self.assertEqual(event["reviewed_granularity"], audit["audited_unit"])
            self.assertIn("operational campaign assertion", event["summary"])
            self.assertIn("no point battle", event["summary"])
            for participant in event["participants"]:
                if participant["side"] == "side_a":
                    self.assertEqual(participant["termination"], "campaign_victory")
                    self.assertEqual(
                        participant["result_class"], "operational_campaign_victory"
                    )
                else:
                    self.assertEqual(participant["termination"], "campaign_defeat")
                    self.assertEqual(
                        participant["result_class"], "operational_campaign_defeat"
                    )
        dargo = lane.WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT[
            "hced-Darghiyya1845-1"
        ]
        self.assertIn("temporary_russian_occupation", dargo["opposite_result_disposition"])
        self.assertIn("component", dargo["scope_note"])

    def test_engagement_rows_do_not_inherit_campaign_semantics(self) -> None:
        by_id = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        for candidate_id in {"hced-Gimrah1832-1", "hced-Gunib1859-1"}:
            event = by_id[candidate_id]
            self.assertEqual(event["event_type"], "engagement")
            self.assertNotIn("operational campaign assertion", event["summary"])
            self.assertEqual(
                {participant["termination"] for participant in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )

    def test_unknown_is_never_draw_and_no_outcome_is_overridden(self) -> None:
        self.assertFalse(lane.WAVE8_MURIDS_HOLDS)
        self.assertFalse(lane.WAVE8_MURIDS_TERMINAL_EXCLUSIONS)
        self.assertFalse(lane.WAVE8_MURIDS_OUTCOME_OVERRIDES)
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, contract in lane.WAVE8_MURIDS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(contract["result_type"], "win")
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                winner_side = int(contract["winner_side"])
                self.assertEqual(
                    rows[candidate_id]["winner_raw"],
                    rows[candidate_id][f"side_{winner_side}_raw"],
                )
                self.assertEqual(
                    rows[candidate_id]["loser_raw"],
                    rows[candidate_id][f"side_{3 - winner_side}_raw"],
                )

    def test_location_quarantine_withholds_all_points_but_retains_country(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(
            lane.wave8_murids_location_quarantine_additions(),
            {
                "point": lane.WAVE8_MURIDS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            set(lane.WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_MURIDS_CONTRACT_IDS,
        )
        for review in lane.WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS.values():
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(review["retained_country"], "Russia")
            self.assertTrue(review["reason"])

        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Russia")
            self.assertIn("location_provenance", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_adjacent_literal_labels_and_dagestan_lane_are_exhaustively_audited(self) -> None:
        actual = {
            label: {
                str(row["candidate_id"])
                for row in self.hced_rows
                if normalize_label(row.get("side_1_raw")) == label
                or normalize_label(row.get("side_2_raw")) == label
            }
            for label in lane.WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY
        }
        expected = {
            label: set(candidate_ids)
            for label, candidate_ids in (
                lane.WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY.items()
            )
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(lane.WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS), 6)
        self.assertEqual(len(lane.WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS), 3)
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for dispositions in (
            lane.WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS,
            lane.WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS,
        ):
            for candidate_id, disposition in dispositions.items():
                with self.subTest(candidate_id=candidate_id):
                    self.assertEqual(
                        canonical_hced_row_sha256(by_id[candidate_id]),
                        disposition["raw_row_sha256"],
                    )
        self.assertTrue(
            lane.WAVE8_MURIDS_CONTRACT_IDS.isdisjoint(
                lane.WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS
            )
        )

    def test_existing_dagestan_and_anapa_ownership_is_pinned(self) -> None:
        by_event_id = {
            str(event["id"]): event for event in self.release_events
        }
        for candidate_id, disposition in (
            lane.WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS.items()
        ):
            event = by_event_id[disposition["owner_event_id"]]
            self.assertEqual(event["hced_candidate_id"], candidate_id)
            self.assertTrue(str(event["id"]).startswith("hced_wave8_dagestan_"))
        anapa = lane.WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS[
            "hced-Anapa1789-1"
        ]
        self.assertEqual(
            by_event_id[anapa["owner_event_id"]]["hced_candidate_id"],
            "hced-Anapa1789-1",
        )

    def test_clean_integration_audit_finds_no_iwbd_or_release_duplicate(self) -> None:
        result = lane.validate_wave8_murids_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(result["dagestan_lane_dispositions"], 6)
        self.assertEqual(result["adjacent_hced_dispositions"], 3)
        self.assertEqual(result["integration_dispositions"], 9)
        self.assertEqual(result["iwbd_probable_twins"], 0)
        self.assertIn(result["release_lane_overlap"], {0, 4})

    def test_iwbd_alternate_name_collision_fails_closed(self) -> None:
        injected = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-injected-gunib",
                "name": "Siege of Ghunib",
                "start_date": "1859-08-25",
                "end_date": "1859-08-25",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_murids_integration_dispositions(
                self.hced_rows,
                injected,
                self.release_events,
            )

    def test_existing_release_alternate_name_collision_fails_closed(self) -> None:
        injected = [
            *copy.deepcopy(self.release_events),
            {
                "id": "injected_dargo_duplicate",
                "name": "Battle of Dargo",
                "year": 1845,
                "end_year": 1845,
                "aliases": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_murids_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                injected,
            )

    def test_release_overlap_is_all_or_none_and_lane_owned(self) -> None:
        overlap = {
            str(event["hced_candidate_id"]): event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_MURIDS_CONTRACT_IDS
        }
        self.assertIn(set(overlap), (set(), set(lane.WAVE8_MURIDS_CONTRACT_IDS)))
        for event in overlap.values():
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))

        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_MURIDS_SOURCES
        }
        release_source_ids = {
            str(source["id"]) for source in self.release_sources
        }
        self.assertIn(
            lane_source_ids & release_source_ids,
            (set(), lane_source_ids),
        )

        if overlap:
            partial = [
                event
                for event in self.release_events
                if event.get("hced_candidate_id")
                != next(iter(lane.WAVE8_MURIDS_CONTRACT_IDS))
            ]
        else:
            partial = [*copy.deepcopy(self.release_events), self._events()[0]]
        with self.assertRaisesRegex(ValueError, "overlap is partial|overlap is partial|overlap is partial"):
            lane.validate_wave8_murids_funnel(self.funnel, partial)

    def test_queue_drift_missing_duplicate_and_extra_exact_rows_fail_closed(self) -> None:
        target_id = "hced-Darghiyya1842-1"
        target_index = next(
            index
            for index, row in enumerate(self.hced_rows)
            if row.get("candidate_id") == target_id
        )

        changed = list(self.hced_rows)
        changed[target_index] = copy.deepcopy(changed[target_index])
        changed[target_index]["winner_raw"] = "Russia"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_murids_queue_contracts(changed)

        missing = [
            row for row in self.hced_rows if row.get("candidate_id") != target_id
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_murids_queue_contracts(missing)

        duplicated = [*self.hced_rows, copy.deepcopy(self.hced_rows[target_index])]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_murids_queue_contracts(duplicated)

        extra_row = copy.deepcopy(self.hced_rows[target_index])
        extra_row["candidate_id"] = "hced-new-murids-row"
        extra = [*self.hced_rows, extra_row]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_murids_queue_contracts(extra)

    def test_related_dagestan_row_drift_fails_closed(self) -> None:
        changed = list(self.hced_rows)
        index = next(
            index
            for index, row in enumerate(changed)
            if row.get("candidate_id") == "hced-Akhulgo1839-1"
        )
        changed[index] = copy.deepcopy(changed[index])
        changed[index]["name"] = "Changed Akhulgo"
        with self.assertRaisesRegex(ValueError, "related HCED row changed"):
            lane.validate_wave8_murids_integration_dispositions(
                changed,
                self.iwbd_rows,
                self.release_events,
            )

    def test_duplicate_raw_or_canonical_event_name_is_rejected(self) -> None:
        entities, _, existing = self._installed()
        raw_duplicate = [
            *existing,
            {"id": "raw_duplicate", "name": "Gimrah", "year": 1832},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_murids_contracts(
                self.hced_rows,
                entities,
                raw_duplicate,
            )
        canonical_duplicate = [
            *existing,
            {"id": "canonical_duplicate", "name": "Assault of Gimry", "year": 1832},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_murids_contracts(
                self.hced_rows,
                entities,
                canonical_duplicate,
            )

    def test_source_installation_is_complete_and_collision_safe(self) -> None:
        _, sources, _ = self._installed()
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_MURIDS_SOURCES
        }
        self.assertTrue(lane_source_ids <= set(sources))
        for source_id in lane_source_ids:
            Source.from_dict(sources[source_id])
        collision_id = next(iter(lane_source_ids))
        colliding = {collision_id: {"id": collision_id, "title": "wrong"}}
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_murids_sources(colliding)

    def test_funnel_drift_fails_but_post_integration_absence_is_allowed(self) -> None:
        changed = copy.deepcopy(self.funnel)
        record = next(
            item for item in changed["labels"] if item.get("label") == "murids"
        )
        record["events_touched"] = 5
        with self.assertRaisesRegex(ValueError, "funnel field changed"):
            lane.validate_wave8_murids_funnel(changed, [])

        integrated = copy.deepcopy(self.funnel)
        integrated["labels"] = [
            item for item in integrated["labels"] if item.get("label") != "murids"
        ]
        self.assertEqual(
            lane.validate_wave8_murids_funnel(integrated, self._events()),
            {"events_touched": 4, "sole_blocker_events": 4},
        )

    def test_promoter_requires_all_three_existing_identities(self) -> None:
        entities, _, existing = self._installed()
        for entity_id in lane.WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS:
            with self.subTest(entity_id=entity_id):
                changed = copy.deepcopy(entities)
                del changed[entity_id]
                with self.assertRaisesRegex(ValueError, "missing required existing entity"):
                    lane.promote_wave8_murids_contracts(
                        self.hced_rows,
                        changed,
                        existing,
                    )


if __name__ == "__main__":
    unittest.main()

