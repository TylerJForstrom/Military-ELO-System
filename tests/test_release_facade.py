import hashlib
import inspect
import json
import re
import unittest
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from military_elo import release
from military_elo.promotion import common, hced, iwbd, iwd, orchestrator, policy, ucdp
from scripts import build_release


EXPECTED_EXPORTS = {
    policy: (
        "_HABSBURG_WINDOWS",
        "_ENGLAND_WINDOWS",
        "SEED_CODE_POLICIES",
        "IWD_COW_CODE_POLICIES",
        "HCED_LABEL_POLICIES",
        "HCED_FACTION_LABELS",
        "HCED_PENDING_SPLIT_LABELS",
        "IWBD_COALITION_SIDE_LABELS",
        "IDENTITY_DENY_WINDOWS",
        "HCED_CURATED_EXCLUSIONS",
        "IWBD_CURATED_EXCLUSIONS",
        "IWD_CURATED_PARENT_EXCLUSIONS",
        "HCED_LABEL_CURATED_EXCLUSIONS",
        "SEED_EVENT_INTERVAL_EXEMPTIONS",
        "UCDP_ACTOR_PARTY_POLICIES",
        "UCDP_WAR_TYPES",
        "HCED_LABEL_REJECTION_COUNTERS",
        "IWBD_REJECTION_COUNTERS",
        "UCDP_REJECTION_COUNTERS",
        "UCDP_GW_CODE_POLICIES",
        "UCDP_CURATED_EXCLUSIONS",
        "_cow_policy_seed_id",
        "_label_policy_seed_id",
        "_policy_seed_id",
        "_gw_policy_seed_id",
    ),
    common: (
        "_declared_rejections",
        "read_jsonl",
        "_write_json",
        "normalize_label",
        "_slug",
        "_EVENT_ORDINAL_WORDS",
        "_normalized_event_name",
        "_event_key",
        "_cross_source_event_keys",
        "_candidate_entity_id",
        "_infer_kind",
        "_normalized_labels",
        "_candidate_labels",
        "_seed_entity_labels",
        "_candidate_overlaps_entity",
        "_candidate_policy_seed",
        "_resolve_code",
        "_scale",
        "_domain",
        "_participants",
        "_strategic_participants",
        "_WAR_NUMERAL_TOKENS",
        "_WAR_STOP_TOKENS",
        "_war_tokens",
        "_war_tokens_match",
        "_entity_covers",
        "_validate_seed_event_intervals",
        "_resolve_label_tiers",
        "_count_review_records",
        "_deduplicate",
    ),
    hced: (
        "_hced_label_row_key",
        "resolve_hced_side_label",
        "promote_hced_label_rows",
    ),
    iwd: (
        "_seed_war_token_spans",
        "_overlaps_seed_war",
        "_humanize_war_name",
        "aggregate_iwd_parent_wars",
    ),
    iwbd: (
        "_IWBD_CANDIDATE_ID",
        "_iwbd_id_parts",
        "_iwbd_dates",
        "_iwbd_base_war",
        "_matches_hced_exact",
        "_matches_hced_fuzzy",
        "promote_iwbd_battles",
    ),
    ucdp: (
        "_UCDP_PARENTHETICAL",
        "_ucdp_label_variants",
        "resolve_ucdp_party",
        "_ucdp_split",
        "_ucdp_int",
        "promote_ucdp_termination_episodes",
    ),
    orchestrator: ("build_expanded_release",),
}

LEGACY_IMPORTED_EXPORTS = {
    "hashlib": hashlib,
    "json": json,
    "re": re,
    "unicodedata": unicodedata,
    "Counter": Counter,
    "date": date,
    "Path": Path,
    "Any": Any,
    "Iterable": Iterable,
}


class ReleaseFacadeTests(unittest.TestCase):
    def test_facade_reexports_every_moved_symbol_by_identity(self) -> None:
        for owner, names in EXPECTED_EXPORTS.items():
            for name in names:
                with self.subTest(module=owner.__name__, name=name):
                    self.assertIs(getattr(release, name), getattr(owner, name))

    def test_build_script_keeps_the_legacy_public_import(self) -> None:
        self.assertIs(build_release.build_expanded_release, release.build_expanded_release)

    def test_facade_keeps_legacy_imported_names(self) -> None:
        for name, value in LEGACY_IMPORTED_EXPORTS.items():
            with self.subTest(name=name):
                self.assertIs(getattr(release, name), value)

    def test_build_entry_point_signature_is_unchanged(self) -> None:
        self.assertEqual(
            list(inspect.signature(release.build_expanded_release).parameters),
            ["seed_dir", "review_root", "release_dir", "registry_path"],
        )


if __name__ == "__main__":
    unittest.main()
