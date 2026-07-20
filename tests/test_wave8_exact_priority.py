import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_exact_priority as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_exact_priority_"

HAMET_DERNA = "hamet_karamanli_claimant_contingent_derna_1805"
EATON_AUXILIARIES = "eaton_hamet_arab_greek_auxiliaries_derna_1805"
WALKER_LA_VIRGEN = "walker_expeditionary_force_la_virgen_1855"
NICARAGUAN_DEMOCRATS = "nicaraguan_democratic_force_la_virgen_1855"
NICARAGUAN_LEGITIMISTS = "nicaraguan_legitimist_force_la_virgen_1855"
COSTA_RICAN_ARMY = "costa_rican_national_army_santa_rosa_1856"
SCHLESSINGER_DETACHMENT = (
    "schlessinger_walker_filibuster_detachment_santa_rosa_1856"
)
ARMINIUS_COALITION = "arminius_led_germanic_coalition_teutoburg_9"
TWIN_VILLAGES_COALITION = (
    "taovaya_fort_defending_coalition_twin_villages_1759"
)
ORTIZ_PARRILLA_EXPEDITION = "ortiz_parrilla_spanish_led_expedition_1759"
HAYFIELD_CHEYENNE_SIOUX_FORCE = "hayfield_cheyenne_sioux_attack_force_1867"

EXPECTED_HASHES = {
    "hced-El Herri1914-1": (
        "fe91f6b7992a075ec9e324793d6add09598278368e71a88e0f5b7b64740e4c0b"
    ),
    "hced-ElKsiba1913-1": (
        "1a4671d25d58cbf580cb903855b88338a450a63902b8dcfc5184d6ce68908011"
    ),
    "hced-Hayfield Fight1867-1": (
        "e175dec6e2da69ca1019b170f94ea90001433ec458b61318ac3fe29ce2076dcd"
    ),
    "hced-In Rhar1900-1": (
        "0cb5a31feaac95140b220734afb3f9ace4e0b314863acfd50da68ff1c58eb4c1"
    ),
    "hced-In Salah1900-1": (
        "7639a1aa0dfb82617e1422a9c0e4efcdfe5ef8d6690c171850f551cfb1b907ca"
    ),
    "hced-Ingosten1899-1": (
        "06f8d695e15ac230959f30be7ee6405f3873d8cc6e90c90c76e59d31947b218c"
    ),
    "hced-Khenifra1914-1": (
        "faff20c86502374e75e854c6153b604a02fbf7786e67c93c1233d59eeb1776d5"
    ),
    "hced-Powder1876-1": (
        "c89dd0c7bd9ffe3bff435dc12241995b30f419464627baa7881ba4a27b0dfb10"
    ),
    "hced-Wagon Box Fight1867-1": (
        "8d12e4b1e296e5c2c322d8ed267defcf750718bf99ada52a52ccdc1b69c56dd7"
    ),
    "hced-Amida359-1": (
        "c46a44ab431eca94064d51982cee7947e439524e21bdf4dff6c152898ec01637"
    ),
    "hced-Amida502-503-1": (
        "5e435d325346a25e84234b8f4dea84eac517872c3389198d684a638ee2cb6f9f"
    ),
    "hced-Akroinos739-1": (
        "d342fa6e1910e941bfcdcfd3639b3ac3328ff6d10765179c74e905f6ca187026"
    ),
    "hced-Calpulalpam1860-1": (
        "f7e420f15234141959bd92b6cd103a4b82d15b0b4b33a4394fa01002c583a32d"
    ),
    "hced-Carthage, Tunisia697-1": (
        "889402c7a7a787e8593769d88f080460abb42722f8d316cdc084bbc2334609a6"
    ),
    "hced-Ctesiphon363-1": (
        "dde39031af8f8654460615651a15a870fdda00badd7f6c8b8457dbbc3f5c9969"
    ),
    "hced-Derna1805-1": (
        "821591e6a4733f91c25f30a2aba17cb199537c3941cf2b55840125a1ff716f87"
    ),
    "hced-Granada, Nicaragua1856-1": (
        "e00e51d575246bdd94bf6c25cb010d389c5fb90536c73168313973f2f49f7d74"
    ),
    "hced-La Virgen1855-1": (
        "22a82e98c7f20f21e1135ba5801acdc65c66765477614a18b800c27682367314"
    ),
    "hced-Red River1759-1": (
        "80dd300e8e760766faed4944f672fb597944822d850551f00506f0979876a083"
    ),
    "hced-Santa Rosa de Copan1856-1": (
        "0ca5fb235b393560bd5fef08cc2c13f4b39c3659c88209fc6f74a1b38f1fbc49"
    ),
    "hced-Teutoburgwald9-1": (
        "5eb0ca0863620e7f8cf42e3f64f2cd98744313e61d2d3bd18933096521389330"
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


class Wave8ExactPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_EXACT_PRIORITY_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_EXACT_PRIORITY_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_exact_priority_entities(entities)
        lane.install_wave8_exact_priority_sources(sources)
        return entities, sources, existing

    def _projection(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_exact_priority_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, existing, events

    def test_all_reserved_rows_and_sha256_contracts_are_exact(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("candidate_id") in lane.WAVE8_EXACT_PRIORITY_TARGET_IDS
        }
        self.assertEqual(lane.WAVE8_EXACT_PRIORITY_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(
            lane.validate_wave8_exact_priority_queue_contracts(self.hced_rows),
            {
                "audited_candidate_rows": 21,
                "automated_discovery_rows": 21,
                "holds": 3,
                "promotion_contracts": 18,
                "reserved_hced_rows": 21,
                "reviewed_hced_rows": 21,
            },
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(
                    row["winner_loser_complete"],
                    candidate_id != "hced-Powder1876-1",
                )

    def test_reservation_partition_holds_granada_without_inventing_a_draw(self) -> None:
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS,
            {
                "hced-El Herri1914-1",
                "hced-ElKsiba1913-1",
                "hced-Hayfield Fight1867-1",
                "hced-In Rhar1900-1",
                "hced-In Salah1900-1",
                "hced-Ingosten1899-1",
                "hced-Khenifra1914-1",
                "hced-Amida359-1",
                "hced-Amida502-503-1",
                "hced-Akroinos739-1",
                "hced-Calpulalpam1860-1",
                "hced-Carthage, Tunisia697-1",
                "hced-Ctesiphon363-1",
                "hced-Derna1805-1",
                "hced-La Virgen1855-1",
                "hced-Red River1759-1",
                "hced-Santa Rosa de Copan1856-1",
                "hced-Teutoburgwald9-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_HOLD_IDS,
            {
                "hced-Granada, Nicaragua1856-1",
                "hced-Powder1876-1",
                "hced-Wagon Box Fight1867-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS,
            lane.WAVE8_EXACT_PRIORITY_TARGET_IDS,
        )
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_RESERVED_IDS,
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS
            | lane.WAVE8_EXACT_PRIORITY_HOLD_IDS,
        )
        hold = lane.WAVE8_EXACT_PRIORITY_HOLDS[
            "hced-Granada, Nicaragua1856-1"
        ]
        self.assertEqual(hold["disposition"], "hold")
        self.assertNotIn("result_type", hold)
        self.assertNotIn("winner_side", hold)
        self.assertIn("not converted to a draw", hold["audit_note"])
        powder = lane.WAVE8_EXACT_PRIORITY_HOLDS["hced-Powder1876-1"]
        self.assertIn("Unknown is not a draw", powder["audit_note"])
        self.assertNotIn("result_type", powder)
        wagon = lane.WAVE8_EXACT_PRIORITY_HOLDS[
            "hced-Wagon Box Fight1867-1"
        ]
        self.assertIn("one-for-one", wagon["audit_note"])
        self.assertFalse(
            any(
                "central_american" in str(entity["id"])
                for entity in lane.WAVE8_EXACT_PRIORITY_ENTITIES
            )
        )
        for candidate_id, contract in lane.WAVE8_EXACT_PRIORITY_CONTRACTS.items():
            self.assertEqual(contract["result_type"], "win")
            reversed_outcome = candidate_id == "hced-Ctesiphon363-1"
            self.assertEqual(contract["winner_side"], 2 if reversed_outcome else 1)
            self.assertIs(contract["source_outcome_override"], reversed_outcome)
            self.assertIs(contract["outcome_reversal"], reversed_outcome)

    def test_new_identities_are_alias_free_and_event_bounded(self) -> None:
        entities = {
            str(item["id"]): item for item in lane.WAVE8_EXACT_PRIORITY_ENTITIES
        }
        expected_windows = {
            HAMET_DERNA: (1805, 1805),
            EATON_AUXILIARIES: (1805, 1805),
            WALKER_LA_VIRGEN: (1855, 1855),
            NICARAGUAN_DEMOCRATS: (1855, 1855),
            NICARAGUAN_LEGITIMISTS: (1855, 1855),
            COSTA_RICAN_ARMY: (1856, 1856),
            SCHLESSINGER_DETACHMENT: (1856, 1856),
            ARMINIUS_COALITION: (9, 9),
            TWIN_VILLAGES_COALITION: (1759, 1759),
            ORTIZ_PARRILLA_EXPEDITION: (1759, 1759),
            HAYFIELD_CHEYENNE_SIOUX_FORCE: (1867, 1867),
            "in_salah_ksourian_force_igosten_1899": (1899, 1899),
            "deghamcha_sali_resistance_force_1900": (1900, 1900),
            "pasha_timmi_in_rhar_force_1900": (1900, 1900),
            "moha_ou_said_el_ksiba_force_1913": (1913, 1913),
            "moha_ou_hammou_khenifra_force_1914": (1914, 1914),
            "moha_ou_hammou_el_herri_force_1914": (1914, 1914),
        }
        self.assertEqual(set(entities), set(expected_windows))
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    expected_windows[entity_id],
                )
                self.assertEqual(entity["aliases"], [])
                self.assertEqual(entity["predecessors"], [])
                self.assertIn("No rating is inherited", entity["continuity_note"])
                Entity.from_dict(entity)

    def test_sources_parse_and_pin_role_and_family_provenance(self) -> None:
        self.assertEqual(len(lane.WAVE8_EXACT_PRIORITY_SOURCES), 44)
        sources = {
            str(source["id"]): source
            for source in lane.WAVE8_EXACT_PRIORITY_SOURCES
        }
        known_sources = {
            str(source["id"]): source for source in self.release_sources
        }
        known_sources.update(sources)
        for source_id, source in sources.items():
            with self.subTest(source_id=source_id):
                Source.from_dict(source)
                self.assertTrue(source["source_family_id"])
                self.assertEqual(
                    source["evidence_roles"],
                    sorted(set(source["evidence_roles"])),
                )
        for candidate_id, contract in lane.WAVE8_EXACT_PRIORITY_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]), 2
                )
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(
                        {
                            known_sources[source_id]["source_family_id"]
                            for source_id in contract["outcome_source_ids"]
                        }
                    ),
                )
                self.assertTrue(
                    all(
                        "outcome" in known_sources[source_id]["evidence_roles"]
                        for source_id in contract["outcome_source_ids"]
                    )
                )
        for hold in lane.WAVE8_EXACT_PRIORITY_HOLDS.values():
            self.assertGreaterEqual(len(hold["evidence_source_family_ids"]), 2)
        self.assertEqual(
            sources["wave8_exact_priority_army_sioux_wars_atlas"]["title"],
            "Atlas of the Sioux Wars, Second Edition",
        )
        self.assertEqual(
            {
                source_id: (sources[source_id]["title"], sources[source_id]["source_type"])
                for source_id in (
                    "wave8_exact_priority_constantine_tidikelt",
                    "wave8_exact_priority_persee_in_rhar",
                )
            },
            {
                "wave8_exact_priority_constantine_tidikelt": (
                    "Nécrologie",
                    "digitized_historical_obituary",
                ),
                "wave8_exact_priority_persee_in_rhar": (
                    "L'occupation du Touât",
                    "contemporary_scholarly_report",
                ),
            },
        )

    def test_promotions_emit_exact_candidate_keyed_coalitions_and_wins(self) -> None:
        _, _, _, emitted = self._projection()
        events = {str(event["hced_candidate_id"]): event for event in emitted}
        expected = {
            "hced-El Herri1914-1": (
                "Battle of El Herri",
                {"moha_ou_hammou_el_herri_force_1914"},
                {"french_third_republic"},
            ),
            "hced-ElKsiba1913-1": (
                "Battle of El Ksiba",
                {"moha_ou_said_el_ksiba_force_1913"},
                {"french_third_republic"},
            ),
            "hced-Hayfield Fight1867-1": (
                "Hayfield Fight",
                {"united_states"},
                {HAYFIELD_CHEYENNE_SIOUX_FORCE},
            ),
            "hced-In Rhar1900-1": (
                "Capture of In Rhar",
                {"french_third_republic"},
                {"pasha_timmi_in_rhar_force_1900"},
            ),
            "hced-In Salah1900-1": (
                "Combat of Deghamcha and Sali",
                {"french_third_republic"},
                {"deghamcha_sali_resistance_force_1900"},
            ),
            "hced-Ingosten1899-1": (
                "Combat of Igosten",
                {"french_third_republic"},
                {"in_salah_ksourian_force_igosten_1899"},
            ),
            "hced-Khenifra1914-1": (
                "Capture of Khenifra",
                {"french_third_republic"},
                {"moha_ou_hammou_khenifra_force_1914"},
            ),
            "hced-Amida359-1": (
                "Siege and capture of Amida (359)",
                {"sasanian_empire"},
                {"roman_empire"},
            ),
            "hced-Amida502-503-1": (
                "Siege and capture of Amida (502-503)",
                {"sasanian_empire"},
                {"byzantine_empire"},
            ),
            "hced-Akroinos739-1": (
                "Battle of Akroinon",
                {"byzantine_empire"},
                {"umayyad_caliphate"},
            ),
            "hced-Calpulalpam1860-1": (
                "Battle of Calpulalpan",
                {"mexican_liberal_forces"},
                {"mexican_conservative_forces"},
            ),
            "hced-Carthage, Tunisia697-1": (
                "Umayyad capture of Carthage",
                {"umayyad_caliphate"},
                {"byzantine_empire"},
            ),
            "hced-Ctesiphon363-1": (
                "Battle before Ctesiphon",
                {"roman_empire"},
                {"sasanian_empire"},
            ),
            "hced-Derna1805-1": (
                "Battle of Derna",
                {"united_states", HAMET_DERNA, EATON_AUXILIARIES},
                {"yusuf_karamanli_regency_of_tripoli_1795_1832"},
            ),
            "hced-La Virgen1855-1": (
                "Battle of La Virgen",
                {WALKER_LA_VIRGEN, NICARAGUAN_DEMOCRATS},
                {NICARAGUAN_LEGITIMISTS},
            ),
            "hced-Santa Rosa de Copan1856-1": (
                "Battle of Santa Rosa (Costa Rica)",
                {COSTA_RICAN_ARMY},
                {SCHLESSINGER_DETACHMENT},
            ),
            "hced-Teutoburgwald9-1": (
                "Battle of the Teutoburg Forest",
                {ARMINIUS_COALITION},
                {"roman_empire"},
            ),
            "hced-Red River1759-1": (
                "Battle of the Twin Villages",
                {TWIN_VILLAGES_COALITION},
                {ORTIZ_PARRILLA_EXPEDITION},
            ),
        }
        self.assertEqual(set(events), set(expected))
        self.assertFalse(lane.WAVE8_EXACT_PRIORITY_HOLD_IDS & set(events))
        for candidate_id, (name, winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if "victory" in item["termination"]
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if "defeat" in item["termination"]
                    },
                    losers,
                )
                self.assertFalse(
                    any(
                        token in item["termination"]
                        for item in event["participants"]
                        for token in ("draw", "inconclusive", "unknown")
                    )
                )
                Event.from_dict(event)
        self.assertEqual(events["hced-ElKsiba1913-1"]["aliases"], [])
        self.assertNotIn(
            "None",
            {
                alias
                for event in emitted
                for alias in event.get("aliases", [])
            },
        )

    def test_chronology_and_event_types_are_pinned(self) -> None:
        expected = {
            "hced-El Herri1914-1": (
                "13 November 1914",
                "day",
                "colonial_anti_colonial",
                (1914, 1914),
            ),
            "hced-ElKsiba1913-1": (
                "8-10 June 1913",
                "day_range",
                "colonial_anti_colonial",
                (1913, 1913),
            ),
            "hced-Hayfield Fight1867-1": (
                "1 August 1867",
                "day",
                "colonial_anti_colonial",
                (1867, 1867),
            ),
            "hced-In Rhar1900-1": (
                "19 March 1900",
                "day",
                "colonial_anti_colonial",
                (1900, 1900),
            ),
            "hced-In Salah1900-1": (
                "5 January 1900",
                "day",
                "colonial_anti_colonial",
                (1900, 1900),
            ),
            "hced-Ingosten1899-1": (
                "27 or 28 December 1899",
                "day_conflict",
                "colonial_anti_colonial",
                (1899, 1899),
            ),
            "hced-Khenifra1914-1": (
                "12 June 1914",
                "day",
                "colonial_anti_colonial",
                (1914, 1914),
            ),
            "hced-Amida359-1": (
                "359 CE",
                "year",
                "interstate_limited",
                (359, 359),
            ),
            "hced-Amida502-503-1": (
                "late 502-10 January 503",
                "year_range",
                "interstate_limited",
                (502, 503),
            ),
            "hced-Akroinos739-1": (
                "740 CE",
                "year",
                "interstate_limited",
                (740, 740),
            ),
            "hced-Calpulalpam1860-1": (
                "22 December 1860",
                "day",
                "civil_war",
                (1860, 1860),
            ),
            "hced-Carthage, Tunisia697-1": (
                "698 CE",
                "year",
                "imperial_conquest",
                (698, 698),
            ),
            "hced-Ctesiphon363-1": (
                "363 CE",
                "year",
                "interstate_limited",
                (363, 363),
            ),
            "hced-Derna1805-1": (
                "27 April 1805",
                "day",
                "interstate_claimant_intervention",
                (1805, 1805),
            ),
            "hced-La Virgen1855-1": (
                "3 September 1855",
                "day",
                "civil_war_foreign_intervention",
                (1855, 1855),
            ),
            "hced-Santa Rosa de Copan1856-1": (
                "20 March 1856",
                "day",
                "foreign_filibuster_intervention",
                (1856, 1856),
            ),
            "hced-Teutoburgwald9-1": (
                "9 CE",
                "year",
                "anti_imperial_revolt",
                (9, 9),
            ),
            "hced-Red River1759-1": (
                "7 October 1759",
                "day",
                "colonial_anti_colonial",
                (1759, 1759),
            ),
        }
        events = {
            str(event["hced_candidate_id"]): event
            for event in self._projection()[3]
        }
        for candidate_id, (date_text, precision, war_type, years) in expected.items():
            contract = lane.WAVE8_EXACT_PRIORITY_CONTRACTS[candidate_id]
            self.assertEqual(contract["canonical_event"]["date_text"], date_text)
            self.assertEqual(
                contract["canonical_event"]["date_precision"], precision
            )
            self.assertEqual(events[candidate_id]["date_precision"], precision)
            self.assertEqual(events[candidate_id]["war_type"], war_type)
            self.assertEqual(
                (events[candidate_id]["year"], events[candidate_id]["end_year"]),
                years,
            )

        for candidate_id in {
            "hced-Amida502-503-1",
            "hced-Akroinos739-1",
            "hced-Carthage, Tunisia697-1",
        }:
            contract = lane.WAVE8_EXACT_PRIORITY_CONTRACTS[candidate_id]
            self.assertIs(contract["source_date_override"], True)
            self.assertGreaterEqual(len(contract["date_source_ids"]), 2)

        carthage = events["hced-Carthage, Tunisia697-1"]
        self.assertEqual(Event.from_dict(carthage).track, "operational")
        self.assertEqual(carthage["event_type"], "campaign")
        self.assertEqual(carthage["scale"], "campaign")
        self.assertEqual(carthage["stakes"], "major")
        self.assertEqual(carthage["domain"], "mixed")
        self.assertIn("operational campaign assertion", carthage["summary"])
        self.assertEqual(
            {item["termination"] for item in carthage["participants"]},
            {"campaign_victory", "campaign_defeat"},
        )
        for participant in carthage["participants"]:
            self.assertEqual(
                set(participant["outcome"]),
                {
                    "campaign_objective",
                    "force_preservation",
                    "logistics_sustainment",
                    "tempo_initiative",
                    "theater_control",
                },
            )
            self.assertEqual(participant["stakes"], 0.68)
            self.assertEqual(participant["national_scale"], 0.52)
            self.assertIn("operational_campaign_", participant["result_class"])

    def test_all_promoted_points_are_quarantined_and_countries_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_EXACT_PRIORITY_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS)
        expected_countries = {
            "hced-El Herri1914-1": "Morocco",
            "hced-ElKsiba1913-1": "Morocco",
            "hced-Hayfield Fight1867-1": "United States",
            "hced-In Rhar1900-1": "Algeria",
            "hced-In Salah1900-1": "Algeria",
            "hced-Ingosten1899-1": "Algeria",
            "hced-Khenifra1914-1": "Morocco",
            "hced-Amida359-1": "Turkey",
            "hced-Amida502-503-1": "Turkey",
            "hced-Akroinos739-1": "Turkey",
            "hced-Calpulalpam1860-1": "Mexico",
            "hced-Carthage, Tunisia697-1": "Tunisia",
            "hced-Ctesiphon363-1": "Iraq",
            "hced-Derna1805-1": "Libya",
            "hced-La Virgen1855-1": "Nicaragua",
            "hced-Red River1759-1": "United States",
            "hced-Santa Rosa de Copan1856-1": "Costa Rica",
            "hced-Teutoburgwald9-1": "Germany",
        }
        for event in self._projection()[3]:
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"], expected_countries[candidate_id]
            )
            self.assertIn("location_provenance", event)

    def test_projected_release_inventory_and_final_audit_validate(self) -> None:
        entities, sources, existing, emitted = self._projection()
        release = [*existing, *emitted]
        self.assertEqual(
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                release,
            ),
            {
                "held_candidate_events": 0,
                "lane_entities": 17,
                "lane_events": 18,
                "lane_sources": 44,
                "outside_entity_uses": 0,
                "reserved_candidate_ids": 21,
            },
        )
        self.assertEqual(
            lane.validate_wave8_exact_priority_final_audit(
                entities,
                sources,
                release,
                lane.wave8_exact_priority_metadata(),
            ),
            {
                "held_candidate_events": 0,
                "lane_entities": 17,
                "lane_events": 18,
                "lane_sources": 44,
                "outside_entity_uses": 0,
                "reserved_candidate_ids": 21,
                "final_audit_signature": (
                    lane.WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE
                ),
            },
        )

    def test_hash_and_automated_discovery_tampering_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Calpulalpam1860-1"
        )
        row["winner_raw"] = "Mexican Government"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_exact_priority_queue_contracts(tampered)

        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Derna1805-1"
        )
        row["do_not_rate_automatically"] = False
        with self.assertRaises(ValueError):
            lane.promote_wave8_exact_priority_contracts(
                tampered,
                self._installed()[0],
                self._installed()[2],
            )

    def test_release_source_family_and_role_tampering_fail_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        source_id = "wave8_exact_priority_tsha_ortiz_parrilla"
        sources[source_id]["source_family_id"] = "tampered_family"
        with self.assertRaisesRegex(ValueError, "source provenance"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        sources[source_id]["evidence_roles"] = [
            "identity_boundary_or_context_reference"
        ]
        with self.assertRaisesRegex(ValueError, "source provenance"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_outcome_tampering_and_unknown_as_draw_fail_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        event = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
        )
        event["participants"][0]["termination"] = "engagement_inconclusive"
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        for field, value in (
            ("side", "side_b"),
            ("result_class", "stalemate_or_inconclusive"),
            ("evidence_confidence", 0.10),
            (
                "outcome",
                {
                    "battlefield_control": 0.5,
                    "mission_objective": 0.5,
                    "force_preservation": 0.5,
                    "positional_gain": 0.5,
                },
            ),
        ):
            with self.subTest(field=field):
                entities, sources, existing, emitted = self._projection()
                event = next(
                    item
                    for item in emitted
                    if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
                )
                event["participants"][0][field] = value
                with self.assertRaisesRegex(ValueError, "release outcome"):
                    lane.validate_wave8_exact_priority_release_inventory(
                        entities,
                        sources,
                        [*existing, *emitted],
                    )

    def test_identity_window_tampering_fails_promotion_and_release(self) -> None:
        entities, sources, existing = self._installed()
        entities[HAMET_DERNA]["end_year"] = 1804
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_exact_priority_contracts(
                self.hced_rows,
                entities,
                existing,
            )

        entities, sources, existing, emitted = self._projection()
        entities[COSTA_RICAN_ARMY]["start_year"] = 1857
        with self.assertRaisesRegex(ValueError, "release entity drift"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_coalition_decomposition_tampering_fails_release_audit(self) -> None:
        entities, sources, existing, emitted = self._projection()
        derna = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Derna1805-1"
        )
        derna["participants"] = [
            item
            for item in derna["participants"]
            if item["entity_id"] != EATON_AUXILIARIES
        ]
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        la_virgen = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-La Virgen1855-1"
        )
        la_virgen["participants"][0]["entity_id"] = COSTA_RICAN_ARMY
        with self.assertRaisesRegex(ValueError, "release outcome"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

    def test_release_inventory_hold_leak_partial_inventory_and_metadata_fail(self) -> None:
        entities, sources, existing, emitted = self._projection()
        with self.assertRaisesRegex(ValueError, "event inventory"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted[:-1]],
            )

        hold_leak = copy.deepcopy(emitted[0])
        hold_leak["id"] = f"{EVENT_ID_PREFIX}held_granada"
        hold_leak["hced_candidate_id"] = "hced-Granada, Nicaragua1856-1"
        with self.assertRaisesRegex(ValueError, "held candidate"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted, hold_leak],
            )

        entities, sources, existing, emitted = self._projection()
        teutoburg = next(
            item
            for item in emitted
            if item["hced_candidate_id"] == "hced-Teutoburgwald9-1"
        )
        teutoburg["aliases"].append("Germanic Tribes")
        with self.assertRaisesRegex(ValueError, "event alias drift"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted],
            )

        entities, sources, existing, emitted = self._projection()
        metadata = copy.deepcopy(lane.wave8_exact_priority_metadata())
        metadata["final_audit_signature"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "metadata drift"):
            lane.validate_wave8_exact_priority_final_audit(
                entities,
                sources,
                [*existing, *emitted],
                metadata,
            )

    def test_event_bounded_identity_use_outside_lane_fails_closed(self) -> None:
        entities, sources, existing, emitted = self._projection()
        leaked = {
            "id": "uncontracted_hamet_rate",
            "name": "Uncontracted Hamet event",
            "year": 1805,
            "participants": [{"entity_id": HAMET_DERNA}],
        }
        with self.assertRaisesRegex(ValueError, "outside exact contracts"):
            lane.validate_wave8_exact_priority_release_inventory(
                entities,
                sources,
                [*existing, *emitted, leaked],
            )

    def test_duplicate_and_probable_twin_guards_fail_closed(self) -> None:
        _, _, existing, emitted = self._projection()
        self.assertEqual(
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "held_release_events": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
            },
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_exact_priority_contracts(
                self.hced_rows,
                self._installed()[0],
                [*existing, emitted[0]],
            )

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-varus",
                "batname": "Varus Battle",
                "batyear": 9,
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable twin"):
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

        with self.assertRaisesRegex(ValueError, "overlap is partial"):
            lane.validate_wave8_exact_priority_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, emitted[0]],
            )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        lane.install_wave8_exact_priority_entities(entities)
        lane.install_wave8_exact_priority_entities(entities)
        self.assertEqual(len(entities), 17)
        entities[HAMET_DERNA]["end_year"] = 1804
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_exact_priority_entities(entities)

        sources: dict[str, dict] = {}
        lane.install_wave8_exact_priority_sources(sources)
        lane.install_wave8_exact_priority_sources(sources)
        self.assertEqual(len(sources), 44)
        source_id = "wave8_exact_priority_kalkriese_varus"
        sources[source_id]["source_family_id"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_exact_priority_sources(sources)

    def test_installers_are_atomic_on_late_collision(self) -> None:
        late_entity = lane.WAVE8_EXACT_PRIORITY_ENTITIES[-1]
        entities = {
            str(late_entity["id"]): {
                **copy.deepcopy(late_entity),
                "name": "late collision",
            }
        }
        before_entities = copy.deepcopy(entities)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_exact_priority_entities(entities)
        self.assertEqual(entities, before_entities)

        late_source = lane.WAVE8_EXACT_PRIORITY_SOURCES[-1]
        sources = {
            str(late_source["id"]): {
                **copy.deepcopy(late_source),
                "title": "late collision",
            }
        }
        before_sources = copy.deepcopy(sources)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_exact_priority_sources(sources)
        self.assertEqual(sources, before_sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_exact_priority_audit_signature(),
            lane.WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_exact_priority_counts(),
            {
                "country_quarantine_additions": 0,
                "date_overrides": 3,
                "holds": 3,
                "new_entities": 17,
                "new_sources": 44,
                "newly_rated_events": 18,
                "outcome_overrides": 1,
                "outcome_reversals": 1,
                "point_quarantine_additions": 18,
                "promotion_contracts": 18,
                "reserved_hced_rows": 21,
                "reviewed_hced_rows": 21,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_exact_priority_cohort_counts(),
            {
                "byzantine_umayyad_wars": 1,
                "first_barbary_war": 1,
                "french_conquest_tidikelt": 3,
                "great_sioux_war": 1,
                "mexican_war_of_reform": 1,
                "nicaragua_filibuster_conflict": 3,
                "red_cloud_war": 2,
                "roman_germania_conflict": 1,
                "sasanian_roman_wars": 3,
                "spanish_northern_frontier": 1,
                "umayyad_conquest_north_africa": 1,
                "zaian_war": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
