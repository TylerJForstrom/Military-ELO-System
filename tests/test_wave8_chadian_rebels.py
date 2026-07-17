import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_chadian_rebels as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_chadian_rebels_"

EXPECTED_EXACT_IDS = {
    "hced-Abeche1983-1",
    "hced-Iriba1990-1",
    "hced-N'Djamena1979-1",
    "hced-N'Djamena1980-1",
    "hced-Ouaddai1990-1",
    "hced-Oum Chalouba1983-1",
}
EXPECTED_ADJACENT_IDS = {"hced-Ati1978-1", "hced-Erdi1986-1"}
EXPECTED_PROMOTIONS = {
    "hced-Ati1978-1": {
        "name": "Battle of Ati",
        "event_type": "engagement",
        "date_text": "18-20 May 1978 (source-day variance)",
        "granularity": "three_day_battle_and_rebel_evacuation",
        "winner": {
            "french_operation_tacaud_ati_force_1978",
            "malloum_fat_ati_defense_force_1978",
        },
        "loser": {"fap_frolinat_ati_assault_force_1978"},
    },
    "hced-N'Djamena1979-1": {
        "name": "First Battle of N'Djamena",
        "event_type": "engagement",
        "date_text": "12-22 February 1979",
        "granularity": "urban_battle_and_regime_displacement_sequence",
        "winner": {
            "fan_habre_ndjamena_force_february_1979",
            "fap_goukouni_ndjamena_entry_force_february_1979",
        },
        "loser": {"malloum_fat_ndjamena_force_february_1979"},
    },
    "hced-N'Djamena1980-1": {
        "name": "Second Battle of N'Djamena",
        "event_type": "campaign",
        "date_text": "22 March-16 December 1980 (closing-day variance)",
        "granularity": "nine_month_urban_campaign",
        "winner": {
            "gunt_fap_ndjamena_campaign_force_1980",
            "libyan_ndjamena_intervention_force_1980",
        },
        "loser": {"fan_habre_ndjamena_campaign_force_1980"},
    },
}

EXPECTED_RAW_FIELDS = {
    "hced-Abeche1983-1": (
        "Abeche", "Chad", "Chadian Rebels", "Chad", "Chadian Rebels", 1983, 23
    ),
    "hced-Ati1978-1": (
        "Ati", "France, Chadian Government", "Northern Chadian Rebels",
        "France, Chadian Government", "Northern Chadian Rebels", 1978, 1271
    ),
    "hced-Erdi1986-1": (
        "Erdi", "Libya, North Chadian Rebels", "Chad",
        "Libya, North Chadian Rebels", "Chad", 1986, 5285
    ),
    "hced-Iriba1990-1": (
        "Iriba", "Chadian Government", "Chadian Rebels",
        "Chadian Government", "Chadian Rebels", 1990, 7435
    ),
    "hced-N'Djamena1979-1": (
        "N'Djamena", "Chadian Rebels", "Chadian Government",
        "Chadian Rebels", "Chadian Government", 1979, 11285
    ),
    "hced-N'Djamena1980-1": (
        "N'Djamena", "Chadian Government, Libya", "Chadian Rebels",
        "Chadian Government, Libya", "Chadian Rebels", 1980, 11287
    ),
    "hced-Ouaddai1990-1": (
        "Ouaddai", "Chadian Rebels", "Chad",
        "Chadian Rebels", "Chad", 1990, 11979
    ),
    "hced-Oum Chalouba1983-1": (
        "Oum Chalouba", "Chad", "Chadian Rebels",
        "Chad", "Chadian Rebels", 1983, 11989
    ),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _object_hash(value) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sorted_newline_sha256(values) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _participant_ids(event: dict, side: str | None = None) -> set[str]:
    return {
        str(participant["entity_id"])
        for participant in event.get("participants", [])
        if side is None or participant.get("side") == side
    }


class Wave8ChadianRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data" / "review" / "hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        cls.release_events_path = ROOT / "data" / "release" / "events.json"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.ucdp_paths = {
            name: ROOT / "data" / "review" / name
            for name in lane.WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256
        }
        cls.ucdp_rows = [
            row for path in cls.ucdp_paths.values() for row in _jsonl(path)
        ]
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.release_events = _json(cls.release_events_path)
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.owned_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in lane.WAVE8_CHADIAN_REBELS_RESERVED_IDS
        }

    def _installed(self):
        new_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_CHADIAN_REBELS_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        lane.install_wave8_chadian_rebels_entities(entities)

        new_source_ids = {
            str(source["id"]) for source in lane.WAVE8_CHADIAN_REBELS_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        lane.install_wave8_chadian_rebels_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_CHADIAN_REBELS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self) -> list[dict]:
        entities, _, existing = self._installed()
        return lane.promote_wave8_chadian_rebels_contracts(
            self.hced_rows, entities, existing
        )

    def test_public_api_is_complete(self) -> None:
        required = {
            "WAVE8_CHADIAN_REBELS_CONTRACTS",
            "WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS",
            "WAVE8_CHADIAN_REBELS_ENTITIES",
            "WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE",
            "WAVE8_CHADIAN_REBELS_HOLDS",
            "WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS",
            "WAVE8_CHADIAN_REBELS_SOURCES",
            "WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS",
            "install_wave8_chadian_rebels_entities",
            "install_wave8_chadian_rebels_sources",
            "promote_wave8_chadian_rebels_contracts",
            "validate_wave8_chadian_rebels_funnel",
            "validate_wave8_chadian_rebels_integration_dispositions",
            "validate_wave8_chadian_rebels_queue_contracts",
            "wave8_chadian_rebels_audit_signature",
            "wave8_chadian_rebels_counts",
        }
        self.assertTrue(required <= set(lane.__all__))
        self.assertTrue(all(hasattr(lane, name) for name in lane.__all__))
        self.assertFalse(any(name.startswith("_") for name in lane.__all__))

    def test_locked_queue_file_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256,
        )
        for name, path in self.ucdp_paths.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                lane.WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256[name],
            )

    def test_candidate_partition_and_digest_are_exact(self) -> None:
        self.assertEqual(
            lane.WAVE8_CHADIAN_REBELS_EXACT_CANDIDATE_IDS, EXPECTED_EXACT_IDS
        )
        self.assertEqual(
            lane.WAVE8_CHADIAN_REBELS_ADJACENT_CANDIDATE_IDS,
            EXPECTED_ADJACENT_IDS,
        )
        self.assertEqual(
            lane.WAVE8_CHADIAN_REBELS_RESERVED_IDS,
            EXPECTED_EXACT_IDS | EXPECTED_ADJACENT_IDS,
        )
        self.assertEqual(
            _sorted_newline_sha256(lane.WAVE8_CHADIAN_REBELS_RESERVED_IDS),
            lane.WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256,
        )

    def test_every_owned_hced_row_has_exact_semantics_and_fingerprint(self) -> None:
        self.assertEqual(set(self.owned_rows), EXPECTED_EXACT_IDS | EXPECTED_ADJACENT_IDS)
        for candidate_id, values in EXPECTED_RAW_FIELDS.items():
            row = self.owned_rows[candidate_id]
            measured = (
                row["name"], row["side_1_raw"], row["side_2_raw"],
                row["winner_raw"], row["loser_raw"], row["year_best"],
                row["source_row"],
            )
            self.assertEqual(measured, values)
            self.assertEqual(row["year_low"], values[5])
            self.assertEqual(row["year_high"], values[5])
            self.assertTrue(row["winner_loser_complete"])
            self.assertEqual(
                canonical_hced_row_sha256(row),
                lane.WAVE8_CHADIAN_REBELS_ROW_HASHES[candidate_id],
            )

    def test_queue_validator_covers_all_and_only_owned_spellings(self) -> None:
        self.assertEqual(
            lane.validate_wave8_chadian_rebels_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_rows": 2,
                "exact_hced_rows": 6,
                "holds": 5,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 8,
                "terminal_exclusions": 0,
            },
        )
        exact = {
            row["candidate_id"]
            for row in self.hced_rows
            if _EXACT(row.get("side_1_raw")) or _EXACT(row.get("side_2_raw"))
        }
        self.assertEqual(exact, EXPECTED_EXACT_IDS)

    def test_queue_validator_rejects_mutation_missing_and_new_label_rows(self) -> None:
        changed = copy.deepcopy(self.hced_rows)
        next(
            row for row in changed if row.get("candidate_id") == "hced-Abeche1983-1"
        )["participants_raw"].append("drift")
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            lane.validate_wave8_chadian_rebels_queue_contracts(changed)

        missing = [
            row for row in self.hced_rows
            if row.get("candidate_id") != "hced-Erdi1986-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            lane.validate_wave8_chadian_rebels_queue_contracts(missing)

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-Future Chadian Rebels1991-1",
                "name": "Future",
                "side_1_raw": "Chadian Rebels",
                "side_2_raw": "Chad",
                "winner_raw": "Chad",
                "loser_raw": "Chadian Rebels",
                "year_low": 1991,
                "year_high": 1991,
                "year_best": 1991,
                "winner_loser_complete": True,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_chadian_rebels_queue_contracts(future)

        adjacent = copy.deepcopy(self.hced_rows)
        adjacent.append(
            {
                "candidate_id": "hced-Future Northern Rebels1991-1",
                "name": "Future North",
                "side_1_raw": "Northern Chadian Rebels",
                "side_2_raw": "Chad",
                "winner_raw": "Chad",
                "loser_raw": "Northern Chadian Rebels",
                "year_low": 1991,
                "year_high": 1991,
                "year_best": 1991,
                "winner_loser_complete": True,
            }
        )
        with self.assertRaisesRegex(ValueError, "adjacent-label inventory changed"):
            lane.validate_wave8_chadian_rebels_queue_contracts(adjacent)

    def test_funnel_audit_pins_all_three_labels(self) -> None:
        self.assertEqual(
            lane.validate_wave8_chadian_rebels_funnel(self.funnel),
            {"funnel_labels": 3, "rows_touched": 8, "sole_blocker_rows": 4},
        )
        changed = copy.deepcopy(self.funnel)
        record = next(
            item for item in changed["labels"] if item["label"] == "chadian rebels"
        )
        record["sole_blocker_events"] += 1
        with self.assertRaisesRegex(ValueError, "funnel field changed"):
            lane.validate_wave8_chadian_rebels_funnel(changed)

    def test_dispositions_are_complete_disjoint_and_conservative(self) -> None:
        self.assertEqual(set(lane.WAVE8_CHADIAN_REBELS_CONTRACTS), set(EXPECTED_PROMOTIONS))
        self.assertEqual(
            set(lane.WAVE8_CHADIAN_REBELS_HOLDS),
            {
                "hced-Abeche1983-1", "hced-Erdi1986-1",
                "hced-Iriba1990-1", "hced-Ouaddai1990-1",
                "hced-Oum Chalouba1983-1",
            },
        )
        self.assertEqual(lane.WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(lane.WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES, {})
        self.assertFalse(
            set(lane.WAVE8_CHADIAN_REBELS_CONTRACTS)
            & set(lane.WAVE8_CHADIAN_REBELS_HOLDS)
        )
        self.assertEqual(
            set(lane.WAVE8_CHADIAN_REBELS_CONTRACTS)
            | set(lane.WAVE8_CHADIAN_REBELS_HOLDS),
            lane.WAVE8_CHADIAN_REBELS_RESERVED_IDS,
        )

    def test_holds_are_unrateable_unknowns_and_never_draws(self) -> None:
        forbidden = {
            "outcome_source_family_ids", "outcome_source_ids", "result_type",
            "side_1_entity_ids", "side_2_entity_ids", "winner_side",
        }
        for candidate_id, item in lane.WAVE8_CHADIAN_REBELS_HOLDS.items():
            self.assertEqual(item["disposition"], "hold", candidate_id)
            self.assertFalse(item["terminal_exclusion"], candidate_id)
            self.assertEqual(item["reviewed_outcome"], "unknown", candidate_id)
            self.assertTrue(item["unknown_is_never_draw"], candidate_id)
            self.assertFalse(forbidden & set(item), candidate_id)
            self.assertIn("never", item["hold_reason"].casefold())
            self.assertIn("draw", item["hold_reason"].casefold())
            self.assertNotIn("winner", item["historical_review"].get("row_resolution", ""))

    def test_adjacent_spelling_ownership_is_explicit(self) -> None:
        dispositions = lane.WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS
        self.assertEqual(set(dispositions), EXPECTED_ADJACENT_IDS)
        self.assertIn("promoted", dispositions["hced-Ati1978-1"]["disposition"])
        self.assertIn("held", dispositions["hced-Erdi1986-1"]["disposition"])
        for candidate_id, item in dispositions.items():
            self.assertEqual(
                item["raw_row_sha256"],
                lane.WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES[candidate_id],
            )
            self.assertEqual(
                item["owner_module"],
                "military_elo.promotion.wave8_chadian_rebels",
            )

    def test_sources_parse_and_outcomes_have_three_independent_families(self) -> None:
        source_by_id = {
            source["id"]: source for source in lane.WAVE8_CHADIAN_REBELS_SOURCES
        }
        self.assertEqual(len(source_by_id), 16)
        self.assertEqual(
            len({source["source_family_id"] for source in source_by_id.values()}),
            16,
        )
        for source in source_by_id.values():
            parsed = Source.from_dict(source)
            self.assertEqual(parsed.id, source["id"])
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"], sorted(set(source["evidence_roles"]))
            )
        for candidate_id, contract in lane.WAVE8_CHADIAN_REBELS_CONTRACTS.items():
            outcome_ids = contract["outcome_source_ids"]
            self.assertGreaterEqual(len(outcome_ids), 3, candidate_id)
            self.assertTrue(set(outcome_ids) <= set(contract["evidence_refs"]))
            self.assertTrue(
                all("outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in outcome_ids)
            )
            measured_families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcome_ids}
            )
            self.assertEqual(measured_families, contract["outcome_source_family_ids"])
            self.assertGreaterEqual(len(measured_families), 3)

    def test_entities_parse_are_alias_free_and_event_year_bounded(self) -> None:
        entities = {entity["id"]: entity for entity in lane.WAVE8_CHADIAN_REBELS_ENTITIES}
        self.assertEqual(len(entities), 9)
        used: set[str] = set()
        for contract in lane.WAVE8_CHADIAN_REBELS_CONTRACTS.values():
            used.update(contract["side_1_entity_ids"])
            used.update(contract["side_2_entity_ids"])
        self.assertEqual(used, set(entities))
        for entity in entities.values():
            parsed = Entity.from_dict(entity)
            self.assertEqual(parsed.start_year, parsed.end_year)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("generic chadian rebels", note)
            self.assertIn("strategic civil-war outcome", note)
            self.assertNotIn(
                normalize_label(entity["name"]),
                {"chadian rebels", "frolinat", "fan", "fap", "gunt", "chad", "libya", "france"},
            )

    def test_contracts_pin_dates_granularity_actors_and_raw_outcomes(self) -> None:
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = lane.WAVE8_CHADIAN_REBELS_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            row = self.owned_rows[candidate_id]
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(canonical["date_text"], expected["date_text"])
            self.assertEqual(canonical["granularity"], expected["granularity"])
            self.assertEqual(contract["event_type"], expected["event_type"])
            self.assertEqual(set(contract["side_1_entity_ids"]), expected["winner"])
            self.assertEqual(set(contract["side_2_entity_ids"]), expected["loser"])
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_promoter_emits_three_parseable_deterministic_events(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 3)
        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            [
                "hced-Ati1978-1",
                "hced-N'Djamena1979-1",
                "hced-N'Djamena1980-1",
            ],
        )
        for event in events:
            parsed = Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            expected = EXPECTED_PROMOTIONS[candidate_id]
            contract = lane.WAVE8_CHADIAN_REBELS_CONTRACTS[candidate_id]
            self.assertEqual(event["id"], f"{EVENT_ID_PREFIX}{_event_slug(candidate_id)}")
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual(event["event_type"], expected["event_type"])
            self.assertEqual(event["reviewed_granularity"], expected["granularity"])
            self.assertEqual(_participant_ids(event, "side_a"), expected["winner"])
            self.assertEqual(_participant_ids(event, "side_b"), expected["loser"])
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(parsed.track, "operational" if candidate_id.endswith("1980-1") else "tactical")
            self.assertTrue(all("draw" not in str(p).casefold() for p in event["participants"]))

    def test_second_ndjamena_is_operational_not_tactical(self) -> None:
        event = next(
            item for item in self._events()
            if item["hced_candidate_id"] == "hced-N'Djamena1980-1"
        )
        self.assertEqual(event["event_type"], "campaign")
        self.assertEqual(event["reviewed_granularity"], "nine_month_urban_campaign")
        operational_dimensions = {
            "campaign_objective", "theater_control", "force_preservation",
            "tempo_initiative", "logistics_sustainment",
        }
        for participant in event["participants"]:
            self.assertEqual(set(participant["outcome"]), operational_dimensions)
            if participant["side"] == "side_a":
                self.assertEqual(participant["termination"], "campaign_victory")
                self.assertEqual(participant["result_class"], "major_operational_victory")
            else:
                self.assertEqual(participant["termination"], "campaign_defeat")
                self.assertEqual(participant["result_class"], "major_operational_defeat")

    def test_promoted_locations_withhold_points_and_retain_country(self) -> None:
        self.assertEqual(
            lane.WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_CHADIAN_REBELS_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            lane.wave8_chadian_rebels_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_CHADIAN_REBELS_CONTRACT_IDS,
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Chad")
            self.assertIn("location_provenance", event)
            Event.from_dict(event)

    def test_iwbd_erdi_twin_is_opposite_and_held(self) -> None:
        disposition = lane.WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS[
            "iwbd-207-80-1650"
        ]
        row = next(
            row for row in self.iwbd_rows if row["candidate_id"] == "iwbd-207-80-1650"
        )
        self.assertEqual(_object_hash(row), disposition["raw_row_sha256"])
        self.assertEqual(row["winner_raw"], "Chad")
        self.assertEqual(
            self.owned_rows["hced-Erdi1986-1"]["winner_raw"],
            "Libya, North Chadian Rebels",
        )
        self.assertEqual(
            disposition["disposition"], "opposite_result_cross_source_twin_held"
        )
        self.assertIn("hced-Erdi1986-1", lane.WAVE8_CHADIAN_REBELS_HOLDS)

    def test_iwbd_fingerprint_and_future_twin_fail_closed(self) -> None:
        changed = copy.deepcopy(self.iwbd_rows)
        next(row for row in changed if row.get("candidate_id") == "iwbd-207-80-1650")[
            "winner_raw"
        ] = "Libya"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint changed"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, changed
            )

        future = copy.deepcopy(self.iwbd_rows)
        future.append(
            {
                "candidate_id": "iwbd-future-ati",
                "name": "Battle of Ati",
                "start_date": "1978-05-19",
                "end_date": "1978-05-20",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed IWBD twin"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, future
            )

    def test_ucdp_inventory_pins_28_strategic_nonduplicates(self) -> None:
        dispositions = lane.WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS
        self.assertEqual(len(dispositions), 28)
        indexed = {row["candidate_id"]: row for row in self.ucdp_rows}
        self.assertEqual(set(dispositions), set(dispositions) & set(indexed))
        scopes = Counter(item["scope"] for item in dispositions.values())
        self.assertEqual(
            scopes,
            Counter(
                {
                    "annual_conflict_record": 6,
                    "annual_dyad_record": 8,
                    "strategic_conflict_episode": 6,
                    "strategic_dyad_episode_or_termination": 8,
                }
            ),
        )
        for candidate_id, disposition in dispositions.items():
            self.assertEqual(_object_hash(indexed[candidate_id]), disposition["raw_row_sha256"])
            self.assertEqual(disposition["conflict_id"], "288")
            self.assertIn("not_named_tactical_duplicate", disposition["disposition"])

    def test_ucdp_missing_and_mutated_boundaries_fail_closed(self) -> None:
        missing = [
            row for row in self.ucdp_rows
            if row.get("candidate_id") != "ucdp-termination-dyad-288-1237"
        ]
        with self.assertRaisesRegex(ValueError, "missing UCDP boundary"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, self.iwbd_rows, (), missing
            )
        changed = copy.deepcopy(self.ucdp_rows)
        next(
            row for row in changed
            if row.get("candidate_id") == "ucdp-termination-dyad-288-1237"
        )["raw"]["d_outcome"] = "5"
        with self.assertRaisesRegex(ValueError, "UCDP fingerprint changed"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, self.iwbd_rows, (), changed
            )

    def test_current_release_boundaries_are_distinct_and_exact(self) -> None:
        indexed = {event["id"]: event for event in self.release_events}
        self.assertEqual(len(lane.WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES), 3)
        for event_id, boundary in lane.WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES.items():
            event = indexed[event_id]
            self.assertEqual(event["name"], boundary["expected_name"])
            self.assertEqual(event["year"], 1987)
            self.assertEqual(event["end_year"], 1987)
            self.assertEqual(
                _participant_ids(event), set(boundary["expected_entity_ids"])
            )
            self.assertNotIn(normalize_label(event["name"]), {"erdi", "ati", "n djamena"})

    def test_integration_validator_accepts_base_or_complete_lane_only(self) -> None:
        _, _, existing = self._installed()
        base = lane.validate_wave8_chadian_rebels_integration_dispositions(
            self.hced_rows, self.iwbd_rows, existing, self.ucdp_rows
        )
        self.assertEqual(base["release_lane_overlap"], 0)
        self.assertEqual(base["ucdp_overlap_dispositions"], 28)
        events = self._events()
        complete = lane.validate_wave8_chadian_rebels_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            [*existing, *events],
            self.ucdp_rows,
        )
        self.assertEqual(complete["release_lane_overlap"], 3)

        with self.assertRaisesRegex(ValueError, "partial or duplicated"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, events[0]],
                self.ucdp_rows,
            )
        with self.assertRaisesRegex(ValueError, "partial or duplicated"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, *events, copy.deepcopy(events[0])],
                self.ucdp_rows,
            )

    def test_integration_rejects_holds_and_future_hced_release_twins(self) -> None:
        held = {
            "id": "bad-held-release",
            "name": "Erdi",
            "year": 1986,
            "end_year": 1986,
            "hced_candidate_id": "hced-Erdi1986-1",
            "participants": [],
        }
        with self.assertRaisesRegex(ValueError, "nonpromotion entered release"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, self.iwbd_rows, [*self.release_events, held]
            )

        hced = copy.deepcopy(self.hced_rows)
        hced.append(
            {
                "candidate_id": "hced-cross-lane-ati1978",
                "name": "Battle of Ati",
                "side_1_raw": "Different actor",
                "side_2_raw": "Different opponent",
                "year_low": 1978,
                "year_high": 1978,
                "year_best": 1978,
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed HCED twin"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                hced, self.iwbd_rows
            )

        release_twin = {
            "id": "foreign-ati-owner",
            "name": "Battle of Ati",
            "year": 1978,
            "end_year": 1978,
            "participants": [],
        }
        with self.assertRaisesRegex(ValueError, "unreviewed current-release twin"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*self.release_events, release_twin],
            )

    def test_integration_rejects_released_ucdp_boundary(self) -> None:
        event = {
            "id": "bad-ucdp-release",
            "name": "Strategic Chad row",
            "year": 1990,
            "end_year": 1990,
            "participants": [],
            "ucdp_candidate_id": "ucdp-termination-dyad-288-1237",
        }
        with self.assertRaisesRegex(ValueError, "UCDP boundary entered release"):
            lane.validate_wave8_chadian_rebels_integration_dispositions(
                self.hced_rows, self.iwbd_rows, [*self.release_events, event]
            )

    def test_installers_are_idempotent_copy_safe_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        lane.install_wave8_chadian_rebels_entities(entities)
        lane.install_wave8_chadian_rebels_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        lane.install_wave8_chadian_rebels_entities(entities)
        lane.install_wave8_chadian_rebels_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)

        fixture = lane.WAVE8_CHADIAN_REBELS_ENTITIES[0]
        entities[fixture["id"]]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_chadian_rebels_entities(entities)
        source = lane.WAVE8_CHADIAN_REBELS_SOURCES[0]
        sources[source["id"]]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_chadian_rebels_sources(sources)

    def test_promoter_is_input_immutable_and_fails_on_entity_or_duplicate_drift(self) -> None:
        entities, _, existing = self._installed()
        rows_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        lane.promote_wave8_chadian_rebels_contracts(self.hced_rows, entities, existing)
        self.assertEqual(self.hced_rows, rows_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)

        missing = copy.deepcopy(entities)
        missing.pop("fap_frolinat_ati_assault_force_1978")
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_chadian_rebels_contracts(self.hced_rows, missing, existing)

        wrong_window = copy.deepcopy(entities)
        wrong_window["fap_frolinat_ati_assault_force_1978"]["start_year"] = 1979
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_chadian_rebels_contracts(
                self.hced_rows, wrong_window, existing
            )

        duplicate = [
            *existing,
            {"id": "foreign", "name": "Ati", "year": 1978, "end_year": 1978},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_chadian_rebels_contracts(
                self.hced_rows, entities, duplicate
            )

    def test_signature_is_independently_reproducible(self) -> None:
        payload = {
            "adjacent_hced_dispositions": lane.WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS,
            "adjacent_row_hashes": lane.WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES,
            "contracts": lane.WAVE8_CHADIAN_REBELS_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "current_release_boundaries": lane.WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES,
            "duplicate_audits": lane.WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS,
            "entities": lane.WAVE8_CHADIAN_REBELS_ENTITIES,
            "exact_row_hashes": lane.WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES,
            "expected_candidate_id_sha256": lane.WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256,
            "expected_candidate_ids": sorted(lane.WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS),
            "funnel_audits": lane.WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS,
            "hced_queue_sha256": lane.WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256,
            "holds": lane.WAVE8_CHADIAN_REBELS_HOLDS,
            "integration_dispositions": lane.WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": lane.WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_queue_sha256": lane.WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256,
            "location_quarantine_reasons": lane.WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": lane.WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                lane.WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": lane.WAVE8_CHADIAN_REBELS_SOURCES,
            "terminal_exclusions": lane.WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS,
            "ucdp_overlap_dispositions": lane.WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS,
            "ucdp_queue_sha256": lane.WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256,
        }
        measured = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(measured, lane.WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, lane.wave8_chadian_rebels_audit_signature())
        self.assertEqual(len(measured), 64)

    def test_counts_cohorts_metadata_and_integration_count_are_exact(self) -> None:
        self.assertEqual(
            lane.wave8_chadian_rebels_counts(),
            {
                "adjacent_hced_rows": 2,
                "country_quarantine_additions": 0,
                "current_release_boundaries": 3,
                "exact_hced_rows": 6,
                "holds": 5,
                "integration_dispositions": 40,
                "iwbd_duplicate_dispositions": 1,
                "new_entities": 9,
                "new_sources": 16,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 8,
                "terminal_exclusions": 0,
                "ucdp_overlap_dispositions": 28,
            },
        )
        self.assertEqual(
            lane.wave8_chadian_rebels_cohort_counts(),
            {
                "abeche_actions_1983": 1,
                "ati_battle_1978": 1,
                "erdi_cross_source_conflict_1986": 1,
                "iriba_actions_1990": 1,
                "ndjamena_first_battle_1979": 1,
                "ndjamena_second_battle_1980": 1,
                "ouaddai_mps_offensive_1990": 1,
                "oum_chalouba_actions_1983": 1,
            },
        )
        self.assertEqual(len(lane.WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS), 40)
        metadata = lane.wave8_chadian_rebels_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_chadian_rebels_counts())
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE,
        )


def _EXACT(value) -> bool:
    return normalize_label(value) == "chadian rebels"


def _event_slug(candidate_id: str) -> str:
    # Mirrors the public ID contract without importing the private slug helper.
    normalized = normalize_label(candidate_id).replace(" ", "_")
    return normalized[:80].rstrip("_")


if __name__ == "__main__":
    unittest.main()
