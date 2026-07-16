import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_peruvian_rebels import (
    WAVE8_PERUVIAN_REBELS_CONTRACT_IDS,
    WAVE8_PERUVIAN_REBELS_CONTRACTS,
    WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_ENTITIES,
    WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS,
    WAVE8_PERUVIAN_REBELS_FINAL_AUDIT_SIGNATURE,
    WAVE8_PERUVIAN_REBELS_HOLD_IDS,
    WAVE8_PERUVIAN_REBELS_HOLDS,
    WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES,
    WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_PERUVIAN_REBELS_RESERVED_IDS,
    WAVE8_PERUVIAN_REBELS_SOURCES,
    install_wave8_peruvian_rebels_entities,
    install_wave8_peruvian_rebels_sources,
    promote_wave8_peruvian_rebels_contracts,
    validate_wave8_peruvian_rebels_integration_dispositions,
    validate_wave8_peruvian_rebels_queue_contracts,
    wave8_peruvian_rebels_audit_signature,
    wave8_peruvian_rebels_cohort_counts,
    wave8_peruvian_rebels_counts,
    wave8_peruvian_rebels_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_peruvian_rebels_"


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


EXPECTED_ADJUDICATIONS = {
    "hced-Apacheta1814-1": {
        "name": "Battle of La Apacheta",
        "date": "9-10 November 1814 (source date variance)",
        "winners": {"pumacahua_angulo_cuzco_junta_army_apacheta_1814"},
        "losers": {"picoaga_moscoso_arequipa_royalist_force_apacheta_1814"},
    },
    "hced-Chacaltaya1814-1": {
        "name": "Battle of Chacaltaya (Achocalla)",
        "date": "2 November 1814",
        "winners": {"ramirez_royalist_division_chacaltaya_1814"},
        "losers": {"pinedo_munecas_cuzco_expedition_chacaltaya_1814"},
    },
    "hced-Torata1823-1": {
        "name": "Battle of Torata",
        "date": "19 January 1823",
        "winners": {"valdes_royalist_southern_division_torata_1823"},
        "losers": {"alvarado_liberating_army_south_torata_1823"},
    },
    "hced-Junin1824-1": {
        "name": "Battle of Junin",
        "date": "6 August 1824",
        "winners": {"united_liberating_army_peru_campaign_1824"},
        "losers": {"royal_army_peru_campaign_1824"},
    },
    "hced-Ayacucho1824-1": {
        "name": "Battle of Ayacucho",
        "date": "9 December 1824",
        "winners": {"united_liberating_army_peru_campaign_1824"},
        "losers": {"royal_army_peru_campaign_1824"},
    },
}


class Wave8PeruvianRebelsTests(unittest.TestCase):
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
            if row.get("candidate_id") in WAVE8_PERUVIAN_REBELS_RESERVED_IDS
        ]

    def _installed(self):
        new_entity_ids = {entity["id"] for entity in WAVE8_PERUVIAN_REBELS_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in new_entity_ids
        }
        install_wave8_peruvian_rebels_entities(entities)

        new_source_ids = {source["id"] for source in WAVE8_PERUVIAN_REBELS_SOURCES}
        sources = {
            source["id"]: source
            for source in self.release_sources
            if source["id"] not in new_source_ids
        }
        install_wave8_peruvian_rebels_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_PERUVIAN_REBELS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_peruvian_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_inventory_signature_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_PERUVIAN_REBELS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_PERUVIAN_REBELS_ENTITIES,
            "expected_candidate_ids": sorted(
                WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_PERUVIAN_REBELS_HOLDS,
            "integration_dispositions": WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_PERUVIAN_REBELS_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_PERUVIAN_REBELS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_peruvian_rebels_audit_signature(), independent)
        self.assertEqual(WAVE8_PERUVIAN_REBELS_CONTRACT_IDS, set(EXPECTED_ADJUDICATIONS))
        self.assertEqual(
            WAVE8_PERUVIAN_REBELS_HOLD_IDS,
            {"hced-Cerro de Pasco1862-1"},
        )
        self.assertEqual(
            WAVE8_PERUVIAN_REBELS_RESERVED_IDS,
            WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_peruvian_rebels_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 8,
                "new_sources": 13,
                "newly_rated_events": 5,
                "outcome_overrides": 0,
                "point_quarantine_additions": 5,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_peruvian_rebels_cohort_counts(),
            {
                "corrupt_source_chronology": 1,
                "cuzco_junta_rebellion_1814": 2,
                "final_peru_campaign_1824": 2,
                "first_intermediate_ports_campaign_1822_1823": 1,
            },
        )

    def test_all_and_only_six_exact_label_rows_are_owned(self) -> None:
        exact_label_rows = {
            row["candidate_id"]: row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Peruvian Rebels"
            or row.get("side_2_raw") == "Peruvian Rebels"
        }
        self.assertEqual(set(exact_label_rows), WAVE8_PERUVIAN_REBELS_RESERVED_IDS)
        self.assertNotIn("hced-Callao1824-1826-1", exact_label_rows)
        self.assertNotIn("hced-Callao1824-1826-1", WAVE8_PERUVIAN_REBELS_RESERVED_IDS)
        self.assertEqual(
            validate_wave8_peruvian_rebels_queue_contracts(self.hced_rows),
            {"promotion_contracts": 5, "holds": 1, "reviewed_hced_rows": 6},
        )

    def test_every_promotion_and_hold_hash_is_pinned_and_fails_closed(self) -> None:
        indexed = {row["candidate_id"]: row for row in self.lane_rows}
        self.assertEqual(set(indexed), WAVE8_PERUVIAN_REBELS_RESERVED_IDS)
        for inventory in (
            WAVE8_PERUVIAN_REBELS_CONTRACTS,
            WAVE8_PERUVIAN_REBELS_HOLDS,
        ):
            for candidate_id, disposition in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    disposition["raw_row_sha256"],
                )

        for candidate_id in sorted(WAVE8_PERUVIAN_REBELS_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.lane_rows)
                next(row for row in changed if row["candidate_id"] == candidate_id)[
                    "name"
                ] += " changed"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_peruvian_rebels_queue_contracts(changed)

    def test_sources_and_bounded_entities_parse_and_install(self) -> None:
        self.assertEqual(
            (len(WAVE8_PERUVIAN_REBELS_ENTITIES), len(WAVE8_PERUVIAN_REBELS_SOURCES)),
            (8, 13),
        )
        source_by_id = {source["id"]: source for source in WAVE8_PERUVIAN_REBELS_SOURCES}
        for source in WAVE8_PERUVIAN_REBELS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))

        forbidden_names = {"peru", "peruvian rebels", "spain", "spanish empire"}
        for entity in WAVE8_PERUVIAN_REBELS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotIn(entity["name"].casefold(), forbidden_names)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        self.assertTrue(
            {entity["id"] for entity in WAVE8_PERUVIAN_REBELS_ENTITIES} <= set(entities)
        )
        self.assertTrue(
            {source["id"] for source in WAVE8_PERUVIAN_REBELS_SOURCES} <= set(sources)
        )

    def test_exact_dates_sides_outcomes_and_event_parsing(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 5)
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_ADJUDICATIONS))
        for candidate_id, expected in EXPECTED_ADJUDICATIONS.items():
            with self.subTest(candidate_id=candidate_id):
                event = by_candidate[candidate_id]
                Event.from_dict(event)
                self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(
                    WAVE8_PERUVIAN_REBELS_CONTRACTS[candidate_id]["canonical_event"]["date_text"],
                    expected["date"],
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
                self.assertEqual(winners, expected["winners"])
                self.assertEqual(losers, expected["losers"])
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["reviewed_granularity"], "engagement")

    def test_unknown_is_never_draw_and_no_outcome_is_overridden(self) -> None:
        self.assertEqual(WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in WAVE8_PERUVIAN_REBELS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
        for event in self._events():
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {"engagement_victory", "engagement_defeat"},
            )

    def test_cerro_de_pasco_1862_is_terminally_excluded_on_date_conflict(self) -> None:
        hold = WAVE8_PERUVIAN_REBELS_HOLDS["hced-Cerro de Pasco1862-1"]
        self.assertEqual(
            hold["hold_category"],
            "source_year_conflicts_with_documented_event",
        )
        self.assertEqual(hold["source_assertion"]["year_low"], 1862)
        self.assertEqual(hold["documented_event"]["date"], "6 December 1820")
        self.assertEqual(
            hold["evidence_refs"],
            ["wave8_peruvian_rebels_culture_ministry_pasco_1820"],
        )
        self.assertNotIn("winner_side", hold)
        self.assertNotIn("result_type", hold)
        self.assertIn("without silently moving", hold["hold_reason"])
        self.assertIn("draw", hold["hold_reason"])
        self.assertNotIn(
            "hced-Cerro de Pasco1862-1",
            {event["hced_candidate_id"] for event in self._events()},
        )

    def test_source_roles_and_outcome_families_are_exact(self) -> None:
        source_by_id = {source["id"]: source for source in WAVE8_PERUVIAN_REBELS_SOURCES}
        for contract in WAVE8_PERUVIAN_REBELS_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            self.assertTrue(outcomes)
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted({source_by_id[source_id]["source_family_id"] for source_id in outcomes}),
            )
            for source_id in outcomes:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
        pasco_source = source_by_id[
            "wave8_peruvian_rebels_culture_ministry_pasco_1820"
        ]
        self.assertIn("outcome_consistency_crosscheck", pasco_source["evidence_roles"])
        self.assertNotIn("outcome", pasco_source["evidence_roles"])

    def test_location_audit_withholds_points_but_retains_modern_countries(self) -> None:
        self.assertEqual(
            WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
            WAVE8_PERUVIAN_REBELS_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            wave8_peruvian_rebels_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": WAVE8_PERUVIAN_REBELS_CONTRACT_IDS,
            },
        )
        raw_by_id = {row["candidate_id"]: row for row in self.lane_rows}
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                raw_by_id[event["hced_candidate_id"]]["modern_location_country"],
            )
            self.assertIn("location_provenance", event)

    def test_iwbd_zero_overlap_is_pinned_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_peruvian_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )

        planted = copy.deepcopy(self.iwbd_rows)
        planted.append(
            {
                "candidate_id": "iwbd-future-ayacucho",
                "name": "Battle of Ayacucho",
                "start_date": "1824-12-09",
                "end_date": "1824-12-09",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_peruvian_rebels_integration_dispositions(
                self.hced_rows,
                planted,
            )

    def test_existing_event_collision_fails_closed(self) -> None:
        entities, _, existing = self._installed()
        collision = [*existing, {"name": "Battle of Junin", "year": 1824}]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_peruvian_rebels_contracts(
                self.hced_rows,
                entities,
                collision,
            )


if __name__ == "__main__":
    unittest.main()
