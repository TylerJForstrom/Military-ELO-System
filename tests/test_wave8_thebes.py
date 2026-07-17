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
from military_elo.promotion import wave8_thebes as lane


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_thebes_"

CORONEA_EXILES_ID = (
    "orchomenian_boeotian_exiles_locrian_euboean_exiles_coronea_447_bce"
)
CORONEA_ATHENIAN_ID = "tolmides_athenian_allied_force_coronea_447_bce"
DELIUM_BOEOTIAN_ID = "boeotian_federal_field_army_delium_424_bce"
DELIUM_ATHENIAN_ID = "hippocrates_athenian_field_army_delium_424_bce"
TEGYRA_THEBAN_ID = "pelopidas_sacred_band_cavalry_tegyra_375_bce"
TEGYRA_SPARTAN_ID = "spartan_orchomenus_garrison_force_tegyra_375_bce"
LEUCTRA_BOEOTIAN_ID = "epaminondas_boeotian_field_army_leuctra_371_bce"
LEUCTRA_LACEDAEMONIAN_ID = (
    "cleombrotus_lacedaemonian_allied_army_leuctra_371_bce"
)
MANTINEA_THEBAN_ID = "epaminondas_theban_allied_army_mantinea_362_bce"
MANTINEA_OPPOSITION_ID = "spartan_athenian_mantinean_allied_army_362_bce"
THEBES_ASSAULT_ID = "alexander_macedonian_greek_assault_force_thebes_335_bce"
THEBES_DEFENDERS_ID = "theban_rebel_civic_defenders_335_bce"


EXPECTED_RAW_HASHES = {
    "hced-Coronea-447-1": (
        "00e955d94fad33140d093479ab6c3d3ef2ba8e20206a12b05f488e18f21e8ff9"
    ),
    "hced-Delium-424-1": (
        "fad4a7d0e653c05f1fc43adcf953813336d440e80adadcb29b530c131d5e5cb3"
    ),
    "hced-Leuctra-371-1": (
        "b68adb278e24a23a4cc5c75d4b1ecc45c22ea0804924283420e02e567d391094"
    ),
    "hced-Mantinea-362-1": (
        "2b8a38d2546d047a8ffa34b9e2dab19f0fd3426a69dc5e3c63eddebca8df19db"
    ),
    "hced-Tegyra-375-1": (
        "127755835753e6f0748fdd8afdb8d1dd48510ba8888e97313bf11353dc29142c"
    ),
    "hced-Thebes-335-1": (
        "34e4310c1224bc71e22366cdc4f9ecd489ff0942419e947aec8addfbd23f88a1"
    ),
}

EXPECTED_RAW_ROWS = {
    "hced-Coronea-447-1": {
        "side_1": "Thebes",
        "side_2": "Athens, Boetia",
        "winner": "Thebes",
        "loser": "Athens, Boetia",
        "complete": True,
        "year": -447,
        "point": [22.9597293, 38.3593442],
    },
    "hced-Delium-424-1": {
        "side_1": "Thebes",
        "side_2": "Athens",
        "winner": "Thebes",
        "loser": "Athens",
        "complete": True,
        "year": -424,
        "point": [23.6654365, 38.3327765],
    },
    "hced-Tegyra-375-1": {
        "side_1": "Thebes",
        "side_2": "Sparta",
        "winner": "Thebes",
        "loser": "Sparta",
        "complete": True,
        "year": -375,
        "point": [22.957728, 38.534199],
    },
    "hced-Leuctra-371-1": {
        "side_1": "Thebes",
        "side_2": "Sparta",
        "winner": "Thebes",
        "loser": "Sparta",
        "complete": True,
        "year": -371,
        "point": [23.182943, 38.254175],
    },
    "hced-Mantinea-362-1": {
        "side_1": "Thebes",
        "side_2": "Athens, Sparta",
        "winner": "Draw",
        "loser": None,
        "complete": False,
        "year": -362,
        "point": [22.383333, 37.616667],
    },
    "hced-Thebes-335-1": {
        "side_1": "Macedonia",
        "side_2": "Thebes",
        "winner": "Macedonia",
        "loser": "Thebes",
        "complete": True,
        "year": -335,
        "point": [23.3204309, 38.322579],
    },
}

EXPECTED_ACTORS = {
    "hced-Coronea-447-1": ({CORONEA_EXILES_ID}, {CORONEA_ATHENIAN_ID}),
    "hced-Delium-424-1": ({DELIUM_BOEOTIAN_ID}, {DELIUM_ATHENIAN_ID}),
    "hced-Tegyra-375-1": ({TEGYRA_THEBAN_ID}, {TEGYRA_SPARTAN_ID}),
    "hced-Leuctra-371-1": (
        {LEUCTRA_BOEOTIAN_ID},
        {LEUCTRA_LACEDAEMONIAN_ID},
    ),
    "hced-Mantinea-362-1": ({MANTINEA_THEBAN_ID}, {MANTINEA_OPPOSITION_ID}),
    "hced-Thebes-335-1": ({THEBES_ASSAULT_ID}, {THEBES_DEFENDERS_ID}),
}

EXPECTED_CANONICAL = {
    "hced-Coronea-447-1": (
        "Battle of Coronea (447 BCE)",
        -447,
        "447 BCE (traditional chronology)",
        "year",
        "engagement",
    ),
    "hced-Delium-424-1": (
        "Battle of Delium",
        -424,
        "late 424 BCE",
        "year",
        "engagement",
    ),
    "hced-Tegyra-375-1": (
        "Battle of Tegyra",
        -375,
        "375 BCE",
        "year",
        "engagement",
    ),
    "hced-Leuctra-371-1": (
        "Battle of Leuctra",
        -371,
        "371 BCE",
        "year",
        "engagement",
    ),
    "hced-Mantinea-362-1": (
        "Battle of Mantinea (362 BCE)",
        -362,
        "summer 362 BCE",
        "season",
        "engagement",
    ),
    "hced-Thebes-335-1": (
        "Siege and destruction of Thebes",
        -335,
        "335 BCE",
        "year",
        "city_siege_and_assault",
    ),
}

# These rows mention Thebes only inside a composite side string.  They are
# intentionally outside the exact-label lane and must never be swept in by a
# substring fallback.
COMPOSITE_LABEL_IDS = {
    "hced-Chaeronea-338-1",
    "hced-Coronea-394-1",
    "hced-Cynoscephalae-364-1",
    "hced-Haliartus-395-1",
    "hced-Munychia-403-1",
    "hced-Nemea-394-1",
    "hced-Neon-354-1",
    "hced-Oenophyta-457-1",
    "hced-Plataea-479-1",
    "hced-Plataea-429-1",
    "hced-Tanagra-457-1",
    "hced-Tanagra-426-1",
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


class Wave8ThebesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "thebes"
            or normalize_label(row.get("side_2_raw")) == "thebes"
        ]

    def _installed(self):
        entity_ids = {str(entity["id"]) for entity in lane.WAVE8_THEBES_ENTITIES}
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in entity_ids
        }
        source_ids = {str(source["id"]) for source in lane.WAVE8_THEBES_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_THEBES_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_thebes_entities(entities)
        lane.install_wave8_thebes_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_thebes_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_funnel_and_queue_pin_all_six_exact_label_rows(self) -> None:
        exact_by_id = {
            str(row["candidate_id"]): row
            for row in self.exact_rows
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_ROWS))
        self.assertEqual(
            lane.WAVE8_THEBES_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_ROWS),
        )

        candidate_payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(exact_by_id)
        )
        candidate_digest = hashlib.sha256(candidate_payload.encode()).hexdigest()
        self.assertEqual(
            candidate_digest,
            lane.WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256,
        )

        # Historical pre-promotion projection of the unresolved-label funnel.
        # All six exact-label rows are promoted into the release ledger, so
        # the live build/ funnel correctly no longer carries the cohort; the
        # locked pre-promotion accounting is preserved inline instead.
        historical_funnel = {
            "labels": [
                {
                    "centuries": {"BCE_04": 4, "BCE_05": 2},
                    "event_candidate_id_sha256": (
                        "7ddb38c5103454765606d88a2b08d700cb22ca56d36d10d952701837e60af75b"
                    ),
                    "events_touched": 6,
                    "failure_cases": {"zero_time_valid_candidates": 6},
                    "label": "thebes",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 6,
                }
            ],
            "row_label_data": [
                {
                    "blocker_labels": ["athens boetia", "thebes"],
                    "candidate_id": "hced-Coronea-447-1",
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["thebes"],
                    "candidate_id": "hced-Delium-424-1",
                    "sole_blocker_label": "thebes",
                },
                {
                    "blocker_labels": ["thebes"],
                    "candidate_id": "hced-Tegyra-375-1",
                    "sole_blocker_label": "thebes",
                },
                {
                    "blocker_labels": ["thebes"],
                    "candidate_id": "hced-Leuctra-371-1",
                    "sole_blocker_label": "thebes",
                },
                {
                    "blocker_labels": ["athens sparta", "thebes"],
                    "candidate_id": "hced-Mantinea-362-1",
                    "sole_blocker_label": None,
                },
                {
                    "blocker_labels": ["thebes"],
                    "candidate_id": "hced-Thebes-335-1",
                    "sole_blocker_label": "thebes",
                },
            ],
        }
        funnel_rows = {
            str(row["candidate_id"]): row
            for row in historical_funnel["row_label_data"]
            if "thebes" in row.get("blocker_labels", [])
        }
        self.assertEqual(set(funnel_rows), set(EXPECTED_RAW_ROWS))
        label_rows = [
            row
            for row in historical_funnel["labels"]
            if row.get("label") == "thebes"
        ]
        self.assertEqual(len(label_rows), 1)
        label = label_rows[0]
        self.assertEqual(label["event_candidate_id_sha256"], candidate_digest)
        self.assertEqual(label["events_touched"], 6)
        self.assertEqual(label["unresolved_side_attempts"], 6)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 6)
        self.assertEqual(label["centuries"], {"BCE_04": 4, "BCE_05": 2})
        self.assertEqual(
            {
                candidate_id
                for candidate_id, row in funnel_rows.items()
                if row.get("sole_blocker_label") == "thebes"
            },
            {
                "hced-Delium-424-1",
                "hced-Leuctra-371-1",
                "hced-Tegyra-375-1",
                "hced-Thebes-335-1",
            },
        )

        self.assertFalse(
            any(
                row.get("label") == "thebes"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Thebes lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                str(row.get("candidate_id"))
                in lane.WAVE8_THEBES_EXPECTED_CANDIDATE_IDS
                for row in self.funnel.get("row_label_data", [])
            ),
            "promoted Thebes candidates must be absent from the live funnel",
        )

        self.assertEqual(
            lane.validate_wave8_thebes_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_THEBES_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        self.assertIn(len(integrated), {0, 6})
        if integrated:
            self.assertEqual(
                {str(event["hced_candidate_id"]) for event in integrated},
                set(lane.WAVE8_THEBES_CONTRACT_IDS),
            )
            self.assertEqual(len({str(event["id"]) for event in integrated}), 6)
            self.assertTrue(
                all(
                    str(event["id"]).startswith(EVENT_ID_PREFIX)
                    for event in integrated
                )
            )
            for event in integrated:
                self.assertNotIn("geometry", event)
                self.assertEqual(event["modern_location_country"], "Greece")
                Event.from_dict(event)

    def test_raw_rows_and_exact_hashes_are_fully_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(
                    (
                        row["side_1_raw"],
                        row["side_2_raw"],
                        row["winner_raw"],
                        row["loser_raw"],
                        row["winner_loser_complete"],
                        row["year_best"],
                    ),
                    (
                        expected["side_1"],
                        expected["side_2"],
                        expected["winner"],
                        expected["loser"],
                        expected["complete"],
                        expected["year"],
                    ),
                )
                self.assertEqual(row["modern_location_country"], "Greece")
                self.assertEqual(
                    [float(row["longitude"]), float(row["latitude"])],
                    expected["point"],
                )
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    EXPECTED_RAW_HASHES[candidate_id],
                )
                self.assertEqual(
                    lane.WAVE8_THEBES_CONTRACTS[candidate_id]["raw_row_sha256"],
                    EXPECTED_RAW_HASHES[candidate_id],
                )

    def test_signature_dispositions_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": lane.WAVE8_THEBES_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": lane.WAVE8_THEBES_CROSS_LANE_DISPOSITIONS,
            "entities": lane.WAVE8_THEBES_ENTITIES,
            "exact_candidate_id_sha256": (
                lane.WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256
            ),
            "existing_release_duplicate_dispositions": (
                lane.WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                lane.WAVE8_THEBES_EXPECTED_CANDIDATE_IDS
            ),
            "holds": lane.WAVE8_THEBES_HOLDS,
            "integration_dispositions": lane.WAVE8_THEBES_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                lane.WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": lane.WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": (
                lane.WAVE8_THEBES_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": lane.WAVE8_THEBES_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                lane.WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": lane.WAVE8_THEBES_SOURCES,
            "terminal_exclusions": lane.WAVE8_THEBES_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            independent,
            "b2e341390dccf5ebb9e4d16e3cdbddf3c1640163af361064fa231b599c54595a",
        )
        self.assertEqual(independent, lane.WAVE8_THEBES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(lane.wave8_thebes_audit_signature(), independent)

        self.assertEqual(lane.WAVE8_THEBES_CONTRACT_IDS, set(EXPECTED_RAW_ROWS))
        self.assertEqual(lane.WAVE8_THEBES_HOLD_IDS, frozenset())
        self.assertEqual(lane.WAVE8_THEBES_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(lane.WAVE8_THEBES_EXCLUSION_IDS, frozenset())
        self.assertEqual(lane.WAVE8_THEBES_HOLDS, {})
        self.assertEqual(lane.WAVE8_THEBES_TERMINAL_EXCLUSIONS, {})
        self.assertIs(
            lane.WAVE8_THEBES_EXCLUSIONS,
            lane.WAVE8_THEBES_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(lane.WAVE8_THEBES_NONPROMOTIONS, {})
        self.assertEqual(
            lane.WAVE8_THEBES_RESERVED_IDS,
            lane.WAVE8_THEBES_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            lane.wave8_thebes_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 6,
                "new_entities": 12,
                "new_sources": 15,
                "newly_rated_events": 6,
                "outcome_overrides": 1,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_thebes_cohort_counts(),
            {
                "boeotian_spartan_war_375_371_bce": 2,
                "first_peloponnesian_war_boeotia_447_bce": 1,
                "peloponnesian_war_boeotian_campaign_424_bce": 1,
                "theban_hegemony_mantinea_362_bce": 1,
                "theban_revolt_against_alexander_335_bce": 1,
            },
        )

    def test_sources_and_twelve_event_bounded_entities_parse(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in lane.WAVE8_THEBES_SOURCES
        }
        entity_by_id = {
            str(entity["id"]): entity for entity in lane.WAVE8_THEBES_ENTITIES
        }
        self.assertEqual(len(source_by_id), 15)
        self.assertEqual(
            len({source["source_family_id"] for source in source_by_id.values()}),
            12,
        )
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertIn(
                source["source_type"],
                {
                    "translated_primary_source",
                    "peer_reviewed_scholarly_article",
                    "open_access_scholarly_monograph_chapter",
                    "open_access_scholarly_monograph",
                    "scholarly_history_chapter",
                    "scholarly_reference_entry",
                },
            )

        self.assertEqual(len(entity_by_id), 12)
        self.assertEqual(
            set(entity_by_id),
            set().union(*(winner | loser for winner, loser in EXPECTED_ACTORS.values())),
        )
        all_actor_ids = []
        for candidate_id, contract in lane.WAVE8_THEBES_CONTRACTS.items():
            event_year = contract["canonical_event"]["year_low"]
            actor_ids = [
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            ]
            self.assertEqual(len(actor_ids), 2)
            all_actor_ids.extend(actor_ids)
            for entity_id in actor_ids:
                entity = entity_by_id[entity_id]
                Entity.from_dict(entity)
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    (event_year, event_year),
                    candidate_id,
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                note = entity["continuity_note"].casefold()
                self.assertIn("no rating is inherited", note)
                self.assertIn("same-name thebes", note)
                self.assertIn("modern state", note)
                self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))
        self.assertEqual(len(all_actor_ids), len(set(all_actor_ids)))

        generic_ids = {
            "athens",
            "boeotia",
            "macedonia",
            "sparta",
            "thebes",
        }
        self.assertTrue(generic_ids.isdisjoint(entity_by_id))
        self.assertTrue(
            all(entity["start_year"] < 0 for entity in entity_by_id.values())
        )
        consumed_sources = {
            source_id
            for entity in entity_by_id.values()
            for source_id in entity["source_ids"]
        } | {
            source_id
            for contract in lane.WAVE8_THEBES_CONTRACTS.values()
            for source_id in contract["evidence_refs"]
        }
        self.assertEqual(consumed_sources, set(source_by_id))

    def test_each_historical_actor_resolution_is_event_specific(self) -> None:
        contracts = lane.WAVE8_THEBES_CONTRACTS
        self.assertEqual(
            set(contracts["hced-Coronea-447-1"]["side_1_entity_ids"]),
            {CORONEA_EXILES_ID},
        )
        self.assertNotIn("theban", CORONEA_EXILES_ID)
        self.assertIn(
            "not a Theban army",
            contracts["hced-Coronea-447-1"]["audit_note"],
        )
        self.assertEqual(
            set(contracts["hced-Delium-424-1"]["side_1_entity_ids"]),
            {DELIUM_BOEOTIAN_ID},
        )
        self.assertIn(
            "multiple other Boeotian contingents",
            contracts["hced-Delium-424-1"]["audit_note"],
        )
        self.assertEqual(
            set(contracts["hced-Tegyra-375-1"]["side_1_entity_ids"]),
            {TEGYRA_THEBAN_ID},
        )
        self.assertIn(
            "three hundred infantry",
            contracts["hced-Tegyra-375-1"]["audit_note"],
        )
        self.assertEqual(
            set(contracts["hced-Leuctra-371-1"]["side_1_entity_ids"]),
            {LEUCTRA_BOEOTIAN_ID},
        )
        self.assertIn(
            "federal formation",
            contracts["hced-Leuctra-371-1"]["audit_note"],
        )
        self.assertEqual(
            set(contracts["hced-Mantinea-362-1"]["side_1_entity_ids"]),
            {MANTINEA_THEBAN_ID},
        )
        self.assertEqual(
            set(contracts["hced-Mantinea-362-1"]["side_2_entity_ids"]),
            {MANTINEA_OPPOSITION_ID},
        )
        self.assertEqual(
            set(contracts["hced-Thebes-335-1"]["side_1_entity_ids"]),
            {THEBES_ASSAULT_ID},
        )
        self.assertEqual(
            set(contracts["hced-Thebes-335-1"]["side_2_entity_ids"]),
            {THEBES_DEFENDERS_ID},
        )
        self.assertIn(
            "Egyptian Thebes",
            contracts["hced-Thebes-335-1"]["audit_note"],
        )

        for candidate_id, contract in contracts.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertTrue(contract["actor_override"])
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertFalse(contract["outcome_reversal"])
                self.assertEqual(
                    contract["duplicate_ownership"],
                    {
                        "owner_module": "military_elo.promotion.wave8_thebes",
                        "status": "canonical_hced_owner",
                    },
                )
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]),
                    2,
                )

    def test_canonical_events_and_promoted_outputs_are_complete_and_deterministic(self) -> None:
        entities, _, existing = self._installed()
        existing_before = copy.deepcopy(existing)
        first = lane.promote_wave8_thebes_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        second = lane.promote_wave8_thebes_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(first, second)
        self.assertEqual(existing, existing_before)
        self.assertEqual(len(first), 6)
        by_candidate = {str(event["hced_candidate_id"]): event for event in first}
        self.assertEqual(set(by_candidate), set(EXPECTED_ACTORS))

        names = set()
        canonical_keys = set()
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_ACTORS.items()
        ):
            event = by_candidate[candidate_id]
            contract = lane.WAVE8_THEBES_CONTRACTS[candidate_id]
            expected_name, year, _, precision, granularity = EXPECTED_CANONICAL[
                candidate_id
            ]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected_name)
            self.assertEqual((event["year"], event["end_year"]), (year, year))
            self.assertEqual(event["date_precision"], precision)
            self.assertEqual(event["reviewed_granularity"], granularity)
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )
            self.assertEqual(
                event["source_ids"],
                ["hced_dataset", *contract["evidence_refs"]],
            )
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
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
            self.assertEqual(winners, expected_winners)
            self.assertEqual(losers, expected_losers)
            self.assertEqual(
                {p["termination"] for p in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )
            names.add(event["name"])
            canonical_keys.add(event["canonical_event_key"])
        self.assertEqual(len(names), 6)
        self.assertEqual(len(canonical_keys), 6)

    def test_mantinea_raw_draw_is_corrected_only_to_attested_tactical_victory(self) -> None:
        raw = next(
            row
            for row in self.exact_rows
            if row["candidate_id"] == "hced-Mantinea-362-1"
        )
        self.assertEqual(raw["winner_raw"], "Draw")
        self.assertIsNone(raw["loser_raw"])
        self.assertFalse(raw["winner_loser_complete"])

        contract = lane.WAVE8_THEBES_CONTRACTS["hced-Mantinea-362-1"]
        self.assertTrue(contract["source_outcome_override"])
        self.assertFalse(contract["outcome_reversal"])
        self.assertEqual((contract["result_type"], contract["winner_side"]), ("win", 1))
        self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)
        self.assertEqual(
            set(lane.WAVE8_THEBES_OUTCOME_OVERRIDES),
            {"hced-Mantinea-362-1"},
        )
        override = lane.WAVE8_THEBES_OUTCOME_OVERRIDES[
            "hced-Mantinea-362-1"
        ]
        self.assertEqual(override["raw_winner_raw"], "Draw")
        self.assertIsNone(override["raw_loser_raw"])
        self.assertFalse(override["raw_winner_loser_complete"])
        self.assertEqual(
            override["corrected_winner_entity_ids"],
            [MANTINEA_THEBAN_ID],
        )
        self.assertEqual(
            override["corrected_loser_entity_ids"],
            [MANTINEA_OPPOSITION_ID],
        )
        self.assertIn("no_decisive_strategic_payoff", override["strategic_disposition"])
        self.assertEqual(override["outcome_source_ids"], contract["outcome_source_ids"])

        event = next(
            event
            for event in self._events()
            if event["hced_candidate_id"] == "hced-Mantinea-362-1"
        )
        terminations = {item["termination"] for item in event["participants"]}
        self.assertEqual(
            terminations,
            {"engagement_victory", "engagement_defeat"},
        )
        self.assertNotIn("inconclusive", " ".join(terminations))
        summary = event["summary"].casefold()
        self.assertIn("raw draw", summary)
        self.assertIn("tactical", summary)
        self.assertIn("strategically", summary)

        self.assertEqual(lane.WAVE8_THEBES_HOLDS, {})
        self.assertEqual(lane.WAVE8_THEBES_TERMINAL_EXCLUSIONS, {})
        self.assertNotIn(
            "draw",
            {contract["result_type"] for contract in lane.WAVE8_THEBES_CONTRACTS.values()},
        )
        self.assertNotIn(
            "unknown",
            {contract["result_type"] for contract in lane.WAVE8_THEBES_CONTRACTS.values()},
        )

    def test_promoted_only_location_review_withholds_all_points_and_keeps_greece(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(
            lane.WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_THEBES_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            set(lane.WAVE8_THEBES_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_THEBES_CONTRACT_IDS,
        )
        self.assertTrue(
            lane.WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS.isdisjoint(
                lane.WAVE8_THEBES_HOLD_IDS
                | lane.WAVE8_THEBES_TERMINAL_EXCLUSION_IDS
            )
        )
        expected_additions = {
            "country": frozenset(),
            "point": lane.WAVE8_THEBES_CONTRACT_IDS,
        }
        self.assertEqual(
            lane.WAVE8_THEBES_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": lane.WAVE8_THEBES_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            lane.wave8_thebes_location_quarantine_additions(),
            expected_additions,
        )

        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, review in (
            lane.WAVE8_THEBES_LOCATION_QUARANTINE_REASONS.items()
        ):
            row = by_id[candidate_id]
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(review["retained_country"], "Greece")
            self.assertEqual(
                review["raw_point"],
                [float(row["longitude"]), float(row["latitude"])],
            )
            self.assertTrue(review["reason"])
            self.assertTrue(
                set(review["evidence_refs"])
                <= set(lane.WAVE8_THEBES_CONTRACTS[candidate_id]["evidence_refs"])
            )

        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Greece")
            self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_composite_thebes_labels_remain_outside_the_exact_lane(self) -> None:
        contains_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if any(
                "thebes" in normalize_label(row.get(field))
                for field in ("side_1_raw", "side_2_raw")
            )
        }
        incidental_ids = set(contains_rows) - lane.WAVE8_THEBES_RESERVED_IDS
        self.assertEqual(incidental_ids, COMPOSITE_LABEL_IDS)
        self.assertTrue(
            COMPOSITE_LABEL_IDS.isdisjoint(lane.WAVE8_THEBES_RESERVED_IDS)
        )
        for candidate_id in COMPOSITE_LABEL_IDS:
            row = contains_rows[candidate_id]
            labels = {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            self.assertNotIn("thebes", labels)
        self.assertEqual(
            contains_rows["hced-Coronea-394-1"]["year_best"],
            -394,
        )
        self.assertEqual(
            contains_rows["hced-Coronea-447-1"]["year_best"],
            -447,
        )

    def test_zero_duplicate_audits_pass_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(lane.WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(lane.WAVE8_THEBES_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(lane.WAVE8_THEBES_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(lane.WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_THEBES_RESERVED_IDS,
        )
        for candidate_id, audit in lane.WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT.items():
            canonical = lane.WAVE8_THEBES_CONTRACTS[candidate_id]["canonical_event"]
            self.assertEqual(
                audit["years"],
                [canonical["year_low"], canonical["year_high"]],
            )
            self.assertEqual(audit["aliases"], sorted(set(audit["aliases"])))
            self.assertTrue(
                all(alias == normalize_label(alias) for alias in audit["aliases"])
            )
            self.assertIn(normalize_label(canonical["name"]), audit["aliases"])

        expected = {
            "cross_lane_hced_dispositions": 0,
            "existing_release_duplicate_dispositions": 0,
            "integration_dispositions": 0,
            "iwbd_duplicate_dispositions": 0,
            "iwbd_probable_twins": 0,
            "iwbd_zero_overlap_candidates": 6,
        }
        self.assertEqual(
            lane.validate_wave8_thebes_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            expected,
        )
        self.assertEqual(
            lane.validate_wave8_thebes_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*self.release_events, *self._events()],
            ),
            expected,
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-coronea-447-twin",
                "name": "Battle of Coronea (447 BCE)",
                "year_best": -447,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_thebes_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-leuktra-twin",
                "name": "Battle of Leuktra",
                "year_best": -371,
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_thebes_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {"id": "future-thebes-twin", "name": "Siege of Thebes", "year": -335},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_thebes_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_every_row_tamper_missing_duplicate_and_future_exact_row_fail_closed(self) -> None:
        for candidate_id in sorted(lane.WAVE8_THEBES_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    row
                    for row in tampered
                    if row.get("candidate_id") == candidate_id
                )
                row["name"] = str(row["name"]) + " changed"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    lane.validate_wave8_thebes_queue_contracts(tampered)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Delium-424-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row, found 0"):
            lane.validate_wave8_thebes_queue_contracts(missing)

        duplicate = copy.deepcopy(self.hced_rows)
        duplicate.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced_rows
                    if row.get("candidate_id") == "hced-Tegyra-375-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row, found 2"):
            lane.validate_wave8_thebes_queue_contracts(duplicate)

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-future-exact-thebes",
                "side_1_raw": " THEBES ",
                "side_2_raw": "Future opponent",
                "year_best": -300,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Thebes inventory changed"):
            lane.validate_wave8_thebes_queue_contracts(future)

    def test_entity_windows_and_event_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short[LEUCTRA_BOEOTIAN_ID]["start_year"] = -370
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_thebes_contracts(
                self.hced_rows,
                short,
                existing,
            )

        missing = copy.deepcopy(entities)
        missing.pop(THEBES_DEFENDERS_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_thebes_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        events = lane.promote_wave8_thebes_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_thebes_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        canonical_collision = [
            *existing,
            {"id": "future-delium", "name": "Battle of Delium", "year": -424},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_thebes_contracts(
                self.hced_rows,
                entities,
                canonical_collision,
            )

        raw_collision = [
            *existing,
            {"id": "future-tegyra", "name": "Tegyra", "year": -375},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_thebes_contracts(
                self.hced_rows,
                entities,
                raw_collision,
            )

    def test_installers_are_idempotent_copy_fixtures_and_reject_collisions(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        entity_fixtures_before = copy.deepcopy(lane.WAVE8_THEBES_ENTITIES)
        source_fixtures_before = copy.deepcopy(lane.WAVE8_THEBES_SOURCES)

        lane.install_wave8_thebes_entities(entities)
        lane.install_wave8_thebes_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        lane.install_wave8_thebes_entities(entities)
        lane.install_wave8_thebes_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)

        entities[CORONEA_EXILES_ID]["name"] = "tampered"
        sources["wave8_thebes_thucydides_coronea"]["title"] = "tampered"
        self.assertEqual(lane.WAVE8_THEBES_ENTITIES, entity_fixtures_before)
        self.assertEqual(lane.WAVE8_THEBES_SOURCES, source_fixtures_before)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_thebes_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_thebes_sources(sources)


if __name__ == "__main__":
    unittest.main()
