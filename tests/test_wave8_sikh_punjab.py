import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_sikh_punjab as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_sikh_punjab_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "9595b3b15abf30ad7649c48b4959eeca9a2361a21bc99876acb9fe7c0c67e929"
)
FINAL_AUDIT_SIGNATURE = (
    "e9ed6765d051daa426bf9de099f4126be176d97457a3a2c7461ceda3a06909cb"
)

AMRITSAR_SIKH_ID = "guru_hargobind_akal_sena_amritsar_1634"
AMRITSAR_MUGHAL_ID = "mukhlis_khan_mughal_expedition_amritsar_1634"
BADDOWAL_SIKH_ID = "ranjodh_ajit_khalsa_field_force_baddowal_1846"
BADDOWAL_BRITISH_INDIAN_ID = (
    "harry_smith_british_indian_relief_column_baddowal_1846"
)
GUJRAT_SIKH_ID = "ram_singh_bedi_sikh_misl_coalition_gujrat_1797"
GUJRAT_DURRANI_ID = "shahanchibashi_durrani_field_force_gujrat_1797"
GURDAS_MUGHAL_ID = "mughal_imperial_siege_coalition_gurdas_nangal_1715"
GURDAS_SIKH_ID = "banda_singh_sikh_garrison_gurdas_nangal_1715"

ANANDPUR_1700_ID = "hced-Anandpur1700-1"
ANANDPUR_1700_HASH = (
    "3f992b5f13d444a3178aab638c90b8a7fd465615d6b8c6cc9f1fa95bf6146590"
)

EXPECTED_RAW_HASHES = {
    "hced-Amritsar1634-1": (
        "cdd8d1bbe8184a53ea8e5d9058db7492ea3151b1679c491a30b587aaa46e0be0"
    ),
    "hced-Anandpur1701-1": (
        "f67a4c4086cc928cdf58b7e704691a5f593035460d03011d684f5d2e82173e0e"
    ),
    "hced-Baddowal1846-1": (
        "afddca7611c520558de29a1c545e089f1efd688ba8e4b84ca56989f8c838e6f4"
    ),
    "hced-Gujrat, Pakistan1797-1": (
        "882db3889fa7363e0a8a6eed1a012a0dcfbf13352ac500e59046a82fb7fcffc5"
    ),
    "hced-Gurdas Nangal1715-1": (
        "5598e77f7b5c04fb0685fbbb7dfedfda64f84feda3f45e273350373edbe1ce5e"
    ),
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Amritsar1634-1": ({AMRITSAR_SIKH_ID}, {AMRITSAR_MUGHAL_ID}),
    "hced-Baddowal1846-1": (
        {BADDOWAL_SIKH_ID},
        {BADDOWAL_BRITISH_INDIAN_ID},
    ),
    "hced-Gujrat, Pakistan1797-1": ({GUJRAT_SIKH_ID}, {GUJRAT_DURRANI_ID}),
    "hced-Gurdas Nangal1715-1": ({GURDAS_MUGHAL_ID}, {GURDAS_SIKH_ID}),
}

EXPECTED_CANONICAL = {
    "hced-Amritsar1634-1": (
        "Battle of Amritsar (1634)",
        1634,
        "14 April 1634",
        "day",
        "engagement",
    ),
    "hced-Gurdas Nangal1715-1": (
        "Siege of Gurdas Nangal",
        1715,
        "beginning of April-7 December 1715",
        "month_to_day_range",
        "siege",
    ),
    "hced-Gujrat, Pakistan1797-1": (
        "Battle of Gujrat (1797)",
        1797,
        "three-day battle ending 29 April 1797",
        "day_range",
        "engagement",
    ),
    "hced-Baddowal1846-1": (
        "Action at Baddowal",
        1846,
        "21 January 1846",
        "day",
        "engagement",
    ),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8SikhPunjabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "sikh punjab"
            or normalize_label(row.get("side_2_raw")) == "sikh punjab"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SIKH_PUNJAB_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SIKH_PUNJAB_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_sikh_punjab_entities(entities)
        lane.install_wave8_sikh_punjab_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_sikh_punjab_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_funnel_and_queue_pin_all_five_exact_label_rows(self) -> None:
        exact_by_id = {
            str(row["candidate_id"]): row for row in self.exact_rows
        }
        funnel_rows = {
            str(row["candidate_id"]): row
            for row in self.funnel["row_label_data"]
            if "sikh punjab" in row.get("blocker_labels", [])
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_HASHES))
        self.assertEqual(set(funnel_rows), set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_HASHES),
        )

        payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(exact_by_id)
        )
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        labels = [
            row
            for row in self.funnel["labels"]
            if row.get("label") == "sikh punjab"
        ]
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(
            label["event_candidate_id_sha256"],
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(label["events_touched"], 5)
        self.assertEqual(label["unresolved_side_attempts"], 5)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 5)
        self.assertEqual(label["centuries"], {"CE_17": 1, "CE_18": 3, "CE_19": 1})
        self.assertEqual(
            {
                candidate_id
                for candidate_id, row in funnel_rows.items()
                if row.get("sole_blocker_label") == "sikh punjab"
            },
            set(EXPECTED_RAW_HASHES) - {"hced-Anandpur1701-1"},
        )
        for row in funnel_rows.values():
            self.assertTrue(
                any(
                    failure.get("label") == "sikh punjab"
                    and failure.get("failure_case") == "zero_time_valid_candidates"
                    for failure in row.get("label_failures", [])
                )
            )

    def test_hashes_dispositions_counts_and_ownership_are_pinned(self) -> None:
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                expected_hash,
            )
        self.assertEqual(lane.WAVE8_SIKH_PUNJAB_ROW_HASHES, EXPECTED_RAW_HASHES)
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS,
            set(EXPECTED_WINNERS_AND_LOSERS),
        )
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_HOLD_IDS,
            {"hced-Anandpur1701-1"},
        )
        self.assertEqual(lane.WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS, set())
        self.assertEqual(lane.WAVE8_SIKH_PUNJAB_EXCLUSION_IDS, set())
        self.assertIs(
            lane.WAVE8_SIKH_PUNJAB_EXCLUSIONS,
            lane.WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            set(lane.WAVE8_SIKH_PUNJAB_NONPROMOTIONS),
            lane.WAVE8_SIKH_PUNJAB_HOLD_IDS,
        )
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_RESERVED_IDS,
            set(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(
            lane.validate_wave8_sikh_punjab_queue_contracts(self.hced_rows),
            {
                "cross_lane_hced_dispositions": 1,
                "holds": 1,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_sikh_punjab_counts(),
            {
                "country_quarantine_additions": 1,
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "new_entities": 8,
                "new_sources": 13,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_sikh_punjab_cohort_counts(),
            {
                "banda_singh_mughal_conflict_1715": 1,
                "first_anglo_sikh_war_baddowal_1846": 1,
                "guru_hargobind_mughal_conflict_1634": 1,
                "sikh_durrani_gujrat_campaign_1797": 1,
            },
        )

    def test_semantic_signature_is_frozen(self) -> None:
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_FINAL_AUDIT_SIGNATURE,
            FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_sikh_punjab_audit_signature(),
            FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(len(bytes.fromhex(FINAL_AUDIT_SIGNATURE)), 32)

    def test_sources_and_entities_are_parseable_bounded_and_exact(self) -> None:
        self.assertEqual(len(lane.WAVE8_SIKH_PUNJAB_SOURCES), 13)
        self.assertEqual(len(lane.WAVE8_SIKH_PUNJAB_ENTITIES), 8)
        source_ids = {
            str(source["id"]) for source in lane.WAVE8_SIKH_PUNJAB_SOURCES
        }
        source_families = {
            str(source["source_family_id"])
            for source in lane.WAVE8_SIKH_PUNJAB_SOURCES
        }
        self.assertEqual(len(source_ids), 13)
        self.assertEqual(len(source_families), 13)
        for source in lane.WAVE8_SIKH_PUNJAB_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SIKH_PUNJAB_ENTITIES
        }
        used_ids = {
            str(entity_id)
            for contract in lane.WAVE8_SIKH_PUNJAB_CONTRACTS.values()
            for side in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[side]
        }
        self.assertEqual(used_ids, entity_ids)
        for entity in lane.WAVE8_SIKH_PUNJAB_ENTITIES:
            parsed = Entity.from_dict(entity)
            self.assertEqual(parsed.start_year, parsed.end_year)
            self.assertIn(parsed.start_year, {1634, 1715, 1797, 1846})
            self.assertTrue(parsed.kind.startswith("event_bounded_"))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertIn("modern state", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
            self.assertNotIn(
                normalize_label(entity["name"]),
                {
                    "afghanistan",
                    "mughal empire",
                    "punjab",
                    "sikh empire",
                    "sikh punjab",
                    "sikhs",
                    "united kingdom",
                },
            )

    def test_contract_dates_actors_outcomes_and_sources_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source
            for source in lane.WAVE8_SIKH_PUNJAB_SOURCES
        }
        for candidate_id, contract in lane.WAVE8_SIKH_PUNJAB_CONTRACTS.items():
            name, year, date_text, precision, granularity = EXPECTED_CANONICAL[
                candidate_id
            ]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], name)
            self.assertEqual(
                (canonical["year_low"], canonical["year_high"]),
                (year, year),
            )
            self.assertEqual(canonical["date_text"], date_text)
            self.assertEqual(canonical["date_precision"], precision)
            self.assertEqual(canonical["granularity"], granularity)
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(
                contract["actor_override"],
                "event_bounded_exact_opposing_forces",
            )
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": (
                        "military_elo.promotion.wave8_sikh_punjab"
                    ),
                    "status": "canonical_hced_owner",
                },
            )
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertTrue(
                set(contract["outcome_source_ids"])
                <= set(contract["evidence_refs"])
            )
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                expected_families,
            )
            self.assertGreaterEqual(len(expected_families), 2)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn(
                    "outcome",
                    source_by_id[source_id]["evidence_roles"],
                )
            row = self.hced_by_id[candidate_id]
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])

        self.assertEqual(lane.WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES, {})
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_CONTRACTS["hced-Baddowal1846-1"][
                "side_2_entity_ids"
            ],
            [BADDOWAL_BRITISH_INDIAN_ID],
        )
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_CONTRACTS[
                "hced-Gujrat, Pakistan1797-1"
            ]["side_2_entity_ids"],
            [GUJRAT_DURRANI_ID],
        )

    def test_anandpur_is_an_unknown_hold_and_never_a_draw(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_SIKH_PUNJAB_HOLDS),
            {"hced-Anandpur1701-1"},
        )
        hold = lane.WAVE8_SIKH_PUNJAB_HOLDS["hced-Anandpur1701-1"]
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        self.assertTrue(forbidden.isdisjoint(hold))
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(hold["result_type"], "unknown")
        self.assertEqual(hold["reviewed_outcome"], "unknown")
        self.assertTrue(hold["unknown_is_never_draw"])
        self.assertFalse(hold["terminal_exclusion"])
        self.assertIn("not promoted", hold["hold_reason"])
        self.assertIn("never converted", hold["hold_reason"])
        self.assertEqual(len(hold["evidence_refs"]), 2)
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "ambiguous_multi_operation_aggregate",
        )
        self.assertEqual(
            hold["duplicate_ownership"]["status"],
            "held_hced_owner",
        )

        adjacent = lane.WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS
        self.assertEqual(set(adjacent), {ANANDPUR_1700_ID})
        self.assertEqual(adjacent[ANANDPUR_1700_ID]["raw_row_sha256"], ANANDPUR_1700_HASH)
        self.assertEqual(
            adjacent[ANANDPUR_1700_ID]["related_candidate_id"],
            "hced-Anandpur1701-1",
        )
        self.assertIn("double rating", adjacent[ANANDPUR_1700_ID]["reason"])

    def test_every_locked_row_and_adjacent_twin_fail_closed_on_drift(self) -> None:
        for candidate_id in EXPECTED_RAW_HASHES:
            with self.subTest(candidate_id=candidate_id):
                mutated = copy.deepcopy(self.hced_rows)
                row = next(
                    item for item in mutated if item["candidate_id"] == candidate_id
                )
                row["name"] = f"{row['name']} drift"
                with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                    lane.validate_wave8_sikh_punjab_queue_contracts(mutated)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Amritsar1634-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            lane.validate_wave8_sikh_punjab_queue_contracts(missing)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(copy.deepcopy(self.hced_by_id["hced-Baddowal1846-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            lane.validate_wave8_sikh_punjab_queue_contracts(duplicated)

        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-sikh-punjab-row",
                "side_1_raw": "Sikh Punjab",
                "side_2_raw": "Future opponent",
                "name": "Future row",
                "year_low": 1850,
                "year_high": 1850,
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Sikh Punjab inventory changed"):
            lane.validate_wave8_sikh_punjab_queue_contracts(future)

        no_adjacent = [
            row for row in self.hced_rows if row["candidate_id"] != ANANDPUR_1700_ID
        ]
        with self.assertRaisesRegex(ValueError, "adjacent Anandpur twin"):
            lane.validate_wave8_sikh_punjab_queue_contracts(no_adjacent)
        changed_adjacent = copy.deepcopy(self.hced_rows)
        next(
            row for row in changed_adjacent if row["candidate_id"] == ANANDPUR_1700_ID
        )["name"] = "Anandpur chronology drift"
        with self.assertRaisesRegex(ValueError, "adjacent Anandpur twin fingerprint"):
            lane.validate_wave8_sikh_punjab_queue_contracts(changed_adjacent)

    def test_emission_is_four_parseable_exact_wins_without_generic_actors(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 4)
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in events
        }
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertFalse(lane.WAVE8_SIKH_PUNJAB_HOLD_IDS & set(by_candidate))
        forbidden_ids = {
            "afghanistan",
            "mughal_empire",
            "punjab",
            "sikh_empire",
            "sikh_punjab",
            "united_kingdom",
        }
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                event["name"],
                EXPECTED_CANONICAL[candidate_id][0],
            )
            self.assertEqual(event["date_precision"], EXPECTED_CANONICAL[candidate_id][3])
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
            self.assertFalse((winners | losers) & forbidden_ids)
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            contract = lane.WAVE8_SIKH_PUNJAB_CONTRACTS[candidate_id]
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
        self.assertEqual(
            [(event["year"], event["hced_candidate_id"]) for event in events],
            sorted(
                (event["year"], event["hced_candidate_id"])
                for event in events
            ),
        )

    def test_installs_promotions_and_entity_windows_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_sikh_punjab_entities(entities)
        lane.install_wave8_sikh_punjab_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)
        events_1 = lane.promote_wave8_sikh_punjab_contracts(
            self.hced_rows,
            entities,
            copy.deepcopy(existing),
        )
        events_2 = lane.promote_wave8_sikh_punjab_contracts(
            self.hced_rows,
            entities,
            copy.deepcopy(existing),
        )
        self.assertEqual(events_1, events_2)

        colliding_entities = copy.deepcopy(entities)
        colliding_entities[AMRITSAR_SIKH_ID] = {"id": AMRITSAR_SIKH_ID}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_sikh_punjab_entities(colliding_entities)
        first_source = str(lane.WAVE8_SIKH_PUNJAB_SOURCES[0]["id"])
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_sikh_punjab_sources(
                {first_source: {"id": first_source}}
            )

        missing_entity = copy.deepcopy(entities)
        missing_entity.pop(BADDOWAL_BRITISH_INDIAN_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_sikh_punjab_contracts(
                self.hced_rows,
                missing_entity,
                existing,
            )
        wrong_window = copy.deepcopy(entities)
        wrong_window[GUJRAT_SIKH_ID]["start_year"] = 1798
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_sikh_punjab_contracts(
                self.hced_rows,
                wrong_window,
                existing,
            )

    def test_promotion_candidate_and_event_duplicate_guards_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        candidate_collision = [
            *copy.deepcopy(existing),
            {
                "id": "future_owner",
                "name": "Unrelated",
                "year": 1634,
                "hced_candidate_id": "hced-Amritsar1634-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_sikh_punjab_contracts(
                self.hced_rows,
                entities,
                candidate_collision,
            )
        canonical_collision = [
            *copy.deepcopy(existing),
            {"id": "future_twin", "name": "Action at Baddowal", "year": 1846},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_sikh_punjab_contracts(
                self.hced_rows,
                entities,
                canonical_collision,
            )
        raw_collision = [
            *copy.deepcopy(existing),
            {"id": "future_raw_twin", "name": "Gurdas Nangal", "year": 1715},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_sikh_punjab_contracts(
                self.hced_rows,
                entities,
                raw_collision,
            )

    def test_duplicate_audit_and_all_integration_twin_guards(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT),
            set(EXPECTED_RAW_HASHES),
        )
        dispositions = {
            **lane.WAVE8_SIKH_PUNJAB_CONTRACTS,
            **lane.WAVE8_SIKH_PUNJAB_NONPROMOTIONS,
        }
        for candidate_id, audit in (
            lane.WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT.items()
        ):
            self.assertEqual(audit["aliases"], sorted(set(audit["aliases"])))
            self.assertTrue(
                all(alias == normalize_label(alias) for alias in audit["aliases"])
            )
            canonical = dispositions[candidate_id]["canonical_event"]
            self.assertIn(normalize_label(canonical["name"]), audit["aliases"])
            if candidate_id == "hced-Anandpur1701-1":
                self.assertEqual(audit["years"], [1700, 1701])
            else:
                self.assertEqual(
                    audit["years"],
                    [canonical["year_low"], canonical["year_high"]],
                )

        self.assertEqual(lane.WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        self.assertEqual(
            lane.validate_wave8_sikh_punjab_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 5,
            },
        )

        hced_twin = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-amritsar-twin",
                "name": "Battle of Amritsar (1634)",
                "year_best": 1634,
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_sikh_punjab_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
                self.release_events,
            )
        iwbd_twin = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-baddowal-twin",
                "name": "Battle of Buddowal",
                "start_date": "1846-01-21",
                "end_date": "1846-01-21",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_sikh_punjab_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
                self.release_events,
            )
        release_twin = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future-release-gurdas-twin",
                "name": "Siege of Gurdas Nangal",
                "year": 1715,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_sikh_punjab_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_location_quarantines_are_local_complete_and_non_mutating(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS,
        )
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Gujrat, Pakistan1797-1"},
        )
        self.assertEqual(
            lane.WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_ADDITIONS,
            {
                "country": lane.WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS,
                "point": lane.WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            lane.wave8_sikh_punjab_location_quarantine_additions(),
            lane.WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            set(lane.WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS,
        )
        for candidate_id, review in (
            lane.WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS.items()
        ):
            expected = {"withhold_point"}
            if candidate_id == "hced-Gujrat, Pakistan1797-1":
                expected.add("withhold_country")
            self.assertEqual(set(review["actions"]), expected)
            self.assertTrue(review["reason"])

        by_candidate = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        for candidate_id, event in by_candidate.items():
            self.assertNotIn("geometry", event)
            if candidate_id == "hced-Gujrat, Pakistan1797-1":
                self.assertNotIn("modern_location_country", event)
                self.assertNotIn("location_provenance", event)
            else:
                self.assertEqual(event["modern_location_country"], "India")
                self.assertIn("location_provenance", event)
        self.assertFalse(
            lane.WAVE8_SIKH_PUNJAB_HOLD_IDS
            & lane.WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS
        )
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_release_overlap_is_all_or_none_and_uses_lane_ownership(self) -> None:
        event_overlap = {
            str(event["hced_candidate_id"]): event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS
        }
        self.assertIn(
            set(event_overlap),
            (set(), set(lane.WAVE8_SIKH_PUNJAB_CONTRACT_IDS)),
        )
        for event in event_overlap.values():
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))

        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SIKH_PUNJAB_ENTITIES
        }
        release_entity_ids = {
            str(entity["id"]) for entity in self.release_entities
        }
        self.assertIn(
            lane_entity_ids & release_entity_ids,
            (set(), lane_entity_ids),
        )
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SIKH_PUNJAB_SOURCES
        }
        release_source_ids = {
            str(source["id"]) for source in self.release_sources
        }
        self.assertIn(
            lane_source_ids & release_source_ids,
            (set(), lane_source_ids),
        )


if __name__ == "__main__":
    unittest.main()
