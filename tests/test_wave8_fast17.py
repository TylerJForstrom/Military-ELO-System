import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_fast17 import (
    WAVE8_FAST17_CONTRACT_IDS,
    WAVE8_FAST17_CONTRACTS,
    WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_FAST17_ENTITIES,
    WAVE8_FAST17_FINAL_AUDIT_SIGNATURE,
    WAVE8_FAST17_HOLD_IDS,
    WAVE8_FAST17_HOLDS,
    WAVE8_FAST17_IWBD_DUPLICATE_HOLD_IDS,
    WAVE8_FAST17_IWBD_DUPLICATE_HOLDS,
    WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS,
    WAVE8_FAST17_RESERVED_IDS,
    WAVE8_FAST17_SOURCES,
    install_wave8_fast17_entities,
    install_wave8_fast17_sources,
    promote_wave8_fast17_contracts,
    validate_wave8_fast17_queue_contracts,
    wave8_fast17_cohort_counts,
    wave8_fast17_counts,
    wave8_fast17_location_quarantine_additions,
    wave8_fast17_signature,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_fast17_"


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


EXPECTED_SIDES = {
    "hced-Assietta1747-1": (
        ("kingdom_sardinia_piedmont", "habsburg_monarchy"),
        ("kingdom_france",),
    ),
    "hced-Belgrade1807-1": (
        ("serbian_revolutionary_forces_1804_1815",),
        ("ottoman_empire",),
    ),
    "hced-Casteldelfino1744-1": (
        ("kingdom_france",),
        ("kingdom_sardinia_piedmont",),
    ),
    "hced-Deligrad1806-1": (
        ("serbian_revolutionary_forces_1804_1815",),
        ("ottoman_empire",),
    ),
    "hced-Groenkloof1901-1": (
        ("united_kingdom",),
        ("lotter_commando_1901",),
    ),
    "hced-Ivanovatz1805-1": (
        ("serbian_revolutionary_forces_1804_1815",),
        ("ottoman_empire",),
    ),
    "hced-Ladysmith1899-1900-1": (
        ("united_kingdom",),
        ("south_african_republic", "orange_free_state_1854"),
    ),
    "hced-La Maddalena1793-1": (
        ("kingdom_sardinia_piedmont",),
        ("french_first_republic",),
    ),
    "hced-Madonna del Olmo1744-1": (
        ("kingdom_france", "spanish_empire"),
        ("kingdom_sardinia_piedmont",),
    ),
    "hced-Moedwil1901-1": (
        ("united_kingdom",),
        ("south_african_republic",),
    ),
    "hced-Nish1809-1": (
        ("ottoman_empire",),
        ("serbian_revolutionary_forces_1804_1815",),
    ),
    "hced-Poplar Grove1900-1": (
        ("united_kingdom",),
        ("south_african_republic", "orange_free_state_1854"),
    ),
    "hced-Sannahs Post1916-1": (
        ("orange_free_state_1854",),
        ("united_kingdom",),
    ),
    "hced-Tugela Heights1900-1": (
        ("united_kingdom",),
        ("south_african_republic", "orange_free_state_1854"),
    ),
    "hced-Vaal Kranz1900-1": (
        ("orange_free_state_1854", "south_african_republic"),
        ("united_kingdom",),
    ),
    "hced-Vicenza1848-1": (
        ("austrian_empire",),
        ("durando_vicenza_defense_force_1848",),
    ),
    "hced-Wagon Hill1900-1": (
        ("united_kingdom",),
        ("orange_free_state_1854",),
    ),
}


EXPECTED_CANONICAL_EVENTS = {
    "hced-Assietta1747-1": ("Battle of Assietta", 1747, 1747, "engagement"),
    "hced-Belgrade1807-1": (
        "Capture of Belgrade Fortress",
        1807,
        1807,
        "siege",
    ),
    "hced-Casteldelfino1744-1": (
        "Second Battle of Casteldelfino (Pietralunga)",
        1744,
        1744,
        "engagement",
    ),
    "hced-Deligrad1806-1": ("Battle of Deligrad", 1806, 1806, "engagement"),
    "hced-Groenkloof1901-1": (
        "Battle of Groenkloof",
        1901,
        1901,
        "engagement",
    ),
    "hced-Ivanovatz1805-1": (
        "Battle of Ivankovac",
        1805,
        1805,
        "engagement",
    ),
    "hced-Ladysmith1899-1900-1": (
        "Siege of Ladysmith",
        1899,
        1900,
        "siege",
    ),
    "hced-La Maddalena1793-1": (
        "Defense of La Maddalena",
        1793,
        1793,
        "engagement",
    ),
    "hced-Madonna del Olmo1744-1": (
        "Battle of Madonna dell'Olmo",
        1744,
        1744,
        "engagement",
    ),
    "hced-Moedwil1901-1": ("Battle of Moedwil", 1901, 1901, "engagement"),
    "hced-Nish1809-1": ("Battle of Čegar", 1809, 1809, "engagement"),
    "hced-Poplar Grove1900-1": (
        "Battle of Poplar Grove",
        1900,
        1900,
        "engagement",
    ),
    "hced-Sannahs Post1916-1": (
        "Battle of Sanna's Post",
        1900,
        1900,
        "engagement",
    ),
    "hced-Tugela Heights1900-1": (
        "Battle of Tugela Heights",
        1900,
        1900,
        "engagement_series",
    ),
    "hced-Vaal Kranz1900-1": (
        "Battle of Vaalkrans",
        1900,
        1900,
        "engagement",
    ),
    "hced-Vicenza1848-1": ("Battle of Vicenza", 1848, 1848, "engagement"),
    "hced-Wagon Hill1900-1": (
        "Battle of Wagon Hill",
        1900,
        1900,
        "engagement",
    ),
}


class Wave8Fast17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")

    def _installed_entities_sources_and_existing(self):
        entity_ids = {str(entity["id"]) for entity in WAVE8_FAST17_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
            if entity["id"] not in entity_ids
        }
        install_wave8_fast17_entities(entities)

        source_ids = {str(source["id"]) for source in WAVE8_FAST17_SOURCES}
        sources = {
            str(source["id"]): source
            for source in _json(ROOT / "data" / "release" / "sources.json")
            if source["id"] not in source_ids
        }
        install_wave8_fast17_sources(sources)

        existing = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE8_FAST17_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed_entities_sources_and_existing()
        events = promote_wave8_fast17_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_complete_signature_inventory_counts_and_cohorts_are_pinned(self) -> None:
        signature_payload = {
            "contracts": WAVE8_FAST17_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_FAST17_ENTITIES,
            "holds": WAVE8_FAST17_HOLDS,
            "iwbd_duplicate_holds": WAVE8_FAST17_IWBD_DUPLICATE_HOLDS,
            "point_quarantine_additions": sorted(
                WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_FAST17_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(signature_payload).encode()
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_FAST17_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_fast17_signature(), independent_signature)
        self.assertEqual((len(WAVE8_FAST17_CONTRACT_IDS), len(WAVE8_FAST17_HOLD_IDS)), (17, 0))
        self.assertEqual(WAVE8_FAST17_RESERVED_IDS, WAVE8_FAST17_CONTRACT_IDS)
        self.assertEqual(
            wave8_fast17_counts(),
            {
                "country_quarantine_additions": 1,
                "holds": 0,
                "iwbd_duplicate_holds": 1,
                "new_entities": 2,
                "new_sources": 15,
                "newly_rated_events": 17,
                "point_quarantine_additions": 3,
                "promotion_contracts": 17,
                "reviewed_hced_rows": 17,
            },
        )
        self.assertEqual(
            wave8_fast17_cohort_counts(),
            {
                "first_italian_war_of_independence": 1,
                "first_serbian_uprising": 4,
                "french_revolutionary_wars": 1,
                "second_anglo_boer_war": 8,
                "war_of_austrian_succession": 3,
            },
        )

    def test_entities_sources_and_canonical_provenance_parse(self) -> None:
        self.assertEqual((len(WAVE8_FAST17_ENTITIES), len(WAVE8_FAST17_SOURCES)), (2, 15))
        for entity in WAVE8_FAST17_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertEqual(entity["source_ids"], sorted(set(entity["source_ids"])))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        for source in WAVE8_FAST17_SOURCES:
            Source.from_dict(source)
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        entities, sources, _ = self._installed_entities_sources_and_existing()
        for entity in WAVE8_FAST17_ENTITIES:
            Entity.from_dict(entities[entity["id"]])
        for source in WAVE8_FAST17_SOURCES:
            Source.from_dict(sources[source["id"]])

    def test_all_17_queue_hashes_validate_and_drift_fails_closed(self) -> None:
        self.assertEqual(
            validate_wave8_fast17_queue_contracts(self.hced_rows),
            {"promotion_contracts": 17, "holds": 0, "reviewed_hced_rows": 17},
        )
        rows_by_id = {row["candidate_id"]: row for row in self.hced_rows}
        for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items():
            self.assertEqual(
                canonical_hced_row_sha256(rows_by_id[candidate_id]),
                contract["raw_row_sha256"],
            )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Sannahs Post1916-1"
        )["winner_raw"] = "unknown"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_fast17_queue_contracts(changed)

    def test_exact_sides_dates_direct_winners_and_no_reversals(self) -> None:
        rows_by_id = {row["candidate_id"]: row for row in self.hced_rows}
        actual_sides = {
            candidate_id: (
                tuple(contract["side_1_entity_ids"]),
                tuple(contract["side_2_entity_ids"]),
            )
            for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items()
        }
        self.assertEqual(actual_sides, EXPECTED_SIDES)
        actual_events = {
            candidate_id: (
                contract["canonical_event"]["name"],
                contract["canonical_event"]["year_low"],
                contract["canonical_event"]["year_high"],
                contract["canonical_event"]["granularity"],
            )
            for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items()
        }
        self.assertEqual(actual_events, EXPECTED_CANONICAL_EVENTS)
        for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items():
            row = rows_by_id[candidate_id]
            self.assertIs(contract["source_outcome_override"], False)
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract.get("result_type", "win"), "win")
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
            self.assertEqual(
                (row["year_low"], row["year_high"]),
                (
                    contract["canonical_event"]["year_low"],
                    contract["canonical_event"]["year_high"],
                ),
            )

    def test_every_outcome_is_direct_and_all_provenance_lists_are_canonical(self) -> None:
        sources = {source["id"]: source for source in WAVE8_FAST17_SOURCES}
        for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items():
            evidence = contract["evidence_refs"]
            outcome_ids = contract["outcome_source_ids"]
            family_ids = contract["outcome_source_family_ids"]
            self.assertEqual(evidence, sorted(set(evidence)), candidate_id)
            self.assertEqual(outcome_ids, sorted(set(outcome_ids)), candidate_id)
            self.assertEqual(family_ids, sorted(set(family_ids)), candidate_id)
            self.assertTrue(outcome_ids, candidate_id)
            self.assertNotIn("hced_dataset", outcome_ids, candidate_id)
            self.assertLessEqual(set(outcome_ids), set(evidence), candidate_id)
            self.assertTrue(
                all("outcome" in sources[source_id]["evidence_roles"] for source_id in outcome_ids),
                candidate_id,
            )
            self.assertEqual(
                family_ids,
                sorted({sources[source_id]["source_family_id"] for source_id in outcome_ids}),
                candidate_id,
            )

    def test_current_artifacts_emit_and_parse_exactly_17_when_lane_filtered(self) -> None:
        entities, sources, events = self._emit()
        self.assertEqual(len(events), 17)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_FAST17_CONTRACT_IDS,
        )
        self.assertTrue(WAVE8_FAST17_HOLD_IDS.isdisjoint(event["hced_candidate_id"] for event in events))
        self.assertEqual(len({event["canonical_event_key"] for event in events}), 17)

        for entity in WAVE8_FAST17_ENTITIES:
            Entity.from_dict(entities[entity["id"]])
        for source in WAVE8_FAST17_SOURCES:
            Source.from_dict(sources[source["id"]])
        for event in events:
            parsed = Event.from_dict(event)
            contract = WAVE8_FAST17_CONTRACTS[event["hced_candidate_id"]]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], contract["canonical_event"]["name"])
            self.assertEqual(event["reviewed_granularity"], contract["canonical_event"]["granularity"])
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(
                event["source_ids"],
                sorted(set(["hced_dataset", *contract["evidence_refs"]])),
            )
            self.assertEqual(tuple(event["source_ids"]), parsed.source_ids)

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
            self.assertEqual(winners, set(contract["side_1_entity_ids"]))
            self.assertEqual(losers, set(contract["side_2_entity_ids"]))

    def test_location_additions_are_exported_without_mutating_shared_manifests(self) -> None:
        before_points = HCED_POINT_QUARANTINE_IDS
        before_countries = HCED_COUNTRY_QUARANTINE_IDS
        self.assertEqual(
            WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS,
            {
                "hced-Groenkloof1901-1",
                "hced-Nish1809-1",
                "hced-Vaal Kranz1900-1",
            },
        )
        self.assertEqual(
            WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-La Maddalena1793-1"},
        )
        self.assertEqual(
            wave8_fast17_location_quarantine_additions(),
            {
                "country": WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS,
            },
        )
        self._emit()
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_vicenza_iwbd_duplicate_hold_is_exact_and_singleton(self) -> None:
        self.assertEqual(WAVE8_FAST17_IWBD_DUPLICATE_HOLD_IDS, {"iwbd-10-4-40"})
        hold = WAVE8_FAST17_IWBD_DUPLICATE_HOLDS["iwbd-10-4-40"]
        self.assertEqual(hold["hold_category"], "duplicate_of_exact_hced_event")
        self.assertEqual(
            hold["duplicate_of_hced_candidate_id"],
            "hced-Vicenza1848-1",
        )
        iwbd = next(row for row in self.iwbd_rows if row["candidate_id"] == "iwbd-10-4-40")
        target = WAVE8_FAST17_CONTRACTS[hold["duplicate_of_hced_candidate_id"]]
        self.assertEqual((iwbd["name"], iwbd["start_date"]), ("Vicenza", "1848-06-11"))
        self.assertEqual((iwbd["attacker_raw"], iwbd["winner_raw"]), ("Austria", "Austria"))
        self.assertEqual(iwbd["defender_raw"], "Sardinia")
        self.assertEqual(
            (target["canonical_event"]["name"], target["canonical_event"]["year_low"]),
            ("Battle of Vicenza", 1848),
        )
        self.assertEqual(
            target["side_2_entity_ids"],
            ["durando_vicenza_defense_force_1848"],
        )


if __name__ == "__main__":
    unittest.main()
