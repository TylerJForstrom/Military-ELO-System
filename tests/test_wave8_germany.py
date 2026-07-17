import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_germany import (
    WAVE8_GERMANY_CONTRACT_IDS,
    WAVE8_GERMANY_CONTRACTS,
    WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS,
    WAVE8_GERMANY_ENTITIES,
    WAVE8_GERMANY_EXCLUSIONS,
    WAVE8_GERMANY_EXCLUSION_IDS,
    WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS,
    WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE,
    WAVE8_GERMANY_HOLD_IDS,
    WAVE8_GERMANY_HOLDS,
    WAVE8_GERMANY_INTEGRATION_DISPOSITIONS,
    WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_GERMANY_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_GERMANY_NONPROMOTIONS,
    WAVE8_GERMANY_OUTCOME_OVERRIDE_METADATA,
    WAVE8_GERMANY_OUTCOME_OVERRIDES,
    WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GERMANY_RESERVED_IDS,
    WAVE8_GERMANY_SOURCES,
    WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
    WAVE8_GERMANY_TERMINAL_EXCLUSIONS,
    install_wave8_germany_entities,
    install_wave8_germany_sources,
    promote_wave8_germany_contracts,
    validate_wave8_germany_integration_dispositions,
    validate_wave8_germany_queue_contracts,
    wave8_germany_audit_signature,
    wave8_germany_cohort_counts,
    wave8_germany_counts,
    wave8_germany_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_germany_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue unavailable: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_GERMANY_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_GERMANY_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_GERMANY_HOLDS,
        "integration_dispositions": WAVE8_GERMANY_INTEGRATION_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_GERMANY_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_GERMANY_SOURCES,
        "terminal_exclusions": WAVE8_GERMANY_TERMINAL_EXCLUSIONS,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class Wave8GermanyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        funnel_path = ROOT / "build" / "hced-unresolved-label-funnel.json"
        if not funnel_path.exists():
            raise unittest.SkipTest("HCED unresolved-label funnel is unavailable")
        cls.funnel = _json(funnel_path)
        cls.iwbd_rows = _jsonl(
            ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        )
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _entities(self) -> dict[str, dict]:
        lane_ids = {str(entity["id"]) for entity in WAVE8_GERMANY_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in lane_ids
        }
        install_wave8_germany_entities(entities)
        return entities

    def _pre_lane_events(self) -> list[dict]:
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_GERMANY_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]

    def _events(self) -> list[dict]:
        return promote_wave8_germany_contracts(
            self.rows,
            self._entities(),
            self._pre_lane_events(),
        )

    def test_exact_sixteen_row_inventory_counts_and_signature(self) -> None:
        # The lane is fully integrated, so the live funnel no longer carries
        # its rows. The pre-promotion sixteen-row scope is validated against
        # the historical audit-moment projection (regenerated from the tree
        # before the Seljuks lane promoted Dorylaeum and this lane reserved
        # its cohort), then the live funnel is required to have released it.
        historical_blockers = {
            "hced-Cassano1158-1": ["germany"],
            "hced-Cedynia972-1": ["germany"],
            "hced-Cesis1919-1": ["germany"],
            "hced-Cotrone982-1": ["germany"],
            "hced-Dorylaeum1147-1": ["germany", "seljuks"],
            "hced-Dyle891-1": ["danish vikings", "germany"],
            "hced-La Gueule891-1": ["danish vikings", "germany"],
            "hced-Legnano1176-1": ["germany", "lombard league"],
            "hced-Pressburg907-1": ["germany"],
            "hced-Psie Pole1109-1": ["germany"],
            "hced-Raab1044-1": ["germany"],
            "hced-Riade933-1": ["germany"],
            "hced-Riga1709-1710-1": ["germany"],
            "hced-SantAngelo998-1": ["anti pope john crescentius", "germany"],
            "hced-Sidon1196-1": ["germany"],
            "hced-Warmstadt1113-1": [
                "germany",
                "palatinate lower saxony north mark groitch thuringia",
            ],
        }
        historical_sole_blocker_ids = {
            "hced-Cesis1919-1",
            "hced-Cotrone982-1",
            "hced-Riga1709-1710-1",
            "hced-Sidon1196-1",
        }
        historical_funnel = {
            "labels": [
                {
                    "event_candidate_id_sha256": (
                        "9d3b28f89eae15baed2eb001f6bb25f58ac9d34ac8356928a25236eabb333c4f"
                    ),
                    "events_touched": 16,
                    "failure_cases": {"one_wrong_interval_candidate": 16},
                    "label": "germany",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 16,
                }
            ],
            "row_label_data": [
                {
                    "candidate_id": candidate_id,
                    "blocker_labels": blockers,
                    "sole_blocker_label": (
                        "germany"
                        if candidate_id in historical_sole_blocker_ids
                        else None
                    ),
                    "label_failures": [
                        {
                            "label": "germany",
                            "failure_case": "one_wrong_interval_candidate",
                        }
                    ],
                }
                for candidate_id, blockers in historical_blockers.items()
            ],
        }
        scoped_rows = {
            str(row["candidate_id"]): row
            for row in historical_funnel["row_label_data"]
            if "germany" in row.get("blocker_labels", [])
        }
        exact_unresolved_germany_ids = set(scoped_rows)
        self.assertEqual(
            exact_unresolved_germany_ids,
            WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(len(exact_unresolved_germany_ids), 16)

        label_rows = [
            row
            for row in historical_funnel["labels"]
            if row.get("label") == "germany"
        ]
        self.assertEqual(len(label_rows), 1)
        label_row = label_rows[0]
        candidate_id_payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(scoped_rows)
        )
        scoped_id_sha256 = hashlib.sha256(
            candidate_id_payload.encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            scoped_id_sha256,
            "9d3b28f89eae15baed2eb001f6bb25f58ac9d34ac8356928a25236eabb333c4f",
        )
        self.assertEqual(label_row["event_candidate_id_sha256"], scoped_id_sha256)
        self.assertEqual(label_row["events_touched"], len(scoped_rows))
        self.assertEqual(label_row["unresolved_side_attempts"], len(scoped_rows))
        self.assertEqual(
            label_row["sole_blocker_events"],
            sum(
                row.get("sole_blocker_label") == "germany"
                for row in scoped_rows.values()
            ),
        )
        for row in scoped_rows.values():
            self.assertTrue(
                any(
                    failure.get("label") == "germany"
                    for failure in row.get("label_failures", [])
                )
            )

        live_rows = self.funnel.get("row_label_data", [])
        self.assertFalse(
            any(
                row.get("label") == "germany"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Germany lane must not remain unresolved",
        )
        self.assertFalse(
            any("germany" in row.get("blocker_labels", []) for row in live_rows),
            "the completed Germany lane must not remain unresolved",
        )
        self.assertFalse(
            WAVE8_GERMANY_RESERVED_IDS
            & {str(row.get("candidate_id")) for row in live_rows},
            "reserved Germany candidates must be absent from the live funnel",
        )
        self.assertEqual(
            (
                len(WAVE8_GERMANY_CONTRACT_IDS),
                len(WAVE8_GERMANY_HOLD_IDS),
                len(WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS),
            ),
            (13, 2, 1),
        )
        dispositions = (
            WAVE8_GERMANY_CONTRACT_IDS,
            WAVE8_GERMANY_HOLD_IDS,
            WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
        )
        for index, left in enumerate(dispositions):
            for right in dispositions[index + 1 :]:
                self.assertFalse(left & right)
        self.assertEqual(
            WAVE8_GERMANY_RESERVED_IDS,
            exact_unresolved_germany_ids,
        )
        self.assertIs(WAVE8_GERMANY_EXCLUSIONS, WAVE8_GERMANY_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            WAVE8_GERMANY_EXCLUSION_IDS,
            WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(
            set(WAVE8_GERMANY_NONPROMOTIONS),
            WAVE8_GERMANY_HOLD_IDS | WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(_independent_signature(), WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_germany_audit_signature(),
            WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_germany_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "holds": 2,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 2,
                "iwbd_zero_overlap_candidates": 16,
                "new_entities": 21,
                "new_sources": 27,
                "newly_rated_events": 13,
                "outcome_overrides": 1,
                "point_quarantine_additions": 3,
                "promotion_contracts": 13,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_germany_cohort_counts(),
            {
                "baltic_independence_wars_1919": 1,
                "east_frankish_magyar_war_907": 1,
                "east_frankish_magyar_war_933": 1,
                "east_frankish_viking_campaign_891": 2,
                "great_northern_war_riga_1709_1710": 1,
                "henry_iii_hungarian_intervention_1044": 1,
                "lombard_league_wars_1176": 1,
                "odo_mieszko_border_conflict_972": 1,
                "otto_ii_calabrian_campaign_982": 1,
                "otto_iii_roman_intervention_998": 1,
                "salian_saxon_conflict_1113": 1,
                "second_crusade_1147": 1,
            },
        )

    def test_every_row_hash_is_pinned_and_queue_validation_fails_closed(self) -> None:
        expected_hashes = {
            "hced-Cassano1158-1": "6dffa003740e174c3ab83a37cf7788c99ee02b453cf4679d1e995f8740b98123",
            "hced-Cedynia972-1": "7f2cdaa193a71937d493a48a0312267077ebb2e2d10803c382cba84ff048c0df",
            "hced-Cesis1919-1": "5c46929071e0917eedee58d741b065c2f91a9d3e75455ed078c37d2707a83300",
            "hced-Cotrone982-1": "b24f37a40d430c5f57a0c2617a6717cac4ee327d0d3771a89fb0f5fbc545b9df",
            "hced-Dorylaeum1147-1": "19eeb036de9ac497b6d3e99856e5a6e7627fec13e2a47b8802b21d977e918b43",
            "hced-Dyle891-1": "2f33f1a8acb214c89abc890958622091d462899165fa0ee07f76a4f49b9bfeef",
            "hced-La Gueule891-1": "3e968135745eaf6e62b3c33b7854a1c85ce5fe5382c98e10e641321b9b9eaf3e",
            "hced-Legnano1176-1": "cf4a4ef42b58368a84a1fa3528d7bcf8430a46d108dfecfe5d4df51cee6f051f",
            "hced-Pressburg907-1": "5bb057d7aedc0d925c04c263e49b4b9fa6fcdbc50a4ab762bce4b1fcdacc1cf0",
            "hced-Psie Pole1109-1": "8ef7c2c52798ce733edc88c78eb594978c63d59adcda980af5431f4815cbd606",
            "hced-Raab1044-1": "08934f8effcef6769d1e3d1be80356e43c882066cc19a557ae3f2bd06d2c09dd",
            "hced-Riade933-1": "82402b09a4c09af072977d8d5087926fd52cd731f79a469130a8e11925d386eb",
            "hced-Riga1709-1710-1": "0251050bb72cd46bd0f001775be5b6abad8c75fa5fbd7166b89a5159d618ac2b",
            "hced-SantAngelo998-1": "c6c65bc2be57b881fec7718a1f088a589e68af5d5e3ab3ba9ec616fbdaa44595",
            "hced-Sidon1196-1": "12176aceb6dcb654acbd9f0c442aa643d4eb150b3ebfe37ff3c88ea211a1defc",
            "hced-Warmstadt1113-1": "5bd629bc1df7f942eb55265df3e8fd58a97c0708c7aff0a824b9e0820a260757",
        }
        indexed = {row["candidate_id"]: row for row in self.rows}
        inventory = {
            **WAVE8_GERMANY_CONTRACTS,
            **WAVE8_GERMANY_NONPROMOTIONS,
        }
        self.assertEqual(set(expected_hashes), WAVE8_GERMANY_RESERVED_IDS)
        for candidate_id, expected in expected_hashes.items():
            self.assertEqual(canonical_hced_row_sha256(indexed[candidate_id]), expected)
            self.assertEqual(inventory[candidate_id]["raw_row_sha256"], expected)
        self.assertEqual(
            validate_wave8_germany_queue_contracts(self.rows),
            {
                "promotion_contracts": 13,
                "holds": 2,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 1,
            },
        )

        for candidate_id in (
            "hced-Cedynia972-1",
            "hced-Cassano1158-1",
            "hced-Sidon1196-1",
        ):
            changed = copy.deepcopy(self.rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "winner_raw"
            ] = "Unknown"
            with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                validate_wave8_germany_queue_contracts(changed)

    def test_twenty_one_alias_free_bounded_entities_and_sources_parse(self) -> None:
        self.assertEqual((len(WAVE8_GERMANY_ENTITIES), len(WAVE8_GERMANY_SOURCES)), (21, 27))
        source_by_id = {}
        family_ids = set()
        for source in WAVE8_GERMANY_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
            source_by_id[source["id"]] = source
            family_ids.add(source["source_family_id"])
        self.assertEqual(len(source_by_id), 27)
        self.assertEqual(len(family_ids), 27)

        entity_by_id = {}
        for entity in WAVE8_GERMANY_ENTITIES:
            Entity.from_dict(entity)
            entity_by_id[entity["id"]] = entity
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotEqual(entity["name"].casefold(), "germany")
            self.assertEqual(entity["source_ids"], sorted(set(entity["source_ids"])))
            self.assertLessEqual(set(entity["source_ids"]), set(source_by_id))
        self.assertEqual(len(entity_by_id), 21)
        used = {
            entity_id
            for contract in WAVE8_GERMANY_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
            if entity_id in entity_by_id
        }
        self.assertEqual(used, set(entity_by_id))

    def test_no_generic_or_cross_regime_germany_identity_is_used(self) -> None:
        forbidden = {
            "clio_q183_1991_6a7d0305",
            "german_empire",
            "nazi_germany",
            "weimar_germany",
            "federal_republic_germany",
            "german_democratic_republic",
        }
        all_used = {
            entity_id
            for contract in WAVE8_GERMANY_CONTRACTS.values()
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
        }
        self.assertFalse(all_used & forbidden)
        self.assertEqual(
            WAVE8_GERMANY_CONTRACTS["hced-Cesis1919-1"]["side_2_entity_ids"],
            ["landeswehr_iron_division_cesis_force_1919"],
        )
        self.assertEqual(
            (
                WAVE8_GERMANY_CONTRACTS["hced-Riga1709-1710-1"][
                    "side_1_entity_ids"
                ],
                WAVE8_GERMANY_CONTRACTS["hced-Riga1709-1710-1"][
                    "side_2_entity_ids"
                ],
            ),
            (
                ["kingdom_sweden"],
                ["clio_ru_moskva_rurik_dyn_1547_93deb0e2"],
            ),
        )
        self.assertEqual(
            WAVE8_GERMANY_CONTRACTS["hced-Dorylaeum1147-1"]["side_1_entity_ids"],
            ["clio_tr_rum_sultanate_1094_835c76cf"],
        )
        self.assertEqual(
            WAVE8_GERMANY_CONTRACTS["hced-Raab1044-1"]["side_2_entity_ids"],
            ["kingdom_hungary"],
        )

    def test_outcomes_are_direct_and_only_riga_is_reversed(self) -> None:
        winner_sides = {
            candidate_id: contract["winner_side"]
            for candidate_id, contract in WAVE8_GERMANY_CONTRACTS.items()
        }
        self.assertEqual(
            winner_sides,
            {
                "hced-Cedynia972-1": 1,
                "hced-Cesis1919-1": 1,
                "hced-Cotrone982-1": 1,
                "hced-Dorylaeum1147-1": 1,
                "hced-Dyle891-1": 1,
                "hced-La Gueule891-1": 1,
                "hced-Legnano1176-1": 1,
                "hced-Pressburg907-1": 1,
                "hced-Raab1044-1": 1,
                "hced-Riade933-1": 1,
                "hced-Riga1709-1710-1": 2,
                "hced-SantAngelo998-1": 1,
                "hced-Warmstadt1113-1": 1,
            },
        )
        override_ids = {
            candidate_id
            for candidate_id, contract in WAVE8_GERMANY_CONTRACTS.items()
            if contract["source_outcome_override"]
        }
        self.assertEqual(override_ids, {"hced-Riga1709-1710-1"})
        self.assertEqual(set(WAVE8_GERMANY_OUTCOME_OVERRIDES), override_ids)
        self.assertIs(
            WAVE8_GERMANY_OUTCOME_OVERRIDE_METADATA,
            WAVE8_GERMANY_OUTCOME_OVERRIDES,
        )
        self.assertEqual(
            WAVE8_GERMANY_OUTCOME_OVERRIDES["hced-Riga1709-1710-1"][
                "corrected_winner_entity_ids"
            ],
            ["clio_ru_moskva_rurik_dyn_1547_93deb0e2"],
        )
        for contract in WAVE8_GERMANY_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertTrue(contract["actor_override"])
            self.assertTrue(contract["outcome_source_ids"])
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
        for hold in WAVE8_GERMANY_HOLDS.values():
            self.assertEqual(hold["reviewed_outcome"], "unknown")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertNotIn("winner_side", hold)

    def test_outcome_source_families_are_exact_and_independent(self) -> None:
        sources = {source["id"]: source for source in WAVE8_GERMANY_SOURCES}
        all_outcome_families = set()
        for contract in WAVE8_GERMANY_CONTRACTS.values():
            expected = sorted(
                {
                    sources[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected)
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", sources[source_id]["evidence_roles"])
            all_outcome_families.update(expected)
        self.assertGreaterEqual(len(all_outcome_families), 18)

    def test_thirteen_promoted_events_parse_and_preserve_exact_ownership(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 13)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_GERMANY_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith("hced_wave8_germany_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertNotIn(event["hced_candidate_id"], WAVE8_GERMANY_NONPROMOTIONS)
            contract = WAVE8_GERMANY_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            winning_ids = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            self.assertEqual(
                winning_ids,
                set(contract[f"side_{contract['winner_side']}_entity_ids"]),
            )

        riga = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Riga1709-1710-1"
        )
        self.assertEqual((riga["year"], riga["end_year"]), (1709, 1710))
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in riga["participants"]
                if participant["termination"] == "engagement_victory"
            },
            {"clio_ru_moskva_rurik_dyn_1547_93deb0e2"},
        )

    def test_current_release_integration_is_exactly_all_or_none(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_GERMANY_RESERVED_IDS
        ]
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_GERMANY_CONTRACT_IDS,
        )
        self.assertEqual(len(events), 13)
        self.assertEqual(len({event["id"] for event in events}), 13)
        for event in events:
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))

    def test_location_contract_withholds_only_three_points(self) -> None:
        expected = {"hced-Dyle891-1", "hced-Raab1044-1", "hced-Riade933-1"}
        self.assertEqual(WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS, expected)
        self.assertFalse(WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            WAVE8_GERMANY_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected, "country": frozenset()},
        )
        self.assertEqual(
            wave8_germany_location_quarantine_additions(),
            {"point": expected, "country": frozenset()},
        )
        events = self._events()
        for event in events:
            candidate_id = event["hced_candidate_id"]
            self.assertIn("modern_location_country", event)
            if candidate_id in expected:
                self.assertNotIn("geometry", event)
            else:
                self.assertIn("geometry", event)

    def test_nonpromotions_are_unknown_or_terminal_not_silent_draws(self) -> None:
        self.assertEqual(
            WAVE8_GERMANY_HOLD_IDS,
            {"hced-Cassano1158-1", "hced-Psie Pole1109-1"},
        )
        cassano = WAVE8_GERMANY_HOLDS["hced-Cassano1158-1"]
        self.assertIn("Treccani", cassano["hold_reason"])
        self.assertIn("stable tactical", cassano["hold_reason"])
        psie = WAVE8_GERMANY_HOLDS["hced-Psie Pole1109-1"]
        self.assertIn("later tradition", psie["hold_reason"])
        self.assertTrue(psie["unknown_is_never_draw"])

        self.assertEqual(WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS, {"hced-Sidon1196-1"})
        sidon = WAVE8_GERMANY_TERMINAL_EXCLUSIONS["hced-Sidon1196-1"]
        self.assertTrue(sidon["terminal_exclusion"])
        self.assertIn("September 1197", sidon["hold_reason"])
        self.assertIn("without inventing", sidon["hold_reason"])
        self.assertFalse(
            WAVE8_GERMANY_NONPROMOTIONS.keys()
            & {event["hced_candidate_id"] for event in self._events()}
        )

    def test_dyle_and_geul_are_distinct_opposite_outcome_actions(self) -> None:
        dyle = WAVE8_GERMANY_CONTRACTS["hced-Dyle891-1"]
        geul = WAVE8_GERMANY_CONTRACTS["hced-La Gueule891-1"]
        self.assertNotEqual(dyle["canonical_event"]["canonical_key"], geul["canonical_event"]["canonical_key"])
        self.assertEqual(
            (
                dyle["side_2_entity_ids"],
                geul["side_1_entity_ids"],
            ),
            (
                ["viking_lotharingian_campaign_army_891"],
                ["viking_lotharingian_campaign_army_891"],
            ),
        )
        self.assertEqual(
            dyle["side_1_entity_ids"],
            ["arnulf_east_frankish_royal_army_dyle_891"],
        )
        self.assertEqual(
            geul["side_2_entity_ids"],
            ["sunderold_east_frankish_force_geul_891"],
        )

    def test_two_cesis_iwbd_twins_are_fingerprint_pinned(self) -> None:
        self.assertEqual(
            set(WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS),
            {"iwbd-107-39-783", "iwbd-108-40-787"},
        )
        self.assertEqual(WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_GERMANY_INTEGRATION_DISPOSITIONS,
            WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS,
        )
        for disposition in WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS.values():
            self.assertEqual(disposition["hced_candidate_id"], "hced-Cesis1919-1")
            self.assertEqual(disposition["disposition"], "deduplicate_to_hced")
            self.assertEqual(disposition["fingerprint"]["name"], "Cesis")
            self.assertEqual(disposition["fingerprint"]["defender_raw"], "Russia")
        self.assertEqual(
            validate_wave8_germany_integration_dispositions(
                self.rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "integration_dispositions": 2,
                "iwbd_duplicate_dispositions": 2,
                "iwbd_zero_overlap_candidates": 16,
            },
        )

        changed = copy.deepcopy(self.iwbd_rows)
        next(
            row for row in changed if row["candidate_id"] == "iwbd-107-39-783"
        )["defender_raw"] = "Baltische Landeswehr"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave8_germany_integration_dispositions(self.rows, changed)

        added = copy.deepcopy(self.iwbd_rows)
        added.append(
            {
                "candidate_id": "iwbd-future-legnano",
                "name": "Legnano",
                "start_date": "1176-05-29",
                "end_date": "1176-05-29",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed plausible IWBD overlap"):
            validate_wave8_germany_integration_dispositions(self.rows, added)

    def test_installers_are_idempotent_and_collisions_fail_closed(self) -> None:
        entities = self._entities()
        installed = copy.deepcopy(entities)
        install_wave8_germany_entities(installed)
        self.assertEqual(installed, entities)
        entity_id = WAVE8_GERMANY_ENTITIES[0]["id"]
        collision = copy.deepcopy(entities)
        collision[entity_id]["name"] = "Generic Germany"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_germany_entities(collision)

        lane_source_ids = {source["id"] for source in WAVE8_GERMANY_SOURCES}
        sources = {
            source["id"]: source
            for source in self.release_sources
            if source["id"] not in lane_source_ids
        }
        install_wave8_germany_sources(sources)
        installed_sources = copy.deepcopy(sources)
        install_wave8_germany_sources(installed_sources)
        self.assertEqual(installed_sources, sources)
        source_id = WAVE8_GERMANY_SOURCES[0]["id"]
        source_collision = copy.deepcopy(sources)
        source_collision[source_id]["title"] = "Changed title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_germany_sources(source_collision)

    def test_promotion_does_not_mutate_inputs_and_rejects_duplicate_owner(self) -> None:
        rows = copy.deepcopy(self.rows)
        entities = self._entities()
        existing = self._pre_lane_events()
        rows_before = copy.deepcopy(rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        promote_wave8_germany_contracts(rows, entities, existing)
        self.assertEqual(rows, rows_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)

        duplicate = copy.deepcopy(existing)
        duplicate.append(
            {
                "id": "existing_owner",
                "name": "Unrelated placeholder",
                "year": 972,
                "hced_candidate_id": "hced-Cedynia972-1",
            }
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_germany_contracts(rows, entities, duplicate)


if __name__ == "__main__":
    unittest.main()
