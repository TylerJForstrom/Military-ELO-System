import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion import wave8_followup_e as lane


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8FollowupEBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.brecke = _jsonl(ROOT / "data/reference/brecke-wars.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.ucdp = []
        for filename in (
            "ucdp-actor-26.1-candidates.jsonl",
            "ucdp-conflict-26.1-candidates.jsonl",
            "ucdp-dyadic-26.1-candidates.jsonl",
            "ucdp-termination-dyad-candidates.jsonl",
        ):
            cls.ucdp.extend(_jsonl(ROOT / "data/review" / filename))
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _base_artifacts(self):
        entity_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_ENTITIES}
        source_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_SOURCES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in entity_ids
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_FOLLOWUP_E_RESERVED_IDS
        ]
        return entities, sources, existing

    def _integrated(self):
        entities, sources, existing = self._base_artifacts()
        lane.install_wave8_followup_e_entities(entities)
        lane.install_wave8_followup_e_sources(sources)
        promoted = lane.promote_wave8_followup_e_contracts(
            self.hced,
            entities,
            existing,
        )
        return entities, sources, existing, promoted

    def test_verified_inventory_is_exact_and_disjoint(self) -> None:
        counts = lane.wave8_followup_e_counts()
        self.assertEqual(
            counts,
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_dispositions": 30,
                "holds": 3,
                "location_reviews": 13,
                "new_entities": 27,
                "new_sources": 47,
                "newly_rated_events": 13,
                "point_quarantine_additions": 11,
                "promotion_contracts": 13,
                "reviewed_hced_rows": 19,
                "terminal_exclusions": 3,
            },
        )
        dispositions = (
            set(lane.WAVE8_FOLLOWUP_E_CONTRACT_IDS),
            set(lane.WAVE8_FOLLOWUP_E_HOLDS),
            set(lane.WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS),
        )
        for left in range(len(dispositions)):
            for right in range(left + 1, len(dispositions)):
                self.assertFalse(dispositions[left] & dispositions[right])
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_E_RESERVED_IDS,
            set().union(*dispositions),
        )
        self.assertEqual(
            len({str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_ENTITIES}),
            27,
        )
        self.assertEqual(
            len({str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_SOURCES}),
            47,
        )

    def test_holds_and_terminal_exclusions_are_nonrating_never_draws(self) -> None:
        for hold in lane.WAVE8_FOLLOWUP_E_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)
            self.assertNotEqual(hold.get("result_type"), "draw")
        for exclusion in lane.WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS.values():
            self.assertEqual(exclusion["disposition"], "terminal_exclusion")
            self.assertIs(exclusion["terminal_exclusion"], True)
            self.assertIs(exclusion["unknown_is_never_draw"], True)
            self.assertNotIn("result_type", exclusion)
            self.assertNotIn("winner_side", exclusion)
        self.assertEqual(
            set(lane.WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS),
            {
                "hced-Calatanazar1002-1",
                "hced-Hudayda1934-1",
                "hced-Zamora873-1",
            },
        )

    def test_explicit_funnel_and_location_adapters_are_pinned(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_FOLLOWUP_E_FUNNEL_AUDITS),
            {
                "banu_bu_ali_berad",
                "cordova",
                "honduran_rebels",
                "somali_rebels",
            },
        )
        self.assertNotIn("saudi_arabia_exact", lane.WAVE8_FOLLOWUP_E_FUNNEL_AUDITS)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_E_LOCATION_REVIEWS), 13)
        self.assertEqual(
            set(lane.WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS), 11)
        self.assertFalse(lane.WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS)
        for candidate_id in (
            "hced-Dul Madoba1913-1",
            "hced-Hudayda1934-1",
        ):
            self.assertIn(candidate_id, lane.WAVE8_FOLLOWUP_E_LOCATION_REVIEWS)
            self.assertNotIn(
                candidate_id,
                lane.WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS,
            )
            self.assertNotIn(
                candidate_id,
                lane.WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS,
            )

    def test_all_five_queue_validators_run_fail_closed(self) -> None:
        validations = lane.validate_wave8_followup_e_queue_contracts(self.hced)
        self.assertEqual(
            list(validations),
            [
                "cordova",
                "honduran_rebels",
                "somali_rebels",
                "banu_bu_ali_berad",
                "saudi_arabia_exact",
            ],
        )
        self.assertEqual(
            sum(item["promotion_contracts"] for item in validations.values()),
            13,
        )
        self.assertEqual(
            sum(item["reviewed_hced_rows"] for item in validations.values()),
            19,
        )
        self.assertEqual(sum(item.get("holds", 0) for item in validations.values()), 3)
        self.assertEqual(
            sum(item.get("terminal_exclusions", 0) for item in validations.values()),
            3,
        )

    def test_four_declared_historical_funnels_validate(self) -> None:
        historical_rows = []
        for audits in lane.WAVE8_FOLLOWUP_E_FUNNEL_AUDITS.values():
            for label, expected in audits.items():
                row = {"label": label, **copy.deepcopy(expected)}
                if "zero_time_valid_candidates" in row:
                    zero_time_valid = row.pop("zero_time_valid_candidates")
                    row["failure_cases"] = {
                        "zero_time_valid_candidates": zero_time_valid
                    }
                historical_rows.append(row)
        validations = lane.validate_wave8_followup_e_funnels(
            {"labels": historical_rows}
        )
        self.assertEqual(
            set(validations),
            {
                "banu_bu_ali_berad",
                "cordova",
                "honduran_rebels",
                "somali_rebels",
            },
        )
        self.assertEqual(validations["cordova"]["labels"], 2)
        self.assertEqual(validations["honduran_rebels"]["audited_labels"], 2)
        self.assertEqual(validations["somali_rebels"]["events_touched"], 3)
        self.assertEqual(
            set(validations["banu_bu_ali_berad"]),
            {"banu bu ali", "berad tribes"},
        )
        historical_fingerprints = {
            (label, str(expected["event_candidate_id_sha256"]))
            for audits in lane.WAVE8_FOLLOWUP_E_FUNNEL_AUDITS.values()
            for label, expected in audits.items()
        }
        live_fingerprints = {
            (str(row.get("label")), str(row.get("event_candidate_id_sha256")))
            for row in self.funnel.get("labels", [])
        }
        self.assertTrue(historical_fingerprints.isdisjoint(live_fingerprints))

    def test_heterogeneous_discovery_inputs_all_remain_nonrating(self) -> None:
        validations = lane.validate_wave8_followup_e_discovery_dispositions(
            self.hced,
            self.iwbd,
            self.brecke,
            self.wikidata,
            self.ucdp,
        )
        self.assertEqual(
            set(validations),
            {
                "banu_bu_ali_berad",
                "cordova",
                "honduran_rebels",
                "saudi_arabia_exact",
                "somali_rebels",
            },
        )
        self.assertEqual(validations["cordova"]["discovery_promotions"], 0)
        self.assertEqual(
            validations["honduran_rebels"]["discovery_promotions"],
            0,
        )
        self.assertEqual(validations["somali_rebels"]["automated_promotions"], 0)
        self.assertEqual(
            validations["saudi_arabia_exact"]["discovery_promotions"],
            0,
        )
        self.assertEqual(
            validations["somali_rebels"]["ucdp_dispositions"],
            10,
        )
        self.assertEqual(
            validations["saudi_arabia_exact"]["iwbd_discovery_duplicates"],
            1,
        )

    def test_discovery_adapter_fails_on_ucdp_fingerprint_drift(self) -> None:
        ucdp = copy.deepcopy(self.ucdp)
        row = next(
            item
            for item in ucdp
            if item.get("candidate_id") == "ucdp-termination-dyad-337-2158"
        )
        row["raw"]["d_outcome"] = "3"
        with self.assertRaisesRegex(ValueError, "UCDP fingerprint changed"):
            lane.validate_wave8_followup_e_discovery_dispositions(
                self.hced,
                self.iwbd,
                self.brecke,
                self.wikidata,
                ucdp,
            )

    def test_cross_dataset_adjacency_and_parent_ownership_validate(self) -> None:
        _, _, existing = self._base_artifacts()
        validations = lane.validate_wave8_followup_e_integration_dispositions(
            self.hced,
            self.iwd,
            self.iwbd,
            self.brecke,
            self.wikidata,
            self.ucdp,
            existing,
        )
        self.assertEqual(
            set(validations),
            {
                "banu_bu_ali_berad",
                "cordova",
                "honduran_rebels",
                "saudi_arabia_exact",
                "somali_rebels",
            },
        )
        self.assertEqual(
            validations["saudi_arabia_exact"]["existing_parent_war_owners"],
            1,
        )
        self.assertEqual(
            validations["honduran_rebels"]["parent_coverage_dispositions"],
            2,
        )
        self.assertEqual(
            validations["somali_rebels"]["integration_dispositions"],
            12,
        )

    def test_entity_and_source_installation_is_complete_and_idempotent(self) -> None:
        entities, sources, _ = self._base_artifacts()
        lane.install_wave8_followup_e_entities(entities)
        lane.install_wave8_followup_e_sources(sources)
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_ENTITIES},
            set(entities),
        )
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_E_SOURCES},
            set(sources),
        )
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_followup_e_entities(entities)
        lane.install_wave8_followup_e_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)

        conflicting_entities = copy.deepcopy(entities)
        entity_id = str(lane.WAVE8_FOLLOWUP_E_ENTITIES[0]["id"])
        conflicting_entities[entity_id]["name"] = "drifted"
        with self.assertRaises(ValueError):
            lane.install_wave8_followup_e_entities(conflicting_entities)
        conflicting_sources = copy.deepcopy(sources)
        source_id = str(lane.WAVE8_FOLLOWUP_E_SOURCES[0]["id"])
        conflicting_sources[source_id]["title"] = "drifted"
        with self.assertRaises(ValueError):
            lane.install_wave8_followup_e_sources(conflicting_sources)

    def test_declared_order_promotes_exactly_thirteen_unique_events(self) -> None:
        _, _, _, promoted = self._integrated()
        self.assertEqual(len(promoted), 13)
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in promoted},
            lane.WAVE8_FOLLOWUP_E_CONTRACT_IDS,
        )
        self.assertEqual(len({str(event["id"]) for event in promoted}), 13)
        self.assertTrue(
            all(
                event.get("identity_resolution") == "candidate_keyed_exact"
                for event in promoted
            )
        )
        emitted = {str(event["hced_candidate_id"]) for event in promoted}
        self.assertFalse(emitted & set(lane.WAVE8_FOLLOWUP_E_HOLDS))
        self.assertFalse(
            emitted & set(lane.WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS)
        )

    def test_sequential_duplicate_guard_rejects_a_second_promotion(self) -> None:
        entities, _, existing, promoted = self._integrated()
        with self.assertRaises(ValueError):
            lane.promote_wave8_followup_e_contracts(
                self.hced,
                entities,
                [*existing, *promoted],
            )

    def test_published_location_quarantines_apply_only_to_emitted_events(self) -> None:
        _, _, _, promoted = self._integrated()
        by_id = {str(event["hced_candidate_id"]): event for event in promoted}
        for candidate_id in lane.WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_id[candidate_id])
            self.assertIn("modern_location_country", by_id[candidate_id])
        self.assertNotIn("hced-Dul Madoba1913-1", by_id)
        self.assertNotIn("hced-Hudayda1934-1", by_id)

    def test_artifact_validator_accepts_absent_or_complete_and_rejects_partial(self) -> None:
        base_entities, base_sources, existing = self._base_artifacts()
        absent = lane.validate_wave8_followup_e_artifact_state(
            existing,
            base_entities.values(),
            base_sources.values(),
        )
        self.assertEqual(absent["artifact_state"], "absent")
        self.assertEqual(absent["events_present"], 0)

        entities, sources, existing, promoted = self._integrated()
        integrated = lane.validate_wave8_followup_e_artifact_state(
            [*existing, *promoted],
            entities.values(),
            sources.values(),
        )
        self.assertEqual(
            integrated,
            {
                "artifact_state": "integrated",
                "entities_present": 27,
                "events_present": 13,
                "holds_absent": 3,
                "sources_present": 47,
                "terminal_exclusions_absent": 3,
            },
        )
        with self.assertRaisesRegex(ValueError, "event state is partial"):
            lane.validate_wave8_followup_e_artifact_state(
                [*existing, *promoted[:-1]],
                entities.values(),
                sources.values(),
            )
        forbidden_event = {
            "id": "planted-unknown-hold",
            "hced_candidate_id": "hced-Dul Madoba1913-1",
        }
        with self.assertRaisesRegex(ValueError, "nonrating disposition"):
            lane.validate_wave8_followup_e_artifact_state(
                [*existing, forbidden_event],
                base_entities.values(),
                base_sources.values(),
            )

    def test_signature_and_metadata_are_sealed(self) -> None:
        self.assertEqual(
            lane.wave8_followup_e_audit_signature(),
            lane.WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE,
            "9248d7b4019353e9c108cd0848edb0845bb8732804beec5f665890654274d5ee",
        )
        metadata = lane.wave8_followup_e_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_followup_e_counts())
        self.assertEqual(len(metadata["lanes"]), 5)
        self.assertEqual(len(metadata["promoted_candidate_ids"]), 13)
        self.assertEqual(len(metadata["hold_candidate_ids"]), 3)
        self.assertEqual(len(metadata["terminal_exclusion_candidate_ids"]), 3)


if __name__ == "__main__":
    unittest.main()
