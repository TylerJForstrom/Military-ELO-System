import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_egypt_forces as lane
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_egypt_forces_"


EXPECTED_ACTORS = {
    "hced-Alexandria1365-1": ({"peter_i_alexandria_crusade_force_1365"}, {"mamluk_alexandria_defenders_1365"}),
    "hced-Ascalon1247-1": ({"al_salih_ayyub_ascalon_siege_force_1247"}, {"frankish_ascalon_garrison_1247"}),
    "hced-Aussa1875-1": ({"afar_issa_awsa_defenders_1875"}, {"munzinger_awsa_expedition_1875"}),
    "hced-Dufile1888-1": ({"dufile_garrison_1888"}, {"umar_salih_dufile_force_1888"}),
    "hced-Megiddo-609-1": ({"necho_ii_megiddo_force_609_bce"}, {"josiah_judah_force_609_bce"}),
    "hced-Montgisard1177-1": ({"baldwin_iv_montgisard_force_1177"}, {"saladin_montgisard_campaign_force_1177"}),
    "hced-Nile-47-1": ({"caesarian_pergamene_nile_coalition_47_bce"}, {"ptolemy_xiii_nile_army_47_bce"}),
    "hced-Sinkat1884-1": ({"osman_digna_sinkat_force_1884"}, {"sinkat_egyptian_garrison_1884"}),
    "hced-al, Damietta1218-1219-1": ({"fifth_crusade_damietta_siege_host_1218_1219"}, {"ayyubid_damietta_garrison_1218_1219"}),
    "hced-Abu Ageila1967-1": ({"israeli_abu_ageila_force_1967"}, {"egyptian_abu_ageila_force_1967"}),
    "hced-Rafa1967-1": ({"israeli_rafah_force_1967"}, {"egyptian_rafah_force_1967"}),
    "hced-Gaza1967-1": ({"israeli_gaza_force_1967"}, {"egyptian_gaza_force_1967"}),
    "hced-Jebel Libni1967-1": ({"israeli_jebel_libni_force_1967"}, {"egyptian_jebel_libni_force_1967"}),
    "hced-Mitla Pass1967-1": ({"israeli_mitla_interdiction_force_1967"}, {"egyptian_mitla_retreat_force_1967"}),
    "hced-Bir Gafgafa1967-1": ({"israeli_bir_gafgafa_force_1967"}, {"egyptian_bir_gafgafa_force_1967"}),
    "hced-Chinese Farm1973-1": ({"israeli_chinese_farm_force_1973"}, {"egyptian_chinese_farm_defenders_1973"}),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8EgyptForcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.iwd_rows = _jsonl(ROOT / "data" / "review" / "iwd-1.21-candidates.jsonl")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.seed_entities = _json(ROOT / "data" / "seed" / "entities.json")
        cls.seed_events = _json(ROOT / "data" / "seed" / "events.json")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_EGYPT_FORCES_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_EGYPT_FORCES_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_egypt_forces_entities(entities)
        lane.install_wave8_egypt_forces_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_egypt_forces_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_signature_counts_cohorts_and_partition_are_exact(self):
        payload = {
            "adjacent_row_hashes": lane.WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES,
            "contracts": lane.WAVE8_EGYPT_FORCES_CONTRACTS,
            "country_quarantine_additions": sorted(lane.WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS),
            "current_release_event_audit": lane.WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT,
            "entities": lane.WAVE8_EGYPT_FORCES_ENTITIES,
            "exact_label_funnel_audit": lane.WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT,
            "exact_row_hashes": lane.WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES,
            "existing_release_dispositions": lane.WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS,
            "hced_twin_dispositions": lane.WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS,
            "holds": lane.WAVE8_EGYPT_FORCES_HOLDS,
            "identity_boundary_audit": lane.WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT,
            "iwbd_duplicate_dispositions": lane.WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS,
            "iwd_audit": lane.WAVE8_EGYPT_FORCES_IWD_AUDIT,
            "location_quarantine_reasons": lane.WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": lane.WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(lane.WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS),
            "sources": lane.WAVE8_EGYPT_FORCES_SOURCES,
            "terminal_exclusions": lane.WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(_canonical_json(payload).encode()).hexdigest()
        self.assertEqual(
            independent,
            "bb523b35e94b15c8d88c5f06f4c62161be9c6d18a25e86a538a675223be6949a",
        )
        self.assertEqual(independent, lane.WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(independent, lane.wave8_egypt_forces_audit_signature())
        self.assertEqual(
            lane.wave8_egypt_forces_counts(),
            {
                "adjacent_hced_rows": 38,
                "audited_current_release_events": 56,
                "audited_existing_identities": 18,
                "country_quarantine_additions": 2,
                "exact_label_rows": 58,
                "existing_release_dispositions": 31,
                "hced_same_event_twins": 0,
                "holds": 9,
                "iwbd_duplicate_dispositions": 20,
                "iwd_related_rows": 1,
                "new_entities": 32,
                "new_sources": 38,
                "newly_rated_events": 16,
                "outcome_overrides": 0,
                "point_quarantine_additions": 16,
                "promotion_contracts": 16,
                "reviewed_hced_rows": 58,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(
            lane.wave8_egypt_forces_cohort_counts(),
            {
                "ancient_chronology": 3,
                "ancient_duplicate_conflict": 1,
                "ancient_egypt": 1,
                "equatoria_expeditionary": 1,
                "fifth_crusade": 1,
                "hellenistic_chronology": 2,
                "khedival_periphery": 2,
                "mahdist_war": 2,
                "medieval_egypt": 3,
                "ptolemaic_civil_war": 1,
                "six_day_war_sinai": 6,
                "yom_kippur_war_sinai": 4,
            },
        )

        partitions = (
            lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS,
            lane.WAVE8_EGYPT_FORCES_HOLD_IDS,
            lane.WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS,
            frozenset(lane.WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
        )
        self.assertEqual(frozenset().union(*partitions), lane.WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS)
        for i in range(len(partitions)):
            for j in range(i + 1, len(partitions)):
                self.assertFalse(partitions[i] & partitions[j])

    def test_all_58_literal_rows_and_funnel_projection_are_pinned(self):
        result = lane.validate_wave8_egypt_forces_queue_contracts(self.hced_rows)
        self.assertEqual(
            result,
            {
                "adjacent_hced_rows": 38,
                "exact_label_rows": 58,
                "existing_release_dispositions": 31,
                "holds": 9,
                "promotion_contracts": 16,
                "reviewed_hced_rows": 58,
                "terminal_exclusions": 2,
            },
        )
        exact = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Egypt" or row.get("side_2_raw") == "Egypt"
        }
        self.assertEqual(set(exact), lane.WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS)
        for candidate_id, expected_hash in lane.WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES.items():
            self.assertEqual(canonical_hced_row_sha256(exact[candidate_id]), expected_hash)

        mapping_digest = hashlib.sha256(
            _canonical_json(lane.WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES).encode()
        ).hexdigest()
        self.assertEqual(
            mapping_digest,
            lane.WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT["exact_row_hash_mapping_sha256"],
        )
        funnel_record = next(
            item for item in self.funnel["labels"] if item["label"] == "egypt"
        )
        self.assertEqual(funnel_record["events_touched"], 13)
        self.assertEqual(funnel_record["unresolved_side_attempts"], 13)
        self.assertEqual(
            funnel_record["event_candidate_id_sha256"],
            lane.WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT["event_candidate_id_sha256"],
        )

        tampered = copy.deepcopy(self.hced_rows)
        row = next(item for item in tampered if item["candidate_id"] == "hced-Abu Ageila1967-1")
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed|exact row fingerprint"):
            lane.validate_wave8_egypt_forces_queue_contracts(tampered)

        duplicate = copy.deepcopy(self.hced_rows)
        duplicate.append(copy.deepcopy(exact["hced-Abu Ageila1967-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one|expected once"):
            lane.validate_wave8_egypt_forces_queue_contracts(duplicate)

    def test_38_adjacent_rows_and_zero_same_event_hced_twins_fail_closed(self):
        adjacent = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if "Egypt" not in {row.get("side_1_raw"), row.get("side_2_raw")}
            and any(
                "egypt" in str(value or "").casefold()
                for value in (row.get("side_1_raw"), row.get("side_2_raw"))
            )
        }
        self.assertEqual(set(adjacent), set(lane.WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES))
        for candidate_id, expected_hash in lane.WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES.items():
            self.assertEqual(canonical_hced_row_sha256(adjacent[candidate_id]), expected_hash)
        self.assertEqual(lane.WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS, {})

        tampered = copy.deepcopy(self.hced_rows)
        row = next(item for item in tampered if item["candidate_id"] == "hced-Alexandria1798-1")
        row["side_2_raw"] += " changed"
        with self.assertRaisesRegex(ValueError, "adjacent row fingerprint changed"):
            lane.validate_wave8_egypt_forces_queue_contracts(tampered)

        future_twin = copy.deepcopy(self.hced_rows)
        future_twin.append(
            {
                "candidate_id": "hced-future-Chinese-Farm-1973",
                "name": "Chinese Farm",
                "year_low": 1973,
                "year_high": 1973,
                "year_best": 1973,
                "side_1_raw": "Israel",
                "side_2_raw": "Arab Republic",
            }
        )
        with self.assertRaisesRegex(ValueError, "same-event twin"):
            lane.validate_wave8_egypt_forces_queue_contracts(future_twin)

    def test_sources_and_event_bounded_entities_are_valid_and_exactly_used(self):
        sources = {str(item["id"]): item for item in lane.WAVE8_EGYPT_FORCES_SOURCES}
        self.assertEqual(len(sources), 38)
        self.assertEqual(len({item["source_family_id"] for item in sources.values()}), 38)
        used_sources = set()
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))

        entities = {str(item["id"]): item for item in lane.WAVE8_EGYPT_FORCES_ENTITIES}
        self.assertEqual(len(entities), 32)
        used_entities = set()
        for entity in entities.values():
            Entity.from_dict(entity)
            self.assertTrue(entity["kind"].startswith("event_bounded_"))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertIn("generic egypt", entity["continuity_note"].casefold())
            used_sources.update(entity["source_ids"])
        self.assertNotIn("egypt", entities)

        for contract in lane.WAVE8_EGYPT_FORCES_CONTRACTS.values():
            low = contract["canonical_event"]["year_low"]
            high = contract["canonical_event"]["year_high"]
            actor_ids = [*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]]
            used_entities.update(actor_ids)
            for entity_id in actor_ids:
                self.assertEqual(
                    (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                    (low, high),
                )
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", sources[source_id]["evidence_roles"])
            used_sources.update(contract["evidence_refs"])
        for item in lane.WAVE8_EGYPT_FORCES_NONPROMOTIONS.values():
            used_sources.update(item["evidence_refs"])
        self.assertEqual(used_entities, set(entities))
        self.assertEqual(used_sources, set(sources))

    def test_holds_are_unknown_not_draw_and_exclusions_have_proof(self):
        self.assertEqual(len(lane.WAVE8_EGYPT_FORCES_HOLDS), 9)
        self.assertEqual(len(lane.WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS), 2)
        for item in lane.WAVE8_EGYPT_FORCES_NONPROMOTIONS.values():
            self.assertFalse(
                {"result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids"}
                & set(item)
            )
            self.assertTrue(item["evidence_refs"])
        self.assertEqual(
            lane.WAVE8_EGYPT_FORCES_HOLDS["hced-Suez Canal (2nd)1973-1"]["disposition"],
            "hold",
        )
        self.assertIn(
            "not converted into a rating",
            lane.WAVE8_EGYPT_FORCES_HOLDS["hced-Suez Canal (2nd)1973-1"]["hold_reason"],
        )
        kadesh = lane.WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS["hced-Kadesh-1275-1"]
        self.assertEqual(
            kadesh["duplicate_ownership"]["existing_owner_event_id"],
            "battle_kadesh_1274_bce",
        )
        self.assertIn("inconclusive", kadesh["hold_reason"])
        tokar = lane.WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS["hced-Tokar1883-1"]
        self.assertIn("annihilated", tokar["hold_reason"])
        self.assertEqual(lane.WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES, {})
        for contract in lane.WAVE8_EGYPT_FORCES_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_all_16_promotions_are_parseable_local_wins_with_unique_formations(self):
        events = self._events()
        self.assertEqual(len(events), 16)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_ACTORS))
        all_actor_ids = set()
        for candidate_id, (winners, losers) in EXPECTED_ACTORS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            actual_winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_victory"
            }
            actual_losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_defeat"
            }
            self.assertEqual(actual_winners, winners)
            self.assertEqual(actual_losers, losers)
            self.assertEqual(
                {item["termination"] for item in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )
            all_actor_ids.update(actual_winners | actual_losers)
        self.assertEqual(len(all_actor_ids), 32)
        self.assertEqual(
            by_candidate["hced-al, Damietta1218-1219-1"]["end_year"],
            1219,
        )
        chinese_farm_ids = {
            item["entity_id"]
            for item in by_candidate["hced-Chinese Farm1973-1"]["participants"]
        }
        self.assertNotIn("clio_eg_egypt_modern_2_1973_e01853c2", chinese_farm_ids)
        six_day_ids = {
            item["entity_id"]
            for candidate_id, event in by_candidate.items()
            if candidate_id.endswith("1967-1")
            for item in event["participants"]
        }
        self.assertEqual(len(six_day_ids), 12)
        self.assertTrue(all("1967" in entity_id for entity_id in six_day_ids))

    def test_location_quarantine_is_local_complete_and_nonmutating(self):
        before_point_object = HCED_POINT_QUARANTINE_IDS
        before_country_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        row_by_id = {str(row["candidate_id"]): row for row in self.hced_rows}

        self.assertEqual(
            lane.WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS,
        )
        self.assertEqual(
            lane.WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Aussa1875-1", "hced-Dufile1888-1"},
        )
        self.assertEqual(
            lane.wave8_egypt_forces_location_quarantine_additions(),
            {
                "country": frozenset({"hced-Aussa1875-1", "hced-Dufile1888-1"}),
                "point": lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS,
            },
        )
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            if candidate_id in lane.WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
                self.assertNotIn("modern_location_country", event)
                self.assertNotIn("location_provenance", event)
            else:
                self.assertEqual(
                    event["modern_location_country"],
                    row_by_id[candidate_id]["modern_location_country"],
                )
                self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_point_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_country_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_all_existing_identity_and_event_boundaries_are_pinned(self):
        self.assertEqual(
            lane.validate_wave8_egypt_forces_identity_boundaries(
                self.seed_entities,
                self.release_entities,
                self.seed_events,
                self.release_events,
            ),
            {
                "audited_release_entities": 18,
                "audited_release_events": 56,
                "audited_seed_entities": 3,
                "audited_seed_events": 2,
                "existing_1967_identity_candidates": 0,
            },
        )
        release_by_id = {str(item["id"]): item for item in self.release_entities}
        audited = lane.WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["release_entities"]
        self.assertFalse(
            {
                entity_id
                for entity_id in audited
                if release_by_id[entity_id]["start_year"] <= 1967
                <= release_by_id[entity_id]["end_year"]
            }
        )
        event_by_id = {str(item["id"]): item for item in self.release_events}
        self.assertEqual(
            {item["termination"] for item in event_by_id["battle_kadesh_1274_bce"]["participants"]},
            {"inconclusive"},
        )
        self.assertIn(
            "clio_eg_egypt_modern_2_1973_e01853c2",
            {item["entity_id"] for item in event_by_id["iwd_war_70_yom_kippur_1973"]["participants"]},
        )

        changed_entities = copy.deepcopy(self.release_entities)
        entity = next(item for item in changed_entities if item["id"] == "clio_eg_egypt_modern_2_1953_a888d535")
        entity["end_year"] = 1967
        with self.assertRaisesRegex(ValueError, "identity window drifted"):
            lane.validate_wave8_egypt_forces_identity_boundaries(
                self.seed_entities,
                changed_entities,
                self.seed_events,
                self.release_events,
            )

        changed_events = copy.deepcopy(self.release_events)
        event = next(item for item in changed_events if item["id"] == "battle_kadesh_1274_bce")
        event["participants"][0]["entity_id"] = "clio_eg_egypt_modern_2_1973_e01853c2"
        with self.assertRaisesRegex(ValueError, "release event projection drifted"):
            lane.validate_wave8_egypt_forces_identity_boundaries(
                self.seed_entities,
                self.release_entities,
                self.seed_events,
                changed_events,
            )

    def test_iwbd_iwd_and_current_release_duplicate_audits_fail_closed(self):
        current_overlap = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS
        }
        self.assertIn(
            current_overlap,
            (set(), set(lane.WAVE8_EGYPT_FORCES_CONTRACT_IDS)),
        )
        self.assertEqual(
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
                self.iwd_rows,
            ),
            {
                "existing_release_dispositions": 31,
                "hced_same_event_twins": 0,
                "iwbd_duplicate_dispositions": 20,
                "iwd_related_rows": 1,
                "release_lane_overlap": len(current_overlap),
            },
        )
        released_iwbd = {
            str(event["iwbd_candidate_id"])
            for event in self.release_events
            if event.get("iwbd_candidate_id")
        }
        self.assertFalse(released_iwbd & set(lane.WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS))
        self.assertFalse(
            [event for event in self.release_events if str(event.get("iwd_parent_war_id") or "") == "64"]
        )

        changed_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(item for item in changed_iwbd if item["candidate_id"] == "iwbd-169-64-1524")
        row["review_status"] = "changed"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint changed"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, changed_iwbd, self.release_events, self.iwd_rows
            )

        future_iwbd = copy.deepcopy(self.iwbd_rows)
        row = copy.deepcopy(next(item for item in future_iwbd if item["candidate_id"] == "iwbd-169-64-1524"))
        row["candidate_id"] = "iwbd-future-abu-ageila"
        future_iwbd.append(row)
        with self.assertRaisesRegex(ValueError, "IWBD exact twin inventory drifted"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, future_iwbd, self.release_events, self.iwd_rows
            )

        changed_iwd = copy.deepcopy(self.iwd_rows)
        row = next(item for item in changed_iwd if item["candidate_id"] == "iwd-195")
        row["extraction_notes"].append("changed")
        with self.assertRaisesRegex(ValueError, "IWD iwd-195 fingerprint changed"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, self.release_events, changed_iwd
            )

    def test_release_integration_is_all_or_none_and_preserves_single_owners(self):
        promoted = self._events()
        _, _, base_release = self._installed()
        full_release = [*copy.deepcopy(base_release), *copy.deepcopy(promoted)]
        result = lane.validate_wave8_egypt_forces_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            full_release,
            self.iwd_rows,
        )
        self.assertEqual(result["release_lane_overlap"], 16)

        partial = [*copy.deepcopy(base_release), copy.deepcopy(promoted[0])]
        with self.assertRaisesRegex(ValueError, "partial release integration"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, partial, self.iwd_rows
            )

        held = [
            *copy.deepcopy(full_release),
            {
                "id": "bad_held_egypt_event",
                "name": "Masindi",
                "year": 1872,
                "hced_candidate_id": "hced-Masindi1872-1",
                "participants": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "hold or exclusion entered release"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, held, self.iwd_rows
            )

        twin = [
            *copy.deepcopy(full_release),
            {
                "id": "bad_chinese_farm_twin",
                "name": "Chinese Farm",
                "aliases": [],
                "year": 1973,
                "participants": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_egypt_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, twin, self.iwd_rows
            )

    def test_installers_are_idempotent_and_promoter_rejects_collisions_and_bad_windows(self):
        entities, sources, existing = self._installed()
        entities_before = copy.deepcopy(entities)
        sources_before = copy.deepcopy(sources)
        lane.install_wave8_egypt_forces_entities(entities)
        lane.install_wave8_egypt_forces_sources(sources)
        self.assertEqual(entities, entities_before)
        self.assertEqual(sources, sources_before)

        bad_entities = copy.deepcopy(entities)
        entity_id = lane.WAVE8_EGYPT_FORCES_ENTITIES[0]["id"]
        bad_entities[entity_id]["name"] += " changed"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_egypt_forces_entities(bad_entities)

        bad_sources = copy.deepcopy(sources)
        source_id = lane.WAVE8_EGYPT_FORCES_SOURCES[0]["id"]
        bad_sources[source_id]["title"] += " changed"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_egypt_forces_sources(bad_sources)

        promoted = lane.promote_wave8_egypt_forces_contracts(
            self.hced_rows, entities, existing
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_egypt_forces_contracts(
                self.hced_rows, entities, [*existing, *promoted]
            )

        bad_window = copy.deepcopy(entities)
        bad_window["egyptian_abu_ageila_force_1967"]["end_year"] = 1966
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_egypt_forces_contracts(
                self.hced_rows, bad_window, existing
            )


if __name__ == "__main__":
    unittest.main()
