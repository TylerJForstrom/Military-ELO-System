from __future__ import annotations

"""Backward-compatible facade for the modular release-promotion pipeline."""

# These imports were public module attributes in the former monolith. Keep
# them bound here so direct and wildcard imports retain the legacy namespace.
import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from .promotion.policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_LABEL_REJECTION_COUNTERS,
    HCED_PENDING_SPLIT_LABELS,
    IDENTITY_DENY_WINDOWS,
    IWBD_COALITION_SIDE_LABELS,
    IWBD_CURATED_EXCLUSIONS,
    IWBD_REJECTION_COUNTERS,
    IWD_COW_CODE_POLICIES,
    IWD_CURATED_PARENT_EXCLUSIONS,
    SEED_CODE_POLICIES,
    SEED_EVENT_INTERVAL_EXEMPTIONS,
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_CURATED_EXCLUSIONS,
    UCDP_GW_CODE_POLICIES,
    UCDP_REJECTION_COUNTERS,
    UCDP_WAR_TYPES,
    _cow_policy_seed_id,
    _ENGLAND_WINDOWS,
    _gw_policy_seed_id,
    _HABSBURG_WINDOWS,
    _label_policy_seed_id,
    _policy_seed_id,
)

from .promotion.common import (
    normalize_label,
    read_jsonl,
    _candidate_entity_id,
    _candidate_labels,
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _count_review_records,
    _cross_source_event_keys,
    _declared_rejections,
    _deduplicate,
    _domain,
    _entity_covers,
    _event_key,
    _EVENT_ORDINAL_WORDS,
    _infer_kind,
    _normalized_event_name,
    _normalized_labels,
    _participants,
    _resolve_code,
    _resolve_label_tiers,
    _scale,
    _seed_entity_labels,
    _slug,
    _strategic_participants,
    _validate_seed_event_intervals,
    _WAR_NUMERAL_TOKENS,
    _WAR_STOP_TOKENS,
    _war_tokens,
    _war_tokens_match,
    _write_json,
)

from .promotion.hced import (
    promote_hced_label_rows,
    resolve_hced_side_label,
    _hced_label_row_key,
)

from .promotion.iwd import (
    aggregate_iwd_parent_wars,
    _humanize_war_name,
    _overlaps_seed_war,
    _seed_war_token_spans,
)

from .promotion.iwbd import (
    promote_iwbd_battles,
    _iwbd_base_war,
    _IWBD_CANDIDATE_ID,
    _iwbd_dates,
    _iwbd_id_parts,
    _matches_hced_exact,
    _matches_hced_fuzzy,
)

from .promotion.ucdp import (
    promote_ucdp_termination_episodes,
    resolve_ucdp_party,
    _ucdp_int,
    _ucdp_label_variants,
    _UCDP_PARENTHETICAL,
    _ucdp_split,
)

from .promotion.orchestrator import (
    build_expanded_release,
)
