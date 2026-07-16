import json
import unittest
from pathlib import Path

from military_elo.promotion.policy import (
    IDENTITY_DENY_WINDOWS,
    _cow_policy_seed_id,
    _gw_policy_seed_id,
    _label_policy_seed_id,
    _policy_seed_id,
)
from military_elo.promotion.wave6_1800_2021_policy import (
    WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS,
    WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
)


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed"


class CrispStateIdentityTrancheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entities = {
            entity["id"]: entity
            for entity in json.loads(
                (SEED / "entities.json").read_text(encoding="utf-8")
            )
        }
        cls.sources = {
            source["id"]: source
            for source in json.loads(
                (SEED / "sources.json").read_text(encoding="utf-8")
            )
        }

    def test_tranche_reuses_existing_rating_ids_and_has_direct_sources(self) -> None:
        expected = {
            "mahdist_ansar_forces": (1881, 1899, "britannica_al_mahdi"),
            "principality_bulgaria": (1878, 1908, "britannica_bulgaria_history"),
            "kingdom_bulgaria": (1908, 1946, "britannica_bulgaria_history"),
            "argentine_republic_1861": (1861, 1930, "britannica_argentina_history"),
            "clio_q414_1930_5e281b3e": (
                1930,
                None,
                "britannica_argentina_history",
            ),
            "clio_q170588_1836_8e422d86": (
                1836,
                1846,
                "britannica_texas_revolution",
            ),
            "clio_mx_mexico_1_1868_ffbcfbae": (
                1868,
                2024,
                "britannica_mexico_history",
            ),
            "clio_sy_syria_modern_1946_86597c89": (
                1946,
                1957,
                "britannica_syria_history",
            ),
            "clio_q41137_1973_b05dea50": (
                1962,
                None,
                "britannica_syria_history",
            ),
        }
        for entity_id, (low, high, source_id) in expected.items():
            with self.subTest(entity=entity_id):
                entity = self.entities[entity_id]
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]), (low, high)
                )
                self.assertIn(source_id, entity["source_ids"])
                self.assertIn(source_id, self.sources)
                self.assertEqual(
                    self.sources[source_id]["publisher"], "Encyclopaedia Britannica"
                )

    def test_mahdist_label_spellings_share_one_bounded_identity(self) -> None:
        labels = (
            "mahdists",
            "mahdiyya",
            "the mahdiyya",
            "sudanese mahdists",
            "sudanese islamists",
        )
        for label in labels:
            with self.subTest(label=label, year=1880):
                self.assertIsNone(_label_policy_seed_id(label, 1880, 1880))
            with self.subTest(label=label, year=1881):
                self.assertEqual(
                    _label_policy_seed_id(label, 1881, 1881),
                    "mahdist_ansar_forces",
                )
            with self.subTest(label=label, year=1899):
                self.assertEqual(
                    _label_policy_seed_id(label, 1899, 1899),
                    "mahdist_ansar_forces",
                )
            with self.subTest(label=label, year=1900):
                self.assertIsNone(_label_policy_seed_id(label, 1900, 1900))

    def test_argentina_transition_years_fail_closed(self) -> None:
        expected = {
            1860: "argentine_confederation",
            1861: None,
            1862: "argentine_republic_1861",
            1929: "argentine_republic_1861",
            1930: None,
            1931: "clio_q414_1930_5e281b3e",
        }
        for year, entity_id in expected.items():
            with self.subTest(year=year):
                self.assertEqual(
                    _label_policy_seed_id("argentina", year, year), entity_id
                )

    def test_argentina_seshat_code_uses_the_same_boundaries(self) -> None:
        expected = {
            1830: None,
            1831: "argentine_confederation",
            1861: None,
            1862: "argentine_republic_1861",
            1930: None,
            1931: "clio_q414_1930_5e281b3e",
        }
        for year, entity_id in expected.items():
            with self.subTest(year=year):
                self.assertEqual(
                    _policy_seed_id("ar_argentina_rep_1", year, year), entity_id
                )

    def test_bulgaria_1908_transition_fails_closed(self) -> None:
        expected = {
            1877: None,
            1878: "principality_bulgaria",
            1907: "principality_bulgaria",
            1908: None,
            1909: "kingdom_bulgaria",
            1946: "kingdom_bulgaria",
            1947: None,
        }
        for year, entity_id in expected.items():
            with self.subTest(year=year):
                self.assertEqual(
                    _label_policy_seed_id("bulgaria", year, year), entity_id
                )

    def test_texas_policy_excludes_pre_independence_and_transfer_year(self) -> None:
        for label in ("texas", "texan rebels"):
            with self.subTest(label=label, year=1835):
                self.assertIsNone(_label_policy_seed_id(label, 1835, 1835))
            with self.subTest(label=label, year=1836):
                self.assertEqual(
                    _label_policy_seed_id(label, 1836, 1836),
                    "clio_q170588_1836_8e422d86",
                )
            with self.subTest(label=label, year=1845):
                self.assertEqual(
                    _label_policy_seed_id(label, 1845, 1845),
                    "clio_q170588_1836_8e422d86",
                )
            with self.subTest(label=label, year=1846):
                self.assertIsNone(_label_policy_seed_id(label, 1846, 1846))

    def test_texas_opponent_code_uses_only_the_curated_mexican_republic(self) -> None:
        expected = {
            1823: None,
            1824: "mexican_republic",
            1836: "mexican_republic",
            1842: "mexican_republic",
            1863: "mexican_republic",
            1864: None,
            1867: None,
            1868: "clio_mx_mexico_1_1868_ffbcfbae",
            2024: "clio_mx_mexico_1_1868_ffbcfbae",
            2025: None,
        }
        for year, entity_id in expected.items():
            with self.subTest(year=year):
                self.assertEqual(
                    _policy_seed_id("mx_mexico_1", year, year), entity_id
                )
        self.assertEqual(IDENTITY_DENY_WINDOWS["mexico"], ((1864, 1867),))

    def test_syria_label_and_code_paths_share_the_uar_gap(self) -> None:
        expected = {
            1945: None,
            1946: "clio_sy_syria_modern_1946_86597c89",
            1957: "clio_sy_syria_modern_1946_86597c89",
            1958: None,
            1961: None,
            1962: "clio_q41137_1973_b05dea50",
            1967: "clio_q41137_1973_b05dea50",
            2026: "clio_q41137_1973_b05dea50",
        }
        for year, entity_id in expected.items():
            with self.subTest(year=year, path="label"):
                self.assertEqual(_label_policy_seed_id("syria", year, year), entity_id)
            with self.subTest(year=year, path="code"):
                self.assertEqual(
                    _policy_seed_id("sy_syria_modern", year, year), entity_id
                )

    def test_reviewed_1967_syria_contract_targets_post_uar_identity(self) -> None:
        candidate_id = "iwbd-169-64-1532"
        self.assertNotIn(candidate_id, WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS)
        contract = WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS[candidate_id]
        self.assertEqual(
            contract["defender"],
            (("clio_q41137_1973_b05dea50", "clio_q41137_1973_b05dea50"),),
        )

    def test_cow_and_gw_codes_use_the_same_crisp_boundaries(self) -> None:
        cases = (
            ("160", 1851, "argentine_confederation"),
            ("160", 1861, None),
            ("160", 1865, "argentine_republic_1861"),
            ("160", 1930, None),
            ("160", 1982, "clio_q414_1930_5e281b3e"),
            ("355", 1885, "principality_bulgaria"),
            ("355", 1908, None),
            ("355", 1913, "kingdom_bulgaria"),
            ("652", 1948, "clio_sy_syria_modern_1946_86597c89"),
            ("652", 1958, None),
            ("652", 1961, None),
            ("652", 1967, "clio_q41137_1973_b05dea50"),
        )
        for code, year, entity_id in cases:
            with self.subTest(code=code, year=year, path="cow"):
                self.assertEqual(_cow_policy_seed_id(code, year, year), entity_id)
            with self.subTest(code=code, year=year, path="gw"):
                self.assertEqual(_gw_policy_seed_id(code, year, year), entity_id)


if __name__ == "__main__":
    unittest.main()
