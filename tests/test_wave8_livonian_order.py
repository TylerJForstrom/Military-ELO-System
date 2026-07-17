from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_livonian_order import (
    WAVE8_LIVONIAN_ORDER_CONTRACT_IDS,
    WAVE8_LIVONIAN_ORDER_CONTRACTS,
    WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_LIVONIAN_ORDER_ENTITIES,
    WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS,
    WAVE8_LIVONIAN_ORDER_FINAL_AUDIT_SIGNATURE,
    WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT,
    WAVE8_LIVONIAN_ORDER_HOLD_IDS,
    WAVE8_LIVONIAN_ORDER_HOLDS,
    WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_LIVONIAN_ORDER_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS,
    WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES,
    WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS,
    WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_RESERVED_IDS,
    WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_SOURCES,
    WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS,
    install_wave8_livonian_order_entities,
    install_wave8_livonian_order_sources,
    promote_wave8_livonian_order_contracts,
    validate_wave8_livonian_order_funnel,
    validate_wave8_livonian_order_integration_dispositions,
    validate_wave8_livonian_order_queue_contracts,
    wave8_livonian_order_audit_signature,
    wave8_livonian_order_cohort_counts,
    wave8_livonian_order_counts,
    wave8_livonian_order_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_livonian_order_"

TSARDOM = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"
LIVONIAN_BRANCH = "livonian_branch_teutonic_order_1237_1561"
SMOLINO_COALITION = "muscovite_novgorodian_pskovian_smolino_coalition_1502"
FELLIN_DEFENCE = "fellin_order_garrison_defence_1560"
NARVA_DEFENCE = "narva_order_city_castle_defence_1558"
ERGEME_FORCE = "ergeme_order_auxiliary_field_force_1560"


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Fellin1560-1": ({TSARDOM}, {FELLIN_DEFENCE}),
    "hced-Lake Smolino1502-1": ({LIVONIAN_BRANCH}, {SMOLINO_COALITION}),
    "hced-Narva1558-1": ({TSARDOM}, {NARVA_DEFENCE}),
    "hced-Oomuli1560-1": ({TSARDOM}, {ERGEME_FORCE}),
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


class Wave8LivonianOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_LIVONIAN_ORDER_RESERVED_IDS
        ]

    def _installed(self):
        fixture_entity_ids = {
            str(entity["id"]) for entity in WAVE8_LIVONIAN_ORDER_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_livonian_order_entities(entities)

        fixture_source_ids = {
            str(source["id"]) for source in WAVE8_LIVONIAN_ORDER_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_livonian_order_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_LIVONIAN_ORDER_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_livonian_order_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return events, entities, sources, existing

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        payload = {
            "contracts": WAVE8_LIVONIAN_ORDER_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_LIVONIAN_ORDER_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS
            ),
            "funnel_audit": WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT,
            "holds": WAVE8_LIVONIAN_ORDER_HOLDS,
            "integration_dispositions": WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT,
            "location_reviews": WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS,
            "outcome_overrides": WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": (
                WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS
            ),
            "row_dispositions": WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS,
            "sources": WAVE8_LIVONIAN_ORDER_SOURCES,
            "terminal_exclusions": WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS,
        }
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(
            digest,
            "03c1efc405bbf7befde877442d9186f2cdd40d3484bffbebeaa1f9e8fe35a892",
        )
        self.assertEqual(digest, wave8_livonian_order_audit_signature())
        self.assertEqual(digest, WAVE8_LIVONIAN_ORDER_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_livonian_order_counts(),
            {
                "country_quarantine_additions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 3,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 7,
                "new_entities": 5,
                "new_sources": 16,
                "newly_rated_events": 4,
                "outcome_overrides": 2,
                "point_quarantine_additions": 2,
                "promotion_contracts": 4,
                "related_hced_dispositions": 1,
                "reviewed_hced_rows": 7,
                "sole_blocker_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_livonian_order_cohort_counts(),
            {
                "livonian_war_1558_1561": 3,
                "muscovite_livonian_war_1501_1503": 1,
            },
        )

    def test_authoritative_funnel_pins_seven_rows_and_four_sole_blockers(self) -> None:
        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": (
                        "57fce904f7f47658baca08f28413afa99111f7d465efe0a7520c061c68e57adf"
                    ),
                    "events_touched": 7,
                    "failure_cases": {"zero_time_valid_candidates": 7},
                    "label": "livonian order",
                    "sole_blocker_events": 4,
                }
            ],
            "greedy_batch": {
                "ranking": [
                    {
                        "events_touched": 7,
                        "label": "livonian order",
                        "marginal_events": 4,
                        "newly_unblocked_candidate_id_sha256": (
                            "8d35ae2da31bf0da56b17ff6d5540d49513268b3142da604291f960c12a019a1"
                        ),
                    }
                ]
            },
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "label_failures": [
                        {
                            "failure_case": "zero_time_valid_candidates",
                            "label": "livonian order",
                        }
                    ],
                    "sole_blocker_label": (
                        "livonian order"
                        if candidate_id in WAVE8_LIVONIAN_ORDER_CONTRACT_IDS
                        else None
                    ),
                }
                for candidate_id in sorted(
                    WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS
                )
            ],
        }
        self.assertEqual(
            validate_wave8_livonian_order_funnel(historical_funnel),
            {
                "exact_label_rows": 7,
                "held_other_identity_rows": 3,
                "sole_blocker_rows": 4,
            },
        )
        exact_payload = "".join(
            f"{candidate_id}\n"
            for candidate_id in sorted(WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS)
        )
        sole_payload = "".join(
            f"{candidate_id}\n"
            for candidate_id in sorted(WAVE8_LIVONIAN_ORDER_CONTRACT_IDS)
        )
        self.assertEqual(
            hashlib.sha256(exact_payload.encode()).hexdigest(),
            WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT["event_candidate_id_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(sole_payload.encode()).hexdigest(),
            WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT[
                "newly_unblocked_candidate_id_sha256"
            ],
        )
        changed = copy.deepcopy(historical_funnel)
        next(
            row
            for row in changed["labels"]
            if row["label"] == "livonian order"
        )["sole_blocker_events"] = 5
        with self.assertRaisesRegex(ValueError, "funnel sole_blocker_events changed"):
            validate_wave8_livonian_order_funnel(changed)

        changed = copy.deepcopy(historical_funnel)
        next(
            row
            for row in changed["row_label_data"]
            if row.get("candidate_id") == "hced-Fellin1560-1"
        )["sole_blocker_label"] = None
        with self.assertRaisesRegex(ValueError, "funnel sole blockers changed"):
            validate_wave8_livonian_order_funnel(changed)

        self.assertFalse(
            any(
                row.get("label") == "livonian order"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Livonian Order lane must not remain unresolved",
        )
        live_row_ids = {
            str(row.get("candidate_id"))
            for row in self.funnel.get("row_label_data", [])
        }
        self.assertFalse(
            live_row_ids & WAVE8_LIVONIAN_ORDER_CONTRACT_IDS,
            "promoted Livonian Order candidates must not remain in live funnel rows",
        )

    def test_complete_exact_queue_inventory_and_raw_hashes_fail_closed(self) -> None:
        self.assertEqual(
            validate_wave8_livonian_order_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 4,
                "holds": 3,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 0,
            },
        )
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "livonian order"
            or normalize_label(row.get("side_2_raw")) == "livonian order"
        }
        self.assertEqual(set(exact_rows), WAVE8_LIVONIAN_ORDER_RESERVED_IDS)
        inventories = {
            **WAVE8_LIVONIAN_ORDER_CONTRACTS,
            **WAVE8_LIVONIAN_ORDER_HOLDS,
        }
        for candidate_id, row in exact_rows.items():
            self.assertEqual(
                canonical_hced_row_sha256(row),
                inventories[candidate_id]["raw_row_sha256"],
            )
            exact_sides = sum(
                normalize_label(row.get(field)) == "livonian order"
                for field in ("side_1_raw", "side_2_raw")
            )
            self.assertEqual(exact_sides, 1)

        for candidate_id in sorted(WAVE8_LIVONIAN_ORDER_RESERVED_IDS):
            changed = copy.deepcopy(self.hced_rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "name"
            ] += " tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_livonian_order_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Fellin1560-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_livonian_order_queue_contracts(missing)

        duplicated = [*self.hced_rows, copy.deepcopy(exact_rows["hced-Fellin1560-1"])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_livonian_order_queue_contracts(duplicated)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureLivonianOrder1561-1",
                "side_1_raw": "Livonian Order",
                "side_2_raw": "Unreviewed opponent",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Livonian Order inventory changed"):
            validate_wave8_livonian_order_queue_contracts(future)

    def test_sources_and_bounded_entities_parse_install_and_firewall_identity(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_LIVONIAN_ORDER_SOURCES
        }
        self.assertEqual(len(source_by_id), 16)
        self.assertEqual(
            len(
                {
                    source["source_family_id"]
                    for source in WAVE8_LIVONIAN_ORDER_SOURCES
                }
            ),
            16,
        )
        for source in WAVE8_LIVONIAN_ORDER_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_LIVONIAN_ORDER_ENTITIES
        }
        self.assertEqual(
            set(entity_by_id),
            {
                LIVONIAN_BRANCH,
                SMOLINO_COALITION,
                FELLIN_DEFENCE,
                NARVA_DEFENCE,
                ERGEME_FORCE,
            },
        )
        for entity in WAVE8_LIVONIAN_ORDER_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("livonian brothers of the sword", note)
            self.assertIn("coalition", note)
            self.assertLessEqual(set(entity["source_ids"]), set(source_by_id))
            self.assertNotIn(
                entity["name"].casefold(),
                {"livonian order", "teutonic order", "livonian confederation"},
            )
        self.assertEqual(
            (
                entity_by_id[LIVONIAN_BRANCH]["start_year"],
                entity_by_id[LIVONIAN_BRANCH]["end_year"],
            ),
            (1237, 1561),
        )
        for entity_id, entity in entity_by_id.items():
            if entity_id != LIVONIAN_BRANCH:
                self.assertEqual(entity["start_year"], entity["end_year"])

        entities, sources, _ = self._installed()
        install_wave8_livonian_order_entities(entities)
        install_wave8_livonian_order_sources(sources)
        for entity_id, fixture in entity_by_id.items():
            self.assertEqual(entities[entity_id], fixture)
        for source_id, fixture in source_by_id.items():
            self.assertEqual(sources[source_id], fixture)

        bad_entities = {LIVONIAN_BRANCH: {"id": LIVONIAN_BRANCH, "name": "collision"}}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_livonian_order_entities(bad_entities)
        bad_sources = {
            next(iter(source_by_id)): {
                "id": next(iter(source_by_id)),
                "title": "collision",
            }
        }
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_livonian_order_sources(bad_sources)

    def test_all_three_nonsole_rows_are_explicit_unknown_not_draw_holds(self) -> None:
        self.assertEqual(
            WAVE8_LIVONIAN_ORDER_HOLD_IDS,
            {
                "hced-Aizkraulke1279-1",
                "hced-Helmed1501-1",
                "hced-Wilkomierz1435-1",
            },
        )
        self.assertFalse(WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS)
        for candidate_id, hold in WAVE8_LIVONIAN_ORDER_HOLDS.items():
            self.assertEqual((hold["disposition"], hold["result_type"]), ("hold", "unknown"))
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertIn("not promoted", hold["hold_reason"].casefold())
            self.assertIn("draw", hold["hold_reason"].casefold())
            self.assertNotIn(candidate_id, WAVE8_LIVONIAN_ORDER_CONTRACTS)
            for forbidden in (
                "winner_side",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "outcome_source_ids",
                "outcome_source_family_ids",
            ):
                self.assertNotIn(forbidden, hold)

        self.assertIn(
            "Danish Tallinn",
            " ".join(
                WAVE8_LIVONIAN_ORDER_HOLDS["hced-Aizkraulke1279-1"][
                    "reviewed_actor_description"
                ]
            ),
        )
        pabaiskas = " ".join(
            WAVE8_LIVONIAN_ORDER_HOLDS["hced-Wilkomierz1435-1"][
                "reviewed_actor_description"
            ]
        )
        self.assertIn("Polish auxiliaries", pabaiskas)
        self.assertIn("Tatar allies", pabaiskas)

    def test_contract_dates_outcomes_sources_and_override_metadata_are_exact(self) -> None:
        expected = {
            "hced-Fellin1560-1": (
                "Siege and capture of Fellin (Viljandi)",
                "month",
                "August 1560",
                1,
                False,
                False,
            ),
            "hced-Lake Smolino1502-1": (
                "Battle of Lake Smolino",
                "day",
                "13 September 1502",
                1,
                True,
                False,
            ),
            "hced-Narva1558-1": (
                "Capture of Narva",
                "day",
                "11 May 1558",
                2,
                True,
                True,
            ),
            "hced-Oomuli1560-1": (
                "Battle of Ērģeme",
                "day",
                "2 August 1560",
                1,
                False,
                False,
            ),
        }
        source_by_id = {
            str(source["id"]): source for source in WAVE8_LIVONIAN_ORDER_SOURCES
        }
        for candidate_id, contract in WAVE8_LIVONIAN_ORDER_CONTRACTS.items():
            canonical = contract["canonical_event"]
            name, precision, date_text, winner_side, override, reversal = expected[
                candidate_id
            ]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                (precision, date_text),
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(
                (
                    contract["disposition"],
                    contract["result_type"],
                    contract["winner_side"],
                ),
                ("promote", "win", winner_side),
            )
            self.assertIs(contract["source_outcome_override"], override)
            self.assertIs(contract["outcome_reversal"], reversal)
            self.assertEqual(contract["actor_override"], "bounded_exact_opposing_forces")
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )

        self.assertEqual(
            set(WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES),
            {"hced-Lake Smolino1502-1", "hced-Narva1558-1"},
        )
        smolino = WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES[
            "hced-Lake Smolino1502-1"
        ]
        self.assertEqual(
            (
                smolino["raw_winner_raw"],
                smolino["raw_loser_raw"],
                smolino["raw_winner_loser_complete"],
            ),
            ("Draw", None, False),
        )
        self.assertEqual(smolino["corrected_winner_entity_ids"], [LIVONIAN_BRANCH])
        narva = WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES["hced-Narva1558-1"]
        self.assertEqual(
            (narva["raw_winner_raw"], narva["raw_loser_raw"]),
            ("Livonian Order", "Russia"),
        )
        self.assertEqual(narva["corrected_winner_entity_ids"], [TSARDOM])
        self.assertEqual(narva["override_kind"], "sourced_tactical_outcome_reversal")

    def test_emission_rates_only_four_bounded_tactical_results(self) -> None:
        events, entities, sources, _ = self._emit()
        self.assertEqual(len(events), 4)
        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            [
                "hced-Lake Smolino1502-1",
                "hced-Narva1558-1",
                "hced-Fellin1560-1",
                "hced-Oomuli1560-1",
            ],
        )
        self.assertFalse(
            {event["hced_candidate_id"] for event in events}
            & WAVE8_LIVONIAN_ORDER_HOLD_IDS
        )
        expected_aliases = {
            "hced-Fellin1560-1": ["Fellin"],
            "hced-Lake Smolino1502-1": ["Lake Smolino"],
            "hced-Narva1558-1": ["Narva"],
            "hced-Oomuli1560-1": ["Oomuli"],
        }
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
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
            self.assertEqual(
                (winners, losers),
                EXPECTED_WINNERS_AND_LOSERS[candidate_id],
            )
            self.assertTrue(
                all(
                    participant["result_class"]
                    in {"limited_victory", "limited_defeat"}
                    for participant in event["participants"]
                )
            )
            self.assertEqual(event["aliases"], expected_aliases[candidate_id])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertNotIn("hced_dataset", event["outcome_source_ids"])
            self.assertLessEqual(set(event["outcome_source_ids"]), set(sources))
            self.assertTrue(
                all(participant["entity_id"] in entities for participant in event["participants"])
            )

    def test_location_reviews_and_quarantines_are_promoted_only_and_local(self) -> None:
        self.assertEqual(
            wave8_livonian_order_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": frozenset(
                    {"hced-Lake Smolino1502-1", "hced-Oomuli1560-1"}
                ),
            },
        )
        self.assertEqual(
            WAVE8_LIVONIAN_ORDER_LOCATION_QUARANTINE_ADDITIONS,
            {
                "country": WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS,
            },
        )
        self.assertLessEqual(
            WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS,
            WAVE8_LIVONIAN_ORDER_CONTRACT_IDS,
        )
        self.assertEqual(
            set(WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS),
            WAVE8_LIVONIAN_ORDER_CONTRACT_IDS,
        )
        events, _, _, _ = self._emit()
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        for candidate_id in WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_candidate[candidate_id])
            self.assertIn("modern_location_country", by_candidate[candidate_id])
            self.assertIn("location_provenance", by_candidate[candidate_id])
        for candidate_id in WAVE8_LIVONIAN_ORDER_CONTRACT_IDS - (
            WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS
        ):
            self.assertIn("geometry", by_candidate[candidate_id])
            self.assertIn("modern_location_country", by_candidate[candidate_id])

    def test_related_hced_and_all_duplicate_surfaces_fail_closed(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_livonian_order_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )
        related = WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS[
            "hced-Seritsa1501-1"
        ]
        seritsa = next(
            row
            for row in self.hced_rows
            if row.get("candidate_id") == "hced-Seritsa1501-1"
        )
        self.assertEqual(canonical_hced_row_sha256(seritsa), related["raw_row_sha256"])
        self.assertIn("non-exact", related["reason"])

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row.get("candidate_id") == "hced-Seritsa1501-1"
        )["name"] += " tampered"
        with self.assertRaisesRegex(ValueError, "related HCED fingerprint changed"):
            validate_wave8_livonian_order_integration_dispositions(
                changed,
                self.iwbd_rows,
                existing,
            )

        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-FutureSmolino1502-1",
                "name": "Battle of Lake Smolino",
                "year_best": 1502,
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_livonian_order_integration_dispositions(
                future_hced,
                self.iwbd_rows,
                existing,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-ergeme",
                "name": "Ergeme",
                "start_date": "1560-01-01",
                "end_date": "1560-12-31",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_livonian_order_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        future_release = [
            *existing,
            {
                "id": "future_capture_narva",
                "name": "Capture of Narva",
                "year": 1558,
                "end_year": 1558,
                "aliases": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_livonian_order_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

        ownership_collision = [
            *existing,
            {
                "id": "future_owned_candidate",
                "name": "Unrelated",
                "year": 1900,
                "hced_candidate_id": "hced-Fellin1560-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidate ownership collision"):
            validate_wave8_livonian_order_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                ownership_collision,
            )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_LIVONIAN_ORDER_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned:
            self.assertEqual(owned_ids, set(WAVE8_LIVONIAN_ORDER_CONTRACT_IDS))
            self.assertEqual(len(owned), len(WAVE8_LIVONIAN_ORDER_CONTRACT_IDS))
            self.assertEqual(len({str(event["id"]) for event in owned}), len(owned))
            self.assertTrue(
                all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in owned)
            )
        self.assertFalse(
            WAVE8_LIVONIAN_ORDER_HOLD_IDS & owned_ids,
            "held Livonian Order candidates must never be integrated",
        )

    def test_promotion_rejects_existing_candidate_name_and_missing_entity(self) -> None:
        events, entities, _, existing = self._emit()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_livonian_order_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        duplicate_name = {
            "id": "future_duplicate_name",
            "name": "Battle of Lake Smolino",
            "year": 1502,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_livonian_order_contracts(
                self.hced_rows,
                entities,
                [*existing, duplicate_name],
            )

        missing_entity = dict(entities)
        missing_entity.pop(SMOLINO_COALITION)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_livonian_order_contracts(
                self.hced_rows,
                missing_entity,
                existing,
            )


if __name__ == "__main__":
    unittest.main()
