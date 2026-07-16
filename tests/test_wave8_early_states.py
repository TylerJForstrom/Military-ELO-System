import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_early_states import (
    WAVE8_EARLY_STATES_CONTRACT_IDS,
    WAVE8_EARLY_STATES_CONTRACTS,
    WAVE8_EARLY_STATES_ENTITIES,
    WAVE8_EARLY_STATES_FINAL_AUDIT_SIGNATURE,
    WAVE8_EARLY_STATES_HOLD_IDS,
    WAVE8_EARLY_STATES_HOLDS,
    WAVE8_EARLY_STATES_RESERVED_IDS,
    WAVE8_EARLY_STATES_SOURCES,
    install_wave8_early_states_entities,
    install_wave8_early_states_sources,
    promote_wave8_early_states_contracts,
    validate_wave8_early_states_queue_contracts,
    wave8_early_states_audit_signature,
    wave8_early_states_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _independent_signature() -> str:
    lines: list[str] = []
    for disposition, inventory in (
        ("promote", WAVE8_EARLY_STATES_CONTRACTS),
        ("hold", WAVE8_EARLY_STATES_HOLDS),
    ):
        for candidate_id, item in sorted(inventory.items()):
            lines.append(
                "|".join(
                    (
                        disposition,
                        candidate_id,
                        item["raw_row_sha256"],
                        item["canonical_event"]["canonical_key"],
                        ",".join(item.get("side_1_entity_ids", [])),
                        ",".join(item.get("side_2_entity_ids", [])),
                        str(item.get("winner_side", "")),
                        str(bool(item.get("source_outcome_override"))),
                        ",".join(item.get("outcome_source_ids", [])),
                        item.get("hold_category", ""),
                        str(bool(item.get("terminal_exclusion"))),
                        item.get("duplicate_of_candidate_id", ""),
                    )
                )
            )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


class Wave8EarlyStatesTests(unittest.TestCase):
    def _entities_and_existing(self):
        lane_ids = {entity["id"] for entity in WAVE8_EARLY_STATES_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data/release/entities.json")
            if entity["id"] not in lane_ids
        }
        install_wave8_early_states_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data/release/events.json")
            if event.get("hced_candidate_id") not in WAVE8_EARLY_STATES_CONTRACT_IDS
        ]
        return entities, existing

    def test_exact_inventory_counts_cohorts_and_signature(self) -> None:
        self.assertEqual(
            (len(WAVE8_EARLY_STATES_CONTRACT_IDS), len(WAVE8_EARLY_STATES_HOLD_IDS)),
            (21, 10),
        )
        self.assertFalse(
            WAVE8_EARLY_STATES_CONTRACT_IDS & WAVE8_EARLY_STATES_HOLD_IDS
        )
        self.assertEqual(
            WAVE8_EARLY_STATES_RESERVED_IDS,
            WAVE8_EARLY_STATES_CONTRACT_IDS | WAVE8_EARLY_STATES_HOLD_IDS,
        )
        self.assertEqual(
            wave8_early_states_cohort_counts(),
            {
                "gurkha_audit": 5,
                "muslim_ummah_audit": 9,
                "parthia_audit": 7,
            },
        )
        self.assertEqual(
            _independent_signature(), WAVE8_EARLY_STATES_FINAL_AUDIT_SIGNATURE
        )
        self.assertEqual(
            wave8_early_states_audit_signature(),
            WAVE8_EARLY_STATES_FINAL_AUDIT_SIGNATURE,
        )

    def test_all_31_current_queue_hashes_are_pinned(self) -> None:
        rows = {row["candidate_id"]: row for row in _rows()}
        inventory = {
            **WAVE8_EARLY_STATES_CONTRACTS,
            **WAVE8_EARLY_STATES_HOLDS,
        }
        self.assertEqual(len(inventory), 31)
        self.assertEqual(
            validate_wave8_early_states_queue_contracts(list(rows.values())),
            {"promotion_contracts": 21, "holds": 10, "reviewed_hced_rows": 31},
        )
        for candidate_id, disposition in inventory.items():
            self.assertIn(candidate_id, rows)
            self.assertEqual(
                canonical_hced_row_sha256(rows[candidate_id]),
                disposition["raw_row_sha256"],
                candidate_id,
            )

        changed = copy.deepcopy(list(rows.values()))
        target = next(
            row for row in changed if row["candidate_id"] == "hced-Ohud625-1"
        )
        target["winner_raw"] = "Mecca"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_early_states_queue_contracts(changed)

    def test_sources_entities_and_evidence_graph_validate(self) -> None:
        self.assertEqual(
            (len(WAVE8_EARLY_STATES_ENTITIES), len(WAVE8_EARLY_STATES_SOURCES)),
            (19, 27),
        )
        source_ids = {source["id"] for source in WAVE8_EARLY_STATES_SOURCES}
        entity_ids = {entity["id"] for entity in WAVE8_EARLY_STATES_ENTITIES}
        self.assertEqual(len(source_ids), 27)
        self.assertEqual(len(entity_ids), 19)
        for source in WAVE8_EARLY_STATES_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
        for entity in WAVE8_EARLY_STATES_ENTITIES:
            Entity.from_dict(entity)
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        for item in [
            *WAVE8_EARLY_STATES_CONTRACTS.values(),
            *WAVE8_EARLY_STATES_HOLDS.values(),
        ]:
            self.assertTrue(item["evidence_refs"])
            self.assertTrue(set(item["evidence_refs"]) <= source_ids)

        installed_entities: dict[str, dict] = {}
        install_wave8_early_states_entities(installed_entities)
        self.assertEqual(set(installed_entities), entity_ids)
        installed_sources: dict[str, dict] = {}
        install_wave8_early_states_sources(installed_sources)
        self.assertEqual(set(installed_sources), source_ids)

    def test_identity_windows_are_precise_and_generic_labels_forbidden(self) -> None:
        entities = {entity["id"]: entity for entity in WAVE8_EARLY_STATES_ENTITIES}
        self.assertEqual(
            (
                entities["medinan_muslim_polity_622_632"]["start_year"],
                entities["medinan_muslim_polity_622_632"]["end_year"],
            ),
            (622, 632),
        )
        self.assertEqual(
            (
                entities["arsacid_empire"]["start_year"],
                entities["arsacid_empire"]["end_year"],
                entities["arsacid_empire"]["aliases"],
            ),
            (-247, 224, []),
        )
        for entity_id, entity in entities.items():
            if entity_id not in {
                "medinan_muslim_polity_622_632",
                "arsacid_empire",
            }:
                self.assertEqual(
                    entity["start_year"], entity["end_year"], entity_id
                )
        forbidden = {"muslim ummah", "gurkhas", "parthia"}
        for entity in WAVE8_EARLY_STATES_ENTITIES:
            self.assertNotIn(entity["id"].replace("_", " ").casefold(), forbidden)
            self.assertNotIn(entity["name"].casefold(), forbidden)
            self.assertTrue(
                forbidden.isdisjoint(alias.casefold() for alias in entity["aliases"])
            )

    def test_canonical_names_and_exact_sides_are_pinned(self) -> None:
        expected_names = {
            "hced-Ajnadin634-1": "Battle of Ajnadayn",
            "hced-Hunain630-1": "Battle of Hunayn",
            "hced-Khaybar628-1": "Conquest of Khaybar",
            "hced-Madain637-1": "Capture of Ctesiphon/al-Mada’in",
            "hced-Ohud625-1": "Battle of Uhud",
            "hced-Pelusium640-1": "Siege of Pelusium",
            "hced-Ullais633-1": "Battle of Ullais",
            "hced-Walaja633-1": "Battle of Walaja",
            "hced-Yarmuk636-1": "Battle of Yarmuk",
            "hced-Almorah1815-1": "Battle and capture of Almora",
            "hced-Jitgargh1815-1": "Battle of Jitgadhi",
            "hced-Kalanga1814-1": "Siege of Nalapani/Kalanga",
            "hced-Malaon1815-1": "Battle of Malaun/Deothal",
            "hced-Parsa1815-1": "Attack on the Parsa outpost",
            "hced-Arsanias62-1": "Capitulation at Rhandeia on the Arsanias",
            "hced-Atra199-1": "Second siege of Hatra",
            "hced-Carrhae-53-1": "Battle of Carrhae",
            "hced-Ctesiphon198-1": "Capture of Ctesiphon",
            "hced-Gindarus-38-1": "Battle of Gindarus",
            "hced-Hormizdagan224-1": "Battle of Hormozdgan",
            "hced-Zab-130-1": "Battle of the Greater Zab",
        }
        self.assertEqual(
            {
                candidate_id: contract["canonical_event"]["name"]
                for candidate_id, contract in WAVE8_EARLY_STATES_CONTRACTS.items()
            },
            expected_names,
        )
        expected_sides = {
            "hced-Ajnadin634-1": (("rashidun_caliphate",), ("byzantine_empire",)),
            "hced-Hunain630-1": (("medinan_muslim_polity_622_632",), ("hawazin_thaqif_coalition_hunayn_630",)),
            "hced-Khaybar628-1": (("medinan_muslim_polity_622_632",), ("khaybar_oasis_defenders_628",)),
            "hced-Madain637-1": (("rashidun_caliphate",), ("sasanian_empire",)),
            "hced-Ohud625-1": (("medinan_muslim_polity_622_632",), ("quraysh_meccan_field_force_uhud_625",)),
            "hced-Pelusium640-1": (("rashidun_caliphate",), ("byzantine_pelusium_garrison_640",)),
            "hced-Ullais633-1": (("rashidun_caliphate",), ("ullais_sasanian_christian_arab_coalition_633",)),
            "hced-Walaja633-1": (("rashidun_caliphate",), ("walaja_sasanian_christian_arab_coalition_633",)),
            "hced-Yarmuk636-1": (("rashidun_caliphate",), ("byzantine_empire",)),
            "hced-Almorah1815-1": (("nicolls_eic_kumaon_field_force_1815",), ("bam_shah_nepalese_kumaon_force_1815",)),
            "hced-Jitgargh1815-1": (("ujir_singh_thapa_jitgadhi_force_1815",), ("wood_eic_butwal_column_1815",)),
            "hced-Kalanga1814-1": (("gillespie_mawby_eic_doon_force_1814",), ("balbhadra_kunwar_nalapani_garrison_1814",)),
            "hced-Malaon1815-1": (("ochterlony_eic_malaun_force_1815",), ("amar_singh_thapa_malaun_force_1815",)),
            "hced-Parsa1815-1": (("nepalese_parsa_attack_force_1815",), ("eic_parsa_outpost_1815",)),
            "hced-Arsanias62-1": (("arsacid_empire",), ("roman_empire",)),
            "hced-Atra199-1": (("hatra_kingdom_defenders_199",), ("roman_empire",)),
            "hced-Carrhae-53-1": (("arsacid_empire",), ("roman_republic",)),
            "hced-Ctesiphon198-1": (("roman_empire",), ("arsacid_empire",)),
            "hced-Gindarus-38-1": (("roman_republic",), ("arsacid_empire",)),
            "hced-Hormizdagan224-1": (("sasanian_empire",), ("arsacid_empire",)),
            "hced-Zab-130-1": (("clio_ir_seleucid_emp_bce318_21d0ee32",), ("arsacid_empire",)),
        }
        self.assertEqual(
            {
                candidate_id: (
                    tuple(contract["side_1_entity_ids"]),
                    tuple(contract["side_2_entity_ids"]),
                )
                for candidate_id, contract in WAVE8_EARLY_STATES_CONTRACTS.items()
            },
            expected_sides,
        )

    def test_uhud_is_the_only_direct_outcome_override(self) -> None:
        override_ids = {
            candidate_id
            for candidate_id, contract in WAVE8_EARLY_STATES_CONTRACTS.items()
            if contract["source_outcome_override"]
        }
        self.assertEqual(override_ids, {"hced-Ohud625-1"})
        uhud = WAVE8_EARLY_STATES_CONTRACTS["hced-Ohud625-1"]
        self.assertEqual(uhud["winner_side"], 2)
        self.assertEqual(
            uhud["outcome_source_ids"],
            ["ucpress_quran_and_conquest_chapter_1"],
        )
        source_by_id = {source["id"]: source for source in WAVE8_EARLY_STATES_SOURCES}
        self.assertIn(
            "outcome",
            source_by_id[uhud["outcome_source_ids"][0]]["evidence_roles"],
        )

        entities, existing = self._entities_and_existing()
        by_id = {
            event["hced_candidate_id"]: event
            for event in promote_wave8_early_states_contracts(
                _rows(), entities, existing
            )
        }
        winners = {
            participant["entity_id"]
            for participant in by_id["hced-Ohud625-1"]["participants"]
            if participant["side"] == "side_a"
        }
        self.assertEqual(winners, {"quraysh_meccan_field_force_uhud_625"})
        self.assertEqual(
            by_id["hced-Ohud625-1"]["outcome_source_ids"],
            ["ucpress_quran_and_conquest_chapter_1"],
        )
        for candidate_id in WAVE8_EARLY_STATES_CONTRACT_IDS - override_ids:
            self.assertEqual(by_id[candidate_id]["outcome_source_ids"], ["hced_dataset"])

    def test_holds_terminal_exclusions_and_duplicate_guard_never_emit(self) -> None:
        terminal = {
            candidate_id
            for candidate_id, hold in WAVE8_EARLY_STATES_HOLDS.items()
            if hold.get("terminal_exclusion")
        }
        self.assertEqual(terminal, {"hced-Mecca630-1", "hced-Yarmuk634-1"})
        self.assertEqual(
            WAVE8_EARLY_STATES_HOLDS["hced-Mecca630-1"]["hold_category"],
            "exclude_not_discrete_engagement",
        )
        yarmuk = WAVE8_EARLY_STATES_HOLDS["hced-Yarmuk634-1"]
        self.assertEqual(
            yarmuk["hold_category"], "exclude_duplicate_of_reviewed_candidate"
        )
        self.assertEqual(yarmuk["duplicate_of_candidate_id"], "hced-Yarmuk636-1")
        self.assertIn("hced-Yarmuk636-1", WAVE8_EARLY_STATES_CONTRACT_IDS)
        self.assertEqual(
            WAVE8_EARLY_STATES_HOLDS["hced-Jaitak1814-1815-1"]["canonical_event"]["year_high"],
            1815,
        )

        entities, existing = self._entities_and_existing()
        emitted = {
            event["hced_candidate_id"]
            for event in promote_wave8_early_states_contracts(
                _rows(), entities, existing
            )
        }
        self.assertEqual(emitted, WAVE8_EARLY_STATES_CONTRACT_IDS)
        self.assertTrue(WAVE8_EARLY_STATES_HOLD_IDS.isdisjoint(emitted))

    def test_emitted_events_have_exact_provenance_and_winner_orientation(self) -> None:
        entities, existing = self._entities_and_existing()
        events = promote_wave8_early_states_contracts(_rows(), entities, existing)
        self.assertEqual(len(events), 21)
        by_id = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_id), WAVE8_EARLY_STATES_CONTRACT_IDS)
        for candidate_id, event in by_id.items():
            Event.from_dict(event)
            contract = WAVE8_EARLY_STATES_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith("hced_wave8_early_states_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )
            self.assertEqual(
                event["source_ids"], ["hced_dataset", *contract["evidence_refs"]]
            )
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertIn("Candidate-keyed Wave 8 tactical assertion", event["summary"])
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["side"] == "side_a"
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["side"] == "side_b"
            }
            winner_side = contract["winner_side"]
            self.assertEqual(winners, set(contract[f"side_{winner_side}_entity_ids"]))
            self.assertEqual(losers, set(contract[f"side_{3 - winner_side}_entity_ids"]))

        self.assertEqual(by_id["hced-Ohud625-1"]["aliases"], ["Ohud"])
        self.assertEqual(by_id["hced-Almorah1815-1"]["aliases"], ["Almorah"])
        self.assertEqual(by_id["hced-Atra199-1"]["aliases"], ["Atra"])


if __name__ == "__main__":
    unittest.main()
