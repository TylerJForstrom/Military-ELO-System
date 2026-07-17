import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_epirus import (
    WAVE8_EPIRUS_CONTRACT_IDS,
    WAVE8_EPIRUS_CONTRACTS,
    WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS,
    WAVE8_EPIRUS_ENTITIES,
    WAVE8_EPIRUS_EXCLUSION_IDS,
    WAVE8_EPIRUS_EXCLUSIONS,
    WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS,
    WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE,
    WAVE8_EPIRUS_HOLD_IDS,
    WAVE8_EPIRUS_HOLDS,
    WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS,
    WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_EPIRUS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS,
    WAVE8_EPIRUS_OUTCOME_OVERRIDES,
    WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_EPIRUS_RESERVED_IDS,
    WAVE8_EPIRUS_SOURCES,
    install_wave8_epirus_entities,
    install_wave8_epirus_sources,
    promote_wave8_epirus_contracts,
    validate_wave8_epirus_integration_dispositions,
    validate_wave8_epirus_queue_contracts,
    wave8_epirus_audit_signature,
    wave8_epirus_cohort_counts,
    wave8_epirus_counts,
    wave8_epirus_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_epirus_"
PYRRHUS_ID = "pyrrhus_epirote_kingdom_297_272_bce"
ALEXANDER_ID = "alexander_i_epirote_kingdom_343_331_bce"
PANDOSIA_COALITION_ID = "lucanian_bruttian_pandosia_coalition_331_bce"
ARGOS_COALITION_ID = "argos_antigonid_spartan_defensive_coalition_272_bce"
THEODORE_ID = "theodore_komnenos_doukas_epirote_state_1215_1230"
LATIN_THESSALONICA_ID = "latin_kingdom_thessalonica_1204_1224"

EXPECTED_RAW_HASHES = {
    "hced-Argos-272-1": "57cfcdfd5a555caec0e8fe2710aa609eec702a0a66757d30263af3bba4242075",
    "hced-Asculum, Apulia-279-1": "a8647fa5b3bdef7af84a1dab2b1536dde43efc7f62cf241f5a7825d2a4245185",
    "hced-Beneventum-275-1": "1966261b413a4184e045a541bbaa6b3101843a6a33b13051d0630cad96fcd84d",
    "hced-Heraclea, Lucania-280-1": "caacbafa2e0bb60e28a4d02cfb16696ae04e2c426a6440a40a644aad73613f49",
    "hced-Lilybaeum-277-1": "b5a3431d7bbfa4e40d1658784b9e3e2bbc32f9e2605f752a8c2683cc3f15aba7",
    "hced-Pandosia-331-1": "2f6f7c4692aa647a8d4929a9f2ced4f8b5b3abd47f6cdd0fa91618799b768122",
    "hced-Thessalonica1224-1": "8573d4e988fd0d3c151f161ac51d3db7b5043ad825ee269066feb3065f51433b",
    "hced-Thessalonica1264-1": "d886ca74fb2dc085ffcc715f75fd6d8413d60bc808666681bb495000bbbb65c4",
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Pandosia-331-1": ({PANDOSIA_COALITION_ID}, {ALEXANDER_ID}),
    "hced-Heraclea, Lucania-280-1": ({PYRRHUS_ID}, {"roman_republic"}),
    "hced-Asculum, Apulia-279-1": ({PYRRHUS_ID}, {"roman_republic"}),
    "hced-Beneventum-275-1": ({"roman_republic"}, {PYRRHUS_ID}),
    "hced-Argos-272-1": ({ARGOS_COALITION_ID}, {PYRRHUS_ID}),
    "hced-Thessalonica1224-1": ({THEODORE_ID}, {LATIN_THESSALONICA_ID}),
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Wave8EpirusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _load_jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _load_jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = json.loads(
            (ROOT / "build/hced-unresolved-label-funnel.json").read_text(encoding="utf-8")
        )
        cls.release_entities = {
            str(entity["id"]): entity
            for entity in json.loads((ROOT / "data/release/entities.json").read_text(encoding="utf-8"))
        }
        cls.release_events = json.loads((ROOT / "data/release/events.json").read_text(encoding="utf-8"))
        cls.release_metadata = json.loads(
            (ROOT / "data/release/metadata.json").read_text(encoding="utf-8")
        )
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if str(row.get("candidate_id")) in WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS
        ]

    def _installed(self) -> tuple[dict, dict, list]:
        lane_entity_ids = {str(entity["id"]) for entity in WAVE8_EPIRUS_ENTITIES}
        entities = {
            entity_id: copy.deepcopy(entity)
            for entity_id, entity in self.release_entities.items()
            if entity_id not in lane_entity_ids
        }
        sources: dict[str, dict] = {}
        install_wave8_epirus_entities(entities)
        install_wave8_epirus_sources(sources)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_EPIRUS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_epirus_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def _emit(self) -> tuple[dict, dict, list]:
        entities, sources, existing = self._installed()
        return (
            entities,
            sources,
            promote_wave8_epirus_contracts(self.hced_rows, entities, existing),
        )

    def test_exact_eight_row_inventory_hashes_and_counts(self) -> None:
        self.assertEqual(len(self.lane_rows), 8)
        self.assertEqual(WAVE8_EPIRUS_RESERVED_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_EPIRUS_CONTRACT_IDS | WAVE8_EPIRUS_HOLD_IDS, set(EXPECTED_RAW_HASHES))
        self.assertFalse(WAVE8_EPIRUS_CONTRACT_IDS & WAVE8_EPIRUS_HOLD_IDS)
        self.assertEqual(WAVE8_EPIRUS_EXCLUSION_IDS, WAVE8_EPIRUS_HOLD_IDS)
        self.assertIs(WAVE8_EPIRUS_EXCLUSIONS, WAVE8_EPIRUS_HOLDS)

        by_id = {str(row["candidate_id"]): row for row in self.lane_rows}
        self.assertEqual(set(by_id), set(EXPECTED_RAW_HASHES))
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(canonical_hced_row_sha256(by_id[candidate_id]), expected_hash)

        self.assertEqual(
            validate_wave8_epirus_queue_contracts(self.hced_rows),
            {"promotion_contracts": 6, "holds": 2, "reviewed_hced_rows": 8},
        )
        self.assertEqual(
            wave8_epirus_counts(),
            {
                "country_quarantine_additions": 1,
                "cross_lane_hced_dispositions": 0,
                "exclusions": 2,
                "existing_release_duplicate_dispositions": 0,
                "holds": 2,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 6,
                "new_sources": 10,
                "newly_rated_events": 6,
                "outcome_overrides": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 8,
            },
        )
        self.assertEqual(
            wave8_epirus_cohort_counts(),
            {
                "alexander_i_south_italy_331_bce": 1,
                "epirote_latin_war_1215_1224": 1,
                "pyrrhic_war_280_275_bce": 3,
                "pyrrhus_peloponnese_campaign_272_bce": 1,
            },
        )

    def test_semantic_signature_is_pinned_and_sha256_shaped(self) -> None:
        self.assertEqual(
            WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE,
            "95886e660a445c7f982f340e7d4b612104aefe84b4943a3c50f0ed4227be08de",
        )
        self.assertEqual(wave8_epirus_audit_signature(), WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(len(bytes.fromhex(WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE)), 32)
        self.assertEqual(
            hashlib.sha256(bytes.fromhex(WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE)).digest_size,
            32,
        )

    def test_sources_and_entities_are_parseable_bounded_and_non_generic(self) -> None:
        self.assertEqual(len(WAVE8_EPIRUS_SOURCES), 10)
        self.assertEqual(len(WAVE8_EPIRUS_ENTITIES), 6)
        source_ids = {str(source["id"]) for source in WAVE8_EPIRUS_SOURCES}
        source_families = {str(source["source_family_id"]) for source in WAVE8_EPIRUS_SOURCES}
        self.assertEqual(len(source_ids), 10)
        self.assertEqual(len(source_families), 10)
        for source in WAVE8_EPIRUS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))

        expected_windows = {
            ALEXANDER_ID: (-343, -331),
            PANDOSIA_COALITION_ID: (-331, -331),
            PYRRHUS_ID: (-297, -272),
            ARGOS_COALITION_ID: (-272, -272),
            THEODORE_ID: (1215, 1230),
            LATIN_THESSALONICA_ID: (1204, 1224),
        }
        by_id = {str(entity["id"]): entity for entity in WAVE8_EPIRUS_ENTITIES}
        self.assertEqual(set(by_id), set(expected_windows))
        for entity_id, entity in by_id.items():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity_id],
            )
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
            self.assertNotEqual(entity["name"].casefold(), "epirus")

    def test_ancient_pyrrhus_alexander_and_medieval_epirus_never_bridge(self) -> None:
        contracts = WAVE8_EPIRUS_CONTRACTS
        self.assertEqual(contracts["hced-Pandosia-331-1"]["side_2_entity_ids"], [ALEXANDER_ID])
        for candidate_id in (
            "hced-Heraclea, Lucania-280-1",
            "hced-Asculum, Apulia-279-1",
            "hced-Beneventum-275-1",
            "hced-Argos-272-1",
        ):
            sides = set(contracts[candidate_id]["side_1_entity_ids"]) | set(
                contracts[candidate_id]["side_2_entity_ids"]
            )
            self.assertIn(PYRRHUS_ID, sides)
            self.assertNotIn(ALEXANDER_ID, sides)
            self.assertNotIn(THEODORE_ID, sides)
        medieval_sides = set(contracts["hced-Thessalonica1224-1"]["side_1_entity_ids"]) | set(
            contracts["hced-Thessalonica1224-1"]["side_2_entity_ids"]
        )
        self.assertEqual(medieval_sides, {THEODORE_ID, LATIN_THESSALONICA_ID})
        self.assertFalse({ALEXANDER_ID, PYRRHUS_ID} & medieval_sides)

    def test_contract_dates_actors_outcomes_and_provenance_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_EPIRUS_SOURCES}
        expected_years = {
            "hced-Pandosia-331-1": -331,
            "hced-Heraclea, Lucania-280-1": -280,
            "hced-Asculum, Apulia-279-1": -279,
            "hced-Beneventum-275-1": -275,
            "hced-Argos-272-1": -272,
            "hced-Thessalonica1224-1": 1224,
        }
        for candidate_id, contract in WAVE8_EPIRUS_CONTRACTS.items():
            self.assertEqual(contract["canonical_event"]["year_low"], expected_years[candidate_id])
            self.assertEqual(contract["canonical_event"]["year_high"], expected_years[candidate_id])
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"]))
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
        self.assertEqual(
            WAVE8_EPIRUS_CONTRACTS["hced-Thessalonica1224-1"]["canonical_event"]["granularity"],
            "siege",
        )
        self.assertEqual(WAVE8_EPIRUS_OUTCOME_OVERRIDES, {})

    def test_lilybaeum_and_thessalonica_1264_are_terminal_nonrated_holds(self) -> None:
        self.assertEqual(
            set(WAVE8_EPIRUS_HOLDS),
            {"hced-Lilybaeum-277-1", "hced-Thessalonica1264-1"},
        )
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        for hold in WAVE8_EPIRUS_HOLDS.values():
            self.assertTrue(forbidden.isdisjoint(hold))
            self.assertIn("never a draw", hold["hold_reason"].casefold())
        lily = WAVE8_EPIRUS_HOLDS["hced-Lilybaeum-277-1"]
        self.assertEqual(lily["canonical_event"]["date_text"], "late 277 or 276 BCE")
        self.assertEqual(lily["hold_category"], "event_year_not_uniquely_defensible")
        thess = WAVE8_EPIRUS_HOLDS["hced-Thessalonica1264-1"]
        self.assertEqual(
            thess["hold_category"],
            "named_engagement_not_attested_by_reviewed_sources",
        )
        self.assertIn("not a distinct battle at Thessalonica", thess["hold_reason"])

    def test_emission_is_six_parseable_wins_without_generic_epirus_or_draws(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 6)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertFalse(WAVE8_EPIRUS_HOLD_IDS & set(by_candidate))
        for candidate_id, (expected_winners, expected_losers) in EXPECTED_WINNERS_AND_LOSERS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_defeat"
            }
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            self.assertNotIn("epirus", winners | losers)
            terminations = {item["termination"] for item in event["participants"]}
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            contract = WAVE8_EPIRUS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

    def test_asculum_remains_a_win_not_a_draw_and_actor_corrections_are_explicit(self) -> None:
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        asculum = by_candidate["hced-Asculum, Apulia-279-1"]
        self.assertEqual(
            {p["entity_id"] for p in asculum["participants"] if p["termination"] == "engagement_victory"},
            {PYRRHUS_ID},
        )
        argos = WAVE8_EPIRUS_CONTRACTS["hced-Argos-272-1"]
        self.assertEqual(argos["side_1_entity_ids"], [ARGOS_COALITION_ID])
        thess = WAVE8_EPIRUS_CONTRACTS["hced-Thessalonica1224-1"]
        self.assertEqual(thess["side_2_entity_ids"], [LATIN_THESSALONICA_ID])
        self.assertNotIn("kingdom of thessaly", " ".join(thess["side_2_entity_ids"]))

    def test_location_quarantine_is_promoted_only_and_does_not_mutate_globals(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}

        self.assertEqual(WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS, WAVE8_EPIRUS_CONTRACT_IDS)
        self.assertEqual(WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS, {"hced-Argos-272-1"})
        self.assertEqual(set(WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS), WAVE8_EPIRUS_CONTRACT_IDS)
        self.assertEqual(
            WAVE8_EPIRUS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_EPIRUS_CONTRACT_IDS,
                "country": frozenset({"hced-Argos-272-1"}),
            },
        )
        self.assertEqual(
            wave8_epirus_location_quarantine_additions(),
            {
                "point": WAVE8_EPIRUS_CONTRACT_IDS,
                "country": frozenset({"hced-Argos-272-1"}),
            },
        )
        for event in events:
            self.assertNotIn("geometry", event)
        self.assertNotIn("modern_location_country", by_candidate["hced-Argos-272-1"])
        for candidate_id in WAVE8_EPIRUS_CONTRACT_IDS - {"hced-Argos-272-1"}:
            self.assertIn("modern_location_country", by_candidate[candidate_id])
            self.assertIn("location_provenance", by_candidate[candidate_id])
        self.assertTrue(WAVE8_EPIRUS_HOLD_IDS.isdisjoint(WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS))
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_duplicate_audits_are_zero_and_fail_closed_on_future_twins(self) -> None:
        self.assertEqual(WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(len(WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT), 8)
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_epirus_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-Argos-272",
                "name": "Battle of Argos",
                "year_best": -272,
                "side_1_raw": "Argos",
                "side_2_raw": "Macedonia",
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_epirus_integration_dispositions(hced_twin, self.iwbd_rows)

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {"candidate_id": "iwbd-future-heraclea", "name": "Battle of Heraclea", "year": -280}
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_epirus_integration_dispositions(self.hced_rows, iwbd_twin)

        release_twin = [
            *existing,
            {"id": "future-thessalonica-twin", "name": "Thessalonica", "year": 1224},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_epirus_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_completed_lane_is_resolved_out_of_the_live_funnel(self) -> None:
        self.assertFalse(
            any(
                row.get("label") == "epirus"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Epirus lane must not remain unresolved",
        )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        integrated = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        if not self._is_integrated():
            self.assertFalse(integrated)
            return

        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            set(WAVE8_EPIRUS_CONTRACT_IDS),
        )
        self.assertEqual(len({event["id"] for event in integrated}), 6)
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in integrated)
        )
        release_candidate_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        }
        self.assertFalse(
            WAVE8_EPIRUS_HOLD_IDS & release_candidate_ids,
            "terminal Epirus holds must never reach the release",
        )
        self.assertLessEqual(
            {str(entity["id"]) for entity in WAVE8_EPIRUS_ENTITIES},
            set(self.release_entities),
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_epirus_hced_events"], 6)
        self.assertEqual(
            promotion["wave8_epirus_candidate_ids"],
            sorted(WAVE8_EPIRUS_CONTRACT_IDS),
        )

    def test_raw_row_tamper_entity_window_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(row for row in tampered if row.get("candidate_id") == "hced-Argos-272-1")
        row["winner_raw"] = "Epirus"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_epirus_queue_contracts(tampered)

        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short[PYRRHUS_ID]["end_year"] = -276
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_epirus_contracts(self.hced_rows, short, existing)

        events = promote_wave8_epirus_contracts(self.hced_rows, entities, existing)
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_epirus_contracts(self.hced_rows, entities, [*existing, events[0]])

    def test_installers_fail_on_collisions_and_do_not_alias_inputs(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_epirus_entities(entities)
        install_wave8_epirus_sources(sources)
        entities[PYRRHUS_ID]["name"] = "tampered"
        sources["wave8_epirus_cambridge_pyrrhus"]["title"] = "tampered"
        self.assertNotEqual(
            entities[PYRRHUS_ID]["name"],
            next(e["name"] for e in WAVE8_EPIRUS_ENTITIES if e["id"] == PYRRHUS_ID),
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_epirus_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_epirus_sources(sources)


if __name__ == "__main__":
    unittest.main()
