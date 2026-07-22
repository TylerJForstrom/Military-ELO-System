import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_al_qaeda_taliban as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import expected_exact_hced_win_participants


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_al_qaeda_taliban_"

EXPECTED_EVENTS = {
    "hced-Operation Anaconda2002-1": {
        "name": "Operation Anaconda",
        "year": 2002,
        "scale": "battle",
        "scale_level": 3,
        "side_a": {
            "us_cjtf_mountain_anaconda_force_2002",
            "zia_haidar_afghan_militia_anaconda_force_2002",
            "canadian_3_ppcli_sniper_anaconda_contingent_2002",
            "australian_sas_anaconda_contingent_2002",
        },
        "side_b": {
            "al_qaeda_shahi_kot_force_2002",
            "taliban_shahi_kot_contingent_2002",
        },
    },
    "hced-Operation Mongoose2003-1": {
        "name": "Operation Mongoose",
        "year": 2003,
        "scale": "skirmish",
        "scale_level": 1,
        "side_a": {
            "us_mongoose_ground_force_2003",
            "afghan_militia_mongoose_contingent_2003",
            "epaf_mongoose_strike_detachment_2003",
        },
        "side_b": {"adi_ghar_mongoose_opposition_force_2003"},
    },
}

GENERIC_ENTITY_IDS = {
    "afghanistan",
    "al_qaeda",
    "australia",
    "canada",
    "hizb_i_islami_afghanistan",
    "islamic_republic_afghanistan",
    "taliban",
    "united_kingdom",
    "united_states",
    "us_united_states_of_america_contemporary",
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


class Wave8AlQaedaTalibanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        review = ROOT / "data" / "review"
        cls.hced_path = review / "hced-candidates.jsonl"
        cls.iwbd_path = review / "iwbd-candidates.jsonl"
        cls.iwd_path = review / "iwd-1.21-candidates.jsonl"
        cls.wikidata_battle_path = review / "wikidata-battle-candidates.jsonl"
        cls.wikidata_generic_path = review / "wikidata-candidates.jsonl"
        cls.ucdp_paths = {
            name: review / name
            for name in lane.WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256
        }
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.iwd_rows = _jsonl(cls.iwd_path)
        cls.ucdp_rows = [
            row for path in cls.ucdp_paths.values() for row in _jsonl(path)
        ]
        cls.wikidata_battle_rows = _jsonl(cls.wikidata_battle_path)
        cls.wikidata_generic_rows = _jsonl(cls.wikidata_generic_path)
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.hced_by_id = {
            str(row.get("candidate_id")): row for row in cls.hced_rows
        }

    def _installed(self):
        entities = {str(item["id"]): copy.deepcopy(item) for item in self.release_entities}
        lane.install_wave8_al_qaeda_taliban_entities(entities)
        sources = {str(item["id"]): copy.deepcopy(item) for item in self.release_sources}
        lane.install_wave8_al_qaeda_taliban_sources(sources)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_al_qaeda_taliban_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def _integration(self, **overrides):
        values = {
            "hced_rows": self.hced_rows,
            "iwbd_rows": self.iwbd_rows,
            "iwd_rows": self.iwd_rows,
            "ucdp_rows": self.ucdp_rows,
            "wikidata_battle_rows": self.wikidata_battle_rows,
            "wikidata_generic_rows": self.wikidata_generic_rows,
            "existing_events": self.release_events,
            "release_sources": self.release_sources,
        }
        values.update(overrides)
        return lane.validate_wave8_al_qaeda_taliban_integration_dispositions(
            **values
        )

    def test_locked_queue_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_AL_QAEDA_TALIBAN_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_AL_QAEDA_TALIBAN_IWBD_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwd_path.read_bytes()).hexdigest(),
            lane.WAVE8_AL_QAEDA_TALIBAN_IWD_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.wikidata_battle_path.read_bytes()).hexdigest(),
            lane.WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.wikidata_generic_path.read_bytes()).hexdigest(),
            lane.WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_QUEUE_SHA256,
        )
        for name, expected in lane.WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256.items():
            self.assertEqual(
                hashlib.sha256(self.ucdp_paths[name].read_bytes()).hexdigest(),
                expected,
            )

    def test_exact_label_inventory_and_raw_year_bug_are_pinned(self) -> None:
        exact_ids = {
            str(row.get("candidate_id"))
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "al qaeda taliban"
            or normalize_label(row.get("side_2_raw")) == "al qaeda taliban"
        }
        self.assertEqual(exact_ids, lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS)
        anaconda = self.hced_by_id["hced-Operation Anaconda2002-1"]
        self.assertEqual(
            (anaconda["year_low"], anaconda["year_best"], anaconda["year_high"]),
            (2001, 2001, 2001),
        )
        self.assertEqual(anaconda["source_record_id"], "Operation Anaconda2002")
        self.assertEqual(anaconda["scale_raw"], "1")
        mongoose = self.hced_by_id["hced-Operation Mongoose2003-1"]
        self.assertEqual(
            (mongoose["year_low"], mongoose["year_best"], mongoose["year_high"]),
            (2003, 2003, 2003),
        )
        for candidate_id in exact_ids:
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                lane.WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES[candidate_id],
            )
            self.assertIs(
                self.hced_by_id[candidate_id]["do_not_rate_automatically"],
                True,
            )

    def test_historical_funnel_contract_is_exact(self) -> None:
        historical = {"labels": [copy.deepcopy(lane.WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT)]}
        self.assertEqual(
            lane.validate_wave8_al_qaeda_taliban_funnel(historical),
            {"exact_label_rows": 2, "shared_label_rows": 0, "sole_blocker_rows": 2},
        )
        tampered = copy.deepcopy(historical)
        tampered["labels"][0]["events_touched"] = 3
        with self.assertRaisesRegex(ValueError, "funnel field"):
            lane.validate_wave8_al_qaeda_taliban_funnel(tampered)
        current = [
            row
            for row in self.funnel.get("labels", [])
            if row.get("label") == "al qaeda taliban"
        ]
        if current:
            self.assertEqual(current, historical["labels"])

    def test_queue_validator_fails_closed_on_raw_drift(self) -> None:
        self.assertEqual(
            lane.validate_wave8_al_qaeda_taliban_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_dispositions": 7,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 9,
                "exact_label_rows": 2,
                "holds": 1,
                "lane_exclusions": 6,
            },
        )
        for candidate_id in lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS:
            rows = copy.deepcopy(self.hced_rows)
            next(row for row in rows if row["candidate_id"] == candidate_id)[
                "participants_raw"
            ].append("tamper")
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    lane.validate_wave8_al_qaeda_taliban_queue_contracts(rows)

    def test_exact_promotion_inventory_has_no_lane_holds_or_exclusions(self) -> None:
        self.assertEqual(lane.WAVE8_AL_QAEDA_TALIBAN_RESERVED_IDS,
                         lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS)
        self.assertEqual(lane.WAVE8_AL_QAEDA_TALIBAN_HOLD_IDS, frozenset())
        self.assertEqual(
            lane.WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS,
            frozenset(),
        )
        self.assertEqual(lane.WAVE8_AL_QAEDA_TALIBAN_EXCLUSION_IDS, frozenset())
        self.assertEqual(len(lane.WAVE8_AL_QAEDA_TALIBAN_AUDITED_HOLD_IDS), 33)
        self.assertEqual(len(lane.WAVE8_AL_QAEDA_TALIBAN_AUDITED_EXCLUSION_IDS), 15)

    def test_exhaustive_disposition_partition_is_2_33_15(self) -> None:
        self.assertEqual(
            lane.WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS,
            {
                "hced": {"promote": 2, "hold": 1, "exclude": 6, "total": 9},
                "iwbd": {"promote": 0, "hold": 0, "exclude": 6, "total": 6},
                "iwd": {"promote": 0, "hold": 5, "exclude": 0, "total": 5},
                "ucdp": {"promote": 0, "hold": 27, "exclude": 0, "total": 27},
                "wikidata_battle": {"promote": 0, "hold": 0, "exclude": 3, "total": 3},
                "wikidata_generic": {"promote": 0, "hold": 0, "exclude": 0, "total": 0},
                "all": {"promote": 2, "hold": 33, "exclude": 15, "total": 50},
            },
        )
        self.assertEqual(len(lane.WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS), 50)
        self.assertTrue(
            all(
                item["automated_rating_authorized"] is False
                for item in lane.WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS.values()
            )
        )

    def test_all_hced_and_cross_dataset_row_hashes_are_pinned(self) -> None:
        hced = self.hced_by_id
        for candidate_id, item in lane.WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS.items():
            self.assertEqual(
                canonical_hced_row_sha256(hced[candidate_id]),
                item["raw_row_sha256"],
            )
        datasets = (
            (self.iwbd_rows, lane.WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS),
            (self.iwd_rows, lane.WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS),
            (self.ucdp_rows, lane.WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS),
            (
                self.wikidata_battle_rows,
                lane.WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
            ),
        )
        for rows, dispositions in datasets:
            by_id = {str(row["candidate_id"]): row for row in rows}
            for candidate_id, item in dispositions.items():
                self.assertEqual(
                    _canonical_object_sha256(by_id[candidate_id]),
                    item["raw_row_sha256"],
                )
                self.assertIs(by_id[candidate_id]["do_not_rate_automatically"], True)

    def test_sources_are_nine_new_eight_families_plus_one_reuse(self) -> None:
        source_ids = [str(source["id"]) for source in lane.WAVE8_AL_QAEDA_TALIBAN_SOURCES]
        families = {
            str(source["source_family_id"])
            for source in lane.WAVE8_AL_QAEDA_TALIBAN_SOURCES
        }
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual((len(source_ids), len(families)), (9, 8))
        self.assertNotIn("wave8_taliban_al_qaeda_army_oef", source_ids)
        for fixture in lane.WAVE8_AL_QAEDA_TALIBAN_SOURCES:
            source = Source.from_dict(fixture)
            self.assertEqual(source.id, fixture["id"])
            self.assertTrue(source.url.startswith("https://"))
            self.assertNotIn("wikipedia", source.url.casefold())
        self.assertEqual(
            lane.validate_wave8_al_qaeda_taliban_reused_sources(self.release_sources),
            {"reused_sources": 1},
        )

    def test_reused_army_source_drift_fails_closed(self) -> None:
        sources = copy.deepcopy(self.release_sources)
        reused = next(
            source
            for source in sources
            if source["id"] == "wave8_taliban_al_qaeda_army_oef"
        )
        reused["title"] = "tamper"
        with self.assertRaisesRegex(ValueError, "reused source changed"):
            lane.validate_wave8_al_qaeda_taliban_reused_sources(sources)

    def test_entities_are_ten_alias_free_one_year_boundaries(self) -> None:
        entity_ids = [str(entity["id"]) for entity in lane.WAVE8_AL_QAEDA_TALIBAN_ENTITIES]
        self.assertEqual(len(entity_ids), len(set(entity_ids)))
        self.assertEqual(len(entity_ids), 10)
        self.assertFalse(set(entity_ids) & GENERIC_ENTITY_IDS)
        years = []
        for fixture in lane.WAVE8_AL_QAEDA_TALIBAN_ENTITIES:
            entity = Entity.from_dict(fixture)
            self.assertEqual(entity.start_year, entity.end_year)
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            self.assertIn("no rating is inherited", entity.continuity_note.casefold())
            years.append(entity.start_year)
        self.assertEqual(years.count(2002), 6)
        self.assertEqual(years.count(2003), 4)

    def test_anaconda_contract_pins_year_scale_granularity_and_scope(self) -> None:
        contract = lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[
            "hced-Operation Anaconda2002-1"
        ]
        canonical = contract["canonical_event"]
        self.assertEqual((canonical["year_low"], canonical["year_high"]), (2002, 2002))
        self.assertEqual(canonical["principal_start_date"], "2002-03-02")
        self.assertEqual(canonical["principal_end_date"], "2002-03-11")
        self.assertEqual(canonical["clearance_through_date"], "2002-03-18")
        self.assertEqual(canonical["operation_over_by_date"], "2002-03-19")
        self.assertEqual(canonical["date_precision"], "day_range_source_variance")
        self.assertEqual(contract["expected_scale_level"], 3)
        self.assertIs(contract["source_date_override"], True)
        self.assertIs(contract["source_scale_override"], True)
        self.assertIs(contract["source_outcome_override"], False)
        self.assertEqual(contract["result_type"], "win")
        note = contract["audit_note"].casefold()
        for phrase in ("many opposing fighters escaped", "local objective", "no strategic defeat"):
            self.assertIn(phrase, note)
        self.assertFalse(
            any(
                token in entity_id
                for entity_id in contract["side_1_entity_ids"]
                for token in ("united_kingdom", "british", "uk_")
            )
        )

    def test_mongoose_contract_preserves_dates_and_source_conflict(self) -> None:
        contract = lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[
            "hced-Operation Mongoose2003-1"
        ]
        canonical = contract["canonical_event"]
        self.assertEqual((canonical["year_low"], canonical["year_high"]), (2003, 2003))
        self.assertEqual(canonical["initial_contact_date"], "2003-01-27")
        self.assertEqual(canonical["organized_clearance_start_date"], "2003-01-28")
        self.assertEqual(canonical["last_attested_date"], "2003-02-11")
        self.assertIs(canonical["closure_unknown"], True)
        self.assertEqual(canonical["date_precision"], "open_day_range_source_variance")
        self.assertEqual(contract["expected_scale_level"], 1)
        self.assertIs(contract["source_date_override"], False)
        self.assertIs(contract["source_scale_override"], False)
        self.assertEqual(
            contract["side_2_entity_ids"],
            ["adi_ghar_mongoose_opposition_force_2003"],
        )
        boundary = contract["actor_boundary_note"].casefold()
        for phrase in ("hig", "hekmatyar", "taliban", "no hig"):
            self.assertIn(phrase, boundary)

    def test_unknown_is_never_draw_and_discovery_never_supplies_outcome(self) -> None:
        for candidate_id, contract in lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACTS.items():
            row = self.hced_by_id[candidate_id]
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertNotIn(
                normalize_label(row["winner_raw"]),
                {"draw", "inconclusive", "stalemate", "unknown"},
            )
            for source_id in contract["outcome_source_ids"]:
                self.assertFalse(
                    any(token in source_id for token in ("iwbd", "iwd", "ucdp", "wikidata"))
                )

    def test_promoter_emits_two_model_valid_deterministic_events(self) -> None:
        first = self._events()
        second = self._events()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)
        by_candidate = {event["hced_candidate_id"]: event for event in first}
        self.assertEqual(set(by_candidate), set(EXPECTED_EVENTS))
        for candidate_id, expected in EXPECTED_EVENTS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertEqual(event["id"], EVENT_ID_PREFIX + normalize_label(candidate_id).replace(" ", "_"))
            self.assertEqual((event["name"], event["year"], event["end_year"]),
                             (expected["name"], expected["year"], expected["year"]))
            self.assertEqual(event["scale"], expected["scale"])
            self.assertEqual(
                {p["entity_id"] for p in event["participants"] if p["side"] == "side_a"},
                expected["side_a"],
            )
            self.assertEqual(
                {p["entity_id"] for p in event["participants"] if p["side"] == "side_b"},
                expected["side_b"],
            )

    def test_scale_override_rebuilds_every_participant_vector(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        for candidate_id, expected in EXPECTED_EVENTS.items():
            contract = lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[candidate_id]
            rebuilt = expected_exact_hced_win_participants(
                contract["side_1_entity_ids"],
                contract["side_2_entity_ids"],
                confidence=contract["confidence"],
                scale_level=expected["scale_level"],
                lane_name="Wave 8 exact al Qaeda Taliban actor audit",
            )
            self.assertEqual(events[candidate_id]["participants"], rebuilt)
        anaconda = events["hced-Operation Anaconda2002-1"]
        mongoose = events["hced-Operation Mongoose2003-1"]
        for participant in anaconda["participants"]:
            self.assertAlmostEqual(participant["national_scale"], 0.42)
        for participant in mongoose["participants"]:
            self.assertAlmostEqual(participant["national_scale"], 0.22)
        self.assertEqual((anaconda["decisiveness"], anaconda["geographic_scope"]), (0.72, 0.35))
        self.assertEqual((mongoose["decisiveness"], mongoose["geographic_scope"]), (0.6, 0.17))

    def test_no_generic_identity_leaks_into_participants(self) -> None:
        emitted_ids = {
            participant["entity_id"]
            for event in self._events()
            for participant in event["participants"]
        }
        fixture_ids = {entity["id"] for entity in lane.WAVE8_AL_QAEDA_TALIBAN_ENTITIES}
        self.assertEqual(emitted_ids, fixture_ids)
        self.assertFalse(emitted_ids & GENERIC_ENTITY_IDS)
        self.assertEqual(len(emitted_ids), 10)

    def test_location_quarantine_withholds_two_points_and_retains_country(self) -> None:
        point_before = set(HCED_POINT_QUARANTINE_IDS)
        country_before = set(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS,
        )
        self.assertEqual(
            lane.WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS,
            frozenset(),
        )
        self.assertEqual(
            lane.WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS,
            {
                "hced-Operation Anaconda2002-1": (
                    "hced-Operation Anaconda2002-1\t"
                    "hced_wave8_al_qaeda_taliban_hced_operation_anaconda2002_1\t"
                    "geometry\tbroad_campaign_centroid_proxy"
                ),
                "hced-Operation Mongoose2003-1": (
                    "hced-Operation Mongoose2003-1\t"
                    "hced_wave8_al_qaeda_taliban_hced_operation_mongoose2003_1\t"
                    "geometry\tcandidate_keyed_point_not_independently_verified"
                ),
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Afghanistan")
            self.assertIn("location_provenance", event)
        self.assertEqual(set(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(set(HCED_COUNTRY_QUARANTINE_IDS), country_before)

    def test_integration_validator_accepts_all_fifty_dispositions(self) -> None:
        self.assertEqual(
            self._integration(),
            {
                "audited_candidates": 50,
                "hced_dispositions": 9,
                "iwbd_dispositions": 6,
                "iwd_dispositions": 5,
                "ucdp_dispositions": 27,
                "wikidata_battle_dispositions": 3,
                "wikidata_generic_dispositions": 0,
                "release_lane_overlap": 2,
                "automated_discovery_ratings": 0,
            },
        )

    def test_iwbd_and_iwd_drift_injections_fail_closed(self) -> None:
        iwbd = copy.deepcopy(self.iwbd_rows)
        next(row for row in iwbd if row["candidate_id"] == "iwbd-225-87-1699")["name"] = "tamper"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint"):
            self._integration(iwbd_rows=iwbd)
        iwd = copy.deepcopy(self.iwd_rows)
        next(row for row in iwd if row["candidate_id"] == "iwd-243")["parent_war_id"] = "tamper"
        with self.assertRaisesRegex(ValueError, "IWD fingerprint"):
            self._integration(iwd_rows=iwd)

    def test_ucdp_taliban_dyad_starts_after_mongoose(self) -> None:
        row = next(
            row
            for row in self.ucdp_rows
            if row["candidate_id"] == "ucdp-dyadic-26.1-735-2003-2095"
        )
        self.assertEqual(row["raw"]["start_date2"], "2003-02-14")
        self.assertGreater(row["raw"]["start_date2"], "2003-02-11")
        ucdp = copy.deepcopy(self.ucdp_rows)
        next(
            row
            for row in ucdp
            if row["candidate_id"] == "ucdp-dyadic-26.1-735-2003-2095"
        )["raw"]["start_date2"] = "2003-01-27"
        with self.assertRaisesRegex(ValueError, "UCDP fingerprint"):
            self._integration(ucdp_rows=ucdp)

    def test_wikidata_duplicates_nesting_and_false_positive_are_nonrating(self) -> None:
        dispositions = lane.WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS
        self.assertEqual(
            dispositions["Q1476042"]["owner_event_id"],
            "hced_wave8_al_qaeda_taliban_hced_operation_anaconda2002_1",
        )
        self.assertEqual(
            dispositions["Q4872492"]["nesting_owner_event_id"],
            "hced_wave8_al_qaeda_taliban_hced_operation_anaconda2002_1",
        )
        self.assertEqual(
            dispositions["Q281145"]["disposition"],
            "exclude_lexical_false_positive",
        )
        wikidata = copy.deepcopy(self.wikidata_battle_rows)
        next(row for row in wikidata if row["candidate_id"] == "Q1476042")[
            "winners"
        ] = [{"label": "invented"}]
        with self.assertRaisesRegex(ValueError, "Wikidata battle fingerprint"):
            self._integration(wikidata_battle_rows=wikidata)

    def test_generic_wikidata_near_hit_injection_fails_closed(self) -> None:
        generic = copy.deepcopy(self.wikidata_generic_rows)
        injected = copy.deepcopy(generic[0])
        injected["candidate_id"] = "Q-injected-mongoose"
        injected["name"] = "Operation Mongoose"
        generic.append(injected)
        with self.assertRaisesRegex(ValueError, "generic Wikidata near hit"):
            self._integration(wikidata_generic_rows=generic)

    def test_release_overlap_is_strictly_all_or_none(self) -> None:
        complete = self._integration()
        self.assertEqual(complete["release_lane_overlap"], 2)

        without_lane = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
        ]
        absent = self._integration(existing_events=without_lane)
        self.assertEqual(absent["release_lane_overlap"], 0)

        events = self._events()
        with self.assertRaisesRegex(ValueError, "overlap is partial"):
            self._integration(existing_events=[*without_lane, events[0]])

    def test_nested_or_duplicate_release_injection_fails_closed(self) -> None:
        injected = {
            "id": "foreign_takur_ghar",
            "name": "Battle of Takur Ghar",
            "year": 2002,
        }
        with self.assertRaisesRegex(ValueError, "existing-release near hit"):
            self._integration(existing_events=[*self.release_events, injected])

    def test_nonrating_discovery_row_cannot_be_released(self) -> None:
        injected = {
            "id": "foreign_iwd_rating",
            "name": "Foreign IWD rating",
            "year": 1900,
            "source_candidate_id": "iwd-243",
        }
        with self.assertRaisesRegex(ValueError, "nonrating discovery row was released"):
            self._integration(existing_events=[*self.release_events, injected])

    def test_existing_release_owners_are_byte_pinned(self) -> None:
        by_id = {str(event["id"]): event for event in self.release_events}
        self.assertEqual(len(lane.WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES), 8)
        for event_id, boundary in lane.WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES.items():
            self.assertEqual(
                _canonical_object_sha256(by_id[event_id]),
                boundary["canonical_object_sha256"],
            )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        lane.install_wave8_al_qaeda_taliban_entities(entities)
        lane.install_wave8_al_qaeda_taliban_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        lane.install_wave8_al_qaeda_taliban_entities(entities)
        lane.install_wave8_al_qaeda_taliban_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)
        entities[next(iter(entities))]["name"] = "tamper"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_al_qaeda_taliban_entities(entities)
        sources[next(iter(sources))]["title"] = "tamper"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_al_qaeda_taliban_sources(sources)

    def test_promoter_is_nonmutating_and_missing_entity_fails_closed(self) -> None:
        entities, _, existing = self._installed()
        rows_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        lane.promote_wave8_al_qaeda_taliban_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        self.assertEqual(self.hced_rows, rows_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)
        entities.pop("adi_ghar_mongoose_opposition_force_2003")
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_al_qaeda_taliban_contracts(
                self.hced_rows,
                entities,
                existing,
            )

    def test_signature_counts_metadata_and_public_api_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_al_qaeda_taliban_audit_signature(),
            lane.WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(len(lane.WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE), 64)
        self.assertEqual(
            lane.wave8_al_qaeda_taliban_cohort_counts(),
            {"afghanistan_2002_2003_tactical": 2},
        )
        counts = lane.wave8_al_qaeda_taliban_counts()
        self.assertEqual(
            counts,
            {
                "audited_candidates": 50,
                "promotion_contracts": 2,
                "newly_rated_events": 2,
                "participant_rows": 10,
                "new_entities": 10,
                "new_sources": 9,
                "new_source_families": 8,
                "reused_sources": 1,
                "holds": 33,
                "lane_exclusions": 15,
                "point_quarantine_additions": 2,
                "country_quarantine_additions": 0,
                "automated_discovery_ratings": 0,
                "source_date_overrides": 1,
                "source_scale_overrides": 1,
                "source_outcome_overrides": 0,
            },
        )
        metadata = lane.wave8_al_qaeda_taliban_metadata()
        self.assertEqual(metadata["counts"], counts)
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_al_qaeda_taliban_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS,
            },
        )
        for name in lane.__all__:
            self.assertTrue(hasattr(lane, name), name)


if __name__ == "__main__":
    unittest.main()
