import json
import unittest
from pathlib import Path

from military_elo.release import (
    HCED_FACTION_LABELS,
    HCED_LABEL_POLICIES,
    HCED_PENDING_SPLIT_LABELS,
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_WAR_TYPES,
    _label_policy_seed_id,
    normalize_label,
    promote_hced_label_rows,
    promote_ucdp_termination_episodes,
    resolve_hced_side_label,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"

MIGRATED_TO_POLICIES = {
    "carlists",
    "chinese communists",
    "irish rebels",
    "parliamentarians",
    "royalists",
    "spanish nationalists",
    "spanish republicans",
    "taiping",
}
NEWLY_BLOCKED = {
    "cristinos",
    "mexican rebels",
    "russian whites",
    "seminole indians",
    "vendeen rebels",
    "white russians",
}


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


def _ucdp_conflict_row(**overrides):
    raw = {
        "conflict_id": "202",
        "year": "1949",
        "c_epterm": "1",
        "c_outcome": "4",
        "c_ep_startyear": "1946",
        "c_ep_endyear": "1949",
        "c_epno": "1",
        "c_epid": "9001",
        "c_ependdate": "1949-10-01",
        "c_ependprec": "1",
        "side_a": "Government of China",
        "gwno_a": "710",
        "side_b": "PLA",
        "gwno_b": "",
        "side_a_2nd": "",
        "gwno_a_2nd": "",
        "side_b_2nd": "",
        "gwno_b_2nd": "",
        "intensity_level": "2",
        "incompatibility": "2",
        "type_of_conflict": "3",
        "territory_name": "",
    }
    raw.update(overrides)
    return {"raw": raw}


def _government_resolver(name, code, low_year, high_year):
    return f"gov_{str(code).strip() or 'unknown'}", None, "seed_label"


class ActorLabelPolicyTests(unittest.TestCase):
    def test_actor_labels_resolve_only_inside_attested_windows(self) -> None:
        cases = [
            ("royalists", 1645, "english_royalists", 1660),
            ("parliamentarians", 1645, "english_parliamentarians", 1660),
            ("taiping", 1856, "taiping_heavenly_kingdom", 1866),
            ("chinese communists", 1934, "chinese_communist_forces", 1950),
            ("carlists", 1836, "carlist_army_first_war", 1874),
            ("greek rebels", 1825, "greek_revolutionaries_1821", 1835),
            ("mexican liberals", 1859, "mexican_liberal_forces", 1865),
            ("mexican conservatives", 1859, "mexican_conservative_forces", 1865),
            ("spanish republicans", 1937, "second_spanish_republic", 1941),
            ("spanish nationalists", 1937, "spanish_nationalist_faction", 1941),
            ("viet cong", 1968, "viet_cong", 1955),
        ]
        for label, inside_year, entity_id, outside_year in cases:
            with self.subTest(label=label):
                self.assertEqual(
                    _label_policy_seed_id(label, inside_year, inside_year), entity_id
                )
                self.assertIsNone(
                    _label_policy_seed_id(label, outside_year, outside_year)
                )

    def test_cuban_risings_are_three_identities_with_no_namesake_bridge(self) -> None:
        self.assertEqual(
            _label_policy_seed_id("cuban rebels", 1873, 1873),
            "cuban_insurgent_army_1868",
        )
        self.assertEqual(
            _label_policy_seed_id("cuban rebels", 1896, 1896),
            "cuban_liberation_army_1895",
        )
        self.assertEqual(
            _label_policy_seed_id("cuban rebels", 1957, 1958), "cuban_26_july_movement"
        )
        for gap_year in (1885, 1902, 1953):
            with self.subTest(year=gap_year):
                self.assertIsNone(
                    _label_policy_seed_id("cuban rebels", gap_year, gap_year)
                )

    def test_blocklist_migration_kept_the_front_gate_complete(self) -> None:
        self.assertEqual(len(HCED_FACTION_LABELS), 79)
        for label in MIGRATED_TO_POLICIES:
            with self.subTest(label=label, direction="out"):
                self.assertNotIn(label, HCED_FACTION_LABELS)
                self.assertIn(label, HCED_LABEL_POLICIES)
        for label in NEWLY_BLOCKED:
            with self.subTest(label=label, direction="in"):
                self.assertIn(label, HCED_FACTION_LABELS)

    def test_front_gate_sets_are_mutually_exclusive(self) -> None:
        blocklist = set(HCED_FACTION_LABELS)
        policies = set(HCED_LABEL_POLICIES)
        pending = set(HCED_PENDING_SPLIT_LABELS)
        self.assertEqual(blocklist & policies, set())
        self.assertEqual(blocklist & pending, set())
        self.assertEqual(policies & pending, set())

    def test_front_gates_fire_before_alias_matching(self) -> None:
        context = _empty_tier_context()
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Vendeen Rebels", 1793, 1793, context
        )
        self.assertEqual(
            (entity_id, reason, tier), (None, "faction_label_not_a_polity", None)
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Switzerland", 1815, 1815, context
        )
        self.assertEqual(
            (entity_id, reason, tier), (None, "label_pending_identity_split", None)
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Royalists", 1645, 1645, context
        )
        self.assertEqual(
            (entity_id, reason, tier), ("english_royalists", None, "label_policy")
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Royalists", 1660, 1660, context
        )
        self.assertEqual(
            (entity_id, reason, tier), (None, "label_outside_policy_window", None)
        )

    def test_label_curated_exclusions_are_counted_before_every_other_gate(self) -> None:
        rows = [{"candidate_id": "hced-Ia Drang1965-1"}]
        result = promote_hced_label_rows(
            rows,
            curated_seed_keys=set(),
            promoted_event_keys=set(),
            resolve_code=lambda *args: (None, None, "no_unique_time_valid_polity"),
            resolve_side_label=lambda *args: (
                None,
                None,
                "no_unique_time_valid_label_match",
                None,
            ),
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["curated_row_exclusion"], 1)


class UcdpActorPolicyTests(unittest.TestCase):
    def test_actor_policies_are_conflict_scoped(self) -> None:
        self.assertEqual(
            set(UCDP_ACTOR_PARTY_POLICIES),
            {("202", "pla"), ("242", "m 26 7")},
        )

    def test_conflict_202_pla_resolves_through_the_actor_policy(self) -> None:
        result = promote_ucdp_termination_episodes(
            [_ucdp_conflict_row()], [], [], _government_resolver
        )
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        methods = {
            row["entity_id"]: row["method"] for row in event["ucdp_party_resolutions"]
        }
        self.assertEqual(methods["chinese_communist_forces"], "actor_party_policy")
        by_entity = {p["entity_id"]: p for p in event["participants"]}
        self.assertEqual(
            by_entity["chinese_communist_forces"]["termination"], "victory"
        )
        self.assertEqual(by_entity["gov_710"]["termination"], "defeat")
        self.assertEqual(event["war_type"], "civil_war")

    def test_actor_policy_is_side_symmetric(self) -> None:
        result = promote_ucdp_termination_episodes(
            [
                _ucdp_conflict_row(
                    side_a="PLA",
                    gwno_a="",
                    side_b="Government of China",
                    gwno_b="710",
                    c_outcome="3",
                )
            ],
            [],
            [],
            _government_resolver,
        )
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        by_entity = {p["entity_id"]: p for p in event["participants"]}
        self.assertEqual(
            by_entity["chinese_communist_forces"]["termination"], "victory"
        )
        self.assertEqual(by_entity["gov_710"]["termination"], "defeat")

    def test_mixed_government_and_actor_primary_side_is_rejected(self) -> None:
        result = promote_ucdp_termination_episodes(
            [
                _ucdp_conflict_row(
                    side_a="Government of Nationalist China, PLA",
                    gwno_a="713",
                )
            ],
            [],
            [],
            _government_resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["nonstate_primary_party"], 1)

    def test_actor_policy_secondary_is_provenance_only(self) -> None:
        result = promote_ucdp_termination_episodes(
            [
                _ucdp_conflict_row(
                    side_b="Government of Other China",
                    gwno_b="711",
                    side_b_2nd="PLA",
                    gwno_b_2nd="",
                )
            ],
            [],
            [],
            _government_resolver,
        )
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        rated = {p["entity_id"] for p in event["participants"]}
        self.assertNotIn("chinese_communist_forces", rated)
        self.assertEqual(
            event["ucdp_secondary_parties"]["side_b"][0]["resolved_entity_id"],
            "chinese_communist_forces",
        )

    def test_homonymous_pla_in_another_conflict_never_resolves(self) -> None:
        result = promote_ucdp_termination_episodes(
            [_ucdp_conflict_row(conflict_id="347")], [], [], _government_resolver
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["nonstate_primary_party"], 1)

    def test_actor_policy_window_is_the_attested_existence_bound(self) -> None:
        result = promote_ucdp_termination_episodes(
            [
                _ucdp_conflict_row(
                    c_ep_startyear="1950", c_ep_endyear="1950", year="1950"
                )
            ],
            [],
            [],
            _government_resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["unresolved_time_bounded_party"], 1)

    def test_war_type_mapping_is_exhaustive_and_never_coerces(self) -> None:
        self.assertEqual(
            UCDP_WAR_TYPES,
            {
                "1": "colonial_anti_colonial",
                "2": "interstate_limited",
                "3": "civil_war",
                "4": "insurgency_intervention",
            },
        )
        result = promote_ucdp_termination_episodes(
            [_ucdp_conflict_row(type_of_conflict="5")], [], [], _government_resolver
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["unmapped_type_of_conflict"], 1)


@unittest.skipUnless(RELEASE_EVENTS.exists(), "release artifact not built")
class ActorReleaseArtifactTests(unittest.TestCase):
    ALLOWED_TIERS = {
        "label_policy",
        "seed_alias",
        "crosswalk_observation",
        "cliopatria_alias",
        "cliopatria_alias_to_seed",
        "label_composite",
        "seshat_crosswalk",
        "wave6_pre1500_candidate_policy",
        "wave7_candidate_keyed_exact",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))

    def test_label_events_carry_an_auditable_resolution_tier(self) -> None:
        label_events = [
            e for e in self.events if str(e["id"]).startswith("hced_label_")
        ]
        self.assertEqual(len(label_events), 2_484)
        self.assertEqual(
            sum(e.get("identity_resolution") == "label" for e in label_events),
            2_479,
        )
        self.assertEqual(
            sum(
                e.get("identity_resolution") == "wave7_candidate_keyed_migration"
                for e in label_events
            ),
            5,
        )
        for event in label_events:
            tiers = event.get("side_identity_resolution")
            self.assertIsInstance(tiers, dict, event["id"])
            self.assertEqual(set(tiers), {"side_a", "side_b"}, event["id"])
            for tier in tiers.values():
                self.assertIn(tier, self.ALLOWED_TIERS, event["id"])

    def test_curated_actors_are_rated_and_distinct(self) -> None:
        rated = {p["entity_id"] for e in self.events for p in e["participants"]}
        for actor in (
            "english_royalists",
            "english_parliamentarians",
            "taiping_heavenly_kingdom",
            "chinese_communist_forces",
            "viet_cong",
        ):
            with self.subTest(actor=actor):
                self.assertIn(actor, rated)
        # The NVA/PAVN and the NLF stay separate rated identities.
        self.assertIn("north_vietnam", rated)

    def test_pavn_engagements_mislabelled_viet_cong_stay_staged(self) -> None:
        event_names_1965_1968 = {
            str(e["name"]).lower()
            for e in self.events
            if 1964 <= e["year"] <= 1968
            and any(p["entity_id"] == "viet_cong" for p in e["participants"])
        }
        for excluded in ("ia drang", "con thien", "hue"):
            with self.subTest(excluded=excluded):
                self.assertFalse(
                    any(excluded in name for name in event_names_1965_1968),
                    f"a curated-excluded PAVN engagement ({excluded}) was rated for viet_cong",
                )

    def test_ucdp_events_use_actor_policies_only_in_scope(self) -> None:
        actor_policy_events = set()
        for event in self.events:
            if not str(event["id"]).startswith("ucdp_term_"):
                continue
            for row in event.get("ucdp_party_resolutions", []):
                if row["method"] == "actor_party_policy":
                    actor_policy_events.add(str(event["id"]))
                    key = (str(event["ucdp_conflict_id"]), normalize_label(row["name"]))
                    self.assertIn(key, UCDP_ACTOR_PARTY_POLICIES, event["id"])
        self.assertEqual(
            actor_policy_events,
            {
                "ucdp_term_202_ep1_china_pla_conflict_termination_1946_1949",
                "ucdp_term_242_ep2_cuba_m_26_7_conflict_termination_1956_19",
            },
        )


if __name__ == "__main__":
    unittest.main()
