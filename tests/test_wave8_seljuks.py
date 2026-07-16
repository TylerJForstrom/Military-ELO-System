import copy
import hashlib
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_seljuks import (
    WAVE8_SELJUKS_CONTRACT_IDS,
    WAVE8_SELJUKS_CONTRACTS,
    WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS,
    WAVE8_SELJUKS_ENTITIES,
    WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS,
    WAVE8_SELJUKS_FINAL_AUDIT_SIGNATURE,
    WAVE8_SELJUKS_HOLD_IDS,
    WAVE8_SELJUKS_HOLDS,
    WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS,
    WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SELJUKS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_SELJUKS_OUTCOME_OVERRIDES,
    WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SELJUKS_RESERVED_IDS,
    WAVE8_SELJUKS_SOURCES,
    WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS,
    install_wave8_seljuks_entities,
    install_wave8_seljuks_sources,
    promote_wave8_seljuks_contracts,
    validate_wave8_seljuks_integration_dispositions,
    validate_wave8_seljuks_queue_contracts,
    wave8_seljuks_audit_signature,
    wave8_seljuks_cohort_counts,
    wave8_seljuks_counts,
    wave8_seljuks_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_seljuks_"
GREAT_SELJUK_ID = "clio_ir_seljuk_sultanate_1040_577da931"
MONGOL_EMPIRE_ID = "mongol_empire"
RUM_KILIJ_ID = "rum_sultanate_kilij_arslan_i_1092_1107"
PEOPLES_CRUSADE_ID = "peoples_crusade_asia_minor_force_1096"
RUM_MESUD_ID = "rum_sultanate_mesud_i_1116_1156"
GERMAN_CRUSADE_ID = "conrad_iii_german_crusader_army_1147"
ZENGI_ID = "zengid_mosul_aleppo_imad_al_din_1127_1146"
EDESSA_ID = "county_edessa_joscelin_ii_1131_1150"
NUR_AL_DIN_ID = "zengid_aleppo_nur_al_din_1146_1154"
RUM_KAYKHUSRAW_ID = "rum_sultanate_kaykhusraw_ii_1237_1246"
BASASIRI_FORCE_ID = "al_basasiri_fatimid_aligned_field_force_1060"


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


EXPECTED_RAW_LABELS = {
    "hced-Baghdad1055-1": ("Seljuks", "Abbasid Caliphate", "Seljuks"),
    "hced-Civetot1096-1": ("Seljuks", "People's Crusaders", "Seljuks"),
    "hced-Dorylaeum1147-1": ("Seljuks", "Germany", "Seljuks"),
    "hced-Edessa1144-1": ("Seljuks", "County of Edessa", "Seljuks"),
    "hced-Edessa1146-1": ("Seljuks", "County of Edessa", "Seljuks"),
    "hced-Elasa1167-1": ("Seljuks", "Crusaders, Egyptian Rebels", "Seljuks"),
    "hced-Hasankale1048-1": ("Seljuks", "Byzantium", "Seljuks"),
    "hced-Kose Dagh1243-1": ("Mongols", "Seljuks", "Mongols"),
    "hced-Kufah1060-1": ("Arslan al-Basasiri", "Seljuks", "Arslan al-Basasiri"),
}


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Civetot1096-1": ({RUM_KILIJ_ID}, {PEOPLES_CRUSADE_ID}),
    "hced-Dorylaeum1147-1": ({RUM_MESUD_ID}, {GERMAN_CRUSADE_ID}),
    "hced-Edessa1144-1": ({ZENGI_ID}, {EDESSA_ID}),
    "hced-Edessa1146-1": ({NUR_AL_DIN_ID}, {EDESSA_ID}),
    "hced-Kose Dagh1243-1": ({MONGOL_EMPIRE_ID}, {RUM_KAYKHUSRAW_ID}),
    "hced-Kufah1060-1": ({GREAT_SELJUK_ID}, {BASASIRI_FORCE_ID}),
}


EXPECTED_DATES = {
    "hced-Civetot1096-1": ("day", "21 October 1096"),
    "hced-Dorylaeum1147-1": ("day", "26 October 1147"),
    "hced-Edessa1144-1": ("day_range", "28 November-24 December 1144"),
    "hced-Edessa1146-1": ("day_range", "27 October-3 November 1146"),
    "hced-Kose Dagh1243-1": ("day", "26 June 1243"),
    "hced-Kufah1060-1": ("day", "15 January 1060"),
}


EXPECTED_WINDOWS = {
    RUM_KILIJ_ID: (1092, 1107),
    PEOPLES_CRUSADE_ID: (1096, 1096),
    RUM_MESUD_ID: (1116, 1156),
    GERMAN_CRUSADE_ID: (1147, 1147),
    ZENGI_ID: (1127, 1146),
    EDESSA_ID: (1131, 1150),
    NUR_AL_DIN_ID: (1146, 1154),
    RUM_KAYKHUSRAW_ID: (1237, 1246),
    BASASIRI_FORCE_ID: (1060, 1060),
}


class Wave8SeljuksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        new_entity_ids = {str(item["id"]) for item in WAVE8_SELJUKS_ENTITIES}
        entities = {
            str(item["id"]): item
            for item in self.release_entities
            if str(item["id"]) not in new_entity_ids
        }
        install_wave8_seljuks_entities(entities)

        new_source_ids = {str(item["id"]) for item in WAVE8_SELJUKS_SOURCES}
        sources = {
            str(item["id"]): item
            for item in self.release_sources
            if str(item["id"]) not in new_source_ids
        }
        install_wave8_seljuks_sources(sources)
        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_SELJUKS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_seljuks_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_complete_inventory_signature_counts_and_cohorts(self) -> None:
        payload = {
            "contracts": WAVE8_SELJUKS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_SELJUKS_ENTITIES,
            "expected_candidate_ids": sorted(WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS),
            "holds": WAVE8_SELJUKS_HOLDS,
            "integration_dispositions": WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_SELJUKS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_SELJUKS_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_SELJUKS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_seljuks_audit_signature(), independent)
        self.assertEqual(WAVE8_SELJUKS_CONTRACT_IDS, set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertEqual(WAVE8_SELJUKS_HOLD_IDS, set(EXPECTED_RAW_LABELS) - set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertEqual(WAVE8_SELJUKS_RESERVED_IDS, set(EXPECTED_RAW_LABELS))
        self.assertEqual(WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS, {"hced-Baghdad1055-1"})
        self.assertEqual(
            wave8_seljuks_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "holds": 3,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 9,
                "new_sources": 17,
                "newly_rated_events": 6,
                "outcome_overrides": 1,
                "point_quarantine_additions": 2,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 9,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            wave8_seljuks_cohort_counts(),
            {
                "bayju_rum_campaign_1243": 1,
                "kilij_arslan_peoples_crusade_1096": 1,
                "mesud_second_crusade_1147": 1,
                "nur_al_din_edessa_1146": 1,
                "tughril_basasiri_iraq_1060": 1,
                "zengid_edessa_1144": 1,
            },
        )

    def test_all_and_only_nine_exact_seljuks_rows_are_hash_pinned(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Seljuks"
            or row.get("side_2_raw") == "Seljuks"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_LABELS))
        for candidate_id, row in exact_rows.items():
            expected = EXPECTED_RAW_LABELS[candidate_id]
            self.assertEqual(
                (row["side_1_raw"], row["side_2_raw"], row["winner_raw"]),
                expected,
            )
            disposition = (
                WAVE8_SELJUKS_CONTRACTS.get(candidate_id)
                or WAVE8_SELJUKS_HOLDS[candidate_id]
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                disposition["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_seljuks_queue_contracts(self.hced_rows),
            {"promotion_contracts": 6, "holds": 3, "reviewed_hced_rows": 9},
        )

    def test_queue_inventory_fails_closed_on_mutation_or_absence(self) -> None:
        changed = copy.deepcopy(self.hced_rows)
        next(
            row for row in changed if row["candidate_id"] == "hced-Kufah1060-1"
        )["winner_raw"] = "Seljuks"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_seljuks_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Elasa1167-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_seljuks_queue_contracts(missing)

    def test_holds_and_exclusion_never_contain_a_result_or_invent_a_draw(self) -> None:
        self.assertEqual(WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS, {"hced-Baghdad1055-1"})
        self.assertIn("noncompetitive", WAVE8_SELJUKS_HOLDS["hced-Baghdad1055-1"]["hold_category"])
        self.assertIn("inconclusive", WAVE8_SELJUKS_HOLDS["hced-Elasa1167-1"]["hold_category"])
        self.assertIn("contradictory", WAVE8_SELJUKS_HOLDS["hced-Hasankale1048-1"]["hold_category"])
        forbidden = {"result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids"}
        for hold in WAVE8_SELJUKS_HOLDS.values():
            self.assertFalse(forbidden & set(hold))
            if "draw" in hold["hold_reason"].casefold():
                self.assertIn(
                    "not converted into a draw",
                    hold["hold_reason"].casefold(),
                )
            self.assertTrue(hold["evidence_refs"])

    def test_entities_are_bounded_distinct_and_parseable(self) -> None:
        source_ids = {str(source["id"]) for source in WAVE8_SELJUKS_SOURCES}
        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SELJUKS_ENTITIES}
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entity_by_id.items()
            },
            EXPECTED_WINDOWS,
        )
        rum_ids = {RUM_KILIJ_ID, RUM_MESUD_ID, RUM_KAYKHUSRAW_ID}
        self.assertEqual(len(rum_ids), 3)
        self.assertTrue(rum_ids <= set(entity_by_id))
        self.assertNotEqual(ZENGI_ID, NUR_AL_DIN_ID)
        for entity in WAVE8_SELJUKS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotIn(entity["name"].casefold(), {"seljuks", "seljuk turks", "germany", "muslims"})
            self.assertTrue(set(entity["source_ids"]) <= source_ids)

        entities, _, _ = self._installed()
        self.assertIn(GREAT_SELJUK_ID, entities)
        self.assertIn(MONGOL_EMPIRE_ID, entities)
        for entity_id in entity_by_id:
            Entity.from_dict(entities[entity_id])

    def test_sources_roles_families_and_installation_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_SELJUKS_SOURCES}
        self.assertEqual(len(source_by_id), 17)
        allowed_domains = {
            "academic.oup.com",
            "assets.cambridge.org",
            "belgeler.gov.tr",
            "dergipark.org.tr",
            "islamansiklopedisi.org.tr",
            "kutuphane.ttk.gov.tr",
            "sourcebooks.web.fordham.edu",
            "www.cambridge.org",
            "www.iranicaonline.org",
            "www.thetbs.org",
        }
        for source in WAVE8_SELJUKS_SOURCES:
            Source.from_dict(source)
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
            self.assertIn(urlsplit(source["url"]).netloc, allowed_domains)

        for candidate_id, contract in WAVE8_SELJUKS_CONTRACTS.items():
            outcome_ids = list(contract["outcome_source_ids"])
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)))
            self.assertEqual(outcome_ids, contract["evidence_refs"])
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2, candidate_id)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted({source_by_id[item]["source_family_id"] for item in outcome_ids}),
            )
            for source_id in outcome_ids:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        _, sources, _ = self._installed()
        for source_id in source_by_id:
            Source.from_dict(sources[source_id])

    def test_dates_sides_and_only_direct_outcome_reversal_are_explicit(self) -> None:
        self.assertEqual(set(WAVE8_SELJUKS_OUTCOME_OVERRIDES), {"hced-Kufah1060-1"})
        for candidate_id, contract in WAVE8_SELJUKS_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["date_precision"], canonical["date_text"]),
                EXPECTED_DATES[candidate_id],
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertNotEqual(contract["result_type"], "draw")
            self.assertTrue(contract["actor_override"])
            expected_override = candidate_id == "hced-Kufah1060-1"
            self.assertEqual(contract["source_outcome_override"], expected_override)
            self.assertEqual(contract["outcome_reversal"], expected_override)

    def test_emitted_events_parse_with_exact_actors_and_no_draws(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 6)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        for candidate_id, (expected_winners, expected_losers) in EXPECTED_WINNERS_AND_LOSERS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
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
            self.assertFalse(
                any("draw" in participant["termination"] for participant in event["participants"])
            )
            self.assertNotIn("seljuks", winners | losers)
            self.assertNotIn("germany", winners | losers)
            contract = WAVE8_SELJUKS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(event["outcome_source_family_ids"], contract["outcome_source_family_ids"])

        entities, _, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_seljuks_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_location_quarantine_is_applied_without_mutating_shared_sets(self) -> None:
        points_before = HCED_POINT_QUARANTINE_IDS
        countries_before = HCED_COUNTRY_QUARANTINE_IDS
        point_values = frozenset(points_before)
        country_values = frozenset(countries_before)
        _, _, events = self._emit()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        expected_points = {"hced-Edessa1144-1", "hced-Edessa1146-1"}
        self.assertEqual(WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            WAVE8_SELJUKS_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": set()},
        )
        self.assertEqual(
            wave8_seljuks_location_quarantine_additions(),
            {"point": expected_points, "country": set()},
        )
        for candidate_id in expected_points:
            self.assertNotIn("geometry", by_candidate[candidate_id])
            self.assertEqual(by_candidate[candidate_id]["modern_location_country"], "Turkey")
        for candidate_id in set(by_candidate) - expected_points:
            self.assertIn("geometry", by_candidate[candidate_id])
            self.assertIn("modern_location_country", by_candidate[candidate_id])
        self.assertIs(HCED_POINT_QUARANTINE_IDS, points_before)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, countries_before)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, point_values)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, country_values)

    def test_iwbd_zero_overlap_audit_fails_closed_on_future_twin(self) -> None:
        self.assertEqual(WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            validate_wave8_seljuks_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )
        future = copy.deepcopy(self.iwbd_rows)
        future.append(
            {
                "candidate_id": "iwbd-future-kose-dag",
                "name": "Kose Dagh",
                "start_date": "1243-06-26",
                "end_date": "1243-06-26",
            }
        )
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_seljuks_integration_dispositions(self.hced_rows, future)


if __name__ == "__main__":
    unittest.main()
