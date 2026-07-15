import json
import unittest
from pathlib import Path

from military_elo.release import (
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _cow_policy_seed_id,
    _humanize_war_name,
    _overlaps_seed_war,
    _seed_war_token_spans,
    _war_tokens,
    _war_tokens_match,
    aggregate_iwd_parent_wars,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"
RELEASE_METADATA = PROJECT_ROOT / "data" / "release" / "metadata.json"
REGISTRY = PROJECT_ROOT / "data" / "catalog" / "registry.json"
RESULTS = PROJECT_ROOT / "web" / "data" / "results.json"


def _component(
    candidate_id,
    parent_id,
    parent_name,
    name,
    start,
    end,
    outcome,
    initiators,
    targets,
):
    return {
        "candidate_id": candidate_id,
        "source_component_id": candidate_id.rsplit("-", 1)[-1],
        "parent_war_id": parent_id,
        "parent_war_name": parent_name,
        "name": name,
        "start_year": start,
        "end_year": end,
        "terminal_outcome_code": outcome,
        "initiators": [{"name": name_, "cow_code": code} for name_, code in initiators],
        "targets": [{"name": name_, "cow_code": code} for name_, code in targets],
    }


def _resolve_all(name, cow_code, low_year, high_year):
    return f"entity_{name.lower().replace(' ', '_')}", None


class WarTokenMatcherTests(unittest.TestCase):
    def test_seed_overlap_catches_world_war_naming_variants(self) -> None:
        seed_spans = _seed_war_token_spans(
            [
                {"event_type": "war", "name": "First World War", "cluster_id": "first_world_war", "year": 1914, "end_year": 1918},
                {"event_type": "war", "name": "Second World War in Europe", "cluster_id": "second_world_war_europe", "year": 1939, "end_year": 1945},
                {"event_type": "war", "name": "Gulf War", "cluster_id": "gulf_war", "year": 1990, "end_year": 1991},
                {"event_type": "war", "name": "Korean War", "cluster_id": "korean_war", "year": 1950, "end_year": 1953},
            ]
        )
        for variant, low, high in (
            ("WorldWarI", 1914, 1918),
            ("WorldWarII", 1939, 1945),
            ("GulfWar1991", 1991, 1991),
            ("Korean_1950-53", 1950, 1953),
        ):
            with self.subTest(variant=variant):
                self.assertTrue(
                    _overlaps_seed_war(seed_spans, [_war_tokens(variant)], low, high)
                )

    def test_seed_overlap_requires_year_intersection(self) -> None:
        seed_spans = _seed_war_token_spans(
            [{"event_type": "war", "name": "Vietnam War", "cluster_id": "vietnam_war", "year": 1955, "end_year": 1975}]
        )
        self.assertTrue(
            _overlaps_seed_war(seed_spans, [_war_tokens("Vietnam1965-75")], 1965, 1975)
        )
        self.assertFalse(
            _overlaps_seed_war(seed_spans, [_war_tokens("China-Vietnam1979")], 1979, 1979)
        )

    def test_short_or_unrelated_token_sets_do_not_match(self) -> None:
        self.assertFalse(
            _war_tokens_match(_war_tokens("SevenWeeks1866"), _war_tokens("Seven Years' War"))
        )
        self.assertFalse(_war_tokens_match(_war_tokens("II"), _war_tokens("Second World War")))

    def test_humanized_names_split_camel_case_and_digits(self) -> None:
        self.assertEqual(_humanize_war_name("GulfWar1991"), "Gulf War 1991")
        self.assertEqual(_humanize_war_name("1890CentralAmericanWar"), "1890 Central American War")
        self.assertEqual(_humanize_war_name("Korean_1950-53"), "Korean 1950-53")


class CowCodePolicyTests(unittest.TestCase):
    def test_cow_365_resolves_by_era_and_never_bridges_1918_1921(self) -> None:
        self.assertEqual(_cow_policy_seed_id("365", 1877, 1878), "russian_empire")
        self.assertEqual(_cow_policy_seed_id("365", 1939, 1940), "soviet_union")
        self.assertIsNone(_cow_policy_seed_id("365", 1918, 1921))
        self.assertIsNone(_cow_policy_seed_id("365", 1917, 1922))
        self.assertIsNone(_cow_policy_seed_id("220", 1991, 1991))

    def test_wave4_identity_windows_fail_closed_at_both_edges(self) -> None:
        cases = (
            ("100", 1863, 1885, "united_states_colombia"),
            ("670", 1932, 2026, "kingdom_saudi_arabia"),
            ("678", 1918, 1961, "mutawakkilite_kingdom_yemen"),
        )
        for code, low, high, entity_id in cases:
            with self.subTest(code=code):
                self.assertEqual(_cow_policy_seed_id(code, low, high), entity_id)
                self.assertIsNone(_cow_policy_seed_id(code, low - 1, low))
                self.assertIsNone(_cow_policy_seed_id(code, high, high + 1))


class CandidateSeedMappingTests(unittest.TestCase):
    SEED_BY_ID = {
        "kingdom_france": {
            "id": "kingdom_france",
            "name": "Kingdom of France",
            "aliases": ["France under the Ancien Regime"],
            "start_year": 987,
            "end_year": 1792,
        },
        "mongol_empire": {
            "id": "mongol_empire",
            "name": "Mongol Empire",
            "aliases": ["Great Mongol State"],
            "start_year": 1206,
            "end_year": 1294,
        },
    }

    def test_vassal_with_sovereign_codes_is_not_absorbed(self) -> None:
        # The Duchy of Burgundy carries the French crown's crosswalk codes in
        # Cliopatria but is a distinct polity that fought France.
        burgundy = {
            "canonical_name_candidate": "Duchy of Burgundy",
            "aliases": [],
            "wikipedia_titles": [],
            "seshat_ids": ["fr_valois_k_1"],
            "start_year": 1003,
            "end_year": 1481,
        }
        self.assertIsNone(_candidate_policy_seed(burgundy, self.SEED_BY_ID))

    def test_candidate_sharing_the_seed_name_is_absorbed(self) -> None:
        kingdom = {
            "canonical_name_candidate": "(Kingdom of France)",
            "aliases": [],
            "wikipedia_titles": ["Kingdom of France"],
            "seshat_ids": ["fr_valois_k_1"],
            "start_year": 990,
            "end_year": 1791,
        }
        self.assertEqual(_candidate_policy_seed(kingdom, self.SEED_BY_ID), "kingdom_france")

    def test_name_match_requires_era_overlap(self) -> None:
        # Bogd-Khanate-era Mongolia reuses the name "Great Mongol State" but is
        # seven centuries away from the seed Mongol Empire.
        modern_mongolia = {"start_year": 1912, "end_year": 1925}
        self.assertFalse(
            _candidate_overlaps_entity(modern_mongolia, self.SEED_BY_ID["mongol_empire"])
        )
        medieval = {"start_year": 1206, "end_year": 1294}
        self.assertTrue(
            _candidate_overlaps_entity(medieval, self.SEED_BY_ID["mongol_empire"])
        )
        open_ended = {"id": "x", "name": "X", "start_year": 1958, "end_year": None}
        self.assertTrue(
            _candidate_overlaps_entity({"start_year": 1990, "end_year": 2024}, open_ended)
        )


class IwdAggregationTests(unittest.TestCase):
    @staticmethod
    def _resolve_wave4_policy(name, cow_code, low_year, high_year):
        entity_id = _cow_policy_seed_id(str(cow_code), low_year, high_year)
        if entity_id:
            return entity_id, None
        return f"entity_{name.lower().replace(' ', '_')}", None

    def test_colombia_ecuador_parent_uses_the_1863_federal_identity(self) -> None:
        component = _component(
            "iwd-23", "15", "Ecuadorian-Colombian1863",
            "Ecuadorian-Colombian1863", 1863, 1863, "1",
            [("Colombia", "100")], [("Ecuador", "130")],
        )
        result = aggregate_iwd_parent_wars(
            [component], [], self._resolve_wave4_policy
        )
        self.assertEqual(result["parent_rejections"], {})
        self.assertEqual(len(result["events"]), 1)
        participants = result["events"][0]["participants"]
        winner = next(p for p in participants if "victory" in p["termination"])
        self.assertEqual(winner["entity_id"], "united_states_colombia")

    def test_saudi_yemen_parent_uses_both_curated_1934_identities(self) -> None:
        component = _component(
            "iwd-107", "48", "SaudiArabia-Yemen1934",
            "SaudiArabia-Yemen1934", 1934, 1934, "1",
            [("Saudi Arabia", "670")], [("Yemen", "678")],
        )
        result = aggregate_iwd_parent_wars(
            [component], [], self._resolve_wave4_policy
        )
        self.assertEqual(result["parent_rejections"], {})
        self.assertEqual(len(result["events"]), 1)
        participants = result["events"][0]["participants"]
        by_termination = {p["termination"]: p["entity_id"] for p in participants}
        self.assertEqual(
            by_termination,
            {
                "victory": "kingdom_saudi_arabia",
                "defeat": "mutawakkilite_kingdom_yemen",
            },
        )

    def _gulf_components(self, coalition_size=16):
        return [
            _component(
                f"iwd-{200 + index}",
                "82",
                "GulfWar1991",
                f"GulfWar_Ally{index}_1991",
                1991,
                1991,
                "1",
                [(f"Ally {index}", str(100 + index))],
                [("Iraq", "645")],
            )
            for index in range(coalition_size)
        ]

    def test_gulf_style_parent_produces_exactly_one_event(self) -> None:
        result = aggregate_iwd_parent_wars(self._gulf_components(), [], _resolve_all)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["parents_promoted"], 1)
        event = result["events"][0]
        iraq_rows = [p for p in event["participants"] if p["entity_id"] == "entity_iraq"]
        self.assertEqual(len(iraq_rows), 1)
        self.assertEqual(iraq_rows[0]["termination"], "defeat")
        winners = [p for p in event["participants"] if p["termination"] == "victory"]
        self.assertEqual(len(winners), 16)
        self.assertEqual(len(event["iwd_components"]), 16)
        self.assertTrue(all(c["status"] == "aggregated" for c in event["iwd_components"]))

    def test_component_dyads_never_become_separate_events(self) -> None:
        components = self._gulf_components() + [
            _component(
                "iwd-300", "83", "OtherWar1993", "OtherWar_A_1993",
                1993, 1993, "1", [("Armenia", "371")], [("Azerbaijan", "373")],
            )
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["parents_total"], 2)
        self.assertEqual(len(result["events"]), 2)
        parent_ids = [event["iwd_parent_war_id"] for event in result["events"]]
        self.assertEqual(sorted(parent_ids), ["82", "83"])

    def test_mixed_component_outcomes_are_not_forced_into_one_result(self) -> None:
        components = [
            _component("iwd-1", "58", "Sinai1956", "Sinai_A", 1956, 1956, "1",
                       [("Israel", "666")], [("Egypt", "651")]),
            _component("iwd-2", "58", "Sinai1956", "Sinai_B", 1956, 1956, "3",
                       [("United Kingdom", "200")], [("Egypt", "651")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["mixed_component_outcomes"], 1)

    def test_unanimous_draw_stays_a_draw(self) -> None:
        components = [
            _component("iwd-1", "54", "FirstKashmir1947-49", "Kashmir_A", 1947, 1949, "3",
                       [("India", "750")], [("Pakistan", "770")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        event = result["events"][0]
        self.assertEqual(event["decisiveness"], 0.44)
        self.assertTrue(all(p["termination"] == "draw" for p in event["participants"]))
        self.assertTrue(
            all(p["result_class"] == "stalemate_or_inconclusive" for p in event["participants"])
        )

    def test_entity_on_both_sides_quarantines_the_parent(self) -> None:
        # A vs B, B vs C, and C vs A form an odd cycle: C would need to stand on
        # both coalitions, and no explicit side-switch policy exists.
        components = [
            _component("iwd-1", "40", "LatvianWar1918-1920", "L_A", 1918, 1920, "1",
                       [("A", "1")], [("B", "2")]),
            _component("iwd-2", "40", "LatvianWar1918-1920", "L_B", 1918, 1920, "1",
                       [("B", "2")], [("C", "3")]),
            _component("iwd-3", "40", "LatvianWar1918-1920", "L_C", 1918, 1920, "1",
                       [("C", "3")], [("A", "1")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["inconsistent_coalition_sides"], 1)

    def test_disconnected_coalition_graph_quarantines_the_parent(self) -> None:
        components = [
            _component("iwd-1", "9", "SomeWar", "S_A", 1900, 1901, "1",
                       [("A", "1")], [("B", "2")]),
            _component("iwd-2", "9", "SomeWar", "S_B", 1900, 1901, "1",
                       [("C", "3")], [("D", "4")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["disconnected_coalition_graph"], 1)

    def test_unresolved_party_quarantines_the_parent(self) -> None:
        def resolver(name, cow_code, low_year, high_year):
            if name == "Unmappable":
                return None, None
            return _resolve_all(name, cow_code, low_year, high_year)

        components = [
            _component("iwd-1", "56", "Korean_1950-53", "K_A", 1950, 1953, "3",
                       [("Unmappable", "210")], [("North Korea", "731")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], resolver)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["unresolved_time_bounded_party"], 1)

    def test_two_labels_resolving_to_one_entity_quarantine_the_parent(self) -> None:
        def resolver(name, cow_code, low_year, high_year):
            return "entity_same", None

        components = [
            _component("iwd-1", "7", "SomeWar", "S_A", 1900, 1901, "1",
                       [("Alpha", "1")], [("Beta", "2")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], resolver)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["same_or_empty_opposing_side"], 1)

    def test_incomplete_reconstruction_lowers_confidence(self) -> None:
        complete = aggregate_iwd_parent_wars(self._gulf_components(3), [], _resolve_all)
        components = self._gulf_components(3) + [
            _component("iwd-299", "82", "GulfWar1991", "GulfWar_NoOutcome_1991",
                       1991, 1991, None, [("Ally X", "199")], [("Iraq", "645")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        event = result["events"][0]
        self.assertEqual(complete["events"][0]["confidence"], 0.76)
        self.assertEqual(event["confidence"], 0.73)
        self.assertLess(event["confidence"], complete["events"][0]["confidence"])
        self.assertEqual(result["components_aggregated"], 3)
        self.assertEqual(result["components_attached"], 4)
        statuses = {c["candidate_id"]: c["status"] for c in event["iwd_components"]}
        self.assertEqual(statuses["iwd-299"], "not_aggregated_missing_terminal_outcome")

    def test_component_missing_years_is_excluded_from_event_span(self) -> None:
        components = [
            _component("iwd-1", "82", "GulfWar1991", "GulfWar_A_1991", 1991, 1991, "1",
                       [("Ally A", "101")], [("Iraq", "645")]),
            _component("iwd-2", "82", "GulfWar1991", "GulfWar_NoYears_1991", None, None, "1",
                       [("Ally B", "102")], [("Iraq", "645")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        event = result["events"][0]
        self.assertEqual((event["year"], event["end_year"]), (1991, 1991))
        self.assertEqual(event["confidence"], 0.70)
        statuses = {c["candidate_id"]: c["status"] for c in event["iwd_components"]}
        self.assertEqual(statuses["iwd-2"], "not_aggregated_missing_year")
        rated_ids = {p["entity_id"] for p in event["participants"]}
        self.assertNotIn("entity_ally_b", rated_ids)

    def test_unknown_outcome_codes_are_never_coerced_into_results(self) -> None:
        # Code 0 means the war is ongoing in that source row; it is not a draw.
        components = [
            _component("iwd-1", "50", "SomeWar1940", "S_A", 1940, 1941, "0",
                       [("A", "1")], [("B", "2")]),
            _component("iwd-2", "50", "SomeWar1940", "S_B", 1940, 1941, "0",
                       [("C", "3")], [("B", "2")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["no_usable_component"], 1)

    def test_multi_party_component_sides_stay_allied(self) -> None:
        components = [
            _component("iwd-1", "94", "Malaysia_1963-1966", "M_A", 1963, 1966, "1",
                       [("Malaysia", "820"), ("United Kingdom", "200")],
                       [("Indonesia", "850")]),
            _component("iwd-2", "94", "Malaysia_1963-1966", "M_B", 1964, 1965, "1",
                       [("United Kingdom", "200")], [("Indonesia", "850")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(len(result["events"]), 1)
        by_entity = {p["entity_id"]: p for p in result["events"][0]["participants"]}
        self.assertEqual(by_entity["entity_malaysia"]["side"], by_entity["entity_united_kingdom"]["side"])
        self.assertEqual(by_entity["entity_malaysia"]["termination"], "victory")
        self.assertEqual(by_entity["entity_indonesia"]["termination"], "defeat")

    def test_allies_in_one_component_opposing_each_other_quarantine(self) -> None:
        components = [
            _component("iwd-1", "40", "SomeWar1918", "S_A", 1918, 1920, "1",
                       [("A", "1"), ("B", "2")], [("C", "3")]),
            _component("iwd-2", "40", "SomeWar1918", "S_B", 1918, 1920, "1",
                       [("A", "1")], [("B", "2")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["parent_rejections"]["inconsistent_coalition_sides"], 1)

    def test_outcome_orientation_follows_each_initiator_side(self) -> None:
        # X initiated and won one dyad; Y initiated and lost the other.
        # Both components agree that X's side won.
        components = [
            _component("iwd-1", "70", "SomeWar1973", "S_A", 1973, 1973, "1",
                       [("X", "1")], [("Y", "2")]),
            _component("iwd-2", "70", "SomeWar1973", "S_B", 1973, 1973, "2",
                       [("Y", "2")], [("X", "1")]),
        ]
        result = aggregate_iwd_parent_wars(components, [], _resolve_all)
        event = result["events"][0]
        by_entity = {p["entity_id"]: p for p in event["participants"]}
        self.assertEqual(by_entity["entity_x"]["termination"], "victory")
        self.assertEqual(by_entity["entity_y"]["termination"], "defeat")

    def test_seed_overlap_rejects_world_wars_before_rating(self) -> None:
        seed_spans = _seed_war_token_spans(
            [
                {"event_type": "war", "name": "First World War", "cluster_id": "first_world_war", "year": 1914, "end_year": 1918},
                {"event_type": "war", "name": "Second World War in Europe", "cluster_id": "second_world_war_europe", "year": 1939, "end_year": 1945},
            ]
        )
        components = [
            _component("iwd-1", "38", "WorldWarI", "WWI_Component", 1914, 1918, "2",
                       [("Germany", "255")], [("France", "220")]),
            _component("iwd-2", "53", "WorldWarII", "WWII_Component", 1939, 1945, "2",
                       [("Germany", "255")], [("Poland", "290")]),
        ]
        result = aggregate_iwd_parent_wars(components, seed_spans, _resolve_all)
        self.assertEqual(result["events"], [])
        self.assertEqual(
            result["parent_rejections"]["overlaps_curated_strategic_event"], 2
        )

    def test_existential_severity_is_never_inferred_from_outcome_codes(self) -> None:
        result = aggregate_iwd_parent_wars(self._gulf_components(), [], _resolve_all)
        for participant in result["events"][0]["participants"]:
            self.assertIn(
                participant["result_class"],
                {"limited_victory", "limited_defeat", "stalemate_or_inconclusive"},
            )
            self.assertIn(participant["termination"], {"victory", "defeat", "draw"})
            self.assertGreaterEqual(participant["outcome"]["sovereignty_survival"], 0.7)


@unittest.skipUnless(RELEASE_EVENTS.exists(), "release artifact not built")
class ReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.events = events
        cls.iwd_events = [e for e in events if str(e["id"]).startswith("iwd_war_")]

    def test_release_has_at_most_one_event_per_iwd_parent(self) -> None:
        self.assertTrue(self.iwd_events)
        parent_ids = [event["iwd_parent_war_id"] for event in self.iwd_events]
        self.assertEqual(len(parent_ids), len(set(parent_ids)))
        cluster_ids = [event["cluster_id"] for event in self.iwd_events]
        self.assertEqual(len(cluster_ids), len(set(cluster_ids)))

    def test_iraq_receives_one_gulf_war_update_not_sixteen(self) -> None:
        gulf_events = [e for e in self.iwd_events if "gulf" in str(e["name"]).lower()]
        self.assertEqual(len(gulf_events), 1)
        gulf = gulf_events[0]
        self.assertEqual(len(gulf["iwd_components"]), 17)
        losers = [p for p in gulf["participants"] if p["termination"] == "defeat"]
        self.assertEqual(len(losers), 1)
        iraq_id = losers[0]["entity_id"]
        iraq_rows = [p for p in gulf["participants"] if p["entity_id"] == iraq_id]
        self.assertEqual(len(iraq_rows), 1)
        iraq_gulf_events = [
            e
            for e in self.iwd_events
            if "gulf" in str(e["name"]).lower()
            and any(p["entity_id"] == iraq_id for p in e["participants"])
        ]
        self.assertEqual(len(iraq_gulf_events), 1)

    def test_world_wars_stay_with_the_curated_seed(self) -> None:
        self.assertFalse(
            [e for e in self.iwd_events if "world" in str(e["name"]).lower()]
        )
        for entity_id in ("nazi_germany", "german_empire"):
            with self.subTest(entity=entity_id):
                self.assertFalse(
                    [
                        e
                        for e in self.iwd_events
                        if any(p["entity_id"] == entity_id for p in e["participants"])
                    ]
                )
                strategic_wars = [
                    e
                    for e in self.events
                    if e.get("event_type") == "war"
                    and str(e.get("war_type")) == "world_war"
                    and any(p["entity_id"] == entity_id for p in e["participants"])
                ]
                self.assertEqual(len(strategic_wars), 1)

    def test_iwd_events_never_claim_existential_outcomes(self) -> None:
        for event in self.iwd_events:
            self.assertLessEqual(event["confidence"], 0.76)
            sides = {p["side"] for p in event["participants"]}
            self.assertGreaterEqual(len(sides), 2)
            for participant in event["participants"]:
                self.assertIn(
                    participant["result_class"],
                    {"limited_victory", "limited_defeat", "stalemate_or_inconclusive"},
                )
                self.assertIn(participant["termination"], {"victory", "defeat", "draw"})


@unittest.skipUnless(
    RELEASE_EVENTS.exists() and RELEASE_METADATA.exists() and REGISTRY.exists() and RESULTS.exists(),
    "release, registry, and dashboard artifacts not all built",
)
class ArtifactCountConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))

    def test_generated_counts_agree_across_artifacts(self) -> None:
        expected = self.metadata["record_counts_expected"]
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.events), expected["events"])
        self.assertEqual(len(self.registry["entities"]), expected["registry_polities"])
        self.assertEqual(coverage["registry_polities"], expected["registry_polities"])
        self.assertEqual(coverage["rated_events"], len(self.events))
        self.assertEqual(self.results["meta"]["rated_events"], len(self.events))
        self.assertEqual(self.results["meta"]["entities"], expected["entities"])
        results_coverage = self.results["registry"]["coverage"]
        for key in (
            "registry_polities",
            "rated_entities",
            "rated_events",
            "staged_source_records",
            "unresolved_event_candidates",
            "provisional_iwd_wars",
        ):
            self.assertEqual(results_coverage[key], coverage[key], key)

    def test_operational_document_count_pins_match_artifacts(self) -> None:
        coverage = self.registry["coverage"]
        values = {
            "registry": int(coverage["registry_polities"]),
            "rated_entities": int(coverage["rated_entities"]),
            "events": len(self.events),
            "staged": int(coverage["staged_source_records"]),
            "unresolved": int(coverage["unresolved_event_candidates"]),
        }
        documents = {
            PROJECT_ROOT / "README.md": ("registry", "rated_entities", "events"),
            PROJECT_ROOT / "docs" / "METHODOLOGY.md": tuple(values),
            PROJECT_ROOT / "docs" / "DATA_SOURCES.md": tuple(values),
            PROJECT_ROOT / "docs" / "REVIEW_WORKFLOW.md": tuple(values),
        }
        for path, keys in documents.items():
            text = path.read_text(encoding="utf-8")
            for key in keys:
                with self.subTest(document=path.name, count=key):
                    self.assertIn(f"{values[key]:,}", text)

    def test_promotion_accounting_matches_events(self) -> None:
        promotion = self.metadata["promotion"]
        iwd_events = [e for e in self.events if str(e["id"]).startswith("iwd_war_")]
        self.assertEqual(promotion["accepted_iwd_wars"], len(iwd_events))
        self.assertEqual(
            promotion["iwd_components_attached_to_rated_parents"],
            sum(len(e["iwd_components"]) for e in iwd_events),
        )
        self.assertEqual(
            promotion["iwd_components_aggregated"],
            sum(
                1
                for e in iwd_events
                for c in e["iwd_components"]
                if c["status"] == "aggregated"
            ),
        )
        rejected_parents = sum(promotion["iwd_rejections"].values())
        self.assertEqual(
            rejected_parents + len(iwd_events),
            promotion["iwd_parent_wars_total"],
        )


if __name__ == "__main__":
    unittest.main()
