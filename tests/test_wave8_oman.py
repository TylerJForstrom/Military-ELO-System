import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_oman as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
YARUBID_OMAN = "yarubid_imamate_oman_1624_1742"
SOURCE_CANDIDATE = "clio_q1752110_1626_66067cfa"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8OmanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane.install_wave8_oman_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_OMAN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith("hced_wave8_oman_")
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_oman_contracts(self.hced, entities, existing)

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_oman_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_exact_inventory_hashes_and_outcome_orientation_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_OMAN_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_OMAN_ROW_HASHES))
        self.assertEqual(len(rows), 3)
        for candidate_id, expected_hash in lane.WAVE8_OMAN_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (row["side_1_raw"], row["side_2_raw"]),
                    ("Oman", "Portugal"),
                )
                self.assertEqual(
                    (row["winner_raw"], row["loser_raw"]),
                    ("Oman", "Portugal"),
                )
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_oman_queue_contracts(self.hced),
            {
                "exact_label_rows": 4,
                "holds": 1,
                "out_of_cohort_exact_label_rows": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "target_exact_label_rows": 3,
            },
        )
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        if "oman" in labels:
            self.assertEqual(
                lane.validate_wave8_oman_funnel(self.funnel),
                {
                    "events_touched": 3,
                    "one_wrong_interval_candidate": 3,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 3,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_oman_exact_label_funnel_audit"
                ],
                lane.WAVE8_OMAN_FUNNEL_AUDIT,
            )

    def test_identity_is_time_bounded_alias_free_and_does_not_inherit(self) -> None:
        self.assertEqual(len(lane.WAVE8_OMAN_ENTITIES), 1)
        entity = lane.WAVE8_OMAN_ENTITIES[0]
        self.assertEqual(entity["id"], YARUBID_OMAN)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1624, 1742))
        self.assertFalse(entity["aliases"])
        self.assertFalse(entity["predecessors"])
        self.assertIn("No rating is inherited", entity["continuity_note"])
        Entity.from_dict(entity)

    def test_sources_parse_and_each_promotion_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_OMAN_SOURCES), 7)
        for source in lane.WAVE8_OMAN_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_OMAN_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(len(contract["outcome_source_ids"]), 2)
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])

    def test_only_muscat_and_fort_jesus_promote(self) -> None:
        self.assertEqual(
            lane.WAVE8_OMAN_CONTRACT_IDS,
            {"hced-Mombasa1696-1698-1", "hced-Muscat1650-1"},
        )
        self.assertEqual(lane.WAVE8_OMAN_HOLD_IDS, {"hced-Zanzibar1652-1"})
        self.assertEqual(
            lane.WAVE8_OMAN_RESERVED_IDS,
            set(lane.WAVE8_OMAN_ROW_HASHES),
        )
        events = self._events()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_OMAN_CONTRACT_IDS,
        )
        self.assertNotIn(
            "hced-Zanzibar1652-1",
            {event["hced_candidate_id"] for event in events},
        )

    def test_zanzibar_stays_unknown_and_is_never_a_draw(self) -> None:
        hold = lane.WAVE8_OMAN_HOLDS["hced-Zanzibar1652-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(
            hold["hold_category"],
            "contradictory_outcome_and_actor_evidence",
        )
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertEqual(len(hold["evidence_refs"]), 2)
        self.assertIn("ultimately repulsed", hold["hold_reason"])

    def test_promoted_events_lock_dates_actors_and_tactical_results(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        muscat = events["hced-Muscat1650-1"]
        self.assertEqual(muscat["name"], "Capture of Muscat")
        self.assertEqual((muscat["year"], muscat["end_year"]), (1650, 1650))
        self.assertEqual(muscat["date_precision"], "year")
        mombasa = events["hced-Mombasa1696-1698-1"]
        self.assertEqual(mombasa["name"], "Siege of Fort Jesus")
        self.assertEqual((mombasa["year"], mombasa["end_year"]), (1696, 1698))
        self.assertEqual(mombasa["date_precision"], "year_range")
        for event in events.values():
            terminations = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {
                    YARUBID_OMAN: "engagement_victory",
                    "kingdom_portugal": "engagement_defeat",
                },
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_unverified_points_are_withheld_but_jurisdictions_remain(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        expected_countries = {
            "hced-Muscat1650-1": "Oman",
            "hced-Mombasa1696-1698-1": "Kenya",
        }
        self.assertEqual(
            lane.WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_OMAN_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS)
        for candidate_id, event in events.items():
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"], expected_countries[candidate_id]
            )
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_exist(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_oman_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_installers_are_idempotent_and_reject_drift(self) -> None:
        entities, _ = self._installed()
        before = copy.deepcopy(entities[YARUBID_OMAN])
        lane.install_wave8_oman_entities(entities)
        self.assertEqual(entities[YARUBID_OMAN], before)
        entities[YARUBID_OMAN]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_oman_entities(entities)

        sources = {}
        lane.install_wave8_oman_sources(sources)
        lane.install_wave8_oman_sources(sources)
        self.assertEqual(len(sources), 7)
        first_source_id = str(lane.WAVE8_OMAN_SOURCES[0]["id"])
        sources[first_source_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_oman_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Muscat1650-1"
        )
        row["winner_raw"] = "Portugal"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_oman_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Capture of Muscat",
                "year": 1650,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_oman_contracts(self.hced, entities, existing)

    def test_signature_counts_and_cohort_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_oman_audit_signature(),
            lane.WAVE8_OMAN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_oman_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 1,
                "new_entities": 1,
                "new_sources": 7,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_oman_cohort_counts(),
            {"yarubid_portuguese_wars_1650_1698": 3},
        )

    def test_release_artifacts_are_either_preintegration_or_exactly_integrated(self) -> None:
        release_entities = {str(row["id"]): row for row in self.release_entities}
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id") in lane.WAVE8_OMAN_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertNotIn(YARUBID_OMAN, release_entities)
            self.assertFalse(release_events)
            return

        self.assertEqual(set(release_events), lane.WAVE8_OMAN_CONTRACT_IDS)
        self.assertIn(YARUBID_OMAN, release_entities)
        self.assertFalse(release_entities[YARUBID_OMAN]["aliases"])
        registry_entities = {
            str(row["id"]): row for row in self.registry["entities"]
        }
        self.assertEqual(registry_entities[YARUBID_OMAN]["status"], "rated")
        self.assertEqual(
            registry_entities[YARUBID_OMAN]["identity_status"], "curated"
        )
        self.assertEqual(registry_entities[SOURCE_CANDIDATE]["status"], "unrated")
        source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_OMAN_SOURCES}, source_ids
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_oman_hced_events"], 2)
        self.assertEqual(
            promotion["wave8_oman_candidate_ids"],
            sorted(lane.WAVE8_OMAN_CONTRACT_IDS),
        )
        self.assertEqual(len(promotion["wave8_oman_holds"]), 1)


if __name__ == "__main__":
    unittest.main()
