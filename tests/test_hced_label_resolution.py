import hashlib
import json
import unittest
from pathlib import Path

from military_elo.release import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_POLICIES,
    HCED_PENDING_SPLIT_LABELS,
    _canonicalize_superseded_identity,
    _candidate_entity_id,
    _event_key,
    _label_policy_seed_id,
    _normalized_event_name,
    _resolve_label_tiers,
    _split_composite_label,
    normalize_label,
    promote_hced_label_rows,
    resolve_hced_side_label,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"
RELEASE_ENTITIES = PROJECT_ROOT / "data" / "release" / "entities.json"
RELEASE_METADATA = PROJECT_ROOT / "data" / "release" / "metadata.json"
REGISTRY = PROJECT_ROOT / "data" / "catalog" / "registry.json"
SEED_ENTITIES = PROJECT_ROOT / "data" / "seed" / "entities.json"
CLIOPATRIA_CANDIDATES = (
    PROJECT_ROOT / "data" / "review" / "cliopatria-entity-candidates.jsonl"
)
WAVE4_PRE_LABEL_EVENT_IDS = (
    PROJECT_ROOT / "tests" / "fixtures" / "wave4_pre_label_event_ids.txt"
)

LABEL_TIERS = {
    "label_policy",
    "seed_alias",
    "crosswalk_observation",
    "cliopatria_alias",
    "cliopatria_alias_to_seed",
    "label_composite",
}
LABEL_CONFIDENCE_VALUES = {0.70, 0.67, 0.64, 0.61, 0.58}


def _seed(entity_id, name, start, end, aliases=()):
    return {
        "id": entity_id,
        "name": name,
        "aliases": list(aliases),
        "start_year": start,
        "end_year": end,
    }


def _polity(name, start, end, aliases=(), wikipedia=(), seshat_ids=(), wikidata_ids=()):
    return {
        "record_type": "POLITY",
        "canonical_name_candidate": name,
        "start_year": start,
        "end_year": end,
        "aliases": list(aliases),
        "wikipedia_titles": list(wikipedia),
        "seshat_ids": list(seshat_ids),
        "wikidata_ids": list(wikidata_ids),
    }


def _labels_of(*values):
    labels = {normalize_label(value) for value in values}
    labels.discard("")
    return labels


def _context(
    seeds=(),
    polities=(),
    label_observations=None,
    release_polities=(),
    entity_labels_extra=None,
):
    seeds = list(seeds)
    polities = list(polities)
    seed_by_id = {str(entity["id"]): entity for entity in seeds}
    seed_label_index = {}
    for entity in seeds:
        for label in [entity.get("name"), *entity.get("aliases", [])]:
            normalized = normalize_label(label)
            if normalized:
                seed_label_index.setdefault(normalized, set()).add(str(entity["id"]))
    polity_alias_index = {}
    for polity in polities:
        for label in {
            polity.get("canonical_name_candidate"),
            *polity.get("aliases", []),
            *polity.get("wikipedia_titles", []),
        }:
            normalized = normalize_label(label)
            if normalized:
                polity_alias_index.setdefault(normalized, []).append(polity)
    release_entities = {str(entity["id"]): entity for entity in seeds}
    for polity in release_polities:
        entity_id = _candidate_entity_id(polity)
        release_entities[entity_id] = {
            "id": entity_id,
            "start_year": int(polity["start_year"]),
            "end_year": int(polity["end_year"]),
        }
    entity_labels = {
        str(entity["id"]): _labels_of(entity.get("name"), *entity.get("aliases", []))
        for entity in seeds
    }
    for polity in (*polities, *release_polities):
        entity_labels.setdefault(_candidate_entity_id(polity), set()).update(
            _labels_of(
                polity.get("canonical_name_candidate"),
                *polity.get("aliases", []),
                *polity.get("wikipedia_titles", []),
            )
        )
    for entity_id, labels in (entity_labels_extra or {}).items():
        entity_labels.setdefault(entity_id, set()).update(labels)
    return {
        "seed_entities": seeds,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": dict(label_observations or {}),
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }


def _row(
    candidate_id,
    name,
    year,
    side1,
    side2,
    winner,
    loser,
    codes1=(),
    codes2=(),
    consulted=None,
    year_high=None,
):
    return {
        "candidate_id": candidate_id,
        "source_record_id": candidate_id,
        "name": name,
        "year_low": year,
        "year_best": year,
        "year_high": year if year_high is None else year_high,
        "side_1_raw": side1,
        "side_2_raw": side2,
        "winner_raw": winner,
        "loser_raw": loser,
        "seshat_side_1_candidates": list(codes1),
        "seshat_side_2_candidates": list(codes2),
        "consulted_source_raw": consulted,
        "war_names": [],
        "theatre_raw": None,
        "scale_raw": 2,
        "source_row": 1,
    }


def _resolve_code_stub(code, low_year, high_year):
    return f"seed_code_{code}", None, None


def _resolve_label_stub(label, low_year, high_year):
    normalized = normalize_label(label)
    if not normalized:
        return None, None, "blank_side_label", None
    return f"entity_{normalized.replace(' ', '_')}", None, None, "cliopatria_alias"


def _mapping_label_resolver(mapping):
    def resolve(label, low_year, high_year):
        del low_year, high_year
        entity_id = mapping.get(normalize_label(label))
        if entity_id is None:
            return None, None, "no_unique_time_valid_label_match", None
        return entity_id, None, None, "cliopatria_alias"

    return resolve


class CompositeLabelSplitterTests(unittest.TestCase):
    def test_explicit_delimiters_and_oxford_comma_split(self) -> None:
        self.assertEqual(_split_composite_label("Aland, Bland"), ["Aland", "Bland"])
        self.assertEqual(_split_composite_label("Aland; Bland"), ["Aland", "Bland"])
        self.assertEqual(_split_composite_label("Aland & Bland"), ["Aland", "Bland"])
        self.assertEqual(
            _split_composite_label("Aland, Bland, and Cland"),
            ["Aland", "Bland", "Cland"],
        )

    def test_single_names_and_internal_and_are_never_split(self) -> None:
        for label in (
            "Aland",
            "Bosnia and Herzegovina",
            "Trinidad and Tobago",
            "",
            None,
        ):
            with self.subTest(label=label):
                self.assertEqual(_split_composite_label(label), [])


class SupersededIdentityCanonicalizationTests(unittest.TestCase):
    def test_unmapped_identity_is_an_exact_noop(self) -> None:
        polity = {"canonical_name_candidate": "Aland"}
        self.assertEqual(
            _canonicalize_superseded_identity("raw_aland", polity, 1900, 1900, {}, {}),
            ("raw_aland", polity),
        )

    def test_singleton_remap_selects_target_and_drops_raw_polity(self) -> None:
        target = {"id": "canonical", "start_year": 1854, "end_year": 1902}
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw",
                {"canonical_name_candidate": "Raw"},
                1899,
                1899,
                {"raw": ("canonical",)},
                {"canonical": target},
            ),
            ("canonical", None),
        )

    def test_split_supersession_selects_exactly_one_full_interval_target(self) -> None:
        targets = {
            "pre": {"id": "pre", "start_year": 1270, "end_year": 1854},
            "post": {"id": "post", "start_year": 1855, "end_year": 1936},
        }
        supersessions = {"raw": ("pre", "post")}
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw", None, 1854, 1854, supersessions, targets
            ),
            ("pre", None),
        )
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw", None, 1855, 1855, supersessions, targets
            ),
            ("post", None),
        )
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw", None, 1854, 1855, supersessions, targets
            ),
            (None, None),
        )

    def test_missing_or_ambiguous_target_fails_closed(self) -> None:
        overlapping = {
            "first": {"id": "first", "start_year": 1800, "end_year": 1900},
            "second": {"id": "second", "start_year": 1850, "end_year": 1950},
        }
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw", None, 1870, 1870, {"raw": ("missing",)}, overlapping
            ),
            (None, None),
        )
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw",
                None,
                1870,
                1870,
                {"raw": ("first", "second")},
                overlapping,
            ),
            (None, None),
        )
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw", None, 1870, 1870, {"raw": ()}, overlapping
            ),
            (None, None),
        )
        self.assertEqual(
            _canonicalize_superseded_identity(
                "raw",
                None,
                1870,
                1870,
                {"raw": ("intermediate",), "intermediate": ("first",)},
                {
                    **overlapping,
                    "intermediate": {
                        "id": "intermediate",
                        "start_year": 1800,
                        "end_year": 1900,
                    },
                },
            ),
            (None, None),
        )


class CompositeLabelPromotionTests(unittest.TestCase):
    def test_fully_resolved_post1500_composite_promotes_one_coalition(self) -> None:
        resolver = _mapping_label_resolver(
            {"aland": "a", "bland": "b", "cland": "c", "dland": "d"}
        )
        raw_coalition = "Aland, Bland & Cland"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-composite",
                    "Battle of Coalition",
                    1900,
                    raw_coalition,
                    "Dland",
                    raw_coalition,
                    "Dland",
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            resolver,
        )
        self.assertEqual(result["accepted"], 1)
        event = result["events"][0]
        self.assertEqual(
            event["side_identity_resolution"],
            {"side_a": "label_composite", "side_b": "cliopatria_alias"},
        )
        side_a = [
            participant
            for participant in event["participants"]
            if participant["side"] == "side_a"
        ]
        self.assertEqual(
            {participant["entity_id"] for participant in side_a}, {"a", "b", "c"}
        )
        self.assertTrue(
            all(
                participant["role"] == "major_ally"
                and participant["contribution"] == 0.3333
                for participant in side_a
            )
        )

    def test_one_unresolved_member_keeps_the_row_staged(self) -> None:
        resolver = _mapping_label_resolver({"aland": "a", "dland": "d"})
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-partial-composite",
                    "Battle of Partial Coalition",
                    1900,
                    "Aland, Bland",
                    "Dland",
                    "Aland, Bland",
                    "Dland",
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            resolver,
        )
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(result["rejections"]["no_unique_time_valid_label_match"], 1)

    def test_pre1500_and_cross_boundary_composites_never_resolve_members(self) -> None:
        for low_year, high_year in ((1499, 1499), (1499, 1500)):
            seen: list[str] = []

            def resolver(label, member_low, member_high):
                del member_low, member_high
                seen.append(str(label))
                return _mapping_label_resolver(
                    {"aland": "a", "bland": "b", "dland": "d"}
                )(label, low_year, high_year)

            raw_coalition = "Aland, Bland"
            result = promote_hced_label_rows(
                [
                    _row(
                        f"hced-frozen-{low_year}-{high_year}",
                        "Battle of Frozen Coalition",
                        low_year,
                        raw_coalition,
                        "Dland",
                        raw_coalition,
                        "Dland",
                        year_high=high_year,
                    )
                ],
                set(),
                set(),
                _resolve_code_stub,
                resolver,
            )
            with self.subTest(low_year=low_year, high_year=high_year):
                self.assertEqual(result["accepted"], 0)
                self.assertEqual(seen, [raw_coalition])

    def test_1500_boundary_is_included(self) -> None:
        raw_coalition = "Aland, Bland"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-boundary-composite",
                    "Battle of Boundary Coalition",
                    1500,
                    raw_coalition,
                    "Dland",
                    raw_coalition,
                    "Dland",
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            _mapping_label_resolver({"aland": "a", "bland": "b", "dland": "d"}),
        )
        self.assertEqual(result["accepted"], 1)

    def test_members_never_use_candidate_keyed_resolver(self) -> None:
        generic = _mapping_label_resolver({"aland": "a"})
        candidate_calls: list[str] = []

        def candidate_resolver(candidate, label, low_year, high_year):
            del candidate
            candidate_calls.append(str(label))
            if normalize_label(label) == "forbidden":
                return "candidate_only", None, None, "candidate_policy"
            return generic(label, low_year, high_year)

        raw_coalition = "Aland, Forbidden"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-candidate-guard",
                    "Battle of Candidate Guard",
                    1900,
                    raw_coalition,
                    "Dland",
                    raw_coalition,
                    "Dland",
                    codes2=("d",),
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            generic,
            resolve_candidate_side_label=candidate_resolver,
        )
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(candidate_calls, [raw_coalition])

    def test_exact_member_resolver_is_separate_from_candidate_resolver(self) -> None:
        generic = _mapping_label_resolver({"aland": "a"})
        candidate_calls: list[str] = []
        member_calls: list[str] = []

        def candidate_resolver(candidate, label, low_year, high_year):
            del candidate
            candidate_calls.append(str(label))
            return generic(label, low_year, high_year)

        def member_resolver(candidate, label, low_year, high_year):
            del candidate
            member_calls.append(str(label))
            if normalize_label(label) == "bland":
                return "candidate_b", None, None, "candidate_reviewed_label_binding"
            return generic(label, low_year, high_year)

        raw_coalition = "Aland, Bland"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-reviewed-member",
                    "Battle of Reviewed Coalition",
                    1900,
                    raw_coalition,
                    "Dland",
                    raw_coalition,
                    "Dland",
                    codes2=("d",),
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            generic,
            resolve_candidate_side_label=candidate_resolver,
            resolve_candidate_composite_member=member_resolver,
        )
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(candidate_calls, [raw_coalition])
        self.assertEqual(member_calls, ["Aland", "Bland"])
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in result["events"][0]["participants"]
                if participant["side"] == "side_a"
            },
            {"a", "candidate_b"},
        )

    def test_composite_member_supersession_uses_canonical_participant(self) -> None:
        old_orange = "clio_q218023_1856_cfb4e08e"
        raw_orange = {"canonical_name_candidate": "Free Orange State"}

        def resolver(label, low_year, high_year):
            del low_year, high_year
            matches = {
                "transvaal": ("transvaal", None),
                "orange free state": (old_orange, raw_orange),
                "united kingdom": ("united_kingdom", None),
            }
            match = matches.get(normalize_label(label))
            if match is None:
                return None, None, "no_unique_time_valid_label_match", None
            return match[0], match[1], None, "cliopatria_alias"

        supersessions = {old_orange: ("orange_free_state_1854",)}
        target_entities = {
            "orange_free_state_1854": {
                "id": "orange_free_state_1854",
                "start_year": 1854,
                "end_year": 1902,
            }
        }

        def canonicalize(entity_id, polity, low_year, high_year):
            return _canonicalize_superseded_identity(
                entity_id,
                polity,
                low_year,
                high_year,
                supersessions,
                target_entities,
            )

        raw_coalition = "Transvaal, Orange Free State"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-boer-composite",
                    "Battle of Boer Coalition",
                    1899,
                    raw_coalition,
                    "United Kingdom",
                    raw_coalition,
                    "United Kingdom",
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            resolver,
            canonicalize_composite_identity=canonicalize,
        )
        self.assertEqual(result["accepted"], 1)
        participant_ids = {
            participant["entity_id"]
            for participant in result["events"][0]["participants"]
        }
        self.assertIn("orange_free_state_1854", participant_ids)
        self.assertNotIn(old_orange, participant_ids)
        self.assertNotIn(old_orange, result["resolved_polities"])

    def test_distinct_raw_members_that_canonicalize_together_are_rejected(self) -> None:
        resolver = _mapping_label_resolver(
            {"aland": "raw_a", "bland": "raw_b", "dland": "d"}
        )
        target_entities = {
            "canonical": {"id": "canonical", "start_year": 1800, "end_year": 2000}
        }

        def canonicalize(entity_id, polity, low_year, high_year):
            return _canonicalize_superseded_identity(
                entity_id,
                polity,
                low_year,
                high_year,
                {"raw_a": ("canonical",), "raw_b": ("canonical",)},
                target_entities,
            )

        raw_coalition = "Aland, Bland"
        result = promote_hced_label_rows(
            [
                _row(
                    "hced-canonical-duplicate",
                    "Battle of Canonical Duplicate",
                    1900,
                    raw_coalition,
                    "Dland",
                    raw_coalition,
                    "Dland",
                )
            ],
            set(),
            set(),
            _resolve_code_stub,
            resolver,
            canonicalize_composite_identity=canonicalize,
        )
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(result["rejections"]["no_unique_time_valid_label_match"], 1)


class LabelPolicyTests(unittest.TestCase):
    def test_france_label_resolves_by_era_and_never_bridges_1793_or_1816(self) -> None:
        self.assertEqual(_label_policy_seed_id("france", 1650, 1650), "kingdom_france")
        self.assertEqual(
            _label_policy_seed_id("france", 1795, 1795), "french_first_republic"
        )
        self.assertEqual(
            _label_policy_seed_id("france", 1809, 1809), "first_french_empire"
        )
        self.assertEqual(
            _label_policy_seed_id("france", 1860, 1860), "second_french_empire"
        )
        self.assertEqual(
            _label_policy_seed_id("france", 1915, 1915), "french_third_republic"
        )
        self.assertEqual(
            _label_policy_seed_id("france", 1960, 1960), "french_fifth_republic"
        )
        # 1816-1851 (Restoration through Second Republic) and 1941-1957 are
        # deliberate gaps; 1870 sits inside BOTH the Second Empire and Third
        # Republic windows, so the boundary year is ambiguous and fails.
        for year in (1830, 1870, 1945):
            with self.subTest(year=year):
                self.assertIsNone(_label_policy_seed_id("france", year, year))
        # A span crossing a policy gap never resolves to either neighbor.
        self.assertIsNone(_label_policy_seed_id("france", 1790, 1810))

    def test_russia_label_splits_tsardom_empire_and_soviet_eras(self) -> None:
        self.assertEqual(
            _label_policy_seed_id("russia", 1700, 1700),
            "clio_ru_moskva_rurik_dyn_1547_93deb0e2",
        )
        self.assertEqual(_label_policy_seed_id("russia", 1877, 1878), "russian_empire")
        self.assertEqual(_label_policy_seed_id("russia", 1939, 1940), "soviet_union")
        self.assertIsNone(_label_policy_seed_id("russia", 1918, 1921))
        self.assertIsNone(_label_policy_seed_id("russia", 1917, 1922))
        self.assertIsNone(_label_policy_seed_id("russia", 1992, 1992))

    def test_rome_and_byzantium_split_at_395_with_boundary_ambiguity_failing(
        self,
    ) -> None:
        self.assertEqual(_label_policy_seed_id("rome", -100, -100), "roman_republic")
        self.assertEqual(_label_policy_seed_id("rome", 100, 100), "roman_empire")
        self.assertEqual(_label_policy_seed_id("romans", 100, 100), "roman_empire")
        # -27 sits inside both declared windows: ambiguity always fails.
        self.assertIsNone(_label_policy_seed_id("rome", -27, -27))
        self.assertEqual(
            _label_policy_seed_id("byzantium", 600, 600), "byzantine_empire"
        )
        self.assertIsNone(_label_policy_seed_id("rome", 600, 600))
        self.assertIsNone(_label_policy_seed_id("byzantium", 300, 300))

    def test_persia_interregna_stay_staged(self) -> None:
        self.assertEqual(
            _label_policy_seed_id("persia", -500, -500), "achaemenid_empire"
        )
        self.assertEqual(_label_policy_seed_id("persia", 400, 400), "sasanian_empire")
        self.assertEqual(_label_policy_seed_id("persia", 1600, 1600), "safavid_empire")
        self.assertIsNone(_label_policy_seed_id("persia", 100, 100))
        self.assertIsNone(_label_policy_seed_id("persia", 1750, 1750))

    def test_policy_labels_resolve_with_the_label_policy_tier(self) -> None:
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "France", 1650, 1650, _context()
        )
        self.assertEqual(entity_id, "kingdom_france")
        self.assertIsNone(polity)
        self.assertIsNone(reason)
        self.assertEqual(tier, "label_policy")

    def test_policy_labels_never_fall_through_to_alias_matching(self) -> None:
        # A Cliopatria candidate carrying the alias "France" and covering 1830
        # must not rescue a label whose policy deliberately omits 1816-1957.
        context = _context(
            polities=[_polity("July Monarchy", 1830, 1848, aliases=("France",))]
        )
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "France", 1830, 1830, context
        )
        self.assertIsNone(entity_id)
        self.assertIsNone(polity)
        self.assertEqual(reason, "label_outside_policy_window")
        self.assertIsNone(tier)


class FactionLabelTests(unittest.TestCase):
    def test_faction_labels_never_resolve_even_with_a_colliding_polity_alias(
        self,
    ) -> None:
        context = _context(
            polities=[
                _polity("Mujahideen", 1987, 2024, aliases=("Mujahideen",)),
                # The Cliopatria polity file carries the party record itself.
                _polity("Kuomintang", 1917, 1929, wikidata_ids=("Q31113",)),
            ]
        )
        for label, year in (("Mujahideen", 1990), ("Kuomintang", 1925)):
            with self.subTest(label=label):
                entity_id, polity, reason, tier = resolve_hced_side_label(
                    label, year, year, context
                )
                self.assertIsNone(entity_id)
                self.assertEqual(reason, "faction_label_not_a_polity")
                self.assertIsNone(tier)

    def test_collective_peoples_labels_stay_staged(self) -> None:
        for label in ("vikings", "tatars", "saxons", "huns", "mongols"):
            with self.subTest(label=label):
                self.assertIn(label, HCED_FACTION_LABELS)
                entity_id, _, reason, _ = resolve_hced_side_label(
                    label, 1000, 1000, _context()
                )
                self.assertIsNone(entity_id)
                self.assertEqual(reason, "faction_label_not_a_polity")

    def test_confederate_states_is_a_time_bounded_polity_alias(self) -> None:
        self.assertNotIn("confederate states of america", HCED_FACTION_LABELS)
        self.assertIn("confederates", HCED_FACTION_LABELS)
        csa = _polity(
            "Confederate States of America", 1861, 1865, wikidata_ids=("Q81931",)
        )
        context = _context(polities=[csa])
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "Confederate States of America", 1861, 1865, context
        )
        self.assertEqual(entity_id, "clio_q81931_1861_f3bc20bd")
        self.assertEqual(entity_id, _candidate_entity_id(csa))
        self.assertIs(polity, csa)
        self.assertIsNone(reason)
        self.assertEqual(tier, "cliopatria_alias")

        for year in (1860, 1866):
            with self.subTest(year=year):
                entity_id, polity, reason, tier = resolve_hced_side_label(
                    "Confederate States of America", year, year, context
                )
                self.assertIsNone(entity_id)
                self.assertIsNone(polity)
                self.assertEqual(reason, "no_unique_time_valid_label_match")
                self.assertIsNone(tier)


class PendingSplitTests(unittest.TestCase):
    def test_pending_split_labels_never_resolve_even_with_a_unique_time_valid_candidate(
        self,
    ) -> None:
        context = _context(
            polities=[_polity("Swiss Confederation", 1294, 2024, wikidata_ids=("Q39",))]
        )
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "Swiss Confederation", 1700, 1700, context
        )
        self.assertIsNone(entity_id)
        self.assertIsNone(polity)
        self.assertEqual(reason, "label_pending_identity_split")
        self.assertIsNone(tier)

    def test_pending_split_is_checked_before_policy_and_alias_tiers(self) -> None:
        # No pending-split label may double as a policy label: the pending
        # gate is authoritative and runs first.
        self.assertTrue(HCED_PENDING_SPLIT_LABELS.isdisjoint(HCED_LABEL_POLICIES))
        # Even a covering curated seed alias cannot outrank the pending gate.
        context = _context(
            seeds=[_seed("modern_switzerland", "Switzerland", 1523, None)],
            polities=[_polity("Swiss Confederation", 1294, 2024)],
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Switzerland", 1700, 1700, context
        )
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "label_pending_identity_split")
        self.assertIsNone(tier)


class LabelResolutionTierTests(unittest.TestCase):
    def test_bare_mexico_uses_real_seed_and_cliopatria_boundaries(self) -> None:
        seeds = json.loads(SEED_ENTITIES.read_text(encoding="utf-8"))
        polities = []
        for line in CLIOPATRIA_CANDIDATES.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("record_type") == "POLITY":
                polities.append(row)
        context = _context(seeds=seeds, polities=polities)
        expected = {
            1863: ("mexican_republic", None, "seed_alias"),
            1864: (None, "no_unique_time_valid_label_match", None),
            1867: (None, "no_unique_time_valid_label_match", None),
            1868: (
                "clio_mx_mexico_1_1868_ffbcfbae",
                None,
                "cliopatria_alias",
            ),
            2024: (
                "clio_mx_mexico_1_1868_ffbcfbae",
                None,
                "cliopatria_alias",
            ),
            2025: (None, "no_unique_time_valid_label_match", None),
        }
        for year, resolution in expected.items():
            with self.subTest(year=year):
                entity_id, _polity, reason, tier = resolve_hced_side_label(
                    "Mexico", year, year, context
                )
                self.assertEqual((entity_id, reason, tier), resolution)

    def test_seed_alias_requires_uniqueness_and_full_interval_coverage(self) -> None:
        wessex = _seed("wessex", "Kingdom of Wessex", 519, 927, aliases=("Wessex",))
        open_ended = _seed("modernland", "Modernland", 1948, None)
        context = _context(seeds=[wessex, open_ended])
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Wessex", 800, 800, context
        )
        self.assertEqual((entity_id, reason, tier), ("wessex", None, "seed_alias"))
        # Open-ended seeds cover any later interval.
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Modernland", 2000, 2000, context
        )
        self.assertEqual((entity_id, tier), ("modernland", "seed_alias"))
        # Partial interval coverage fails.
        entity_id, _, reason, _ = resolve_hced_side_label("Wessex", 900, 950, context)
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")
        # Two seeds sharing one alias are ambiguous and fail.
        ambiguous = _context(
            seeds=[
                _seed("mercia_a", "North Mercia", 600, 900, aliases=("Mercia",)),
                _seed("mercia_b", "South Mercia", 600, 900, aliases=("Mercia",)),
            ]
        )
        entity_id, _, reason, _ = resolve_hced_side_label("Mercia", 700, 700, ambiguous)
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")

    def test_observation_tier_requires_release_entity_coverage_and_name_coherence(
        self,
    ) -> None:
        coherent = _polity("Fooland Kingdom", 1400, 1600, aliases=("Fooland",))
        coherent_id = _candidate_entity_id(coherent)
        context = _context(
            release_polities=[coherent],
            label_observations={"fooland": [(1450, 1450, coherent_id)]},
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Fooland", 1450, 1450, context
        )
        self.assertEqual(entity_id, coherent_id)
        self.assertIsNone(reason)
        self.assertEqual(tier, "crosswalk_observation")
        # The same observation fails once the interval leaves the entity span.
        entity_id, _, reason, _ = resolve_hced_side_label(
            "Fooland", 1700, 1700, context
        )
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")
        # A mis-crosswalked observation (label not among the entity's own
        # labels) is filtered by the coherence guard.
        incoherent = _polity("Barland Kingdom", 1400, 1600, aliases=("Barland",))
        incoherent_context = _context(
            release_polities=[incoherent],
            label_observations={
                "fooland": [(1450, 1450, _candidate_entity_id(incoherent))]
            },
        )
        entity_id, _, reason, _ = resolve_hced_side_label(
            "Fooland", 1450, 1450, incoherent_context
        )
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")

    def test_incoherent_observation_falls_through_to_alias_tier_not_failure(
        self,
    ) -> None:
        mispaired = _polity("Barland Kingdom", 1400, 1600, aliases=("Barland",))
        aliased = _polity("Fooland Kingdom", 1400, 1600, aliases=("Fooland",))
        context = _context(
            polities=[aliased],
            release_polities=[mispaired],
            label_observations={
                "fooland": [(1450, 1450, _candidate_entity_id(mispaired))]
            },
        )
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "Fooland", 1450, 1450, context
        )
        self.assertEqual(entity_id, _candidate_entity_id(aliased))
        self.assertIs(polity, aliased)
        self.assertIsNone(reason)
        self.assertEqual(tier, "cliopatria_alias")

    def test_iwd_wrapper_keeps_observation_tier_unguarded(self) -> None:
        # The IWD path passes require_observation_coherence=False, pinning the
        # committed 44-war behavior: the same mis-paired observation that the
        # HCED pass filters still resolves for IWD.
        mispaired = _polity("Barland Kingdom", 1400, 1600, aliases=("Barland",))
        mispaired_id = _candidate_entity_id(mispaired)
        context = _context(
            release_polities=[mispaired],
            label_observations={"fooland": [(1450, 1450, mispaired_id)]},
        )
        entity_id, polity, tier = _resolve_label_tiers(
            "fooland", 1450, 1450, context, require_observation_coherence=False
        )
        self.assertEqual(entity_id, mispaired_id)
        self.assertIsNone(polity)
        self.assertEqual(tier, "crosswalk_observation")
        guarded_id, _, guarded_tier = _resolve_label_tiers(
            "fooland", 1450, 1450, context, require_observation_coherence=True
        )
        self.assertIsNone(guarded_id)
        self.assertIsNone(guarded_tier)

    def test_two_candidates_sharing_an_alias_quarantine_the_side(self) -> None:
        context = _context(
            polities=[
                _polity("North Borduria", 1400, 1600, aliases=("Borduria",)),
                _polity("South Borduria", 1400, 1600, aliases=("Borduria",)),
            ]
        )
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Borduria", 1500, 1500, context
        )
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")
        self.assertIsNone(tier)

    def test_seed_mapped_candidate_must_cover_the_span_or_fail_outright(self) -> None:
        seed = _seed("kingdom_france", "Kingdom of France", 987, 1792)
        candidate = _polity(
            "Kingdom of France", 990, 1800, aliases=("Royaume de France",)
        )
        context = _context(seeds=[seed], polities=[candidate])
        # Inside the seed interval the candidate resolves to the seed identity.
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "Royaume de France", 1700, 1700, context
        )
        self.assertEqual(entity_id, "kingdom_france")
        self.assertIsNone(polity)
        self.assertIsNone(reason)
        self.assertEqual(tier, "cliopatria_alias_to_seed")
        # Outside the seed interval the resolution fails outright instead of
        # falling back to a parallel candidate rating identity.
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Royaume de France", 1795, 1795, context
        )
        self.assertIsNone(entity_id)
        self.assertEqual(reason, "no_unique_time_valid_label_match")
        self.assertIsNone(tier)

    def test_name_match_alone_never_bridges_eras(self) -> None:
        # Bogd-Khanate-era Mongolia reuses the seed alias "Great Mongol State"
        # but is seven centuries away from the seed Mongol Empire: it keeps its
        # own candidate identity instead of inheriting the seed rating line.
        seed = _seed(
            "mongol_empire",
            "Mongol Empire",
            1206,
            1294,
            aliases=("Great Mongol State",),
        )
        modern = _polity("Great Mongol State", 1912, 1925, aliases=("Bogd Khanate",))
        context = _context(seeds=[seed], polities=[modern])
        entity_id, polity, reason, tier = resolve_hced_side_label(
            "Great Mongol State", 1913, 1920, context
        )
        self.assertEqual(entity_id, _candidate_entity_id(modern))
        self.assertNotEqual(entity_id, "mongol_empire")
        self.assertIs(polity, modern)
        self.assertIsNone(reason)
        self.assertEqual(tier, "cliopatria_alias")


class TwoPassStructureTests(unittest.TestCase):
    def test_coded_rows_promote_identically_with_and_without_label_pass(self) -> None:
        # The label pass must not mutate any pass-1 state it is handed: the
        # curated-seed key set and the pass-1 promoted-event key set stay
        # untouched even when the pass accepts new events.
        curated = {_event_key("Battle of Curated", 1800)}
        promoted = {_event_key("Battle of Promoted", 1801)}
        curated_before, promoted_before = set(curated), set(promoted)
        rows = [
            _row("hced-1", "Battle of New", 1802, "Aland", "Bland", "Aland", "Bland")
        ]
        result = promote_hced_label_rows(
            rows, curated, promoted, _resolve_code_stub, _resolve_label_stub
        )
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["rows_total"], 1)
        self.assertEqual(curated, curated_before)
        self.assertEqual(promoted, promoted_before)

    def test_label_resolved_rows_never_feed_label_observations(self) -> None:
        # Row A's label resolves via alias at 1905 (only one covering
        # candidate). Row B's identical label at 1915 is ambiguous at the
        # alias tier and would resolve ONLY if row A's resolution had been
        # written back into label_observations; it must stay staged.
        early = _polity("Aland Kingdom", 1890, 1920, aliases=("Aland",))
        late = _polity("New Aland", 1912, 1930, aliases=("Aland",))
        other = _polity("Bland Kingdom", 1890, 1930, aliases=("Bland",))
        context = _context(polities=[early, late, other], release_polities=[early])
        self.assertEqual(context["label_observations"], {})

        rows = [
            _row("hced-a", "Battle of Alpha", 1905, "Aland", "Bland", "Aland", "Bland"),
            _row("hced-b", "Battle of Beta", 1915, "Aland", "Bland", "Aland", "Bland"),
        ]
        result = promote_hced_label_rows(
            rows,
            set(),
            set(),
            _resolve_code_stub,
            lambda label, low, high: resolve_hced_side_label(label, low, high, context),
        )
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["events"][0]["hced_candidate_id"], "hced-a")
        self.assertEqual(result["rejections"]["no_unique_time_valid_label_match"], 1)
        self.assertEqual(context["label_observations"], {})
        # Counterfactual: had the pass fed observations, row B would resolve.
        context["label_observations"]["aland"] = [
            (1905, 1905, _candidate_entity_id(early))
        ]
        entity_id, _, reason, tier = resolve_hced_side_label(
            "Aland", 1915, 1915, context
        )
        self.assertEqual(entity_id, _candidate_entity_id(early))
        self.assertIsNone(reason)
        self.assertEqual(tier, "crosswalk_observation")

    def test_mixed_row_uses_code_path_for_the_coded_side(self) -> None:
        seen_codes = []

        def resolve_code(code, low_year, high_year):
            seen_codes.append((code, low_year, high_year))
            return f"seed_code_{code}", None, None

        rows = [
            _row(
                "hced-mixed",
                "Battle of Mixed",
                1650,
                "Fooland",
                "Barland",
                "Fooland",
                "Barland",
                codes1=("fr_1",),
            )
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), resolve_code, _resolve_label_stub
        )
        self.assertEqual(seen_codes, [("fr_1", 1650, 1650)])
        event = result["events"][0]
        self.assertEqual(
            event["side_identity_resolution"],
            {"side_a": "seshat_crosswalk", "side_b": "cliopatria_alias"},
        )
        sides = {
            p["side"]
            for p in event["participants"]
            if p["entity_id"] == "seed_code_fr_1"
        }
        self.assertEqual(sides, {"side_a"})

    def test_unknown_winner_is_not_a_draw(self) -> None:
        rows = [
            _row("hced-blank", "Battle of Blank", 1700, "Aland", "Bland", None, None)
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), _resolve_code_stub, _resolve_label_stub
        )
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(result["rejections"]["label_outcome_not_aligned"], 1)

    def test_blank_winner_never_matches_a_blank_side_label_vacuously(self) -> None:
        # A coded side with a blank raw label plus a blank winner must fail
        # the alignment gate, not sail through "" == "" into a side-a victory
        # invented from an unknown outcome.
        rows = [
            _row(
                "hced-vacuous",
                "Battle of Vacuum",
                1700,
                "",
                "Bland",
                "",
                "Bland",
                codes1=("x1",),
            )
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), _resolve_code_stub, _resolve_label_stub
        )
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(result["rejections"]["label_outcome_not_aligned"], 1)

    def test_coded_side_failures_are_counted_in_the_label_pass(self) -> None:
        # A deferred row's coded side still resolves through the Seshat-code
        # path; its failures surface under the label-pass counters, never the
        # pass-1 counters.
        def failing_code(reason):
            def resolve(code, low_year, high_year):
                return None, None, reason

            return resolve

        for reason in ("outside_continuity_policy", "no_unique_time_valid_polity"):
            with self.subTest(reason=reason):
                rows = [
                    _row(
                        f"hced-coded-{reason}",
                        "Battle of Codes",
                        1700,
                        "Aland",
                        "Bland",
                        "Aland",
                        "Bland",
                        codes1=("x1",),
                    )
                ]
                result = promote_hced_label_rows(
                    rows, set(), set(), failing_code(reason), _resolve_label_stub
                )
                self.assertEqual(result["accepted"], 0)
                self.assertEqual(result["rejections"][reason], 1)

    def test_confidence_penalty_per_label_resolved_side(self) -> None:
        rows = [
            # consulted, one coded + one label side, point year -> 0.70
            _row(
                "c-1",
                "Battle One",
                1801,
                "A1",
                "B1",
                "A1",
                "B1",
                codes1=("x1",),
                consulted="src",
            ),
            # consulted, two label sides, point year -> 0.67
            _row("c-2", "Battle Two", 1802, "A2", "B2", "A2", "B2", consulted="src"),
            # unconsulted, one coded + one label side, point year -> 0.64
            _row("c-3", "Battle Three", 1803, "A3", "B3", "A3", "B3", codes1=("x3",)),
            # unconsulted, two label sides, point year -> 0.61
            _row("c-4", "Battle Four", 1804, "A4", "B4", "A4", "B4"),
            # unconsulted, two label sides, year range -> 0.58
            _row("c-5", "Battle Five", 1805, "A5", "B5", "A5", "B5", year_high=1806),
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), _resolve_code_stub, _resolve_label_stub
        )
        self.assertEqual(result["accepted"], 5)
        confidences = {
            e["hced_candidate_id"]: e["confidence"] for e in result["events"]
        }
        self.assertEqual(
            confidences,
            {"c-1": 0.70, "c-2": 0.67, "c-3": 0.64, "c-4": 0.61, "c-5": 0.58},
        )
        self.assertEqual(set(confidences.values()), LABEL_CONFIDENCE_VALUES)
        for event in result["events"]:
            for participant in event["participants"]:
                self.assertEqual(
                    participant["evidence_confidence"], event["confidence"]
                )

    def test_event_carries_identity_resolution_provenance(self) -> None:
        rows = [
            _row(
                "hced-777",
                "Battle of Marker",
                1650,
                "Fooland",
                "Barland",
                "Fooland",
                "Barland",
            )
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), _resolve_code_stub, _resolve_label_stub
        )
        event = result["events"][0]
        self.assertTrue(str(event["id"]).startswith("hced_label_"))
        self.assertEqual(event["identity_resolution"], "label")
        self.assertEqual(event["hced_candidate_id"], "hced-777")
        self.assertEqual(set(event["side_identity_resolution"]), {"side_a", "side_b"})
        for tier in event["side_identity_resolution"].values():
            self.assertIn(tier, LABEL_TIERS | {"seshat_crosswalk"})
        self.assertIn("time-bounded label policy", event["summary"])
        self.assertIn("lower identity confidence", event["summary"])
        self.assertEqual(event["event_type"], "engagement")

    def test_same_name_year_label_rows_use_source_disambiguation(
        self,
    ) -> None:
        promoted = {_event_key("Battle of Foo", 1800)}
        rows = [
            # duplicates a pass-1 promoted event
            _row("d-1", "Battle of Foo", 1800, "A1", "B1", "A1", "B1"),
            # Distinct source assertions with one display name and year both
            # survive; source order must not choose a winner.
            _row("d-2", "Battle of Bar", 1801, "A2", "B2", "A2", "B2"),
            _row("d-3", "Battle of Bar", 1801, "B2", "A2", "B2", "A2"),
            # duplicates a curated seed event
            _row("d-4", "Battle of Seed", 1802, "A3", "B3", "A3", "B3"),
        ]
        result = promote_hced_label_rows(
            rows,
            {_event_key("Battle of Seed", 1802)},
            promoted,
            _resolve_code_stub,
            _resolve_label_stub,
        )
        self.assertEqual(result["accepted"], 2)
        self.assertEqual(
            {event["hced_candidate_id"] for event in result["events"]},
            {"d-2", "d-3"},
        )
        self.assertEqual(result["rejections"]["duplicate_of_promoted_event"], 1)
        self.assertEqual(result["rejections"]["duplicate_of_curated_seed"], 1)

    def test_source_ids_include_cliopatria_only_when_a_clio_entity_participates(
        self,
    ) -> None:
        def resolve_clio(label, low_year, high_year):
            normalized = normalize_label(label)
            if normalized == "clioland":
                return "clio_land_1400_abcd1234", None, None, "cliopatria_alias"
            return f"seed_{normalized}", None, None, "seed_alias"

        rows = [
            _row("s-1", "Battle of Seeds", 1500, "Aland", "Bland", "Aland", "Bland"),
            _row(
                "s-2", "Battle of Clio", 1501, "Clioland", "Bland", "Clioland", "Bland"
            ),
        ]
        result = promote_hced_label_rows(
            rows, set(), set(), _resolve_code_stub, resolve_clio
        )
        by_id = {e["hced_candidate_id"]: e for e in result["events"]}
        self.assertEqual(
            by_id["s-1"]["source_ids"], ["hced_dataset", "hced_seshat_crosswalk"]
        )
        self.assertEqual(
            by_id["s-2"]["source_ids"],
            ["hced_dataset", "hced_seshat_crosswalk", "cliopatria_v020"],
        )

    def test_entities_materialize_only_on_acceptance(self) -> None:
        polity = _polity("Aland Kingdom", 1400, 1600, aliases=("Aland",))

        def resolver(label, low_year, high_year):
            normalized = normalize_label(label)
            if normalized == "aland":
                return _candidate_entity_id(polity), polity, None, "cliopatria_alias"
            return f"seed_{normalized}", None, None, "seed_alias"

        # The row resolves both sides but dies at the promoted-event dedup
        # gate: no polity may reach the entity index.
        rejected = promote_hced_label_rows(
            [_row("m-1", "Battle of Foo", 1500, "Aland", "Bland", "Aland", "Bland")],
            set(),
            {_event_key("Battle of Foo", 1500)},
            _resolve_code_stub,
            resolver,
        )
        self.assertEqual(rejected["accepted"], 0)
        self.assertEqual(rejected["rejections"]["duplicate_of_promoted_event"], 1)
        self.assertEqual(rejected["resolved_polities"], {})
        # The same row without the duplicate materializes exactly the polity.
        accepted = promote_hced_label_rows(
            [_row("m-1", "Battle of Foo", 1500, "Aland", "Bland", "Aland", "Bland")],
            set(),
            set(),
            _resolve_code_stub,
            resolver,
        )
        self.assertEqual(accepted["accepted"], 1)
        self.assertEqual(
            accepted["resolved_polities"], {_candidate_entity_id(polity): polity}
        )


@unittest.skipUnless(
    RELEASE_EVENTS.exists() and RELEASE_METADATA.exists() and RELEASE_ENTITIES.exists(),
    "release artifact not built",
)
class ReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        cls.entities = json.loads(RELEASE_ENTITIES.read_text(encoding="utf-8"))
        cls.label_events = [
            e for e in cls.events if str(e["id"]).startswith("hced_label_")
        ]

    def test_existing_crosswalk_payload_is_unchanged_except_audited_correction(
        self,
    ) -> None:
        # Pin Wave 4's reviewed pre-label-pass events by stable ID, not by their
        # positions in the rebuilt ledger. Later promotion waves may insert new
        # crosswalk or strategic rows ahead of the label pass without changing
        # the content of this baseline cohort.
        baseline_ids = WAVE4_PRE_LABEL_EVENT_IDS.read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(len(baseline_ids), 1_865)
        self.assertEqual(len(baseline_ids), len(set(baseline_ids)))
        events_by_id = {str(event["id"]): event for event in self.events}
        missing_ids = set(baseline_ids) - set(events_by_id)
        audited_removals = {"hced_hced_aros1886_1"}
        self.assertEqual(
            missing_ids,
            audited_removals,
            "an unenumerated Wave 4 baseline event disappeared",
        )
        self.assertIn("hced-Aros1886-1", HCED_CURATED_EXCLUSIONS)
        legacy = [
            events_by_id[event_id]
            for event_id in baseline_ids
            if event_id not in audited_removals
        ]
        legacy_payload = []
        for event in legacy:
            additive_fields = {
                "outcome_source_ids",
                "outcome_source_family_ids",
            }
            if str(event["id"]).startswith("hced_hced_"):
                additive_fields.update(
                    {
                        "hced_candidate_id",
                        "modern_location_country",
                        "geometry",
                        "location_provenance",
                    }
                )
            legacy_payload.append(
                {
                    key: value
                    for key, value in event.items()
                    if key not in additive_fields
                }
            )
        digest = hashlib.sha256(
            json.dumps(legacy_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            digest,
            "f759ddc612f635bae9c0921792afa32457da80d682f23a6d1e82be578a151b01",
            "pre-label-pass event block changed content",
        )
        self.assertGreater(len(self.events), len(legacy))
        # Exactly one legacy crosswalk event carries a reviewed Wave 8
        # correction annotation (Cracow 1772); every other legacy event stays
        # unmarked, so a new marker appearing in the block still fails.
        legacy_marked = {
            str(event["id"]): str(event.get("identity_resolution"))
            for event in legacy
            if "identity_resolution" in event
        }
        self.assertEqual(
            legacy_marked,
            {"hced_hced_cracow1772_1": "candidate_keyed_exact_wave8_correction"},
        )
        hced_legacy = [e for e in legacy if str(e["id"]).startswith("hced_")]
        self.assertEqual(len(hced_legacy), 1768)
        for event in hced_legacy:
            self.assertTrue(
                str(event["id"]).startswith("hced_hced_"),
                f"unexpected hced id in legacy block: {event['id']}",
            )
        # No label event leaked in front of the append point.
        self.assertTrue(all(not str(e["id"]).startswith("hced_label_") for e in legacy))

    def test_iwd_promotion_is_unchanged_by_the_label_pass(self) -> None:
        iwd_events = [e for e in self.events if str(e["id"]).startswith("iwd_war_")]
        self.assertEqual(len(iwd_events), 66)
        promotion = self.metadata["promotion"]
        self.assertEqual(promotion["accepted_iwd_wars"], 66)
        self.assertEqual(
            sum(promotion["iwd_rejections"].values()) + 66,
            promotion["iwd_parent_wars_total"],
        )
        for event in iwd_events:
            self.assertNotIn("identity_resolution", event)

    def test_same_name_year_hced_collisions_are_enumerated(self) -> None:
        groups: dict[tuple[str, int], list[str]] = {}
        for event in self.events:
            if not str(event["id"]).startswith("hced_"):
                continue
            key = (_normalized_event_name(event["name"]), int(event["year"]))
            groups.setdefault(key, []).append(str(event["id"]))
        collisions = {tuple(sorted(ids)) for ids in groups.values() if len(ids) > 1}
        self.assertEqual(
            collisions,
            {
                (
                    "hced_label_hced_second_arlon1794_1",
                    "hced_label_hced_third_arlon1794_1",
                ),
                (
                    "hced_label_hced_2ndbreslau1757_1",
                    "hced_label_hced_breslau1757_1",
                ),
                (
                    "hced_label_hced_corfuland1716_1",
                    "hced_label_hced_corfusea1716_1",
                ),
                (
                    "hced_hced_1stgiurgevo1811_1",
                    "hced_hced_2ndgiurgevo1811_1",
                ),
                (
                    "hced_label_hced_2ndschweidnitz1757_1",
                    "hced_label_hced_schweidnitz1757_1",
                ),
            },
        )

    def test_label_events_all_carry_marker_and_reduced_confidence(self) -> None:
        self.assertEqual(
            len(self.label_events),
            self.metadata["promotion"]["accepted_hced_label_events"],
        )
        self.assertTrue(self.label_events)
        expected_migrations = {
            row["event_id"]
            for row in self.metadata["promotion"]["wave7_global_identity_migrations"]
        }
        observed_migrations = {
            event["id"]
            for event in self.label_events
            if event.get("identity_resolution") == "wave7_candidate_keyed_migration"
        }
        self.assertEqual(observed_migrations, expected_migrations)
        for event in self.label_events:
            self.assertIn(
                event["identity_resolution"],
                {"label", "wave7_candidate_keyed_migration"},
            )
            self.assertLessEqual(event["confidence"], 0.70)
            self.assertIn(event["confidence"], LABEL_CONFIDENCE_VALUES)
            self.assertEqual(event["event_type"], "engagement")
            tiers = event["side_identity_resolution"]
            self.assertEqual(set(tiers), {"side_a", "side_b"})
            for tier in tiers.values():
                self.assertIn(
                    tier,
                    LABEL_TIERS
                    | {
                        "seshat_crosswalk",
                        "wave6_pre1500_candidate_policy",
                        "wave7_candidate_keyed_exact",
                        "candidate_reviewed_code_binding",
                        "candidate_reviewed_label_binding",
                    },
                )
            # At least one side is label- or reviewed-candidate-resolved on
            # every event emitted through this pass.
            self.assertTrue(
                set(tiers.values())
                & (
                    LABEL_TIERS
                    | {
                        "wave6_pre1500_candidate_policy",
                        "wave7_candidate_keyed_exact",
                        "candidate_reviewed_code_binding",
                        "candidate_reviewed_label_binding",
                    }
                )
            )

    def test_no_faction_or_pending_split_label_entity_in_any_label_event(self) -> None:
        names_by_id = {str(row["id"]): str(row["name"]) for row in self.entities}
        blocked = HCED_FACTION_LABELS | HCED_PENDING_SPLIT_LABELS
        for event in self.label_events:
            for participant in event["participants"]:
                entity_id = str(participant["entity_id"])
                self.assertIn(entity_id, names_by_id)
                self.assertNotIn(
                    normalize_label(names_by_id[entity_id]),
                    blocked,
                    f"blocked label entity {entity_id} in {event['id']}",
                )

    @unittest.skipUnless(
        (PROJECT_ROOT / "data" / "review" / "hced-candidates.jsonl").exists(),
        "staged HCED review queue not present",
    )
    def test_no_blocked_source_label_resolved_into_any_label_event(self) -> None:
        # The documented leak class is a blocked SOURCE label resolving to an
        # entity whose canonical name differs (e.g. the label "vikings"
        # reaching the "Viking settlements" record). Join every label event
        # back to its staged candidate and check the raw side labels of the
        # label-resolved sides, not just entity names.
        review_path = PROJECT_ROOT / "data" / "review" / "hced-candidates.jsonl"
        candidates = {}
        with review_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    candidates[str(row["candidate_id"])] = row
        blocked = HCED_FACTION_LABELS | HCED_PENDING_SPLIT_LABELS
        joined = 0
        for event in self.label_events:
            candidate = candidates.get(str(event["hced_candidate_id"]))
            if candidate is None:
                continue
            joined += 1
            tiers = event["side_identity_resolution"]
            for side_key, label_field in (
                ("side_a", "side_1_raw"),
                ("side_b", "side_2_raw"),
            ):
                if tiers[side_key] == "seshat_crosswalk":
                    continue
                self.assertNotIn(
                    normalize_label(candidate.get(label_field)),
                    blocked,
                    f"blocked source label resolved in {event['id']}",
                )
        self.assertGreater(joined, 0, "no label event joined a staged candidate")

    def test_observation_tier_events_match_the_declared_audit_list(self) -> None:
        audit = self.metadata["promotion"]["hced_label_observation_resolutions"]
        self.assertEqual(
            [entry["label"] for entry in audit], ["north korea", "timurid empire"]
        )
        self.assertEqual(
            {entry["label"]: entry["resolved_sides"] for entry in audit},
            {"north korea": 10, "timurid empire": 1},
        )
        observation_sides = sum(
            1
            for event in self.label_events
            for tier in event["side_identity_resolution"].values()
            if tier == "crosswalk_observation"
        )
        self.assertEqual(
            observation_sides, sum(entry["resolved_sides"] for entry in audit)
        )

    def test_label_events_never_claim_strategic_severity(self) -> None:
        tactical_classes = {
            "limited_victory",
            "limited_defeat",
            "major_tactical_victory",
            "major_tactical_defeat",
            "stalemate_or_inconclusive",
        }
        tactical_terminations = {
            "engagement_victory",
            "engagement_defeat",
            "inconclusive_engagement",
        }
        for event in self.label_events:
            self.assertEqual(event["event_type"], "engagement")
            for participant in event["participants"]:
                self.assertIn(participant["result_class"], tactical_classes)
                self.assertIn(participant["termination"], tactical_terminations)


@unittest.skipUnless(
    RELEASE_EVENTS.exists() and RELEASE_METADATA.exists() and REGISTRY.exists(),
    "release and registry artifacts not built",
)
class ArtifactCountConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_hced_promotion_accounting_identity(self) -> None:
        promotion = self.metadata["promotion"]
        pass1_rejected = sum(promotion["hced_rejections"].values())
        label_rejected = sum(promotion["hced_label_rejections"].values())
        accepted = promotion["accepted_hced_events"]
        label_accepted = promotion["accepted_hced_label_events"]
        queue_total = promotion["source_queue_counts"]["hced-candidates.jsonl"]
        self.assertEqual(
            pass1_rejected + label_rejected + accepted + label_accepted, queue_total
        )
        # Pinned measured funnel after reserving the reviewed Wave 8 rows:
        # 1,533 + 2,936 + 1,887 + 2,525 == 8,881.
        self.assertEqual(
            (pass1_rejected, label_rejected, accepted, label_accepted, queue_total),
            (1533, 2936, 1887, 2525, 8881),
        )
        # Label-pass identity: rejections + accepted == deferred input rows.
        self.assertEqual(
            label_rejected + label_accepted,
            promotion["hced_label_pass_input_rows"],
        )
        self.assertEqual(promotion["hced_label_pass_input_rows"], 5_461)
        # All thirteen declared counters are present, including the zeros.
        self.assertEqual(len(promotion["hced_label_rejections"]), 13)
        self.assertEqual(
            promotion["hced_label_rejections"]["duplicate_of_promoted_event"], 0
        )
        self.assertEqual(
            promotion["hced_label_rejections"]["curated_row_exclusion"], 87
        )
        self.assertEqual(promotion["hced_rejections"]["curated_exclusion"], 158)
        # uncoded_side is gone from pass 1: replaced by the deferral.
        self.assertNotIn("uncoded_side", promotion["hced_rejections"])

    def test_label_event_counts_agree_across_artifacts(self) -> None:
        label_events = [
            e for e in self.events if str(e["id"]).startswith("hced_label_")
        ]
        coverage = self.registry["coverage"]
        self.assertEqual(len(label_events), 2_525)
        self.assertEqual(coverage["provisional_hced_label_events"], len(label_events))
        self.assertEqual(
            self.metadata["promotion"]["accepted_hced_label_events"], len(label_events)
        )
        self.assertEqual(
            len(self.events), self.metadata["record_counts_expected"]["events"]
        )
        self.assertEqual(coverage["rated_events"], len(self.events))

    def test_unresolved_event_candidates_subtract_label_events(self) -> None:
        coverage = self.registry["coverage"]
        queue = coverage["source_queue_counts"]
        self.assertEqual(coverage["staged_source_records"], sum(queue.values()))
        event_like = (
            coverage["staged_source_records"]
            - queue["cliopatria-entity-candidates.jsonl"]
            - queue["ucdp-actor-26.1-candidates.jsonl"]
        )
        candidate_keyed_hced = sum(
            value
            for key, value in coverage.items()
            if key.startswith("candidate_keyed_") and key.endswith("_hced_events")
        )
        expected_unresolved = (
            event_like
            - coverage["provisional_hced_events"]
            - coverage["provisional_hced_label_events"]
            - candidate_keyed_hced
            - coverage["iwd_components_aggregated"]
            - coverage["provisional_iwbd_battles"]
            - coverage["provisional_ucdp_events"]
        )
        self.assertEqual(coverage["unresolved_event_candidates"], expected_unresolved)


if __name__ == "__main__":
    unittest.main()
