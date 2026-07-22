import json
import unittest
from collections import Counter
from pathlib import Path

from military_elo.config import ModelConfig
from military_elo.engine import EloEngine
from military_elo.models import Entity, Event, Participant
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
)
from military_elo.release import (
    SEED_CODE_POLICIES,
    _label_policy_seed_id,
    _policy_seed_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
RELEASE_ROOT = PROJECT_ROOT / "data" / "release"
RESULTS_PATH = PROJECT_ROOT / "web" / "data" / "results.json"

TSARDOM_ID = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"
PORTUGAL_IDS = frozenset(
    {
        "kingdom_portugal",
        "united_kingdom_portugal_brazil_algarves",
        "kingdom_portugal_restored",
        "portuguese_first_republic",
    }
)
WAVE5_ENTITY_IDS = PORTUGAL_IDS | {TSARDOM_ID}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _wave5_release_is_built() -> bool:
    entities_path = RELEASE_ROOT / "entities.json"
    events_path = RELEASE_ROOT / "events.json"
    if not entities_path.exists() or not events_path.exists():
        return False
    try:
        release_ids = {row["id"] for row in _json(entities_path)}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    return WAVE5_ENTITY_IDS <= release_ids


def _piraja_contract_row():
    contract = HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS["hced-Piraja1822-1"]
    row = {
        "candidate_id": "hced-Piraja1822-1",
        **contract["fingerprint"],
        "scale_raw": "2",
    }
    for field in ("source_row", "year_low", "year_best", "year_high"):
        row[field] = int(row[field])
    for field in (
        "seshat_side_1_candidates",
        "seshat_side_2_candidates",
        "war_names",
    ):
        row[field] = list(row[field])
    return row


class Wave5BulkPolicyTests(unittest.TestCase):
    def test_portugal_code_and_label_windows_are_exact(self) -> None:
        expected = {
            1146: None,
            1147: "kingdom_portugal",
            1814: "kingdom_portugal",
            1815: None,
            1816: "united_kingdom_portugal_brazil_algarves",
            1821: "united_kingdom_portugal_brazil_algarves",
            1822: None,
            1823: "kingdom_portugal_restored",
            1909: "kingdom_portugal_restored",
            1910: None,
            1911: "portuguese_first_republic",
            1925: "portuguese_first_republic",
            1926: None,
        }
        for year, entity_id in expected.items():
            with self.subTest(path="label", year=year):
                self.assertEqual(
                    _label_policy_seed_id("portugal", year, year), entity_id
                )
            for code in ("pt_portuguese_emp_1", "pt_portuguese_emp_2"):
                with self.subTest(path=code, year=year):
                    self.assertEqual(_policy_seed_id(code, year, year), entity_id)

        # An interval that straddles any identity reset is not silently assigned
        # to either neighbor. All three within-year transition years are likewise
        # unresolved in a year-only source.
        for low, high in (
            (1814, 1815),
            (1815, 1816),
            (1821, 1822),
            (1822, 1823),
            (1909, 1910),
            (1910, 1911),
            (1925, 1926),
        ):
            with self.subTest(path="label", interval=(low, high)):
                self.assertIsNone(_label_policy_seed_id("portugal", low, high))
            for code in ("pt_portuguese_emp_1", "pt_portuguese_emp_2"):
                with self.subTest(path=code, interval=(low, high)):
                    self.assertIsNone(_policy_seed_id(code, low, high))

    def test_piraja_exact_contract_is_the_only_1822_portugal_path(self) -> None:
        candidate_id = "hced-Piraja1822-1"
        contract = HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS[candidate_id]
        self.assertEqual(contract["review"]["event_date"], "1822-11-08")
        self.assertEqual(len(contract["review"]["source_urls"]), 2)

        row = _piraja_contract_row()
        generic = promote_hced_crosswalk_rows(
            [row], {}, set(), lambda polity: None,
            reviewed_identity_bindings={},
        )
        self.assertEqual(generic["events"], [])
        self.assertEqual(generic["rejections"]["outside_continuity_policy"], 1)

        reviewed = promote_hced_crosswalk_rows(
            [row], {}, set(), lambda polity: None,
            reviewed_identity_bindings={candidate_id: contract},
            resolve_reviewed_id=lambda entity_id, low, high: (entity_id, None),
            require_complete_reviewed_identity_bindings=True,
        )
        self.assertEqual(len(reviewed["events"]), 1)
        self.assertEqual(
            {participant["entity_id"] for participant in reviewed["events"][0]["participants"]},
            {"empire_brazil", "kingdom_portugal_restored"},
        )
        self.assertNotIn("portugal", reviewed["label_observations"])

    def test_piraja_contract_fails_closed_on_source_or_resolver_drift(self) -> None:
        row = _piraja_contract_row()
        changed = dict(row)
        changed["winner_raw"] = "Portugal"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            promote_hced_crosswalk_rows(
                [changed], {}, set(), lambda polity: None,
                reviewed_identity_bindings=HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
                resolve_reviewed_id=lambda entity_id, low, high: (entity_id, None),
            )
        with self.assertRaisesRegex(ValueError, "exact-ID resolver returned"):
            promote_hced_crosswalk_rows(
                [row], {}, set(), lambda polity: None,
                reviewed_identity_bindings=HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
                resolve_reviewed_id=lambda entity_id, low, high: ("wrong", None),
            )
        with self.assertRaisesRegex(ValueError, "target row is missing"):
            promote_hced_crosswalk_rows(
                [], {}, set(), lambda polity: None,
                reviewed_identity_bindings=HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
                resolve_reviewed_id=lambda entity_id, low, high: (entity_id, None),
                require_complete_reviewed_identity_bindings=True,
            )

    def test_cross_boundary_salvador_campaign_is_explicitly_excluded(self) -> None:
        self.assertIn("hced-Salvador1822-1823-1", HCED_CURATED_EXCLUSIONS)

    def test_tsardom_1721_boundary_splits_and_crossing_intervals_fail(self) -> None:
        for resolver, key in (
            (_policy_seed_id, "ru_romanov_dyn_1"),
            (_label_policy_seed_id, "russia"),
        ):
            with self.subTest(path=key, edge="first_tsardom_year"):
                self.assertEqual(resolver(key, 1547, 1547), TSARDOM_ID)
                self.assertIsNone(resolver(key, 1546, 1546))
            with self.subTest(path=key, edge="last_tsardom_year"):
                self.assertEqual(resolver(key, 1720, 1720), TSARDOM_ID)
            with self.subTest(path=key, edge="first_empire_year"):
                self.assertEqual(resolver(key, 1721, 1721), "russian_empire")
            with self.subTest(path=key, edge="crossing_interval"):
                self.assertIsNone(resolver(key, 1720, 1721))

        # The second Romanov source code names only the imperial-era identity.
        self.assertIsNone(_policy_seed_id("ru_romanov_dyn_2", 1720, 1720))
        self.assertEqual(
            _policy_seed_id("ru_romanov_dyn_2", 1721, 1721), "russian_empire"
        )

    def test_policy_targets_are_narrow_existing_seed_entities_with_direct_sources(
        self,
    ) -> None:
        entities = {row["id"]: row for row in _json(SEED_ROOT / "entities.json")}
        sources = {row["id"]: row for row in _json(SEED_ROOT / "sources.json")}
        expected = {
            TSARDOM_ID: {
                "interval": (1547, 1720),
                "predecessors": [],
                "source_ids": {
                    "russian_presidential_library_ivan_iv_1547",
                    "russian_presidential_library_empire_1721",
                    "cliopatria_polities",
                },
            },
            "kingdom_portugal": {
                "interval": (1143, 1814),
                "predecessors": [],
                "source_ids": {
                    "portugal_mne_foundation_1143",
                    "brazil_chamber_united_kingdom_1815",
                },
            },
            "united_kingdom_portugal_brazil_algarves": {
                "interval": (1815, 1822),
                "predecessors": ["kingdom_portugal"],
                "source_ids": {
                    "brazil_chamber_united_kingdom_1815",
                    "brazil_government_independence_timeline",
                },
            },
            "kingdom_portugal_restored": {
                "interval": (1822, 1910),
                "predecessors": ["united_kingdom_portugal_brazil_algarves"],
                "source_ids": {
                    "brazil_government_independence_timeline",
                    "portugal_parliament_monarchy_1910",
                },
            },
            "portuguese_first_republic": {
                "interval": (1910, 1926),
                "predecessors": ["kingdom_portugal_restored"],
                "source_ids": {
                    "portugal_parliament_first_republic",
                },
            },
        }

        self.assertLessEqual(WAVE5_ENTITY_IDS, set(entities))
        for entity_id, contract in expected.items():
            with self.subTest(entity=entity_id):
                entity = entities[entity_id]
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    contract["interval"],
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], contract["predecessors"])
                self.assertEqual(set(entity["source_ids"]), contract["source_ids"])
                self.assertLessEqual(set(entity["source_ids"]), set(sources))
                note = entity["continuity_note"].casefold()
                self.assertTrue(
                    "no rating" in note or "inherits nothing" in note,
                    entity["continuity_note"],
                )

        direct_source_ids = {
            source_id
            for contract in expected.values()
            for source_id in contract["source_ids"]
            if source_id != "cliopatria_polities"
        }
        for source_id in direct_source_ids:
            with self.subTest(source=source_id):
                self.assertEqual(
                    sources[source_id]["evidence_roles"],
                    ["identity_boundary_or_context_reference"],
                )
                self.assertTrue(sources[source_id]["url"].startswith("https://"))

        policy_targets = {
            entity_id
            for code in ("pt_portuguese_emp_1", "pt_portuguese_emp_2", "ru_romanov_dyn_1")
            for _, _, entity_id in SEED_CODE_POLICIES[code]
        }
        self.assertLessEqual(WAVE5_ENTITY_IDS, policy_targets)
        self.assertLessEqual(policy_targets, set(entities))

    def test_portuguese_successors_do_not_inherit_elo(self) -> None:
        rows = {row["id"]: row for row in _json(SEED_ROOT / "entities.json")}
        portugal_entities = [Entity.from_dict(rows[entity_id]) for entity_id in PORTUGAL_IDS]
        rival = Entity("test_rival", "Test rival", "state", 1000, 2000)
        dimensions = {
            "battlefield_outcome": 1.0,
            "political_objectives": 1.0,
            "territorial_outcome": 1.0,
            "sovereignty_survival": 1.0,
            "settlement_durability": 1.0,
            "force_preservation": 1.0,
        }
        event = Event(
            id="pre_union_portuguese_win",
            name="Pre-union Portuguese win",
            year=1800,
            end_year=1800,
            event_type="war",
            war_type="interstate_limited",
            scale="major_war",
            stakes="major",
            decisiveness=1.0,
            confidence=1.0,
            participants=(
                Participant("kingdom_portugal", "a", outcome=dimensions),
                Participant(
                    "test_rival",
                    "b",
                    outcome={key: 0.0 for key in dimensions},
                ),
            ),
            source_ids=("test_source",),
        )
        config = ModelConfig()
        engine = EloEngine(config).run([*portugal_entities, rival], [event])

        self.assertGreater(
            engine.states["kingdom_portugal"].strategic.rating, config.baseline
        )
        for successor_id in (
            "united_kingdom_portugal_brazil_algarves",
            "kingdom_portugal_restored",
            "portuguese_first_republic",
        ):
            with self.subTest(successor=successor_id):
                state = engine.states[successor_id]
                self.assertEqual(state.strategic.rating, config.baseline)
                self.assertEqual(state.tactical.rating, config.baseline)
                self.assertEqual(state.operational.rating, config.baseline)
                self.assertEqual(state.events, 0)


@unittest.skipUnless(
    _wave5_release_is_built(),
    "Wave 5 Portugal/Tsardom release artifacts have not been rebuilt",
)
class Wave5BulkArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _json(RELEASE_ROOT / "events.json")
        cls.entities = _json(RELEASE_ROOT / "entities.json")

    @staticmethod
    def _participants(event) -> set[str]:
        return {row["entity_id"] for row in event["participants"]}

    def test_exact_portugal_and_tsardom_hced_cohort_sizes(self) -> None:
        portugal = [
            event
            for event in self.events
            if self._participants(event) & PORTUGAL_IDS
            and event.get("identity_resolution") != "candidate_keyed_exact"
        ]
        tsardom = [
            event
            for event in self.events
            if TSARDOM_ID in self._participants(event)
        ]

        # Portugal has its original cohort plus the audited 1515 Hormuz row;
        # the already-rated 1918 Estaires row remains migrated from its
        # Cliopatria envelope into the curated First Republic identity.
        # Tsardom contains 55 newly unlocked rows plus
        # the three already-rated rows on the existing Cliopatria identity;
        # three source rows failed the historical accuracy audit.
        self.assertEqual(len(portugal), 84)
        self.assertEqual(len(tsardom), 62)
        self.assertEqual(
            Counter(
                "label" if event["id"].startswith("hced_label_") else "crosswalk"
                for event in portugal
            ),
            {"crosswalk": 16, "label": 68},
        )
        self.assertEqual(
            Counter(
                "label" if event["id"].startswith("hced_label_") else "crosswalk"
                for event in tsardom
            ),
            {"crosswalk": 45, "label": 17},
        )

        combined = [*portugal, *tsardom]
        event_ids = [event["id"] for event in combined]
        candidate_ids = [event.get("hced_candidate_id") for event in combined]
        self.assertEqual(len(combined), 146)
        self.assertEqual(len(event_ids), len(set(event_ids)))
        self.assertNotIn(None, candidate_ids)
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        # Wave 5 rows carry the bare hced family; the four Tsardom rows later
        # re-promoted by exact Wave 8 lanes carry curated bibliographic
        # families instead.
        curated_family_rows = {
            event["id"]
            for event in combined
            if tuple(event.get("outcome_source_family_ids", ())) != ("hced",)
        }
        self.assertEqual(
            curated_family_rows,
            {
                "hced_wave8_germany_hced_riga1709_1710_1",
                "hced_wave8_livonian_order_hced_narva1558_1",
                "hced_wave8_livonian_order_hced_fellin1560_1",
                "hced_wave8_livonian_order_hced_oomuli1560_1",
            },
        )

    def test_tsardom_is_one_reused_identity_with_one_elo_history(self) -> None:
        tsardom_entities = [
            entity
            for entity in self.entities
            if entity["name"].casefold() == "tsardom of russia"
            or entity["id"] in {TSARDOM_ID, "tsardom_russia"}
        ]
        self.assertEqual(len(tsardom_entities), 1)
        self.assertEqual(tsardom_entities[0]["id"], TSARDOM_ID)
        self.assertEqual(
            (tsardom_entities[0]["start_year"], tsardom_entities[0]["end_year"]),
            (1547, 1720),
        )

        tsardom_events = [
            event
            for event in self.events
            if TSARDOM_ID in self._participants(event)
        ]
        self.assertEqual(len(tsardom_events), 62)
        self.assertFalse(
            any(
                "tsardom_russia" in self._participants(event)
                for event in self.events
            )
        )

        results = _json(RESULTS_PATH)
        for collection_name, collection in (
            ("rated entities", results["entities"]),
            ("registry", results["registry"]["entities"]),
        ):
            with self.subTest(site_collection=collection_name):
                site_tsardoms = [
                    entity
                    for entity in collection
                    if entity["name"].casefold() == "tsardom of russia"
                    or entity["id"] in {TSARDOM_ID, "tsardom_russia"}
                ]
                self.assertEqual(len(site_tsardoms), 1)
                self.assertEqual(site_tsardoms[0]["id"], TSARDOM_ID)

        self.assertIn(TSARDOM_ID, results["series"])
        self.assertNotIn("tsardom_russia", results["series"])
        site_tsardom_events = [
            event
            for event in results["events"]
            if TSARDOM_ID in self._participants(event)
        ]
        self.assertEqual(len(site_tsardom_events), 62)
        self.assertFalse(
            any(
                "tsardom_russia" in self._participants(event)
                for event in results["events"]
            )
        )

    def test_bulk_events_remain_inside_their_identity_windows(self) -> None:
        portugal_windows = {
            "kingdom_portugal": (1147, 1814),
            "united_kingdom_portugal_brazil_algarves": (1815, 1821),
            "kingdom_portugal_restored": (1822, 1909),
            "portuguese_first_republic": (1911, 1925),
        }
        for event in self.events:
            participants = self._participants(event)
            matched_portugal = participants & PORTUGAL_IDS
            if matched_portugal:
                self.assertEqual(len(matched_portugal), 1, event["id"])
                entity_id = next(iter(matched_portugal))
                low, high = portugal_windows[entity_id]
                self.assertGreaterEqual(event["year"], low, event["id"])
                self.assertLessEqual(event["end_year"], high, event["id"])
            if TSARDOM_ID in participants:
                self.assertGreaterEqual(event["year"], 1547, event["id"])
                self.assertLessEqual(event["end_year"], 1720, event["id"])


if __name__ == "__main__":
    unittest.main()
