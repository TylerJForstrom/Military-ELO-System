import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_french_religious_forces as lane
from military_elo.promotion.common import _slug, normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_french_religious_forces_"
FINAL_AUDIT_SIGNATURE = (
    "cbca7f8a20ae78e87ea5becc5a73df0cde6272771015e8019d98e77f08df2a70"
)


# hash, name, side 1, side 2, winner, loser, complete, massacre, year, source row
EXPECTED_RAW_ROWS = {
    "hced-Arnay-le-Duc1570-1": (
        "13cad0aecfea5749e90ef645006a7c1f8f505379d4861891e09dacc45fbc2cbb",
        "Arnay-le-Duc",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1570,
        1077,
    ),
    "hced-Auneau1587-1": (
        "ad83416d7a4b0330ec9f6dcf0e5d9a056cd6431f4f86e3a7f139a59820b0dbb9",
        "Auneau",
        "French Catholics",
        "German Protestants",
        "French Catholics",
        "German Protestants",
        True,
        "No",
        1587,
        1317,
    ),
    "hced-Caudebec1592-1": (
        "efae7cf23eb895cf2beb23ab1a623e3bb7cc71837a4b69328ac379244b86cb2b",
        "Caudebec",
        "French Catholics",
        "French Protestants",
        "Draw",
        None,
        False,
        "No",
        1592,
        3343,
    ),
    "hced-Coutras1587-1": (
        "30f4251cb53d3e5e3a50ab1e9a6df37f92f0e4b70636b97fbfec6d1e4c320abd",
        "Coutras",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1587,
        4199,
    ),
    "hced-Dormans1575-1": (
        "6625e3af5daf8ae169d81371b5cd9f51f42b3b77096bc47e0c6e896913c5b9c6",
        "Dormans",
        "French Catholics",
        "French Protestants, German Protestants, moderate French Catholics",
        "French Catholics",
        "French Protestants, German Protestants, moderate French Catholics",
        True,
        "No",
        1575,
        4869,
    ),
    "hced-Dreux1562-1": (
        "5fb72b9d0c6ce35be86dbcfa3eaa2703e0055b463c4f49ab02a5928d082d4114",
        "Dreux",
        "French Catholics",
        "French Protestants, German Protestants",
        "French Catholics",
        "French Protestants, German Protestants",
        True,
        "No",
        1562,
        4923,
    ),
    "hced-Jarnac1569-1": (
        "518856899a604c04272dbb6ce64ef276029c5c8b976c6c1c411fdd18b83f4b12",
        "Jarnac",
        "French Catholics",
        "Hugenots",
        "French Catholics",
        "Hugenots",
        True,
        "No",
        1569,
        7629,
    ),
    "hced-La Roche-LAbeille1569-1": (
        "e06fc6e708fa5c25a402451a715c221225c1f34ab337f229ba9a35eb81115af4",
        "La Roche-LAbeille",
        "French Protestants, German Protestants",
        "French Catholics",
        "French Protestants, German Protestants",
        "French Catholics",
        True,
        "No",
        1569,
        8989,
    ),
    "hced-La Rochelle1572-1": (
        "76216489e2747c83938abacc25018f62e79a6048011fab366c18eb228652e733",
        "La Rochelle",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1572,
        8993,
    ),
    "hced-La Rochelle1625-1": (
        "438c068b0e68f5418868a84cc57038e3c6a1c830e36cfca669f6f4cc7b66d743",
        "La Rochelle",
        "France",
        "French Protestants",
        "France",
        "French Protestants",
        True,
        "No",
        1625,
        8995,
    ),
    "hced-Moncontour1569-1": (
        "ec16b2f2e9d25ced3abf51cce394baac6e53adf8dae600edad464e3110497ae5",
        "Moncontour",
        "French Catholics, Spain, Italy, Switzerland",
        "French Protestants",
        "French Catholics, Spain, Italy, Switzerland",
        "French Protestants",
        True,
        "No",
        1569,
        10627,
    ),
    "hced-Montauban1621-1": (
        "5de093403012133090997dc51f6bf6283c800f88f4e73cf010ea3514c6cd7271",
        "Montauban",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1621,
        10681,
    ),
    "hced-Orleans1563-1": (
        "be505efe254719fb1ce447b70c04792795554e53cdcff5702881b9569ceb4c67",
        "Orleans",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1563,
        11897,
    ),
    "hced-Orthez1569-1": (
        "cd771a92c114310993840d3f8c58cd8c43f36997fe365ae29ed57176e561251a",
        "Orthez",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        True,
        "No",
        1569,
        11917,
    ),
    "hced-Paris1590-1": (
        "07e8b3c944f82fc2a5f7fc67c8677741b585920ee238843ffd82e710297dd4c1",
        "Paris",
        "Spain, French Catholics",
        "French Protestants",
        "Spain, French Catholics",
        "French Protestants",
        True,
        "No",
        1436,
        12197,
    ),
    "hced-Poitiers1569-1": (
        "110f8c121a94f6a6ff9514d3dc597735fbe03d826ffbb96b2aa1f269020ba5cb",
        "Poitiers",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        True,
        "No",
        1569,
        12661,
    ),
    "hced-Rouen1562-1": (
        "b82a47acce32568db414954bcb4daadd774bc1a6ba53aeb048282cb26fcf3ac0",
        "Rouen",
        "French Catholics",
        "French Protestants, England",
        "French Catholics",
        "French Protestants, England",
        True,
        "No",
        1562,
        13593,
    ),
    "hced-Rouen1591-1": (
        "cfcc4a7a84e8b7d33e748a396387392a0cdba056a1d70959159da128eed32691",
        "Rouen",
        "Holy League",
        "French Protestants",
        "Holy League",
        "French Protestants",
        True,
        "No",
        1591,
        13595,
    ),
    "hced-St Denis, France1567-1": (
        "55c075c45c352134fdf91017a43d45aa6f3b214d290982f360c03410ab8c865e",
        "St Denis, France",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        True,
        "No",
        1567,
        13769,
    ),
    "hced-St Jean dAngely1621-1": (
        "2cbeff4bc1938d344f057b80a41086f88aac872e5a7a506b56e41517a3ffca13",
        "St Jean dAngely",
        "France",
        "French Protestants",
        "France",
        "French Protestants",
        True,
        "No",
        1621,
        13801,
    ),
    "hced-Vassy1562-1": (
        "aaa336e4a6665261ce0c6ea07831a6ed5d76141786ddcc3c7af34ad3f1288d94",
        "Vassy",
        "French Catholics",
        "French Protestants",
        "Massacre",
        None,
        False,
        "Yes",
        1562,
        16665,
    ),
    "hced-Vergt1562-1": (
        "2e3725453cec199c1242ca60ce445ad1eee4dc82756c761aeaf11cb7b479ac81",
        "Vergt",
        "French Catholics",
        "French Protestants",
        "French Catholics",
        "French Protestants",
        True,
        "No",
        1562,
        16765,
    ),
}


EXPECTED_PROMOTIONS = {
    "hced-Arnay-le-Duc1570-1": (
        "Battle of Arnay-le-Duc",
        "month",
        "coligny_huguenot_field_army_arnay_1570",
        "cosse_royal_interception_force_arnay_1570",
    ),
    "hced-Auneau1587-1": (
        "Battle of Auneau",
        "day",
        "guise_catholic_league_army_auneau_1587",
        "dohna_german_protestant_relief_army_auneau_1587",
    ),
    "hced-Coutras1587-1": (
        "Battle of Coutras",
        "day",
        "navarre_huguenot_army_coutras_1587",
        "joyeuse_royal_army_coutras_1587",
    ),
    "hced-Dormans1575-1": (
        "Battle of Dormans",
        "day",
        "guise_royal_army_dormans_1575",
        "thore_german_malcontent_army_dormans_1575",
    ),
    "hced-Dreux1562-1": (
        "Battle of Dreux",
        "day",
        "montmorency_guise_royal_army_dreux_1562",
        "conde_coligny_huguenot_german_army_dreux_1562",
    ),
    "hced-Jarnac1569-1": (
        "Battle of Jarnac",
        "day",
        "anjou_tavannes_royal_army_jarnac_1569",
        "conde_coligny_huguenot_army_jarnac_1569",
    ),
    "hced-La Roche-LAbeille1569-1": (
        "Battle of La Roche-l'Abeille",
        "day",
        "coligny_huguenot_german_force_roche_1569",
        "strozzi_royal_detachment_roche_1569",
    ),
    "hced-La Rochelle1625-1": (
        "Naval Battle off Île de Ré",
        "month",
        "montmorency_royal_fleet_re_1625",
        "soubise_rochelais_fleet_re_1625",
    ),
    "hced-Moncontour1569-1": (
        "Battle of Moncontour",
        "day",
        "anjou_royal_coalition_army_moncontour_1569",
        "coligny_huguenot_army_moncontour_1569",
    ),
    "hced-Montauban1621-1": (
        "Siege of Montauban (1621)",
        "month_range",
        "montauban_huguenot_garrison_civic_defenders_1621",
        "louis_xiii_royal_siege_army_montauban_1621",
    ),
    "hced-Orthez1569-1": (
        "Battle and Capture of Orthez",
        "day_range",
        "montgomery_huguenot_bearn_force_orthez_1569",
        "terride_royalist_bearn_force_orthez_1569",
    ),
    "hced-Poitiers1569-1": (
        "Siege of Poitiers (1569)",
        "day_range",
        "guise_poitiers_royalist_garrison_1569",
        "coligny_huguenot_siege_army_poitiers_1569",
    ),
    "hced-Rouen1562-1": (
        "Siege of Rouen (1562)",
        "month_range",
        "guise_royal_siege_army_rouen_1562",
        "rouen_huguenot_english_garrison_1562",
    ),
    "hced-St Denis, France1567-1": (
        "Battle of Saint-Denis",
        "day",
        "montmorency_royal_army_saint_denis_1567",
        "conde_huguenot_field_army_saint_denis_1567",
    ),
    "hced-St Jean dAngely1621-1": (
        "Siege of Saint-Jean-d'Angély (1621)",
        "month_range",
        "louis_xiii_royal_siege_army_saint_jean_1621",
        "soubise_saint_jean_huguenot_garrison_1621",
    ),
    "hced-Vergt1562-1": (
        "Battle of Vergt",
        "day",
        "montluc_royalist_army_vergt_1562",
        "duras_huguenot_relief_army_vergt_1562",
    ),
}


# Historical pre-promotion funnel projection.  The live
# build/hced-unresolved-label-funnel.json no longer carries the two exact
# labels or the promoted candidate rows once the lane is published, so the
# pre-promotion accounting is validated against this exact reconstruction.
HISTORICAL_FUNNEL_LABEL_ROWS = {
    "french catholics": (
        "hced-Arnay-le-Duc1570-1",
        "hced-Auneau1587-1",
        "hced-Caudebec1592-1",
        "hced-Coutras1587-1",
        "hced-Dormans1575-1",
        "hced-Dreux1562-1",
        "hced-Jarnac1569-1",
        "hced-La Roche-LAbeille1569-1",
        "hced-La Rochelle1572-1",
        "hced-Montauban1621-1",
        "hced-Orleans1563-1",
        "hced-Orthez1569-1",
        "hced-Poitiers1569-1",
        "hced-Rouen1562-1",
        "hced-St Denis, France1567-1",
        "hced-Vergt1562-1",
    ),
    "french protestants": (
        "hced-Arnay-le-Duc1570-1",
        "hced-Caudebec1592-1",
        "hced-Coutras1587-1",
        "hced-La Rochelle1572-1",
        "hced-La Rochelle1625-1",
        "hced-Moncontour1569-1",
        "hced-Montauban1621-1",
        "hced-Orleans1563-1",
        "hced-Orthez1569-1",
        "hced-Paris1590-1",
        "hced-Poitiers1569-1",
        "hced-Rouen1591-1",
        "hced-St Denis, France1567-1",
        "hced-St Jean dAngely1621-1",
        "hced-Vergt1562-1",
    ),
}
HISTORICAL_FUNNEL_SOLE_BLOCKERS = {
    "hced-La Rochelle1625-1": "french protestants",
    "hced-Moncontour1569-1": "french protestants",
    "hced-Rouen1562-1": "french catholics",
    "hced-St Jean dAngely1621-1": "french protestants",
}
HISTORICAL_FUNNEL_LABEL_RECORDS = [
    {
        "candidate_ids": [],
        "centuries": {"CE_16": 15, "CE_17": 1},
        "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": (
            "8a2ac2c2783e2e8c11c538a233853f6114fbd0f413cc0958220e91260620f0bd"
        ),
        "events_touched": 16,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 16,
        },
        "label": "french catholics",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 16,
    },
    {
        "candidate_ids": [],
        "centuries": {"CE_15": 1, "CE_16": 11, "CE_17": 3},
        "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": (
            "04cbc352e3049810b7f5781f5871d91ceaf5b2178502b486691119e15b216608"
        ),
        "events_touched": 15,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 15,
        },
        "label": "french protestants",
        "rated_counterpart_entities": 2,
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 15,
    },
]


def _historical_funnel():
    labels_by_candidate = {}
    for label, candidate_ids in HISTORICAL_FUNNEL_LABEL_ROWS.items():
        for candidate_id in candidate_ids:
            labels_by_candidate.setdefault(candidate_id, []).append(label)
    row_label_data = []
    for candidate_id in sorted(labels_by_candidate):
        row = {
            "candidate_id": candidate_id,
            "greedy_eligible": candidate_id != "hced-Paris1590-1",
            "label_failures": [
                {
                    "candidate_ids": [],
                    "failure_case": "zero_time_valid_candidates",
                    "label": label,
                    "time_valid_candidate_ids": [],
                }
                for label in labels_by_candidate[candidate_id]
            ],
        }
        if candidate_id == "hced-Paris1590-1":
            row["other_blockers"] = ["duplicate_of_existing_event"]
        sole_label = HISTORICAL_FUNNEL_SOLE_BLOCKERS.get(candidate_id)
        if sole_label is not None:
            row["sole_blocker_label"] = sole_label
        row_label_data.append(row)
    return {
        "greedy_batch": {"ranking": []},
        "labels": copy.deepcopy(HISTORICAL_FUNNEL_LABEL_RECORDS),
        "row_label_data": row_label_data,
    }


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8FrenchReligiousForcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data/review/hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data/review/iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        labels = {"french catholics", "french protestants"}
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) in labels
            or normalize_label(row.get("side_2_raw")) in labels
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"])
            for entity in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"])
            for source in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_french_religious_forces_entities(entities)
        lane.install_wave8_french_religious_forces_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, sources, existing = self._installed()
        events = lane.promote_wave8_french_religious_forces_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return events, entities, sources, existing

    def test_locked_queues_and_every_exact_raw_row_are_fingerprinted(self):
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_QUEUE_SHA256,
        )
        exact_by_id = {
            str(row["candidate_id"]): row for row in self.exact_rows
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_ROWS))
        self.assertEqual(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_RAW_ROWS),
        )
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            (
                row_hash,
                name,
                side_1,
                side_2,
                winner,
                loser,
                complete,
                massacre,
                year,
                source_row,
            ) = expected
            row = exact_by_id[candidate_id]
            self.assertEqual(
                (
                    row["name"],
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                    row["winner_loser_complete"],
                    row["massacre_raw"],
                    row["year_low"],
                    row["source_row"],
                ),
                (
                    name,
                    side_1,
                    side_2,
                    winner,
                    loser,
                    complete,
                    massacre,
                    year,
                    source_row,
                ),
            )
            self.assertEqual((row["year_low"], row["year_best"], row["year_high"]), (year, year, year))
            self.assertEqual(canonical_hced_row_sha256(row), row_hash)
            self.assertEqual(
                lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[candidate_id],
                row_hash,
            )

    def test_exact_label_inventories_and_cross_label_twins_are_coordinated(self):
        result = lane.validate_wave8_french_religious_forces_queue_contracts(
            self.hced_rows
        )
        self.assertEqual(
            result,
            {
                "french_catholic_exact_rows": 17,
                "french_protestant_exact_rows": 16,
                "holds": 5,
                "promotion_contracts": 16,
                "reviewed_hced_rows": 22,
                "shared_exact_rows": 11,
                "terminal_exclusions": 1,
            },
        )
        catholic = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES[
            "french catholics"
        ]
        protestant = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES[
            "french protestants"
        ]
        self.assertEqual(catholic & protestant, lane.WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS)
        self.assertEqual(len(catholic | protestant), 22)
        self.assertEqual(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS,
            {
                "french catholics": "4ce4b7550abeb80060b2e0075b7d2e20b09576d62e922580ab5653752c36d475",
                "french protestants": "1987e8717d053c927e84f35492dd77ffd5db82f079b46ccf4590a4e8c75f606e",
            },
        )
        self.assertEqual(
            set(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS),
            catholic & protestant,
        )
        for candidate_id, review in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS.items():
            self.assertEqual(
                review["disposition"],
                lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS[candidate_id],
            )
            self.assertIs(review["single_candidate_single_disposition"], True)
            self.assertEqual(review["owner_module"], lane.__name__)

    def test_funnel_pins_both_labels_shared_rows_and_sole_blockers(self):
        historical_funnel = _historical_funnel()
        self.assertEqual(
            lane.validate_wave8_french_religious_forces_funnel(historical_funnel),
            {
                "french_catholic_funnel_rows": 16,
                "french_protestant_funnel_rows": 15,
                "funnel_rows": 21,
                "greedy_eligible_rows": 20,
                "release_lane_overlap": 0,
                "shared_funnel_rows": 10,
                "sole_blocker_rows": 4,
            },
        )
        audit = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_FUNNEL_AUDIT
        self.assertEqual(
            audit["funnel_candidate_id_sha256"],
            "a4e12d53e61a9ab7edc5a4dcd70bb9499bf249eb9be2525c6aae805d9f060f77",
        )
        self.assertEqual(
            audit["greedy_candidate_id_sha256"],
            "183dbadafc58c7096610533dd906eeba35b81de995ffea5756cff439555da4cb",
        )
        self.assertEqual(audit["non_greedy_candidate_ids"], ["hced-Paris1590-1"])
        self.assertNotIn("hced-Vassy1562-1", {
            row["candidate_id"] for row in historical_funnel["row_label_data"]
        })
        for record in audit["labels"].values():
            self.assertEqual(record["candidate_ids"], [])
            self.assertEqual(record["time_valid_candidate_ids"], [])
        self.assertFalse(
            any(
                normalize_label(record.get("label"))
                in {"french catholics", "french protestants"}
                for record in self.funnel.get("labels", [])
            ),
            "the completed French religious forces lane must not remain unresolved",
        )
        live_row_ids = {
            str(row.get("candidate_id"))
            for row in self.funnel.get("row_label_data", [])
        }
        self.assertFalse(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS & live_row_ids,
            "promoted French religious forces candidates must be absent "
            "from the live funnel",
        )

    def test_five_holds_are_unknown_never_draw_and_vassy_is_not_rateable(self):
        expected_holds = {
            "hced-Caudebec1592-1": "compound_maneuver_without_undivided_tactical_result",
            "hced-La Rochelle1572-1": "truncated_multi_year_siege_and_nuanced_settlement",
            "hced-Orleans1563-1": "siege_terminated_without_clean_competitive_winner",
            "hced-Paris1590-1": "raw_date_contamination_and_existing_event_collision",
            "hced-Rouen1591-1": "truncated_siege_and_misbounded_royal_coalition",
        }
        self.assertEqual(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS, frozenset(expected_holds))
        for candidate_id, category in expected_holds.items():
            hold = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS[candidate_id]
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)
            self.assertEqual(hold["hold_category"], category)
            self.assertIn("draw", hold["hold_reason"].casefold())
            for forbidden in (
                "winner_side",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "outcome_source_ids",
                "outcome_source_family_ids",
            ):
                self.assertNotIn(forbidden, hold)
        self.assertEqual(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS["hced-Paris1590-1"]["canonical_event"]["year_low"],
            1590,
        )
        self.assertEqual(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS["hced-La Rochelle1572-1"]["canonical_event"]["year_high"],
            1573,
        )
        exclusion = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS["hced-Vassy1562-1"]
        self.assertEqual(exclusion["disposition"], "terminal_exclude")
        self.assertEqual(exclusion["result_type"], "not_rateable")
        self.assertIn("civilian", exclusion["exclusion_category"])
        self.assertIs(exclusion["outcome_not_adjudicated"], True)
        self.assertNotIn("winner_side", exclusion)
        self.assertFalse(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES)

    def test_sources_entities_and_contracts_are_bounded_and_independent(self):
        source_by_id = {
            source["id"]: source
            for source in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES
        }
        self.assertEqual(len(source_by_id), 21)
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
        entity_by_id = {
            entity["id"]: entity
            for entity in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES
        }
        self.assertEqual(len(entity_by_id), 32)
        for entity in entity_by_id.values():
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("french protestants", note)
            self.assertIn("french catholics", note)
            self.assertNotIn(normalize_label(entity["name"]), {"french protestants", "french catholics"})
        self.assertEqual(set(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS), set(EXPECTED_PROMOTIONS))
        for candidate_id, contract in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS.items():
            name, precision, winner, loser = EXPECTED_PROMOTIONS[candidate_id]
            self.assertEqual(contract["canonical_event"]["name"], name)
            self.assertEqual(contract["canonical_event"]["date_precision"], precision)
            self.assertEqual(contract["side_1_entity_ids"], [winner])
            self.assertEqual(contract["side_2_entity_ids"], [loser])
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            expected_families = sorted({
                source_by_id[source_id]["source_family_id"]
                for source_id in contract["outcome_source_ids"]
            })
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)

    def test_promoter_emits_only_sixteen_bounded_wins(self):
        events, entities, sources, _ = self._events()
        self.assertEqual(len(events), 16)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS,
        )
        self.assertFalse(
            {event["hced_candidate_id"] for event in events}
            & (
                lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS
                | lane.WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
            )
        )
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            name, _, winner, loser = EXPECTED_PROMOTIONS[candidate_id]
            self.assertEqual(event["name"], name)
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["id"], f"{EVENT_ID_PREFIX}{_slug(candidate_id, 80)}")
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["outcome"]["battlefield_control"] > 0.5
            }
            losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["outcome"]["battlefield_control"] < 0.5
            }
            self.assertEqual(winners, {winner})
            self.assertEqual(losers, {loser})
            self.assertLessEqual(set(event["outcome_source_ids"]), set(sources))
            self.assertLessEqual({winner, loser}, set(entities))

    def test_location_quarantine_is_local_point_only_and_retains_france(self):
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        events, _, _, _ = self._events()
        self.assertEqual(
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS),
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS,
        )
        for event in events:
            candidate_id = event["hced_candidate_id"]
            review = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS[candidate_id]
            raw = self.hced_by_id[candidate_id]
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "France")
            self.assertIn("location_provenance", event)
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertEqual(review["retained_country"], "France")
            self.assertEqual(
                review["raw_point"],
                [float(raw["longitude"]), float(raw["latitude"])],
            )
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_hced_iwbd_and_existing_release_duplicate_boundaries_are_pinned(self):
        adjacent = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS
        self.assertEqual(
            set(adjacent),
            {"hced-Havana1555-1", "hced-Ivry1590-1", "hced-La Rochelle1627-1"},
        )
        for candidate_id, review in adjacent.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                review["raw_row_sha256"],
            )
        duplicate = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS["hced-Paris1436-1"]
        self.assertEqual(
            canonical_hced_row_sha256(self.hced_by_id["hced-Paris1436-1"]),
            duplicate["raw_row_sha256"],
        )
        self.assertEqual(duplicate["matched_exact_candidate_id"], "hced-Paris1590-1")
        self.assertFalse(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)
        self.assertEqual(
            set(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS,
        )
        result = lane.validate_wave8_french_religious_forces_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertEqual(result["iwbd_probable_twins"], 0)
        self.assertEqual(result["release_probable_twins"], 0)
        self.assertIn(
            result["release_lane_overlap"],
            (0, len(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS)),
        )
        self.assertEqual(result["existing_release_boundaries_found"], 2)
        self.assertEqual(result["cross_label_twins"], 11)
        self.assertEqual(result["integration_dispositions"], 20)

    def test_integration_fails_closed_on_future_twins_and_nonpromotion_leaks(self):
        _, _, existing = self._installed()
        fake_hced = copy.deepcopy(self.hced_rows)
        fake_hced.append({
            "candidate_id": "hced-future-coutras-twin",
            "name": "Battle of Coutras",
            "year_low": 1587,
            "side_1_raw": "Future A",
            "side_2_raw": "Future B",
        })
        with self.assertRaisesRegex(ValueError, "unreviewed HCED twin"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                fake_hced, self.iwbd_rows, existing
            )
        fake_iwbd = copy.deepcopy(self.iwbd_rows)
        fake_iwbd.append({
            "candidate_id": "iwbd-future-jarnac-twin",
            "name": "Battle of Jarnac",
            "start_date": "1569-03-13",
        })
        with self.assertRaisesRegex(ValueError, "unreviewed IWBD twin"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, fake_iwbd, existing
            )
        fake_release = copy.deepcopy(existing)
        fake_release.append({
            "id": "future_dreux_twin",
            "name": "Battle of Dreux",
            "year": 1562,
        })
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, fake_release
            )
        held_leak = copy.deepcopy(existing)
        held_leak.append({
            "id": "illegal_held_paris",
            "name": "Siege of Paris",
            "year": 1590,
            "hced_candidate_id": "hced-Paris1590-1",
        })
        with self.assertRaisesRegex(ValueError, "held/excluded row was rated"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, held_leak
            )

    def test_release_lane_and_artifacts_are_strictly_all_or_none(self):
        events, entities, sources, existing = self._events()
        self.assertEqual(
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, existing
            )["release_lane_overlap"],
            0,
        )
        full = [*copy.deepcopy(existing), *copy.deepcopy(events)]
        self.assertEqual(
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, full
            )["release_lane_overlap"],
            16,
        )
        self.assertEqual(
            lane.validate_wave8_french_religious_forces_funnel(
                _historical_funnel(), full
            )["release_lane_overlap"],
            16,
        )
        with self.assertRaisesRegex(ValueError, "release overlap is partial"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, full[:-1]
            )
        duplicated = copy.deepcopy(full)
        duplicated.append(copy.deepcopy(events[0]))
        with self.assertRaisesRegex(ValueError, "partial or duplicated"):
            lane.validate_wave8_french_religious_forces_integration_dispositions(
                self.hced_rows, self.iwbd_rows, duplicated
            )

        lane_entity_ids = {item["id"] for item in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES}
        lane_source_ids = {item["id"] for item in lane.WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES}
        release_entity_ids = {item["id"] for item in self.release_entities}
        release_source_ids = {item["id"] for item in self.release_sources}
        self.assertIn(lane_entity_ids & release_entity_ids, (set(), lane_entity_ids))
        self.assertIn(lane_source_ids & release_source_ids, (set(), lane_source_ids))
        self.assertLessEqual(lane_entity_ids, set(entities))
        self.assertLessEqual(lane_source_ids, set(sources))

    def test_installers_are_idempotent_copy_fixtures_and_reject_collisions(self):
        entities, sources, _ = self._installed()
        lane.install_wave8_french_religious_forces_entities(entities)
        lane.install_wave8_french_religious_forces_sources(sources)
        entity_fixture = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES[0]
        source_fixture = lane.WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES[0]
        self.assertEqual(entities[entity_fixture["id"]], entity_fixture)
        self.assertIsNot(entities[entity_fixture["id"]], entity_fixture)
        self.assertEqual(sources[source_fixture["id"]], source_fixture)
        self.assertIsNot(sources[source_fixture["id"]], source_fixture)
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_french_religious_forces_entities({
                entity_fixture["id"]: {"id": entity_fixture["id"], "name": "collision"}
            })
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_french_religious_forces_sources({
                source_fixture["id"]: {"id": source_fixture["id"], "title": "collision"}
            })

    def test_promoter_rejects_row_entity_and_existing_event_drift(self):
        entities, _, existing = self._installed()
        mutated_rows = copy.deepcopy(self.hced_rows)
        row = next(item for item in mutated_rows if item["candidate_id"] == "hced-Coutras1587-1")
        row["winner_raw"] = "French Catholics"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.promote_wave8_french_religious_forces_contracts(
                mutated_rows, entities, existing
            )
        missing = copy.deepcopy(entities)
        missing.pop("navarre_huguenot_army_coutras_1587")
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_french_religious_forces_contracts(
                self.hced_rows, missing, existing
            )
        duplicate = copy.deepcopy(existing)
        duplicate.append({"id": "future_coutras_duplicate", "name": "Battle of Coutras", "year": 1587})
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_french_religious_forces_contracts(
                self.hced_rows, entities, duplicate
            )

    def test_signature_counts_cohorts_and_metadata_are_deterministic(self):
        self.assertEqual(lane.wave8_french_religious_forces_audit_signature(), FINAL_AUDIT_SIGNATURE)
        self.assertEqual(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE, FINAL_AUDIT_SIGNATURE)
        counts = lane.wave8_french_religious_forces_counts()
        expected_counts = {
            "reviewed_hced_rows": 22,
            "promotion_contracts": 16,
            "holds": 5,
            "terminal_exclusions": 1,
            "newly_rated_events": 16,
            "new_entities": 32,
            "new_sources": 21,
            "point_quarantine_additions": 16,
            "country_quarantine_additions": 0,
            "outcome_overrides": 0,
            "cross_label_twins": 11,
            "iwbd_zero_overlap_candidates": 22,
        }
        for key, value in expected_counts.items():
            self.assertEqual(counts[key], value)
        self.assertEqual(
            lane.wave8_french_religious_forces_cohort_counts(),
            {
                "eighth_french_war_1587": 2,
                "fifth_french_war_1575": 1,
                "first_french_war_1562_1563": 5,
                "fourth_french_war_1572_1573": 1,
                "huguenot_rebellion_1621": 2,
                "huguenot_rebellion_1625": 1,
                "ninth_french_war_1589_1598": 3,
                "second_french_war_1567": 1,
                "third_french_war_1568_1570": 6,
            },
        )
        metadata = lane.wave8_french_religious_forces_metadata()
        self.assertEqual(metadata["counts"], counts)
        self.assertEqual(metadata["final_audit_signature"], FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            lane.wave8_french_religious_forces_row_dispositions(),
            dict(sorted(lane.WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS.items())),
        )


if __name__ == "__main__":
    unittest.main()
