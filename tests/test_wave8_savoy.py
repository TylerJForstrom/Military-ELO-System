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
from military_elo.promotion.wave8_savoy import (
    WAVE8_SAVOY_CONTRACT_IDS,
    WAVE8_SAVOY_CONTRACTS,
    WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS,
    WAVE8_SAVOY_ENTITIES,
    WAVE8_SAVOY_EXCLUSION_IDS,
    WAVE8_SAVOY_EXCLUSIONS,
    WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS,
    WAVE8_SAVOY_FINAL_AUDIT_SIGNATURE,
    WAVE8_SAVOY_HOLD_IDS,
    WAVE8_SAVOY_HOLDS,
    WAVE8_SAVOY_INTEGRATION_DISPOSITIONS,
    WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SAVOY_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_SAVOY_LOCATION_REVIEWS,
    WAVE8_SAVOY_NONPROMOTIONS,
    WAVE8_SAVOY_OUTCOME_OVERRIDES,
    WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS,
    WAVE8_SAVOY_RESERVED_IDS,
    WAVE8_SAVOY_SOURCES,
    install_wave8_savoy_entities,
    install_wave8_savoy_sources,
    promote_wave8_savoy_contracts,
    validate_wave8_savoy_integration_dispositions,
    validate_wave8_savoy_queue_contracts,
    wave8_savoy_audit_signature,
    wave8_savoy_cohort_counts,
    wave8_savoy_counts,
    wave8_savoy_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_savoy_"

SAVOYARD_CRUSADE_ID = "amadeus_vi_savoyard_crusade_1366_1367"
DUCAL_SAVOY_ID = "savoyard_state_ducal_1416_1713"
SFORZA_VENETIAN_ID = "sforza_venetian_borgomanero_coalition_1449"
GENEVA_REPUBLIC_ID = "republic_geneva_1536_1798"


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


EXPECTED_RAW_LABELS = {
    "hced-Borgomanero1449-1": ("Milan", "Savoy", "Milan", "Savoy"),
    "hced-Casale1628-1": ("France", "Savoy", "France", "Savoy"),
    "hced-Cassano1705-1": ("France", "Savoy", "France", "Savoy"),
    "hced-Gallipoli1366-1": (
        "Savoy",
        "Ottoman Empire",
        "Savoy",
        "Ottoman Empire",
    ),
    "hced-Geneva1602-1": ("Geneva", "Savoy", "Geneva", "Savoy"),
    "hced-Nice1543-1": (
        "Ottoman Empire",
        "Savoy",
        "Ottoman Empire",
        "Savoy",
    ),
    "hced-Staffarda1690-1": ("France", "Savoy", "France", "Savoy"),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Borgomanero1449-1": (
        {SFORZA_VENETIAN_ID},
        {"kingdom_france", DUCAL_SAVOY_ID},
    ),
    "hced-Gallipoli1366-1": ({SAVOYARD_CRUSADE_ID}, {"ottoman_empire"}),
    "hced-Geneva1602-1": ({GENEVA_REPUBLIC_ID}, {DUCAL_SAVOY_ID}),
    "hced-Nice1543-1": (
        {"kingdom_france", "ottoman_empire"},
        {DUCAL_SAVOY_ID},
    ),
    "hced-Staffarda1690-1": (
        {"kingdom_france"},
        {DUCAL_SAVOY_ID, "spanish_empire"},
    ),
}


EXPECTED_DATES = {
    "hced-Borgomanero1449-1": (
        "day_range",
        "20-23 April 1449 (source date variance)",
    ),
    "hced-Gallipoli1366-1": ("day_range", "22-26 August 1366"),
    "hced-Geneva1602-1": (
        "day_range",
        "night of 11-12 December 1602 Old Style (21-22 December New Style)",
    ),
    "hced-Nice1543-1": ("day_range", "10-22 August 1543"),
    "hced-Staffarda1690-1": ("day", "18 August 1690"),
}


EXPECTED_COUNTRIES = {
    "hced-Borgomanero1449-1": "Italy",
    "hced-Gallipoli1366-1": "Turkey",
    "hced-Geneva1602-1": "Switzerland",
    "hced-Nice1543-1": "France",
    "hced-Staffarda1690-1": "Italy",
}


class Wave8SavoyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_SAVOY_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_savoy_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_SAVOY_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_savoy_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_SAVOY_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_savoy_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_SAVOY_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_SAVOY_ENTITIES,
            "exclusions": WAVE8_SAVOY_EXCLUSIONS,
            "expected_candidate_ids": sorted(
                WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_SAVOY_HOLDS,
            "integration_dispositions": WAVE8_SAVOY_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT,
            "location_reviews": WAVE8_SAVOY_LOCATION_REVIEWS,
            "outcome_overrides": WAVE8_SAVOY_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_SAVOY_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_SAVOY_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_savoy_audit_signature(), independent_signature)
        self.assertEqual(
            WAVE8_SAVOY_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(
            WAVE8_SAVOY_HOLD_IDS,
            {"hced-Cassano1705-1"},
        )
        self.assertEqual(
            WAVE8_SAVOY_EXCLUSION_IDS,
            {"hced-Casale1628-1"},
        )
        self.assertEqual(WAVE8_SAVOY_RESERVED_IDS, set(EXPECTED_RAW_LABELS))
        self.assertEqual(
            wave8_savoy_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "exclusions": 1,
                "holds": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "location_reviews": 5,
                "new_entities": 4,
                "new_sources": 16,
                "newly_rated_events": 5,
                "outcome_overrides": 0,
                "point_quarantine_additions": 0,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_savoy_cohort_counts(),
            {
                "geneva_escalade_1602": 1,
                "italian_war_nice_1543": 1,
                "milanese_succession_borgomanero_1449": 1,
                "nine_years_war_staffarda_1690": 1,
                "savoyard_crusade_gallipoli_1366": 1,
            },
        )

    def test_all_and_only_seven_savoy_rows_are_hash_pinned_fail_closed(self) -> None:
        exact_label_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Savoy"
            or row.get("side_2_raw") == "Savoy"
        }
        self.assertEqual(set(exact_label_rows), set(EXPECTED_RAW_LABELS))
        dispositions = {
            **WAVE8_SAVOY_CONTRACTS,
            **WAVE8_SAVOY_NONPROMOTIONS,
        }
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
                dispositions[candidate_id]["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_savoy_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 5,
                "holds": 1,
                "exclusions": 1,
                "reviewed_hced_rows": 7,
            },
        )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Nice1543-1"
        )["winner_raw"] = "Savoy"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_savoy_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Cassano1705-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_savoy_queue_contracts(missing)

        future = copy.deepcopy(self.hced_rows)
        extra = copy.deepcopy(exact_label_rows["hced-Geneva1602-1"])
        extra["candidate_id"] = "hced-FutureSavoy1603-1"
        extra["source_record_id"] = "FutureSavoy1603"
        extra["source_row"] = 999999
        future.append(extra)
        with self.assertRaisesRegex(ValueError, "exact Savoy inventory changed"):
            validate_wave8_savoy_queue_contracts(future)

    def test_sources_and_bounded_entities_parse_install_and_do_not_bridge(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_SAVOY_SOURCES}
        self.assertEqual(len(source_by_id), 16)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_SAVOY_SOURCES}),
            16,
        )
        for source in WAVE8_SAVOY_SOURCES:
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SAVOY_ENTITIES}
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entity_by_id.items()
            },
            {
                SAVOYARD_CRUSADE_ID: (1366, 1367),
                DUCAL_SAVOY_ID: (1416, 1713),
                SFORZA_VENETIAN_ID: (1449, 1449),
                GENEVA_REPUBLIC_ID: (1536, 1798),
            },
        )
        forbidden_names = {
            "house of savoy",
            "piedmont",
            "savoy",
            "savoyard",
            "savoyards",
        }
        for entity in WAVE8_SAVOY_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn(str(entity["name"]).casefold(), forbidden_names)
            self.assertIn(
                "no rating is inherited",
                str(entity["continuity_note"]).casefold(),
            )
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])

    def test_installers_are_idempotent_deep_copying_and_fail_on_collision(self) -> None:
        entity_fixture = WAVE8_SAVOY_ENTITIES[0]
        source_fixture = WAVE8_SAVOY_SOURCES[0]

        entities = {}
        install_wave8_savoy_entities(entities)
        install_wave8_savoy_entities(entities)
        entities[str(entity_fixture["id"])]["name"] = "mutated copy"
        self.assertNotEqual(entity_fixture["name"], "mutated copy")
        bad_entities = {
            str(entity_fixture["id"]): {
                **copy.deepcopy(entity_fixture),
                "name": "collision",
            }
        }
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_savoy_entities(bad_entities)

        sources = {}
        install_wave8_savoy_sources(sources)
        install_wave8_savoy_sources(sources)
        sources[str(source_fixture["id"])]["title"] = "mutated copy"
        self.assertNotEqual(source_fixture["title"], "mutated copy")
        bad_sources = {
            str(source_fixture["id"]): {
                **copy.deepcopy(source_fixture),
                "title": "collision",
            }
        }
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_savoy_sources(bad_sources)

    def test_exact_dates_actors_coalitions_and_outcomes_are_pinned(self) -> None:
        self.assertEqual(WAVE8_SAVOY_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in WAVE8_SAVOY_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                EXPECTED_DATES[candidate_id],
            )
            self.assertEqual(canonical["granularity"], "engagement")
            self.assertEqual(contract["result_type"], "win")
            self.assertNotEqual(contract["result_type"], "draw")
            self.assertEqual(contract["winner_side"], 1)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

        self.assertEqual(
            set(WAVE8_SAVOY_CONTRACTS["hced-Borgomanero1449-1"][
                "side_1_entity_ids"
            ]),
            {SFORZA_VENETIAN_ID},
        )
        self.assertEqual(
            set(WAVE8_SAVOY_CONTRACTS["hced-Borgomanero1449-1"][
                "side_2_entity_ids"
            ]),
            {"kingdom_france", DUCAL_SAVOY_ID},
        )
        self.assertEqual(
            set(WAVE8_SAVOY_CONTRACTS["hced-Nice1543-1"]["side_1_entity_ids"]),
            {"kingdom_france", "ottoman_empire"},
        )
        self.assertNotIn(
            "habsburg_monarchy",
            WAVE8_SAVOY_CONTRACTS["hced-Staffarda1690-1"][
                "side_2_entity_ids"
            ],
        )

    def test_nonpromotions_are_explicit_and_never_turn_unknown_into_draw(self) -> None:
        self.assertEqual(set(WAVE8_SAVOY_HOLDS), {"hced-Cassano1705-1"})
        self.assertEqual(set(WAVE8_SAVOY_EXCLUSIONS), {"hced-Casale1628-1"})
        forbidden_rate_keys = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        for disposition in WAVE8_SAVOY_NONPROMOTIONS.values():
            self.assertTrue(disposition["unknown_is_never_draw"])
            self.assertFalse(forbidden_rate_keys & set(disposition))
            self.assertIn("draw", disposition["hold_reason"].casefold())

        cassano = WAVE8_SAVOY_HOLDS["hced-Cassano1705-1"]
        self.assertEqual(cassano["disposition"], "research_hold")
        self.assertEqual(cassano["reviewed_outcome"], "unresolved_conflict")
        self.assertIn("prince eugene", cassano["hold_reason"].casefold())
        self.assertIn("imperial army", cassano["hold_reason"].casefold())

        casale = WAVE8_SAVOY_EXCLUSIONS["hced-Casale1628-1"]
        self.assertEqual(casale["disposition"], "terminal_exclusion")
        self.assertEqual(casale["reviewed_outcome"], "not_a_valid_event_assertion")
        self.assertEqual(
            casale["canonical_event"]["granularity"],
            "source_conflation",
        )
        reason = casale["hold_reason"].casefold()
        for token in ("spanish", "casale", "sampeyre", "location", "sides"):
            self.assertIn(token, reason)

    def test_emitted_events_are_parseable_exact_and_never_invent_draws(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 5)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertEqual(
            [event["year"] for event in events],
            [1366, 1449, 1543, 1602, 1690],
        )
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
            self.assertFalse(
                any(
                    "draw" in participant["termination"]
                    for participant in event["participants"]
                )
            )
            self.assertFalse(
                {"savoy", "house_of_savoy", "piedmont"} & (winners | losers)
            )
            contract = WAVE8_SAVOY_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

        entities, _, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_savoy_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_outcome_sources_and_family_provenance_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_SAVOY_SOURCES}
        for candidate_id, contract in WAVE8_SAVOY_CONTRACTS.items():
            evidence_ids = list(contract["evidence_refs"])
            outcome_ids = list(contract["outcome_source_ids"])
            self.assertEqual(evidence_ids, sorted(set(evidence_ids)))
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
            self.assertTrue(outcome_ids, candidate_id)
            self.assertTrue(set(outcome_ids) <= set(evidence_ids))
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in outcome_ids
                    }
                ),
            )
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

    def test_location_audit_retains_all_five_reviewed_points_and_countries(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}

        self.assertEqual(set(WAVE8_SAVOY_LOCATION_REVIEWS), set(by_candidate))
        self.assertEqual(WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_SAVOY_LOCATION_QUARANTINE_ADDITIONS,
            {"point": frozenset(), "country": frozenset()},
        )
        self.assertEqual(
            wave8_savoy_location_quarantine_additions(),
            {"point": frozenset(), "country": frozenset()},
        )
        for candidate_id, country in EXPECTED_COUNTRIES.items():
            self.assertEqual(
                WAVE8_SAVOY_LOCATION_REVIEWS[candidate_id]["action"],
                "retain_point_and_country",
            )
            self.assertIn("geometry", by_candidate[candidate_id])
            self.assertEqual(
                by_candidate[candidate_id]["modern_location_country"],
                country,
            )
            self.assertIn("location_provenance", by_candidate[candidate_id])
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_duplicate_and_cross_lane_audits_fail_closed(self) -> None:
        self.assertEqual(WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS),
            {"hced-Casale1629-1"},
        )
        self.assertEqual(
            validate_wave8_savoy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_probable_twins": 0,
            },
        )

        future_iwbd = copy.deepcopy(self.iwbd_rows)
        future_iwbd.append(
            {
                "candidate_id": "iwbd-future-staffarda",
                "name": "Staffarda",
                "year": 1690,
            }
        )
        with self.assertRaisesRegex(ValueError, "unadjudicated IWBD duplicate"):
            validate_wave8_savoy_integration_dispositions(
                self.hced_rows,
                future_iwbd,
            )

        future_release = [
            {
                "id": "future-staffarda",
                "name": "Battle of Staffarda",
                "year": 1690,
                "hced_candidate_id": "hced-future-staffarda",
            }
        ]
        with self.assertRaisesRegex(ValueError, "unadjudicated release duplicates"):
            validate_wave8_savoy_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Casale1629-1"
        )["winner_raw"] = "Spain"
        with self.assertRaisesRegex(ValueError, "related Casale fingerprint changed"):
            validate_wave8_savoy_integration_dispositions(
                changed,
                self.iwbd_rows,
            )


if __name__ == "__main__":
    unittest.main()
