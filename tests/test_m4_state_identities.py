import json
import unittest
from pathlib import Path

from military_elo.release import (
    HCED_CURATED_EXCLUSIONS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    IDENTITY_DENY_WINDOWS,
    IWD_COW_CODE_POLICIES,
    IWD_CURATED_PARENT_EXCLUSIONS,
    SEED_EVENT_INTERVAL_EXEMPTIONS,
    SEED_CODE_POLICIES,
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_GW_CODE_POLICIES,
    _cow_policy_seed_id,
    _label_policy_seed_id,
    _policy_seed_id,
    _resolve_label_tiers,
    _slug,
    _validate_seed_event_intervals,
    aggregate_iwd_parent_wars,
    resolve_hced_side_label,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"
REGISTRY = PROJECT_ROOT / "data" / "catalog" / "registry.json"


def _empty_tier_context():
    return {
        "seed_entities": [],
        "release_entities": {},
        "entity_labels": {},
        "label_observations": {},
        "seed_by_id": {},
        "polity_alias_index": {},
        "seed_label_index": {},
    }


class StateLabelWindowTests(unittest.TestCase):
    def test_france_resolves_era_correctly_with_deliberate_gaps(self) -> None:
        self.assertEqual(_label_policy_seed_id("france", 1700, 1700), "kingdom_france")
        self.assertEqual(_label_policy_seed_id("france", 1795, 1795), "french_first_republic")
        self.assertEqual(_label_policy_seed_id("france", 1808, 1812), "first_french_empire")
        self.assertEqual(_label_policy_seed_id("france", 1859, 1859), "second_french_empire")
        self.assertEqual(_label_policy_seed_id("france", 1914, 1918), "french_third_republic")
        self.assertEqual(_label_policy_seed_id("france", 1991, 1991), "french_fifth_republic")
        # Restoration/July Monarchy/Second Republic and Vichy/Fourth Republic gaps.
        self.assertIsNone(_label_policy_seed_id("france", 1830, 1830))
        self.assertIsNone(_label_policy_seed_id("france", 1950, 1950))
        # Bare 1870 fits both the Second Empire and Third Republic windows.
        self.assertIsNone(_label_policy_seed_id("france", 1870, 1870))

    def test_habsburg_chain_and_branch_ambiguity(self) -> None:
        for label in ("austria", "habsburg empire"):
            with self.subTest(label=label):
                self.assertIsNone(_label_policy_seed_id(label, 1540, 1550))
                self.assertEqual(_label_policy_seed_id(label, 1683, 1683), "habsburg_monarchy")
                self.assertEqual(_label_policy_seed_id(label, 1809, 1809), "austrian_empire")
                self.assertEqual(_label_policy_seed_id(label, 1914, 1918), "austria_hungary")
                self.assertIsNone(_label_policy_seed_id(label, 1920, 1920))
        self.assertEqual(_label_policy_seed_id("austria hungary", 1859, 1859), "austrian_empire")

    def test_exact_habsburg_boundaries(self) -> None:
        label_expected = {
            1803: "habsburg_monarchy",
            1804: "austrian_empire",
            1866: "austrian_empire",
            1867: "austria_hungary",
        }
        cow_expected = {
            1803: None,
            1804: "austrian_empire",
            1866: "austrian_empire",
            1867: "austria_hungary",
        }
        for year, entity_id in label_expected.items():
            with self.subTest(year=year, path="label"):
                self.assertEqual(_label_policy_seed_id("austria", year, year), entity_id)
            with self.subTest(year=year, path="cow"):
                self.assertEqual(_cow_policy_seed_id("300", year, year), cow_expected[year])

    def test_england_interregnum_gap(self) -> None:
        self.assertEqual(_label_policy_seed_id("england", 1066, 1066), "kingdom_england")
        self.assertEqual(_label_policy_seed_id("england", 1700, 1700), "kingdom_england")
        self.assertIsNone(_label_policy_seed_id("england", 1650, 1655))
        self.assertIsNone(_label_policy_seed_id("england", 1648, 1650))
        self.assertIsNone(_label_policy_seed_id("england", 1710, 1710))
        self.assertEqual(_label_policy_seed_id("england", 1648, 1648), "kingdom_england")
        self.assertEqual(_label_policy_seed_id("england", 1661, 1661), "kingdom_england")

    def test_persia_five_window_chain(self) -> None:
        self.assertEqual(_label_policy_seed_id("persia", -490, -480), "achaemenid_empire")
        self.assertEqual(_label_policy_seed_id("persia", 260, 260), "sasanian_empire")
        self.assertEqual(_label_policy_seed_id("persia", 1736, 1736), "safavid_empire")
        self.assertEqual(_label_policy_seed_id("persia", 1740, 1740), "afsharid_iran")
        self.assertEqual(_label_policy_seed_id("persia", 1857, 1857), "qajar_iran")
        # Seleucid/Parthian, Zand, and Pahlavi eras stay staged.
        self.assertIsNone(_label_policy_seed_id("persia", -100, -100))
        self.assertIsNone(_label_policy_seed_id("persia", 1770, 1770))
        self.assertIsNone(_label_policy_seed_id("persia", 1935, 1935))

    def test_remaining_state_windows(self) -> None:
        self.assertEqual(_label_policy_seed_id("prussia", 1757, 1757), "kingdom_prussia")
        self.assertEqual(_label_policy_seed_id("prussia", 1870, 1870), "kingdom_prussia")
        self.assertEqual(_label_policy_seed_id("prussia", 1871, 1871), "german_empire")
        self.assertIsNone(_label_policy_seed_id("prussia", 1880, 1880))
        self.assertEqual(_label_policy_seed_id("poland", 1683, 1683), "polish_lithuanian_commonwealth")
        self.assertEqual(_label_policy_seed_id("poland", 1920, 1920), "second_polish_republic")
        self.assertIsNone(_label_policy_seed_id("poland", 1850, 1850))
        self.assertEqual(_label_policy_seed_id("sweden", 1709, 1709), "kingdom_sweden")
        self.assertIsNone(_label_policy_seed_id("sweden", 1400, 1400))
        self.assertEqual(_label_policy_seed_id("denmark", 1864, 1864), "kingdom_denmark")
        self.assertEqual(_label_policy_seed_id("scotland", 1314, 1314), "kingdom_scotland")
        self.assertIsNone(_label_policy_seed_id("scotland", 1750, 1750))
        self.assertEqual(_label_policy_seed_id("venice", 1571, 1571), "republic_venice")
        self.assertEqual(_label_policy_seed_id("korea", 1592, 1598), "joseon")
        self.assertIsNone(_label_policy_seed_id("korea", 1904, 1905))
        self.assertEqual(_label_policy_seed_id("afghanistan", 1761, 1761), "durrani_empire")
        self.assertEqual(_label_policy_seed_id("afghanistan", 1880, 1880), "emirate_afghanistan")
        self.assertIsNone(_label_policy_seed_id("afghanistan", 1935, 1935))
        self.assertEqual(_label_policy_seed_id("marathas", 1761, 1761), "maratha_confederacy")
        self.assertEqual(_label_policy_seed_id("maratha empire", 1803, 1803), "maratha_confederacy")
        self.assertEqual(_label_policy_seed_id("mysore", 1780, 1780), "kingdom_mysore")
        self.assertEqual(_label_policy_seed_id("punjab", 1846, 1846), "sikh_empire")
        self.assertEqual(_label_policy_seed_id("transvaal", 1900, 1900), "south_african_republic")
        self.assertEqual(_label_policy_seed_id("muslim caliphate", 636, 636), "rashidun_caliphate")
        self.assertEqual(_label_policy_seed_id("muslim caliphate", 717, 718), "umayyad_caliphate")

    def test_wave4_exact_source_label_windows(self) -> None:
        cases = (
            ("macedonia", -336, -323, "macedonian_empire"),
            ("ummayyad caliphate", 661, 750, "umayyad_caliphate"),
            ("mamluks", 1250, 1517, "mamluk_sultanate"),
            ("dutch rebels", 1568, 1795, "dutch_republic"),
            ("untied kingdom", 1707, 2026, "united_kingdom"),
        )
        for label, low, high, entity_id in cases:
            with self.subTest(label=label, edge="low"):
                self.assertEqual(_label_policy_seed_id(label, low, low), entity_id)
                self.assertIsNone(_label_policy_seed_id(label, low - 1, low - 1))
            with self.subTest(label=label, edge="high"):
                self.assertEqual(_label_policy_seed_id(label, high, high), entity_id)
                self.assertIsNone(_label_policy_seed_id(label, high + 1, high + 1))


class StateCodePolicyTests(unittest.TestCase):
    def test_cow_code_policies_resolve_by_era(self) -> None:
        self.assertEqual(_cow_policy_seed_id("255", 1806, 1806), "kingdom_prussia")
        self.assertEqual(_cow_policy_seed_id("255", 1914, 1918), "german_empire")
        self.assertIsNone(_cow_policy_seed_id("255", 1870, 1871))
        self.assertEqual(_cow_policy_seed_id("300", 1859, 1859), "austrian_empire")
        self.assertEqual(_cow_policy_seed_id("300", 1914, 1918), "austria_hungary")
        self.assertEqual(_cow_policy_seed_id("345", 1912, 1913), "kingdom_serbia")
        self.assertIsNone(_cow_policy_seed_id("345", 1941, 1941))

    def test_prussia_germany_boundary_agrees_across_pipelines(self) -> None:
        for year, entity_id in ((1870, "kingdom_prussia"), (1871, "german_empire")):
            with self.subTest(year=year):
                self.assertEqual(_label_policy_seed_id("prussia", year, year), entity_id)
                self.assertEqual(_cow_policy_seed_id("255", year, year), entity_id)

    def test_wave4_cow_identity_windows_are_exact(self) -> None:
        cases = (
            ("100", 1863, 1885, "united_states_colombia"),
            ("670", 1932, 2026, "kingdom_saudi_arabia"),
            ("678", 1918, 1961, "mutawakkilite_kingdom_yemen"),
        )
        for code, low, high, entity_id in cases:
            with self.subTest(code=code, edge="low"):
                self.assertEqual(_cow_policy_seed_id(code, low, low), entity_id)
                self.assertIsNone(_cow_policy_seed_id(code, low - 1, low - 1))
            with self.subTest(code=code, edge="high"):
                self.assertEqual(_cow_policy_seed_id(code, high, high), entity_id)
                self.assertIsNone(_cow_policy_seed_id(code, high + 1, high + 1))

    def test_wave4_seed_identities_are_narrow_and_directly_sourced(self) -> None:
        seed_root = PROJECT_ROOT / "data" / "seed"
        entities = {
            entity["id"]: entity
            for entity in json.loads((seed_root / "entities.json").read_text(encoding="utf-8"))
        }
        source_ids = {
            source["id"]
            for source in json.loads((seed_root / "sources.json").read_text(encoding="utf-8"))
        }
        expected = {
            "united_states_colombia": (
                "United States of Colombia", 1863, 1885, "colombia"
            ),
            "kingdom_saudi_arabia": (
                "Kingdom of Saudi Arabia", 1932, None, "saudi arabia"
            ),
            "mutawakkilite_kingdom_yemen": (
                "Mutawakkilite Kingdom of Yemen", 1918, 1961, "yemen"
            ),
        }
        for entity_id, (name, low, high, forbidden_alias) in expected.items():
            with self.subTest(entity=entity_id):
                entity = entities[entity_id]
                self.assertEqual(
                    (entity["name"], entity["start_year"], entity["end_year"]),
                    (name, low, high),
                )
                self.assertNotIn(
                    forbidden_alias,
                    {str(alias).casefold() for alias in entity["aliases"]},
                )
                self.assertTrue(entity["source_ids"])
                self.assertLessEqual(set(entity["source_ids"]), source_ids)

    def test_extended_seed_code_windows(self) -> None:
        self.assertEqual(_policy_seed_id("fr_bourbon_k_2", 1795, 1800), "french_first_republic")
        self.assertEqual(_policy_seed_id("gb_british_emp_1", 1588, 1588), "kingdom_england")
        self.assertIsNone(_policy_seed_id("gb_british_emp_1", 1650, 1655))
        self.assertEqual(_policy_seed_id("gb_british_emp_1", 1800, 1800), "united_kingdom")
        self.assertEqual(_policy_seed_id("at_habsburg_1", 1683, 1683), "habsburg_monarchy")
        self.assertIsNone(_policy_seed_id("at_habsburg_1", 1540, 1550))
        self.assertEqual(_policy_seed_id("kr_joseon", 1592, 1598), "joseon")
        self.assertEqual(_policy_seed_id("rs_serbia_k", 1914, 1918), "kingdom_serbia")
        self.assertEqual(_policy_seed_id("br_brazil_emp", 1865, 1870), "empire_brazil")
        self.assertEqual(_policy_seed_id("ir_qajar_dyn", 1822, 1822), "qajar_iran")
        self.assertIsNone(_policy_seed_id("fr_france_modern_1", 1870, 1870))
        self.assertEqual(
            _policy_seed_id("fr_france_modern_1", 1871, 1871),
            "french_third_republic",
        )

    def test_every_policy_window_targets_an_existing_seed_identity(self) -> None:
        seed_path = PROJECT_ROOT / "data" / "seed" / "entities.json"
        seed_ids = {e["id"] for e in json.loads(seed_path.read_text(encoding="utf-8"))}
        tables = {
            "seed_code": SEED_CODE_POLICIES,
            "hced_label": HCED_LABEL_POLICIES,
            "iwd_cow": IWD_COW_CODE_POLICIES,
            "ucdp_gw": UCDP_GW_CODE_POLICIES,
            "ucdp_actor": UCDP_ACTOR_PARTY_POLICIES,
        }
        for table_name, table in tables.items():
            for policy_key, windows in table.items():
                for _, _, entity_id in windows:
                    with self.subTest(table=table_name, key=policy_key, entity=entity_id):
                        self.assertIn(entity_id, seed_ids)

    def test_france_revolution_boundary_edges(self) -> None:
        self.assertEqual(_label_policy_seed_id("france", 1792, 1792), "kingdom_france")
        self.assertEqual(
            _label_policy_seed_id("france", 1793, 1793), "french_first_republic"
        )

    def test_seed_event_interval_exemptions_are_exact_and_enforced(self) -> None:
        seed_root = PROJECT_ROOT / "data" / "seed"
        entities = json.loads((seed_root / "entities.json").read_text(encoding="utf-8"))
        events = json.loads((seed_root / "events.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(SEED_EVENT_INTERVAL_EXEMPTIONS),
            {
                ("american_revolutionary_war", "united_states"),
                ("napoleonic_wars", "first_french_empire"),
                ("afghanistan_war_2001_2021", "islamic_republic_afghanistan"),
            },
        )
        self.assertEqual(
            {
                key: (
                    value["event_interval"],
                    value["entity_interval"],
                )
                for key, value in SEED_EVENT_INTERVAL_EXEMPTIONS.items()
            },
            {
                ("american_revolutionary_war", "united_states"): (
                    (1775, 1783),
                    (1776, None),
                ),
                ("napoleonic_wars", "first_french_empire"): (
                    (1803, 1815),
                    (1804, 1815),
                ),
                ("afghanistan_war_2001_2021", "islamic_republic_afghanistan"): (
                    (2001, 2021),
                    (2004, 2021),
                ),
            },
        )
        _validate_seed_event_intervals(events, {e["id"]: e for e in entities})

        widened = [dict(event) for event in events]
        next(
            event
            for event in widened
            if event["id"] == "american_revolutionary_war"
        )["year"] = 1774
        with self.assertRaisesRegex(ValueError, "interval exemption expected"):
            _validate_seed_event_intervals(
                widened,
                {entity["id"]: entity for entity in entities},
            )


class IdentityDenyWindowTests(unittest.TestCase):
    def test_turkey_deny_window_blocks_every_tier(self) -> None:
        self.assertEqual(IDENTITY_DENY_WINDOWS["turkey"], ((1919, 1923),))
        self.assertEqual(IDENTITY_DENY_WINDOWS["latvia"], ((1918, 1991),))
        context = _empty_tier_context()
        context["seed_entities"] = [
            {
                "id": "ottoman_empire",
                "name": "Ottoman Empire",
                "aliases": ["Turkey"],
                "start_year": 1299,
                "end_year": 1922,
            }
        ]
        # Outside the window the alias resolves normally.
        entity_id, _, tier = _resolve_label_tiers(
            "turkey", 1912, 1913, context, require_observation_coherence=True
        )
        self.assertEqual((entity_id, tier), ("ottoman_empire", "seed_alias"))
        # Inside (or intersecting) the window it never resolves.
        for low, high in ((1919, 1919), (1921, 1921), (1918, 1919), (1923, 1925)):
            with self.subTest(span=(low, high)):
                entity_id, _, tier = _resolve_label_tiers(
                    "turkey", low, high, context, require_observation_coherence=True
                )
                self.assertIsNone(entity_id)

    def test_deny_windows_and_label_policies_are_disjoint(self) -> None:
        self.assertEqual(set(IDENTITY_DENY_WINDOWS) & set(HCED_LABEL_POLICIES), set())


class PipelineAsymmetryTests(unittest.TestCase):
    def test_iwd_alias_tiers_intentionally_bypass_hced_front_gates(self) -> None:
        context = _empty_tier_context()
        context["seed_entities"] = [
            {
                "id": "broad_spain_envelope",
                "name": "Spain envelope",
                "aliases": ["Spain"],
                "start_year": 1516,
                "end_year": 2024,
            }
        ]
        # HCED treats its label-policy table as authoritative and stages 1909.
        entity_id, _, reason, _ = resolve_hced_side_label("Spain", 1909, 1909, context)
        self.assertEqual((entity_id, reason), (None, "label_outside_policy_window"))
        # IWD/IWBD intentionally call the lower alias tiers directly to
        # preserve their established promotion contract.
        entity_id, _, tier = _resolve_label_tiers(
            "spain", 1909, 1909, context, require_observation_coherence=False
        )
        self.assertEqual((entity_id, tier), ("broad_spain_envelope", "seed_alias"))


class CuratedExclusionTableTests(unittest.TestCase):
    def test_exclusion_tables_are_enumerated_and_documented(self) -> None:
        self.assertEqual(len(HCED_CURATED_EXCLUSIONS), 62)
        self.assertEqual(len(HCED_LABEL_CURATED_EXCLUSIONS), 53)
        self.assertEqual(set(IWD_CURATED_PARENT_EXCLUSIONS), {"5", "10", "42"})
        self.assertLessEqual(
            {
                "hced-Megalopolis-331-1",
                "hced-Jaxartes-329-1",
                "hced-Antioch1268-1",
                "hced-Mons1572-1",
                "hced-Steenwijk1592-1",
                "hced-Amjhera1728-1",
                "hced-Abensberg1809-1",
            },
            set(HCED_LABEL_CURATED_EXCLUSIONS),
        )
        self.assertLessEqual(
            {
                "hced-Altona1714-1",
                "hced-Bronnitsa1614-1",
                "hced-Punitz1704-1",
                "hced-Salvador1638-1",
                "hced-Malacca1606-1",
                "hced-Beachy Head1707-1",
                "hced-Colonia do Sacrimento1735-1",
                "hced-Reval1719-1",
                "hced-Majadahonda1812-1",
                "hced-Elba1811-1",
                "hced-Campo1811-1",
                "hced-Azov1695-1696-1",
                "hced-Salvador1822-1823-1",
                "hced-Aden1513-1",
                "hced-Wofla1542-1",
                "hced-Marbella1705-1",
                "hced-Cadiz1810-1812-1",
                "hced-Barrosa1811-1",
                "hced-Riga1701-1",
            },
            set(HCED_CURATED_EXCLUSIONS),
        )
        for table in (HCED_CURATED_EXCLUSIONS, HCED_LABEL_CURATED_EXCLUSIONS):
            for candidate_id, reason in table.items():
                with self.subTest(candidate=candidate_id):
                    self.assertTrue(candidate_id.startswith("hced-"))
                    self.assertGreater(len(reason), 10)

    def test_iwd_curated_parent_exclusion_stages_the_whole_parent(self) -> None:
        components = [
            {
                "candidate_id": "iwd-10",
                "source_component_id": "10",
                "parent_war_id": "10",
                "parent_war_name": "ItalianUnification1859",
                "name": "ItalianUnification1859",
                "start_year": 1859,
                "end_year": 1859,
                "terminal_outcome_code": "1",
                "initiators": [{"name": "Italy", "cow_code": "325"}],
                "targets": [{"name": "Austria", "cow_code": "300"}],
            }
        ]
        result = aggregate_iwd_parent_wars(
            components,
            [],
            lambda name, code, low, high: (f"entity_{name.lower()}", None),
            curated_parent_exclusions=IWD_CURATED_PARENT_EXCLUSIONS,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["curated_exclusion"], 1)


@unittest.skipUnless(
    RELEASE_EVENTS.exists() and REGISTRY.exists(), "release artifacts not built"
)
class TrancheReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_ledger_composition_pins(self) -> None:
        self.assertEqual(len(self.events), 4_406)
        label = [e for e in self.events if e.get("identity_resolution") == "label"]
        crosswalk = [
            e
            for e in self.events
            if str(e["id"]).startswith("hced_") and e.get("identity_resolution") is None
        ]
        self.assertEqual(len(label), 2_328)
        self.assertEqual(len(crosswalk), 1_824)
        self.assertEqual(sum(str(e["id"]).startswith("iwd_war_") for e in self.events), 64)
        self.assertEqual(sum(str(e["id"]).startswith("iwbd_") for e in self.events), 143)
        self.assertEqual(sum(str(e["id"]).startswith("ucdp_term_") for e in self.events), 7)
        rated = {p["entity_id"] for e in self.events for p in e["participants"]}
        self.assertEqual(len(rated), 235)

    def test_enumerated_identity_supersessions(self) -> None:
        qajar_events = [
            e
            for e in self.events
            if any(p["entity_id"] == "qajar_iran" for p in e["participants"])
        ]
        khoi_1822 = [e for e in qajar_events if e["year"] == 1822]
        self.assertEqual(len(khoi_1822), 1)
        brazil_events = [
            e
            for e in self.events
            if any(p["entity_id"] == "empire_brazil" for p in e["participants"])
        ]
        # 26 rated events total; 18 of them are the enumerated Paraguayan-war
        # supersessions from the previous build's Cliopatria envelope.
        self.assertEqual(len(brazil_events), 26)
        paraguayan_war = [
            e for e in brazil_events if not (e["end_year"] < 1864 or e["year"] > 1870)
        ]
        self.assertGreaterEqual(len(paraguayan_war), 18)

    def test_superseded_envelopes_left_the_registry(self) -> None:
        rows_by_name: dict[str, list[dict]] = {}
        for row in self.registry["entities"]:
            rows_by_name.setdefault(str(row["name"]), []).append(row)
        for name in ("Empire of Brazil", "Qajar Iran", "Maratha Confederacy"):
            with self.subTest(name=name):
                rows = rows_by_name.get(name, [])
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["identity_status"], "curated")
        self.assertEqual(len(self.registry["entities"]), 1_598)

    def test_no_kingdom_of_england_event_bridges_the_interregnum(self) -> None:
        for event in self.events:
            if any(p["entity_id"] == "kingdom_england" for p in event["participants"]):
                intersects = not (event["end_year"] < 1649 or event["year"] > 1660)
                self.assertFalse(
                    intersects,
                    f"{event['id']} rates kingdom_england inside the 1649-1660 gap",
                )

    def test_curated_exclusions_never_enter_the_ledger(self) -> None:
        event_ids = {str(e["id"]) for e in self.events}
        for candidate_id in (*HCED_CURATED_EXCLUSIONS, *HCED_LABEL_CURATED_EXCLUSIONS):
            with self.subTest(candidate=candidate_id):
                self.assertNotIn(f"hced_{_slug(candidate_id, 80)}", event_ids)
                self.assertNotIn(f"hced_label_{_slug(candidate_id, 74)}", event_ids)
        for event in self.events:
            if str(event["id"]).startswith("iwd_war_"):
                self.assertNotIn(
                    str(event.get("iwd_parent_war_id")), IWD_CURATED_PARENT_EXCLUSIONS
                )


if __name__ == "__main__":
    unittest.main()
