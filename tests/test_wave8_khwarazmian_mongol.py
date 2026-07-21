import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_khwarazmian_mongol as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
KHWAREZM = "clio_tm_khwarezmid_emp_1202_3ad0d483"
MONGOLS = "mongol_empire"
EVENT_ID_PREFIX = "hced_wave8_khwarazmian_mongol_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8KhwarazmianMongolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.cliopatria = _jsonl(
            ROOT / "data/review/cliopatria-entity-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
        }
        lane.install_wave8_khwarazmian_mongol_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_khwarazmian_mongol_contracts(
            self.hced,
            entities,
            existing,
        )

    def _integrated_events(self):
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]

    def test_exact_inventory_row_hashes_and_raw_outcomes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id"))
            in lane.WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES
        }
        self.assertEqual(
            set(rows),
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES),
        )
        self.assertEqual(len(rows), 16)
        for candidate_id, expected_hash in (
            lane.WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(
                    canonical_hced_row_sha256(row),
                    expected_hash,
                )
                for field, value in (
                    lane.WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES[
                        candidate_id
                    ].items()
                ):
                    self.assertEqual(row[field], value)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])

    def test_queue_validation_covers_every_spelling_and_disposition(self) -> None:
        self.assertEqual(
            lane.validate_wave8_khwarazmian_mongol_queue_contracts(self.hced),
            {
                "exact_label_rows": 16,
                "exact_labels": 5,
                "holds": 10,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 16,
            },
        )
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS,
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS,
            {
                candidate_id
                for candidate_ids in (
                    lane.WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS.values()
                )
                for candidate_id in candidate_ids
            },
        )
        self.assertEqual(
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS),
            {
                "khwarezem",
                "khwarezm",
                "khwarezm empire",
                "khwarezm rebels",
                "khwarezmian empire",
            },
        )

    def test_historical_funnel_pins_all_five_exact_labels(self) -> None:
        historical = {"labels": []}
        for expected in lane.WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT.values():
            historical["labels"].append(
                {
                    "candidate_ids": expected["candidate_ids"],
                    "event_candidate_id_sha256": expected[
                        "event_candidate_id_sha256"
                    ],
                    "events_touched": expected["events_touched"],
                    "failure_cases": {
                        "zero_time_valid_candidates": expected[
                            "zero_time_valid_candidates"
                        ]
                    },
                    "label": expected["label"],
                    "rated_counterpart_entities": expected[
                        "rated_counterpart_entities"
                    ],
                    "sole_blocker_events": expected["sole_blocker_events"],
                    "unresolved_side_attempts": expected[
                        "unresolved_side_attempts"
                    ],
                }
            )
        self.assertEqual(
            lane.validate_wave8_khwarazmian_mongol_funnel(historical),
            {
                "events_touched": 16,
                "exact_labels": 5,
                "unresolved_side_attempts": 16,
            },
        )
        promotion = self.release_metadata.get("promotion", {})
        if "accepted_wave8_khwarazmian_mongol_hced_events" not in promotion:
            self.assertEqual(
                lane.validate_wave8_khwarazmian_mongol_funnel(self.funnel),
                {
                    "events_touched": 16,
                    "exact_labels": 5,
                    "unresolved_side_attempts": 16,
                },
            )

    def test_existing_registry_identity_is_reused_at_its_exact_window(self) -> None:
        candidate = next(
            row
            for row in self.cliopatria
            if row.get("candidate_id") == "cliopatria-1229"
        )
        self.assertEqual(candidate["canonical_name_candidate"], "Khwarezmid Empire")
        self.assertEqual(candidate["seshat_ids"], ["tm_khwarezmid_emp"])
        self.assertEqual((candidate["start_year"], candidate["end_year"]), (1202, 1235))
        self.assertEqual(candidate["aliases"], [])
        self.assertEqual(
            candidate["temporal_coverage_groups"],
            [{"start_year": 1202, "end_year": 1235}],
        )

        entity = lane.WAVE8_KHWARAZMIAN_MONGOL_ENTITIES[0]
        self.assertEqual(entity["id"], KHWAREZM)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1202, 1235))
        self.assertEqual(entity["aliases"], [])
        self.assertEqual(entity["predecessors"], [])
        Entity.from_dict(entity)

    def test_no_generic_label_alias_or_window_change_is_opened(self) -> None:
        entity = lane.WAVE8_KHWARAZMIAN_MONGOL_ENTITIES[0]
        aliases = {normalize_label(alias) for alias in entity["aliases"]}
        self.assertFalse(aliases)
        self.assertTrue(
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS).isdisjoint(
                aliases
            )
        )
        self.assertNotIn(
            normalize_label(entity["name"]),
            lane.WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS,
        )
        self.assertIn("retaining its 1202-1235 source window exactly", entity["continuity_note"])

    def test_sources_are_canonical_parseable_and_family_distinct(self) -> None:
        self.assertEqual(len(lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES), 5)
        expected_urls = {
            "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/csi-books/GreatCommanders.pdf",
            "https://www.cambridge.org/core/books/the-cambridge-history-of-iran/D0BEE51C0C239F497ADBC0CA18796A5B",
            "https://doi.org/10.17863/CAM.87960",
            "https://www.iranicaonline.org/articles/jalal-al-din-kvarazmsahi-mengbirni/",
            "https://archive.org/details/historyoftheworl011691mbp",
        }
        self.assertEqual(
            {str(source["url"]) for source in lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES},
            expected_urls,
        )
        families = set()
        for source in lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES:
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertTrue(source["source_family_id"])
            families.add(source["source_family_id"])
        self.assertEqual(len(families), 5)

    def test_each_promotion_has_two_or_more_event_specific_outcome_families(self) -> None:
        source_by_id = {
            str(source["id"]): source
            for source in lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES
        }
        for candidate_id, contract in (
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                outcome_ids = contract["outcome_source_ids"]
                self.assertGreaterEqual(len(outcome_ids), 2)
                self.assertEqual(
                    len(contract["outcome_source_family_ids"]),
                    len(outcome_ids),
                )
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(
                        {
                            source_by_id[source_id]["source_family_id"]
                            for source_id in outcome_ids
                        }
                    ),
                )
                self.assertEqual(
                    set(contract["event_evidence_roles"]),
                    set(outcome_ids),
                )
                self.assertTrue(
                    all(
                        role.strip()
                        for role in contract["event_evidence_roles"].values()
                    )
                )
                self.assertTrue(
                    all(
                        "outcome" in source_by_id[source_id]["evidence_roles"]
                        for source_id in outcome_ids
                    )
                )

    def test_exact_six_events_promote_with_pinned_names_and_years(self) -> None:
        events = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        self.assertEqual(
            set(events),
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        )
        self.assertEqual(
            {candidate_id: (event["name"], event["year"]) for candidate_id, event in events.items()},
            {
                "hced-Bokhara1220-1": ("Siege and Capture of Bukhara", 1220),
                "hced-Indus1221-1": ("Battle of the Indus", 1221),
                "hced-Khojend1220-1": ("Siege of Khujand", 1220),
                "hced-Otrar1219-1": ("Siege of Otrar", 1219),
                "hced-Parwan Durrah1221-1": ("Battle of Parwan", 1221),
                "hced-Samarkand1220-1": ("Siege of Samarkand", 1220),
            },
        )
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in events.values())
        )

    def test_emitted_outcomes_preserve_raw_polarity_without_overrides(self) -> None:
        events = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS[candidate_id]
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                outcomes = {
                    participant["entity_id"]: participant["termination"]
                    for participant in event["participants"]
                }
                winner = (
                    KHWAREZM
                    if candidate_id == "hced-Parwan Durrah1221-1"
                    else MONGOLS
                )
                loser = MONGOLS if winner == KHWAREZM else KHWAREZM
                self.assertEqual(outcomes[winner], "engagement_victory")
                self.assertEqual(outcomes[loser], "engagement_defeat")
                self.assertNotIn("draw", event["summary"].casefold())
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")

    def test_promoted_events_fit_both_identity_windows_and_parse(self) -> None:
        entities, _ = self._installed()
        self.assertEqual(
            (entities[KHWAREZM]["start_year"], entities[KHWAREZM]["end_year"]),
            (1202, 1235),
        )
        self.assertEqual(
            (entities[MONGOLS]["start_year"], entities[MONGOLS]["end_year"]),
            (1206, 1294),
        )
        for event in self._events():
            self.assertGreaterEqual(event["year"], 1206)
            self.assertLessEqual(event["end_year"], 1235)
            self.assertEqual(event["event_type"], "engagement")
            Event.from_dict(event)

    def test_all_ten_boundary_rows_have_explicit_unknown_not_draw_holds(self) -> None:
        self.assertEqual(len(lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS), 10)
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
            & lane.WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS,
            set(),
        )
        for candidate_id, hold in lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(hold["disposition"], "hold")
                self.assertEqual(hold["result_type"], "unknown")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertTrue(hold["hold_category"])
                self.assertTrue(hold["hold_reason"])

    def test_massacre_date_counterpart_and_identity_boundaries_are_exact(self) -> None:
        massacre_scope = {
            "hced-Bamian1221-1",
            "hced-Gurganj1221-1",
            "hced-Hamadan1220-1",
            "hced-Merv1221-1",
        }
        self.assertTrue(
            all(
                lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS[candidate_id][
                    "hold_category"
                ]
                == "massacre_or_city_capture_scope_not_clean_tactical_battle"
                for candidate_id in massacre_scope
            )
        )
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS["hced-Jand1218-1"][
                "hold_category"
            ],
            "source_year_precedes_reviewed_siege_chronology",
        )
        self.assertIn(
            "counterpart",
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS["hced-Andkhui1205-1"][
                "hold_category"
            ],
        )
        for candidate_id in {"hced-Dabusiyya1032-1", "hced-Shahr Rey1194-1"}:
            self.assertEqual(
                lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS[candidate_id][
                    "hold_category"
                ],
                "row_predates_selected_khwarezmid_empire_interval",
            )
        self.assertIn(
            "rebel_faction",
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS["hced-Hazarasp1017-1"][
                "hold_category"
            ],
        )
        self.assertIn(
            "post_imperial_mercenary",
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLDS["hced-Jerusalem1244-1"][
                "hold_category"
            ],
        )

    def test_no_hold_or_massacre_row_is_emitted(self) -> None:
        emitted = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        self.assertTrue(
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS.isdisjoint(emitted)
        )
        rows = {str(row["candidate_id"]): row for row in self.hced}
        self.assertTrue(
            all(
                rows[candidate_id]["massacre_raw"] == "No"
                for candidate_id in emitted
            )
        )

    def test_wikidata_twins_are_pinned_discovery_only_without_outcomes(self) -> None:
        self.assertEqual(
            lane.validate_wave8_khwarazmian_mongol_discovery_dispositions(
                self.wikidata
            ),
            {"discovery_nonrating_twins": 6, "discovery_promotions": 0},
        )
        self.assertEqual(
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS),
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        )
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata
            if str(row.get("candidate_id"))
            in lane.WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES
        }
        self.assertEqual(len(by_id), 6)
        for row in by_id.values():
            self.assertEqual(row["winners"], [])
            self.assertIs(row["do_not_rate_automatically"], True)
            self.assertEqual(row["review_status"], "needs_review")

    def test_current_hced_iwbd_and_release_have_no_other_probable_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_khwarazmian_mongol_integration_dispositions(
                self.hced,
                self.iwbd,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_injected_cross_source_twins_fail_closed(self) -> None:
        hced = copy.deepcopy(self.hced)
        hced.append(
            {
                "candidate_id": "hced-future-bukhara-twin",
                "name": "Siege of Bukhara",
                "year_best": 1220,
                "side_1_raw": "unrelated",
                "side_2_raw": "unrelated",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_khwarazmian_mongol_integration_dispositions(
                hced,
                self.iwbd,
            )

        iwbd = copy.deepcopy(self.iwbd)
        iwbd.append(
            {
                "candidate_id": "iwbd-future-parwan-twin",
                "name": "Battle of Parwan",
                "year": 1221,
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_khwarazmian_mongol_integration_dispositions(
                self.hced,
                iwbd,
            )

        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_khwarazmian_mongol_integration_dispositions(
                self.hced,
                self.iwbd,
                [{"id": "release-twin", "name": "Battle of the Indus", "year": 1221}],
            )

    def test_row_identity_and_duplicate_promotion_guards_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Parwan Durrah1221-1"
        )
        row["winner_raw"] = "Mongols"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_khwarazmian_mongol_queue_contracts(tampered)

        entities, existing = self._installed()
        short = copy.deepcopy(entities)
        short[KHWAREZM]["end_year"] = 1219
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_khwarazmian_mongol_contracts(
                self.hced,
                short,
                existing,
            )

        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_khwarazmian_mongol_contracts(
                self.hced,
                entities,
                [
                    *existing,
                    {
                        "id": "already-owned",
                        "name": "unrelated",
                        "year": 1220,
                        "hced_candidate_id": "hced-Bokhara1220-1",
                    },
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_khwarazmian_mongol_contracts(
                self.hced,
                entities,
                [
                    *existing,
                    {"id": "name-twin", "name": "Siege of Otrar", "year": 1219},
                ],
            )

    def test_installers_are_idempotent_copy_safe_and_collision_safe(self) -> None:
        entities = {}
        lane.install_wave8_khwarazmian_mongol_entities(entities)
        lane.install_wave8_khwarazmian_mongol_entities(entities)
        self.assertEqual(set(entities), {KHWAREZM})
        entities[KHWAREZM]["name"] = "drift"
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_ENTITIES[0]["name"],
            "Khwarezmid Empire",
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_khwarazmian_mongol_entities(entities)

        sources = {}
        lane.install_wave8_khwarazmian_mongol_sources(sources)
        lane.install_wave8_khwarazmian_mongol_sources(sources)
        self.assertEqual(len(sources), 5)
        source_id = "wave8_khwarazmian_mongol_juvaini_boyle"
        sources[source_id]["title"] = "drift"
        fixture = next(
            item
            for item in lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES
            if item["id"] == source_id
        )
        self.assertNotEqual(sources[source_id]["title"], fixture["title"])
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_khwarazmian_mongol_sources(sources)

    def test_promoted_only_points_are_withheld_but_country_and_provenance_remain(self) -> None:
        expected_countries = {
            "hced-Bokhara1220-1": "Uzbekistan",
            "hced-Indus1221-1": "Pakistan",
            "hced-Khojend1220-1": "Tajikistan",
            "hced-Otrar1219-1": "Kazakhstan",
            "hced-Parwan Durrah1221-1": "Afghanistan",
            "hced-Samarkand1220-1": "Uzbekistan",
        }
        self.assertEqual(
            lane.WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_KHWARAZMIAN_MONGOL_COUNTRY_QUARANTINE_ADDITIONS
        )
        self.assertEqual(
            set(lane.WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        )
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                expected_countries[candidate_id],
            )
            self.assertIn("location_provenance", event)
            self.assertEqual(
                lane.WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS[
                    candidate_id
                ]["actions"],
                ["withhold_point"],
            )

    def test_current_release_artifacts_are_strictly_all_or_none(self) -> None:
        integrated = self._integrated_events()
        promotion = self.release_metadata.get("promotion", {})
        count_key = "accepted_wave8_khwarazmian_mongol_hced_events"
        self.assertIn(
            len(integrated),
            {0, len(lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS)},
        )
        self.assertEqual(bool(integrated), count_key in promotion)
        release_candidate_ids = {
            str(event.get("hced_candidate_id")) for event in self.release_events
        }
        self.assertTrue(
            lane.WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS.isdisjoint(
                release_candidate_ids
            )
        )

        release_entities = {
            str(entity["id"]): entity for entity in self.release_entities
        }
        release_source_ids = {
            str(source["id"]) for source in self.release_sources
        }
        lane_source_ids = {
            str(source["id"])
            for source in lane.WAVE8_KHWARAZMIAN_MONGOL_SOURCES
        }
        registry_entities = {
            str(entity["id"]): entity for entity in self.registry["entities"]
        }

        if not integrated:
            self.assertNotIn(KHWAREZM, release_entities)
            self.assertTrue(lane_source_ids.isdisjoint(release_source_ids))
            self.assertEqual(registry_entities[KHWAREZM]["status"], "unrated")
            self.assertEqual(
                registry_entities[KHWAREZM]["identity_status"],
                "source_candidate",
            )
            return

        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in integrated},
            lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        )
        self.assertEqual(len({str(event["id"]) for event in integrated}), 6)
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in integrated)
        )
        self.assertIn(KHWAREZM, release_entities)
        self.assertEqual(release_entities[KHWAREZM]["aliases"], [])
        self.assertLessEqual(lane_source_ids, release_source_ids)
        self.assertEqual(promotion[count_key], 6)
        self.assertEqual(
            promotion["wave8_khwarazmian_mongol_candidate_ids"],
            sorted(lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS),
        )
        self.assertEqual(
            len(promotion["wave8_khwarazmian_mongol_holds"]),
            10,
        )
        self.assertEqual(registry_entities[KHWAREZM]["status"], "rated")
        self.assertEqual(registry_entities[KHWAREZM]["identity_status"], "curated")
        self.assertEqual(
            self.registry["coverage"][
                "candidate_keyed_wave8_khwarazmian_mongol_hced_events"
            ],
            6,
        )

    def test_signature_counts_cohorts_and_metadata_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_khwarazmian_mongol_audit_signature(),
            lane.WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_khwarazmian_mongol_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_twins": 6,
                "holds": 10,
                "new_entities": 1,
                "new_sources": 5,
                "newly_rated_events": 6,
                "outcome_overrides": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 16,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_khwarazmian_mongol_cohort_counts(),
            {
                "campaign_date_or_counterpart_holds_1205_1218": 2,
                "mongol_invasion_massacre_scope_holds_1220_1221": 4,
                "mongol_invasion_promotions_1219_1221": 6,
                "post_empire_mercenary_hold_1244": 1,
                "pre_empire_identity_holds_1017_1194": 3,
            },
        )
        metadata = lane.wave8_khwarazmian_mongol_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_khwarazmian_mongol_counts())
        self.assertEqual(
            metadata["final_audit_signature"],
            lane.WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(lane.WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS),
        )
        self.assertEqual(
            metadata["hold_candidate_ids"],
            sorted(lane.WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS),
        )


if __name__ == "__main__":
    unittest.main()
