import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "data" / "release"
REGISTRY = ROOT / "data" / "catalog" / "registry.json"
RESULTS = ROOT / "web" / "data" / "results.json"

APPROVED_HCED = {
    "hced-Miletus-334-1",
    "hced-Issus-333-1",
    "hced-Sebastopolis692-1",
    "hced-Yaunis Khan1516-1",
    "hced-Slaak1631-1",
    "hced-Sas van Gent1644-1",
    "hced-Saints1782-1",
}
BLOCKED_HCED = {
    "hced-Megalopolis-331-1",
    "hced-Jaxartes-329-1",
    "hced-Antioch1268-1",
    "hced-Mons1572-1",
    "hced-Steenwijk1592-1",
    "hced-Amjhera1728-1",
    "hced-Abensberg1809-1",
    "hced-Hudayda1934-1",
}


class Wave5ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads((RELEASE / "events.json").read_text(encoding="utf-8"))
        cls.entities = json.loads((RELEASE / "entities.json").read_text(encoding="utf-8"))
        cls.sources = json.loads((RELEASE / "sources.json").read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))
        cls.events_by_id = {event["id"]: event for event in cls.events}
        cls.registry_by_id = {
            entity["id"]: entity for entity in cls.registry["entities"]
        }

    def test_exact_release_composition_and_approved_candidate_set(self) -> None:
        families = Counter(
            tuple(event.get("outcome_source_family_ids", ()))
            for event in self.events
        )
        self.assertEqual(len(self.events), 4_406)
        self.assertEqual(len(self.entities), 236)
        self.assertEqual(len(self.registry_by_id), 1_598)
        self.assertEqual(
            families,
            {
                (): 40,
                ("hced",): 4_152,
                ("iwd",): 64,
                ("iwbd",): 143,
                ("ucdp_conflict_termination",): 7,
            },
        )
        hced_candidates = {
            event["hced_candidate_id"]
            for event in self.events
            if "hced_candidate_id" in event
        }
        self.assertTrue(APPROVED_HCED <= hced_candidates)
        self.assertTrue(BLOCKED_HCED.isdisjoint(hced_candidates))
        iwbd_candidates = {
            event["iwbd_candidate_id"]
            for event in self.events
            if "iwbd_candidate_id" in event
        }
        self.assertTrue({"iwbd-52-18-185", "iwbd-118-45-842"} <= iwbd_candidates)
        iwd_parents = {
            event["iwd_parent_war_id"]
            for event in self.events
            if "iwd_parent_war_id" in event
        }
        self.assertTrue({"15", "48"} <= iwd_parents)
        self.assertIn("1", iwd_parents)
        self.assertEqual(
            sum(len(event.get("iwd_components", ())) for event in self.events),
            100,
        )
        self.assertEqual(len(self.results["events"]), 4_406)

    def test_abtao_and_mishan_are_exact_candidate_keyed_events(self) -> None:
        abtao = self.events_by_id["iwbd_iwbd_52_18_185_abtao"]
        abtao_participants = {
            participant["entity_id"]: participant
            for participant in abtao["participants"]
        }
        self.assertEqual(
            set(abtao_participants),
            {
                "spanish_empire",
                "clio_ch_chile_rep_1_1812_3b31ba25",
                "clio_q419_1822_a6e12c5b",
            },
        )
        self.assertEqual(abtao_participants["spanish_empire"]["contribution"], 1.0)
        self.assertEqual(
            abtao_participants["clio_ch_chile_rep_1_1812_3b31ba25"]["contribution"],
            0.5,
        )
        self.assertEqual(
            abtao_participants["clio_q419_1822_a6e12c5b"]["contribution"],
            0.5,
        )
        self.assertTrue(
            all(
                participant["result_class"] == "stalemate_or_inconclusive"
                for participant in abtao["participants"]
            )
        )

        mishan = self.events_by_id["iwbd_iwbd_118_45_842_mishan"]
        self.assertEqual((mishan["year"], mishan["end_year"]), (1929, 1929))
        self.assertEqual(mishan["iwbd_duration_days"], "2")
        self.assertEqual(
            {participant["entity_id"] for participant in mishan["participants"]},
            {"soviet_union", "clio_cn_chinese_rep_1912_970b7032"},
        )

    def test_registry_absorption_and_saudi_migration_are_exact(self) -> None:
        for entity_id in (
            "united_states_colombia",
            "kingdom_saudi_arabia",
            "mutawakkilite_kingdom_yemen",
        ):
            self.assertIn(entity_id, self.registry_by_id)
            self.assertFalse(self.registry_by_id[entity_id].get("aliases"))

        self.assertNotIn("clio_q851_1936_a94f117c", self.registry_by_id)
        self.assertNotIn("clio_q1061488_1863_68491004", self.registry_by_id)
        self.assertIn("clio_q739_1866_25817025", self.registry_by_id)
        self.assertIn("clio_q1998401_1919_31438771", self.registry_by_id)

        saudi_event_ids = {
            event["id"]
            for event in self.events
            if any(
                participant["entity_id"] == "kingdom_saudi_arabia"
                for participant in event["participants"]
            )
        }
        self.assertEqual(
            saudi_event_ids,
            {
                "iwd_war_48_saudi_arabia_yemen_1934",
                "iwd_war_70_yom_kippur_1973",
                "iwd_war_82_gulf_war_1991",
            },
        )
        self.assertFalse(
            any(
                participant["entity_id"] == "clio_q851_1936_a94f117c"
                for event in self.events
                for participant in event["participants"]
            )
        )

    def test_source_expansion_is_narrow_and_canonical(self) -> None:
        self.assertEqual(len(self.sources), 106)
        self.assertEqual(
            len({source["source_family_id"] for source in self.sources}),
            31,
        )
        new_source_ids = {
            "colombia_constitution_1863",
            "state_department_colombia_history",
            "saudi_mofa_history",
            "uk_archives_yemen_1918",
            "oeaw_mutawakkilite_yemen",
        }
        by_id = {source["id"]: source for source in self.sources}
        self.assertTrue(new_source_ids <= set(by_id))
        for source_id in new_source_ids:
            self.assertEqual(
                by_id[source_id]["evidence_roles"],
                ["identity_boundary_or_context_reference"],
            )


if __name__ == "__main__":
    unittest.main()
