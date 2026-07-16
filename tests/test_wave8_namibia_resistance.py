import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_namibia_resistance import (
    WAVE8_NAMIBIA_LOCATION_REVIEW,
    WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS,
    WAVE8_NAMIBIA_RESISTANCE_CONTRACTS,
    WAVE8_NAMIBIA_RESISTANCE_ENTITIES,
    WAVE8_NAMIBIA_RESISTANCE_FINAL_AUDIT_SIGNATURE,
    WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS,
    WAVE8_NAMIBIA_RESISTANCE_HOLDS,
    WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS,
    WAVE8_NAMIBIA_RESISTANCE_SOURCES,
    full_hced_queue_row_sha256,
    install_wave8_namibia_resistance_entities,
    install_wave8_namibia_resistance_sources,
    promote_wave8_namibia_resistance_contracts,
    validate_wave8_namibia_resistance_queue_contracts,
    wave8_namibia_resistance_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _audit_signature() -> str:
    lines = []
    for disposition, inventory in (
        ("promote", WAVE8_NAMIBIA_RESISTANCE_CONTRACTS),
        ("hold", WAVE8_NAMIBIA_RESISTANCE_HOLDS),
    ):
        for candidate_id, item in sorted(inventory.items()):
            lines.append(
                "|".join(
                    (
                        disposition,
                        candidate_id,
                        item["raw_row_sha256"],
                        item["full_row_sha256"],
                        item["canonical_event"]["canonical_key"],
                        ",".join(item.get("side_1_entity_ids", [])),
                        ",".join(item.get("side_2_entity_ids", [])),
                        str(item.get("winner_side", "")),
                        ",".join(item.get("outcome_source_ids", [])),
                        item.get("hold_category", ""),
                    )
                )
            )
    for candidate_id, review in sorted(WAVE8_NAMIBIA_LOCATION_REVIEW.items()):
        lines.append(
            "|".join(
                (
                    "location",
                    candidate_id,
                    review["point_action"],
                    review["country_action"],
                    str(review.get("latitude", "")),
                    str(review.get("longitude", "")),
                    review.get("country", ""),
                )
            )
        )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


class Wave8NamibiaResistanceTests(unittest.TestCase):
    def _entities_and_existing(self):
        lane_ids = {entity["id"] for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
            if entity["id"] not in lane_ids
        }
        install_wave8_namibia_resistance_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id")
            not in WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS
        ]
        return entities, existing

    def test_inventory_counts_signature_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS),
                len(WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS),
            ),
            (8, 4),
        )
        self.assertFalse(
            WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS
            & WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS
        )
        self.assertEqual(
            WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS,
            WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS
            | WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS,
        )
        self.assertEqual(_audit_signature(), WAVE8_NAMIBIA_RESISTANCE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_namibia_resistance_cohort_counts(),
            {
                "morenga_resistance": 3,
                "ovaherero_resistance_1904": 2,
                "witbooi_resistance_1893_1894": 1,
                "witbooi_resistance_1904_1905": 2,
            },
        )

    def test_entities_are_bounded_alias_free_and_sources_parse(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_NAMIBIA_RESISTANCE_ENTITIES),
                len(WAVE8_NAMIBIA_RESISTANCE_SOURCES),
            ),
            (6, 22),
        )
        for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertLessEqual(entity["start_year"], entity["end_year"])
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        for source in WAVE8_NAMIBIA_RESISTANCE_SOURCES:
            Source.from_dict(source)

    def test_no_timeless_nama_herero_or_damara_identity(self) -> None:
        forbidden_ids = {"nama", "nama_tribe", "herero", "hereros", "damara"}
        forbidden_names = {"nama", "nama tribe", "herero", "hereros", "damara"}
        self.assertTrue(
            forbidden_ids.isdisjoint(
                {entity["id"] for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES}
            )
        )
        self.assertTrue(
            forbidden_names.isdisjoint(
                {entity["name"].casefold() for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES}
            )
        )
        self.assertTrue(
            all(not entity["aliases"] for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES)
        )
        installed_entities = {}
        install_wave8_namibia_resistance_entities(installed_entities)
        self.assertEqual(
            set(installed_entities),
            {entity["id"] for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES},
        )
        installed_sources = {}
        install_wave8_namibia_resistance_sources(installed_sources)
        self.assertEqual(
            set(installed_sources),
            {source["id"] for source in WAVE8_NAMIBIA_RESISTANCE_SOURCES},
        )

    def test_semantic_and_full_queue_hashes_validate_and_full_drift_fails(self) -> None:
        rows = _rows()
        self.assertEqual(
            validate_wave8_namibia_resistance_queue_contracts(rows),
            {"promotion_contracts": 8, "holds": 4, "reviewed_hced_rows": 12},
        )
        hornkranz = next(
            row for row in rows if row["candidate_id"] == "hced-Hornkranz1893-1"
        )
        hold = WAVE8_NAMIBIA_RESISTANCE_HOLDS["hced-Hornkranz1893-1"]
        self.assertEqual(canonical_hced_row_sha256(hornkranz), hold["raw_row_sha256"])
        self.assertEqual(full_hced_queue_row_sha256(hornkranz), hold["full_row_sha256"])

        changed = copy.deepcopy(rows)
        changed_hornkranz = next(
            row for row in changed if row["candidate_id"] == "hced-Hornkranz1893-1"
        )
        changed_hornkranz["massacre_raw"] = "No"
        self.assertEqual(
            canonical_hced_row_sha256(changed_hornkranz),
            hold["raw_row_sha256"],
            "the shared semantic fingerprint intentionally omits massacre_raw",
        )
        self.assertNotEqual(
            full_hced_queue_row_sha256(changed_hornkranz), hold["full_row_sha256"]
        )
        with self.assertRaisesRegex(ValueError, "full queue-row fingerprint changed"):
            validate_wave8_namibia_resistance_queue_contracts(changed)

    def test_exact_sides_emit_and_all_four_holds_remain_non_rateable(self) -> None:
        expected = {
            "hced-Freyers Farm1904-1": (
                ("jakob_morenga_resistance_force_1903_1907",),
                ("german_empire",),
            ),
            "hced-Hartebeestmund1905-1": (
                ("morenga_johannes_christian_hartebeestmund_coalition_1905",),
                ("german_empire",),
            ),
            "hced-Naris1904-1": (
                ("german_empire",),
                ("hendrik_witbooi_khowesin_resistance_1904_1905",),
            ),
            "hced-Naukluf1894-1": (
                ("german_empire",),
                ("hendrik_witbooi_khowesin_resistance_1893_1894",),
            ),
            "hced-Onganjira1904-1": (
                ("german_empire",),
                ("samuel_maharero_main_ovaherero_force_1904",),
            ),
            "hced-Vaalgras1905-1": (
                ("german_empire",),
                ("hendrik_witbooi_khowesin_resistance_1904_1905",),
            ),
            "hced-Van Rooisvlei1928-1": (
                ("german_empire",),
                ("jakob_morenga_resistance_force_1903_1907",),
            ),
            "hced-Waterberg1904-1": (
                ("german_empire",),
                ("samuel_maharero_main_ovaherero_force_1904",),
            ),
        }
        for candidate_id, contract in WAVE8_NAMIBIA_RESISTANCE_CONTRACTS.items():
            self.assertEqual(
                (
                    tuple(contract["side_1_entity_ids"]),
                    tuple(contract["side_2_entity_ids"]),
                ),
                expected[candidate_id],
            )
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])

        self.assertEqual(
            WAVE8_NAMIBIA_RESISTANCE_HOLDS["hced-Hornkranz1893-1"]["hold_category"],
            "massacre_without_rateable_outcome",
        )
        self.assertEqual(
            {
                WAVE8_NAMIBIA_RESISTANCE_HOLDS[candidate_id]["hold_category"]
                for candidate_id in {
                    "hced-Okaharui1904-1",
                    "hced-Oviumbo1904-1",
                    "hced-Owikokorero1904-1",
                }
            },
            {"contradictory_outcome_evidence", "outcome_unknown"},
        )

        entities, existing = self._entities_and_existing()
        events = promote_wave8_namibia_resistance_contracts(_rows(), entities, existing)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS,
        )
        self.assertTrue(
            WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS.isdisjoint(
                {event["hced_candidate_id"] for event in events}
            )
        )
        for event in events:
            Event.from_dict(event)
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["side"] == "side_a"
            }
            self.assertEqual(
                winners,
                set(
                    WAVE8_NAMIBIA_RESISTANCE_CONTRACTS[event["hced_candidate_id"]][
                        "side_1_entity_ids"
                    ]
                ),
            )

    def test_promotions_have_direct_outcome_provenance_without_reversals(self) -> None:
        source_by_id = {
            source["id"]: source for source in WAVE8_NAMIBIA_RESISTANCE_SOURCES
        }
        entities, existing = self._entities_and_existing()
        events = promote_wave8_namibia_resistance_contracts(_rows(), entities, existing)
        for event in events:
            contract = WAVE8_NAMIBIA_RESISTANCE_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertNotEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in event["outcome_source_ids"]
                )
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertTrue(event["id"].startswith("hced_wave8_namibia_resistance_"))

    def test_location_review_exports_corrections_and_quarantines(self) -> None:
        self.assertEqual(set(WAVE8_NAMIBIA_LOCATION_REVIEW), {
            "hced-Hartebeestmund1905-1",
            "hced-Okaharui1904-1",
            "hced-Onganjira1904-1",
            "hced-Owikokorero1904-1",
            "hced-Vaalgras1905-1",
            "hced-Van Rooisvlei1928-1",
            "hced-Waterberg1904-1",
        })
        self.assertEqual(
            (
                WAVE8_NAMIBIA_LOCATION_REVIEW["hced-Hartebeestmund1905-1"]["latitude"],
                WAVE8_NAMIBIA_LOCATION_REVIEW["hced-Hartebeestmund1905-1"]["longitude"],
            ),
            (-28.8, 18.88333),
        )
        self.assertEqual(
            (
                WAVE8_NAMIBIA_LOCATION_REVIEW["hced-Vaalgras1905-1"]["latitude"],
                WAVE8_NAMIBIA_LOCATION_REVIEW["hced-Vaalgras1905-1"]["longitude"],
            ),
            (-26.05, 18.516667),
        )
        self.assertEqual(
            WAVE8_NAMIBIA_LOCATION_REVIEW["hced-Waterberg1904-1"],
            {
                "point_action": "retain",
                "country_action": "override",
                "country": "Namibia",
                "evidence_refs": ["namibia_meft_waterberg"],
                "audit_note": "HCED's modern country South Africa is corrected to Namibia.",
            },
        )
        quarantine_ids = {
            candidate_id
            for candidate_id, review in WAVE8_NAMIBIA_LOCATION_REVIEW.items()
            if review["point_action"] == "quarantine"
        }
        self.assertEqual(
            quarantine_ids,
            {
                "hced-Okaharui1904-1",
                "hced-Onganjira1904-1",
                "hced-Owikokorero1904-1",
                "hced-Van Rooisvlei1928-1",
            },
        )
        self.assertTrue(
            set(WAVE8_NAMIBIA_LOCATION_REVIEW)
            <= WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS
        )


if __name__ == "__main__":
    unittest.main()

