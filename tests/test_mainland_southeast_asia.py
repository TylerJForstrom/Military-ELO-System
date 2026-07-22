import hashlib
import json
import re
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import (
    HCED_LABEL_POLICIES,
    MAINLAND_SEA_REGISTRY_SOURCE_RETENTIONS,
    MAINLAND_SEA_REGISTRY_SUPERSESSIONS,
    _label_policy_seed_id,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "review" / "hced-candidates.jsonl"
IWBD_PATH = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
WIKIDATA_PATH = ROOT / "data" / "review" / "wikidata-battle-candidates.jsonl"
EVENTS_PATH = ROOT / "data" / "release" / "events.json"
ENTITIES_PATH = ROOT / "data" / "release" / "entities.json"
SEED_ENTITIES_PATH = ROOT / "data" / "seed" / "entities.json"
METADATA_PATH = ROOT / "data" / "release" / "metadata.json"
REGISTRY_PATH = ROOT / "data" / "catalog" / "registry.json"

FIRST_TOUNGOO = "first_toungoo_empire_1530_1599"
RESTORED_TOUNGOO = "restored_toungoo_kingdom_1600_1752"
KONBAUNG = "konbaung_kingdom_1752_1885"
AYUTTHAYA = "ayutthaya_kingdom_1351_1767"
RATTANAKOSIN = "rattanakosin_kingdom_1782_1932"
LONGVEK = "longvek_cambodian_kingdom_1528_1594"
FIRST_AVA = "first_ava_kingdom_1364_1555"
TAY_SON = "tay_son_regime_1778_1802"
VIENTIANE = "kingdom_vientiane_1707_1828"
QING = "clio_cn_qing_dyn_1_1645_8a50480c"
LAN_XANG = "clio_la_lan_xang_k_1363_134ccd2c"
DE_BRITO_SYRIAM = "filipe_de_brito_syrian_regime_1600_1613"

NEW_ENTITY_WINDOWS = {
    FIRST_TOUNGOO: (1530, 1599),
    RESTORED_TOUNGOO: (1600, 1752),
    KONBAUNG: (1752, 1885),
    AYUTTHAYA: (1351, 1767),
    RATTANAKOSIN: (1782, 1932),
    LONGVEK: (1528, 1594),
    FIRST_AVA: (1364, 1555),
    TAY_SON: (1778, 1802),
    VIENTIANE: (1707, 1828),
    DE_BRITO_SYRIAM: (1600, 1613),
}

EXPECTED_POLICIES = {
    "burma": (
        (1530, 1598, FIRST_TOUNGOO),
        (1600, 1751, RESTORED_TOUNGOO),
        (1753, 1885, KONBAUNG),
    ),
    "siam": (
        (1351, 1767, AYUTTHAYA),
        (1783, 1932, RATTANAKOSIN),
    ),
    "cambodia": ((1528, 1594, LONGVEK),),
    "ava": ((1364, 1555, FIRST_AVA),),
    "qing": ((1767, 1768, QING),),
    "tay son": ((1785, 1785, TAY_SON),),
    "laos": ((1827, 1827, VIENTIANE),),
}

LABEL_INVENTORY_PINS = {
    "ava": (2, "dafa02782668a3c82c9e1e8f32c944012118ec562259dcc07b473cd18e5342e9"),
    "burma": (33, "610b43edfad53e66785bef80fe48d7d08e400fcd0c13cbdab95fe1613bddaa6b"),
    "cambodia": (3, "002bdba1041d8775517683b385efecfa866a0ab64e176d1030649527a33da0e4"),
    "laos": (1, "6a754c29c71a357fd53f519c5ce31f03e15770f8ed5144d74afd261b9b60391d"),
    "qing": (4, "61adb42db5edca45e62be4f26aacae483e2b58a9cee2ceaab68aacfcb443a8c5"),
    "siam": (13, "5b7c6c06b23a16891a406f9049b5dc4c90f95edee17d6bc37ddb88288119afa4"),
    "tay son": (3, "ecbe0b76467fb79b4ef90ace795ad59487b986b518f4625a95344ef27fe64643"),
}

EXPECTED_PROMOTIONS = {
    "hced-Ava1555-1": (FIRST_TOUNGOO, FIRST_AVA),
    "hced-Ayutthaya1548-1": (AYUTTHAYA, FIRST_TOUNGOO),
    "hced-Ayutthaya1568-1569-1": (FIRST_TOUNGOO, AYUTTHAYA),
    "hced-Ayutthaya1760-1": (AYUTTHAYA, KONBAUNG),
    "hced-Ayutthaya1766-1": (KONBAUNG, AYUTTHAYA),
    "hced-Kaungton1768-1": (KONBAUNG, QING),
    "hced-Lovek1587-1": (LONGVEK, AYUTTHAYA),
    "hced-Lovek1594-1": (AYUTTHAYA, LONGVEK),
    "hced-Maymyo1767-1": (KONBAUNG, QING),
    "hced-Nong Bua Lamphu1827-1": (RATTANAKOSIN, VIENTIANE),
    "hced-Nong Sarai1593-1": (AYUTTHAYA, FIRST_TOUNGOO),
    "hced-Rach Gam-Xoai Mut1785-1": (TAY_SON, RATTANAKOSIN),
    "hced-Syriam1613-1": (RESTORED_TOUNGOO, DE_BRITO_SYRIAM),
    "hced-Three Pagoda Pass1786-1": (RATTANAKOSIN, KONBAUNG),
    "hced-Vientiane1574-1": (FIRST_TOUNGOO, LAN_XANG),
}

KONBAUNG_MIGRATIONS = {
    "hced-Bassein, Burma1825-1",
    "hced-Bassein, Burma1852-1",
    "hced-Bhamo1885-1",
    "hced-Danubyu1825-1",
    "hced-Danubyu1853-1",
    "hced-Kamarut1879-1",
    "hced-Kemmendine1824-1",
    "hced-Kokein1824-1",
    "hced-Martaban1824-1",
    "hced-Martaban1852-1",
    "hced-Melloone1826-1",
    "hced-Minhla1885-1",
    "hced-Pagahm-mew1826-1",
    "hced-Pegu1852-1",
    "hced-Prome1825-1",
    "hced-Prome1852-1",
    "hced-Rangoon1824-1",
    "hced-Rangoon1852-1",
    "hced-Sittang1826-1",
    "hced-Wattee-Goung1825-1",
}

EXPLICIT_HOLDS = {
    "hced-Bangkok1688-1",
    "hced-Pegu1599-1",
    "hced-Phnom Penh1599-1",
    "hced-Hanoi1789-1",
    "hced-Nanjing1862-1864-1",
    "hced-Quy Nhon1773-1",
    "hced-Thang Long1802-1",
}

CROSS_SOURCE_DISPOSITIONS = {
    "hced-Nong Sarai1593-1": "Q111758784",
    "hced-Rach Gam-Xoai Mut1785-1": "Q1047091",
    "hced-Maymyo1767-1": "Q65065263",
    "hced-Bangkok1688-1": "Q7509852",
    "hced-Ayutthaya1766-1": "Q13012906",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _id_digest(candidate_ids) -> str:
    payload = json.dumps(sorted(candidate_ids), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class MainlandSoutheastAsiaPolicyTests(unittest.TestCase):
    def test_policy_windows_are_exact_and_authoritative(self) -> None:
        for label, expected in EXPECTED_POLICIES.items():
            with self.subTest(label=label):
                self.assertEqual(HCED_LABEL_POLICIES[label], expected)

    def test_transition_and_narrow_policy_years_stay_closed(self) -> None:
        closed = {
            "burma": (1277, 1599, 1752, 1886),
            "siam": (1768, 1782, 1933),
            "cambodia": (1595, 1599),
            "ava": (1556,),
            "qing": (1766, 1769, 1789, 1862),
            "tay son": (1773, 1784, 1786, 1802),
            "laos": (1826, 1828),
        }
        for label, years in closed.items():
            for year in years:
                with self.subTest(label=label, year=year):
                    self.assertIsNone(_label_policy_seed_id(label, year, year))
        self.assertIsNone(_label_policy_seed_id("burma", 1598, 1600))
        self.assertIsNone(_label_policy_seed_id("siam", 1767, 1783))

    def test_new_identities_are_alias_free_and_nonheritable(self) -> None:
        entities = {entity["id"]: entity for entity in _json(SEED_ENTITIES_PATH)}
        for entity_id, window in NEW_ENTITY_WINDOWS.items():
            with self.subTest(entity=entity_id):
                entity = entities[entity_id]
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]), window
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertEqual(entity["source_ids"], ["project_continuity_policy"])

    @unittest.skipUnless(QUEUE_PATH.exists(), "locked HCED queue unavailable")
    def test_complete_exact_label_inventories_are_pinned(self) -> None:
        inventory = {label: set() for label in LABEL_INVENTORY_PINS}
        for row in _jsonl(QUEUE_PATH):
            labels = {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            for label in labels & set(inventory):
                inventory[label].add(str(row["candidate_id"]))
        for label, (count, digest) in LABEL_INVENTORY_PINS.items():
            with self.subTest(label=label):
                self.assertEqual(len(inventory[label]), count)
                self.assertEqual(_id_digest(inventory[label]), digest)

    @unittest.skipUnless(
        QUEUE_PATH.exists() and IWBD_PATH.exists() and WIKIDATA_PATH.exists(),
        "locked review queues unavailable",
    )
    def test_cross_source_twins_are_detected_and_have_no_wikidata_outcome(self) -> None:
        targets = {
            row["candidate_id"]: row
            for row in _jsonl(QUEUE_PATH)
            if row["candidate_id"] in CROSS_SOURCE_DISPOSITIONS
        }
        self.assertEqual(set(targets), set(CROSS_SOURCE_DISPOSITIONS))
        observed = set()
        for path in (IWBD_PATH, WIKIDATA_PATH):
            for other in _jsonl(path):
                other_name = normalize_label(
                    other.get("name")
                    or other.get("label")
                    or other.get("battle_name")
                )
                other_year = None
                for key in (
                    "year",
                    "year_best",
                    "start_year",
                    "point_in_time_year",
                    "date",
                    "start_date",
                ):
                    value = other.get(key)
                    if value in (None, ""):
                        continue
                    match = re.match(r"^-?\d+", str(value))
                    if match is None:
                        continue
                    other_year = int(match.group())
                    break
                if other_year is None:
                    continue
                for candidate_id, row in targets.items():
                    name = normalize_label(row.get("name"))
                    year = int(row["year_best"])
                    if abs(other_year - year) <= 1 and (
                        name == other_name
                        or (name and other_name and (name in other_name or other_name in name))
                    ):
                        observed.add((candidate_id, str(other.get("candidate_id"))))
                        if path == WIKIDATA_PATH:
                            self.assertEqual(other.get("winners"), [])
                            self.assertTrue(other.get("do_not_rate_automatically"))
        self.assertEqual(observed, set(CROSS_SOURCE_DISPOSITIONS.items()))


@unittest.skipUnless(
    EVENTS_PATH.exists() and ENTITIES_PATH.exists(), "release artifacts unavailable"
)
class MainlandSoutheastAsiaReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _json(EVENTS_PATH)
        cls.entities = _json(ENTITIES_PATH)
        cls.by_candidate = {
            str(event.get("hced_candidate_id")): event for event in cls.events
        }

    def test_exact_fifteen_events_promote_with_pinned_participants(self) -> None:
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            with self.subTest(candidate=candidate_id):
                event = self.by_candidate[candidate_id]
                self.assertEqual(
                    tuple(p["entity_id"] for p in event["participants"]), expected
                )
                self.assertEqual(
                    tuple(p["termination"] for p in event["participants"]),
                    ("engagement_victory", "engagement_defeat"),
                )
                self.assertEqual(event["identity_resolution"], "label")
                self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
                self.assertNotEqual(event["participants"][0]["result_class"], "draw")

    def test_reviewed_syrian_actor_and_ayutthaya_date_corrections_are_exact(self) -> None:
        syriam = self.by_candidate["hced-Syriam1613-1"]
        self.assertEqual(
            syriam["side_identity_resolution"]["side_b"],
            "candidate_reviewed_label_binding",
        )
        self.assertNotIn(
            "kingdom_portugal",
            {participant["entity_id"] for participant in syriam["participants"]},
        )
        ayutthaya = self.by_candidate["hced-Ayutthaya1568-1569-1"]
        self.assertEqual(
            (ayutthaya["year"], ayutthaya["end_year"], ayutthaya["date_precision"]),
            (1568, 1569, "range"),
        )

    def test_twenty_burma_events_migrate_to_konbaung_only(self) -> None:
        observed = {
            candidate_id
            for candidate_id in KONBAUNG_MIGRATIONS
            if any(
                p["entity_id"] == KONBAUNG
                for p in self.by_candidate[candidate_id]["participants"]
            )
        }
        self.assertEqual(observed, KONBAUNG_MIGRATIONS)
        for candidate_id in KONBAUNG_MIGRATIONS:
            event = self.by_candidate[candidate_id]
            self.assertIn("label_policy", event["side_identity_resolution"].values())
            self.assertNotIn(
                "clio_q836_1820_f17c2530",
                {p["entity_id"] for p in event["participants"]},
            )

    def test_transition_and_actor_ambiguity_rows_remain_staged(self) -> None:
        self.assertTrue(EXPLICIT_HOLDS.isdisjoint(self.by_candidate))

    def test_broad_burma_source_envelope_is_no_longer_rated(self) -> None:
        release_ids = {entity["id"] for entity in self.entities}
        rated_ids = {
            p["entity_id"] for event in self.events for p in event["participants"]
        }
        self.assertNotIn("clio_q836_1820_f17c2530", release_ids)
        self.assertNotIn("clio_q836_1820_f17c2530", rated_ids)
        self.assertIn(KONBAUNG, release_ids)
        self.assertIn(KONBAUNG, rated_ids)

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
                "entities": 1200,
                "events": 5585,
                "sources": 1737,
                "registry_polities": 2539,
            },
        )
        coverage = registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1193)
        self.assertEqual(coverage["unresolved_event_candidates"], 36758)
        self.assertEqual(coverage["provisional_hced_label_events"], 2525)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5318)
        self.assertEqual(location["geojson_points"], 4850)
        self.assertEqual(location["modern_location_country_assertions"], 5218)
        self.assertEqual(location["location_provenance_objects"], 5267)

    @unittest.skipUnless(REGISTRY_PATH.exists(), "registry unavailable")
    def test_source_candidate_supersessions_are_narrow_and_auditable(self) -> None:
        registry = {entity["id"]: entity for entity in _json(REGISTRY_PATH)["entities"]}
        self.assertEqual(
            registry["clio_q836_1820_f17c2530"]["identity_status"],
            "source_candidate",
        )
        self.assertEqual(registry["clio_q836_1820_f17c2530"]["status"], "unrated")
        for source_id, reason in MAINLAND_SEA_REGISTRY_SOURCE_RETENTIONS.items():
            with self.subTest(source=source_id):
                self.assertEqual(registry[source_id]["status"], "unrated")
                self.assertEqual(
                    registry[source_id]["identity_status"], "source_candidate"
                )
                self.assertEqual(registry[source_id]["retention_note"], reason)
        for source_id, target_id in MAINLAND_SEA_REGISTRY_SUPERSESSIONS.items():
            with self.subTest(source=source_id):
                self.assertEqual(registry[source_id]["status"], "unrated")
                self.assertEqual(registry[source_id]["identity_status"], "superseded")
                self.assertEqual(registry[source_id]["superseded_by"], target_id)
        self.assertIn("clio_q1062422_1741_5f5cea8a", registry)
        self.assertEqual(registry["clio_q1062422_1741_5f5cea8a"]["status"], "unrated")


if __name__ == "__main__":
    unittest.main()
