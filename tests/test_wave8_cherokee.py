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
from military_elo.promotion.wave8_cherokee import (
    WAVE8_CHEROKEE_CONTRACT_IDS,
    WAVE8_CHEROKEE_CONTRACTS,
    WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS,
    WAVE8_CHEROKEE_ENTITIES,
    WAVE8_CHEROKEE_EXCLUSION_IDS,
    WAVE8_CHEROKEE_EXCLUSIONS,
    WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS,
    WAVE8_CHEROKEE_FINAL_AUDIT_SIGNATURE,
    WAVE8_CHEROKEE_HOLD_IDS,
    WAVE8_CHEROKEE_HOLDS,
    WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS,
    WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_CHEROKEE_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_CHEROKEE_OUTCOME_OVERRIDES,
    WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS,
    WAVE8_CHEROKEE_RESERVED_IDS,
    WAVE8_CHEROKEE_SOURCES,
    install_wave8_cherokee_entities,
    install_wave8_cherokee_sources,
    promote_wave8_cherokee_contracts,
    validate_wave8_cherokee_integration_dispositions,
    validate_wave8_cherokee_queue_contracts,
    wave8_cherokee_audit_signature,
    wave8_cherokee_cohort_counts,
    wave8_cherokee_counts,
    wave8_cherokee_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_cherokee_"

ECHOE_1760_CHEROKEE = "first_echoe_cherokee_fighting_force_1760"
MONTGOMERIE_1760 = "montgomerie_british_sc_force_echoe_1760"
LOUDOUN_CHEROKEE = "fort_loudoun_overhill_cherokee_siege_force_1760"
LOUDOUN_GARRISON = "fort_loudoun_south_carolina_garrison_1760"
GRANT_1761 = "grant_british_sc_indigenous_allied_force_echoe_1761"
ECHOE_1761_CHEROKEE = "second_echoe_cherokee_fighting_force_1761"
SAN_SABA_TEXAS = "burleson_texas_lipan_tonkawa_force_san_saba_1839"
SAN_SABA_CHEROKEE = "egg_bowles_cherokee_fighting_party_san_saba_1839"


EXPECTED_RAW_LABELS = {
    "hced-Etchoe1760-1": (
        "Cherokee Indians",
        "United Kingdom",
        "Cherokee Indians",
        "United Kingdom",
    ),
    "hced-Etchoe1761-1": (
        "United Kingdom",
        "Cherokee Indians",
        "United Kingdom",
        "Cherokee Indians",
    ),
    "hced-Fort Loudoun1760-1": (
        "Cherokee Indians",
        "United Kingdom, South Carolina",
        "Cherokee Indians",
        "United Kingdom, South Carolina",
    ),
    "hced-Fort Prince George1760-1": (
        "United Kingdom, North Carolina",
        "Cherokee Indians",
        "United Kingdom, North Carolina",
        "Cherokee Indians",
    ),
    "hced-San Saba1839-1": (
        "Texas",
        "Cherokee Indians",
        "Texas",
        "Cherokee Indians",
    ),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Etchoe1760-1": ({ECHOE_1760_CHEROKEE}, {MONTGOMERIE_1760}),
    "hced-Etchoe1761-1": ({GRANT_1761}, {ECHOE_1761_CHEROKEE}),
    "hced-Fort Loudoun1760-1": ({LOUDOUN_CHEROKEE}, {LOUDOUN_GARRISON}),
    "hced-San Saba1839-1": ({SAN_SABA_TEXAS}, {SAN_SABA_CHEROKEE}),
}


EXPECTED_DATES = {
    "hced-Etchoe1760-1": ("day", "27 June 1760", "engagement"),
    "hced-Etchoe1761-1": ("day", "10 June 1761", "engagement"),
    "hced-Fort Loudoun1760-1": (
        "month_to_day",
        "March-7 August 1760; capitulation ended the siege",
        "siege",
    ),
    "hced-San Saba1839-1": ("day", "25 December 1839", "engagement"),
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


class Wave8CherokeeTests(unittest.TestCase):
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
            if row.get("candidate_id") in WAVE8_CHEROKEE_RESERVED_IDS
        ]

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_CHEROKEE_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_cherokee_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_CHEROKEE_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_cherokee_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_CHEROKEE_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_cherokee_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_CHEROKEE_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_CHEROKEE_ENTITIES,
            "expected_candidate_ids": sorted(
                WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_CHEROKEE_HOLDS,
            "integration_dispositions": WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_CHEROKEE_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_CHEROKEE_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_CHEROKEE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_cherokee_audit_signature(), independent_signature)
        self.assertEqual(
            WAVE8_CHEROKEE_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(
            WAVE8_CHEROKEE_HOLD_IDS,
            {"hced-Fort Prince George1760-1"},
        )
        self.assertIs(WAVE8_CHEROKEE_EXCLUSIONS, WAVE8_CHEROKEE_HOLDS)
        self.assertEqual(WAVE8_CHEROKEE_EXCLUSION_IDS, WAVE8_CHEROKEE_HOLD_IDS)
        self.assertEqual(
            WAVE8_CHEROKEE_RESERVED_IDS,
            WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_cherokee_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "holds": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 8,
                "new_sources": 9,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
            },
        )
        self.assertEqual(
            wave8_cherokee_cohort_counts(),
            {
                "anglo_cherokee_war_1760_1761": 3,
                "texas_cherokee_san_saba_1839": 1,
            },
        )

    def test_all_and_only_five_exact_label_rows_are_owned(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Cherokee Indians"
            or row.get("side_2_raw") == "Cherokee Indians"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_LABELS))
        self.assertEqual(
            validate_wave8_cherokee_queue_contracts(self.hced_rows),
            {"promotion_contracts": 4, "holds": 1, "reviewed_hced_rows": 5},
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
                WAVE8_CHEROKEE_CONTRACTS.get(candidate_id)
                or WAVE8_CHEROKEE_HOLDS[candidate_id]
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                disposition["raw_row_sha256"],
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-FutureCherokeeIndians1900-1",
                "side_1_raw": "Cherokee Indians",
                "side_2_raw": "Unreviewed opponent",
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Cherokee Indians inventory"):
            validate_wave8_cherokee_queue_contracts(future)

    def test_each_row_hash_is_pinned_and_queue_drift_fails_closed(self) -> None:
        self.assertEqual(
            validate_wave8_cherokee_queue_contracts(self.lane_rows),
            {"promotion_contracts": 4, "holds": 1, "reviewed_hced_rows": 5},
        )
        for candidate_id in sorted(WAVE8_CHEROKEE_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.lane_rows)
                next(
                    row for row in changed if row["candidate_id"] == candidate_id
                )["name"] += " tampered"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_cherokee_queue_contracts(changed)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Etchoe1760-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_cherokee_queue_contracts(missing)

        duplicated = [*self.lane_rows, copy.deepcopy(self.lane_rows[0])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_cherokee_queue_contracts(duplicated)

    def test_sources_and_event_bounded_entities_parse_and_install(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_CHEROKEE_SOURCES}
        self.assertEqual(len(source_by_id), 9)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_CHEROKEE_SOURCES}),
            9,
        )
        for source in WAVE8_CHEROKEE_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_CHEROKEE_ENTITIES}
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entity_by_id.items()
            },
            {
                ECHOE_1760_CHEROKEE: (1760, 1760),
                MONTGOMERIE_1760: (1760, 1760),
                LOUDOUN_CHEROKEE: (1760, 1760),
                LOUDOUN_GARRISON: (1760, 1760),
                GRANT_1761: (1761, 1761),
                ECHOE_1761_CHEROKEE: (1761, 1761),
                SAN_SABA_TEXAS: (1839, 1839),
                SAN_SABA_CHEROKEE: (1839, 1839),
            },
        )
        for entity in WAVE8_CHEROKEE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern tribal government", note)
            self.assertNotIn(
                entity["name"].casefold(),
                {"cherokee", "cherokee indian", "cherokee indians"},
            )
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        install_wave8_cherokee_entities(entities)
        install_wave8_cherokee_sources(sources)
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])
            self.assertEqual(entities[entity_id], entity_by_id[entity_id])
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])
            self.assertEqual(sources[source_id], source_by_id[source_id])

        collision = copy.deepcopy(entities)
        collision[ECHOE_1760_CHEROKEE] = {
            **collision[ECHOE_1760_CHEROKEE],
            "end_year": 1761,
        }
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_cherokee_entities(collision)

    def test_fort_prince_george_is_terminal_compound_event_hold(self) -> None:
        hold = WAVE8_CHEROKEE_HOLDS["hced-Fort Prince George1760-1"]
        self.assertEqual(
            hold["hold_category"],
            "compound_violence_without_single_tactical_outcome",
        )
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "compound_ambush_massacre_and_siege",
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
        self.assertIn("north carolina actor is wrong", reason)
        self.assertIn("hostage killings are not a competitive british victory", reason)
        self.assertIn("no single defensible tactical winner", reason)
        self.assertIn("cannot produce an elo result", reason)
        self.assertIn("never made a draw", reason)
        self.assertEqual(
            set(hold["evidence_refs"]),
            {
                "wave8_cherokee_ncpedia_etchoe",
                "wave8_cherokee_scencyclopedia_fort_prince_george",
            },
        )

    def test_dates_actors_outcomes_and_source_families_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_CHEROKEE_SOURCES}
        used_cherokee_entities = set()
        for candidate_id, contract in WAVE8_CHEROKEE_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["date_precision"],
                    canonical["date_text"],
                    canonical["granularity"],
                ),
                EXPECTED_DATES[candidate_id],
            )
            expected_winners, expected_losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["war_type"], "colonial_anti_colonial")
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
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            self.assertGreaterEqual(len(expected_families), 2)
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
            used_cherokee_entities.update(
                entity_id
                for entity_id in expected_winners | expected_losers
                if "cherokee" in entity_id
            )

        self.assertEqual(
            used_cherokee_entities,
            {
                ECHOE_1760_CHEROKEE,
                LOUDOUN_CHEROKEE,
                ECHOE_1761_CHEROKEE,
                SAN_SABA_CHEROKEE,
            },
        )
        self.assertEqual(WAVE8_CHEROKEE_OUTCOME_OVERRIDES, {})

    def test_emission_is_four_parseable_wins_without_a_timeless_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertNotIn("hced-Fort Prince George1760-1", by_candidate)

        forbidden_participant_ids = {
            "cherokee",
            "cherokee_indian",
            "cherokee_indians",
            "cherokee_nation",
        }
        observed_entities = set()
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(
                event["reviewed_granularity"],
                WAVE8_CHEROKEE_CONTRACTS[candidate_id]["canonical_event"][
                    "granularity"
                ],
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
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
            observed_entities.update(winners | losers)

        self.assertEqual(observed_entities, {entity["id"] for entity in WAVE8_CHEROKEE_ENTITIES})
        self.assertTrue(
            {ECHOE_1760_CHEROKEE, LOUDOUN_CHEROKEE}.isdisjoint(
                {ECHOE_1761_CHEROKEE, SAN_SABA_CHEROKEE}
            )
        )
        self.assertNotEqual(ECHOE_1761_CHEROKEE, SAN_SABA_CHEROKEE)

    def test_siege_surrender_and_massacre_granularity_are_not_conflated(self) -> None:
        raw_loudoun = next(
            row
            for row in self.lane_rows
            if row["candidate_id"] == "hced-Fort Loudoun1760-1"
        )
        raw_prince_george = next(
            row
            for row in self.lane_rows
            if row["candidate_id"] == "hced-Fort Prince George1760-1"
        )
        self.assertEqual(raw_loudoun["massacre_raw"], "Battle followed by massacre")
        self.assertEqual(raw_prince_george["massacre_raw"], "Battle followed by massacre")

        _, _, events = self._emit()
        loudoun = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Fort Loudoun1760-1"
        )
        self.assertEqual(loudoun["name"], "Siege of Fort Loudoun")
        self.assertEqual(loudoun["reviewed_granularity"], "siege")
        self.assertIn("capitulation", loudoun["summary"])
        self.assertIn("separate massacre episode", loudoun["summary"])
        self.assertEqual(
            [event for event in events if "Loudoun" in event["name"]],
            [loudoun],
        )

    def test_location_audit_quarantines_three_points_and_retains_loudoun(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}

        expected_points = {
            "hced-Etchoe1760-1",
            "hced-Etchoe1761-1",
            "hced-San Saba1839-1",
        }
        self.assertEqual(WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_CHEROKEE_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": frozenset()},
        )
        self.assertEqual(
            wave8_cherokee_location_quarantine_additions(),
            {"point": expected_points, "country": frozenset()},
        )
        for candidate_id in expected_points:
            self.assertNotIn("geometry", by_candidate[candidate_id])
            self.assertEqual(
                by_candidate[candidate_id]["modern_location_country"],
                "United States",
            )
            self.assertIn("location_provenance", by_candidate[candidate_id])

        loudoun = by_candidate["hced-Fort Loudoun1760-1"]
        self.assertEqual(
            loudoun["geometry"],
            {"type": "Point", "coordinates": [-84.2056419, 35.5967631]},
        )
        self.assertEqual(loudoun["modern_location_country"], "United States")
        self.assertIn("location_provenance", loudoun)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_neches_and_iwbd_duplicate_boundaries_fail_closed(self) -> None:
        self.assertEqual(WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS),
            {"hced-Neches1839-1"},
        )
        disposition = WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS[
            "hced-Neches1839-1"
        ]
        self.assertEqual(disposition["disposition"], "related_distinct_event")
        self.assertIn("15-16 July", disposition["reason"])
        self.assertIn("25 December", disposition["reason"])

        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_cherokee_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_probable_twins": 0,
            },
        )

        neches = next(
            row
            for row in self.hced_rows
            if row["candidate_id"] == "hced-Neches1839-1"
        )
        self.assertEqual(
            canonical_hced_row_sha256(neches),
            disposition["raw_row_sha256"],
        )
        changed_hced = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed_hced
            if row["candidate_id"] == "hced-Neches1839-1"
        )["name"] = "Changed Neches"
        with self.assertRaisesRegex(ValueError, "related Neches fingerprint changed"):
            validate_wave8_cherokee_integration_dispositions(
                changed_hced,
                self.iwbd_rows,
                existing,
            )

        future_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-san-saba",
                "name": "San Saba Fight",
                "start_date": "1839-12-25",
                "end_date": "1839-12-25",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_cherokee_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        future_release = [
            *existing,
            {
                "id": "future_echoe_duplicate",
                "name": "First Battle of Etchoe",
                "year": 1760,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed probable release duplicate"):
            validate_wave8_cherokee_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_entity_windows_and_existing_candidate_duplicates_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        too_short = copy.deepcopy(entities)
        too_short[ECHOE_1760_CHEROKEE]["end_year"] = 1759
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_cherokee_contracts(
                self.hced_rows,
                too_short,
                existing,
            )

        events = promote_wave8_cherokee_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_cherokee_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )


if __name__ == "__main__":
    unittest.main()
