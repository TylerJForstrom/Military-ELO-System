import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.hced_location import HCED_POINT_QUARANTINE_IDS
from military_elo.promotion.policy import (
    HCED_EXACT_LABEL_CORRECTION_CONTRACT_IDS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/review/hced-candidates.jsonl"
WIKIDATA_PATH = ROOT / "data/review/wikidata-battle-candidates.jsonl"
EVENTS_PATH = ROOT / "data/release/events.json"
METADATA_PATH = ROOT / "data/release/metadata.json"
REGISTRY_PATH = ROOT / "data/catalog/registry.json"

PROMOTED = {
    "hced-Dasmarinas1897-1": (
        "spanish_empire",
        "philippine_revolutionary_forces",
    ),
    "hced-Goa1570-1": (
        "kingdom_portugal",
        "clio_in_bijapur_sultanate_1492_49a19c59",
    ),
    "hced-Kliszow1702-1": (
        "kingdom_sweden",
        "electorate_saxony_1356",
        "polish_lithuanian_commonwealth",
    ),
    "hced-San Jacinto1899-1": (
        "united_states",
        "first_philippine_republic",
    ),
    "hced-Thorn1703-1": (
        "kingdom_sweden",
        "electorate_saxony_1356",
    ),
    "hced-Warsaw1705-1": (
        "kingdom_sweden",
        "electorate_saxony_1356",
        "polish_lithuanian_commonwealth",
    ),
}
HELD = {"hced-Goa1510-1", "hced-Poznan1704-1"}
REVIEWED = set(PROMOTED) | HELD
ROW_HASHES = {
    "hced-Dasmarinas1897-1": (
        "22fb33878350a00b9414a758a4ca8ba76b70509853faa980030bce4aeba26132"
    ),
    "hced-Goa1510-1": (
        "b2a3719ef3a8d43a054193184d6bc207767224e9d4d89a0245d5afd19d73dc41"
    ),
    "hced-Goa1570-1": (
        "7530be0b6a3b7f66b3923e4374bbc6013c0a870e0cd391baa4bbc48ffd47563f"
    ),
    "hced-Kliszow1702-1": (
        "083f340bdf0a0a465602e9c2d46a89a7bb244cd0ef4255ea1e17e6abbc684cc5"
    ),
    "hced-Poznan1704-1": (
        "b445fd7088f7ad775a7f0217d281e4ec39a483f3cd649bfb8b15115663cf4a01"
    ),
    "hced-San Jacinto1899-1": (
        "a961d4ca62b9b0abb7d8c1c39ad39f130f459ad7a13202cabf1fb011e664b9c4"
    ),
    "hced-Thorn1703-1": (
        "8c2df9852be657d6a85340ea3e14bd0089fd650f7186b8efca02d7d3725616f1"
    ),
    "hced-Warsaw1705-1": (
        "5f5ec7b5088c78510765fbcac178f722008eda064c44eb6cc21075f5722f1b31"
    ),
}
WIKIDATA_TWINS = {
    "hced-Dasmarinas1897-1": "Q4872016",
    "hced-Goa1570-1": "Q126888582",
    "hced-Kliszow1702-1": "Q704762",
    "hced-Poznan1704-1": "Q562324",
    "hced-San Jacinto1899-1": "Q4872274",
    "hced-Thorn1703-1": "Q815214",
    "hced-Warsaw1705-1": "Q481334",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class ExactLabelCorrectionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {row["candidate_id"]: row for row in _jsonl(QUEUE_PATH)}

    def test_review_inventory_and_all_eight_source_rows_are_pinned(self) -> None:
        self.assertEqual(HCED_EXACT_LABEL_CORRECTION_CONTRACT_IDS, set(PROMOTED))
        self.assertEqual(REVIEWED, set(ROW_HASHES))
        for candidate_id, expected_hash in ROW_HASHES.items():
            with self.subTest(candidate=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(self.rows[candidate_id]),
                    expected_hash,
                )

    def test_six_promotions_pin_complete_source_fingerprints_and_sources(self) -> None:
        for candidate_id in PROMOTED:
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

    def test_bindings_are_candidate_scoped_and_open_no_global_alias(self) -> None:
        expected = {
            "hced-Dasmarinas1897-1": {
                "filippino rebels": "philippine_revolutionary_forces"
            },
            "hced-Goa1570-1": {
                "bihar": "clio_in_bijapur_sultanate_1492_49a19c59"
            },
            "hced-Kliszow1702-1": {
                "poland": "polish_lithuanian_commonwealth",
                "saxony": "electorate_saxony_1356",
            },
            "hced-San Jacinto1899-1": {
                "filippino rebels": "first_philippine_republic"
            },
            "hced-Thorn1703-1": {
                "poland saxony": "electorate_saxony_1356"
            },
            "hced-Warsaw1705-1": {
                "poland": "polish_lithuanian_commonwealth",
                "saxony": "electorate_saxony_1356",
            },
        }
        for candidate_id, bindings in expected.items():
            self.assertEqual(
                HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[candidate_id][
                    "label_bindings"
                ],
                bindings,
            )
        for label in ("filippino rebels", "bihar", "saxony", "poland saxony"):
            self.assertNotIn(label, HCED_LABEL_POLICIES)

    def test_unpinned_composite_member_binding_fails_closed(self) -> None:
        candidate_id = "hced-Kliszow1702-1"
        contract = copy.deepcopy(
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[candidate_id]
        )
        contract["label_bindings"]["brandenburg"] = "kingdom_prussia"
        with self.assertRaisesRegex(ValueError, "unpinned label"):
            promote_hced_crosswalk_rows(
                [self.rows[candidate_id]],
                {},
                set(),
                lambda _polity: None,
                reviewed_identity_bindings={candidate_id: contract},
                require_complete_reviewed_identity_bindings=True,
            )

    def test_fingerprint_drift_fails_closed(self) -> None:
        candidate_id = "hced-San Jacinto1899-1"
        changed = copy.deepcopy(self.rows[candidate_id])
        changed["winner_raw"] = "Filippino Rebels"
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

    def test_two_contradictory_or_compressed_rows_remain_explicit_holds(self) -> None:
        self.assertTrue(HELD <= set(HCED_LABEL_CURATED_EXCLUSIONS))
        self.assertIn("compressed chronology", HCED_LABEL_CURATED_EXCLUSIONS["hced-Goa1510-1"])
        self.assertIn("tactically unresolved", HCED_LABEL_CURATED_EXCLUSIONS["hced-Poznan1704-1"])

    def test_wikidata_twins_remain_discovery_only_without_outcomes(self) -> None:
        twins = {row["candidate_id"]: row for row in _jsonl(WIKIDATA_PATH)}
        self.assertTrue(set(WIKIDATA_TWINS.values()) <= set(twins))
        for twin_id in WIKIDATA_TWINS.values():
            with self.subTest(twin=twin_id):
                self.assertEqual(twins[twin_id]["winners"], [])
                self.assertTrue(twins[twin_id]["do_not_rate_automatically"])
        wrong_goa = twins["Q121335666"]
        self.assertEqual(wrong_goa["date"][:4], "1517")
        self.assertNotIn("hced-Goa1510-1", WIKIDATA_TWINS)


@unittest.skipUnless(EVENTS_PATH.exists(), "release artifacts unavailable")
class ExactLabelCorrectionReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _json(EVENTS_PATH)
        cls.by_candidate = {
            event.get("hced_candidate_id"): event for event in cls.events
        }

    def test_exact_six_events_promote_and_two_holds_do_not(self) -> None:
        self.assertTrue(set(PROMOTED) <= set(self.by_candidate))
        self.assertTrue(HELD.isdisjoint(self.by_candidate))
        for candidate_id, expected_participants in PROMOTED.items():
            with self.subTest(candidate=candidate_id):
                event = self.by_candidate[candidate_id]
                self.assertEqual(
                    tuple(p["entity_id"] for p in event["participants"]),
                    expected_participants,
                )
                self.assertEqual(event["identity_resolution"], "label")
                self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
                self.assertTrue(
                    all(p["result_class"] != "draw" for p in event["participants"])
                )
                self.assertEqual(event["participants"][0]["termination"], "engagement_victory")
                self.assertTrue(
                    all(
                        participant["termination"] == "engagement_defeat"
                        for participant in event["participants"][1:]
                    )
                )

    def test_corrected_names_range_and_side_resolution_are_exact(self) -> None:
        expected_names = {
            "hced-Dasmarinas1897-1": "Battle of Pérez Dasmariñas",
            "hced-Goa1570-1": "Siege of Goa (1570–1571)",
            "hced-Kliszow1702-1": "Battle of Kliszów",
            "hced-San Jacinto1899-1": "Battle of San Jacinto (Pangasinan)",
            "hced-Thorn1703-1": "Siege of Thorn",
            "hced-Warsaw1705-1": "Battle of Warsaw (1705)",
        }
        for candidate_id, expected_name in expected_names.items():
            self.assertEqual(self.by_candidate[candidate_id]["name"], expected_name)
        goa = self.by_candidate["hced-Goa1570-1"]
        self.assertEqual(
            (goa["year"], goa["end_year"], goa["date_precision"]),
            (1570, 1571, "range"),
        )
        for candidate_id in ("hced-Kliszow1702-1", "hced-Warsaw1705-1"):
            self.assertEqual(
                self.by_candidate[candidate_id]["side_identity_resolution"]["side_b"],
                "label_composite",
            )
        self.assertEqual(
            self.by_candidate["hced-Thorn1703-1"]["side_identity_resolution"]["side_b"],
            "candidate_reviewed_label_binding",
        )

    def test_location_quarantine_delta_is_exact(self) -> None:
        withheld = {
            "hced-Dasmarinas1897-1",
            "hced-Goa1570-1",
            "hced-San Jacinto1899-1",
            "hced-Warsaw1705-1",
        }
        self.assertEqual(set(PROMOTED) & HCED_POINT_QUARANTINE_IDS, withheld)
        for candidate_id in withheld:
            self.assertNotIn("geometry", self.by_candidate[candidate_id])
        for candidate_id in set(PROMOTED) - withheld:
            self.assertIn("geometry", self.by_candidate[candidate_id])
        self.assertTrue(
            all(
                "modern_location_country" in self.by_candidate[candidate_id]
                for candidate_id in PROMOTED
            )
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
                "entities": 1142,
                "events": 5559,
                "sources": 1685,
                "registry_polities": 2481,
            },
        )
        promotion = metadata["promotion"]
        self.assertTrue(
            set(PROMOTED)
            <= set(promotion["hced_reviewed_crosswalk_identity_candidate_ids"])
        )
        self.assertEqual(sum(promotion["hced_label_rejections"].values()), 2892)
        coverage = registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1135)
        self.assertEqual(coverage["unresolved_event_candidates"], 36784)
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
            (5292, 880, 4850, 5194, 5243),
        )


if __name__ == "__main__":
    unittest.main()
