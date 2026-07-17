import copy
import csv
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
from military_elo.promotion.wave8_alemanni import (
    WAVE8_ALEMANNI_CONTRACT_IDS,
    WAVE8_ALEMANNI_CONTRACTS,
    WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS,
    WAVE8_ALEMANNI_ENTITIES,
    WAVE8_ALEMANNI_EXCLUSION_IDS,
    WAVE8_ALEMANNI_EXCLUSIONS,
    WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS,
    WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE,
    WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE,
    WAVE8_ALEMANNI_HOLD_IDS,
    WAVE8_ALEMANNI_HOLDS,
    WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS,
    WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_ALEMANNI_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS,
    WAVE8_ALEMANNI_NONPROMOTIONS,
    WAVE8_ALEMANNI_OUTCOME_OVERRIDES,
    WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ALEMANNI_RESERVED_IDS,
    WAVE8_ALEMANNI_ROW_HASHES,
    WAVE8_ALEMANNI_SOURCES,
    WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
    WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS,
    install_wave8_alemanni_entities,
    install_wave8_alemanni_sources,
    promote_wave8_alemanni_contracts,
    validate_wave8_alemanni_integration_dispositions,
    validate_wave8_alemanni_queue_contracts,
    wave8_alemanni_audit_signature,
    wave8_alemanni_cohort_counts,
    wave8_alemanni_counts,
    wave8_alemanni_location_quarantine_additions,
    wave8_alemanni_spelling_counts,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_alemanni_"
SNAPSHOT = "data/raw/hced/20260713T161517Z-92a22e49c20d.csv"

BENACUS_ROMANS = "claudius_ii_roman_field_army_lake_benacus_268"
BENACUS_ALAMANNI = "alamannic_invasion_force_lake_benacus_268"
AURELIAN_ROMANS = "aurelian_roman_field_army_italy_271"
AURELIAN_INVADERS = "alamannic_iuthungian_invasion_force_italy_270_271"
SENS_ROMANS = "julian_roman_garrison_sens_356"
SENS_ALAMANNI = "alamannic_besieging_host_sens_356"
CHALONS_ROMANS = "jovinus_roman_field_army_chalons_366"
CHALONS_ALAMANNI = "alamannic_third_raiding_division_chalons_366"
SOLICINIUM_ROMANS = "valentinian_sebastianus_roman_army_solicinium_368"
SOLICINIUM_ALAMANNI = "alamannic_mountain_force_solicinium_368"
CAMPI_ROMANS = "burco_roman_detachment_campi_cannini_457"
CAMPI_ALAMANNI = "alamannic_raiding_band_campi_cannini_457"


EXPECTED_RAW_HASHES = {
    "hced-Campi Cannini457-1": (
        "ca15c209c43db023e5e53c469f1ee7eba476e7de273f6999f3266f8e13e46df2"
    ),
    "hced-Chalons366-1": (
        "ba5e083f0017e27dcb5bfb76925fb4933d8cce06637e758a4c4ad25409aa85d0"
    ),
    "hced-Fano271-1": (
        "24c9d60d88608fb0b468ab11b91274e6f18fdc9754abf30911da0c9de82cb545"
    ),
    "hced-Lake Benacus268-1": (
        "10d0872e45e2d72993c98cf9a644eed82a5f4d8c74e9a6f998df3d70c438ba7d"
    ),
    "hced-Pavia271-1": (
        "774e86f4b3f2c2a03c120b89e116446fc02e1066a308153e5428ec83d2184245"
    ),
    "hced-Placentia271-1": (
        "f2d992db81770b6f4e85243b1bfdce968d610805993373b2f8b3dc75c7baa54f"
    ),
    "hced-Rheims356-1": (
        "e07194549d39eb9b7aeb017c7b3f3dc2369abdf83d946ec11c123e4962527d51"
    ),
    "hced-Sens356-1": (
        "03d0bdad5a7f1445456ea4104e4385aecd59002f94b6116c4072b6f7f14d75e4"
    ),
    "hced-Solicinium368-1": (
        "a330cd2e8c81218bbadf60fd1f73a61140241f6ae4592e42ce8e114cd6d21da6"
    ),
    "hced-Zulpich496-1": (
        "6c143ed6bdf3a8e1ec3c12b595a764af57485558908363f86672759427da369f"
    ),
}


EXPECTED_SPELLINGS = {
    "hced-Campi Cannini457-1": "Alemmani",
    "hced-Chalons366-1": "Alemmani",
    "hced-Fano271-1": "Alemanni",
    "hced-Lake Benacus268-1": "Alemmani",
    "hced-Pavia271-1": "Alemanni",
    "hced-Placentia271-1": "Alemmani",
    "hced-Rheims356-1": "Alemmani",
    "hced-Sens356-1": "Alemanni",
    "hced-Solicinium368-1": "Alemanni",
    "hced-Zulpich496-1": "Alemanni",
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Campi Cannini457-1": ({CAMPI_ROMANS}, {CAMPI_ALAMANNI}),
    "hced-Chalons366-1": ({CHALONS_ROMANS}, {CHALONS_ALAMANNI}),
    "hced-Fano271-1": ({AURELIAN_ROMANS}, {AURELIAN_INVADERS}),
    "hced-Lake Benacus268-1": ({BENACUS_ROMANS}, {BENACUS_ALAMANNI}),
    "hced-Pavia271-1": ({AURELIAN_ROMANS}, {AURELIAN_INVADERS}),
    "hced-Placentia271-1": ({AURELIAN_INVADERS}, {AURELIAN_ROMANS}),
    "hced-Sens356-1": ({SENS_ROMANS}, {SENS_ALAMANNI}),
    "hced-Solicinium368-1": (
        {SOLICINIUM_ROMANS},
        {SOLICINIUM_ALAMANNI},
    ),
}


EXPECTED_NAMES_AND_YEARS = {
    "hced-Campi Cannini457-1": ("Battle of Campi Cannini", 457, "engagement"),
    "hced-Chalons366-1": ("Battle near Chalons-sur-Marne", 366, "engagement"),
    "hced-Fano271-1": (
        "Battle at Fanum Fortunae and the Metaurus",
        271,
        "engagement",
    ),
    "hced-Lake Benacus268-1": ("Battle near Lake Benacus", 268, "engagement"),
    "hced-Pavia271-1": (
        "Battle on the Ticinensian Fields",
        271,
        "engagement",
    ),
    "hced-Placentia271-1": ("Battle of Placentia", 271, "engagement"),
    "hced-Sens356-1": ("Siege of Sens", 356, "siege"),
    "hced-Solicinium368-1": ("Battle of Solicinium", 368, "engagement"),
}


EXPECTED_RAW_LOCATIONS = {
    "hced-Campi Cannini457-1": ("46.0431268", "8.6721267", "Italy"),
    "hced-Chalons366-1": ("48.956682", "4.363073", "France"),
    "hced-Fano271-1": ("43.8398164", "13.0194201", "Italy"),
    "hced-Lake Benacus268-1": ("45.5427247", "10.5446803", "Italy"),
    "hced-Pavia271-1": ("45.1847248", "9.1582069", "Italy"),
    "hced-Placentia271-1": ("45.0526206", "9.6929845", "Italy"),
    "hced-Rheims356-1": ("49.258329", "4.031696", "France"),
    "hced-Sens356-1": ("48.20065", "3.28268", "France"),
    "hced-Solicinium368-1": ("49.3852193", "8.5722444", "Germany"),
    "hced-Zulpich496-1": ("50.6938699", "6.6549936", "Germany"),
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


class Wave8AlemanniTests(unittest.TestCase):
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
            if str(row.get("candidate_id")) in WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS
        ]

    def _installed(self):
        new_entity_ids = {str(item["id"]) for item in WAVE8_ALEMANNI_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in new_entity_ids
        }
        install_wave8_alemanni_entities(entities)

        new_source_ids = {str(item["id"]) for item in WAVE8_ALEMANNI_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in new_source_ids
        }
        install_wave8_alemanni_sources(sources)

        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_ALEMANNI_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_alemanni_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_full_current_raw_snapshot_and_review_funnel_are_exact(self) -> None:
        snapshot_paths = {str(row["source_snapshot"]) for row in self.lane_rows}
        self.assertEqual(snapshot_paths, {SNAPSHOT})
        snapshot_path = ROOT / SNAPSHOT
        self.assertTrue(snapshot_path.is_file())

        with snapshot_path.open(encoding="cp1252", newline="") as handle:
            raw_rows = list(csv.DictReader(handle))
        self.assertEqual(len(raw_rows), 17_762)
        exact_raw_rows = []
        raw_spellings = Counter()
        for row in raw_rows:
            hits = [
                value
                for value in (row["Winner"], row["Loser"])
                if value in {"Alemanni", "Alemmani"}
            ]
            if hits:
                self.assertEqual(len(hits), 1)
                exact_raw_rows.append(row)
                raw_spellings[hits[0]] += 1
        self.assertEqual(len(exact_raw_rows), 10)
        self.assertEqual(raw_spellings, {"Alemanni": 5, "Alemmani": 5})
        self.assertEqual(
            {row["ID"] for row in exact_raw_rows},
            {str(row["source_record_id"]) for row in self.lane_rows},
        )

        exact_review_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") in {"Alemanni", "Alemmani"}
            or row.get("side_2_raw") in {"Alemanni", "Alemmani"}
        }
        self.assertEqual(len(exact_review_rows), 10)
        self.assertEqual(set(exact_review_rows), set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_ALEMANNI_ROW_HASHES, EXPECTED_RAW_HASHES)
        self.assertEqual(
            WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE,
            EXPECTED_SPELLINGS,
        )
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            row = exact_review_rows[candidate_id]
            self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
            observed = {
                value
                for value in (row["side_1_raw"], row["side_2_raw"])
                if value in {"Alemanni", "Alemmani"}
            }
            self.assertEqual(observed, {EXPECTED_SPELLINGS[candidate_id]})

        self.assertEqual(
            validate_wave8_alemanni_queue_contracts(self.hced_rows),
            {
                "exact_alemanni_rows": 5,
                "exact_alemmani_rows": 5,
                "holds": 0,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 10,
                "terminal_exclusions": 2,
            },
        )

    def test_disposition_partition_signature_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(
            WAVE8_ALEMANNI_RESERVED_IDS,
            WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            WAVE8_ALEMANNI_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(WAVE8_ALEMANNI_HOLD_IDS, set())
        self.assertEqual(
            WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
            {"hced-Rheims356-1", "hced-Zulpich496-1"},
        )
        self.assertEqual(
            WAVE8_ALEMANNI_EXCLUSION_IDS,
            WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(WAVE8_ALEMANNI_EXCLUSIONS, WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            set(WAVE8_ALEMANNI_NONPROMOTIONS),
            set(WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS),
        )

        payload = {
            "contracts": WAVE8_ALEMANNI_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_ALEMANNI_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS),
            "expected_spelling_by_candidate": (
                WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE
            ),
            "holds": WAVE8_ALEMANNI_HOLDS,
            "integration_dispositions": WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_ALEMANNI_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS
            ),
            "row_hashes": WAVE8_ALEMANNI_ROW_HASHES,
            "sources": WAVE8_ALEMANNI_SOURCES,
            "terminal_exclusions": WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE,
            "73268ff3b80dad527d43172a5774ea1a386bf4e90ca919e91ce87d98d22848ad",
        )
        self.assertEqual(wave8_alemanni_audit_signature(), independent)
        self.assertEqual(independent, WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE)

        self.assertEqual(
            wave8_alemanni_counts(),
            {
                "country_quarantine_additions": 1,
                "cross_lane_hced_dispositions": 0,
                "exact_alemanni_rows": 5,
                "exact_alemmani_rows": 5,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 10,
                "new_entities": 12,
                "new_sources": 12,
                "newly_rated_events": 8,
                "outcome_overrides": 0,
                "point_quarantine_additions": 8,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 10,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(wave8_alemanni_spelling_counts(), {"Alemanni": 5, "Alemmani": 5})
        self.assertEqual(
            wave8_alemanni_cohort_counts(),
            {
                "aurelian_italian_campaign_271": 3,
                "claudius_alamannic_campaign_268": 1,
                "clovis_alamannic_war_source_conflation": 1,
                "jovinus_alamannic_campaign_366": 1,
                "julian_gaul_campaign_356": 2,
                "majorian_northern_italy_457": 1,
                "valentinian_alamannic_campaign_368": 1,
            },
        )

    def test_sources_are_parseable_authoritative_and_family_aware(self) -> None:
        source_by_id = {str(item["id"]): item for item in WAVE8_ALEMANNI_SOURCES}
        self.assertEqual(len(source_by_id), 12)
        self.assertEqual(
            len({item["source_family_id"] for item in source_by_id.values()}),
            11,
        )
        self.assertEqual(
            source_by_id["wave8_alemanni_ammianus_book_16"]["source_family_id"],
            source_by_id["wave8_alemanni_ammianus_book_27"]["source_family_id"],
        )
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertIn(
                "identity_boundary_or_context_reference",
                source["evidence_roles"],
            )
        self.assertIn(
            "outcome",
            source_by_id["wave8_alemanni_sidonius_poem_5"]["evidence_roles"],
        )
        self.assertNotIn(
            "outcome",
            source_by_id["wave8_alemanni_gregory_tours_book_2"]["evidence_roles"],
        )

    def test_entities_are_parseable_bounded_and_never_generic(self) -> None:
        expected_windows = {
            BENACUS_ROMANS: (268, 268),
            BENACUS_ALAMANNI: (268, 268),
            AURELIAN_ROMANS: (271, 271),
            AURELIAN_INVADERS: (270, 271),
            SENS_ROMANS: (356, 356),
            SENS_ALAMANNI: (356, 356),
            CHALONS_ROMANS: (366, 366),
            CHALONS_ALAMANNI: (366, 366),
            SOLICINIUM_ROMANS: (368, 368),
            SOLICINIUM_ALAMANNI: (368, 368),
            CAMPI_ROMANS: (457, 457),
            CAMPI_ALAMANNI: (457, 457),
        }
        source_ids = {str(item["id"]) for item in WAVE8_ALEMANNI_SOURCES}
        entity_by_id = {str(item["id"]): item for item in WAVE8_ALEMANNI_ENTITIES}
        self.assertEqual(set(entity_by_id), set(expected_windows))
        for entity_id, entity in entity_by_id.items():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity_id],
            )
            self.assertLessEqual(entity["end_year"] - entity["start_year"], 1)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertIn("modern-state", entity["continuity_note"])
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
            self.assertNotIn(
                entity["name"].casefold(),
                {"alamanni", "alemanni", "alemmani", "franks", "rome", "roman empire"},
            )

    def test_only_the_three_271_engagements_share_campaign_formations(self) -> None:
        consumption = Counter()
        actors_by_candidate = {}
        for candidate_id, contract in WAVE8_ALEMANNI_CONTRACTS.items():
            self.assertEqual(len(contract["side_1_entity_ids"]), 1)
            self.assertEqual(len(contract["side_2_entity_ids"]), 1)
            actors = set(
                contract["side_1_entity_ids"] + contract["side_2_entity_ids"]
            )
            actors_by_candidate[candidate_id] = actors
            consumption.update(actors)
        self.assertEqual(consumption[AURELIAN_ROMANS], 3)
        self.assertEqual(consumption[AURELIAN_INVADERS], 3)
        self.assertEqual(
            {
                count
                for entity_id, count in consumption.items()
                if entity_id not in {AURELIAN_ROMANS, AURELIAN_INVADERS}
            },
            {1},
        )
        campaign_271 = {
            "hced-Fano271-1",
            "hced-Pavia271-1",
            "hced-Placentia271-1",
        }
        for candidate_id in campaign_271:
            self.assertEqual(
                actors_by_candidate[candidate_id],
                {AURELIAN_ROMANS, AURELIAN_INVADERS},
            )
        other_candidates = set(actors_by_candidate) - campaign_271
        for candidate_id in other_candidates:
            self.assertTrue(
                actors_by_candidate[candidate_id].isdisjoint(
                    {AURELIAN_ROMANS, AURELIAN_INVADERS}
                )
            )
        other_pairs = [actors_by_candidate[item] for item in sorted(other_candidates)]
        for index, left in enumerate(other_pairs):
            for right in other_pairs[index + 1 :]:
                self.assertTrue(left.isdisjoint(right))
        self.assertFalse(
            {"alemanni", "alemmani", "alamanni", "rome", "roman_empire"}
            & set(consumption)
        )

    def test_contract_dates_outcomes_sides_and_provenance_are_exact(self) -> None:
        source_by_id = {str(item["id"]): item for item in WAVE8_ALEMANNI_SOURCES}
        raw_by_id = {str(row["candidate_id"]): row for row in self.lane_rows}
        for candidate_id, contract in WAVE8_ALEMANNI_CONTRACTS.items():
            canonical = contract["canonical_event"]
            name, year, granularity = EXPECTED_NAMES_AND_YEARS[candidate_id]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(
                (canonical["year_low"], canonical["year_high"]),
                (year, year),
            )
            self.assertEqual(canonical["granularity"], granularity)
            expected_winners, expected_losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                raw_by_id[candidate_id]["winner_raw"],
                raw_by_id[candidate_id]["side_1_raw"],
            )
            self.assertEqual(
                raw_by_id[candidate_id]["loser_raw"],
                raw_by_id[candidate_id]["side_2_raw"],
            )
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "wave8_alemanni",
                    "status": "canonical_hced_owner",
                },
            )
            self.assertTrue(
                set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"])
            )
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
            WAVE8_ALEMANNI_CONTRACTS["hced-Placentia271-1"]["side_1_entity_ids"],
            [AURELIAN_INVADERS],
        )
        self.assertEqual(
            WAVE8_ALEMANNI_CONTRACTS["hced-Fano271-1"]["side_1_entity_ids"],
            [AURELIAN_ROMANS],
        )
        self.assertEqual(
            WAVE8_ALEMANNI_CONTRACTS["hced-Pavia271-1"]["side_1_entity_ids"],
            [AURELIAN_ROMANS],
        )
        self.assertEqual(WAVE8_ALEMANNI_OUTCOME_OVERRIDES, {})

    def test_rheims_and_zulpich_are_terminal_unknowns_not_draws(self) -> None:
        self.assertEqual(WAVE8_ALEMANNI_HOLDS, {})
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
        for candidate_id, exclusion in WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS.items():
            self.assertEqual(exclusion["disposition"], "terminal_exclusion")
            self.assertTrue(exclusion["terminal_exclusion"])
            self.assertTrue(exclusion["unknown_is_never_draw"])
            self.assertEqual(exclusion["reviewed_outcome"], "unknown")
            self.assertTrue(forbidden.isdisjoint(exclusion))
            self.assertIn("cannot produce an Elo event", exclusion["hold_reason"])
            self.assertIn("unknown is never made a draw", exclusion["hold_reason"])
            self.assertEqual(
                exclusion["duplicate_ownership"],
                {
                    "owner_module": "wave8_alemanni",
                    "status": "terminal_hced_owner",
                },
            )
            self.assertNotIn(candidate_id, WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS)
            self.assertNotIn(candidate_id, WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS)

        rheims = WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS["hced-Rheims356-1"]
        self.assertEqual(
            rheims["hold_category"],
            "named_place_is_an_assembly_point_not_an_attested_engagement",
        )
        self.assertEqual(rheims["reviewed_granularity"], "campaign_assembly_not_battle")
        self.assertIn("assembled", rheims["hold_reason"])
        self.assertIn("Brumath", rheims["hold_reason"])

        zulpich = WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS["hced-Zulpich496-1"]
        self.assertEqual(
            zulpich["hold_category"],
            "date_place_and_victor_are_combined_from_separate_source_passages",
        )
        self.assertEqual(zulpich["reviewed_granularity"], "source_conflation")
        self.assertIn("Clovis", zulpich["hold_reason"])
        self.assertIn("Sigibert", zulpich["hold_reason"])

    def test_emission_is_eight_parseable_wins_without_draw_or_ethnic_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 8)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertTrue(
            WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS.isdisjoint(by_candidate)
        )
        raw_by_id = {str(row["candidate_id"]): row for row in self.lane_rows}
        for candidate_id, (
            expected_winners,
            expected_losers,
        ) in EXPECTED_WINNERS_AND_LOSERS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["aliases"], [raw_by_id[candidate_id]["name"]])
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
                {"alemanni", "alemmani", "alamanni", "rome", "roman_empire"}
                & (winners | losers)
            )
            contract = WAVE8_ALEMANNI_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(
                event["reviewed_granularity"],
                contract["canonical_event"]["granularity"],
            )
        self.assertEqual(by_candidate["hced-Sens356-1"]["reviewed_granularity"], "siege")

    def test_location_review_is_promoted_only_and_local_to_the_lane(self) -> None:
        before_point_object = HCED_POINT_QUARANTINE_IDS
        before_country_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        raw_by_id = {str(row["candidate_id"]): row for row in self.lane_rows}
        for candidate_id, expected in EXPECTED_RAW_LOCATIONS.items():
            row = raw_by_id[candidate_id]
            self.assertEqual(
                (row["latitude"], row["longitude"], row["modern_location_country"]),
                expected,
            )

        self.assertEqual(
            WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS,
            WAVE8_ALEMANNI_CONTRACT_IDS,
        )
        self.assertEqual(
            WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Campi Cannini457-1"},
        )
        self.assertEqual(
            set(WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS),
            WAVE8_ALEMANNI_CONTRACT_IDS,
        )
        self.assertEqual(
            WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS[
                "hced-Campi Cannini457-1"
            ]["actions"],
            ["withhold_country", "withhold_point"],
        )
        for candidate_id in WAVE8_ALEMANNI_CONTRACT_IDS - {
            "hced-Campi Cannini457-1"
        }:
            self.assertEqual(
                WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS[candidate_id]["actions"],
                ["withhold_point"],
            )
        self.assertEqual(
            WAVE8_ALEMANNI_LOCATION_QUARANTINE_ADDITIONS,
            {
                "country": frozenset({"hced-Campi Cannini457-1"}),
                "point": WAVE8_ALEMANNI_CONTRACT_IDS,
            },
        )
        self.assertEqual(
            wave8_alemanni_location_quarantine_additions(),
            WAVE8_ALEMANNI_LOCATION_QUARANTINE_ADDITIONS,
        )

        _, _, events = self._emit()
        for event in events:
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            if candidate_id == "hced-Campi Cannini457-1":
                self.assertNotIn("modern_location_country", event)
                self.assertNotIn("location_provenance", event)
            else:
                self.assertEqual(
                    event["modern_location_country"],
                    EXPECTED_RAW_LOCATIONS[candidate_id][2],
                )
                self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_point_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_country_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_duplicate_audits_are_zero_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_ALEMANNI_RESERVED_IDS,
        )
        expected_zero = {
            "cross_lane_hced_dispositions": 0,
            "existing_release_duplicate_dispositions": 0,
            "integration_dispositions": 0,
            "iwbd_duplicate_dispositions": 0,
            "iwbd_probable_twins": 0,
            "iwbd_zero_overlap_candidates": 10,
        }
        self.assertEqual(
            validate_wave8_alemanni_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            expected_zero,
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-lake-garda-269",
                "name": "Lake Garda",
                "year_best": 269,
                "side_1_raw": "Future bounded force",
                "side_2_raw": "Another bounded force",
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_alemanni_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-tolbiac-506",
                "name": "Tolbiac",
                "year": 506,
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_alemanni_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {
                "id": "future-solicinium-alias-twin",
                "name": "Different canonical title",
                "aliases": ["Battle of Solicinium"],
                "year": 368,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_alemanni_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

        _, _, emitted = self._emit()
        self.assertEqual(
            validate_wave8_alemanni_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*self.release_events, *emitted],
            ),
            expected_zero,
        )

    def test_queue_tamper_missing_duplicate_and_new_spelling_rows_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.lane_rows)
        tampered[0]["winner_raw"] = "Alemanni"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_alemanni_queue_contracts(tampered)

        spelling_tamper = copy.deepcopy(self.lane_rows)
        campi = next(
            row
            for row in spelling_tamper
            if row["candidate_id"] == "hced-Campi Cannini457-1"
        )
        campi["side_2_raw"] = "Alemanni"
        campi["loser_raw"] = "Alemanni"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_alemanni_queue_contracts(spelling_tamper)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Lake Benacus268-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_alemanni_queue_contracts(missing)

        duplicated = [*self.lane_rows, copy.deepcopy(self.lane_rows[0])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_alemanni_queue_contracts(duplicated)

        for spelling in ("Alemanni", "Alemmani"):
            with self.subTest(spelling=spelling):
                future = copy.deepcopy(self.hced_rows)
                future.append(
                    {
                        "candidate_id": f"hced-Future{spelling}-600-1",
                        "name": "Future unreviewed exact-label row",
                        "year_best": 600,
                        "side_1_raw": "Future bounded force",
                        "side_2_raw": spelling,
                    }
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "exact Alemanni/Alemmani inventory",
                ):
                    validate_wave8_alemanni_queue_contracts(future)

    def test_entity_window_duplicate_event_and_installer_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        short = copy.deepcopy(entities)
        short[AURELIAN_INVADERS]["end_year"] = 270
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_alemanni_contracts(self.hced_rows, short, existing)

        missing = copy.deepcopy(entities)
        del missing[CHALONS_ROMANS]
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_alemanni_contracts(self.hced_rows, missing, existing)

        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_alemanni_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-benacus-twin",
                        "name": "Battle near Lake Benacus",
                        "year": 268,
                    },
                ],
            )

        events = promote_wave8_alemanni_contracts(self.hced_rows, entities, existing)
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_alemanni_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        entities[BENACUS_ROMANS]["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_alemanni_entities(entities)

        first_source_id = str(WAVE8_ALEMANNI_SOURCES[0]["id"])
        sources[first_source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_alemanni_sources(sources)

        fresh_entities = {}
        fresh_sources = {}
        install_wave8_alemanni_entities(fresh_entities)
        install_wave8_alemanni_sources(fresh_sources)
        fresh_entities[BENACUS_ROMANS]["name"] = "changed after install"
        fresh_sources[first_source_id]["title"] = "changed after install"
        self.assertNotEqual(
            fresh_entities[BENACUS_ROMANS]["name"],
            next(
                item["name"]
                for item in WAVE8_ALEMANNI_ENTITIES
                if item["id"] == BENACUS_ROMANS
            ),
        )
        self.assertNotEqual(
            fresh_sources[first_source_id]["title"],
            WAVE8_ALEMANNI_SOURCES[0]["title"],
        )


if __name__ == "__main__":
    unittest.main()
