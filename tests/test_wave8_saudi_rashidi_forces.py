import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import _slug, normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_first_saudi import WAVE8_FIRST_SAUDI_RESERVED_IDS
from military_elo.promotion.wave8_saudi_rashidi_forces import (
    WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
    WAVE8_SAUDI_RASHIDI_CONTRACTS,
    WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES,
    WAVE8_SAUDI_RASHIDI_ENTITIES,
    WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS,
    WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE,
    WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_HOLD_IDS,
    WAVE8_SAUDI_RASHIDI_HOLDS,
    WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT,
    WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW,
    WAVE8_SAUDI_RASHIDI_NONPROMOTIONS,
    WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES,
    WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_RESERVED_IDS,
    WAVE8_SAUDI_RASHIDI_ROW_INVENTORY,
    WAVE8_SAUDI_RASHIDI_SOURCES,
    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS,
    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS,
    install_wave8_saudi_rashidi_entities,
    install_wave8_saudi_rashidi_sources,
    promote_wave8_saudi_rashidi_contracts,
    validate_wave8_saudi_rashidi_integration_dispositions,
    validate_wave8_saudi_rashidi_queue_contracts,
    wave8_saudi_rashidi_audit_signature,
    wave8_saudi_rashidi_cohort_counts,
    wave8_saudi_rashidi_counts,
    wave8_saudi_rashidi_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_saudi_rashidi_"
OWNED_LABELS = {"rashidis", "saudis", "saudis qasim"}

EXPECTED_NAMES = {
    "hced-Dilam1902-1": "Battle of Dilam",
    "hced-Hofuf1913-1": "Assault and capture of Hofuf",
    "hced-Kinzan1915-1": "Battle of Kanzan",
    "hced-Medina, Saudi Arabia1925-1": "Siege and surrender of Medina",
    "hced-Mulaydah1891-1": "Battle of al-Mulayda",
    "hced-Rawdhat al Muhanna1906-1": "Battle of Rawdat Muhanna",
    "hced-Riyadh1902-1": "Capture of Riyadh",
    "hced-Sabalah1929-1": "Battle of Sabilla",
    "hced-Turabah1919-1": "Battle of Turabah",
    "hced-Umm Urdhumah1929-1": "Battle of Umm Radhmah",
    "hced-Unayzah1904-1": "Assault and capture of Unayzah",
}

EXPECTED_PARTICIPANTS = {
    "hced-Dilam1902-1": {
        "ibn_rashid_dilam_force_1902",
        "ibn_saud_dilam_force_1902",
    },
    "hced-Hofuf1913-1": {
        "ibn_saud_hofuf_assault_force_1913",
        "ottoman_hofuf_garrison_1913",
    },
    "hced-Kinzan1915-1": {
        "dhaydan_ibn_hithlayn_ajman_force_kanzan_1915",
        "ibn_saud_kanzan_force_1915",
    },
    "hced-Medina, Saudi Arabia1925-1": {
        "hashemite_medina_garrison_1925",
        "ibn_saud_medina_siege_force_1925",
    },
    "hced-Mulaydah1891-1": {
        "abd_al_rahman_qassim_coalition_mulayda_1891",
        "muhammad_ibn_abdullah_rashidi_army_mulayda_1891",
    },
    "hced-Rawdhat al Muhanna1906-1": {
        "abdulaziz_ibn_mutaib_rashidi_force_rawdat_muhanna_1906",
        "ibn_saud_rawdat_muhanna_force_1906",
    },
    "hced-Riyadh1902-1": {
        "ajlan_rashidi_riyadh_garrison_1902",
        "ibn_saud_riyadh_raiding_party_1902",
    },
    "hced-Sabalah1929-1": {
        "faisal_sultan_rebel_ikhwan_sabilla_1929",
        "ibn_saud_loyalist_army_sabilla_1929",
    },
    "hced-Turabah1919-1": {
        "abdullah_hashemite_army_turabah_1919",
        "khalid_sultan_ikhwan_force_turabah_1919",
    },
    "hced-Umm Urdhumah1929-1": {
        "azaiyiz_mutair_ikhwan_force_umm_radhmah_1929",
        "ibn_musaid_loyal_shammar_force_umm_radhmah_1929",
    },
    "hced-Unayzah1904-1": {
        "ibn_saud_unayzah_assault_force_1904",
        "majid_ibn_hamoud_rashidi_unayzah_force_1904",
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


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_SAUDI_RASHIDI_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_label_boundaries": WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES,
        "entities": WAVE8_SAUDI_RASHIDI_ENTITIES,
        "first_saudi_ownership_audit": (
            WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT
        ),
        "hced_twin_dispositions": WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS,
        "holds": WAVE8_SAUDI_RASHIDI_HOLDS,
        "integration_dispositions": (
            WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": (
            WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_outside_lane_audit": WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT,
        "iwbd_zero_overlap_audit": (
            WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "label_ownership_audit": WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT,
        "location_review": WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW,
        "outcome_overrides": WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS
        ),
        "release_ownership_audit": WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT,
        "row_inventory": WAVE8_SAUDI_RASHIDI_ROW_INVENTORY,
        "sources": WAVE8_SAUDI_RASHIDI_SOURCES,
        "terminal_exclusions": WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class Wave8SaudiRashidiForcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }

    def _installed(self):
        entities = {item["id"]: copy.deepcopy(item) for item in self.release_entities}
        sources = {item["id"]: copy.deepcopy(item) for item in self.release_sources}
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
        ]
        install_wave8_saudi_rashidi_entities(entities)
        install_wave8_saudi_rashidi_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_saudi_rashidi_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_counts_cohorts_dispositions_and_signature_are_pinned(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_SAUDI_RASHIDI_CONTRACT_IDS),
                len(WAVE8_SAUDI_RASHIDI_HOLD_IDS),
                len(WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS),
            ),
            (11, 4, 1),
        )
        disposition_sets = (
            WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
            WAVE8_SAUDI_RASHIDI_HOLD_IDS,
            WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS,
        )
        for index, left in enumerate(disposition_sets):
            for right in disposition_sets[index + 1 :]:
                self.assertFalse(left & right)
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_RESERVED_IDS,
            WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(_independent_signature(), WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_saudi_rashidi_audit_signature(),
            WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_saudi_rashidi_cohort_counts(),
            {
                "hasa_and_wartime_consolidation_1913_1915": 2,
                "hijaz_expansion_1919_1925": 2,
                "ikhwan_rebellion_1929": 2,
                "riyadh_qassim_reconquest_1902_1906": 4,
                "second_saudi_rashidi_climax_1891": 1,
            },
        )
        self.assertEqual(
            wave8_saudi_rashidi_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_label_boundaries": 4,
                "exact_owned_labels": 3,
                "first_saudi_candidate_overlap": 0,
                "hced_twin_dispositions": 4,
                "holds": 4,
                "integration_dispositions": 16,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_outside_lane_rows": 1,
                "new_entities": 22,
                "new_sources": 14,
                "newly_rated_events": 11,
                "outcome_overrides": 2,
                "point_quarantine_additions": 11,
                "promotion_contracts": 11,
                "release_ownership_rows": 4,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 1,
            },
        )

    def test_exact_label_scope_and_funnel_inventory_are_complete(self) -> None:
        self.assertEqual(set(WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT), OWNED_LABELS)
        self.assertEqual(
            {
                label: len(audit["candidate_ids"])
                for label, audit in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items()
            },
            {"rashidis": 8, "saudis": 15, "saudis qasim": 1},
        )
        self.assertEqual(
            {
                label: audit["funnel_event_candidate_id_sha256"]
                for label, audit in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items()
            },
            {
                "rashidis": "02c7ad2ff436088c5d5c0ff4106af8f99fbcc4b7b91bd8f6f33886cdb16880a6",
                "saudis": "eaa1ab3a42b774324714a4c7c1edfffd4b2374b3204c66bf25459b09b83f39f0",
                "saudis qasim": "858031ba91aaf34bef903c02ac4ae649d5a1e3b5a57d9411e4f3d09d077940e1",
            },
        )
        self.assertEqual(
            {
                label: audit["sole_blocker_events"]
                for label, audit in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items()
            },
            {"rashidis": 0, "saudis": 3, "saudis qasim": 0},
        )
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT["saudis qasim"][
                "candidate_ids"
            ],
            ["hced-Mulaydah1891-1"],
        )
        self.assertTrue(
            WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT["saudis qasim"][
                "mechanically_necessary_variant"
            ]
        )
        exact_ids = {
            row["candidate_id"]
            for row in self.hced_rows
            if {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            & OWNED_LABELS
        }
        self.assertEqual(exact_ids, WAVE8_SAUDI_RASHIDI_RESERVED_IDS)

        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": (
                        "02c7ad2ff436088c5d5c0ff4106af8f99fbcc4b7b91bd8f6f33886cdb16880a6"
                    ),
                    "events_touched": 8,
                    "label": "rashidis",
                    "sole_blocker_events": 0,
                },
                {
                    "event_candidate_id_sha256": (
                        "eaa1ab3a42b774324714a4c7c1edfffd4b2374b3204c66bf25459b09b83f39f0"
                    ),
                    "events_touched": 15,
                    "label": "saudis",
                    "sole_blocker_events": 3,
                },
                {
                    "event_candidate_id_sha256": (
                        "858031ba91aaf34bef903c02ac4ae649d5a1e3b5a57d9411e4f3d09d077940e1"
                    ),
                    "events_touched": 1,
                    "label": "saudis qasim",
                    "sole_blocker_events": 0,
                },
            ],
            "row_label_data": [
                {
                    "blocker_labels": ["saudis"],
                    "candidate_id": "hced-Bukairiya1904-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": "saudis",
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Dilam1902-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Hail1921-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["saudis"],
                    "candidate_id": "hced-Hofuf1913-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": "saudis",
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Jirab1915-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Kinzan1915-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["hashemites", "saudis"],
                    "candidate_id": "hced-Medina, Saudi Arabia1925-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis qasim"],
                    "candidate_id": "hced-Mulaydah1891-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Rawdhat al Muhanna1906-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Riyadh1887-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["rashidis", "saudis"],
                    "candidate_id": "hced-Riyadh1902-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["ikhwan brotherhood", "saudis"],
                    "candidate_id": "hced-Sabalah1929-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["hashemites", "saudis"],
                    "candidate_id": "hced-Taif1924-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["hashemites", "saudis"],
                    "candidate_id": "hced-Turabah1919-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["ikhwan rebels", "saudis"],
                    "candidate_id": "hced-Umm Urdhumah1929-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["saudis"],
                    "candidate_id": "hced-Unayzah1904-1",
                    "greedy_eligible": True,
                    "sole_blocker_label": "saudis",
                },
            ],
        }
        funnel_by_id = {
            row["candidate_id"]: row
            for row in historical_funnel["row_label_data"]
        }
        funnel_labels = {row["label"]: row for row in historical_funnel["labels"]}
        for label, audit in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items():
            label_row = funnel_labels[label]
            self.assertEqual(
                label_row["event_candidate_id_sha256"],
                audit["funnel_event_candidate_id_sha256"],
            )
            self.assertEqual(label_row["events_touched"], audit["events_touched"])
            self.assertEqual(
                label_row["sole_blocker_events"],
                audit["sole_blocker_events"],
            )
        for candidate_id, audit in WAVE8_SAUDI_RASHIDI_ROW_INVENTORY.items():
            row = funnel_by_id[candidate_id]
            self.assertEqual(row["blocker_labels"], audit["blocker_labels"])
            self.assertEqual(row["greedy_eligible"], audit["greedy_eligible"])
            self.assertEqual(
                row["sole_blocker_label"],
                audit["sole_blocker_label"],
            )

        funnel_path = ROOT / "build/hced-unresolved-label-funnel.json"
        if funnel_path.exists():
            live_funnel = _json(funnel_path)
            self.assertFalse(
                any(
                    row.get("label") in OWNED_LABELS
                    for row in live_funnel.get("labels", [])
                ),
                "the completed Saudi-Rashidi lane must not remain unresolved",
            )
            self.assertFalse(
                any(
                    row.get("candidate_id") in WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
                    for row in live_funnel.get("row_label_data", [])
                ),
                "promoted Saudi-Rashidi candidates must not remain in the live funnel",
            )

    def test_raw_fingerprints_and_queue_validator_fail_closed(self) -> None:
        inventory = {
            **WAVE8_SAUDI_RASHIDI_CONTRACTS,
            **WAVE8_SAUDI_RASHIDI_NONPROMOTIONS,
        }
        self.assertEqual(set(inventory), WAVE8_SAUDI_RASHIDI_RESERVED_IDS)
        for candidate_id, disposition in inventory.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )
            self.assertEqual(
                disposition["raw_row_sha256"],
                WAVE8_SAUDI_RASHIDI_ROW_INVENTORY[candidate_id][
                    "raw_row_sha256"
                ],
            )
        self.assertEqual(
            validate_wave8_saudi_rashidi_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 11,
                "holds": 4,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 1,
            },
        )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Riyadh1902-1"
        )["winner_raw"] = "changed"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_saudi_rashidi_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Hail1921-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_saudi_rashidi_queue_contracts(missing)

        expanded = [
            *self.hced_rows,
            {
                "candidate_id": "hced-FutureSaudis1930-1",
                "name": "Future",
                "side_1_raw": "Saudis",
                "side_2_raw": "Other",
                "year_low": 1930,
                "year_high": 1930,
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            validate_wave8_saudi_rashidi_queue_contracts(expanded)

    def test_first_saudi_and_near_label_ownership_do_not_overlap(self) -> None:
        self.assertFalse(
            WAVE8_SAUDI_RASHIDI_RESERVED_IDS & WAVE8_FIRST_SAUDI_RESERVED_IDS
        )
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT[
                "imported_reserved_candidate_ids"
            ],
            sorted(WAVE8_FIRST_SAUDI_RESERVED_IDS),
        )
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT["target_overlap"],
            [],
        )
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES["house of saud"][
                "disposition"
            ],
            "owned_by_wave8_first_saudi",
        )
        self.assertEqual(
            WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES["saudi arabia"][
                "candidate_ids"
            ],
            ["hced-Hamad1920-1", "hced-Hudayda1934-1", "hced-Jahrah1920-1"],
        )
        self.assertNotIn("saudi arabia", WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT)
        self.assertNotIn("house of saud", WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT)

    def test_sources_are_independent_direct_and_exactly_consumed(self) -> None:
        source_by_id = {
            source["id"]: source for source in WAVE8_SAUDI_RASHIDI_SOURCES
        }
        self.assertEqual(len(source_by_id), 14)
        for source in WAVE8_SAUDI_RASHIDI_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["license"], "linked_reference")
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertIn("outcome", source["evidence_roles"])

        used = {
            source_id
            for entity in WAVE8_SAUDI_RASHIDI_ENTITIES
            for source_id in entity["source_ids"]
        }
        for disposition in (
            *WAVE8_SAUDI_RASHIDI_CONTRACTS.values(),
            *WAVE8_SAUDI_RASHIDI_NONPROMOTIONS.values(),
        ):
            used.update(disposition["evidence_refs"])
        self.assertEqual(used, set(source_by_id))

        for contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            families = contract["outcome_source_family_ids"]
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertGreaterEqual(len(families), 2)
            self.assertLessEqual(set(outcomes), set(contract["evidence_refs"]))
            self.assertEqual(
                families,
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in outcomes
                    }
                ),
            )

    def test_entities_are_event_bounded_without_generic_aliases(self) -> None:
        entity_ids = {entity["id"] for entity in WAVE8_SAUDI_RASHIDI_ENTITIES}
        self.assertEqual(entity_ids, set().union(*EXPECTED_PARTICIPANTS.values()))
        forbidden = {
            "house of saud",
            "rashidi",
            "rashidis",
            "saudi",
            "saudi arabia",
            "saudis",
        }
        for entity in WAVE8_SAUDI_RASHIDI_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertTrue(entity["kind"].startswith("event_bounded_"))
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertNotIn(normalize_label(entity["name"]), forbidden)
            self.assertNotIn(normalize_label(entity["id"]), forbidden)

        used = {
            entity_id
            for contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
        }
        self.assertEqual(used, entity_ids)

    def test_contracts_are_bounded_wins_and_overrides_are_explicit(self) -> None:
        self.assertEqual(set(EXPECTED_NAMES), WAVE8_SAUDI_RASHIDI_CONTRACT_IDS)
        for candidate_id, contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], EXPECTED_NAMES[candidate_id])
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(
                canonical["canonical_key"],
                f"{_slug(canonical['name'])}:{canonical['year_low']}:{canonical['year_high']}",
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])
            self.assertEqual(
                set(contract["side_1_entity_ids"])
                | set(contract["side_2_entity_ids"]),
                EXPECTED_PARTICIPANTS[candidate_id],
            )
        self.assertEqual(
            set(WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES),
            {"hced-Kinzan1915-1", "hced-Unayzah1904-1"},
        )
        self.assertEqual(
            {
                candidate_id
                for candidate_id, contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.items()
                if contract["source_outcome_override"]
            },
            set(WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES),
        )
        unayzah = WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES["hced-Unayzah1904-1"]
        self.assertEqual((unayzah["raw_winner_label"], unayzah["raw_loser_label"]), ("Draw", None))
        self.assertEqual(unayzah["reviewed_result"], "side_1_win")
        kanzan = WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES["hced-Kinzan1915-1"]
        self.assertEqual(kanzan["raw_side_1_label"], "Rashidis")
        self.assertIn("al-Ajman", kanzan["reason"])

    def test_holds_never_become_draws_and_hail_exclusion_has_proof(self) -> None:
        self.assertEqual(
            {item["hold_category"] for item in WAVE8_SAUDI_RASHIDI_HOLDS.values()},
            {
                "approach_battle_and_city_capture_boundary_conflict",
                "campaign_phase_and_outcome_conflict",
                "direct_source_outcome_conflict",
                "discrete_engagement_not_independently_located",
            },
        )
        forbidden = {
            "outcome_source_family_ids",
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        for hold in WAVE8_SAUDI_RASHIDI_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertFalse(hold["terminal_exclusion"])
            self.assertFalse(forbidden & set(hold))
            self.assertIn("unknown", hold["hold_reason"].casefold())
            self.assertIn("never converted to a draw", hold["hold_reason"].casefold())

        self.assertEqual(
            set(WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS),
            {"hced-Hail1921-1"},
        )
        hail = WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS["hced-Hail1921-1"]
        self.assertEqual(hail["disposition"], "terminal_exclusion")
        self.assertTrue(hail["terminal_exclusion"])
        self.assertIn("without a fight", hail["hold_reason"])
        self.assertIn("proof", hail["hold_reason"])
        self.assertFalse(forbidden & set(hail))

    def test_promoted_events_have_exact_participants_and_no_draws(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 11)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            contract = WAVE8_SAUDI_RASHIDI_CONTRACTS[candidate_id]
            self.assertEqual(event["name"], EXPECTED_NAMES[candidate_id])
            self.assertEqual(
                {participant["entity_id"] for participant in event["participants"]},
                EXPECTED_PARTICIPANTS[candidate_id],
            )
            self.assertTrue(
                all(
                    participant["result_class"] != "draw"
                    and participant["termination"] != "draw"
                    for participant in event["participants"]
                )
            )
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(event["status"], "complete")
            self.assertNotIn("saudis", {normalize_label(p["entity_id"]) for p in event["participants"]})

        by_id = {event["hced_candidate_id"]: event for event in events}
        unayzah_winner = next(
            participant
            for participant in by_id["hced-Unayzah1904-1"]["participants"]
            if participant["result_class"].endswith("victory")
        )
        self.assertEqual(
            unayzah_winner["entity_id"],
            "ibn_saud_unayzah_assault_force_1904",
        )
        kanzan_winner = next(
            participant
            for participant in by_id["hced-Kinzan1915-1"]["participants"]
            if participant["result_class"].endswith("victory")
        )
        self.assertEqual(
            kanzan_winner["entity_id"],
            "dhaydan_ibn_hithlayn_ajman_force_kanzan_1915",
        )

    def test_location_quarantine_is_local_and_preserves_country(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        expected = {
            "point": WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
            "country": frozenset(),
        }
        self.assertEqual(WAVE8_SAUDI_RASHIDI_LOCATION_QUARANTINE_ADDITIONS, expected)
        self.assertEqual(wave8_saudi_rashidi_location_quarantine_additions(), expected)
        events = self._events()
        for event in events:
            candidate_id = event["hced_candidate_id"]
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Saudi Arabia")
            self.assertIn("location_provenance", event)
            review = WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW[candidate_id]
            row = self.hced_by_id[candidate_id]
            self.assertEqual(review["raw_latitude"], row["latitude"])
            self.assertEqual(review["raw_longitude"], row["longitude"])
            self.assertEqual(
                review["point_disposition"],
                "quarantine_unproven_source_point",
            )

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_hced_iwbd_release_and_cross_label_twins_fail_closed(self) -> None:
        self.assertFalse(WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS)
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_label_boundaries": 4,
                "first_saudi_candidate_overlap": 0,
                "hced_twin_dispositions": 4,
                "integration_dispositions": 16,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_outside_lane_rows": 1,
                "iwbd_probable_twins": 0,
                "release_ownership_rows": 4,
                "release_probable_twins": 0,
                "released_target_candidates": 0,
            },
        )
        outside_id = "iwbd-125-48-872"
        outside = next(row for row in self.iwbd_rows if row["candidate_id"] == outside_id)
        self.assertEqual(
            hashlib.sha256(_canonical_json(outside).encode("utf-8")).hexdigest(),
            WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT[outside_id][
                "raw_row_sha256"
            ],
        )

        changed_iwbd = copy.deepcopy(self.iwbd_rows)
        next(row for row in changed_iwbd if row["candidate_id"] == outside_id)[
            "winner_raw"
        ] = "changed"
        with self.assertRaisesRegex(ValueError, "outside-lane IWBD fingerprint changed"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                changed_iwbd,
                self.release_events,
            )

        future_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-kanzan",
                "name": "Battle of Kanzan",
                "start_date": "1915-06-01",
                "end_date": "1915-06-01",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD twin"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                self.release_events,
            )

        future_hced = [
            *self.hced_rows,
            {
                "candidate_id": "hced-cross-label-sabilla",
                "name": "Battle of Sabilla",
                "side_1_raw": "Other A",
                "side_2_raw": "Other B",
                "year_low": 1929,
                "year_high": 1929,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed cross-label HCED twin"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                future_hced,
                self.iwbd_rows,
                self.release_events,
            )

        future_release = [
            *self.release_events,
            {"id": "future_unayzah", "name": "Unayzah", "year": 1904},
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed probable release twin"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

        changed_release = copy.deepcopy(self.release_events)
        next(
            event
            for event in changed_release
            if event["id"] == "hced_wave8_first_saudi_hced_diriyah1818_1"
        )["name"] = "changed"
        with self.assertRaisesRegex(ValueError, "audited release ownership changed"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                changed_release,
            )

    def test_twin_dispositions_pin_distinct_events(self) -> None:
        self.assertEqual(
            set(WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS),
            {
                "medina_1812_1925",
                "qassim_campaign_1904",
                "riyadh_1887_1902",
                "taif_1916_1924",
            },
        )
        qassim = WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS[
            "qassim_campaign_1904"
        ]
        self.assertEqual(qassim["disposition"], "distinct_engagements_same_campaign")
        self.assertIn("Unayzah", qassim["reason"])
        self.assertIn("Bukayriyah", qassim["reason"])
        self.assertEqual(
            set(WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_SAUDI_RASHIDI_RESERVED_IDS,
        )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities = {}
        sources = {}
        install_wave8_saudi_rashidi_entities(entities)
        install_wave8_saudi_rashidi_sources(sources)
        self.assertEqual(
            set(entities),
            {entity["id"] for entity in WAVE8_SAUDI_RASHIDI_ENTITIES},
        )
        self.assertEqual(
            set(sources),
            {source["id"] for source in WAVE8_SAUDI_RASHIDI_SOURCES},
        )
        original_entities = copy.deepcopy(entities)
        original_sources = copy.deepcopy(sources)
        install_wave8_saudi_rashidi_entities(entities)
        install_wave8_saudi_rashidi_sources(sources)
        self.assertEqual(entities, original_entities)
        self.assertEqual(sources, original_sources)

        bad_entities = copy.deepcopy(entities)
        next(iter(bad_entities.values()))["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_saudi_rashidi_entities(bad_entities)

        bad_sources = copy.deepcopy(sources)
        next(iter(bad_sources.values()))["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_saudi_rashidi_sources(bad_sources)

    def test_promoter_is_atomic_and_rejects_windows_and_duplicates(self) -> None:
        entities, _, existing = self._installed()
        events = promote_wave8_saudi_rashidi_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_saudi_rashidi_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        duplicate_name = [
            *existing,
            {"id": "duplicate_dilam", "name": "Battle of Dilam", "year": 1902},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_saudi_rashidi_contracts(
                self.hced_rows,
                entities,
                duplicate_name,
            )

        short = copy.deepcopy(entities)
        short["ibn_saud_dilam_force_1902"]["end_year"] = 1901
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_saudi_rashidi_contracts(
                self.hced_rows,
                short,
                existing,
            )

        partial_release = [*existing, events[0]]
        with self.assertRaisesRegex(ValueError, "partial candidate release"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                partial_release,
            )

        full_release = [*existing, *events]
        full_result = validate_wave8_saudi_rashidi_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            full_release,
        )
        self.assertEqual(full_result["released_target_candidates"], 11)

        duplicate_release = [*full_release, copy.deepcopy(events[0])]
        with self.assertRaisesRegex(ValueError, "duplicate candidate release"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                duplicate_release,
            )

        held_release = [
            *self.release_events,
            {
                "id": "illegal_hail_release",
                "name": "Hail",
                "year": 1921,
                "hced_candidate_id": "hced-Hail1921-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "held/excluded candidate was rated"):
            validate_wave8_saudi_rashidi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                held_release,
            )

    def test_release_state_is_synchronized_all_or_none(self) -> None:
        expected_entity_ids = {
            entity["id"] for entity in WAVE8_SAUDI_RASHIDI_ENTITIES
        }
        expected_source_ids = {
            source["id"] for source in WAVE8_SAUDI_RASHIDI_SOURCES
        }
        expected_event_ids = {
            f"{EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            for candidate_id in WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
        }
        release_entity_ids = {entity["id"] for entity in self.release_entities}
        release_source_ids = {source["id"] for source in self.release_sources}
        release_event_ids = {event["id"] for event in self.release_events}
        release_candidate_ids = {
            event.get("hced_candidate_id") for event in self.release_events
        }

        hits = {
            "candidates": WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
            & release_candidate_ids,
            "entities": expected_entity_ids & release_entity_ids,
            "events": expected_event_ids & release_event_ids,
            "sources": expected_source_ids & release_source_ids,
        }
        expected = {
            "candidates": WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
            "entities": expected_entity_ids,
            "events": expected_event_ids,
            "sources": expected_source_ids,
        }
        for category in hits:
            self.assertIn(hits[category], (set(), expected[category]))
        self.assertEqual(len({bool(value) for value in hits.values()}), 1)


if __name__ == "__main__":
    unittest.main()
