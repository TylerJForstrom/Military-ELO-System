import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.hced_location import HCED_POINT_QUARANTINE_IDS
from military_elo.promotion.policy import (
    HCED_LABEL_POLICIES,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/review/hced-candidates.jsonl"
WIKIDATA_PATH = ROOT / "data/review/wikidata-battle-candidates.jsonl"
EVENTS_PATH = ROOT / "data/release/events.json"
ENTITIES_PATH = ROOT / "data/release/entities.json"
METADATA_PATH = ROOT / "data/release/metadata.json"
REGISTRY_PATH = ROOT / "data/catalog/registry.json"

ACHAEAN = "clio_q244796_bce279_0be1ca53"
NUMIDIA = "clio_dz_numidia_bce197_0f528fc7"
TARGETS = {
    "hced-Hecatombaeum-226-1": ("sparta", ACHAEAN),
    "hced-Corinth, Greece-146-1": ("roman_republic", ACHAEAN),
    "hced-Muthul-108-1": ("roman_republic", NUMIDIA),
    "hced-Thala-107-1": ("roman_republic", NUMIDIA),
}
SUTHUL = "hced-Suthul-109-1"
REVIEWED = set(TARGETS) | {SUTHUL}
ROW_HASHES = {
    "hced-Hecatombaeum-226-1": (
        "63fef490eef9db63dc4c5bd62ef1cbca275109b4465abf73ccdf41f537c9ab52"
    ),
    "hced-Corinth, Greece-146-1": (
        "a957d040edd5eb3c05d599cc1a2bf1138cd846c5d7c92330dbcfcbfdcaa533aa"
    ),
    "hced-Muthul-108-1": (
        "6963d91ef5387890308432cea3c340f710708b30ba9d2c7190d9b13e27ce58d0"
    ),
    SUTHUL: "299b7822945bc6050ba3da7706945fa0c27a556d8cf0536e812fd544133f3725",
    "hced-Thala-107-1": (
        "814baeb76440551f51a4ca385c0e43af396b6500a5b31e94488b626f64f7542b"
    ),
}
WIKIDATA_TWINS = {
    "hced-Hecatombaeum-226-1": "Q4204610",
    "hced-Corinth, Greece-146-1": "Q587983",
    "hced-Muthul-108-1": "Q2890816",
    "hced-Thala-107-1": "Q3822875",
    SUTHUL: "Q2890102",
    "hced-Bagradas-49-1": "Q619030",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class AchaeanNumidiaPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {row["candidate_id"]: row for row in _jsonl(QUEUE_PATH)}

    def test_five_reviewed_contracts_pin_complete_source_fingerprints(self) -> None:
        for candidate_id in REVIEWED:
            with self.subTest(candidate=candidate_id):
                contract = HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[candidate_id]
                row = self.rows[candidate_id]
                fingerprint = contract["fingerprint"]
                self.assertEqual(fingerprint["source_row"], str(row["source_row"]))
                for field in (
                    "source_record_id",
                    "name",
                    "side_1_raw",
                    "side_2_raw",
                    "winner_raw",
                    "loser_raw",
                ):
                    self.assertEqual(fingerprint[field], row[field])
                for field in ("year_low", "year_best", "year_high"):
                    self.assertEqual(fingerprint[field], str(row[field]))
                self.assertEqual(
                    fingerprint["seshat_side_1_candidates"],
                    tuple(row["seshat_side_1_candidates"]),
                )
                self.assertEqual(
                    fingerprint["seshat_side_2_candidates"],
                    tuple(row["seshat_side_2_candidates"]),
                )
                self.assertEqual(fingerprint["war_names"], tuple(row["war_names"]))
                self.assertEqual(contract["code_bindings"], {})
                self.assertEqual(len(contract["review"]["source_urls"]), 2)
                self.assertEqual(
                    canonical_hced_row_sha256(row), ROW_HASHES[candidate_id]
                )

    def test_bindings_are_exact_label_only_and_open_no_global_alias(self) -> None:
        expected = {
            "hced-Hecatombaeum-226-1": {"achean league": ACHAEAN},
            "hced-Corinth, Greece-146-1": {"achean league": ACHAEAN},
            "hced-Muthul-108-1": {"numidia": NUMIDIA},
            "hced-Thala-107-1": {"numidia": NUMIDIA},
        }
        for candidate_id, binding in expected.items():
            self.assertEqual(
                HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[candidate_id][
                    "label_bindings"
                ],
                binding,
            )
        self.assertNotIn("achean league", HCED_LABEL_POLICIES)
        self.assertNotIn("numidia", HCED_LABEL_POLICIES)

    def test_complete_raw_label_inventory_and_unresolved_bagradas_hold(self) -> None:
        inventory = {"achean league": set(), "numidia": set()}
        for row in self.rows.values():
            labels = {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            for label in labels & set(inventory):
                inventory[label].add(row["candidate_id"])
        self.assertEqual(
            inventory["achean league"],
            {"hced-Hecatombaeum-226-1", "hced-Corinth, Greece-146-1"},
        )
        self.assertEqual(
            inventory["numidia"],
            {
                "hced-Bagradas-49-1",
                "hced-Muthul-108-1",
                "hced-Suthul-109-1",
                "hced-Thala-107-1",
            },
        )
        self.assertNotIn(
            "hced-Bagradas-49-1", HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS
        )

    def test_numidian_chronology_disagreement_is_preserved_as_ranges(self) -> None:
        self.assertEqual(
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS["hced-Muthul-108-1"][
                "event_year_override"
            ],
            {"year_low": -109, "year_best": -108, "year_high": -108},
        )
        self.assertEqual(
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS["hced-Thala-107-1"][
                "event_year_override"
            ],
            {"year_low": -108, "year_best": -107, "year_high": -107},
        )
        self.assertEqual(
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[SUTHUL][
                "event_year_override"
            ],
            {"year_low": -110, "year_best": -109, "year_high": -109},
        )
        self.assertEqual(
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS["hced-Thala-107-1"][
                "canonical_event_override"
            ],
            {"name": "Siege of Thala"},
        )

    def test_fingerprint_drift_fails_before_promotion(self) -> None:
        candidate_id = "hced-Muthul-108-1"
        changed = copy.deepcopy(self.rows[candidate_id])
        changed["winner_raw"] = "Numidia"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            promote_hced_crosswalk_rows(
                [changed],
                {},
                set(),
                lambda _polity: None,
                reviewed_identity_bindings={
                    candidate_id: HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[
                        candidate_id
                    ]
                },
                require_complete_reviewed_identity_bindings=True,
            )

    def test_wikidata_twins_remain_discovery_only_without_outcomes(self) -> None:
        twins = {row["candidate_id"]: row for row in _jsonl(WIKIDATA_PATH)}
        self.assertTrue(set(WIKIDATA_TWINS.values()) <= set(twins))
        for twin_id in WIKIDATA_TWINS.values():
            with self.subTest(twin=twin_id):
                twin = twins[twin_id]
                self.assertEqual(twin["winners"], [])
                self.assertTrue(twin["do_not_rate_automatically"])


@unittest.skipUnless(
    EVENTS_PATH.exists() and ENTITIES_PATH.exists(), "release artifacts unavailable"
)
class AchaeanNumidiaReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _json(EVENTS_PATH)
        cls.entities = {entity["id"]: entity for entity in _json(ENTITIES_PATH)}
        cls.by_candidate = {
            event.get("hced_candidate_id"): event for event in cls.events
        }

    def test_exact_four_events_promote_with_defensible_non_draw_outcomes(self) -> None:
        for candidate_id, participants in TARGETS.items():
            with self.subTest(candidate=candidate_id):
                event = self.by_candidate[candidate_id]
                self.assertEqual(
                    tuple(p["entity_id"] for p in event["participants"]),
                    participants,
                )
                self.assertEqual(
                    tuple(p["termination"] for p in event["participants"]),
                    ("engagement_victory", "engagement_defeat"),
                )
                self.assertEqual(event["identity_resolution"], "label")
                self.assertEqual(
                    event["side_identity_resolution"]["side_b"],
                    "candidate_reviewed_label_binding",
                )
                self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
                self.assertTrue(
                    all(p["result_class"] != "draw" for p in event["participants"])
                )
        self.assertNotIn("hced-Bagradas-49-1", self.by_candidate)

    def test_suthul_owner_is_corrected_in_place_and_thala_is_a_siege(self) -> None:
        suthul_events = [
            event
            for event in self.events
            if event.get("hced_candidate_id") == SUTHUL
        ]
        self.assertEqual(len(suthul_events), 1)
        suthul = suthul_events[0]
        self.assertEqual(
            (suthul["year"], suthul["end_year"], suthul["date_precision"]),
            (-110, -109, "range"),
        )
        self.assertEqual(
            tuple(p["entity_id"] for p in suthul["participants"]),
            (NUMIDIA, "roman_republic"),
        )
        self.assertEqual(
            tuple(p["termination"] for p in suthul["participants"]),
            ("engagement_victory", "engagement_defeat"),
        )
        thala = self.by_candidate["hced-Thala-107-1"]
        self.assertEqual(
            (thala["name"], thala["event_type"]),
            ("Siege of Thala", "engagement"),
        )

    def test_existing_time_bounded_identities_are_reused_without_alias_expansion(self) -> None:
        achaean = self.entities[ACHAEAN]
        numidia = self.entities[NUMIDIA]
        self.assertEqual(
            (achaean["start_year"], achaean["end_year"]), (-279, -145)
        )
        self.assertEqual((numidia["start_year"], numidia["end_year"]), (-197, -47))
        self.assertNotIn("Achean League", achaean["aliases"])
        self.assertNotIn("Numidia", numidia["aliases"])

    def test_reviewed_ranges_and_location_quarantines_are_exact(self) -> None:
        self.assertEqual(
            (
                self.by_candidate["hced-Muthul-108-1"]["year"],
                self.by_candidate["hced-Muthul-108-1"]["end_year"],
                self.by_candidate["hced-Muthul-108-1"]["date_precision"],
            ),
            (-109, -108, "range"),
        )
        self.assertEqual(
            (
                self.by_candidate["hced-Thala-107-1"]["year"],
                self.by_candidate["hced-Thala-107-1"]["end_year"],
                self.by_candidate["hced-Thala-107-1"]["date_precision"],
            ),
            (-108, -107, "range"),
        )
        withheld = {"hced-Hecatombaeum-226-1", "hced-Muthul-108-1"}
        self.assertTrue(withheld <= HCED_POINT_QUARANTINE_IDS)
        for candidate_id in withheld:
            self.assertNotIn("geometry", self.by_candidate[candidate_id])
        for candidate_id in set(TARGETS) - withheld:
            self.assertIn("geometry", self.by_candidate[candidate_id])
        self.assertTrue(
            all("modern_location_country" in self.by_candidate[c] for c in TARGETS)
        )

    @unittest.skipUnless(
        METADATA_PATH.exists() and REGISTRY_PATH.exists(),
        "release metadata unavailable",
    )
    def test_release_count_cascade_is_exact(self) -> None:
        metadata = _json(METADATA_PATH)
        registry = _json(REGISTRY_PATH)
        self.assertEqual(
            metadata["record_counts_expected"],
            {
                "entities": 1164,
                "events": 5567,
                "sources": 1711,
                "registry_polities": 2503,
            },
        )
        promotion = metadata["promotion"]
        self.assertTrue(
            REVIEWED
            <= set(promotion["hced_reviewed_crosswalk_identity_candidate_ids"])
        )
        self.assertEqual(sum(promotion["hced_label_rejections"].values()), 2882)
        coverage = registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1157)
        self.assertEqual(coverage["unresolved_event_candidates"], 36776)
        self.assertEqual(coverage["provisional_hced_label_events"], 2525)
        location = coverage["hced_location_assertions"]
        self.assertEqual(
            (
                location["hced_candidate_bindings"],
                location["candidate_keyed_reviewed_contracts"],
                location["geojson_points"],
                location["modern_location_country_assertions"],
                location["location_provenance_objects"],
            ),
            (5300, 888, 4850, 5202, 5251),
        )


if __name__ == "__main__":
    unittest.main()
