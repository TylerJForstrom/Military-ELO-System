import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_polisario as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_polisario_"
ELPS = "sahrawi_popular_liberation_army_1973_1991"
MAURITANIA = "islamic_republic_mauritania_1960_1978"
MOROCCO = "clio_q1028_1670_ae522447"

EXPECTED_HASHES = {
    "hced-Nouakchott1976-1": (
        "7ccbe779e4264c744ea464506e72a56543a525434d3725d474b306ca0419b50c"
    ),
    "hced-Oum Droussa1977-1": (
        "08c92881fe52f6cfecc8e078b9da5f4c60f4f710d2a909bf5d9125bf71edd9d5"
    ),
    "hced-Smara1976-1": (
        "13c95eb5296ced5ced5b95159362276f85a857e259a2c7034430cb4f023b0f17"
    ),
    "hced-Tan-Tan1979-1": (
        "bdcad53b897455dbb2d9c599b9be5c15e547f401a7e7140b756d3a7aa618fc7a"
    ),
    "hced-Zag1980-1": (
        "4121b4b796474aec2d441d9d9c9bfaf3e1bfbd1e354308b0d99586314d2839bf"
    ),
    "hced-Zouerate1977-1": (
        "bdbd43f2cffd0c67246d80e8251f47729a56332203029b57ab9854d8f468bbd4"
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
    labels = []
    for row in lane.WAVE8_POLISARIO_FUNNEL_AUDIT.values():
        fixture = copy.deepcopy(row)
        zero = fixture.pop("zero_time_valid_candidates")
        fixture["failure_cases"] = {"zero_time_valid_candidates": zero}
        labels.append(fixture)
    return {"labels": labels}


class Wave8PolisarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.ucdp_actor_rows = _jsonl(
            ROOT / "data/review/ucdp-actor-26.1-candidates.jsonl"
        )
        cls.ucdp_conflict_rows = _jsonl(
            ROOT / "data/review/ucdp-conflict-26.1-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw"))
            in {"polisaro", "polisario", "polisario rebels"}
            or normalize_label(row.get("side_2_raw"))
            in {"polisaro", "polisario", "polisario rebels"}
        ]

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_POLISARIO_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_POLISARIO_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_polisario_entities(entities)
        lane.install_wave8_polisario_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_polisario_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_all_six_exact_rows_and_full_fingerprints_are_pinned(self):
        self.assertEqual(lane.WAVE8_POLISARIO_ROW_HASHES, EXPECTED_HASHES)
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(len(rows), len(self.exact_rows))
        self.assertEqual(
            {
                normalize_label(value)
                for row in self.exact_rows
                for value in (row.get("side_1_raw"), row.get("side_2_raw"))
                if normalize_label(value)
                in {"polisaro", "polisario", "polisario rebels"}
            },
            {"polisaro", "polisario", "polisario rebels"},
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_partition_is_exact_three_promotions_three_holds(self):
        self.assertEqual(
            lane.validate_wave8_polisario_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 6,
                "exact_labels": 3,
                "holds": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            lane.WAVE8_POLISARIO_CONTRACT_IDS,
            {
                "hced-Nouakchott1976-1",
                "hced-Oum Droussa1977-1",
                "hced-Tan-Tan1979-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_POLISARIO_HOLD_IDS,
            {
                "hced-Smara1976-1",
                "hced-Zag1980-1",
                "hced-Zouerate1977-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_POLISARIO_CONTRACT_IDS | lane.WAVE8_POLISARIO_HOLD_IDS,
            lane.WAVE8_POLISARIO_RESERVED_IDS,
        )
        self.assertFalse(
            lane.WAVE8_POLISARIO_CONTRACT_IDS & lane.WAVE8_POLISARIO_HOLD_IDS
        )

    def test_historical_three_label_funnel_is_pinned(self):
        self.assertEqual(
            lane.validate_wave8_polisario_funnel(_historical_funnel()),
            {
                "events_touched": 6,
                "labels": 3,
                "sole_blocker_events": 6,
                "zero_time_valid_candidates": 6,
            },
        )
        live = [
            row
            for row in self.funnel.get("labels", [])
            if row.get("label") in lane.WAVE8_POLISARIO_FUNNEL_AUDIT
        ]
        if live:
            self.assertEqual(len(live), 3)
            lane.validate_wave8_polisario_funnel(self.funnel)

    def test_two_new_identities_are_bounded_alias_free_and_parse(self):
        self.assertEqual(len(lane.WAVE8_POLISARIO_ENTITIES), 2)
        entities = {str(item["id"]): item for item in lane.WAVE8_POLISARIO_ENTITIES}
        self.assertEqual(
            (entities[ELPS]["start_year"], entities[ELPS]["end_year"]),
            (1973, 1991),
        )
        self.assertEqual(
            (
                entities[MAURITANIA]["start_year"],
                entities[MAURITANIA]["end_year"],
            ),
            (1960, 1978),
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("inherit no rating", entity["continuity_note"])
            Entity.from_dict(entity)

        release = {str(item["id"]): item for item in self.release_entities}
        self.assertIn(MOROCCO, release)
        self.assertEqual(
            (release[MOROCCO]["start_year"], release[MOROCCO]["end_year"]),
            (1670, 2024),
        )
        self.assertNotIn(MOROCCO, entities)

    def test_sources_parse_and_outcomes_have_independent_families(self):
        self.assertEqual(len(lane.WAVE8_POLISARIO_SOURCES), 10)
        source_ids = {str(source["id"]) for source in lane.WAVE8_POLISARIO_SOURCES}
        for source in lane.WAVE8_POLISARIO_SOURCES:
            Source.from_dict(source)
        consumed = {
            str(source_id)
            for entity in lane.WAVE8_POLISARIO_ENTITIES
            for source_id in entity["source_ids"]
        }
        for contract in lane.WAVE8_POLISARIO_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )
            self.assertEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            consumed.update(contract["evidence_refs"])
        for hold in lane.WAVE8_POLISARIO_HOLDS.values():
            consumed.update(hold["evidence_refs"])
        for reason in lane.WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS.values():
            consumed.update(reason["evidence_refs"])
        self.assertEqual(consumed, source_ids)

    def test_promotions_pin_winners_losers_and_joint_oum_drouss_coalition(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Nouakchott1976-1": ({MAURITANIA}, {ELPS}),
            "hced-Oum Droussa1977-1": ({ELPS}, {MOROCCO, MAURITANIA}),
            "hced-Tan-Tan1979-1": ({ELPS}, {MOROCCO}),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(
                    {
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        participant["entity_id"]
                        for participant in event["participants"]
                        if participant["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], "colonial_anti_colonial")
                Event.from_dict(event)
        oum = events["hced-Oum Droussa1977-1"]
        losers = [
            participant
            for participant in oum["participants"]
            if participant["termination"] == "engagement_defeat"
        ]
        self.assertEqual(len(losers), 2)
        self.assertTrue(all(item["role"] == "major_ally" for item in losers))
        self.assertTrue(all(item["contribution"] == 0.5 for item in losers))

    def test_canonical_names_dates_and_tactical_scope_are_pinned(self):
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected = {
            "hced-Nouakchott1976-1": (
                "Nouakchott raid (June 1976)",
                1976,
                "day_range",
                "raid_on_the_capital_and_immediate_pursuit",
            ),
            "hced-Oum Droussa1977-1": (
                "Battle of Sebkhat Oum Drouss",
                1977,
                "day_range",
                "ambush_of_joint_moroccan_mauritanian_column",
            ),
            "hced-Tan-Tan1979-1": (
                "Battle of Tan-Tan (1979)",
                1979,
                "day",
                "raid_and_temporary_occupation_of_tan_tan",
            ),
        }
        for candidate_id, (name, year, precision, granularity) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual((event["year"], event["end_year"]), (year, year))
                self.assertEqual(event["date_precision"], precision)
                self.assertEqual(event["reviewed_granularity"], granularity)
                self.assertEqual(
                    event["canonical_event_key"],
                    lane.WAVE8_POLISARIO_CONTRACTS[candidate_id]["canonical_event"][
                        "canonical_key"
                    ],
                )

    def test_smara_zag_and_zouerate_are_unknown_holds_never_draws(self):
        expected_categories = {
            "hced-Smara1976-1": (
                "source_draw_is_incomplete_and_no_discrete_1976_result_is_attested"
            ),
            "hced-Zag1980-1": "no_independent_match_for_hced_winner_claim",
            "hced-Zouerate1977-1": (
                "multiple_1977_zouerate_actions_cannot_be_uniquely_aligned"
            ),
        }
        for candidate_id, category in expected_categories.items():
            with self.subTest(candidate_id=candidate_id):
                hold = lane.WAVE8_POLISARIO_HOLDS[candidate_id]
                self.assertEqual(hold["disposition"], "hold")
                self.assertEqual(hold["hold_category"], category)
                self.assertEqual(hold["result_type"], "unknown")
                self.assertEqual(hold["reviewed_outcome"], "unknown_not_draw")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertIn("unknown", hold["hold_reason"].casefold())
        events = self._events()
        self.assertFalse(
            lane.WAVE8_POLISARIO_HOLD_IDS
            & {event["hced_candidate_id"] for event in events}
        )
        self.assertFalse(
            any(
                "inconclusive" in participant["termination"]
                for event in events
                for participant in event["participants"]
            )
        )

    def test_oum_drouss_point_and_country_are_quarantined_only_there(self):
        candidate_id = "hced-Oum Droussa1977-1"
        self.assertEqual(lane.WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS, {candidate_id})
        self.assertEqual(
            lane.WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS,
            {candidate_id},
        )
        reason = lane.WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS[candidate_id]
        self.assertEqual(reason["actions"], ["withhold_country", "withhold_point"])
        self.assertEqual(reason["raw_country"], "Mauritannia")
        self.assertEqual(reason["raw_point"], [-11.9790041, 21.8864169])

        events = {event["hced_candidate_id"]: event for event in self._events()}
        oum = events[candidate_id]
        for key in ("geometry", "modern_location_country", "location_provenance"):
            self.assertNotIn(key, oum)
        expected_retained = {
            "hced-Nouakchott1976-1": ("Mauritania", [-15.9582372, 18.0735299]),
            "hced-Tan-Tan1979-1": ("Morocco", [-11.0987374, 28.4380408]),
        }
        for event_id, (country, coordinates) in expected_retained.items():
            event = events[event_id]
            self.assertEqual(event["modern_location_country"], country)
            self.assertEqual(event["geometry"]["coordinates"], coordinates)
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )
        self.assertEqual(
            lane.validate_wave8_polisario_emissions(events.values()),
            {
                "coalition_events": 1,
                "events": 3,
                "participants": 7,
                "retained_countries": 2,
                "retained_points": 2,
            },
        )

    def test_ucdp_discovery_context_never_rates_automatically(self):
        context = lane.WAVE8_POLISARIO_DISCOVERY_CONTEXT
        self.assertIs(context["do_not_rate_automatically"], True)
        actor = next(
            row
            for row in self.ucdp_actor_rows
            if row["candidate_id"] == context["ucdp_actor_candidate_id"]
        )
        self.assertIs(actor["do_not_rate_automatically"], True)
        self.assertEqual(actor["raw"]["ActorId"], context["ucdp_actor_id"])
        self.assertEqual(actor["raw"]["NameData"], "POLISARIO")
        conflict_rows = [
            row
            for row in self.ucdp_conflict_rows
            if row["raw"].get("conflict_id") == context["ucdp_conflict_id"]
            and row["raw"].get("side_b_id") == context["ucdp_actor_id"]
        ]
        self.assertTrue(conflict_rows)
        self.assertTrue(
            all(row["do_not_rate_automatically"] is True for row in conflict_rows)
        )
        emitted_ids = {event["hced_candidate_id"] for event in self._events()}
        self.assertEqual(emitted_ids, lane.WAVE8_POLISARIO_CONTRACT_IDS)
        self.assertTrue(all(event_id.startswith("hced-") for event_id in emitted_ids))

    def test_preintegration_duplicate_audit_is_zero_and_future_twins_fail(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_polisario_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        fixtures = {
            "hced": (
                [
                    *copy.deepcopy(self.hced_rows),
                    {
                        "candidate_id": "hced-future-tan-tan-twin",
                        "name": "Battle of Tan-Tan",
                        "year_low": 1979,
                    },
                ],
                self.iwbd_rows,
                existing,
            ),
            "iwbd": (
                self.hced_rows,
                [
                    *copy.deepcopy(self.iwbd_rows),
                    {
                        "candidate_id": "iwbd-future-oum-drouss-twin",
                        "batname": "Oum Drouss",
                        "batyear": 1977,
                    },
                ],
                existing,
            ),
            "release": (
                self.hced_rows,
                self.iwbd_rows,
                [
                    *copy.deepcopy(existing),
                    {
                        "id": "future-nouakchott-twin",
                        "name": "Raid on Nouakchott",
                        "year": 1976,
                    },
                ],
            ),
        }
        for view, (hced, iwbd, release) in fixtures.items():
            with self.subTest(view=view):
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_polisario_integration_dispositions(
                        hced,
                        iwbd,
                        release,
                    )

    def test_queue_fingerprints_and_semantic_guards_fail_closed(self):
        extra = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(
            next(
                item
                for item in extra
                if item["candidate_id"] == "hced-Tan-Tan1979-1"
            )
        )
        row["candidate_id"] = "hced-future-polisario-row"
        extra.append(row)
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_polisario_queue_contracts(extra)

        fingerprint = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in fingerprint
            if item["candidate_id"] == "hced-Nouakchott1976-1"
        )
        row["winner_raw"] = "Polisaro"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_polisario_queue_contracts(fingerprint)

        def pinned_hash(row):
            candidate_id = str(row.get("candidate_id"))
            if candidate_id in EXPECTED_HASHES:
                return EXPECTED_HASHES[candidate_id]
            return canonical_hced_row_sha256(row)

        outcome = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in outcome
            if item["candidate_id"] == "hced-Tan-Tan1979-1"
        )
        row["winner_raw"] = "Morocco"
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "promoted outcome alignment drift"):
                lane.validate_wave8_polisario_queue_contracts(outcome)

        hold = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in hold
            if item["candidate_id"] == "hced-Smara1976-1"
        )
        row["winner_loser_complete"] = True
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "unknown-hold guard drift"):
                lane.validate_wave8_polisario_queue_contracts(hold)

    def test_promoter_and_emission_validator_fail_closed_on_drift(self):
        entities, _, existing = self._installed()
        events = lane.promote_wave8_polisario_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_polisario_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_polisario_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-tan-tan-duplicate",
                        "name": "Battle of Tan-Tan (1979)",
                        "year": 1979,
                    },
                ],
            )
        missing = dict(entities)
        missing.pop(ELPS)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_polisario_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        drifted = copy.deepcopy(events)
        drifted[0]["participants"][0]["termination"] = "inconclusive_engagement"
        with self.assertRaisesRegex(ValueError, "emitted contract drift"):
            lane.validate_wave8_polisario_emissions(drifted)

    def test_installers_are_idempotent_and_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_polisario_entities(entities)
        lane.install_wave8_polisario_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)

        entities[ELPS]["end_year"] = 1992
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_polisario_entities(entities)
        source_id = str(lane.WAVE8_POLISARIO_SOURCES[0]["id"])
        sources[source_id]["title"] = "drifted title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_polisario_sources(sources)

    def test_counts_metadata_and_final_audit_signature_are_pinned(self):
        self.assertEqual(
            lane.wave8_polisario_counts(),
            {
                "country_quarantine_additions": 1,
                "holds": 3,
                "new_entities": 2,
                "new_sources": 10,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 1,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_polisario_cohort_counts(),
            {"western_sahara_war_polisario_exact_1976_1980": 6},
        )
        self.assertEqual(
            lane.wave8_polisario_audit_signature(),
            "6c082497b0b7b60de2af0fd882767977abae57b9b78e715b2105b2a56952526e",
        )
        self.assertEqual(
            lane.wave8_polisario_audit_signature(),
            lane.WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_polisario_metadata(),
            {
                "counts": lane.wave8_polisario_counts(),
                "cohorts": lane.wave8_polisario_cohort_counts(),
                "country_quarantine_additions": ["hced-Oum Droussa1977-1"],
                "final_audit_signature": lane.WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE,
                "held_candidate_ids": sorted(lane.WAVE8_POLISARIO_HOLD_IDS),
                "point_quarantine_additions": ["hced-Oum Droussa1977-1"],
                "promoted_candidate_ids": sorted(lane.WAVE8_POLISARIO_CONTRACT_IDS),
            },
        )

    def test_current_release_is_all_or_none_for_future_integration(self):
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_POLISARIO_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        self.assertIn(owned_ids, (set(), set(lane.WAVE8_POLISARIO_CONTRACT_IDS)))
        if not owned_ids:
            return
        self.assertEqual(
            lane.validate_wave8_polisario_emissions(owned),
            {
                "coalition_events": 1,
                "events": 3,
                "participants": 7,
                "retained_countries": 2,
                "retained_points": 2,
            },
        )
        release_entities = {str(item["id"]): item for item in self.release_entities}
        self.assertLessEqual({ELPS, MAURITANIA}, set(release_entities))
        release_source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_POLISARIO_SOURCES},
            release_source_ids,
        )


if __name__ == "__main__":
    unittest.main()
