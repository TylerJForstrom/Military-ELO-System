import json
import unittest
from pathlib import Path

from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import (
    HCED_CURATED_EXCLUSIONS,
)
from military_elo.promotion.wave6_pre1500 import (
    WAVE6_PRE1500_CURATED_EXCLUSIONS,
    WAVE6_PRE1500_ENTITIES,
    WAVE6_PRE1500_ENTITY_IDS,
    WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS,
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE,
    WAVE6_PRE1500_FINGERPRINT_SHA256,
    WAVE6_PRE1500_HOLD_REASONS,
    WAVE6_PRE1500_LABEL_POLICIES,
    WAVE6_PRE1500_NEW_ENTITY_IDS,
    WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID,
    WAVE6_PRE1500_REUSED_ENTITY_IDS,
    WAVE6_PRE1500_SAFE_CANDIDATE_IDS,
    WAVE6_PRE1500_SOURCE_FAMILY_METADATA,
    WAVE6_PRE1500_SOURCES,
    annotate_and_validate_wave6_pre1500_events,
    resolve_wave6_pre1500_candidate_side_label,
    validate_wave6_pre1500_candidates,
    wave6_pre1500_label_policy_entity_id,
    wave6_pre1500_fingerprint,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_GLOB = "wave6_pre1500_manifest_*.jsonl"
MANDATORY_ADDITIONAL_HOLDS = {
    "hced-Selinus-409-1",
    "hced-Himera-409-1",
    "hced-Syracuse-213-1",
    "hced-Tenedos-85-1",
    "hced-Sebastia1070-1",
}


def _manifest_rows() -> list[dict]:
    rows: list[dict] = []
    fixture_root = PROJECT_ROOT / "tests" / "fixtures"
    for path in sorted(fixture_root.glob(FIXTURE_GLOB)):
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
    return rows


def _event(candidate_id: str, entity_ids: set[str] | frozenset[str]) -> dict:
    return {
        "hced_candidate_id": candidate_id,
        "participants": [
            {"entity_id": entity_id} for entity_id in sorted(entity_ids)
        ],
        "source_ids": ["hced_dataset"],
    }


def _valid_event_inventories() -> tuple[list[dict], list[dict]]:
    crosswalk = [
        _event(candidate_id, {entity_id})
        for candidate_id, entity_id in (
            WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID.items()
        )
    ]
    labels = [
        _event(candidate_id, entity_ids)
        for candidate_id, entity_ids in (
            WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE.items()
        )
    ]
    return crosswalk, labels


class Wave6Pre1500ManifestTests(unittest.TestCase):
    def test_exact_frozen_inventory_and_fingerprints(self) -> None:
        rows = _manifest_rows()
        by_id = {row["candidate_id"]: row for row in rows}
        safe = {
            row["candidate_id"] for row in rows if row["disposition"] == "safe"
        }
        holds = {
            row["candidate_id"] for row in rows if row["disposition"] == "hold"
        }

        self.assertEqual(len(rows), len(by_id))
        self.assertEqual(len(safe), 55)
        self.assertEqual(len(holds), 30)
        self.assertEqual(safe, set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS))
        self.assertEqual(holds, set(WAVE6_PRE1500_HOLD_REASONS))
        self.assertEqual(set(by_id), set(WAVE6_PRE1500_FINGERPRINT_SHA256))
        self.assertLessEqual(MANDATORY_ADDITIONAL_HOLDS, holds)

        validate_wave6_pre1500_candidates(rows)
        for candidate_id, row in by_id.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    wave6_pre1500_fingerprint(row),
                    WAVE6_PRE1500_FINGERPRINT_SHA256[candidate_id],
                )

    def test_manifest_fails_closed_on_missing_duplicate_or_drift(self) -> None:
        rows = _manifest_rows()
        with self.assertRaisesRegex(ValueError, "expected exactly one row"):
            validate_wave6_pre1500_candidates(rows[1:])
        with self.assertRaisesRegex(ValueError, "expected exactly one row"):
            validate_wave6_pre1500_candidates([*rows, dict(rows[0])])

        changed = [dict(row) for row in rows]
        changed[0]["winner_raw"] = "fingerprint drift"
        with self.assertRaisesRegex(ValueError, "semantic fingerprint changed"):
            validate_wave6_pre1500_candidates(changed)

    def test_safe_outcomes_sides_and_dates_are_point_locked(self) -> None:
        safe_ids = set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS)
        for row in _manifest_rows():
            if row["candidate_id"] not in safe_ids:
                continue
            with self.subTest(candidate_id=row["candidate_id"]):
                side_1 = normalize_label(row["side_1_raw"])
                side_2 = normalize_label(row["side_2_raw"])
                self.assertTrue(side_1)
                self.assertTrue(side_2)
                self.assertNotEqual(side_1, side_2)
                self.assertEqual(normalize_label(row["winner_raw"]), side_1)
                self.assertEqual(normalize_label(row["loser_raw"]), side_2)
                self.assertEqual(
                    row["year_low"], row["year_best"], row["candidate_id"]
                )
                self.assertEqual(
                    row["year_best"], row["year_high"], row["candidate_id"]
                )

    def test_duplicate_and_attribution_holds_are_never_safe(self) -> None:
        safe_ids = set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS)
        required_holds = {
            "hced-Motya-397-1",
            "hced-Zela-47-1",
            "hced-Kaffa1475-1",
            "hced-Gottolengo1427-1",
            "hced-Caravaggio1448-1",
            "hced-Milan1449-1",
            "hced-Tamaron1037-1",
            "hced-Aljubarrota1385-1",
            "hced-Spercheios996-1",
            "hced-Nesjar1016-1",
            "hced-Aasle1389-1",
            "hced-Falkoping1389-1",
            "hced-Tarq1002-1",
            "hced-Myriocephalum1176-1",
            "hced-Dunstable1461-1",
            *MANDATORY_ADDITIONAL_HOLDS,
        }
        self.assertLessEqual(required_holds, set(WAVE6_PRE1500_HOLD_REASONS))
        self.assertFalse(required_holds & safe_ids)

        safe_keys: list[tuple[str, int]] = []
        for row in _manifest_rows():
            if row["candidate_id"] in safe_ids:
                safe_keys.append(
                    (normalize_label(row["name"]), int(row["year_best"]))
                )
        self.assertEqual(len(safe_keys), len(set(safe_keys)))

    def test_every_hold_is_fingerprinted_and_enumerated(self) -> None:
        self.assertEqual(len(WAVE6_PRE1500_HOLD_REASONS), 30)
        self.assertEqual(
            set(WAVE6_PRE1500_CURATED_EXCLUSIONS),
            set(WAVE6_PRE1500_HOLD_REASONS) - {"hced-Genoa1684-1"},
        )
        self.assertFalse(
            set(WAVE6_PRE1500_CURATED_EXCLUSIONS)
            & set(HCED_CURATED_EXCLUSIONS)
        )
        self.assertLessEqual(
            set(WAVE6_PRE1500_HOLD_REASONS),
            set(WAVE6_PRE1500_FINGERPRINT_SHA256),
        )


class Wave6Pre1500PolicyTests(unittest.TestCase):
    def test_policy_windows_have_exact_boundaries_and_fail_closed_gaps(self) -> None:
        for label, windows in WAVE6_PRE1500_LABEL_POLICIES.items():
            for start, end, entity_id in windows:
                with self.subTest(label=label, edge="start", year=start):
                    self.assertEqual(
                        wave6_pre1500_label_policy_entity_id(label, start, start),
                        entity_id,
                    )
                with self.subTest(label=label, edge="end", year=end):
                    self.assertEqual(
                        wave6_pre1500_label_policy_entity_id(label, end, end),
                        entity_id,
                    )
            with self.subTest(label=label, edge="before"):
                self.assertIsNone(
                    wave6_pre1500_label_policy_entity_id(
                        label, windows[0][0] - 1, windows[0][0] - 1
                    )
                )
            for left, right in zip(windows, windows[1:]):
                if left[1] + 1 < right[0]:
                    gap_year = left[1] + 1
                    with self.subTest(label=label, edge="gap", year=gap_year):
                        self.assertIsNone(
                            wave6_pre1500_label_policy_entity_id(
                                label, gap_year, gap_year
                            )
                        )

        self.assertIsNone(wave6_pre1500_label_policy_entity_id("genoa", 1500, 1500))
        self.assertIsNone(wave6_pre1500_label_policy_entity_id("milan", 1448, 1448))
        self.assertIsNone(wave6_pre1500_label_policy_entity_id("pontus", -62, -62))
        self.assertIsNone(
            wave6_pre1500_label_policy_entity_id("seljuk turks", 1093, 1093)
        )
        self.assertIsNone(
            wave6_pre1500_label_policy_entity_id("yorkists", 1472, 1486)
        )

    def test_label_resolution_is_candidate_keyed_not_a_broad_fallback(self) -> None:
        context = {
            "release_entities": {
                entity["id"]: entity for entity in WAVE6_PRE1500_ENTITIES
            }
        }
        generic_calls: list[tuple[str, int, int]] = []

        def generic(label, low, high):
            generic_calls.append((label, low, high))
            return "generic_entity", None, None, "generic"

        resolved = resolve_wave6_pre1500_candidate_side_label(
            {"candidate_id": "hced-Syracuse-396-1"},
            "Syracuse",
            -396,
            -396,
            context,
            generic,
        )
        self.assertEqual(resolved[0], "syracuse_city_state")
        self.assertEqual(generic_calls, [])

        blocked = resolve_wave6_pre1500_candidate_side_label(
            {"candidate_id": "hced-not-in-manifest"},
            "Syracuse",
            -396,
            -396,
            context,
            generic,
        )
        self.assertIsNone(blocked[0])
        self.assertEqual(blocked[2], "wave6_pre1500_candidate_not_in_manifest")

        held = resolve_wave6_pre1500_candidate_side_label(
            {"candidate_id": "hced-Genoa1684-1"},
            "Genoa",
            1684,
            1684,
            context,
            generic,
        )
        self.assertIsNone(held[0])
        self.assertEqual(held[2], "wave6_pre1500_curated_hold")

        modern_denmark = resolve_wave6_pre1500_candidate_side_label(
            {"candidate_id": "hced-modern-denmark"},
            "Denmark",
            1700,
            1700,
            context,
            generic,
        )
        self.assertEqual(modern_denmark[0], "generic_entity")

    def test_exact_target_mapping_is_candidate_keyed(self) -> None:
        self.assertEqual(
            set(WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE),
            set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS),
        )
        for candidate_id, entity_ids in (
            WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertTrue(entity_ids)
                self.assertLessEqual(entity_ids, WAVE6_PRE1500_ENTITY_IDS)

    def test_event_inventory_guard_accepts_only_the_frozen_mapping(self) -> None:
        crosswalk, labels = _valid_event_inventories()
        annotate_and_validate_wave6_pre1500_events(crosswalk, labels)
        by_id = {event["hced_candidate_id"]: event for event in labels}
        for candidate_id, evidence_ids in (
            WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS.items()
        ):
            self.assertLessEqual(set(evidence_ids), set(by_id[candidate_id]["source_ids"]))

        crosswalk, labels = _valid_event_inventories()
        labels.append(dict(labels[0]))
        with self.assertRaisesRegex(ValueError, "exactly once"):
            annotate_and_validate_wave6_pre1500_events(crosswalk, labels)

        crosswalk, labels = _valid_event_inventories()
        labels[0]["participants"] = [{"entity_id": "wrong_entity"}]
        with self.assertRaisesRegex(ValueError, "target identity mismatch"):
            annotate_and_validate_wave6_pre1500_events(crosswalk, labels)

        crosswalk, labels = _valid_event_inventories()
        labels.append(_event("hced-Sebastia1070-1", {"wrong_entity"}))
        with self.assertRaisesRegex(ValueError, "hold promoted unexpectedly"):
            annotate_and_validate_wave6_pre1500_events(crosswalk, labels)

    def test_reused_bulgarian_and_seljuk_series_are_single_and_lossless(self) -> None:
        self.assertEqual(
            WAVE6_PRE1500_REUSED_ENTITY_IDS,
            {
                "clio_bg_bulgaria_early_682_95daf02a",
                "clio_ir_seljuk_sultanate_1040_577da931",
            },
        )
        self.assertEqual(len(WAVE6_PRE1500_NEW_ENTITY_IDS), 13)
        self.assertNotIn("first_bulgarian_empire", WAVE6_PRE1500_ENTITY_IDS)
        self.assertNotIn("great_seljuk_empire", WAVE6_PRE1500_ENTITY_IDS)

        entities = {entity["id"]: entity for entity in WAVE6_PRE1500_ENTITIES}
        self.assertEqual(
            (
                entities["clio_bg_bulgaria_early_682_95daf02a"]["start_year"],
                entities["clio_bg_bulgaria_early_682_95daf02a"]["end_year"],
            ),
            (681, 1018),
        )
        self.assertEqual(
            (
                entities["clio_ir_seljuk_sultanate_1040_577da931"]["start_year"],
                entities["clio_ir_seljuk_sultanate_1040_577da931"]["end_year"],
            ),
            (1040, 1194),
        )
        baseline = WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID
        self.assertEqual(
            list(baseline.values()).count("clio_bg_bulgaria_early_682_95daf02a"), 7
        )
        self.assertEqual(
            list(baseline.values()).count("clio_ir_seljuk_sultanate_1040_577da931"),
            1,
        )

        crosswalk, labels = _valid_event_inventories()
        with self.assertRaisesRegex(ValueError, "lost or repeated Wave 5 events"):
            annotate_and_validate_wave6_pre1500_events(crosswalk[1:], labels)

    def test_sources_have_explicit_family_dedup_and_direct_entity_links(self) -> None:
        sources = {source["id"]: source for source in WAVE6_PRE1500_SOURCES}
        self.assertEqual(len(sources), len(WAVE6_PRE1500_SOURCES))
        for source in sources.values():
            self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(source["source_family_id"])
            self.assertTrue(source["evidence_roles"])

        family_rows = {
            row["source_family_id"]: row
            for row in WAVE6_PRE1500_SOURCE_FAMILY_METADATA
        }
        family_source_ids = {
            source_id
            for row in family_rows.values()
            for source_id in row["source_ids"]
        }
        self.assertEqual(family_source_ids, set(sources))
        for row in family_rows.values():
            self.assertEqual(row["deduplication_unit"], "source_family_id")
            self.assertEqual(row["independence_credit"], "at_most_one_per_claim")
            for source_id in row["source_ids"]:
                self.assertEqual(
                    sources[source_id]["source_family_id"], row["source_family_id"]
                )

        self.assertEqual(
            {
                sources[source_id]["source_family_id"]
                for source_id in (
                    "wave6_treccani_genoa",
                    "wave6_treccani_ambrosian",
                    "wave6_treccani_maclodio",
                    "wave6_treccani_terraferma",
                )
            },
            {"treccani_editorial_corpus"},
        )
        for entity in WAVE6_PRE1500_ENTITIES:
            self.assertEqual(entity["aliases"], [])
            self.assertLessEqual(set(entity["source_ids"]), set(sources))


if __name__ == "__main__":
    unittest.main()
