import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_holy_roman_empire_exact as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave6_1500_1799 import WAVE6_HCED_EXCLUSIONS
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_hre_exact_"
EXPECTED_SIGNATURE = "740c954b41184a9a774bb70a69e3d74fc361631ae5731f9ddf39428ffd16155a"

EXPECTED_EXACT_ID_DIGEST = "7ce03b4fbb33bc7ea1525ef6d8b2256cc0d9a5e2834b103d39c02e8cc92708fc"
EXPECTED_EXACT_CANONICAL_MAP_DIGEST = "4aa15e61a3bba1d5bb5cb3770b15b099c1514eb9b724ef81f7d47d30cb9f1b9a"
EXPECTED_EXACT_FULL_MAP_DIGEST = "835318489aaebd917d2a6395878061b5c516fae51b1d3b2ab1c71b36f16a45f1"
EXPECTED_ADJACENT_ID_DIGEST = "e01a64f5f8f47dc7acce3b844ae210c71dca18f664b1727a83ee006941540788"
EXPECTED_ADJACENT_CANONICAL_MAP_DIGEST = "16d2e9596f9cc634f9720f3bc1626403391740339e3ab9990e0b45f5dffe45ff"
EXPECTED_ADJACENT_FULL_MAP_DIGEST = "9a7e54d3be6d07161fc561c4708e4b823205ca36bd87fc52dfd8ce00c05128b0"
EXPECTED_OWNER_MAP_DIGEST = "f8a2cc60cc4b18acae54d3395d8c9aa8219e35b9b5375c6b1f7f5c45b47d7f24"

CANONICAL_FIELDS = (
    "candidate_id",
    "source_record_id",
    "source_row",
    "source_snapshot",
    "name",
    "year_low",
    "year_high",
    "side_1_raw",
    "side_2_raw",
    "winner_raw",
    "loser_raw",
    "participants_raw",
    "war_names",
    "consulted_source_raw",
    "duplicate_source_id",
    "seshat_side_1_candidates",
    "seshat_side_2_candidates",
    "theatre_raw",
    "scale_raw",
    "scale_inferred_raw",
    "latitude",
    "longitude",
    "modern_location_country",
)

EXPECTED_OWNER_EVENTS = {
    "hced-Reutlingen1377-1": (
        "hced_wave8_swabian_hre_hced_reutlingen1377_1",
        "52383f983253ce5ae5a057f330e269b549f814c3039f3b2b1fe5419fe265fa91",
    ),
    "hced-Ulm1376-1": (
        "hced_wave8_swabian_hre_hced_ulm1376_1",
        "f4ea269adbc239ba1f3c39e7435a48f67469a57464e548c8c92f012a55b8180f",
    ),
    "hced-Zatec1421-1": (
        "hced_wave8_hussites_hced_zatec1421_1",
        "54c41abd25b31f17c61942654e809a473d6bccde799a850d2465ffc70a729829",
    ),
}

EXPECTED_SIDES = {
    "hced-Unstrut1075-1": (
        "henry_iv_royal_episcopal_field_army_langensalza_1075",
        "saxon_rebel_field_host_langensalza_1075",
    ),
    "hced-Welfesholze1115-1": (
        "lothair_saxon_rhenish_thuringian_rebel_coalition_welfesholz_1115",
        "hoyer_mansfeld_henry_v_imperial_field_army_welfesholz_1115",
    ),
    "hced-Tortona1155-1": (
        "frederick_barbarossa_pavian_montferrat_malaspina_siege_host_tortona_1155",
        "tortona_communal_garrison_milanese_relief_force_1155",
    ),
    "hced-Milan1158-1": (
        "frederick_barbarossa_pavian_cremonese_lodigian_siege_host_milan_1158",
        "milan_communal_defenders_1158",
    ),
    "hced-Rome1167-1": (
        "christian_mainz_rainald_dassel_tusculan_relief_force_monte_porzio_1167",
        "commune_of_rome_field_army_monte_porzio_1167",
    ),
    "hced-Cortenuova1237-1": (
        "frederick_ii_imperial_sicilian_campaign_army_cortenuova_1237",
        "pietro_tiepolo_lombard_league_field_army_cortenuova_1237",
    ),
    "hced-Parma1247-1248-1": (
        "parma_guelph_communal_sortie_force_vittoria_1247_1248",
        "frederick_ii_imperial_siege_host_parma_1247_1248",
    ),
    "hced-Mirischlau1600-1": (
        "basta_transylvanian_noble_coalition_miraslau_1600",
        "michael_wallachian_szekely_field_army_miraslau_1600",
    ),
    "hced-Breitenfeld1631-1": (
        "gustavus_adolphus_swedish_saxon_coalition_breitenfeld_1631",
        "tilly_imperial_catholic_league_army_breitenfeld_1631",
    ),
    "hced-Neubrandenburg1631-1": (
        "tilly_catholic_league_imperial_assault_force_neubrandenburg_1631",
        "kniphausen_swedish_neubrandenburg_garrison_1631",
    ),
    "hced-Alte Veste1632-1": (
        "wallenstein_imperial_catholic_league_camp_force_alte_veste_1632",
        "gustavus_adolphus_swedish_allied_assault_force_alte_veste_1632",
    ),
    "hced-Boulay1635-1": (
        "turenne_fabert_french_weimarian_rearguard_boulay_1635",
        "gallas_imperial_pursuit_vanguard_boulay_1635",
    ),
    "hced-Breisach1638-1": (
        "bernard_weimarian_french_siege_force_breisach_1638",
        "reinach_imperial_breisach_garrison_1638",
    ),
    "hced-Brema1638-1": (
        "leganes_aragon_spanish_army_of_lombardy_breme_1638",
        "mongallar_crequy_french_breme_garrison_relief_force_1638",
    ),
    "hced-Wittenweier1638-1": (
        "bernard_weimarian_french_field_army_wittenweier_1638",
        "goetz_savelli_imperial_bavarian_relief_army_wittenweier_1638",
    ),
    "hced-Brandeis1639-1": (
        "baner_swedish_field_force_brandeis_1639",
        "hofkirch_imperial_bohemian_field_force_brandeis_1639",
    ),
    "hced-Breitenfeld1642-1": (
        "torstensson_swedish_field_army_breitenfeld_1642",
        "leopold_william_piccolomini_imperial_field_army_breitenfeld_1642",
    ),
    "hced-Harkany1687-1": (
        "lorraine_bavarian_habsburg_allied_army_harsany_1687",
        "sari_suleyman_ottoman_field_army_harsany_1687",
    ),
}

EXPECTED_EVENT_FACTS = {
    "hced-Unstrut1075-1": ("Battle of Langensalza (Unstrut)", 1075, 1075, 0.98, "civil_war", "hced_war_german_civil_wars", 2),
    "hced-Welfesholze1115-1": ("Battle of Welfesholz", 1115, 1115, 0.98, "civil_war", "hced_war_german_civil_wars", 2),
    "hced-Tortona1155-1": ("Siege of Tortona (1155)", 1155, 1155, 0.97, "interstate_limited", "hced_war_frederick_s_1st_expedition_to_italy", 2),
    "hced-Milan1158-1": ("Siege of Milan (1158)", 1158, 1158, 0.96, "interstate_limited", "hced_war_frederick_s_expedition_to_italy", 2),
    "hced-Rome1167-1": ("Battle of Monte Porzio (Tusculum)", 1167, 1167, 0.98, "interstate_limited", "hced_war_wars_of_the_lombard_league", 2),
    "hced-Cortenuova1237-1": ("Battle of Cortenuova", 1237, 1237, 0.98, "interstate_limited", "hced_war_imperial_papal_wars", 2),
    "hced-Parma1247-1248-1": ("Siege of Parma and Vittoria (1247-1248)", 1247, 1248, 0.97, "interstate_limited", "hced_war_imperial_papal_war", 2),
    "hced-Mirischlau1600-1": ("Battle of Mirăslău", 1600, 1600, 0.97, "interstate_limited", "hced_war_balkan_national_wars", 3),
    "hced-Breitenfeld1631-1": ("First Battle of Breitenfeld", 1631, 1631, 0.99, "interstate_limited", "hced_war_swedish_war", 3),
    "hced-Neubrandenburg1631-1": ("Siege of Neubrandenburg", 1631, 1631, 0.98, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Alte Veste1632-1": ("Battle of the Alte Veste", 1632, 1632, 0.94, "interstate_limited", "hced_war_swedish_war", 3),
    "hced-Boulay1635-1": ("Wallerfangen-Boulay rear-guard action", 1635, 1635, 0.88, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Breisach1638-1": ("Siege of Breisach (1638)", 1638, 1638, 0.98, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Brema1638-1": ("Siege of Breme (1638)", 1638, 1638, 0.98, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Wittenweier1638-1": ("Battle of Wittenweier", 1638, 1638, 0.97, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Brandeis1639-1": ("Battle of Brandeis (1639)", 1639, 1639, 0.96, "interstate_limited", "hced_war_thirty_years_war", 2),
    "hced-Breitenfeld1642-1": ("Second Battle of Breitenfeld", 1642, 1642, 0.98, "interstate_limited", "hced_war_thirty_years_war", 3),
    "hced-Harkany1687-1": ("Battle of Harsány (Second Mohács)", 1687, 1687, 0.98, "interstate_limited", "hced_war_later_turkish_habsburg_wars", 3),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value):
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _full_hash(row):
    return _sha(dict(row))


class Wave8HolyRomanEmpireExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.seed_entities = _json(ROOT / "data/seed/entities.json")
        cls.seed_events = _json(ROOT / "data/seed/events.json")
        cls.discovery_rows = {}
        cls.discovery_hashes = {}
        for dataset, lock in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS.items():
            path = ROOT / lock["relative_path"]
            cls.discovery_rows[dataset] = _jsonl(path)
            cls.discovery_hashes[dataset] = hashlib.sha256(path.read_bytes()).hexdigest()

    def _base_artifacts(self):
        entity_ids = {str(item["id"]) for item in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES}
        source_ids = {str(item["id"]) for item in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in entity_ids
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        events = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, sources, events

    def _installed(self):
        entities, sources, events = self._base_artifacts()
        lane.install_wave8_holy_roman_empire_exact_entities(entities)
        lane.install_wave8_holy_roman_empire_exact_sources(sources)
        return entities, sources, events

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_holy_roman_empire_exact_contracts(
            self.hced_rows, entities, existing
        )

    def test_exact_label_inventory_has_23_rows(self):
        rows = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "holy roman empire"
            or normalize_label(row.get("side_2_raw")) == "holy roman empire"
        ]
        self.assertEqual(len(rows), 23)
        self.assertEqual({str(row["candidate_id"]) for row in rows}, lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)

    def test_exact_candidate_id_digest_is_pinned(self):
        self.assertEqual(_sha(sorted(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)), EXPECTED_EXACT_ID_DIGEST)

    def test_exact_canonical_hash_map_is_independently_recomputed(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        actual = {
            candidate_id: canonical_hced_row_sha256(by_id[candidate_id])
            for candidate_id in sorted(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)
        }
        self.assertEqual(_sha(actual), EXPECTED_EXACT_CANONICAL_MAP_DIGEST)
        self.assertEqual(actual, lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES)

    def test_exact_full_hash_map_is_independently_recomputed(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        actual = {
            candidate_id: _full_hash(by_id[candidate_id])
            for candidate_id in sorted(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)
        }
        self.assertEqual(_sha(actual), EXPECTED_EXACT_FULL_MAP_DIGEST)
        self.assertEqual(actual, lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES)

    def test_exact_rows_are_complete_raw_side_one_wins_but_still_manual(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for candidate_id in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS:
            row = by_id[candidate_id]
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["duplicate_source_id"], False)

    def test_exact_partition_is_complete_and_disjoint(self):
        parts = [
            set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS),
            set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
            set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS),
            set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES),
        ]
        self.assertEqual(list(map(len, parts)), [18, 1, 1, 3])
        self.assertEqual(sum(map(len, parts)), len(set().union(*parts)))
        self.assertEqual(set().union(*parts), lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)

    def test_queue_validator_reports_exact_accounting(self):
        self.assertEqual(
            lane.validate_wave8_holy_roman_empire_exact_queue_contracts(self.hced_rows),
            {
                "adjacent_coverage_only_rows": 10,
                "exact_label_rows": 23,
                "existing_owner_duplicates": 3,
                "holds": 1,
                "promotion_contracts": 18,
                "reviewed_hced_rows": 33,
                "terminal_exclusions": 1,
            },
        )

    def test_milan_1161_is_unknown_never_draw(self):
        hold = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS["hced-Milan1161-1"]
        self.assertEqual(hold["disposition"], "hold_unknown_never_draw")
        self.assertEqual(hold["outcome_disposition"], "unknown_never_draw")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertIn("1162", hold["reason_code"])

    def test_rakersberg_1416_is_terminally_excluded(self):
        exclusion = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS["hced-Rakersberg1416-1"]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertIn("1418", exclusion["reason_code"])

    def test_existing_owner_events_and_hashes_are_exact(self):
        by_candidate = {str(event.get("hced_candidate_id")): event for event in self.release_events}
        owner_hashes = {}
        for candidate_id, (event_id, expected_hash) in EXPECTED_OWNER_EVENTS.items():
            event = by_candidate[candidate_id]
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(event["id"], event_id)
                self.assertEqual(_full_hash(event), expected_hash)
                self.assertFalse(event["id"].startswith(EVENT_PREFIX))
                owner_hashes[candidate_id] = _full_hash(event)
        self.assertEqual(_sha(owner_hashes), EXPECTED_OWNER_MAP_DIGEST)

    def test_adjacent_inventory_has_10_rows_and_pinned_id_digest(self):
        ids = set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS)
        self.assertEqual(len(ids), 10)
        self.assertEqual(_sha(sorted(ids)), EXPECTED_ADJACENT_ID_DIGEST)
        self.assertFalse(ids & lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS)

    def test_adjacent_canonical_hash_map_is_independently_recomputed(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        actual = {
            candidate_id: canonical_hced_row_sha256(by_id[candidate_id])
            for candidate_id in sorted(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS)
        }
        self.assertEqual(_sha(actual), EXPECTED_ADJACENT_CANONICAL_MAP_DIGEST)

    def test_adjacent_full_hash_map_is_independently_recomputed(self):
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        actual = {
            candidate_id: _full_hash(by_id[candidate_id])
            for candidate_id in sorted(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS)
        }
        self.assertEqual(_sha(actual), EXPECTED_ADJACENT_FULL_MAP_DIGEST)

    def test_adjacent_rows_are_all_coverage_only(self):
        self.assertTrue(
            all(
                item["disposition"] == "coverage_only_separate_exact_actor_lane"
                for item in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS.values()
            )
        )

    def test_cross_dataset_file_counts_and_byte_hashes_are_pinned(self):
        for dataset, lock in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS.items():
            with self.subTest(dataset=dataset):
                self.assertEqual(len(self.discovery_rows[dataset]), lock["rows"])
                self.assertEqual(self.discovery_hashes[dataset], lock["sha256"])

    def test_wikidata_battle_inventory_digests_are_pinned(self):
        inventory = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES["wikidata_battle"]
        self.assertEqual(len(inventory), 29)
        self.assertEqual(_sha(sorted(inventory)), "aebd19d9c29b73fe2f70565a5570771f53d128d9e16e89ad7b80a4418541f71c")
        self.assertEqual(_sha(inventory), "c42227c8a7d05920ac3aa78015d460521ccb7d5678ae510fae55fedfd004f20f")

    def test_wikidata_generic_inventory_digests_are_pinned(self):
        inventory = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES["wikidata_generic"]
        self.assertEqual(len(inventory), 3)
        self.assertEqual(_sha(sorted(inventory)), "0358bb15e47826c6c39a396cc0297acc7712c96c07eecd90b61f9fbb7fedbdcc")
        self.assertEqual(_sha(inventory), "5773dc135b8a01ebefd856a7ec16f77c10779303d36100975bddb2877fe54e2c")

    def test_brecke_inventory_digests_are_pinned(self):
        inventory = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES["brecke"]
        self.assertEqual(len(inventory), 15)
        self.assertEqual(_sha(sorted(inventory)), "983ba64a07bcfe02bbf324f64b6edc58548e9e115f72676a9413da094af932e5")
        self.assertEqual(_sha(inventory), "9d63120f094617810438893b8bff94a58c7e5e9b1cf037401d78f239e744d564")

    def test_cross_dataset_validator_reports_no_promotions(self):
        self.assertEqual(
            lane.validate_wave8_holy_roman_empire_exact_cross_dataset_inventories(
                self.discovery_rows, self.discovery_hashes, self.release_events
            ),
            {
                "broad_war_coverage_only_rows": 15,
                "cross_dataset_inventory_rows": 47,
                "discovery_promotions": 0,
                "empty_dataset_inventories": 7,
                "unknown_never_draw_rows": 32,
            },
        )

    def test_cross_dataset_guard_scans_the_actual_release_event_view(self):
        leaked = [
            *self.release_events,
            {
                "id": "foreign_lane_discovery_leak",
                "source_ids": ["Q10671413"],
            },
        ]
        with self.assertRaisesRegex(ValueError, "discovery-only row entered"):
            lane.validate_wave8_holy_roman_empire_exact_cross_dataset_inventories(
                self.discovery_rows,
                self.discovery_hashes,
                leaked,
            )

    def test_all_wikidata_inventory_rows_are_winnerless_unknowns(self):
        for dataset in ("wikidata_battle", "wikidata_generic"):
            inventory = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES[dataset]
            by_id = {str(row["candidate_id"]): row for row in self.discovery_rows[dataset]}
            for candidate_id in inventory:
                row = by_id[candidate_id]
                with self.subTest(dataset=dataset, candidate_id=candidate_id):
                    self.assertEqual(row["winners"], [])
                    self.assertIs(row["do_not_rate_automatically"], True)

    def test_all_brecke_inventory_rows_are_outcomeless_coverage(self):
        by_id = {str(row["brecke_id"]): row for row in self.discovery_rows["brecke"]}
        for candidate_id in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES["brecke"]:
            row = by_id[candidate_id]
            self.assertIs(row["outcome_available"], False)
            self.assertEqual(row["rating_use"], "coverage_cross_check_only")

    def test_seven_cross_datasets_have_empty_event_inventories(self):
        empty = {
            key
            for key, inventory in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.items()
            if not inventory
        }
        self.assertEqual(
            empty,
            {
                "iwd", "iwbd", "ucdp_actor", "ucdp_conflict", "ucdp_dyadic",
                "ucdp_termination_conflict", "ucdp_termination_dyad",
            },
        )

    def test_new_and_reused_source_counts_are_exact(self):
        new_ids = {str(source["id"]) for source in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES}
        reused_ids = {str(source["id"]) for source in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES}
        self.assertEqual(len(new_ids), 26)
        self.assertEqual(reused_ids, {"wave8_great_northern_exact_landers_field_forge"})
        self.assertFalse(new_ids & reused_ids)

    def test_every_source_fixture_is_model_valid_and_outcome_capable(self):
        for raw in (
            *lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES,
            *lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES,
        ):
            with self.subTest(source_id=raw["id"]):
                parsed = Source.from_dict(raw)
                self.assertEqual(parsed.to_dict(), raw)
                self.assertIn("outcome", raw["evidence_roles"])

    def test_every_event_has_two_independent_outcome_families(self):
        forbidden = {"hced", "wikidata", "wikidata_battles", "brecke"}
        for candidate_id, contract in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
            families = contract["outcome_source_family_ids"]
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(families), 2)
                self.assertEqual(families, sorted(set(families)))
                self.assertFalse(set(families) & forbidden)

    def test_source_register_is_exactly_consumed(self):
        used = {
            source_id
            for contract in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.values()
            for source_id in contract["outcome_source_ids"]
        }
        declared = {
            str(source["id"])
            for source in (
                *lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES,
                *lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES,
            )
        }
        self.assertEqual(used, declared)

    def test_exactly_36_unique_event_formations_are_declared(self):
        ids = [str(entity["id"]) for entity in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES]
        self.assertEqual(len(ids), 36)
        self.assertEqual(len(set(ids)), 36)
        self.assertEqual(set(ids), {entity for pair in EXPECTED_SIDES.values() for entity in pair})

    def test_formations_are_model_valid_alias_free_and_without_continuity(self):
        for raw in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES:
            with self.subTest(entity_id=raw["id"]):
                self.assertEqual(Entity.from_dict(raw).to_dict(), raw)
                self.assertEqual(raw["aliases"], [])
                self.assertEqual(raw["predecessors"], [])
                self.assertNotIn("successors", raw)
                self.assertNotEqual(normalize_label(raw["id"]), "holy roman empire")
                self.assertNotEqual(normalize_label(raw["name"]), "holy roman empire")

    def test_formation_windows_exactly_match_candidate_windows(self):
        by_entity = {str(entity["id"]): entity for entity in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES}
        for candidate_id, contract in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
            low = contract["canonical_event"]["year_low"]
            high = contract["canonical_event"]["year_high"]
            for entity_id in (*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]):
                self.assertEqual((by_entity[entity_id]["start_year"], by_entity[entity_id]["end_year"]), (low, high))

    def test_each_formation_is_consumed_by_exactly_one_event(self):
        uses = {}
        for candidate_id, contract in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
            for entity_id in (*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]):
                uses.setdefault(entity_id, []).append(candidate_id)
        self.assertEqual(len(uses), 36)
        self.assertTrue(all(len(candidate_ids) == 1 for candidate_ids in uses.values()))

    def test_contract_sides_match_the_audited_formations(self):
        for candidate_id, expected in EXPECTED_SIDES.items():
            contract = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS[candidate_id]
            self.assertEqual((contract["side_1_entity_ids"][0], contract["side_2_entity_ids"][0]), expected)

    def test_entity_install_is_idempotent(self):
        entities, _, _ = self._base_artifacts()
        lane.install_wave8_holy_roman_empire_exact_entities(entities)
        once = copy.deepcopy(entities)
        lane.install_wave8_holy_roman_empire_exact_entities(entities)
        self.assertEqual(entities, once)

    def test_source_install_is_idempotent_and_reuses_landers(self):
        _, sources, _ = self._base_artifacts()
        before_landers = copy.deepcopy(sources["wave8_great_northern_exact_landers_field_forge"])
        lane.install_wave8_holy_roman_empire_exact_sources(sources)
        once = copy.deepcopy(sources)
        lane.install_wave8_holy_roman_empire_exact_sources(sources)
        self.assertEqual(sources, once)
        self.assertEqual(sources["wave8_great_northern_exact_landers_field_forge"], before_landers)

    def test_source_install_fails_if_reused_landers_source_is_missing(self):
        _, sources, _ = self._base_artifacts()
        sources.pop("wave8_great_northern_exact_landers_field_forge")
        with self.assertRaises(ValueError):
            lane.install_wave8_holy_roman_empire_exact_sources(sources)

    def test_source_install_fails_closed_on_collision(self):
        _, sources, _ = self._base_artifacts()
        fixture = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES[0]
        sources[fixture["id"]] = {**fixture, "title": "collision"}
        with self.assertRaises(ValueError):
            lane.install_wave8_holy_roman_empire_exact_sources(sources)

    def test_entity_install_fails_closed_on_collision(self):
        entities, _, _ = self._base_artifacts()
        fixture = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES[0]
        entities[fixture["id"]] = {**fixture, "name": "collision"}
        with self.assertRaises(ValueError):
            lane.install_wave8_holy_roman_empire_exact_entities(entities)

    def test_promoter_emits_exactly_18_candidate_keyed_events(self):
        events = self._events()
        self.assertEqual(len(events), 18)
        self.assertEqual({str(event["hced_candidate_id"]) for event in events}, lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS)
        self.assertEqual(len({str(event["id"]) for event in events}), 18)
        self.assertTrue(all(str(event["id"]).startswith(EVENT_PREFIX) for event in events))

    def test_event_order_is_deterministic_by_year_then_candidate(self):
        events = self._events()
        actual = [(int(event["year"]), str(event["hced_candidate_id"])) for event in events]
        self.assertEqual(actual, sorted(actual))
        self.assertEqual(events, self._events())

    def test_canonical_names_windows_confidences_clusters_and_war_types_are_exact(self):
        by_candidate = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, (name, low, high, confidence, war_type, cluster, scale_level) in EXPECTED_EVENT_FACTS.items():
            event = by_candidate[candidate_id]
            contract = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS[candidate_id]
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual((event["name"], event["year"], event["end_year"]), (name, low, high))
                self.assertEqual(event["confidence"], confidence)
                self.assertEqual(event["war_type"], war_type)
                self.assertEqual(event["cluster_id"], cluster)
                self.assertEqual(contract["expected_scale_level"], scale_level)

    def test_all_promotions_are_source_side_one_wins_without_overrides(self):
        for candidate_id, contract in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(contract["result_type"], "win")
                self.assertEqual(contract["winner_side"], 1)
                self.assertIs(contract["source_outcome_override"], False)
                self.assertIs(contract["source_date_override"], False)
                self.assertIs(contract["outcome_reversal"], False)

    def test_emitted_participants_are_tactical_only_and_never_draws(self):
        for event in self._events():
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(len(event["participants"]), 2)
            by_side = {participant["side"]: participant for participant in event["participants"]}
            self.assertEqual(by_side["side_a"]["termination"], "engagement_victory")
            self.assertEqual(by_side["side_b"]["termination"], "engagement_defeat")
            self.assertEqual(by_side["side_a"]["result_class"], "limited_victory")
            self.assertEqual(by_side["side_b"]["result_class"], "limited_defeat")
            self.assertFalse(any("inconclusive" in p["termination"] for p in event["participants"]))
            self.assertEqual(set(by_side["side_a"]["outcome"]), {"battlefield_control", "mission_objective", "force_preservation", "positional_gain"})

    def test_emitted_source_ids_and_families_match_contracts(self):
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            contract = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(event["outcome_source_family_ids"], contract["outcome_source_family_ids"])
            self.assertEqual(event["source_ids"], ["hced_dataset", *contract["evidence_refs"]])

    def test_all_18_points_are_quarantined(self):
        self.assertEqual(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS, lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS)
        self.assertTrue(all("geometry" not in event for event in self._events()))

    def test_only_boulay_and_brema_countries_are_quarantined(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        quarantined = {candidate_id for candidate_id, event in events.items() if "modern_location_country" not in event}
        self.assertEqual(quarantined, {"hced-Boulay1635-1", "hced-Brema1638-1"})
        self.assertTrue(all("location_provenance" not in events[candidate_id] for candidate_id in quarantined))

    def test_no_nonrating_exact_row_is_emitted(self):
        emitted = {str(event["hced_candidate_id"]) for event in self._events()}
        forbidden = (
            set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS)
            | set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS)
            | set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES)
        )
        self.assertFalse(emitted & forbidden)

    def test_no_adjacent_or_discovery_row_is_emitted(self):
        events = self._events()
        emitted = {str(event["hced_candidate_id"]) for event in events}
        self.assertFalse(emitted & set(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS))
        discovery_ids = set().union(
            *(set(inventory) for inventory in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.values())
        )
        self.assertFalse(discovery_ids & emitted)

    def test_breisach_and_wittenweier_have_disjoint_granularity(self):
        breisach = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS["hced-Breisach1638-1"]["canonical_event"]
        wittenweier = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS["hced-Wittenweier1638-1"]["canonical_event"]
        self.assertIn("siege", breisach["granularity"])
        self.assertIn("relief_battle", wittenweier["granularity"])
        self.assertNotEqual(breisach["canonical_key"], wittenweier["canonical_key"])

    def test_wikidata_alte_veste_and_breisach_duplicates_never_emit(self):
        inventory = lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES["wikidata_battle"]
        self.assertTrue({"Q2002331", "Q15727825", "Q331565", "Q77095548"} <= set(inventory))
        event_source_ids = {source_id for event in self._events() for source_id in event["source_ids"]}
        self.assertFalse({"Q2002331", "Q15727825", "Q331565", "Q77095548"} & event_source_ids)

    def test_live_funnel_confirms_the_exact_label_is_complete(self):
        self.assertFalse(
            [
                row
                for row in self.funnel["labels"]
                if row.get("label") == "holy roman empire"
            ]
        )

    def test_current_release_artifact_state_is_absent_or_complete(self):
        state = lane.validate_wave8_holy_roman_empire_exact_current_artifact_state(
            self.release_events, self.release_entities, self.release_sources
        )
        self.assertIn(state["artifact_state"], {"absent", "integrated"})
        if state["artifact_state"] == "absent":
            self.assertEqual(state["promoted_events"], 0)
        else:
            self.assertEqual(state["promoted_events"], 18)

    def test_synthetic_integrated_artifacts_validate_exactly(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_holy_roman_empire_exact_contracts(self.hced_rows, entities, existing)
        self.assertEqual(
            lane.validate_wave8_holy_roman_empire_exact_current_artifact_state(
                [*existing, *events], entities.values(), sources.values()
            ),
            {
                "artifact_state": "integrated",
                "installed_entities": 36,
                "installed_new_sources": 26,
                "promoted_events": 18,
                "reused_sources": 1,
            },
        )

    def test_partial_artifact_state_fails_closed(self):
        entities, sources, existing = self._base_artifacts()
        entities[lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES[0]["id"]] = copy.deepcopy(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES[0])
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_current_artifact_state(
                existing, entities.values(), sources.values()
            )

    def test_exact_row_mutation_fails_closed(self):
        rows = copy.deepcopy(self.hced_rows)
        target = next(row for row in rows if row.get("candidate_id") == "hced-Unstrut1075-1")
        target["winner_raw"] = target["side_2_raw"]
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_queue_contracts(rows)

    def test_unknown_hold_mutation_fails_closed(self):
        rows = copy.deepcopy(self.hced_rows)
        target = next(row for row in rows if row.get("candidate_id") == "hced-Milan1161-1")
        target["winner_raw"] = "Draw"
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_queue_contracts(rows)

    def test_adjacent_row_mutation_fails_closed(self):
        rows = copy.deepcopy(self.hced_rows)
        target = next(row for row in rows if row.get("candidate_id") == "hced-Padua1509-1")
        target["name"] = "changed"
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_queue_contracts(rows)

    def test_existing_owner_mutation_fails_closed(self):
        events = copy.deepcopy(self.release_events)
        target = next(event for event in events if event.get("hced_candidate_id") == "hced-Ulm1376-1")
        target["summary"] += " changed"
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_integration_dispositions(self.hced_rows, events)

    def test_nonrating_guard_is_not_scoped_to_the_lane_event_prefix(self):
        events = [
            *self.release_events,
            {
                "id": "hced_foreign_lane_milan_1161",
                "hced_candidate_id": "hced-Milan1161-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "nonrating disposition emitted"):
            lane.validate_wave8_holy_roman_empire_exact_integration_dispositions(
                self.hced_rows,
                events,
            )

    def test_discovery_snapshot_hash_mutation_fails_closed(self):
        hashes = dict(self.discovery_hashes)
        hashes["wikidata_battle"] = "0" * 64
        with self.assertRaises(ValueError):
            lane.validate_wave8_holy_roman_empire_exact_cross_dataset_inventories(
                self.discovery_rows, hashes, self.release_events
            )

    def test_promoter_fails_when_a_formation_is_missing(self):
        entities, _, existing = self._installed()
        entities.pop(EXPECTED_SIDES["hced-Unstrut1075-1"][0])
        with self.assertRaises(ValueError):
            lane.promote_wave8_holy_roman_empire_exact_contracts(self.hced_rows, entities, existing)

    def test_promoter_fails_on_existing_candidate_collision(self):
        entities, _, existing = self._installed()
        existing.append({
            "id": "collision",
            "name": "unrelated",
            "year": 1075,
            "hced_candidate_id": "hced-Unstrut1075-1",
        })
        with self.assertRaises(ValueError):
            lane.promote_wave8_holy_roman_empire_exact_contracts(self.hced_rows, entities, existing)

    def test_signature_is_independently_recomputed_and_literal(self):
        payload = {
            "adjacent_hced_dispositions": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS,
            "contracts": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS,
            "discovery_inventories": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES,
            "discovery_snapshot_locks": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS,
            "entities": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES,
            "existing_owner_duplicates": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES,
            "full_row_hashes": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES,
            "holds": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS,
            "location_reasons": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_REASONS,
            "reused_sources": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES,
            "row_hashes": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES,
            "sources": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES,
            "terminal_exclusions": lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS,
            "wave6_superseded_exclusion_ids": sorted(
                lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
            ),
        }
        actual = _sha(payload)
        self.assertEqual(actual, EXPECTED_SIGNATURE)
        self.assertEqual(lane.wave8_holy_roman_empire_exact_audit_signature(), EXPECTED_SIGNATURE)
        self.assertEqual(lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FINAL_AUDIT_SIGNATURE, EXPECTED_SIGNATURE)

    def test_counts_and_cohorts_are_exact(self):
        self.assertEqual(
            lane.wave8_holy_roman_empire_exact_counts(),
            {
                "adjacent_coverage_only_rows": 10,
                "country_quarantine_additions": 2,
                "cross_dataset_inventory_rows": 47,
                "existing_owner_duplicates": 3,
                "holds": 1,
                "new_entities": 36,
                "new_sources": 26,
                "newly_rated_events": 18,
                "outcome_overrides": 0,
                "point_quarantine_additions": 18,
                "reviewed_exact_hced_rows": 23,
                "reviewed_hced_rows": 33,
                "reused_sources": 1,
                "terminal_exclusions": 1,
                "unknown_holds": 1,
                "wave6_superseded_exclusions": 11,
            },
        )
        self.assertEqual(
            lane.wave8_holy_roman_empire_exact_cohort_counts(),
            {
                "barbarossa_italian_expeditions": 3,
                "frederick_ii_lombard_conflicts": 2,
                "german_civil_wars": 2,
                "great_turkish_war": 1,
                "miraslau_1600": 1,
                "thirty_years_war": 9,
            },
        )

    def test_wave6_generic_hre_exclusions_are_explicitly_superseded(self):
        historical = {
            candidate_id
            for candidate_id, contract in WAVE6_HCED_EXCLUSIONS.items()
            if contract["category"] == "unsafe_imperial_collapse"
        }
        self.assertEqual(
            historical,
            lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS,
        )
        self.assertLessEqual(
            historical,
            lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS,
        )

    def test_release_metadata_has_one_current_disposition_per_wave6_hre_row(self):
        promotion = self.release_metadata["promotion"]
        active = {
            row["candidate_id"]
            for row in promotion["wave6_1500_1799_hced_exclusions"]
        }
        superseded = {
            row["candidate_id"]
            for row in promotion[
                "wave6_1500_1799_hced_exclusion_supersessions"
            ]
        }
        self.assertFalse(active & superseded)
        self.assertEqual(
            superseded,
            lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS,
        )
    def test_metadata_contains_all_nonrating_dispositions(self):
        metadata = lane.wave8_holy_roman_empire_exact_metadata()
        self.assertEqual(metadata["final_audit_signature"], EXPECTED_SIGNATURE)
        self.assertEqual(metadata["hold_candidate_ids"], ["hced-Milan1161-1"])
        self.assertEqual(metadata["terminal_exclusion_candidate_ids"], ["hced-Rakersberg1416-1"])
        self.assertEqual(len(metadata["existing_owner_duplicates"]), 3)
        self.assertEqual(
            metadata["wave6_superseded_exclusion_candidate_ids"],
            sorted(
                lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
            ),
        )

    def test_emitted_events_are_model_valid(self):
        for raw in self._events():
            with self.subTest(event_id=raw["id"]):
                parsed = Event.from_dict(raw)
                self.assertEqual(parsed.id, raw["id"])
                self.assertEqual(parsed.name, raw["name"])
                self.assertEqual(parsed.year, raw["year"])
                self.assertEqual(
                    {participant.entity_id for participant in parsed.participants},
                    {participant["entity_id"] for participant in raw["participants"]},
                )

    def test_seed_artifacts_contain_no_lane_material(self):
        entity_ids = {str(entity["id"]) for entity in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES}
        source_ids = {str(source["id"]) for source in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES}
        self.assertFalse(entity_ids & {str(entity["id"]) for entity in self.seed_entities})
        self.assertFalse(any(str(event.get("id", "")).startswith(EVENT_PREFIX) for event in self.seed_events))
        self.assertFalse(source_ids & {source_id for event in self.seed_events for source_id in event.get("source_ids", [])})

    def test_lane_opens_no_generic_hre_identity_alias_or_policy(self):
        self.assertFalse(any("policy" in name.casefold() for name in lane.__dict__ if name.startswith("WAVE8_HOLY_ROMAN_EMPIRE")))
        for entity in lane.WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES:
            self.assertEqual(entity["aliases"], [])
            self.assertNotEqual(normalize_label(entity["id"]), "holy roman empire")
            self.assertNotEqual(normalize_label(entity["name"]), "holy roman empire")


if __name__ == "__main__":
    unittest.main()
