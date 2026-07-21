import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.policy import (
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
)
from military_elo.promotion.wave6_1500_1799 import WAVE6_HCED_EXCLUSION_IDS


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "review" / "hced-candidates.jsonl"
EVENTS_PATH = ROOT / "data" / "release" / "events.json"
ENTITIES_PATH = ROOT / "data" / "release" / "entities.json"
SEED_ENTITIES_PATH = ROOT / "data" / "seed" / "entities.json"
METADATA_PATH = ROOT / "data" / "release" / "metadata.json"
REGISTRY_PATH = ROOT / "data" / "catalog" / "registry.json"

ZHENG_ID = "zheng_chenggong_loyalist_forces_1646_1660"
TUNGNING_ID = "kingdom_tungning_1661_1683"
JIN_ID = "nurhaci_hong_taiji_jin_state_1616_1636"
MING_ID = "clio_cn_ming_dyn_1375_80721637"
QING_ID = "clio_cn_qing_dyn_1_1645_8a50480c"

EXPECTED_POLICIES = {
    "ming": (
        (1659, 1659, ZHENG_ID),
        (1661, 1683, TUNGNING_ID),
    ),
    "ming china": (
        (1619, 1619, MING_ID),
        (1661, 1662, TUNGNING_ID),
    ),
    "manchu": (
        (1619, 1619, JIN_ID),
        (1659, 1659, QING_ID),
        (1683, 1683, QING_ID),
    ),
}

EXPECTED_LABEL_INVENTORY = {
    "manchu": {
        "hced-Nanjing1659-1",
        "hced-Penghu1683-1",
        "hced-Sarhu1619-1",
        "hced-Siyanggiayan1619-1",
    },
    "ming": {
        "hced-Baxemboy1661-1",
        "hced-Kaifeng1642-1",
        "hced-Karakorum1372-1",
        "hced-Longwan1360-1",
        "hced-Nanchang1363-1",
        "hced-Nanjing1356-1",
        "hced-Nanjing1659-1",
        "hced-Ningxia1592-1",
        "hced-Ningyuan1626-1",
        "hced-Penghu1683-1",
        "hced-Poyang Lake1363-1",
        "hced-Shaoxing1359-1",
        "hced-Suzhou1366-1",
    },
    "ming china": {
        "hced-Beijing1644-1",
        "hced-Beijing1644-2",
        "hced-Buyur Nor1388-1",
        "hced-Dalinghe1631-1",
        "hced-Dong-do1426-1427-1",
        "hced-Fort Zeelandia1661-1662-1",
        "hced-Jing Luzhen1410-1",
        "hced-Kerulen1409-1",
        "hced-Shenyang1621-1",
        "hced-Siyanggiayan1619-1",
        "hced-Tot-dong1426-1",
        "hced-Tumu1449-1",
        "hced-Xiaoling1631-1",
        "hced-Yangzhou1645-1",
    },
}

EXPECTED_PARTICIPANTS = {
    "hced-Baxemboy1661-1": (TUNGNING_ID, "dutch_republic"),
    "hced-Fort Zeelandia1661-1662-1": (TUNGNING_ID, "dutch_republic"),
    "hced-Nanjing1659-1": (QING_ID, ZHENG_ID),
    "hced-Siyanggiayan1619-1": (JIN_ID, MING_ID),
}

EXPECTED_LABEL_HOLDS = {
    "hced-Penghu1683-1",
    "hced-Sarhu1619-1",
}
EXPECTED_HOLDS = EXPECTED_LABEL_HOLDS | {"hced-Kaifeng1642-1"}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class MingZhengPolicyTests(unittest.TestCase):
    def test_policy_windows_are_exact_and_plural_lane_stays_sealed(self) -> None:
        for label, windows in EXPECTED_POLICIES.items():
            with self.subTest(label=label):
                self.assertEqual(HCED_LABEL_POLICIES[label], windows)
        self.assertNotIn("manchus", HCED_LABEL_POLICIES)

    def test_new_identities_are_alias_free_and_do_not_transfer_elo(self) -> None:
        entities = {entity["id"]: entity for entity in _json(SEED_ENTITIES_PATH)}
        self.assertEqual(
            (entities[ZHENG_ID]["start_year"], entities[ZHENG_ID]["end_year"]),
            (1646, 1660),
        )
        self.assertEqual(
            (
                entities[TUNGNING_ID]["start_year"],
                entities[TUNGNING_ID]["end_year"],
            ),
            (1661, 1683),
        )
        for entity_id in (ZHENG_ID, TUNGNING_ID):
            entity = entities[entity_id]
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating", entity["continuity_note"].casefold())

    def test_reviewed_fort_zeelandia_code_binding_is_candidate_scoped(self) -> None:
        contract = HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[
            "hced-Fort Zeelandia1661-1662-1"
        ]
        self.assertEqual(
            contract["code_bindings"],
            {"cn_qing_dyn_1": TUNGNING_ID},
        )
        self.assertEqual(contract["fingerprint"]["side_1_raw"], "Ming China")
        self.assertEqual(contract["fingerprint"]["year_low"], "1661")
        self.assertEqual(contract["fingerprint"]["year_high"], "1662")
        self.assertEqual(len(contract["review"]["source_urls"]), 2)

    @unittest.skipUnless(QUEUE_PATH.exists(), "locked HCED queue unavailable")
    def test_reviewed_binding_fingerprint_fails_closed_on_drift(self) -> None:
        row = next(
            row
            for row in _jsonl(QUEUE_PATH)
            if row["candidate_id"] == "hced-Fort Zeelandia1661-1662-1"
        )
        contract = {
            row["candidate_id"]: HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[
                row["candidate_id"]
            ]
        }
        changed = copy.deepcopy(row)
        changed["seshat_side_1_candidates"] = ["cn_ming_dyn"]
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            promote_hced_crosswalk_rows(
                [changed],
                {},
                set(),
                lambda _polity: None,
                reviewed_identity_bindings=contract,
                require_complete_reviewed_identity_bindings=True,
            )

    @unittest.skipUnless(QUEUE_PATH.exists(), "locked HCED queue unavailable")
    def test_complete_raw_label_inventory_is_pinned(self) -> None:
        inventory = {label: set() for label in EXPECTED_LABEL_INVENTORY}
        for row in _jsonl(QUEUE_PATH):
            labels = {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            for label in labels & set(inventory):
                inventory[label].add(str(row["candidate_id"]))
        self.assertEqual(inventory, EXPECTED_LABEL_INVENTORY)

    def test_known_umbrella_inversion_and_flood_rows_are_explicit_holds(self) -> None:
        self.assertLessEqual(
            EXPECTED_LABEL_HOLDS, set(HCED_LABEL_CURATED_EXCLUSIONS)
        )
        for candidate_id in EXPECTED_LABEL_HOLDS:
            self.assertGreater(len(HCED_LABEL_CURATED_EXCLUSIONS[candidate_id]), 60)
        self.assertIn("hced-Kaifeng1642-1", WAVE6_HCED_EXCLUSION_IDS)


@unittest.skipUnless(
    EVENTS_PATH.exists() and ENTITIES_PATH.exists(), "release artifacts unavailable"
)
class MingZhengReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _json(EVENTS_PATH)
        cls.entities = _json(ENTITIES_PATH)
        cls.by_candidate = {
            str(event.get("hced_candidate_id")): event for event in cls.events
        }

    def test_exact_expected_candidate_set_and_participants(self) -> None:
        for candidate_id, expected in EXPECTED_PARTICIPANTS.items():
            with self.subTest(candidate=candidate_id):
                event = self.by_candidate[candidate_id]
                self.assertEqual(
                    tuple(p["entity_id"] for p in event["participants"]),
                    expected,
                )
                self.assertEqual(
                    tuple(p["termination"] for p in event["participants"]),
                    ("engagement_victory", "engagement_defeat"),
                )
                self.assertEqual(event["identity_resolution"], "label")
                self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])

    def test_fort_zeelandia_publishes_reviewed_code_provenance(self) -> None:
        event = self.by_candidate["hced-Fort Zeelandia1661-1662-1"]
        self.assertEqual(
            event["side_identity_resolution"],
            {
                "side_a": "candidate_reviewed_code_binding",
                "side_b": "seed_alias",
            },
        )
        self.assertNotIn(QING_ID, {p["entity_id"] for p in event["participants"]})

    def test_holds_never_rate_and_plural_manchus_lane_is_unchanged(self) -> None:
        self.assertTrue(EXPECTED_HOLDS.isdisjoint(self.by_candidate))
        plural_lane = {
            event["hced_candidate_id"]
            for event in self.events
            if event["id"].startswith("hced_wave8_manchus_")
        }
        self.assertEqual(
            plural_lane,
            {
                "hced-Ningyuan1626-1",
                "hced-Niumaozhai1619-1",
                "hced-Shenyang1621-1",
                "hced-Xiaoling1631-1",
                "hced-Yangzhou1645-1",
            },
        )

    @unittest.skipUnless(
        METADATA_PATH.exists() and REGISTRY_PATH.exists(),
        "release metadata unavailable",
    )
    def test_release_count_cascade_is_pinned(self) -> None:
        metadata = _json(METADATA_PATH)
        registry = _json(REGISTRY_PATH)
        self.assertEqual(
            metadata["record_counts_expected"],
            {
                "entities": 1080,
                "events": 5502,
                "sources": 1546,
                "registry_polities": 2419,
            },
        )
        coverage = registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1073)
        self.assertEqual(coverage["unresolved_event_candidates"], 36841)
        self.assertEqual(coverage["provisional_hced_label_events"], 2515)
        self.assertEqual(
            coverage["hced_location_assertions"],
            {
                **coverage["hced_location_assertions"],
                "hced_candidate_bindings": 5235,
                "geojson_points": 4834,
                "modern_location_country_assertions": 5140,
                "location_provenance_objects": 5189,
            },
        )


if __name__ == "__main__":
    unittest.main()
