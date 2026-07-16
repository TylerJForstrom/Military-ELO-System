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
from military_elo.promotion.wave8_insubrian_gauls import (
    WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
    WAVE8_INSUBRIAN_GAULS_CONTRACTS,
    WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_ENTITIES,
    WAVE8_INSUBRIAN_GAULS_EXCLUSION_IDS,
    WAVE8_INSUBRIAN_GAULS_EXCLUSIONS,
    WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS,
    WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE,
    WAVE8_INSUBRIAN_GAULS_HOLD_IDS,
    WAVE8_INSUBRIAN_GAULS_HOLDS,
    WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS,
    WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS,
    WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES,
    WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_INSUBRIAN_GAULS_RESERVED_IDS,
    WAVE8_INSUBRIAN_GAULS_SOURCES,
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
    install_wave8_insubrian_gauls_entities,
    install_wave8_insubrian_gauls_sources,
    promote_wave8_insubrian_gauls_contracts,
    validate_wave8_insubrian_gauls_integration_dispositions,
    validate_wave8_insubrian_gauls_queue_contracts,
    wave8_insubrian_gauls_audit_signature,
    wave8_insubrian_gauls_cohort_counts,
    wave8_insubrian_gauls_counts,
    wave8_insubrian_gauls_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_insubrian_gauls_"

TELAMON_ROMANS = "aemilius_atilius_roman_consular_armies_telamon_225_bce"
TELAMON_GAULS = "boii_insubres_taurisci_gaesatae_coalition_telamon_225_bce"
CLASTIDIUM_ROMANS = "marcellus_roman_relief_detachment_clastidium_222_bce"
CLASTIDIUM_GAULS = "insubrian_gaesatae_diversionary_force_clastidium_222_bce"
MINCIO_ROMANS = "cethegus_roman_consular_army_mincio_197_bce"
MINCIO_INSUBRES = "insubrian_field_force_hamilcar_mincio_197_bce"
COMUM_ROMANS = "marcellus_roman_consular_army_comum_196_bce"
COMUM_INSUBRES = "insubrian_comenses_field_force_comum_196_bce"


EXPECTED_RAW_HASHES = {
    "hced-Adda-223-1": "8c2c8fcc758cfe398f9c49f3cfeccc5e0e1f03cede11faf62e425c4620c80972",
    "hced-Clastidium-222-1": "ccedeefad71ee1c90cf7486f249972f79987ad6c6d18ff14f16ec793fcff3e1f",
    "hced-Lake Como-196-1": "f1b7118b97cdd46fcb6f820f7cb76751e01403914595802fe05182c75d2413b6",
    "hced-Mincio-197-1": "019b2dafc6e30e6afccc70a2f9a1ac37e2c5fb41045b876925390c005eb082bf",
    "hced-Telamon-225-1": "960aa1b7054167f6ffdf6e45b2b23cb65c08e7c63721096c9d3a56ae9e640989",
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Telamon-225-1": ({TELAMON_ROMANS}, {TELAMON_GAULS}),
    "hced-Clastidium-222-1": ({CLASTIDIUM_ROMANS}, {CLASTIDIUM_GAULS}),
    "hced-Mincio-197-1": ({MINCIO_ROMANS}, {MINCIO_INSUBRES}),
    "hced-Lake Como-196-1": ({COMUM_ROMANS}, {COMUM_INSUBRES}),
}

EXPECTED_YEARS = {
    "hced-Telamon-225-1": -225,
    "hced-Clastidium-222-1": -222,
    "hced-Mincio-197-1": -197,
    "hced-Lake Como-196-1": -196,
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8InsubrianGaulsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if str(row.get("candidate_id"))
            in WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS
        ]

    def _installed(self):
        new_entity_ids = {
            str(entity["id"]) for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_insubrian_gauls_entities(entities)

        new_source_ids = {
            str(source["id"]) for source in WAVE8_INSUBRIAN_GAULS_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_insubrian_gauls_sources(sources)

        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_INSUBRIAN_GAULS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_insubrian_gauls_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_exact_five_row_inventory_hashes_and_dispositions(self) -> None:
        exact_label_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Insubrian Gauls"
            or row.get("side_2_raw") == "Insubrian Gauls"
        }
        self.assertEqual(set(exact_label_rows), set(EXPECTED_RAW_HASHES))
        self.assertEqual(len(self.lane_rows), 5)
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_RESERVED_IDS,
            WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_HOLD_IDS, set())
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
            {"hced-Adda-223-1"},
        )
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_EXCLUSION_IDS,
            WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(
            WAVE8_INSUBRIAN_GAULS_EXCLUSIONS,
            WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            set(WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS),
            {"hced-Adda-223-1"},
        )

        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(exact_label_rows[candidate_id]),
                expected_hash,
            )
        self.assertEqual(
            validate_wave8_insubrian_gauls_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 4,
                "holds": 0,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 1,
            },
        )

    def test_signature_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_INSUBRIAN_GAULS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_INSUBRIAN_GAULS_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_INSUBRIAN_GAULS_HOLDS,
            "integration_dispositions": WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": (
                WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_INSUBRIAN_GAULS_SOURCES,
            "terminal_exclusions": WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE,
            "920e300ef51dbd0ce6badbc07109d27bcd764f79c5ec4bae4d858a9b824428dd",
        )
        self.assertEqual(wave8_insubrian_gauls_audit_signature(), independent)
        self.assertEqual(independent, WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_insubrian_gauls_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "new_entities": 8,
                "new_sources": 12,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_insubrian_gauls_cohort_counts(),
            {
                "cisalpine_reconquest_197_196_bce": 2,
                "gallic_war_telamon_225_bce": 1,
                "roman_insubrian_war_223_222_bce": 1,
            },
        )

    def test_sources_and_entities_are_parseable_bounded_and_non_generic(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_INSUBRIAN_GAULS_SOURCES
        }
        self.assertEqual(len(source_by_id), 12)
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

        expected_windows = {
            TELAMON_ROMANS: (-225, -225),
            TELAMON_GAULS: (-225, -225),
            CLASTIDIUM_ROMANS: (-222, -222),
            CLASTIDIUM_GAULS: (-222, -222),
            MINCIO_ROMANS: (-197, -197),
            MINCIO_INSUBRES: (-197, -197),
            COMUM_ROMANS: (-196, -196),
            COMUM_INSUBRES: (-196, -196),
        }
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES
        }
        self.assertEqual(set(entity_by_id), set(expected_windows))
        for entity_id, entity in entity_by_id.items():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity_id],
            )
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertIn("modern state", entity["continuity_note"])
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))
            self.assertNotIn(
                entity["name"].casefold(),
                {"gauls", "insubres", "insubrian gauls", "rome"},
            )

    def test_every_battle_uses_distinct_commands_and_formation_boundaries(self) -> None:
        consumed = []
        for contract in WAVE8_INSUBRIAN_GAULS_CONTRACTS.values():
            self.assertEqual(len(contract["side_1_entity_ids"]), 1)
            self.assertEqual(len(contract["side_2_entity_ids"]), 1)
            consumed.extend(contract["side_1_entity_ids"])
            consumed.extend(contract["side_2_entity_ids"])
        self.assertEqual(len(consumed), 8)
        self.assertEqual(len(set(consumed)), 8)
        self.assertNotIn("roman_republic", consumed)
        self.assertNotIn("insubrian_gauls", consumed)
        self.assertNotIn("insubres", consumed)
        self.assertNotIn("gauls", consumed)

        telamon = WAVE8_INSUBRIAN_GAULS_CONTRACTS["hced-Telamon-225-1"]
        self.assertEqual(
            telamon["historical_review"]["coalition_components"],
            ["Boii", "Gaesatae", "Insubres", "Taurisci"],
        )
        self.assertEqual(telamon["side_2_entity_ids"], [TELAMON_GAULS])

    def test_contract_dates_outcomes_and_provenance_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_INSUBRIAN_GAULS_SOURCES
        }
        for candidate_id, contract in WAVE8_INSUBRIAN_GAULS_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["year_low"], EXPECTED_YEARS[candidate_id])
            self.assertEqual(canonical["year_high"], EXPECTED_YEARS[candidate_id])
            self.assertEqual(canonical["granularity"], "engagement")
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "wave8_insubrian_gauls",
                    "status": "canonical_hced_owner",
                },
            )
            self.assertTrue(set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"]))
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertGreaterEqual(len(expected_families), 2)
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_CONTRACTS["hced-Lake Como-196-1"]["canonical_event"]["name"],
            "Battle in the Comum territory",
        )
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES, {})

    def test_adda_is_terminally_excluded_without_inventing_a_result(self) -> None:
        exclusion = WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS["hced-Adda-223-1"]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertTrue(exclusion["terminal_exclusion"])
        self.assertTrue(exclusion["unknown_is_never_draw"])
        self.assertEqual(exclusion["reviewed_outcome"], "unknown")
        self.assertEqual(
            exclusion["hold_category"],
            "named_site_and_outcome_belong_to_separate_campaign_episodes",
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
        self.assertTrue(forbidden.isdisjoint(exclusion))
        reason = exclusion["hold_reason"].casefold()
        self.assertIn("crossing", reason)
        self.assertIn("later decisive roman victory", reason)
        self.assertIn("cannot produce an elo result", reason)
        self.assertIn("never made a draw", reason)
        self.assertNotIn(
            "hced-Adda-223-1",
            WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS,
        )

    def test_mincio_does_not_invent_cenomanian_allegiance(self) -> None:
        contract = WAVE8_INSUBRIAN_GAULS_CONTRACTS["hced-Mincio-197-1"]
        self.assertEqual(contract["side_1_entity_ids"], [MINCIO_ROMANS])
        self.assertEqual(contract["side_2_entity_ids"], [MINCIO_INSUBRES])
        self.assertEqual(
            contract["historical_review"]["cenomani_disposition"],
            "not rated; neutrality or rear attack reported",
        )
        rated = " ".join(
            contract["side_1_entity_ids"] + contract["side_2_entity_ids"]
        ).casefold()
        self.assertNotIn("cenomani", rated)
        self.assertNotIn("carthage", rated)

    def test_emission_is_four_parseable_wins_without_ethnic_bridge_or_draw(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertNotIn("hced-Adda-223-1", by_candidate)
        for candidate_id, (expected_winners, expected_losers) in EXPECTED_WINNERS_AND_LOSERS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
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
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            terminations = {item["termination"] for item in event["participants"]}
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            self.assertFalse(
                {"gauls", "insubres", "insubrian_gauls", "roman_republic"}
                & (winners | losers)
            )
            contract = WAVE8_INSUBRIAN_GAULS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
        self.assertEqual(by_candidate["hced-Lake Como-196-1"]["aliases"], ["Lake Como"])

    def test_location_quarantine_is_promoted_only_and_does_not_mutate_globals(self) -> None:
        before_point_object = HCED_POINT_QUARANTINE_IDS
        before_country_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        raw_by_id = {str(row["candidate_id"]): row for row in self.lane_rows}
        expected_raw_locations = {
            "hced-Adda-223-1": ("45.8012456", "9.3249373", "Italy"),
            "hced-Clastidium-222-1": ("45.0158408", "9.1272882", "Italy"),
            "hced-Lake Como-196-1": ("46.0401307", "9.2133093", "Italy"),
            "hced-Mincio-197-1": ("45.30144", "10.7092286", "Italy"),
            "hced-Telamon-225-1": ("42.5555309", "11.131689", "Italy"),
        }
        for candidate_id, expected in expected_raw_locations.items():
            row = raw_by_id[candidate_id]
            self.assertEqual(
                (row["latitude"], row["longitude"], row["modern_location_country"]),
                expected,
            )
        _, _, events = self._emit()

        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS,
            WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            set(WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS),
            WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
        )
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_insubrian_gauls_location_quarantine_additions(),
            {
                "point": WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Italy")
            self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_point_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_country_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_duplicate_audits_are_zero_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_INSUBRIAN_GAULS_RESERVED_IDS,
        )
        self.assertEqual(
            validate_wave8_insubrian_gauls_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 5,
            },
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-telamon-225",
                "name": "Battle of Telamon",
                "year_best": -225,
                "side_1_raw": "Future exact force",
                "side_2_raw": "Future exact force two",
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_insubrian_gauls_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-clastidium",
                "name": "Battle of Clastidium",
                "year": -222,
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_insubrian_gauls_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {"id": "future-mincio-twin", "name": "Battle of the Mincio", "year": -197},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_insubrian_gauls_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_queue_tamper_missing_duplicate_and_future_label_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.lane_rows)
        tampered[0]["winner_raw"] = "Insubrian Gauls"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_insubrian_gauls_queue_contracts(tampered)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Telamon-225-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_insubrian_gauls_queue_contracts(missing)

        duplicated = [*self.lane_rows, copy.deepcopy(self.lane_rows[0])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_insubrian_gauls_queue_contracts(duplicated)

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-FutureInsubrianGauls-190-1",
                "name": "Future unreviewed row",
                "year_best": -190,
                "side_1_raw": "Rome",
                "side_2_raw": "Insubrian Gauls",
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Insubrian Gauls inventory"):
            validate_wave8_insubrian_gauls_queue_contracts(future)

    def test_entity_window_duplicate_promotion_and_installer_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        short = copy.deepcopy(entities)
        short[TELAMON_ROMANS]["end_year"] = -226
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_insubrian_gauls_contracts(
                self.hced_rows,
                short,
                existing,
            )

        events = promote_wave8_insubrian_gauls_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_insubrian_gauls_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        entities[TELAMON_ROMANS]["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_insubrian_gauls_entities(entities)

        first_source_id = str(WAVE8_INSUBRIAN_GAULS_SOURCES[0]["id"])
        sources[first_source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_insubrian_gauls_sources(sources)

        fresh_entities = {}
        fresh_sources = {}
        install_wave8_insubrian_gauls_entities(fresh_entities)
        install_wave8_insubrian_gauls_sources(fresh_sources)
        fresh_entities[TELAMON_ROMANS]["name"] = "changed after install"
        fresh_sources[first_source_id]["title"] = "changed after install"
        self.assertNotEqual(
            fresh_entities[TELAMON_ROMANS]["name"],
            next(
                entity["name"]
                for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES
                if entity["id"] == TELAMON_ROMANS
            ),
        )
        self.assertNotEqual(
            fresh_sources[first_source_id]["title"],
            WAVE8_INSUBRIAN_GAULS_SOURCES[0]["title"],
        )


if __name__ == "__main__":
    unittest.main()
