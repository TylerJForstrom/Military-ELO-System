import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_danish_vikings import (
    WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
    WAVE8_DANISH_VIKINGS_CONTRACTS,
    WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_ENTITIES,
    WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS,
    WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS,
    WAVE8_DANISH_VIKINGS_FINAL_AUDIT_SIGNATURE,
    WAVE8_DANISH_VIKINGS_HOLD_IDS,
    WAVE8_DANISH_VIKINGS_HOLDS,
    WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_DANISH_VIKINGS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES,
    WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_DANISH_VIKINGS_RESERVED_IDS,
    WAVE8_DANISH_VIKINGS_SOURCES,
    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS,
    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS,
    WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS,
    install_wave8_danish_vikings_entities,
    install_wave8_danish_vikings_sources,
    promote_wave8_danish_vikings_contracts,
    validate_wave8_danish_vikings_integration_dispositions,
    validate_wave8_danish_vikings_queue_contracts,
    wave8_danish_vikings_audit_signature,
    wave8_danish_vikings_cohort_counts,
    wave8_danish_vikings_counts,
    wave8_danish_vikings_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_danish_vikings_"

ACLEA_WESSEX_ID = "aethelwulf_aethelbald_aclea_army_851"
ACLEA_VIKING_ID = "thames_viking_host_aclea_851"
WESSEX_871_ID = "aethelred_alfred_wessex_campaign_army_871"
GREAT_ARMY_871_ID = "great_heathen_army_wessex_campaign_871"
FARNHAM_WESSEX_ID = "edward_west_saxon_field_army_farnham_893"
FARNHAM_VIKING_ID = "appledore_raiding_detachment_farnham_893"


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
    "hced-Aclea851-1": ("Wessex", "Danish Vikings", "Wessex", "Danish Vikings"),
    "hced-Ashdown871-1": (
        "Wessex",
        "Danish Vikings",
        "Wessex",
        "Danish Vikings",
    ),
    "hced-Dyle891-1": (
        "Germany",
        "Danish Vikings",
        "Germany",
        "Danish Vikings",
    ),
    "hced-Farnham893-1": (
        "Wessex",
        "Danish Vikings",
        "Wessex",
        "Danish Vikings",
    ),
    "hced-La Gueule891-1": (
        "Danish Vikings",
        "Germany",
        "Danish Vikings",
        "Germany",
    ),
    "hced-Merton871-1": (
        "Danish Vikings",
        "Wessex",
        "Danish Vikings",
        "Wessex",
    ),
    "hced-Thanet851-1": (
        "Danish Vikings",
        "Kent, Wessex",
        "Danish Vikings",
        "Kent, Wessex",
    ),
}


EXPECTED_ROW_HASHES = {
    "hced-Aclea851-1": (
        "a937b401c5cd89ef8a6525c1a47a95a2134c679ba8aa63662d28024f41fb9c31"
    ),
    "hced-Ashdown871-1": (
        "89effd46d7ebc1acdbbf3adebb9bde1b20c7ab57d8cfad384dbab70e1deb7d85"
    ),
    "hced-Dyle891-1": (
        "2f33f1a8acb214c89abc890958622091d462899165fa0ee07f76a4f49b9bfeef"
    ),
    "hced-Farnham893-1": (
        "932c3f72caacc1d44fe9e102fcd180a758c226921f0ccf735cacfcd2a106dc4c"
    ),
    "hced-La Gueule891-1": (
        "3e968135745eaf6e62b3c33b7854a1c85ce5fe5382c98e10e641321b9b9eaf3e"
    ),
    "hced-Merton871-1": (
        "4355b88b26dec575774b3918d4a44abe7baa3dbc18b49208be55deccdb1e12d0"
    ),
    "hced-Thanet851-1": (
        "0d8a932fa39470ac9303c78faa6a3591071f38cc65021ecc16784d4084895f15"
    ),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Aclea851-1": ({ACLEA_WESSEX_ID}, {ACLEA_VIKING_ID}),
    "hced-Ashdown871-1": ({WESSEX_871_ID}, {GREAT_ARMY_871_ID}),
    "hced-Farnham893-1": ({FARNHAM_WESSEX_ID}, {FARNHAM_VIKING_ID}),
    "hced-Merton871-1": ({GREAT_ARMY_871_ID}, {WESSEX_871_ID}),
}


EXPECTED_DATES = {
    "hced-Aclea851-1": ("year", "851"),
    "hced-Ashdown871-1": ("month", "January 871"),
    "hced-Farnham893-1": ("year", "893 (Chronicle annal 894, recte 893)"),
    "hced-Merton871-1": ("month", "March 871"),
}


class Wave8DanishVikingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in WAVE8_DANISH_VIKINGS_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        install_wave8_danish_vikings_entities(entities)

        lane_source_ids = {
            str(source["id"]) for source in WAVE8_DANISH_VIKINGS_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        install_wave8_danish_vikings_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_DANISH_VIKINGS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_danish_vikings_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_DANISH_VIKINGS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": (
                WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS
            ),
            "entities": WAVE8_DANISH_VIKINGS_ENTITIES,
            "expected_candidate_ids": sorted(
                WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_DANISH_VIKINGS_HOLDS,
            "integration_dispositions": (
                WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS
            ),
            "iwbd_duplicate_dispositions": (
                WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": (
                WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT
            ),
            "outcome_overrides": WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_DANISH_VIKINGS_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            independent_signature,
            WAVE8_DANISH_VIKINGS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_danish_vikings_audit_signature(),
            independent_signature,
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS,
            WAVE8_DANISH_VIKINGS_RESERVED_IDS,
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS,
            set(EXPECTED_RAW_LABELS),
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_HOLD_IDS,
            {"hced-Thanet851-1"},
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS,
            WAVE8_DANISH_VIKINGS_HOLD_IDS,
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_RESERVED_IDS,
            WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_danish_vikings_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 3,
                "external_owner_hced_dispositions": 2,
                "holds": 1,
                "integration_dispositions": 3,
                "iwbd_duplicate_dispositions": 0,
                "locally_reserved_hced_rows": 5,
                "new_entities": 6,
                "new_sources": 8,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
                "touched_hced_rows": 7,
            },
        )
        self.assertEqual(
            wave8_danish_vikings_cohort_counts(),
            {
                "appledore_raiding_campaign_893": 1,
                "great_army_wessex_campaign_871": 2,
                "thames_invasion_851": 1,
            },
        )

    def test_all_and_only_seven_exact_label_rows_are_hash_pinned(self) -> None:
        exact_label_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Danish Vikings"
            or row.get("side_2_raw") == "Danish Vikings"
        }
        self.assertEqual(set(exact_label_rows), set(EXPECTED_RAW_LABELS))
        for candidate_id, row in exact_label_rows.items():
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                ),
                EXPECTED_RAW_LABELS[candidate_id],
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                EXPECTED_ROW_HASHES[candidate_id],
            )
            disposition = (
                WAVE8_DANISH_VIKINGS_CONTRACTS.get(candidate_id)
                or WAVE8_DANISH_VIKINGS_HOLDS.get(candidate_id)
                or WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS[candidate_id]
            )
            self.assertEqual(
                disposition["raw_row_sha256"],
                EXPECTED_ROW_HASHES[candidate_id],
            )
        self.assertEqual(
            validate_wave8_danish_vikings_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 2,
                "promotion_contracts": 4,
                "holds": 1,
                "reviewed_hced_rows": 7,
            },
        )

        for candidate_id in EXPECTED_RAW_LABELS:
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.hced_rows)
                next(
                    row for row in changed if row["candidate_id"] == candidate_id
                )["name"] += " changed"
                with self.assertRaisesRegex(
                    ValueError,
                    "raw-row fingerprint changed",
                ):
                    validate_wave8_danish_vikings_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Aclea851-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_danish_vikings_queue_contracts(missing)

    def test_sources_and_campaign_bounded_entities_parse_and_install(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_DANISH_VIKINGS_SOURCES
        }
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_DANISH_VIKINGS_ENTITIES
        }
        self.assertEqual(len(source_by_id), 8)
        self.assertEqual(len(entity_by_id), 6)
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entity_by_id.items()
            },
            {
                ACLEA_WESSEX_ID: (851, 851),
                ACLEA_VIKING_ID: (851, 851),
                WESSEX_871_ID: (871, 871),
                GREAT_ARMY_871_ID: (871, 871),
                FARNHAM_WESSEX_ID: (893, 893),
                FARNHAM_VIKING_ID: (893, 893),
            },
        )

        for source in WAVE8_DANISH_VIKINGS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertTrue(source["source_family_id"])
        for entity in WAVE8_DANISH_VIKINGS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertIn(
                "no rating is inherited",
                entity["continuity_note"].casefold(),
            )
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))
            self.assertNotIn(
                entity["name"].casefold(),
                {
                    "danes",
                    "danish vikings",
                    "denmark",
                    "east francia",
                    "northmen",
                    "vikings",
                    "wessex",
                },
            )

        entities, sources, _ = self._installed()
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])
            self.assertIsNot(entities[entity_id], entity_by_id[entity_id])
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])
            self.assertIsNot(sources[source_id], source_by_id[source_id])

        collision = copy.deepcopy(entities)
        collision[ACLEA_WESSEX_ID]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_danish_vikings_entities(collision)

        source_collision = copy.deepcopy(sources)
        first_source_id = next(iter(source_by_id))
        source_collision[first_source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_danish_vikings_sources(source_collision)

    def test_campaign_identity_sharing_is_narrow_and_exact(self) -> None:
        sides = {
            candidate_id: (
                tuple(contract["side_1_entity_ids"]),
                tuple(contract["side_2_entity_ids"]),
            )
            for candidate_id, contract in WAVE8_DANISH_VIKINGS_CONTRACTS.items()
        }
        self.assertEqual(
            sides["hced-Ashdown871-1"],
            ((WESSEX_871_ID,), (GREAT_ARMY_871_ID,)),
        )
        self.assertEqual(
            sides["hced-Merton871-1"],
            ((GREAT_ARMY_871_ID,), (WESSEX_871_ID,)),
        )
        self.assertNotIn("hced-Dyle891-1", sides)
        self.assertNotIn("hced-La Gueule891-1", sides)
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS,
            {"hced-Dyle891-1", "hced-La Gueule891-1"},
        )
        for candidate_id in WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS:
            disposition = WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS[
                candidate_id
            ]
            self.assertEqual(disposition["disposition"], "external_lane_owner")
            self.assertEqual(
                disposition["owner_module"],
                "military_elo.promotion.wave8_germany",
            )

        usage = Counter(
            entity_id
            for contract in WAVE8_DANISH_VIKINGS_CONTRACTS.values()
            for side in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[side]
        )
        self.assertEqual(
            {entity_id for entity_id, count in usage.items() if count == 2},
            {WESSEX_871_ID, GREAT_ARMY_871_ID},
        )
        self.assertEqual(
            {entity_id for entity_id, count in usage.items() if count == 1},
            {
                ACLEA_WESSEX_ID,
                ACLEA_VIKING_ID,
                FARNHAM_WESSEX_ID,
                FARNHAM_VIKING_ID,
            },
        )
        self.assertEqual(set(usage), {entity["id"] for entity in WAVE8_DANISH_VIKINGS_ENTITIES})

    def test_dates_sides_and_outcomes_are_direct_and_never_overridden(self) -> None:
        self.assertEqual(WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in WAVE8_DANISH_VIKINGS_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                EXPECTED_DATES[candidate_id],
            )
            self.assertEqual(canonical["granularity"], "engagement")
            self.assertEqual(contract["result_type"], "win")
            self.assertIn(contract["winner_side"], {1, 2})
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertNotEqual(contract["result_type"], "draw")

    def test_outcome_sources_and_source_families_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_DANISH_VIKINGS_SOURCES
        }
        expected_family_counts = {
            "hced-Aclea851-1": 1,
            "hced-Ashdown871-1": 2,
            "hced-Farnham893-1": 3,
            "hced-Merton871-1": 2,
        }
        for candidate_id, contract in WAVE8_DANISH_VIKINGS_CONTRACTS.items():
            outcome_ids = list(contract["outcome_source_ids"])
            self.assertTrue(outcome_ids)
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
            self.assertTrue(set(outcome_ids) <= set(contract["evidence_refs"]))
            expected_families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcome_ids}
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                expected_families,
            )
            self.assertEqual(len(expected_families), expected_family_counts[candidate_id])
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

    def test_thanet_is_terminal_unknown_not_a_fabricated_engagement(self) -> None:
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS,
            WAVE8_DANISH_VIKINGS_HOLDS,
        )
        exclusion = WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS[
            "hced-Thanet851-1"
        ]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertEqual(
            exclusion["hold_category"],
            "noncompetitive_overwintering_misattributed_as_battle",
        )
        self.assertEqual(exclusion["reviewed_outcome"], "unknown")
        self.assertEqual(exclusion["result_type"], "unknown")
        self.assertTrue(exclusion["unknown_is_never_draw"])
        self.assertNotIn("winner_side", exclusion)
        self.assertEqual(
            exclusion["canonical_event"]["granularity"],
            "noncompetitive_overwintering_notice",
        )
        self.assertIn("overwintered on Thanet", exclusion["hold_reason"])
        self.assertIn("Battle of Sandwich", exclusion["hold_reason"])
        self.assertIn("unknown", exclusion["hold_reason"])
        self.assertEqual(
            set(exclusion["evidence_refs"]),
            {
                "wave8_danish_vikings_he_sandwich_851",
                "wave8_danish_vikings_yale_asc_ninth_century",
            },
        )

    def test_emission_is_parseable_tactical_exact_and_draw_free(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        generic_ids = {
            "danes",
            "danish_vikings",
            "denmark",
            "east_francia",
            "northmen",
            "vikings",
            "wessex",
        }
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
            self.assertFalse((winners | losers) & generic_ids)
            self.assertFalse(
                any(
                    "draw" in participant["termination"]
                    for participant in event["participants"]
                )
            )
            contract = WAVE8_DANISH_VIKINGS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

        entities, _, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_danish_vikings_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_location_quarantine_is_complete_local_and_non_mutating(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()

        self.assertEqual(
            WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS,
            WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_danish_vikings_location_quarantine_additions(),
            {
                "point": WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertIn("modern_location_country", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_cross_lane_iwbd_and_release_boundaries_fail_closed(self) -> None:
        self.assertEqual(WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS),
            {
                "hced-Dyle891-1",
                "hced-Inverdovat877-1",
                "hced-La Gueule891-1",
            },
        )
        self.assertEqual(
            WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS,
            WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS,
        )
        inverdovat = next(
            row
            for row in self.hced_rows
            if row["candidate_id"] == "hced-Inverdovat877-1"
        )
        disposition = WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS[
            "hced-Inverdovat877-1"
        ]
        self.assertEqual(
            canonical_hced_row_sha256(inverdovat),
            disposition["raw_row_sha256"],
        )
        self.assertEqual(
            inverdovat["side_2_raw"],
            "Vikings of Dublin, Danish Vikings",
        )
        self.assertNotIn("hced-Inverdovat877-1", WAVE8_DANISH_VIKINGS_RESERVED_IDS)
        self.assertIn("wave8_irish_history", disposition["reason"])

        self.assertEqual(
            validate_wave8_danish_vikings_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 3,
                "external_owner_hced_dispositions": 2,
                "integration_dispositions": 3,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_probable_twins": 0,
            },
        )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Inverdovat877-1"
        )["name"] = "Inverdovat changed"
        with self.assertRaisesRegex(ValueError, "ownership fingerprint changed"):
            validate_wave8_danish_vikings_integration_dispositions(
                changed,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwbd = copy.deepcopy(self.iwbd_rows)
        future_iwbd.append(
            {
                "candidate_id": "iwbd-future-leuven",
                "name": "Battle of Leuven (Dyle)",
                "start_date": "0891-10-01",
                "end_date": "0891-10-01",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_danish_vikings_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *self.release_events,
            {"id": "future-farnham", "name": "Battle of Farnham", "year": 893},
        ]
        with self.assertRaisesRegex(
            ValueError,
            "unreviewed probable release duplicate",
        ):
            validate_wave8_danish_vikings_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )


if __name__ == "__main__":
    unittest.main()
