import unittest

from military_elo.ingest.stage_open_data import _iwd_value
from military_elo.release import _candidate_entity_id, _policy_seed_id


class ReleasePolicyTests(unittest.TestCase):
    def test_roman_and_byzantine_policies_never_share_an_entity(self) -> None:
        self.assertEqual(_policy_seed_id("it_roman_dominate", 390, 394), "roman_empire")
        self.assertEqual(_policy_seed_id("tr_east_roman_emp", 395, 400), "byzantine_empire")
        self.assertIsNone(_policy_seed_id("it_roman_dominate", 395, 395))

    def test_successor_outside_policy_does_not_inherit_rating(self) -> None:
        self.assertEqual(_policy_seed_id("ru_romanov_dyn_2", 1916, 1917), "russian_empire")
        self.assertIsNone(_policy_seed_id("ru_romanov_dyn_2", 1918, 1918))

    def test_temporally_split_candidates_get_different_ids(self) -> None:
        base = {
            "canonical_name_candidate": "Example Kingdom",
            "seshat_ids": ["xx_example_k"],
            "wikidata_ids": ["Q1"],
            "end_year": 100,
        }
        first = _candidate_entity_id({**base, "start_year": 1})
        second = _candidate_entity_id({**base, "start_year": 200, "end_year": 300})
        self.assertNotEqual(first, second)

    def test_iwd_missing_codes_are_not_parties(self) -> None:
        self.assertIsNone(_iwd_value("-9.0"))
        self.assertEqual(_iwd_value("365.0"), "365")


if __name__ == "__main__":
    unittest.main()
