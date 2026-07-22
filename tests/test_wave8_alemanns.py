import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_alemanns as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_alemanns_"

JULIAN_ROMANS = "julian_roman_field_army_argentoratum_357"
CHNODOMARIUS_HOST = "chnodomarius_alemannic_confederate_host_argentoratum_357"
GRATIAN_GENERALS = "nannienus_mallobaudes_roman_field_army_argentaria_378"
PRIARIUS_LENTIENSES = "priarius_lentiensian_alemannic_host_argentaria_378"

EXPECTED_HASHES = {
    "hced-Argentoratum357-1": (
        "de208a00966d2d4cb5ef2cdab6a39df2edbe0f46d0494325b2c3e1f2e4d749b4"
    ),
    "hced-Argentoratum378-1": (
        "1d7ffd2c7857abe013030f1a05500d31efef0eb408c53dffdb73d2743b50b596"
    ),
}

EXPECTED_DISCOVERY_HASHES = {
    "Q1367199": "09087135a5f51c2c73178e79a6da9f52e1d963d22d159fc9d60762da2fa634b2",
    "Q767605": "8b89c3b2d273fac8958783f838e19d6824351d23595f321506d3a0d77fd73637",
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


def _historical_funnel():
    record = copy.deepcopy(lane.WAVE8_ALEMANNS_FUNNEL_AUDIT)
    zero = record.pop("zero_time_valid_candidates")
    record["failure_cases"] = {"zero_time_valid_candidates": zero}
    return {"labels": [record]}


class Wave8AlemannsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata_rows = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "alemanns"
            or normalize_label(row.get("side_2_raw")) == "alemanns"
        ]

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_ALEMANNS_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_ALEMANNS_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ALEMANNS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_alemanns_entities(entities)
        lane.install_wave8_alemanns_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_alemanns_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_raw_hashes_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_ALEMANNS_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertEqual(row["winner_raw"], "Rome")
                self.assertEqual(row["loser_raw"], "Alemanns")

    def test_queue_partition_is_exactly_two_promotions(self) -> None:
        self.assertEqual(
            lane.validate_wave8_alemanns_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 2,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(lane.WAVE8_ALEMANNS_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_ALEMANNS_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_ALEMANNS_HOLDS)
        self.assertFalse(lane.WAVE8_ALEMANNS_TERMINAL_EXCLUSIONS)

    def test_historical_funnel_pin_is_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_alemanns_funnel(_historical_funnel()),
            {
                "events_touched": 2,
                "sole_blocker_events": 2,
                "zero_time_valid_candidates": 2,
            },
        )
        self.assertEqual(
            lane.WAVE8_ALEMANNS_FUNNEL_AUDIT["event_candidate_id_sha256"],
            "fcdc555ad21a1ae808fd222cb2e258b4439ec4939a282fb221fe6d4f96a64e05",
        )

    def test_four_identities_are_alias_free_and_event_bounded(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_ALEMANNS_ENTITIES}
        self.assertEqual(
            set(entities),
            {
                JULIAN_ROMANS,
                CHNODOMARIUS_HOST,
                GRATIAN_GENERALS,
                PRIARIUS_LENTIENSES,
            },
        )
        expected_years = {
            JULIAN_ROMANS: 357,
            CHNODOMARIUS_HOST: 357,
            GRATIAN_GENERALS: 378,
            PRIARIUS_LENTIENSES: 378,
        }
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    (expected_years[entity_id], expected_years[entity_id]),
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("no aliases", entity["continuity_note"])
                Entity.from_dict(entity)

    def test_install_adds_only_the_four_new_identities(self) -> None:
        lane_ids = {str(item["id"]) for item in lane.WAVE8_ALEMANNS_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_ids
        }
        before = copy.deepcopy(entities)
        lane.install_wave8_alemanns_entities(entities)
        self.assertEqual(set(entities) - set(before), lane_ids)
        for entity_id in before:
            self.assertEqual(entities[entity_id], before[entity_id])

    def test_exactly_three_new_sources_and_two_reused_sources_are_pinned(self) -> None:
        new_ids = {str(item["id"]) for item in lane.WAVE8_ALEMANNS_SOURCES}
        reused_ids = set(lane.WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES)
        self.assertEqual(
            new_ids,
            {
                "wave8_alemanns_ammianus_book_31",
                "wave8_alemanns_drijvers_teitler_378_chronology",
                "wave8_alemanns_ross_strasbourg",
            },
        )
        self.assertEqual(
            reused_ids,
            {
                "wave8_alemanni_ammianus_book_16",
                "wave8_alemanni_drinkwater_alamanni_rome",
            },
        )
        self.assertFalse(new_ids & reused_ids)
        for source in lane.WAVE8_ALEMANNS_SOURCES:
            Source.from_dict(source)
        source_by_id = {str(item["id"]): item for item in self.release_sources}
        self.assertEqual(
            lane.validate_wave8_alemanns_reused_sources(source_by_id),
            {"reused_sources": 2},
        )

    def test_each_outcome_has_three_independent_source_families(self) -> None:
        all_allowed = {
            *lane.WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES,
            *(str(item["id"]) for item in lane.WAVE8_ALEMANNS_SOURCES),
        }
        for candidate_id, contract in lane.WAVE8_ALEMANNS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    contract["outcome_source_ids"],
                    contract["evidence_refs"],
                )
                self.assertEqual(len(contract["outcome_source_family_ids"]), 3)
                self.assertLessEqual(set(contract["evidence_refs"]), all_allowed)
                self.assertLessEqual(
                    set(contract["date_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_canonical_names_and_month_precision_do_not_conflate_battles(self) -> None:
        expected = {
            "hced-Argentoratum357-1": (
                "Battle of Argentoratum (Strasbourg)",
                "August 357",
                "month",
            ),
            "hced-Argentoratum378-1": (
                "Battle of Argentaria",
                "mid-June 378",
                "month_uncertain",
            ),
        }
        for candidate_id, values in expected.items():
            canonical = lane.WAVE8_ALEMANNS_CONTRACTS[candidate_id]["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["date_precision"],
                ),
                values,
            )
        second = lane.WAVE8_ALEMANNS_CONTRACTS["hced-Argentoratum378-1"]
        self.assertNotIn("strasbourg", normalize_label(second["canonical_event"]["name"]))
        self.assertEqual(
            second["historical_review"]["source_name_disposition"],
            "corrected_from_argentoratum_to_argentaria",
        )

    def test_promotions_emit_exact_tactical_winners_and_losers(self) -> None:
        events = {str(item["hced_candidate_id"]): item for item in self._events()}
        expected = {
            "hced-Argentoratum357-1": ({JULIAN_ROMANS}, {CHNODOMARIUS_HOST}),
            "hced-Argentoratum378-1": ({GRATIAN_GENERALS}, {PRIARIUS_LENTIENSES}),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winners, losers) in expected.items():
            event = events[candidate_id]
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "interstate_limited")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["scale"], "battle")
            self.assertEqual(
                {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_victory"
                },
                winners,
            )
            self.assertEqual(
                {
                    item["entity_id"]
                    for item in event["participants"]
                    if item["termination"] == "engagement_defeat"
                },
                losers,
            )
            Event.from_dict(event)

    def test_unknown_is_never_draw_and_no_outcome_is_reversed(self) -> None:
        for contract in lane.WAVE8_ALEMANNS_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        for event in self._events():
            self.assertNotEqual(event["decisiveness"], 0.32)
            self.assertFalse(
                any(
                    "inconclusive" in str(item["termination"])
                    for item in event["participants"]
                )
            )

    def test_both_points_are_withheld_but_france_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ALEMANNS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ALEMANNS_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_ALEMANNS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_ALEMANNS_CONTRACT_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "France")
            self.assertIn("location_provenance", event)

    def test_emitted_events_have_no_raw_name_aliases(self) -> None:
        events = {str(item["hced_candidate_id"]): item for item in self._events()}
        self.assertEqual(events["hced-Argentoratum357-1"]["aliases"], [])
        self.assertEqual(events["hced-Argentoratum378-1"]["aliases"], [])
        self.assertEqual(
            events["hced-Argentoratum378-1"]["name"],
            "Battle of Argentaria",
        )

    def test_wikidata_twins_are_fingerprinted_discovery_only(self) -> None:
        by_id = {
            str(row["candidate_id"]): row
            for row in self.wikidata_rows
            if str(row.get("candidate_id")) in EXPECTED_DISCOVERY_HASHES
        }
        self.assertEqual(set(by_id), set(EXPECTED_DISCOVERY_HASHES))
        for candidate_id, expected_hash in EXPECTED_DISCOVERY_HASHES.items():
            row = by_id[candidate_id]
            self.assertEqual(_full_row_sha256(row), expected_hash)
            self.assertIs(row["do_not_rate_automatically"], True)
            self.assertEqual(row["winners"], [])
        self.assertEqual(
            lane.validate_wave8_alemanns_discovery_dispositions(
                self.wikidata_rows
            ),
            {
                "discovery_nonrating_records": 2,
                "discovery_promotions": 0,
                "probable_duplicates": 2,
                "unknown_never_draw_rows": 2,
            },
        )
        for candidate_id in EXPECTED_DISCOVERY_HASHES:
            disposition = lane.WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS[candidate_id]
            self.assertIs(disposition["rating_authority"], False)
            self.assertEqual(
                disposition["outcome_disposition"],
                "unknown_never_draw",
            )

    def test_iwbd_strasbourg_is_pinned_as_a_distinct_1870_nonauthority(self) -> None:
        self.assertEqual(
            lane.validate_wave8_alemanns_iwbd_dispositions(self.iwbd_rows),
            {
                "distinct_later_iwbd_records": 1,
                "iwbd_promotions": 0,
                "iwbd_rating_authorities": 0,
            },
        )
        disposition = lane.WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS[
            "iwbd-58-20-217"
        ]
        self.assertIs(disposition["rating_authority"], False)
        self.assertIn("1870", disposition["relationship"])
        self.assertIsNone(disposition["hced_candidate_id"])

    def test_cross_source_duplicate_audit_is_clear(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_alemanns_integration_dispositions(
                self.hced_rows,
                self.wikidata_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "discovery_nonrating_records": 2,
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_distinct_nonrating_records": 1,
                "iwbd_probable_twins": 0,
                "wikidata_probable_twins": 0,
            },
        )

    def test_unreviewed_release_twin_fails_closed(self) -> None:
        _, _, existing = self._installed()
        planted = {
            "id": "planted-argentaria-twin",
            "name": "Battle of Argentovaria",
            "year": 378,
        }
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_alemanns_integration_dispositions(
                self.hced_rows,
                self.wikidata_rows,
                self.iwbd_rows,
                [*existing, planted],
            )

    def test_hced_discovery_and_iwbd_drift_fail_closed(self) -> None:
        hced = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in hced
            if row.get("candidate_id") == "hced-Argentoratum378-1"
        )["winner_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_alemanns_queue_contracts(hced)

        discovery = copy.deepcopy(self.wikidata_rows)
        next(
            row for row in discovery if row.get("candidate_id") == "Q767605"
        )["winners"] = [{"label": "Western Roman Empire"}]
        with self.assertRaisesRegex(ValueError, "discovery fingerprint changed"):
            lane.validate_wave8_alemanns_discovery_dispositions(discovery)

        iwbd = copy.deepcopy(self.iwbd_rows)
        next(
            row for row in iwbd if row.get("candidate_id") == "iwbd-58-20-217"
        )["name"] = "Argentaria"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint changed"):
            lane.validate_wave8_alemanns_iwbd_dispositions(iwbd)

    def test_missing_reused_source_and_fixture_collisions_fail_closed(self) -> None:
        sources = {str(item["id"]): copy.deepcopy(item) for item in self.release_sources}
        sources.pop("wave8_alemanni_ammianus_book_16")
        with self.assertRaisesRegex(ValueError, "missing reused source"):
            lane.install_wave8_alemanns_sources(sources)

        entities, sources, _ = self._installed()
        entities[JULIAN_ROMANS]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_alemanns_entities(entities)
        sources["wave8_alemanns_ross_strasbourg"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_alemanns_sources(sources)

    def test_duplicate_promotion_fails_closed(self) -> None:
        entities, _, existing = self._installed()
        events = lane.promote_wave8_alemanns_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted|duplicate event"):
            lane.promote_wave8_alemanns_contracts(
                self.hced_rows,
                entities,
                [*existing, *events],
            )

    def test_signature_counts_and_metadata_are_sealed(self) -> None:
        self.assertEqual(
            lane.wave8_alemanns_audit_signature(),
            "3d4bd6bf2bbc387b2b44c20d9b85a7ab306375b2a747b745f90bfd4717c03696",
        )
        self.assertEqual(
            lane.wave8_alemanns_audit_signature(),
            lane.WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_alemanns_counts(),
            {
                "country_quarantine_additions": 0,
                "discovery_nonrating_records": 2,
                "holds": 0,
                "integration_dispositions": 3,
                "iwbd_nonrating_records": 1,
                "new_entities": 4,
                "new_sources": 3,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reused_sources": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
                "unknown_discovery_outcomes": 2,
            },
        )
        self.assertEqual(
            lane.wave8_alemanns_cohort_counts(),
            {"roman_alemannic_contests_357_378": 2},
        )
        metadata = lane.wave8_alemanns_metadata()
        self.assertEqual(metadata["counts"], lane.wave8_alemanns_counts())
        self.assertEqual(len(metadata["integration_dispositions"]), 3)
        self.assertEqual(metadata["hold_candidate_ids"], [])
        self.assertEqual(metadata["terminal_exclusion_candidate_ids"], [])


if __name__ == "__main__":
    unittest.main()
