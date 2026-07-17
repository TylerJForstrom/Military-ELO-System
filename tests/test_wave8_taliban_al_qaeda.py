import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_taliban_al_qaeda as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_taliban_al_qaeda import (
    WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS,
    WAVE8_TALIBAN_AL_QAEDA_CONTRACTS,
    WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_ENTITIES,
    WAVE8_TALIBAN_AL_QAEDA_EXCLUSION_IDS,
    WAVE8_TALIBAN_AL_QAEDA_EXCLUSIONS,
    WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES,
    WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS,
    WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE,
    WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT,
    WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256,
    WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS,
    WAVE8_TALIBAN_AL_QAEDA_HOLDS,
    WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256,
    WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS,
    WAVE8_TALIBAN_AL_QAEDA_NONPROMOTIONS,
    WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES,
    WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS,
    WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES,
    WAVE8_TALIBAN_AL_QAEDA_SOURCES,
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS,
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS,
    WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256,
    install_wave8_taliban_al_qaeda_entities,
    install_wave8_taliban_al_qaeda_sources,
    promote_wave8_taliban_al_qaeda_contracts,
    validate_wave8_taliban_al_qaeda_funnel,
    validate_wave8_taliban_al_qaeda_integration_dispositions,
    validate_wave8_taliban_al_qaeda_queue_contracts,
    wave8_taliban_al_qaeda_audit_signature,
    wave8_taliban_al_qaeda_cohort_counts,
    wave8_taliban_al_qaeda_counts,
    wave8_taliban_al_qaeda_location_quarantine_additions,
    wave8_taliban_al_qaeda_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_taliban_al_qaeda_"


EXPECTED_RAW = {
    "hced-Kunduz2001-1": (
        "Kunduz",
        "Northern Alliance, United States",
        "Taliban, Al Qaeda",
    ),
    "hced-Mazar-i-Sharif2001-1": (
        "Mazar-i-Sharif",
        "United States, United Kingdom, Northern Alliance",
        "Taliban, al Qaeda",
    ),
    "hced-Qala-i-Jangi2001-1": (
        "Qala-i-Jangi",
        "United States, United Kingdom, Northern Alliance",
        "Taliban, al Qaeda",
    ),
    "hced-Tora Bora2001-1": (
        "Tora Bora",
        "United States, United Kingdom, Northern Alliance",
        "Taliban, al Qaeda",
    ),
}


EXPECTED_EVENTS = {
    "hced-Kunduz2001-1": (
        "Siege and surrender of Kunduz (2001)",
        {
            "united_front_kunduz_siege_force_2001",
            "us_special_operations_airpower_kunduz_2001",
        },
        {
            "taliban_kunduz_garrison_2001",
            "al_qaeda_foreign_fighters_kunduz_2001",
        },
    ),
    "hced-Mazar-i-Sharif2001-1": (
        "Capture of Mazar-e Sharif (2001)",
        {
            "united_front_mazar_assault_force_2001",
            "us_special_operations_airpower_mazar_2001",
        },
        {
            "taliban_mazar_garrison_2001",
            "al_qaeda_foreign_fighters_mazar_2001",
        },
    ),
    "hced-Qala-i-Jangi2001-1": (
        "Suppression of the Qala-i-Jangi uprising",
        {
            "united_front_qala_jangi_recapture_force_2001",
            "us_qala_jangi_response_force_2001",
            "uk_qala_jangi_special_forces_2001",
        },
        {
            "taliban_prisoner_uprising_qala_jangi_2001",
            "al_qaeda_prisoner_uprising_qala_jangi_2001",
        },
    ),
    "hced-Tora Bora2001-1": (
        "End of organized resistance at Tora Bora (2001)",
        {
            "ali_zaman_eastern_afghan_tora_bora_force_2001",
            "us_tora_bora_special_operations_airpower_2001",
            "uk_tora_bora_special_forces_2001",
        },
        {
            "taliban_tora_bora_supporting_fighters_2001",
            "al_qaeda_tora_bora_defenders_2001",
        },
    ),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_object_sha256(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Wave8TalibanAlQaedaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data" / "review" / "hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.ucdp_paths = {
            name: ROOT / "data" / "review" / name
            for name in WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256
        }
        cls.ucdp_rows = [
            row for path in cls.ucdp_paths.values() for row in _jsonl(path)
        ]
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.rows_by_id = {
            str(row.get("candidate_id")): row for row in cls.hced_rows
        }

    def _installed(self):
        entity_ids = {str(item["id"]) for item in WAVE8_TALIBAN_AL_QAEDA_ENTITIES}
        entities = {
            str(item["id"]): item
            for item in self.release_entities
            if str(item["id"]) not in entity_ids
        }
        install_wave8_taliban_al_qaeda_entities(entities)
        source_ids = {str(item["id"]) for item in WAVE8_TALIBAN_AL_QAEDA_SOURCES}
        sources = {
            str(item["id"]): item
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        install_wave8_taliban_al_qaeda_sources(sources)
        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_taliban_al_qaeda_contracts(
            self.hced_rows, entities, existing
        )

    def test_locked_queue_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256,
        )
        for name, expected in WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256.items():
            self.assertEqual(
                hashlib.sha256(self.ucdp_paths[name].read_bytes()).hexdigest(),
                expected,
            )

    def test_complete_exact_label_inventory_and_raw_rows_are_pinned(self) -> None:
        exact_ids = {
            str(row.get("candidate_id"))
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "taliban al qaeda"
            or normalize_label(row.get("side_2_raw")) == "taliban al qaeda"
        }
        self.assertEqual(exact_ids, set(EXPECTED_RAW))
        self.assertEqual(exact_ids, WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS)
        for candidate_id, (name, side_1, side_2) in EXPECTED_RAW.items():
            row = self.rows_by_id[candidate_id]
            self.assertEqual((row["name"], row["side_1_raw"], row["side_2_raw"]),
                             (name, side_1, side_2))
            self.assertEqual(row["winner_raw"], side_1)
            self.assertEqual(row["loser_raw"], side_2)
            self.assertEqual((row["year_low"], row["year_high"]), (2001, 2001))
            self.assertIs(row["winner_loser_complete"], True)
            self.assertEqual(
                canonical_hced_row_sha256(row),
                WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES[candidate_id],
            )

    def test_adjacent_actor_and_spelling_boundaries_are_complete(self) -> None:
        self.assertEqual(
            set(WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS),
            {
                "hced-Kabul1996-1",
                "hced-Kabul2001-1",
                "hced-Kandahar2001-1",
                "hced-Operation Anaconda2002-1",
                "hced-Operation Mongoose2003-1",
            },
        )
        for candidate_id, disposition in (
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS.items()
        ):
            self.assertEqual(
                canonical_hced_row_sha256(self.rows_by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )
        self.assertEqual(
            set(WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS),
            {"exact_taliban_lane", "reversed_al_qaeda_taliban_lane"},
        )
        anaconda = self.rows_by_id["hced-Operation Anaconda2002-1"]
        self.assertEqual((anaconda["year_low"], anaconda["year_high"]), (2001, 2001))

    def test_disposition_partition_promotes_all_four_and_invents_nothing(self) -> None:
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS, set(EXPECTED_RAW))
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS, set(EXPECTED_RAW))
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_HOLDS, {})
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS, {})
        self.assertIs(WAVE8_TALIBAN_AL_QAEDA_EXCLUSIONS,
                      WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS)
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_NONPROMOTIONS, {})
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES, {})

    def test_funnel_record_and_validator_are_exact(self) -> None:
        historical_funnel = {
            "labels": [
                {
                    "label": "taliban al qaeda",
                    "event_candidate_id_sha256": (
                        "d645a53ebb045ff8525088633cb44e88561e27deea3092c6ed4fcd283bdabb09"
                    ),
                    "events_touched": 4,
                    "unresolved_side_attempts": 4,
                    "sole_blocker_events": 4,
                    "candidate_ids": [],
                    "time_valid_candidate_ids": [],
                    "failure_cases": {
                        "multiple_time_valid_candidates": 0,
                        "one_wrong_interval_candidate": 0,
                        "policy_denied_window": 0,
                        "resolver_guard_or_tier_conflict": 0,
                        "zero_time_valid_candidates": 4,
                    },
                    "centuries": {"CE_21": 4},
                    "components_touched": 1,
                    "components_bridged": 0,
                    "rated_counterpart_entities": 1,
                }
            ]
        }
        self.assertEqual(
            validate_wave8_taliban_al_qaeda_funnel(historical_funnel),
            {"exact_label_rows": 4, "shared_label_rows": 0, "sole_blocker_rows": 4},
        )
        record = next(
            item
            for item in historical_funnel["labels"]
            if item.get("label") == "taliban al qaeda"
        )
        self.assertEqual(record, WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT)
        tampered = copy.deepcopy(historical_funnel)
        next(item for item in tampered["labels"] if item.get("label") == "taliban al qaeda")[
            "events_touched"
        ] = 5
        with self.assertRaisesRegex(ValueError, "funnel field"):
            validate_wave8_taliban_al_qaeda_funnel(tampered)
        self.assertFalse(
            any(
                row.get("label") == "taliban al qaeda"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Taliban al Qaeda lane must not remain unresolved",
        )

    def test_queue_validator_and_raw_drift_fail_closed(self) -> None:
        self.assertEqual(
            validate_wave8_taliban_al_qaeda_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_dispositions": 5,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        for candidate_id in sorted(WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                rows = copy.deepcopy(self.hced_rows)
                next(row for row in rows if row.get("candidate_id") == candidate_id)[
                    "participants_raw"
                ].append("tamper")
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    validate_wave8_taliban_al_qaeda_queue_contracts(rows)

    def test_sources_are_authoritative_independent_and_model_valid(self) -> None:
        ids = [str(source["id"]) for source in WAVE8_TALIBAN_AL_QAEDA_SOURCES]
        families = [
            str(source["source_family_id"])
            for source in WAVE8_TALIBAN_AL_QAEDA_SOURCES
        ]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(families), len(set(families)))
        self.assertEqual(len(ids), 17)
        for fixture in WAVE8_TALIBAN_AL_QAEDA_SOURCES:
            parsed = Source.from_dict(fixture)
            self.assertEqual(parsed.id, fixture["id"])
            self.assertTrue(fixture["url"].startswith("https://"))
            self.assertNotIn("wikipedia", fixture["url"].casefold())
            self.assertEqual(fixture["accessed"], "2026-07-16")
        publishers = {source["publisher"] for source in WAVE8_TALIBAN_AL_QAEDA_SOURCES}
        self.assertIn("U.S. Army Center of Military History", publishers)
        self.assertIn("United Nations Commission on Human Rights", publishers)
        self.assertIn("House of Commons Library", publishers)

    def test_every_contract_has_four_independent_outcome_families(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_TALIBAN_AL_QAEDA_SOURCES
        }
        used: set[str] = set()
        for fixture in WAVE8_TALIBAN_AL_QAEDA_ENTITIES:
            used.update(map(str, fixture["source_ids"]))
        for contract in WAVE8_TALIBAN_AL_QAEDA_CONTRACTS.values():
            outcomes = list(contract["outcome_source_ids"])
            families = list(contract["outcome_source_family_ids"])
            self.assertGreaterEqual(len(outcomes), 4)
            self.assertGreaterEqual(len(families), 4)
            self.assertEqual(outcomes, sorted(set(outcomes)))
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertEqual(
                families,
                sorted({source_by_id[item]["source_family_id"] for item in outcomes}),
            )
            used.update(map(str, contract["evidence_refs"]))
        for item in WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.values():
            used.update(map(str, item["evidence_refs"]))
        self.assertEqual(used, set(source_by_id))

    def test_entities_are_event_bounded_without_alias_bridges(self) -> None:
        ids = [str(entity["id"]) for entity in WAVE8_TALIBAN_AL_QAEDA_ENTITIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 18)
        for fixture in WAVE8_TALIBAN_AL_QAEDA_ENTITIES:
            entity = Entity.from_dict(fixture)
            self.assertEqual((entity.start_year, entity.end_year), (2001, 2001))
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            note = entity.continuity_note.casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("generic taliban", note)
            self.assertIn("strategic outcome", note)

    def test_compound_label_is_split_only_into_attested_formations(self) -> None:
        consumed: set[str] = set()
        for candidate_id, (name, winners, losers) in EXPECTED_EVENTS.items():
            contract = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS[candidate_id]
            self.assertEqual(contract["canonical_event"]["name"], name)
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(len(losers), 2)
            self.assertFalse(winners & losers)
            consumed.update(winners | losers)
        self.assertEqual(
            consumed,
            {str(entity["id"]) for entity in WAVE8_TALIBAN_AL_QAEDA_ENTITIES},
        )

    def test_mazar_qala_and_tora_actor_boundaries_are_specific(self) -> None:
        mazar = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS["hced-Mazar-i-Sharif2001-1"]
        self.assertFalse(any(item.startswith("uk_") for item in mazar["side_1_entity_ids"]))
        self.assertIn("no reviewed source", mazar["actor_boundary_note"].casefold())
        qala = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS["hced-Qala-i-Jangi2001-1"]
        self.assertIn("uk_qala_jangi_special_forces_2001", qala["side_1_entity_ids"])
        tora = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS["hced-Tora Bora2001-1"]
        self.assertIn(
            "ali_zaman_eastern_afghan_tora_bora_force_2001",
            tora["side_1_entity_ids"],
        )
        self.assertIn("not silently relabeled", next(
            entity["continuity_note"].casefold()
            for entity in WAVE8_TALIBAN_AL_QAEDA_ENTITIES
            if entity["id"] == "ali_zaman_eastern_afghan_tora_bora_force_2001"
        ))

    def test_unknown_is_never_draw_and_tora_scope_is_tactical(self) -> None:
        for candidate_id, contract in WAVE8_TALIBAN_AL_QAEDA_CONTRACTS.items():
            row = self.rows_by_id[candidate_id]
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertNotIn(normalize_label(row["winner_raw"]),
                             {"draw", "inconclusive", "stalemate"})
        tora = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS["hced-Tora Bora2001-1"]["audit_note"].casefold()
        for phrase in ("field control", "bin laden", "escaped", "no inferred victory"):
            self.assertIn(phrase, tora)

    def test_iwbd_twins_are_pinned_and_hced_owns_each_once(self) -> None:
        by_id = {str(row.get("candidate_id")): row for row in self.iwbd_rows}
        self.assertEqual(len(WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS), 4)
        for candidate_id, item in WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS.items():
            row = by_id[candidate_id]
            self.assertEqual(_canonical_object_sha256(row), item["raw_row_sha256"])
            self.assertEqual(row["winner_raw"], item["expected_winner_raw"])
            self.assertEqual(item["disposition"], "duplicate_of_canonical_hced_owner")
            self.assertIn(item["owner_hced_candidate_id"], WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS)

    def test_ucdp_rows_are_pinned_as_strategic_not_tactical(self) -> None:
        by_id = {str(row.get("candidate_id")): row for row in self.ucdp_rows}
        self.assertEqual(len(WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS), 8)
        for candidate_id, item in WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.items():
            self.assertEqual(_canonical_object_sha256(by_id[candidate_id]), item["raw_row_sha256"])
            self.assertIn(item["scope"], {
                "annual_conflict_record", "annual_dyad_record",
                "strategic_conflict_episode", "strategic_dyad_termination",
                "strategic_dyad_episode",
            })
            self.assertEqual(item["disposition"],
                             "related_strategic_record_not_tactical_duplicate")

    def test_integration_validator_accepts_current_artifacts(self) -> None:
        result = validate_wave8_taliban_al_qaeda_integration_dispositions(
            self.hced_rows, self.iwbd_rows, self.release_events, self.ucdp_rows
        )
        self.assertEqual(result["iwbd_duplicate_dispositions"], 4)
        self.assertEqual(result["ucdp_overlap_dispositions"], 8)
        self.assertEqual(result["existing_release_boundaries"], 4)
        self.assertIn(result["release_lane_overlap"], {0, 4})

    def test_release_overlap_is_strictly_all_or_none(self) -> None:
        events = self._events()
        base = [
            event for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        complete = validate_wave8_taliban_al_qaeda_integration_dispositions(
            self.hced_rows, self.iwbd_rows, [*base, *events], self.ucdp_rows
        )
        self.assertEqual(complete["release_lane_overlap"], 4)
        with self.assertRaisesRegex(ValueError, "overlap is partial"):
            validate_wave8_taliban_al_qaeda_integration_dispositions(
                self.hced_rows, self.iwbd_rows, [*base, events[0]], self.ucdp_rows
            )

    def test_duplicate_and_boundary_drift_injections_fail_closed(self) -> None:
        iwbd = copy.deepcopy(self.iwbd_rows)
        twin = copy.deepcopy(next(row for row in iwbd if row["candidate_id"] == "iwbd-225-87-1703"))
        twin["candidate_id"] = "iwbd-injected-tora-bora"
        iwbd.append(twin)
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_taliban_al_qaeda_integration_dispositions(
                self.hced_rows, iwbd, self.release_events, self.ucdp_rows
            )
        ucdp = copy.deepcopy(self.ucdp_rows)
        next(row for row in ucdp if row["candidate_id"] == "ucdp-termination-conflict-418-2358")[
            "raw"
        ]["conflict_id"] = "tamper"
        with self.assertRaisesRegex(ValueError, "UCDP boundary fingerprint"):
            validate_wave8_taliban_al_qaeda_integration_dispositions(
                self.hced_rows, self.iwbd_rows, self.release_events, ucdp
            )
        release = copy.deepcopy(self.release_events)
        release.append({"id": "foreign_tora", "name": "Tora Bora", "year": 2001})
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_taliban_al_qaeda_integration_dispositions(
                self.hced_rows, self.iwbd_rows, release, self.ucdp_rows
            )

    def test_existing_release_boundaries_are_exact(self) -> None:
        by_id = {str(event["id"]): event for event in self.release_events}
        self.assertEqual(len(WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES), 4)
        for event_id, boundary in WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES.items():
            event = by_id[event_id]
            self.assertEqual(event["name"], boundary["expected_name"])
            self.assertEqual(event["year"], boundary["expected_year"])
            self.assertEqual(event["end_year"], boundary["expected_end_year"])
            self.assertEqual(
                {participant["entity_id"] for participant in event["participants"]},
                set(boundary["expected_entity_ids"]),
            )

    def test_promoter_emits_four_model_valid_deterministic_events(self) -> None:
        first = self._events()
        second = self._events()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 4)
        for event in first:
            parsed = Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            name, winners, losers = EXPECTED_EVENTS[candidate_id]
            self.assertEqual(parsed.name, name)
            self.assertEqual(event["id"], EVENT_ID_PREFIX + normalize_label(candidate_id).replace(" ", "_"))
            self.assertEqual(
                {p["entity_id"] for p in event["participants"] if p["side"] == "side_a"},
                winners,
            )
            self.assertEqual(
                {p["entity_id"] for p in event["participants"] if p["side"] == "side_b"},
                losers,
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")

    def test_local_location_quarantine_retains_country_without_global_mutation(self) -> None:
        point_before = set(HCED_POINT_QUARANTINE_IDS)
        country_before = set(HCED_COUNTRY_QUARANTINE_IDS)
        events = self._events()
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS,
                         WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS)
        self.assertEqual(WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS,
                         frozenset())
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Afghanistan")
            reason = WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["retained_country"], "Afghanistan")
        self.assertEqual(set(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(set(HCED_COUNTRY_QUARANTINE_IDS), country_before)
        self.assertEqual(
            wave8_taliban_al_qaeda_location_quarantine_additions(),
            {"country": frozenset(), "point": WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS},
        )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_taliban_al_qaeda_entities(entities)
        install_wave8_taliban_al_qaeda_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        install_wave8_taliban_al_qaeda_entities(entities)
        install_wave8_taliban_al_qaeda_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)
        entities[next(iter(entities))]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_taliban_al_qaeda_entities(entities)
        sources[next(iter(sources))]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_taliban_al_qaeda_sources(sources)

    def test_promoter_fails_on_missing_entity_and_does_not_mutate_inputs(self) -> None:
        entities, _, existing = self._installed()
        rows_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        promote_wave8_taliban_al_qaeda_contracts(self.hced_rows, entities, existing)
        self.assertEqual(self.hced_rows, rows_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)
        entities.pop("al_qaeda_tora_bora_defenders_2001")
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_taliban_al_qaeda_contracts(self.hced_rows, entities, existing)

    def test_signature_counts_metadata_and_public_api_are_deterministic(self) -> None:
        self.assertEqual(
            wave8_taliban_al_qaeda_audit_signature(),
            WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(len(WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE), 64)
        self.assertEqual(
            wave8_taliban_al_qaeda_cohort_counts(),
            {"afghanistan_2001_tactical": 4},
        )
        counts = wave8_taliban_al_qaeda_counts()
        self.assertEqual(counts["promotion_contracts"], 4)
        self.assertEqual(counts["new_entities"], 18)
        self.assertEqual(counts["new_sources"], 17)
        self.assertEqual(counts["integration_dispositions"], 17)
        self.assertEqual(counts["ucdp_overlap_dispositions"], 8)
        metadata = wave8_taliban_al_qaeda_metadata()
        self.assertEqual(metadata["counts"], counts)
        self.assertEqual(metadata["final_audit_signature"],
                         WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(metadata["queue_sha256"]["hced"],
                         WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256)
        self.assertEqual(len(WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS), 17)
        for name in lane.__all__:
            self.assertTrue(hasattr(lane, name), name)


if __name__ == "__main__":
    unittest.main()
