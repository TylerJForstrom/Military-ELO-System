import json
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import (
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
)


ROOT = Path(__file__).resolve().parents[1]
SEED_ENTITIES_PATH = ROOT / "data" / "seed" / "entities.json"
EVENTS_PATH = ROOT / "data" / "release" / "events.json"
ENTITIES_PATH = ROOT / "data" / "release" / "entities.json"
METADATA_PATH = ROOT / "data" / "release" / "metadata.json"
REGISTRY_PATH = ROOT / "data" / "catalog" / "registry.json"
HCED_QUEUE_PATH = ROOT / "data" / "review" / "hced-candidates.jsonl"


EXPECTED_POLICIES = {
    "wurtemburg": ((1866, 1866, "kingdom_wurttemberg_1806_1918"),),
    "hanover": (
        (1794, 1794, "electorate_hanover_1708_1814"),
        (1866, 1866, "kingdom_hanover_1814_1866"),
    ),
    "hesse": ((1866, 1866, "grand_duchy_hesse_1806_1918"),),
    "hormuz": ((1515, 1515, "kingdom_hormuz_1500_1622"),),
    "java": ((1628, 1629, "mataram_sultanate_1588_1755"),),
    "macassar": ((1660, 1660, "sultanate_gowa_1512_1669"),),
    "palmyra": ((272, 272, "palmyrene_empire_270_273"),),
    "suri empire": ((1540, 1540, "sur_empire_1540_1555"),),
    "corinth": (
        (-435, -435, "corinthian_polis_480_338_bce"),
        (-425, -425, "corinthian_polis_480_338_bce"),
    ),
    "corcyra": ((-435, -435, "classical_corcyra_480_433_bce"),),
}

EXPECTED_ENTITIES = {
    "kingdom_wurttemberg_1806_1918": (1806, 1918),
    "electorate_hanover_1708_1814": (1708, 1814),
    "kingdom_hanover_1814_1866": (1814, 1866),
    "grand_duchy_hesse_1806_1918": (1806, 1918),
    "kingdom_hormuz_1500_1622": (1500, 1622),
    "mataram_sultanate_1588_1755": (1588, 1755),
    "sultanate_gowa_1512_1669": (1512, 1669),
    "palmyrene_empire_270_273": (270, 273),
    "sur_empire_1540_1555": (1540, 1555),
    "corinthian_polis_480_338_bce": (-480, -338),
    "classical_corcyra_480_433_bce": (-480, -433),
}

EXPECTED_EVENT_PARTICIPANTS = {
    "hced-Tauberbischofsheim1866-1": (
        "kingdom_prussia",
        "kingdom_wurttemberg_1806_1918",
    ),
    "hced-Nieuport1794-1": (
        "french_first_republic",
        "electorate_hanover_1708_1814",
    ),
    "hced-Langensalza1866-1": (
        "kingdom_hanover_1814_1866",
        "kingdom_prussia",
    ),
    "hced-Laufach1866-1": (
        "kingdom_prussia",
        "grand_duchy_hesse_1806_1918",
    ),
    "hced-Hormuz1515-1": (
        "kingdom_portugal",
        "kingdom_hormuz_1500_1622",
    ),
    "hced-Batavia1628-1": (
        "dutch_republic",
        "mataram_sultanate_1588_1755",
    ),
    "hced-Batavia1629-1": (
        "dutch_republic",
        "mataram_sultanate_1588_1755",
    ),
    "hced-Macassar1660-1": (
        "dutch_republic",
        "sultanate_gowa_1512_1669",
    ),
    "hced-Emessa272-1": (
        "roman_empire",
        "palmyrene_empire_270_273",
    ),
    "hced-Palmyra272-1": (
        "roman_empire",
        "palmyrene_empire_270_273",
    ),
    "hced-Kanauj1540-1": (
        "sur_empire_1540_1555",
        "mughal_empire",
    ),
    "hced-Leucimne-435-1": (
        "classical_corcyra_480_433_bce",
        "corinthian_polis_480_338_bce",
    ),
    "hced-Solygeia-425-1": (
        "athens",
        "corinthian_polis_480_338_bce",
    ),
}

EXPECTED_HOLDS = {
    "hced-Altenkirchen (1st)1796-1",
    "hced-Pirna1813-1",
    "hced-Ypres1793-1",
    "hced-Hormuz1507-1508-1",
    "hced-Mount Haemus981-1",
    "hced-Macassar1667-1668-1",
    "hced-Surajgarh1530-1",
}

EXPECTED_LABEL_INVENTORY = {
    "wurtemburg": {
        "hced-Altenkirchen (1st)1796-1",
        "hced-Pirna1813-1",
        "hced-Tauberbischofsheim1866-1",
    },
    "hanover": {"hced-Nieuport1794-1", "hced-Langensalza1866-1"},
    "hesse": {"hced-Laufach1866-1", "hced-Ypres1793-1"},
    "hormuz": {"hced-Hormuz1507-1508-1", "hced-Hormuz1515-1"},
    "java": {"hced-Batavia1628-1", "hced-Batavia1629-1"},
    "macassar": {"hced-Macassar1660-1", "hced-Macassar1667-1668-1"},
    "palmyra": {"hced-Emessa272-1", "hced-Palmyra272-1"},
    "suri empire": {"hced-Kanauj1540-1", "hced-Surajgarh1530-1"},
    "corinth": {
        "hced-Crimisus-340-1",
        "hced-Leucimne-435-1",
        "hced-Solygeia-425-1",
        "hced-Sybota-433-1",
    },
    "corcyra": {"hced-Leucimne-435-1"},
}


class StatePolityPolicyTests(unittest.TestCase):
    def test_policy_windows_are_exact_and_authoritative(self) -> None:
        for label, windows in EXPECTED_POLICIES.items():
            with self.subTest(label=label):
                self.assertEqual(HCED_LABEL_POLICIES[label], windows)

    def test_bulgarian_row_does_not_bypass_sealed_pre1500_lane(self) -> None:
        self.assertNotIn("bulgar kingdom", HCED_LABEL_POLICIES)

    def test_unsafe_companion_rows_are_documented_holds(self) -> None:
        self.assertLessEqual(EXPECTED_HOLDS, set(HCED_LABEL_CURATED_EXCLUSIONS))
        for candidate_id in EXPECTED_HOLDS:
            self.assertGreater(len(HCED_LABEL_CURATED_EXCLUSIONS[candidate_id]), 40)

    def test_seed_identity_windows_are_pinned_without_broad_aliases(self) -> None:
        entities = {
            entity["id"]: entity
            for entity in json.loads(SEED_ENTITIES_PATH.read_text())
        }
        for entity_id, interval in EXPECTED_ENTITIES.items():
            with self.subTest(entity=entity_id):
                entity = entities[entity_id]
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]), interval
                )
                self.assertEqual(entity["aliases"], [])
                self.assertIn("project_continuity_policy", entity["source_ids"])

    @unittest.skipUnless(HCED_QUEUE_PATH.exists(), "HCED review queue unavailable")
    def test_policy_label_inventory_is_fully_enumerated(self) -> None:
        inventory = {label: set() for label in EXPECTED_LABEL_INVENTORY}
        with HCED_QUEUE_PATH.open() as handle:
            for line in handle:
                row = json.loads(line)
                labels = {
                    normalize_label(row.get("side_1_raw")),
                    normalize_label(row.get("side_2_raw")),
                }
                for label in labels & set(inventory):
                    inventory[label].add(str(row["candidate_id"]))
        self.assertEqual(inventory, EXPECTED_LABEL_INVENTORY)


@unittest.skipUnless(
    EVENTS_PATH.exists() and ENTITIES_PATH.exists(), "release artifacts unavailable"
)
class StatePolityReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(EVENTS_PATH.read_text())
        cls.entities = json.loads(ENTITIES_PATH.read_text())
        cls.by_candidate = {
            str(event.get("hced_candidate_id")): event for event in cls.events
        }

    def test_exact_expected_candidate_set_promoted(self) -> None:
        touching_new_identity = {
            str(event.get("hced_candidate_id"))
            for event in self.events
            if set(EXPECTED_ENTITIES)
            & {
                participant["entity_id"]
                for participant in event["participants"]
            }
        }
        self.assertEqual(
            set(EXPECTED_EVENT_PARTICIPANTS),
            touching_new_identity,
        )

    def test_participants_and_tactical_results_are_pinned(self) -> None:
        for candidate_id, expected_ids in EXPECTED_EVENT_PARTICIPANTS.items():
            with self.subTest(candidate=candidate_id):
                event = self.by_candidate[candidate_id]
                participants = event["participants"]
                self.assertEqual(
                    tuple(participant["entity_id"] for participant in participants),
                    expected_ids,
                )
                self.assertEqual(
                    tuple(participant["termination"] for participant in participants),
                    ("engagement_victory", "engagement_defeat"),
                )
                self.assertEqual(event["identity_resolution"], "label")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])

    def test_holds_and_unmanifested_bulgarian_row_never_rate(self) -> None:
        self.assertTrue(EXPECTED_HOLDS.isdisjoint(self.by_candidate))
        self.assertNotIn("hced-Anchialus917-1", self.by_candidate)

    def test_all_curated_identity_targets_are_rated_once_in_release(self) -> None:
        release_by_id = {entity["id"]: entity for entity in self.entities}
        self.assertLessEqual(set(EXPECTED_ENTITIES), set(release_by_id))
        used_ids = {
            participant["entity_id"]
            for event in self.events
            for participant in event["participants"]
        }
        self.assertLessEqual(set(EXPECTED_ENTITIES), used_ids)

    @unittest.skipUnless(
        METADATA_PATH.exists() and REGISTRY_PATH.exists(),
        "release metadata unavailable",
    )
    def test_release_count_cascade_is_pinned(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text())
        registry = json.loads(REGISTRY_PATH.read_text())
        self.assertEqual(
            metadata["record_counts_expected"],
            {
                "entities": 1080,
                "events": 5512,
                "sources": 1546,
                "registry_polities": 2419,
            },
        )
        coverage = registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1073)
        self.assertEqual(coverage["unresolved_event_candidates"], 36831)
        self.assertEqual(
            coverage["hced_location_assertions"]["hced_candidate_bindings"],
            5245,
        )


if __name__ == "__main__":
    unittest.main()
