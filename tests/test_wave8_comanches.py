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
from military_elo.promotion.wave8_comanche import (
    WAVE8_COMANCHE_CONTRACTS,
    WAVE8_COMANCHE_HOLD_IDS,
    WAVE8_COMANCHE_RESERVED_IDS,
)
from military_elo.promotion.wave8_comanches import (
    WAVE8_COMANCHES_CONTRACT_IDS,
    WAVE8_COMANCHES_CONTRACTS,
    WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHES_ENTITIES,
    WAVE8_COMANCHES_EXCLUSION_IDS,
    WAVE8_COMANCHES_EXCLUSIONS,
    WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS,
    WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE,
    WAVE8_COMANCHES_HCED_ZERO_OVERLAP_AUDIT,
    WAVE8_COMANCHES_HOLD_IDS,
    WAVE8_COMANCHES_HOLDS,
    WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS,
    WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_COMANCHES_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS,
    WAVE8_COMANCHES_NONPROMOTIONS,
    WAVE8_COMANCHES_OUTCOME_OVERRIDES,
    WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS,
    WAVE8_COMANCHES_RESERVED_IDS,
    WAVE8_COMANCHES_ROW_HASHES,
    WAVE8_COMANCHES_SOURCES,
    WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
    WAVE8_COMANCHES_TERMINAL_EXCLUSIONS,
    install_wave8_comanches_entities,
    install_wave8_comanches_sources,
    promote_wave8_comanches_contracts,
    validate_wave8_comanches_integration_dispositions,
    validate_wave8_comanches_queue_contracts,
    wave8_comanches_audit_signature,
    wave8_comanches_cohort_counts,
    wave8_comanches_counts,
    wave8_comanches_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_comanches_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "ba1385c8e70600c1768673e924e342d050a513b874e65994c01deffeb55a9953"
)

EXPECTED_RAW_HASHES = {
    "hced-Antelope Hills1858-1": (
        "1f99fa8fcf0f3b619bebd5ed703e0bb4b2b33cb566da14a88da0365c0f7f9cc5"
    ),
    "hced-Bandera Pass1841-1": (
        "cf2f183c29b15cdc78593adb1fb173582db33229264ca8e9d416bb89b1755039"
    ),
    "hced-Blanco Canyon1871-1": (
        "1dbaf68b8632e8c3d7bfa17852daf9d29f31ebb9a6235b0decfa028c6be4d006"
    ),
    "hced-Brushy Creek1839-1": (
        "555b4e888449b4a2e9453f7e5bfcc0df23f1082d9b61579afa6eb903da3fd919"
    ),
}

EXPECTED_PARTICIPANTS = {
    "hced-Antelope Hills1858-1": (
        {
            "ford_indigenous_allied_force_antelope_hills_1858",
            "ford_texas_ranger_force_antelope_hills_1858",
        },
        {"comanche_fighting_forces_little_robe_creek_1858"},
    ),
    "hced-Brushy Creek1839-1": (
        {"texas_ranger_militia_force_brushy_creek_1839"},
        {"comanche_raiding_party_brushy_creek_1839"},
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


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_COMANCHES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_COMANCHES_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_COMANCHES_HOLDS,
        "integration_dispositions": WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_COMANCHES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS
        ),
        "related_singular_lane_dispositions": (
            WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS
        ),
        "row_hashes": WAVE8_COMANCHES_ROW_HASHES,
        "sources": WAVE8_COMANCHES_SOURCES,
        "terminal_exclusions": WAVE8_COMANCHES_TERMINAL_EXCLUSIONS,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Wave8ComanchesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "comanches"
            or normalize_label(row.get("side_2_raw")) == "comanches"
        ]

    def _installed(self) -> tuple[dict, dict]:
        lane_entity_ids = {str(entity["id"]) for entity in WAVE8_COMANCHES_ENTITIES}
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(source["id"]) for source in WAVE8_COMANCHES_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        install_wave8_comanches_entities(entities)
        install_wave8_comanches_sources(sources)
        return entities, sources

    def _events(self, existing_events=None) -> list[dict]:
        entities, _ = self._installed()
        existing = (
            [
                copy.deepcopy(event)
                for event in self.release_events
                if event.get("hced_candidate_id")
                not in WAVE8_COMANCHES_CONTRACT_IDS
                and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
            ]
            if existing_events is None
            else copy.deepcopy(existing_events)
        )
        return promote_wave8_comanches_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_funnel_and_queue_lock_the_complete_four_row_exact_cohort(self) -> None:
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS, exact_ids)
        self.assertEqual(WAVE8_COMANCHES_RESERVED_IDS, exact_ids)

        historical_funnel = {
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": FUNNEL_CANDIDATE_ID_SHA256,
                    "label": "comanches",
                    "sole_blocker_events": 4,
                }
            ],
            "row_label_data": [
                {
                    "blocker_labels": ["comanches"],
                    "candidate_id": candidate_id,
                }
                for candidate_id in sorted(EXPECTED_RAW_HASHES)
            ],
        }
        funnel_rows = {
            str(row["candidate_id"]): row
            for row in historical_funnel["row_label_data"]
            if "comanches" in row.get("blocker_labels", [])
        }
        self.assertEqual(set(funnel_rows), exact_ids)
        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(exact_ids))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        label_rows = [
            row
            for row in historical_funnel["labels"]
            if row.get("label") == "comanches"
        ]
        self.assertEqual(len(label_rows), 1)
        self.assertEqual(label_rows[0]["sole_blocker_events"], 4)
        self.assertEqual(
            label_rows[0]["event_candidate_id_sha256"],
            FUNNEL_CANDIDATE_ID_SHA256,
        )

        self.assertFalse(
            any(
                row.get("label") == "comanches"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Comanches lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id")) in exact_ids
                or "comanches" in row.get("blocker_labels", [])
                for row in self.funnel.get("row_label_data", [])
            ),
            "adjudicated Comanches rows must not remain in the live funnel row data",
        )

    def test_row_hashes_and_all_four_dispositions_fail_closed(self) -> None:
        self.assertEqual(WAVE8_COMANCHES_ROW_HASHES, EXPECTED_RAW_HASHES)
        self.assertEqual(
            validate_wave8_comanches_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                expected_hash,
            )
            changed = copy.deepcopy(self.hced_rows)
            next(
                row for row in changed if row["candidate_id"] == candidate_id
            )["name"] += " tampered"
            with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                validate_wave8_comanches_queue_contracts(changed)

    def test_signature_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(_independent_signature(), WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_comanches_audit_signature(),
            WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_comanches_counts(),
            {
                "country_quarantine_additions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 5,
                "new_sources": 11,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "singular_lane_owned_rows": 6,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_comanches_cohort_counts(),
            {
                "antelope_hills_expedition_1858": 1,
                "brushy_creek_running_engagement_1839": 1,
            },
        )

    def test_sources_and_entities_are_schema_valid_and_strictly_bounded(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_COMANCHES_SOURCES}
        self.assertEqual(len(source_by_id), 11)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_COMANCHES_SOURCES}),
            11,
        )
        for source in WAVE8_COMANCHES_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))

        forbidden = {
            "comanche",
            "comanches",
            "comanche indians",
            "comanche nation",
            "texas",
            "united states",
        }
        self.assertEqual(len(WAVE8_COMANCHES_ENTITIES), 5)
        for entity in WAVE8_COMANCHES_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertTrue(entity["kind"].startswith("event_bounded_"))
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn(normalize_label(entity["name"]), forbidden)
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources = self._installed()
        install_wave8_comanches_entities(entities)
        install_wave8_comanches_sources(sources)
        for entity in WAVE8_COMANCHES_ENTITIES:
            self.assertEqual(entities[entity["id"]], entity)
        for source in WAVE8_COMANCHES_SOURCES:
            self.assertEqual(sources[source["id"]], source)

    def test_antelope_and_brushy_have_direct_independent_outcome_evidence(self) -> None:
        self.assertEqual(
            WAVE8_COMANCHES_CONTRACT_IDS,
            {"hced-Antelope Hills1858-1", "hced-Brushy Creek1839-1"},
        )
        source_by_id = {str(source["id"]): source for source in WAVE8_COMANCHES_SOURCES}
        expected = {
            "hced-Antelope Hills1858-1": (
                "Battle of the Antelope Hills (Little Robe Creek)",
                "12 May 1858",
                "engagement_series",
            ),
            "hced-Brushy Creek1839-1": (
                "Battle of Brushy Creek",
                "25 February 1839",
                "running_engagement",
            ),
        }
        for candidate_id, contract in WAVE8_COMANCHES_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["granularity"],
                ),
                expected[candidate_id],
            )
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])
            outcome_ids = contract["outcome_source_ids"]
            self.assertGreaterEqual(len(outcome_ids), 2)
            self.assertEqual(
                set(contract["outcome_source_family_ids"]),
                {source_by_id[item]["source_family_id"] for item in outcome_ids},
            )
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
        self.assertEqual(WAVE8_COMANCHES_OUTCOME_OVERRIDES, {})

    def test_blanco_canyon_is_held_without_inventing_a_draw(self) -> None:
        self.assertEqual(WAVE8_COMANCHES_HOLD_IDS, {"hced-Blanco Canyon1871-1"})
        hold = WAVE8_COMANCHES_HOLDS["hced-Blanco Canyon1871-1"]
        self.assertEqual(
            hold["hold_category"],
            "compound_action_without_unique_tactical_winner",
        )
        self.assertEqual(len(hold["documented_components"]), 4)
        self.assertIn("not converted to a draw", hold["hold_reason"])
        self.assertIn("successfully stampeded", hold["hold_reason"])
        self.assertIn("forced the warriors to withdraw", hold["hold_reason"])
        for key in (
            "result_type",
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
        ):
            self.assertNotIn(key, hold)

    def test_bandera_pass_is_terminally_excluded_as_unverifiable(self) -> None:
        self.assertEqual(
            WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
            {"hced-Bandera Pass1841-1"},
        )
        self.assertIs(WAVE8_COMANCHES_EXCLUSIONS, WAVE8_COMANCHES_TERMINAL_EXCLUSIONS)
        self.assertEqual(WAVE8_COMANCHES_EXCLUSION_IDS, {"hced-Bandera Pass1841-1"})
        exclusion = WAVE8_COMANCHES_TERMINAL_EXCLUSIONS[
            "hced-Bandera Pass1841-1"
        ]
        self.assertEqual(
            exclusion["exclusion_category"],
            "unverifiable_legend_and_conflicting_year",
        )
        self.assertIn("no memoir, official report", exclusion["exclusion_reason"])
        self.assertIn("1842", exclusion["exclusion_reason"])
        self.assertEqual(
            exclusion["canonical_event"]["date_precision"],
            "conflicting_year",
        )
        for key in (
            "result_type",
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
        ):
            self.assertNotIn(key, exclusion)
        self.assertEqual(
            set(WAVE8_COMANCHES_NONPROMOTIONS),
            WAVE8_COMANCHES_HOLD_IDS | WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
        )

    def test_plural_and_singular_lanes_have_explicit_disjoint_ownership(self) -> None:
        self.assertTrue(
            WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS.isdisjoint(
                WAVE8_COMANCHE_RESERVED_IDS
            )
        )
        self.assertEqual(
            set(WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS),
            set(WAVE8_COMANCHE_RESERVED_IDS),
        )
        for candidate_id, disposition in (
            WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS.items()
        ):
            self.assertEqual(
                disposition["owner_module"],
                "military_elo.promotion.wave8_comanche",
            )
            expected = (
                "held_by_singular_lane"
                if candidate_id in WAVE8_COMANCHE_HOLD_IDS
                else "promoted_by_singular_lane"
            )
            self.assertEqual(disposition["owner_status"], expected)

        plural_keys = {
            (
                contract["canonical_event"]["year_low"],
                normalize_label(contract["canonical_event"]["name"]),
            )
            for contract in WAVE8_COMANCHES_CONTRACTS.values()
        }
        singular_keys = {
            (
                contract["canonical_event"]["year_low"],
                normalize_label(contract["canonical_event"]["name"]),
            )
            for contract in WAVE8_COMANCHE_CONTRACTS.values()
        }
        self.assertTrue(plural_keys.isdisjoint(singular_keys))

    def test_direct_construction_emits_only_two_schema_valid_victories(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_COMANCHES_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            contract = WAVE8_COMANCHES_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                event["reviewed_granularity"],
                contract["canonical_event"]["granularity"],
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
            self.assertEqual((winners, losers), EXPECTED_PARTICIPANTS[candidate_id])
            self.assertNotIn(
                "inconclusive_engagement",
                {item["termination"] for item in event["participants"]},
            )

    def test_local_quarantines_withhold_bad_points_and_retain_country(self) -> None:
        point_object = HCED_POINT_QUARANTINE_IDS
        country_object = HCED_COUNTRY_QUARANTINE_IDS
        point_snapshot = frozenset(HCED_POINT_QUARANTINE_IDS)
        country_snapshot = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
            WAVE8_COMANCHES_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_COMANCHES_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            wave8_comanches_location_quarantine_additions(),
            {
                "country": WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, point_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, country_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), point_snapshot)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), country_snapshot)

    def test_iwbd_hced_and_release_duplicate_audits_are_zero(self) -> None:
        self.assertIs(
            WAVE8_COMANCHES_HCED_ZERO_OVERLAP_AUDIT,
            WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT,
        )
        self.assertEqual(
            set(WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_comanches_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
                "singular_lane_owned_rows": 6,
            },
        )

    def test_integration_guard_rejects_new_twins_in_each_input(self) -> None:
        fake_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-new-antelope-twin",
                "name": "Little Robe Creek",
                "year_best": 1858,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed HCED twin"):
            validate_wave8_comanches_integration_dispositions(
                fake_hced,
                self.iwbd_rows,
                self.release_events,
            )

        fake_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-new-brushy-twin",
                "name": "Battle of Brushy Creek",
                "start_date": "1839-02-25",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed IWBD twin"):
            validate_wave8_comanches_integration_dispositions(
                self.hced_rows,
                fake_iwbd,
                self.release_events,
            )

        fake_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "new_blanco_twin",
                "name": "Battle of Blanco Canyon",
                "year": 1871,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_comanches_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                fake_release,
            )

    def test_promotion_rejects_existing_candidate_and_name_year_duplicates(self) -> None:
        duplicate_candidate = {
            "id": "already-owned",
            "name": "Unrelated",
            "year": 1858,
            "hced_candidate_id": "hced-Antelope Hills1858-1",
        }
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            self._events([duplicate_candidate])

        duplicate_name = {
            "id": "already-named",
            "name": "Battle of Brushy Creek",
            "year": 1839,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            self._events([duplicate_name])

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_COMANCHES_CONTRACT_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        promotion = self.release_metadata.get("promotion", {})
        if "accepted_wave8_comanches_hced_events" not in promotion:
            self.assertEqual(integrated, [])
            return
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            WAVE8_COMANCHES_CONTRACT_IDS,
        )
        self.assertEqual(len(integrated), len(WAVE8_COMANCHES_CONTRACT_IDS))
        self.assertEqual(
            len({str(event["id"]) for event in integrated}),
            len(WAVE8_COMANCHES_CONTRACT_IDS),
        )
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in integrated)
        )
        for event in integrated:
            Event.from_dict(event)
        self.assertEqual(promotion["accepted_wave8_comanches_hced_events"], 2)
        self.assertEqual(
            promotion["wave8_comanches_candidate_ids"],
            sorted(WAVE8_COMANCHES_CONTRACT_IDS),
        )


if __name__ == "__main__":
    unittest.main()
