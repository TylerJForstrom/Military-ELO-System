import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_montenegro_1796 as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_montenegro_1796_"

MONTENEGRIN_FORCE = "petar_i_montenegro_brda_force_1796"
SCUTARI_FORCE = "kara_mahmud_scutari_campaign_army_1796"

EXPECTED_HASHES = {
    "hced-Cevo1768-1": (
        "69eb2d4b6c218aba38b65b2b5f08289c2215fa92ccd5c719c4b6776020a6183b"
    ),
    "hced-Krusi1796-1": (
        "87c3703195d0cedfb683d3c84fa3572d5e17134787497b3ebf3a264e983f419b"
    ),
    "hced-Martinici1796-1": (
        "8ea09ffacc9e9876c5108b4fc60ef46aea33e8401e9e99f24834dbcb08a0fe77"
    ),
    "hced-Podgoritza1712-1": (
        "9c854f0b522fd10d3150c078ef36415b7770006e8bc41c316654917ff4dd5980"
    ),
}

EXPECTED_EXACT_LABEL_IDS = {
    "hced-Cevo1768-1",
    "hced-Fundina1876-1",
    "hced-Grahovo1858-1",
    "hced-Krusi1796-1",
    "hced-Martinici1796-1",
    "hced-Mojkovac1916-1",
    "hced-Ostrog1853-1",
    "hced-Podgoritza1712-1",
    "hced-Rijeka1862-1",
    "hced-Vucji Do1876-1",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8Montenegro1796Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "montenegro"
            or normalize_label(row.get("side_2_raw")) == "montenegro"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_MONTENEGRO_1796_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_MONTENEGRO_1796_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_montenegro_1796_entities(entities)
        lane.install_wave8_montenegro_1796_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_montenegro_1796_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_reviewed_row_hashes_are_pinned(self) -> None:
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(exact_ids, EXPECTED_EXACT_LABEL_IDS)
        self.assertEqual(
            lane.WAVE8_MONTENEGRO_1796_EXPECTED_EXACT_LABEL_IDS,
            frozenset(EXPECTED_EXACT_LABEL_IDS),
        )
        self.assertEqual(lane.WAVE8_MONTENEGRO_1796_ROW_HASHES, EXPECTED_HASHES)
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(by_id[candidate_id]), expected_hash
                )

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_montenegro_1796_queue_contracts(self.hced_rows),
            {
                "already_promoted_baseline_rows": 5,
                "exact_label_rows": 10,
                "existing_curated_exclusion_rows": 1,
                "holds": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
            },
        )
        self.assertEqual(
            lane.validate_wave8_montenegro_1796_funnel(self.funnel),
            {
                "events_touched": 4,
                "one_wrong_interval_candidates": 4,
                "sole_blocker_events": 3,
            },
        )

    def test_dispositions_promote_only_the_two_uncontested_1796_battles(self) -> None:
        self.assertEqual(
            lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS,
            {"hced-Krusi1796-1", "hced-Martinici1796-1"},
        )
        self.assertEqual(
            lane.WAVE8_MONTENEGRO_1796_HOLD_IDS,
            {"hced-Cevo1768-1", "hced-Podgoritza1712-1"},
        )
        for contract in lane.WAVE8_MONTENEGRO_1796_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_holds_preserve_source_contradictions_as_unknown_not_draws(self) -> None:
        cevo = lane.WAVE8_MONTENEGRO_1796_HOLDS["hced-Cevo1768-1"]
        podgoritza = lane.WAVE8_MONTENEGRO_1796_HOLDS[
            "hced-Podgoritza1712-1"
        ]
        self.assertEqual(
            cevo["reason_code"],
            "historically_contradictory_outcome_and_event_identity",
        )
        self.assertEqual(
            podgoritza["reason_code"],
            "historically_contradictory_outcome_and_event_identity",
        )
        self.assertIn("surrounded and defeated", cevo["audit_note"])
        self.assertIn("Venetian records", podgoritza["audit_note"])
        self.assertNotIn("draw", cevo["audit_note"].lower())
        self.assertNotIn("draw", podgoritza["audit_note"].lower())

    def test_entities_are_exactly_1796_bounded_and_open_no_generic_alias(self) -> None:
        entities = {
            str(item["id"]): item for item in lane.WAVE8_MONTENEGRO_1796_ENTITIES
        }
        self.assertEqual(set(entities), {MONTENEGRIN_FORCE, SCUTARI_FORCE})
        for entity in entities.values():
            self.assertEqual((entity["start_year"], entity["end_year"]), (1796, 1796))
            self.assertEqual(entity["aliases"], [])
            Entity.from_dict(entity)
        self.assertIn(
            "does not back-project later state institutions",
            entities[MONTENEGRIN_FORCE]["continuity_note"],
        )
        self.assertIn(
            "not every Ottoman unit",
            entities[SCUTARI_FORCE]["continuity_note"],
        )

    def test_sources_parse_and_each_result_has_independent_families(self) -> None:
        for source in lane.WAVE8_MONTENEGRO_1796_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_MONTENEGRO_1796_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 4)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_promoted_events_have_exact_actors_and_tactical_results(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS)
        expected_names = {
            "hced-Martinici1796-1": "Battle of Martinići",
            "hced-Krusi1796-1": "Battle of Krusi",
        }
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(event["name"], expected_names[candidate_id])
                self.assertEqual(event["year"], 1796)
                self.assertEqual(event["end_year"], 1796)
                self.assertEqual(event["date_precision"], "day")
                self.assertEqual(event["war_type"], "interstate")
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                winners = {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_victory"
                }
                losers = {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_defeat"
                }
                self.assertEqual(winners, {MONTENEGRIN_FORCE})
                self.assertEqual(losers, {SCUTARI_FORCE})
                Event.from_dict(event)

    def test_calendar_dates_are_explicit_and_not_collapsed(self) -> None:
        martinici = lane.WAVE8_MONTENEGRO_1796_CONTRACTS[
            "hced-Martinici1796-1"
        ]["canonical_event"]
        krusi = lane.WAVE8_MONTENEGRO_1796_CONTRACTS["hced-Krusi1796-1"][
            "canonical_event"
        ]
        self.assertEqual(
            martinici["date_text"],
            "11 July 1796 Old Style / 22 July 1796 New Style",
        )
        self.assertEqual(
            krusi["date_text"],
            "22 September 1796 Old Style / 3 October 1796 New Style",
        )

    def test_points_are_withheld_but_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Montenegro")
            self.assertIn("location_provenance", event)

    def test_existing_later_rows_and_mojkovac_are_not_reowned(self) -> None:
        reviewed = lane.WAVE8_MONTENEGRO_1796_RESERVED_IDS
        self.assertFalse(
            reviewed
            & {
                "hced-Fundina1876-1",
                "hced-Grahovo1858-1",
                "hced-Mojkovac1916-1",
                "hced-Ostrog1853-1",
                "hced-Rijeka1862-1",
                "hced-Vucji Do1876-1",
            }
        )
        released = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        }
        self.assertLessEqual(
            {
                "hced-Fundina1876-1",
                "hced-Grahovo1858-1",
                "hced-Ostrog1853-1",
                "hced-Rijeka1862-1",
                "hced-Vucji Do1876-1",
            },
            released,
        )
        self.assertNotIn("hced-Mojkovac1916-1", released)

    def test_current_release_artifacts_include_the_lane_exactly_once(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS
        ]
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS,
        )
        self.assertEqual(len(events), 2)
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in events)
        )
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Montenegro")
            self.assertIn("location_provenance", event)
            Event.from_dict(event)

        entity_ids = {
            str(item["id"]) for item in lane.WAVE8_MONTENEGRO_1796_ENTITIES
        }
        release_entities = {
            str(item["id"]): item for item in self.release_entities
        }
        self.assertLessEqual(entity_ids, set(release_entities))
        self.assertTrue(
            all(not release_entities[entity_id]["aliases"] for entity_id in entity_ids)
        )

        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        self.assertLessEqual(entity_ids, set(registry_entities))
        self.assertTrue(
            all(
                registry_entities[entity_id]["status"] == "rated"
                for entity_id in entity_ids
            )
        )

        promotion = self.release_metadata["promotion"]
        self.assertEqual(
            promotion["accepted_wave8_montenegro_1796_hced_events"],
            2,
        )
        self.assertEqual(
            promotion["wave8_montenegro_1796_candidate_ids"],
            sorted(lane.WAVE8_MONTENEGRO_1796_CONTRACT_IDS),
        )
        self.assertEqual(
            {item["candidate_id"] for item in promotion["wave8_montenegro_1796_holds"]},
            lane.WAVE8_MONTENEGRO_1796_HOLD_IDS,
        )
        self.assertEqual(
            promotion["wave8_montenegro_1796_final_audit_signature"],
            lane.WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE,
        )

        coverage = self.registry["coverage"]
        self.assertEqual(
            coverage["candidate_keyed_wave8_montenegro_1796_hced_events"],
            2,
        )
        self.assertEqual(coverage["rated_events"], len(self.release_events))
        self.assertEqual(coverage["registry_polities"], len(self.registry["entities"]))
        self.assertEqual(
            coverage["rated_entities"],
            len(
                {
                    participant["entity_id"]
                    for event in self.release_events
                    for participant in event["participants"]
                }
            ),
        )

    def test_queue_tampering_duplicates_and_massacre_drift_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in tampered if row.get("candidate_id") == "hced-Krusi1796-1"
        )
        target["winner_raw"] = "Scutari, Ottoman Empire"
        with self.assertRaises(ValueError):
            lane.validate_wave8_montenegro_1796_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in duplicated
                    if row.get("candidate_id") == "hced-Martinici1796-1"
                )
            )
        )
        with self.assertRaises(ValueError):
            lane.validate_wave8_montenegro_1796_queue_contracts(duplicated)

        massacre = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in massacre
            if row.get("candidate_id") == "hced-Martinici1796-1"
        )
        target["massacre_raw"] = "Massacre"
        with self.assertRaises(ValueError):
            lane.validate_wave8_montenegro_1796_queue_contracts(massacre)

    def test_duplicate_audit_is_zero_and_future_spelling_twins_fail_closed(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_montenegro_1796_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        future = [
            *copy.deepcopy(self.iwbd_rows),
            {"candidate_id": "iwbd-future", "batname": "Kruši", "batyear": 1796},
        ]
        with self.assertRaises(ValueError):
            lane.validate_wave8_montenegro_1796_integration_dispositions(
                self.hced_rows,
                future,
                existing,
            )

    def test_installers_and_candidate_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        lane.install_wave8_montenegro_1796_entities(entities)
        lane.install_wave8_montenegro_1796_sources(sources)
        events = lane.promote_wave8_montenegro_1796_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaises(ValueError):
            lane.promote_wave8_montenegro_1796_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_counts_cohorts_and_final_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_montenegro_1796_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 2,
                "new_entities": 2,
                "new_sources": 7,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_montenegro_1796_cohort_counts(),
            {"montenegro_scutari_campaigns_1796": 2, "source_critical_holds": 2},
        )
        self.assertEqual(
            lane.wave8_montenegro_1796_audit_signature(),
            "2bf96ff247ffa0a3c8eb78ed4b0f27f48836714d5f771992b97ac73d003ddf0d",
        )
        self.assertEqual(
            lane.wave8_montenegro_1796_audit_signature(),
            lane.WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
