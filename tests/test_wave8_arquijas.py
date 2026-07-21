import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_arquijas as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_arquijas_"
CARLIST = "carlist_army_first_war"
ISABELINE = "isabeline_government_forces_first_carlist_war"

EXPECTED_HASHES = {
    "hced-Arquijas1834-1": (
        "f8bafb6de9ca178ded97f44a16da4a9c0cc96a8cb1982f74da8ee49536ad3c11"
    ),
    "hced-Arquijas1835-1": (
        "89b168b4119b2c20de6cf8db9302b2e287afec914aed3dbab6218ab0a4b02794"
    ),
}

EXPECTED_ADJACENT = {
    "hced-Artaza1834-1": (
        "cd81f724365721250146a3c770797d27784a79b18a9381d3e770cf739db1dc79"
    ),
    "hced-Asarta1833-1": (
        "bd305efe2efa6c551c7c6950bac089f478c4f689a6acae330e0e0d458ac07ddc"
    ),
    "hced-Gatazo1895-1": (
        "bec2c4765349f1ce17583376e2a18ad6db288ecf00b1b8e6a27ae06d34890596"
    ),
    "hced-Lircay1830-1": (
        "dcdfed7c7f4dcec0abe1e4068fa1236ea13a505ba712f91f3610a948bc45c02b"
    ),
    "hced-Mendaza1834-1": (
        "34a724ced4b306041e69198c56605ac7d2f5a57190e5f41806f39f24792c7f02"
    ),
    "hced-Ormaiztegui1835-1": (
        "cf9aaf84b0c5c98903a75a1fcf6ba8e8d3eff276cb2187c3478455ea8ec2147a"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q12254001": (
        "6a066f59c78d6b04f454f02b2791968198d4d0e3557a54f69915470d0cdf1bd5"
    ),
    "Q3755395": (
        "af2321bf2edf2983cf323707e3bb22108702308587e28edede473684eed94071"
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


def _full_row_sha256(row):
    payload = json.dumps(
        row,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Wave8ArquijasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd_rows = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        source_ids = {str(source["id"]) for source in lane.WAVE8_ARQUIJAS_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ARQUIJAS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        before_entities = copy.deepcopy(entities)
        lane.install_wave8_arquijas_entities(entities)
        self.assertEqual(entities, before_entities)
        lane.install_wave8_arquijas_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_arquijas_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_liberals_inventory_and_locked_row_fingerprints(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "liberals"
            or normalize_label(row.get("side_2_raw")) == "liberals"
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact},
            {
                *EXPECTED_HASHES,
                "hced-Gatazo1895-1",
                "hced-Lircay1830-1",
            },
        )
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(lane.WAVE8_ARQUIJAS_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (
                        row["side_1_raw"],
                        row["side_2_raw"],
                        row["winner_raw"],
                        row["loser_raw"],
                    ),
                    ("Carlists", "Liberals", "Carlists", "Liberals"),
                )
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_arquijas_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_rows": 6,
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        integrated_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        } & lane.WAVE8_ARQUIJAS_CONTRACT_IDS
        if not integrated_ids:
            self.assertEqual(
                lane.validate_wave8_arquijas_funnel(self.funnel),
                {
                    "events_touched": 4,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 4,
                    "zero_time_valid_candidates": 4,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_arquijas_exact_label_funnel_audit"
                ],
                lane.WAVE8_ARQUIJAS_FUNNEL_AUDIT,
            )

    def test_only_arquijas_rows_promote_without_holds_or_new_identity(self) -> None:
        self.assertEqual(lane.WAVE8_ARQUIJAS_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_ARQUIJAS_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_ARQUIJAS_HOLDS)
        self.assertFalse(lane.WAVE8_ARQUIJAS_ENTITIES)
        for contract in lane.WAVE8_ARQUIJAS_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_exact_dates_names_and_single_battle_granularity_are_pinned(self) -> None:
        expected = {
            "hced-Arquijas1834-1": (
                "First Battle of Arquijas",
                "15 December 1834",
                "1834-12-15",
                0.90,
            ),
            "hced-Arquijas1835-1": (
                "Second Battle of Arquijas",
                "5 February 1835",
                "1835-02-05",
                0.95,
            ),
        }
        for candidate_id, values in expected.items():
            contract = lane.WAVE8_ARQUIJAS_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["start_date"],
                    contract["confidence"],
                ),
                values,
            )
            self.assertEqual(canonical["start_date"], canonical["end_date"])
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(
                canonical["granularity"],
                "single_battle_in_the_first_carlist_war",
            )

    def test_two_independent_outcome_families_and_both_source_locators(self) -> None:
        sources = {
            str(source["id"]): source for source in lane.WAVE8_ARQUIJAS_SOURCES
        }
        self.assertEqual(len(sources), 2)
        self.assertEqual(
            {source["url"] for source in sources.values()},
            {
                (
                    "https://aunamendi.eusko-ikaskuntza.eus/es/"
                    "batallas-del-puente-de-arquijas/ar-4511/"
                ),
                (
                    "https://publicaciones.defensa.gob.es/media/downloadable/"
                    "files/links/r/h/rhm_extra_ii_2022_.pdf"
                ),
            },
        )
        self.assertEqual(
            lane.WAVE8_ARQUIJAS_ALBI_DOI,
            "https://doi.org/10.55553/504jnk066201",
        )
        for source in sources.values():
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
        for contract in lane.WAVE8_ARQUIJAS_CONTRACTS.values():
            self.assertEqual(set(contract["outcome_source_ids"]), set(sources))
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(set(contract["event_evidence_roles"]), set(sources))
            self.assertIn(
                "tactical_outcome",
                contract["event_evidence_roles"][
                    "wave8_arquijas_aunamendi_battles"
                ],
            )
            self.assertIn(
                "independent_tactical_outcome_crosscheck",
                contract["event_evidence_roles"][
                    "wave8_arquijas_albi_first_carlist_war_north"
                ],
            )

    def test_existing_conflict_bounded_identities_are_reused_without_aliases(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        for entity_id in (CARLIST, ISABELINE):
            entity = entities[entity_id]
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                (1833, 1840),
            )
            self.assertEqual(entity["aliases"], [])
            Entity.from_dict(entity)
        self.assertFalse(lane.WAVE8_ARQUIJAS_ENTITIES)
        self.assertNotIn(
            "liberals",
            {
                normalize_label(alias)
                for entity_id in (CARLIST, ISABELINE)
                for alias in entities[entity_id]["aliases"]
            },
        )

    def test_emitted_events_preserve_raw_carlist_tactical_wins(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_HASHES))
        expected_confidence = {
            "hced-Arquijas1834-1": 0.90,
            "hced-Arquijas1835-1": 0.95,
        }
        for candidate_id, event in events.items():
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                outcomes,
                {
                    CARLIST: "engagement_victory",
                    ISABELINE: "engagement_defeat",
                },
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["scale"], "battle")
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["confidence"], expected_confidence[candidate_id])
            self.assertEqual(
                set(event["outcome_source_ids"]),
                {str(source["id"]) for source in lane.WAVE8_ARQUIJAS_SOURCES},
            )
            self.assertIn("hced_dataset", event["source_ids"])
            Event.from_dict(event)

    def test_promoted_points_are_withheld_but_spain_and_provenance_remain(self) -> None:
        self.assertEqual(
            lane.WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ARQUIJAS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ARQUIJAS_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_ARQUIJAS_CONTRACT_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Spain")
            self.assertIn("location_provenance", event)
            reason = lane.WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(
                set(reason["evidence_refs"]),
                set(event["outcome_source_ids"]),
            )

    def test_six_adjacent_hced_boundaries_are_fingerprinted_and_not_owned(self) -> None:
        dispositions = lane.WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS
        self.assertEqual(set(dispositions), set(EXPECTED_ADJACENT))
        self.assertFalse(set(dispositions) & lane.WAVE8_ARQUIJAS_RESERVED_IDS)
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for candidate_id, expected_hash in EXPECTED_ADJACENT.items():
            self.assertEqual(canonical_hced_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertEqual(
                dispositions[candidate_id]["raw_row_sha256"],
                expected_hash,
            )
        self.assertEqual(
            dispositions["hced-Gatazo1895-1"]["disposition"],
            "adjacent_label_hold_not_owned",
        )
        self.assertEqual(
            dispositions["hced-Lircay1830-1"]["disposition"],
            "adjacent_label_hold_not_owned",
        )
        for candidate_id in ("hced-Artaza1834-1", "hced-Asarta1833-1"):
            self.assertEqual(
                dispositions[candidate_id]["owner_module"],
                "military_elo.promotion.wave8_spanish_liberals",
            )
            self.assertEqual(
                dispositions[candidate_id]["disposition"],
                "external_lane_hold",
            )
        self.assertIn(
            "three_days_before",
            dispositions["hced-Mendaza1834-1"]["relationship"],
        )
        self.assertIn(
            "different_first_carlist_war_battle",
            dispositions["hced-Ormaiztegui1835-1"]["relationship"],
        )

    def test_wikidata_twins_are_fingerprinted_and_never_promoted(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        self.assertEqual(
            lane.WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES,
            EXPECTED_DISCOVERY_HASHES,
        )
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            self.assertEqual(_full_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertIs(by_id[candidate_id]["do_not_rate_automatically"], True)
        self.assertEqual(
            lane.validate_wave8_arquijas_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_twins": 2,
                "discovery_promotions": 0,
                "unknown_never_draw_rows": 1,
            },
        )
        self.assertEqual(by_id["Q3755395"]["winners"][0]["label"], "Carlist army")
        self.assertEqual(by_id["Q12254001"]["winners"], [])
        self.assertEqual(
            lane.WAVE8_ARQUIJAS_DISCOVERY_EXPECTED["Q12254001"][
                "outcome_disposition"
            ],
            "unknown_never_draw",
        )
        self.assertNotIn(
            "draw",
            lane.WAVE8_ARQUIJAS_DISCOVERY_EXPECTED["Q12254001"][
                "outcome_disposition"
            ].replace("never_draw", ""),
        )

    def test_iwd_iwbd_hced_and_release_twin_inventory_is_empty(self) -> None:
        owned_count = sum(
            event.get("hced_candidate_id") in lane.WAVE8_ARQUIJAS_CONTRACT_IDS
            for event in self.release_events
        )
        self.assertEqual(
            lane.validate_wave8_arquijas_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "adjacent_hced_dispositions": 6,
                "existing_release_owned_events": owned_count,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwd_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_future_adjacent_rows_and_cross_source_twins_fail_closed(self) -> None:
        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-liberals",
                "name": "Future unrelated row",
                "side_1_raw": "Liberals",
                "side_2_raw": "Unrelated",
                "participants_raw": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_arquijas_queue_contracts(future_hced)

        future_iwd = [
            *copy.deepcopy(self.iwd_rows),
            {
                "candidate_id": "iwd-future-arquijas",
                "name": "First Battle of Arquijas",
                "year": 1834,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_arquijas_integration_dispositions(
                self.hced_rows,
                future_iwd,
                self.iwbd_rows,
                self.release_events,
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-arquijas",
                "name": "Second Battle of Arquijas",
                "start_date": "1835-02-05",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_arquijas_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_first_arquijas_twin",
                "name": "First Battle of Arquijas",
                "year": 1834,
                "aliases": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_arquijas_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_queue_discovery_and_adjacent_fingerprint_guards_reject_tampering(self) -> None:
        tampered_hced = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered_hced
            if item.get("candidate_id") == "hced-Arquijas1834-1"
        )
        row["winner_raw"] = "Liberals"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_arquijas_queue_contracts(tampered_hced)

        tampered_adjacent = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered_adjacent
            if item.get("candidate_id") == "hced-Mendaza1834-1"
        )
        row["participants_raw"] = []
        with self.assertRaisesRegex(ValueError, "adjacent HCED inventory changed"):
            lane.validate_wave8_arquijas_queue_contracts(tampered_adjacent)

        tampered_discovery = copy.deepcopy(self.wikidata_rows)
        row = next(
            item
            for item in tampered_discovery
            if item.get("candidate_id") == "Q12254001"
        )
        row["winners"] = [{"label": "unknown", "uri": "urn:invalid"}]
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_arquijas_discovery_dispositions(tampered_discovery)

    def test_promoter_rejects_missing_identity_and_duplicate_ownership(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(ISABELINE)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_arquijas_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        events = lane.promote_wave8_arquijas_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_arquijas_contracts(
                self.hced_rows,
                entities,
                [*existing, *events],
            )
        duplicate_name = {
            "id": "future_duplicate_name",
            "name": events[0]["name"],
            "year": events[0]["year"],
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_arquijas_contracts(
                self.hced_rows,
                entities,
                [*existing, duplicate_name],
            )

    def test_installers_are_noop_for_entities_and_collision_safe_for_sources(self) -> None:
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        before = copy.deepcopy(entities)
        lane.install_wave8_arquijas_entities(entities)
        self.assertEqual(entities, before)

        _, sources, _ = self._installed()
        once = copy.deepcopy(sources)
        lane.install_wave8_arquijas_sources(sources)
        self.assertEqual(sources, once)
        for source in lane.WAVE8_ARQUIJAS_SOURCES:
            self.assertIn(str(source["id"]), sources)
            Source.from_dict(sources[str(source["id"])])

        source_id = str(lane.WAVE8_ARQUIJAS_SOURCES[0]["id"])
        collision = copy.deepcopy(sources)
        collision[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_arquijas_sources(collision)

    def test_current_release_events_and_sources_are_all_or_none(self) -> None:
        current_owned = sum(
            event.get("hced_candidate_id") in lane.WAVE8_ARQUIJAS_CONTRACT_IDS
            for event in self.release_events
        )
        integrated = bool(current_owned)
        self.assertEqual(
            lane.validate_wave8_arquijas_current_artifact_state(
                self.release_events,
                self.release_entities,
                self.release_sources,
            ),
            {
                "artifact_state": "integrated" if integrated else "absent",
                "installed_sources": len(lane.WAVE8_ARQUIJAS_SOURCES)
                if integrated
                else 0,
                "promoted_events": len(lane.WAVE8_ARQUIJAS_CONTRACT_IDS)
                if integrated
                else 0,
            },
        )

        events = self._events()
        base_events = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ARQUIJAS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_ARQUIJAS_SOURCES
        }
        base_sources = [
            copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        ]
        integrated_sources = [
            *base_sources,
            *copy.deepcopy(lane.WAVE8_ARQUIJAS_SOURCES),
        ]
        self.assertEqual(
            lane.validate_wave8_arquijas_current_artifact_state(
                [*base_events, *events],
                self.release_entities,
                integrated_sources,
            ),
            {
                "artifact_state": "integrated",
                "installed_sources": 2,
                "promoted_events": 2,
            },
        )

        with self.assertRaisesRegex(ValueError, "event inventory is partial"):
            lane.validate_wave8_arquijas_current_artifact_state(
                [*base_events, events[0]],
                self.release_entities,
                integrated_sources,
            )
        with self.assertRaisesRegex(ValueError, "source inventory is partial"):
            lane.validate_wave8_arquijas_current_artifact_state(
                base_events,
                self.release_entities,
                [*base_sources, lane.WAVE8_ARQUIJAS_SOURCES[0]],
            )
        with self.assertRaisesRegex(ValueError, "artifacts are out of sync"):
            lane.validate_wave8_arquijas_current_artifact_state(
                [*base_events, *events],
                self.release_entities,
                base_sources,
            )

    def test_partial_current_release_ownership_is_rejected(self) -> None:
        partial_release = [self._events()[0], *copy.deepcopy(self.release_events)]
        with self.assertRaisesRegex(ValueError, "ownership is partial"):
            lane.validate_wave8_arquijas_integration_dispositions(
                self.hced_rows,
                self.iwd_rows,
                self.iwbd_rows,
                partial_release,
            )

    def test_counts_metadata_and_final_signature_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_arquijas_counts(),
            {
                "adjacent_hced_dispositions": 6,
                "country_quarantine_additions": 0,
                "discovery_nonrating_twins": 2,
                "holds": 0,
                "integration_dispositions": 8,
                "new_entities": 0,
                "new_sources": 2,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 1,
            },
        )
        self.assertEqual(
            lane.wave8_arquijas_cohort_counts(),
            {"first_carlist_war_arquijas_1834_1835": 2},
        )
        self.assertEqual(
            lane.wave8_arquijas_audit_signature(),
            "7ad64729af51fc9604d00a9dccbe9eaf50c80e84cf9a47aec7c77fd3011134f9",
        )
        self.assertEqual(
            lane.wave8_arquijas_audit_signature(),
            lane.WAVE8_ARQUIJAS_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_arquijas_metadata()
        self.assertEqual(metadata["hold_candidate_ids"], [])
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(EXPECTED_HASHES),
        )
        self.assertEqual(
            metadata["discovery_nonrating_candidate_ids"],
            sorted(EXPECTED_DISCOVERY_HASHES),
        )


if __name__ == "__main__":
    unittest.main()
