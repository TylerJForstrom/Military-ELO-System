"""Deterministic orchestration for the expanded provisional release."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ..canonical import hced_point_geometry_validation_error
from .common import (
    _canonicalize_superseded_identity,
    _candidate_entity_id,
    _candidate_labels,
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _count_review_records,
    _cross_source_event_keys,
    _declared_rejections,
    _deduplicate,
    _entity_covers,
    _event_key,
    _infer_kind,
    _resolve_code,
    _resolve_label_tiers,
    _seed_entity_labels,
    _validate_seed_event_intervals,
    _war_tokens,
    _write_json,
    normalize_label,
    read_jsonl,
)
from .hced import (
    promote_hced_crosswalk_rows,
    promote_hced_label_rows,
    resolve_hced_side_label,
)
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
    HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_WAVE5_CANDIDATE_BINDINGS,
    HCED_WAVE5_COUNTRY_ASSERTIONS,
    HCED_WAVE5_POINT_ASSERTIONS,
    HCED_WAVE5_PROVENANCE_OBJECTS,
    HCED_EXPECTED_QUARANTINE_OVERLAP,
    HCED_EXPECTED_QUARANTINE_UNION,
    HCED_LOCATION_WARNING,
    HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    HCED_POINT_QUARANTINE_EVENT_SHA256,
    HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
    HCED_POINT_QUARANTINE_IDS,
    HCED_SOURCE_BLANK_COUNTRY_IDS,
    hced_candidate_id,
    parse_hced_point,
)
from .iwd import aggregate_iwd_parent_wars, _seed_war_token_spans
from .iwbd import promote_iwbd_battles
from .policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_LABEL_REJECTION_COUNTERS,
    HCED_PENDING_SPLIT_LABELS,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
    IWBD_CURATED_EXCLUSIONS,
    IWBD_REJECTION_COUNTERS,
    IWBD_REVIEWED_IDENTITY_BINDINGS,
    IWBD_REVIEWED_IDENTITY_COHORTS,
    IWD_COW_CODE_POLICIES,
    IWD_CURATED_PARENT_EXCLUSIONS,
    IWD_REVIEWED_PARENT_CONTRACTS,
    SEED_EVENT_INTERVAL_EXEMPTIONS,
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_CURATED_EXCLUSIONS,
    UCDP_REJECTION_COUNTERS,
    UCDP_WAR_TYPES,
    _cow_policy_seed_id,
)
from .ucdp import promote_ucdp_termination_episodes, resolve_ucdp_party
from .wave6_1500_1799 import (
    WAVE6_HCED_CONTRACT_IDS,
    WAVE6_HCED_NONPROMOTED_IDS,
    WAVE6_HCED_RESERVED_IDS,
    install_wave6_entities,
    install_wave6_sources,
    promote_wave6_hced_contracts,
    validate_wave6_queue_contracts,
    wave6_cohort_counts,
)
from .wave6_1500_1799_data import (
    WAVE6_ENTITIES,
    WAVE6_HCED_CONTRACTS,
    WAVE6_HCED_EXCLUSIONS,
    WAVE6_HCED_HOLDS,
    WAVE6_WIKIDATA_EXCLUSIONS,
)
from .wave6_pre1500 import (
    WAVE6_PRE1500_ENTITIES,
    WAVE6_PRE1500_CURATED_EXCLUSIONS,
    WAVE6_PRE1500_ENTITY_IDS,
    WAVE6_PRE1500_HOLD_REASONS,
    WAVE6_PRE1500_REGISTRY_SUPERSESSIONS,
    WAVE6_PRE1500_REUSED_ENTITY_IDS,
    WAVE6_PRE1500_SAFE_CANDIDATE_IDS,
    WAVE6_PRE1500_SOURCE_FAMILY_METADATA,
    WAVE6_PRE1500_SOURCES,
    annotate_and_validate_wave6_pre1500_events,
    resolve_wave6_pre1500_candidate_side_label,
    validate_wave6_pre1500_candidates,
)
from .wave6_1800_2021_holds import (
    WAVE6_HCED_CURATED_EXCLUSIONS,
    WAVE6_HCED_HELD_SOURCE_CONTRACTS,
    WAVE6_IWBD_CURATED_EXCLUSIONS,
    WAVE6_IWBD_HELD_SOURCE_CONTRACTS,
    WAVE6_IWD_CURATED_PARENT_EXCLUSIONS,
    WAVE6_IWD_HELD_PARENT_CONTRACTS,
)
from .wave6_1800_2021_policy import (
    WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
    WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
    WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS,
    WAVE6_IWD_REVIEWED_PARENT_CONTRACTS,
)
from .wave6_1800_2021_registry import (
    WAVE6_1800_2021_ENTITY_OVERRIDES,
    WAVE6_1800_2021_SOURCES,
)
from .wave7_central import (
    WAVE7_CENTRAL_HOLD_IDS,
    WAVE7_CENTRAL_PROMOTION_IDS,
    WAVE7_CENTRAL_RESERVED_IDS,
    install_wave7_central_entities,
    install_wave7_central_sources,
    promote_wave7_central_hced_contracts,
    validate_wave7_central_queue_contracts,
    wave7_central_cohort_counts,
)
from .wave7_central_data import (
    WAVE7_CENTRAL_ENTITIES,
    WAVE7_CENTRAL_HOLDS,
    WAVE7_CENTRAL_SOURCES,
)
from .wave7_central_pass2 import (
    WAVE7_CENTRAL_PASS2_HOLD_IDS,
    WAVE7_CENTRAL_PASS2_PUBLISHED_DUPLICATE_IDS,
    WAVE7_CENTRAL_PASS2_PROMOTION_IDS,
    WAVE7_CENTRAL_PASS2_RESERVED_IDS,
    install_wave7_central_pass2_entities,
    install_wave7_central_pass2_sources,
    promote_wave7_central_pass2_hced_contracts,
    validate_wave7_central_pass2_queue_contracts,
    wave7_central_pass2_cohort_counts,
    wave7_central_pass2_hold_counts,
)
from .wave7_central_pass2_data import (
    WAVE7_CENTRAL_PASS2_ENTITIES,
    WAVE7_CENTRAL_PASS2_HOLDS,
    WAVE7_CENTRAL_PASS2_SOURCES,
)
from .wave7_root import (
    WAVE7_ROOT_CONTRACT_IDS,
    WAVE7_ROOT_ENTITIES,
    WAVE7_ROOT_HOLD_IDS,
    WAVE7_ROOT_HOLDS,
    WAVE7_ROOT_OUTCOME_CORRECTION_IDS,
    WAVE7_ROOT_RESERVED_IDS,
    WAVE7_ROOT_SOURCES,
    install_wave7_root_entities,
    install_wave7_root_sources,
    promote_wave7_root_contracts,
    validate_wave7_root_candidates,
    wave7_root_cohort_counts,
)
from .wave7_global import (
    WAVE7_GLOBAL_HCED_CONTRACT_IDS,
    WAVE7_GLOBAL_HCED_HOLD_IDS,
    WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS,
    WAVE7_GLOBAL_RESERVED_IDS,
    install_wave7_global_entities,
    install_wave7_global_sources,
    migrate_wave7_global_orange_events,
    promote_wave7_global_hced_contracts,
    validate_wave7_global_queue_contracts,
    validate_wave7_global_supersession_candidates,
    wave7_global_cohort_counts,
)
from .wave7_global_data import (
    WAVE7_GLOBAL_ENTITIES,
    WAVE7_GLOBAL_HCED_HOLDS,
    WAVE7_GLOBAL_ORANGE_MIGRATIONS,
    WAVE7_GLOBAL_SOURCES,
    WAVE7_GLOBAL_SUPERSESSIONS,
)
from .wave7_west import (
    WAVE7_WEST_HCED_CONTRACT_IDS,
    WAVE7_WEST_HCED_RESERVED_IDS,
    WAVE7_WEST_PROTECTED_RATED_IDS,
    install_wave7_west_entities,
    install_wave7_west_sources,
    promote_wave7_west_hced_contracts,
    validate_wave7_west_queue_contracts,
    wave7_west_cohort_counts,
)
from .wave7_west_data import (
    WAVE7_WEST_ENTITIES,
    WAVE7_WEST_HCED_HOLDS,
    WAVE7_WEST_PROTECTED_RATED,
    WAVE7_WEST_SOURCES,
)
from .wave8_african_states import (
    WAVE8_AFRICAN_STATES_CONTRACT_IDS,
    WAVE8_AFRICAN_STATES_ENTITIES,
    WAVE8_AFRICAN_STATES_RESERVED_IDS,
    WAVE8_AFRICAN_STATES_SOURCES,
    install_wave8_african_states_entities,
    install_wave8_african_states_sources,
    promote_wave8_african_states_contracts,
    validate_wave8_african_states_queue_contracts,
    wave8_african_states_cohort_counts,
)
from .wave8_early_states import (
    WAVE8_EARLY_STATES_CONTRACT_IDS,
    WAVE8_EARLY_STATES_ENTITIES,
    WAVE8_EARLY_STATES_HOLD_IDS,
    WAVE8_EARLY_STATES_HOLDS,
    WAVE8_EARLY_STATES_RESERVED_IDS,
    WAVE8_EARLY_STATES_SOURCES,
    install_wave8_early_states_entities,
    install_wave8_early_states_sources,
    promote_wave8_early_states_contracts,
    validate_wave8_early_states_queue_contracts,
    wave8_early_states_cohort_counts,
)
from .wave8_canadian_resistance import (
    WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS,
    WAVE8_CANADIAN_RESISTANCE_ENTITIES,
    WAVE8_CANADIAN_RESISTANCE_HOLD_IDS,
    WAVE8_CANADIAN_RESISTANCE_HOLDS,
    WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS,
    WAVE8_CANADIAN_RESISTANCE_SOURCES,
    install_wave8_canadian_resistance_entities,
    install_wave8_canadian_resistance_sources,
    promote_wave8_canadian_resistance_contracts,
    validate_wave8_canadian_resistance_queue_contracts,
    wave8_canadian_resistance_counts,
)
from .wave8_judean_revolts import (
    WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS,
    WAVE8_JUDEAN_REVOLTS_ENTITIES,
    WAVE8_JUDEAN_REVOLTS_HOLD_IDS,
    WAVE8_JUDEAN_REVOLTS_HOLDS,
    WAVE8_JUDEAN_REVOLTS_RESERVED_IDS,
    WAVE8_JUDEAN_REVOLTS_SOURCES,
    install_wave8_judean_revolts_entities,
    install_wave8_judean_revolts_sources,
    promote_wave8_judean_revolts_contracts,
    validate_wave8_judean_revolts_queue_contracts,
    wave8_judean_revolts_counts,
)
from .wave8_new_zealand import (
    WAVE8_NEW_ZEALAND_CONTRACT_IDS,
    WAVE8_NEW_ZEALAND_ENTITIES,
    WAVE8_NEW_ZEALAND_HOLD_IDS,
    WAVE8_NEW_ZEALAND_HOLDS,
    WAVE8_NEW_ZEALAND_RESERVED_IDS,
    WAVE8_NEW_ZEALAND_SOURCES,
    install_wave8_new_zealand_entities,
    install_wave8_new_zealand_sources,
    promote_wave8_new_zealand_contracts,
    validate_wave8_new_zealand_queue_contracts,
    wave8_new_zealand_cohort_counts,
)
from .wave8_namibia_resistance import (
    WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS,
    WAVE8_NAMIBIA_RESISTANCE_ENTITIES,
    WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS,
    WAVE8_NAMIBIA_RESISTANCE_HOLDS,
    WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS,
    WAVE8_NAMIBIA_RESISTANCE_SOURCES,
    install_wave8_namibia_resistance_entities,
    install_wave8_namibia_resistance_sources,
    promote_wave8_namibia_resistance_contracts,
    validate_wave8_namibia_resistance_queue_contracts,
    wave8_namibia_resistance_cohort_counts,
)
from .wave8_north_america import (
    WAVE8_NORTH_AMERICA_CONTRACT_IDS,
    WAVE8_NORTH_AMERICA_ENTITIES,
    WAVE8_NORTH_AMERICA_HOLD_IDS,
    WAVE8_NORTH_AMERICA_HOLDS,
    WAVE8_NORTH_AMERICA_RESERVED_IDS,
    WAVE8_NORTH_AMERICA_SOURCES,
    install_wave8_north_america_entities,
    install_wave8_north_america_sources,
    promote_wave8_north_america_contracts,
    validate_wave8_north_america_queue_contracts,
    wave8_north_america_cohort_counts,
)
from .wave8_polish_audit import (
    WAVE8_POLISH_AUDIT_CONTRACT_IDS,
    WAVE8_POLISH_AUDIT_CORRECTION_COUNT,
    WAVE8_POLISH_AUDIT_ENTITIES,
    WAVE8_POLISH_AUDIT_HOLD_IDS,
    WAVE8_POLISH_AUDIT_HOLDS,
    WAVE8_POLISH_AUDIT_RESERVED_IDS,
    WAVE8_POLISH_AUDIT_SOURCES,
    apply_wave8_polish_audit_corrections,
    install_wave8_polish_audit_entities,
    install_wave8_polish_audit_sources,
    promote_wave8_polish_audit_contracts,
    validate_wave8_polish_audit_queue_contracts,
    wave8_polish_audit_counts,
)
from .wave8_xhosa import (
    WAVE8_XHOSA_CONTRACT_IDS,
    WAVE8_XHOSA_ENTITIES,
    WAVE8_XHOSA_HOLD_IDS,
    WAVE8_XHOSA_HOLDS,
    WAVE8_XHOSA_RESERVED_IDS,
    WAVE8_XHOSA_SOURCES,
    install_wave8_xhosa_entities,
    install_wave8_xhosa_sources,
    promote_wave8_xhosa_contracts,
    validate_wave8_xhosa_queue_contracts,
    wave8_xhosa_cohort_counts,
)
from .wave8_wales import (
    WAVE8_WALES_CONTRACT_IDS,
    WAVE8_WALES_ENTITIES,
    WAVE8_WALES_HOLD_IDS,
    WAVE8_WALES_HOLDS,
    WAVE8_WALES_RESERVED_IDS,
    WAVE8_WALES_SOURCES,
    install_wave8_wales_entities,
    install_wave8_wales_sources,
    promote_wave8_wales_contracts,
    validate_wave8_wales_queue_contracts,
    wave8_wales_cohort_counts,
    wave8_wales_counts,
)
from .wave8_cossack_rebellions import (
    WAVE8_COSSACK_CONTRACT_IDS,
    WAVE8_COSSACK_HOLD_IDS,
    WAVE8_COSSACK_REBELLIONS_ENTITIES,
    WAVE8_COSSACK_REBELLIONS_HOLDS,
    WAVE8_COSSACK_REBELLIONS_SOURCES,
    WAVE8_COSSACK_RESERVED_IDS,
    install_wave8_cossack_entities,
    install_wave8_cossack_sources,
    promote_wave8_cossack_events,
    validate_wave8_cossack_inventory,
    wave8_cossack_cohort_counts,
    wave8_cossack_counts,
)
from .wave8_fast17 import (
    WAVE8_FAST17_CONTRACT_IDS,
    WAVE8_FAST17_ENTITIES,
    WAVE8_FAST17_HOLD_IDS,
    WAVE8_FAST17_HOLDS,
    WAVE8_FAST17_IWBD_DUPLICATE_HOLDS,
    WAVE8_FAST17_RESERVED_IDS,
    WAVE8_FAST17_SOURCES,
    install_wave8_fast17_entities,
    install_wave8_fast17_sources,
    promote_wave8_fast17_contracts,
    validate_wave8_fast17_queue_contracts,
    wave8_fast17_cohort_counts,
    wave8_fast17_counts,
)
from .wave8_naples import (
    WAVE8_NAPLES_CONTRACT_IDS,
    WAVE8_NAPLES_ENTITIES,
    WAVE8_NAPLES_HOLD_IDS,
    WAVE8_NAPLES_HOLDS,
    WAVE8_NAPLES_RESERVED_IDS,
    WAVE8_NAPLES_SOURCES,
    install_wave8_naples_entities,
    install_wave8_naples_sources,
    promote_wave8_naples_contracts,
    validate_wave8_naples_queue_contracts,
    wave8_naples_cohort_counts,
    wave8_naples_counts,
)
from .wave8_somali_irish_sa import (
    WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS,
    WAVE8_SOMALI_IRISH_SA_ENTITIES,
    WAVE8_SOMALI_IRISH_SA_HOLD_IDS,
    WAVE8_SOMALI_IRISH_SA_HOLDS,
    WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES,
    WAVE8_SOMALI_IRISH_SA_RESERVED_IDS,
    WAVE8_SOMALI_IRISH_SA_SOURCES,
    install_wave8_somali_irish_sa_entities,
    install_wave8_somali_irish_sa_sources,
    promote_wave8_somali_irish_sa_contracts,
    validate_wave8_somali_irish_sa_queue_contracts,
    wave8_somali_irish_sa_cohort_counts,
    wave8_somali_irish_sa_counts,
)
from .wave8_argentine_independence import (
    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES,
    WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_HOLDS,
    WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_SOURCES,
    install_wave8_argentine_independence_entities,
    install_wave8_argentine_independence_sources,
    promote_wave8_argentine_independence_contracts,
    validate_wave8_argentine_independence_queue_contracts,
    wave8_argentine_independence_cohort_counts,
    wave8_argentine_independence_counts,
)
from .wave8_ecuador_independence import (
    WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_ENTITIES,
    WAVE8_ECUADOR_INDEPENDENCE_HOLD_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_HOLDS,
    WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_SOURCES,
    install_wave8_ecuador_independence_entities,
    install_wave8_ecuador_independence_sources,
    promote_wave8_ecuador_independence_contracts,
    validate_wave8_ecuador_independence_queue_contracts,
    wave8_ecuador_independence_cohort_counts,
    wave8_ecuador_independence_counts,
)
from .wave8_comanche import (
    WAVE8_COMANCHE_CONTRACT_IDS,
    WAVE8_COMANCHE_ENTITIES,
    WAVE8_COMANCHE_HOLD_IDS,
    WAVE8_COMANCHE_HOLDS,
    WAVE8_COMANCHE_RESERVED_IDS,
    WAVE8_COMANCHE_SOURCES,
    install_wave8_comanche_entities,
    install_wave8_comanche_sources,
    promote_wave8_comanche_contracts,
    validate_wave8_comanche_queue_contracts,
    wave8_comanche_cohort_counts,
    wave8_comanche_counts,
)
from .wave8_garibaldi import (
    WAVE8_GARIBALDI_CONTRACT_IDS,
    WAVE8_GARIBALDI_ENTITIES,
    WAVE8_GARIBALDI_HOLD_IDS,
    WAVE8_GARIBALDI_HOLDS,
    WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS,
    WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_GARIBALDI_OUTCOME_OVERRIDES,
    WAVE8_GARIBALDI_RESERVED_IDS,
    WAVE8_GARIBALDI_SOURCES,
    install_wave8_garibaldi_entities,
    install_wave8_garibaldi_sources,
    promote_wave8_garibaldi_contracts,
    validate_wave8_garibaldi_integration_dispositions,
    validate_wave8_garibaldi_queue_contracts,
    wave8_garibaldi_cohort_counts,
    wave8_garibaldi_counts,
)
from .wave8_algiers_cheyenne import (
    WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS,
    WAVE8_ALGIERS_CHEYENNE_ENTITIES,
    WAVE8_ALGIERS_CHEYENNE_HOLD_IDS,
    WAVE8_ALGIERS_CHEYENNE_HOLDS,
    WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS,
    WAVE8_ALGIERS_CHEYENNE_SOURCES,
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
    install_wave8_algiers_cheyenne_entities,
    install_wave8_algiers_cheyenne_sources,
    promote_wave8_algiers_cheyenne_contracts,
    validate_wave8_algiers_cheyenne_queue_contracts,
    wave8_algiers_cheyenne_cohort_counts,
    wave8_algiers_cheyenne_counts,
)
from .wave8_dagestan import (
    WAVE8_DAGESTAN_CONTRACT_IDS,
    WAVE8_DAGESTAN_ENTITIES,
    WAVE8_DAGESTAN_HOLD_IDS,
    WAVE8_DAGESTAN_HOLDS,
    WAVE8_DAGESTAN_OUTCOME_OVERRIDES,
    WAVE8_DAGESTAN_RESERVED_IDS,
    WAVE8_DAGESTAN_SOURCES,
    install_wave8_dagestan_entities,
    install_wave8_dagestan_sources,
    promote_wave8_dagestan_contracts,
    validate_wave8_dagestan_integration_dispositions,
    validate_wave8_dagestan_queue_contracts,
    wave8_dagestan_cohort_counts,
    wave8_dagestan_counts,
)
from .wave8_irish_history import (
    WAVE8_IRISH_HISTORY_CONTRACT_IDS,
    WAVE8_IRISH_HISTORY_ENTITIES,
    WAVE8_IRISH_HISTORY_HOLD_IDS,
    WAVE8_IRISH_HISTORY_HOLDS,
    WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS,
    WAVE8_IRISH_HISTORY_RESERVED_IDS,
    WAVE8_IRISH_HISTORY_SOURCES,
    WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS,
    install_wave8_irish_history_entities,
    install_wave8_irish_history_sources,
    promote_wave8_irish_history_contracts,
    validate_wave8_irish_history_integration_dispositions,
    validate_wave8_irish_history_queue_contracts,
    wave8_irish_history_cohort_counts,
    wave8_irish_history_counts,
)
from .wave8_muslim_forces import (
    WAVE8_MUSLIM_FORCES_CONTRACT_IDS,
    WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS,
    WAVE8_MUSLIM_FORCES_ENTITIES,
    WAVE8_MUSLIM_FORCES_HOLD_IDS,
    WAVE8_MUSLIM_FORCES_HOLDS,
    WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS,
    WAVE8_MUSLIM_FORCES_RESERVED_IDS,
    WAVE8_MUSLIM_FORCES_SOURCES,
    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS,
    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS,
    install_wave8_muslim_forces_entities,
    install_wave8_muslim_forces_sources,
    promote_wave8_muslim_forces_contracts,
    validate_wave8_muslim_forces_queue_contracts,
    wave8_muslim_forces_cohort_counts,
    wave8_muslim_forces_counts,
)
from .wave8_moros import (
    WAVE8_MOROS_CONTRACT_IDS,
    WAVE8_MOROS_ENTITIES,
    WAVE8_MOROS_HOLD_IDS,
    WAVE8_MOROS_HOLDS,
    WAVE8_MOROS_INTEGRATION_DISPOSITIONS,
    WAVE8_MOROS_OUTCOME_OVERRIDES,
    WAVE8_MOROS_RESERVED_IDS,
    WAVE8_MOROS_SOURCES,
    install_wave8_moros_entities,
    install_wave8_moros_sources,
    promote_wave8_moros_contracts,
    validate_wave8_moros_queue_contracts,
    wave8_moros_cohort_counts,
    wave8_moros_counts,
)
from .wave8_manchus import (
    WAVE8_MANCHUS_CONTRACT_IDS,
    WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS,
    WAVE8_MANCHUS_ENTITIES,
    WAVE8_MANCHUS_HOLD_IDS,
    WAVE8_MANCHUS_HOLDS,
    WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS,
    WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MANCHUS_OUTCOME_OVERRIDES,
    WAVE8_MANCHUS_RESERVED_IDS,
    WAVE8_MANCHUS_SOURCES,
    install_wave8_manchus_entities,
    install_wave8_manchus_sources,
    promote_wave8_manchus_contracts,
    validate_wave8_manchus_integration_dispositions,
    validate_wave8_manchus_queue_contracts,
    wave8_manchus_cohort_counts,
    wave8_manchus_counts,
)
from .wave8_peruvian_rebels import (
    WAVE8_PERUVIAN_REBELS_CONTRACT_IDS,
    WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_ENTITIES,
    WAVE8_PERUVIAN_REBELS_HOLD_IDS,
    WAVE8_PERUVIAN_REBELS_HOLDS,
    WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES,
    WAVE8_PERUVIAN_REBELS_RESERVED_IDS,
    WAVE8_PERUVIAN_REBELS_SOURCES,
    install_wave8_peruvian_rebels_entities,
    install_wave8_peruvian_rebels_sources,
    promote_wave8_peruvian_rebels_contracts,
    validate_wave8_peruvian_rebels_integration_dispositions,
    validate_wave8_peruvian_rebels_queue_contracts,
    wave8_peruvian_rebels_cohort_counts,
    wave8_peruvian_rebels_counts,
)
from .wave8_germany import (
    WAVE8_GERMANY_CONTRACT_IDS,
    WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS,
    WAVE8_GERMANY_ENTITIES,
    WAVE8_GERMANY_HOLD_IDS,
    WAVE8_GERMANY_HOLDS,
    WAVE8_GERMANY_INTEGRATION_DISPOSITIONS,
    WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_GERMANY_OUTCOME_OVERRIDES,
    WAVE8_GERMANY_RESERVED_IDS,
    WAVE8_GERMANY_SOURCES,
    WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
    WAVE8_GERMANY_TERMINAL_EXCLUSIONS,
    install_wave8_germany_entities,
    install_wave8_germany_sources,
    promote_wave8_germany_contracts,
    validate_wave8_germany_integration_dispositions,
    validate_wave8_germany_queue_contracts,
    wave8_germany_cohort_counts,
    wave8_germany_counts,
)
from .wave8_seljuks import (
    WAVE8_SELJUKS_CONTRACT_IDS,
    WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS,
    WAVE8_SELJUKS_ENTITIES,
    WAVE8_SELJUKS_HOLD_IDS,
    WAVE8_SELJUKS_HOLDS,
    WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS,
    WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SELJUKS_OUTCOME_OVERRIDES,
    WAVE8_SELJUKS_RESERVED_IDS,
    WAVE8_SELJUKS_SOURCES,
    WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS,
    install_wave8_seljuks_entities,
    install_wave8_seljuks_sources,
    promote_wave8_seljuks_contracts,
    validate_wave8_seljuks_integration_dispositions,
    validate_wave8_seljuks_queue_contracts,
    wave8_seljuks_cohort_counts,
    wave8_seljuks_counts,
)
from .wave8_danish_vikings import (
    WAVE8_DANISH_VIKINGS_CONTRACT_IDS,
    WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_ENTITIES,
    WAVE8_DANISH_VIKINGS_HOLD_IDS,
    WAVE8_DANISH_VIKINGS_HOLDS,
    WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES,
    WAVE8_DANISH_VIKINGS_RESERVED_IDS,
    WAVE8_DANISH_VIKINGS_SOURCES,
    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS,
    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS,
    install_wave8_danish_vikings_entities,
    install_wave8_danish_vikings_sources,
    promote_wave8_danish_vikings_contracts,
    validate_wave8_danish_vikings_integration_dispositions,
    validate_wave8_danish_vikings_queue_contracts,
    wave8_danish_vikings_cohort_counts,
    wave8_danish_vikings_counts,
)
from .wave8_epirus import (
    WAVE8_EPIRUS_CONTRACT_IDS,
    WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS,
    WAVE8_EPIRUS_ENTITIES,
    WAVE8_EPIRUS_EXCLUSIONS,
    WAVE8_EPIRUS_HOLD_IDS,
    WAVE8_EPIRUS_HOLDS,
    WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS,
    WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_EPIRUS_OUTCOME_OVERRIDES,
    WAVE8_EPIRUS_RESERVED_IDS,
    WAVE8_EPIRUS_SOURCES,
    install_wave8_epirus_entities,
    install_wave8_epirus_sources,
    promote_wave8_epirus_contracts,
    validate_wave8_epirus_integration_dispositions,
    validate_wave8_epirus_queue_contracts,
    wave8_epirus_cohort_counts,
    wave8_epirus_counts,
)
from .wave8_savoy import (
    WAVE8_SAVOY_CONTRACT_IDS,
    WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS,
    WAVE8_SAVOY_ENTITIES,
    WAVE8_SAVOY_EXCLUSION_IDS,
    WAVE8_SAVOY_EXCLUSIONS,
    WAVE8_SAVOY_HOLD_IDS,
    WAVE8_SAVOY_HOLDS,
    WAVE8_SAVOY_INTEGRATION_DISPOSITIONS,
    WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SAVOY_OUTCOME_OVERRIDES,
    WAVE8_SAVOY_RESERVED_IDS,
    WAVE8_SAVOY_SOURCES,
    install_wave8_savoy_entities,
    install_wave8_savoy_sources,
    promote_wave8_savoy_contracts,
    validate_wave8_savoy_integration_dispositions,
    validate_wave8_savoy_queue_contracts,
    wave8_savoy_cohort_counts,
    wave8_savoy_counts,
)
from .wave8_nez_perce import (
    WAVE8_NEZ_PERCE_CONTRACT_IDS,
    WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS,
    WAVE8_NEZ_PERCE_ENTITIES,
    WAVE8_NEZ_PERCE_HOLD_IDS,
    WAVE8_NEZ_PERCE_HOLDS,
    WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS,
    WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES,
    WAVE8_NEZ_PERCE_RESERVED_IDS,
    WAVE8_NEZ_PERCE_SOURCES,
    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS,
    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS,
    install_wave8_nez_perce_entities,
    install_wave8_nez_perce_sources,
    promote_wave8_nez_perce_contracts,
    validate_wave8_nez_perce_integration_dispositions,
    validate_wave8_nez_perce_queue_contracts,
    wave8_nez_perce_cohort_counts,
    wave8_nez_perce_counts,
)
from .wave8_dacia import (
    WAVE8_DACIA_CONTRACT_IDS,
    WAVE8_DACIA_CROSS_LANE_DISPOSITIONS,
    WAVE8_DACIA_ENTITIES,
    WAVE8_DACIA_HOLD_IDS,
    WAVE8_DACIA_HOLDS,
    WAVE8_DACIA_INTEGRATION_DISPOSITIONS,
    WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DACIA_OUTCOME_OVERRIDES,
    WAVE8_DACIA_RESERVED_IDS,
    WAVE8_DACIA_SOURCES,
    WAVE8_DACIA_TERMINAL_EXCLUSION_IDS,
    WAVE8_DACIA_TERMINAL_EXCLUSIONS,
    install_wave8_dacia_entities,
    install_wave8_dacia_sources,
    promote_wave8_dacia_contracts,
    validate_wave8_dacia_integration_dispositions,
    validate_wave8_dacia_queue_contracts,
    wave8_dacia_cohort_counts,
    wave8_dacia_counts,
)
from .wave8_cherokee import (
    WAVE8_CHEROKEE_CONTRACT_IDS,
    WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS,
    WAVE8_CHEROKEE_ENTITIES,
    WAVE8_CHEROKEE_EXCLUSION_IDS,
    WAVE8_CHEROKEE_EXCLUSIONS,
    WAVE8_CHEROKEE_HOLD_IDS,
    WAVE8_CHEROKEE_HOLDS,
    WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS,
    WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_CHEROKEE_OUTCOME_OVERRIDES,
    WAVE8_CHEROKEE_RESERVED_IDS,
    WAVE8_CHEROKEE_SOURCES,
    install_wave8_cherokee_entities,
    install_wave8_cherokee_sources,
    promote_wave8_cherokee_contracts,
    validate_wave8_cherokee_integration_dispositions,
    validate_wave8_cherokee_queue_contracts,
    wave8_cherokee_cohort_counts,
    wave8_cherokee_counts,
)
from .wave8_druze_rebels import (
    WAVE8_DRUZE_REBELS_CONTRACT_IDS,
    WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_ENTITIES,
    WAVE8_DRUZE_REBELS_HOLD_IDS,
    WAVE8_DRUZE_REBELS_HOLDS,
    WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES,
    WAVE8_DRUZE_REBELS_RESERVED_IDS,
    WAVE8_DRUZE_REBELS_SOURCES,
    install_wave8_druze_rebels_entities,
    install_wave8_druze_rebels_sources,
    promote_wave8_druze_rebels_contracts,
    validate_wave8_druze_rebels_integration_dispositions,
    validate_wave8_druze_rebels_queue_contracts,
    wave8_druze_rebels_cohort_counts,
    wave8_druze_rebels_counts,
)
from .wave8_insubrian_gauls import (
    WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
    WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_ENTITIES,
    WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_HOLD_IDS,
    WAVE8_INSUBRIAN_GAULS_HOLDS,
    WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES,
    WAVE8_INSUBRIAN_GAULS_RESERVED_IDS,
    WAVE8_INSUBRIAN_GAULS_SOURCES,
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
    install_wave8_insubrian_gauls_entities,
    install_wave8_insubrian_gauls_sources,
    promote_wave8_insubrian_gauls_contracts,
    validate_wave8_insubrian_gauls_integration_dispositions,
    validate_wave8_insubrian_gauls_queue_contracts,
    wave8_insubrian_gauls_cohort_counts,
    wave8_insubrian_gauls_counts,
)
from .wave8_kiowa import (
    WAVE8_KIOWA_CONTRACT_IDS,
    WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS,
    WAVE8_KIOWA_ENTITIES,
    WAVE8_KIOWA_HOLD_IDS,
    WAVE8_KIOWA_HOLDS,
    WAVE8_KIOWA_INTEGRATION_DISPOSITIONS,
    WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_KIOWA_OUTCOME_OVERRIDES,
    WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS,
    WAVE8_KIOWA_RESERVED_IDS,
    WAVE8_KIOWA_SOURCES,
    install_wave8_kiowa_entities,
    install_wave8_kiowa_sources,
    promote_wave8_kiowa_contracts,
    validate_wave8_kiowa_integration_dispositions,
    validate_wave8_kiowa_queue_contracts,
    wave8_kiowa_cohort_counts,
    wave8_kiowa_counts,
)
from .wave8_uzbekistan import (
    WAVE8_UZBEKISTAN_CONTRACT_IDS,
    WAVE8_UZBEKISTAN_ENTITIES,
    WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_UZBEKISTAN_HOLD_IDS,
    WAVE8_UZBEKISTAN_HOLDS,
    WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS,
    WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS,
    WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES,
    WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS,
    WAVE8_UZBEKISTAN_RESERVED_IDS,
    WAVE8_UZBEKISTAN_SOURCES,
    install_wave8_uzbekistan_entities,
    install_wave8_uzbekistan_sources,
    promote_wave8_uzbekistan_contracts,
    validate_wave8_uzbekistan_integration_dispositions,
    validate_wave8_uzbekistan_queue_contracts,
    wave8_uzbekistan_cohort_counts,
    wave8_uzbekistan_counts,
)
from .wave8_vietnam import (
    WAVE8_VIETNAM_CONTRACT_IDS,
    WAVE8_VIETNAM_ENTITIES,
    WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_HOLD_IDS,
    WAVE8_VIETNAM_HOLDS,
    WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS,
    WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_VIETNAM_OUTCOME_OVERRIDES,
    WAVE8_VIETNAM_RESERVED_IDS,
    WAVE8_VIETNAM_SOURCES,
    WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
    WAVE8_VIETNAM_TERMINAL_EXCLUSIONS,
    install_wave8_vietnam_entities,
    install_wave8_vietnam_sources,
    promote_wave8_vietnam_contracts,
    validate_wave8_vietnam_integration_dispositions,
    validate_wave8_vietnam_queue_contracts,
    wave8_vietnam_cohort_counts,
    wave8_vietnam_counts,
)
from .wave8_hussites import (
    WAVE8_HUSSITES_CONTRACT_IDS,
    WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS,
    WAVE8_HUSSITES_ENTITIES,
    WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_HUSSITES_HOLD_IDS,
    WAVE8_HUSSITES_HOLDS,
    WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS,
    WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_HUSSITES_OUTCOME_OVERRIDES,
    WAVE8_HUSSITES_RESERVED_IDS,
    WAVE8_HUSSITES_SOURCES,
    WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS,
    WAVE8_HUSSITES_TERMINAL_EXCLUSIONS,
    install_wave8_hussites_entities,
    install_wave8_hussites_sources,
    promote_wave8_hussites_contracts,
    validate_wave8_hussites_integration_dispositions,
    validate_wave8_hussites_queue_contracts,
    wave8_hussites_cohort_counts,
    wave8_hussites_counts,
)
from .wave8_livonian_order import (
    WAVE8_LIVONIAN_ORDER_CONTRACT_IDS,
    WAVE8_LIVONIAN_ORDER_ENTITIES,
    WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_HOLD_IDS,
    WAVE8_LIVONIAN_ORDER_HOLDS,
    WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES,
    WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS,
    WAVE8_LIVONIAN_ORDER_RESERVED_IDS,
    WAVE8_LIVONIAN_ORDER_SOURCES,
    WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSION_IDS,
    WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS,
    install_wave8_livonian_order_entities,
    install_wave8_livonian_order_sources,
    promote_wave8_livonian_order_contracts,
    validate_wave8_livonian_order_integration_dispositions,
    validate_wave8_livonian_order_queue_contracts,
    wave8_livonian_order_cohort_counts,
    wave8_livonian_order_counts,
)
from .wave8_satsuma import (
    WAVE8_SATSUMA_CONTRACT_IDS,
    WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
    WAVE8_SATSUMA_ENTITIES,
    WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_HOLD_IDS,
    WAVE8_SATSUMA_HOLDS,
    WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS,
    WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SATSUMA_OUTCOME_OVERRIDES,
    WAVE8_SATSUMA_RESERVED_IDS,
    WAVE8_SATSUMA_SOURCES,
    WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS,
    WAVE8_SATSUMA_TERMINAL_EXCLUSIONS,
    install_wave8_satsuma_entities,
    install_wave8_satsuma_sources,
    promote_wave8_satsuma_contracts,
    validate_wave8_satsuma_integration_dispositions,
    validate_wave8_satsuma_queue_contracts,
    wave8_satsuma_cohort_counts,
    wave8_satsuma_counts,
)
from .wave8_rajputs import (
    WAVE8_RAJPUTS_CONTRACT_IDS,
    WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS,
    WAVE8_RAJPUTS_ENTITIES,
    WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_HOLD_IDS,
    WAVE8_RAJPUTS_HOLDS,
    WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS,
    WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_RAJPUTS_OUTCOME_OVERRIDES,
    WAVE8_RAJPUTS_RESERVED_IDS,
    WAVE8_RAJPUTS_SOURCES,
    WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS,
    WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS,
    install_wave8_rajputs_entities,
    install_wave8_rajputs_sources,
    promote_wave8_rajputs_contracts,
    validate_wave8_rajputs_integration_dispositions,
    validate_wave8_rajputs_queue_contracts,
    wave8_rajputs_cohort_counts,
    wave8_rajputs_counts,
)
from .wave8_mamluk_egypt import (
    WAVE8_MAMLUK_EGYPT_CONTRACT_IDS,
    WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_ENTITIES,
    WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_HOLD_IDS,
    WAVE8_MAMLUK_EGYPT_HOLDS,
    WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES,
    WAVE8_MAMLUK_EGYPT_RESERVED_IDS,
    WAVE8_MAMLUK_EGYPT_SOURCES,
    WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS,
    install_wave8_mamluk_egypt_entities,
    install_wave8_mamluk_egypt_sources,
    promote_wave8_mamluk_egypt_contracts,
    validate_wave8_mamluk_egypt_integration_dispositions,
    validate_wave8_mamluk_egypt_queue_contracts,
    wave8_mamluk_egypt_cohort_counts,
    wave8_mamluk_egypt_counts,
)
from .wave8_rebel_barons import (
    WAVE8_REBEL_BARONS_CONTRACT_IDS,
    WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_ENTITIES,
    WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_REBEL_BARONS_HOLD_IDS,
    WAVE8_REBEL_BARONS_HOLDS,
    WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS,
    WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES,
    WAVE8_REBEL_BARONS_RESERVED_IDS,
    WAVE8_REBEL_BARONS_SOURCES,
    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS,
    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS,
    install_wave8_rebel_barons_entities,
    install_wave8_rebel_barons_sources,
    promote_wave8_rebel_barons_contracts,
    validate_wave8_rebel_barons_integration_dispositions,
    validate_wave8_rebel_barons_queue_contracts,
    wave8_rebel_barons_cohort_counts,
    wave8_rebel_barons_counts,
)
from .wave8_thebes import (
    WAVE8_THEBES_CONTRACT_IDS,
    WAVE8_THEBES_CROSS_LANE_DISPOSITIONS,
    WAVE8_THEBES_ENTITIES,
    WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_THEBES_HOLD_IDS,
    WAVE8_THEBES_HOLDS,
    WAVE8_THEBES_INTEGRATION_DISPOSITIONS,
    WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_THEBES_OUTCOME_OVERRIDES,
    WAVE8_THEBES_RESERVED_IDS,
    WAVE8_THEBES_SOURCES,
    WAVE8_THEBES_TERMINAL_EXCLUSION_IDS,
    WAVE8_THEBES_TERMINAL_EXCLUSIONS,
    install_wave8_thebes_entities,
    install_wave8_thebes_sources,
    promote_wave8_thebes_contracts,
    validate_wave8_thebes_integration_dispositions,
    validate_wave8_thebes_queue_contracts,
    wave8_thebes_cohort_counts,
    wave8_thebes_counts,
)
from .wave8_alemanni import (
    WAVE8_ALEMANNI_CONTRACT_IDS,
    WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS,
    WAVE8_ALEMANNI_ENTITIES,
    WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ALEMANNI_HOLD_IDS,
    WAVE8_ALEMANNI_HOLDS,
    WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS,
    WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ALEMANNI_OUTCOME_OVERRIDES,
    WAVE8_ALEMANNI_RESERVED_IDS,
    WAVE8_ALEMANNI_SOURCES,
    WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
    WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS,
    install_wave8_alemanni_entities,
    install_wave8_alemanni_sources,
    promote_wave8_alemanni_contracts,
    validate_wave8_alemanni_integration_dispositions,
    validate_wave8_alemanni_queue_contracts,
    wave8_alemanni_cohort_counts,
    wave8_alemanni_counts,
    wave8_alemanni_spelling_counts,
)
from .wave8_madagascar import (
    WAVE8_MADAGASCAR_CONTRACT_IDS,
    WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS,
    WAVE8_MADAGASCAR_ENTITIES,
    WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_HOLD_IDS,
    WAVE8_MADAGASCAR_HOLDS,
    WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS,
    WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_OUTCOME_OVERRIDES,
    WAVE8_MADAGASCAR_RESERVED_IDS,
    WAVE8_MADAGASCAR_SOURCES,
    WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS,
    WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS,
    install_wave8_madagascar_entities,
    install_wave8_madagascar_sources,
    promote_wave8_madagascar_contracts,
    validate_wave8_madagascar_integration_dispositions,
    validate_wave8_madagascar_queue_contracts,
    wave8_madagascar_cohort_counts,
    wave8_madagascar_counts,
)
from .wave8_kickapoo import (
    WAVE8_KICKAPOO_CONTRACT_IDS,
    WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS,
    WAVE8_KICKAPOO_ENTITIES,
    WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_KICKAPOO_HOLD_IDS,
    WAVE8_KICKAPOO_HOLDS,
    WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS,
    WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_KICKAPOO_OUTCOME_OVERRIDES,
    WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS,
    WAVE8_KICKAPOO_RESERVED_IDS,
    WAVE8_KICKAPOO_SOURCES,
    WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
    WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS,
    install_wave8_kickapoo_entities,
    install_wave8_kickapoo_sources,
    promote_wave8_kickapoo_contracts,
    validate_wave8_kickapoo_integration_dispositions,
    validate_wave8_kickapoo_queue_contracts,
    wave8_kickapoo_cohort_counts,
    wave8_kickapoo_counts,
)
from .wave8_lordship_isles import (
    WAVE8_LORDSHIP_ISLES_CONTRACT_IDS,
    WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_ENTITIES,
    WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_HOLD_IDS,
    WAVE8_LORDSHIP_ISLES_HOLDS,
    WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES,
    WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS,
    WAVE8_LORDSHIP_ISLES_RESERVED_IDS,
    WAVE8_LORDSHIP_ISLES_SOURCES,
    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS,
    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
    install_wave8_lordship_isles_entities,
    install_wave8_lordship_isles_sources,
    promote_wave8_lordship_isles_contracts,
    validate_wave8_lordship_isles_integration_dispositions,
    validate_wave8_lordship_isles_queue_contracts,
    wave8_lordship_isles_cohort_counts,
    wave8_lordship_isles_counts,
    wave8_lordship_isles_row_dispositions,
)
from .wave8_armenia import (
    WAVE8_ARMENIA_CONTRACT_IDS,
    WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS,
    WAVE8_ARMENIA_ENTITIES,
    WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ARMENIA_HOLD_IDS,
    WAVE8_ARMENIA_HOLDS,
    WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS,
    WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ARMENIA_OUTCOME_OVERRIDES,
    WAVE8_ARMENIA_RESERVED_IDS,
    WAVE8_ARMENIA_SOURCES,
    WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS,
    WAVE8_ARMENIA_TERMINAL_EXCLUSIONS,
    install_wave8_armenia_entities,
    install_wave8_armenia_sources,
    promote_wave8_armenia_contracts,
    validate_wave8_armenia_integration_dispositions,
    validate_wave8_armenia_queue_contracts,
    wave8_armenia_cohort_counts,
    wave8_armenia_counts,
)
from .wave8_comanches import (
    WAVE8_COMANCHES_CONTRACT_IDS,
    WAVE8_COMANCHES_ENTITIES,
    WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_COMANCHES_HOLD_IDS,
    WAVE8_COMANCHES_HOLDS,
    WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS,
    WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_COMANCHES_OUTCOME_OVERRIDES,
    WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS,
    WAVE8_COMANCHES_RESERVED_IDS,
    WAVE8_COMANCHES_SOURCES,
    WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
    WAVE8_COMANCHES_TERMINAL_EXCLUSIONS,
    install_wave8_comanches_entities,
    install_wave8_comanches_sources,
    promote_wave8_comanches_contracts,
    validate_wave8_comanches_integration_dispositions,
    validate_wave8_comanches_queue_contracts,
    wave8_comanches_cohort_counts,
    wave8_comanches_counts,
)
from .wave8_sikh_punjab import (
    WAVE8_SIKH_PUNJAB_CONTRACT_IDS,
    WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS,
    WAVE8_SIKH_PUNJAB_ENTITIES,
    WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_SIKH_PUNJAB_HOLD_IDS,
    WAVE8_SIKH_PUNJAB_HOLDS,
    WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS,
    WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES,
    WAVE8_SIKH_PUNJAB_RESERVED_IDS,
    WAVE8_SIKH_PUNJAB_SOURCES,
    WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS,
    WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS,
    install_wave8_sikh_punjab_entities,
    install_wave8_sikh_punjab_sources,
    promote_wave8_sikh_punjab_contracts,
    validate_wave8_sikh_punjab_integration_dispositions,
    validate_wave8_sikh_punjab_queue_contracts,
    wave8_sikh_punjab_cohort_counts,
    wave8_sikh_punjab_counts,
)
from .wave8_eritrea import (
    WAVE8_ERITREA_CONTRACT_IDS,
    WAVE8_ERITREA_ENTITIES,
    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREA_HOLD_IDS,
    WAVE8_ERITREA_HOLDS,
    WAVE8_ERITREA_INTEGRATION_DISPOSITIONS,
    WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_ERITREA_OUTCOME_OVERRIDES,
    WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
    WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
    WAVE8_ERITREA_RESERVED_IDS,
    WAVE8_ERITREA_SOURCES,
    WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS,
    WAVE8_ERITREA_TERMINAL_EXCLUSIONS,
    install_wave8_eritrea_entities,
    install_wave8_eritrea_sources,
    promote_wave8_eritrea_contracts,
    validate_wave8_eritrea_integration_dispositions,
    validate_wave8_eritrea_queue_contracts,
    wave8_eritrea_cohort_counts,
    wave8_eritrea_counts,
)
from .wave8_flanders import (
    WAVE8_FLANDERS_CONTRACT_IDS,
    WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS,
    WAVE8_FLANDERS_ENTITIES,
    WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_FLANDERS_HOLD_IDS,
    WAVE8_FLANDERS_HOLDS,
    WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS,
    WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_FLANDERS_OUTCOME_OVERRIDES,
    WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS,
    WAVE8_FLANDERS_RESERVED_IDS,
    WAVE8_FLANDERS_SOURCES,
    WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS,
    WAVE8_FLANDERS_TERMINAL_EXCLUSIONS,
    install_wave8_flanders_entities,
    install_wave8_flanders_sources,
    promote_wave8_flanders_contracts,
    validate_wave8_flanders_integration_dispositions,
    validate_wave8_flanders_queue_contracts,
    wave8_flanders_cohort_counts,
    wave8_flanders_counts,
)
from .wave8_france_bavaria import (
    WAVE8_FRANCE_BAVARIA_CONTRACT_IDS,
    WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_ENTITIES,
    WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT,
    WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_HOLD_IDS,
    WAVE8_FRANCE_BAVARIA_HOLDS,
    WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES,
    WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_RESERVED_IDS,
    WAVE8_FRANCE_BAVARIA_SOURCES,
    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS,
    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
    install_wave8_france_bavaria_entities,
    install_wave8_france_bavaria_sources,
    promote_wave8_france_bavaria_contracts,
    validate_wave8_france_bavaria_integration_dispositions,
    validate_wave8_france_bavaria_queue_contracts,
    wave8_france_bavaria_cohort_counts,
    wave8_france_bavaria_counts,
)
from .wave8_eritrean_rebels import (
    WAVE8_ERITREAN_REBELS_CONTRACT_IDS,
    WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_ENTITIES,
    WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_HOLD_IDS,
    WAVE8_ERITREAN_REBELS_HOLDS,
    WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES,
    WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS,
    WAVE8_ERITREAN_REBELS_RESERVED_IDS,
    WAVE8_ERITREAN_REBELS_SOURCES,
    WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS,
    WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS,
    install_wave8_eritrean_rebels_entities,
    install_wave8_eritrean_rebels_sources,
    promote_wave8_eritrean_rebels_contracts,
    validate_wave8_eritrean_rebels_integration_dispositions,
    validate_wave8_eritrean_rebels_queue_contracts,
    wave8_eritrean_rebels_cohort_counts,
    wave8_eritrean_rebels_counts,
)
from .wave8_inca_rebels import (
    WAVE8_INCA_REBELS_CONTRACT_IDS,
    WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS,
    WAVE8_INCA_REBELS_ENTITIES,
    WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_INCA_REBELS_HOLD_IDS,
    WAVE8_INCA_REBELS_HOLDS,
    WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_INCA_REBELS_OUTCOME_OVERRIDES,
    WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS,
    WAVE8_INCA_REBELS_RESERVED_IDS,
    WAVE8_INCA_REBELS_SOURCES,
    WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS,
    WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS,
    install_wave8_inca_rebels_entities,
    install_wave8_inca_rebels_sources,
    promote_wave8_inca_rebels_contracts,
    validate_wave8_inca_rebels_integration_dispositions,
    validate_wave8_inca_rebels_queue_contracts,
    wave8_inca_rebels_cohort_counts,
    wave8_inca_rebels_counts,
)
from .wave8_haitian_rebels import (
    WAVE8_HAITIAN_REBELS_CONTRACT_IDS,
    WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_ENTITIES,
    WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_HOLD_IDS,
    WAVE8_HAITIAN_REBELS_HOLDS,
    WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES,
    WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS,
    WAVE8_HAITIAN_REBELS_RESERVED_IDS,
    WAVE8_HAITIAN_REBELS_SOURCES,
    WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS,
    WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS,
    install_wave8_haitian_rebels_entities,
    install_wave8_haitian_rebels_sources,
    promote_wave8_haitian_rebels_contracts,
    validate_wave8_haitian_rebels_integration_dispositions,
    validate_wave8_haitian_rebels_queue_contracts,
    wave8_haitian_rebels_cohort_counts,
    wave8_haitian_rebels_counts,
)
from .wave8_kingdom_kandy import (
    WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
    WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_ENTITIES,
    WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_HOLD_IDS,
    WAVE8_KINGDOM_KANDY_HOLDS,
    WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES,
    WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS,
    WAVE8_KINGDOM_KANDY_RESERVED_IDS,
    WAVE8_KINGDOM_KANDY_SOURCES,
    WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS,
    WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS,
    install_wave8_kingdom_kandy_entities,
    install_wave8_kingdom_kandy_sources,
    promote_wave8_kingdom_kandy_contracts,
    validate_wave8_kingdom_kandy_integration_dispositions,
    validate_wave8_kingdom_kandy_queue_contracts,
    wave8_kingdom_kandy_cohort_counts,
    wave8_kingdom_kandy_counts,
)
from .wave8_hospitallers import (
    WAVE8_HOSPITALLERS_CONTRACT_IDS,
    WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS,
    WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT,
    WAVE8_HOSPITALLERS_ENTITIES,
    WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_HOSPITALLERS_HOLD_IDS,
    WAVE8_HOSPITALLERS_HOLDS,
    WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS,
    WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT,
    WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES,
    WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS,
    WAVE8_HOSPITALLERS_RESERVED_IDS,
    WAVE8_HOSPITALLERS_SOURCES,
    WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS,
    WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS,
    install_wave8_hospitallers_entities,
    install_wave8_hospitallers_sources,
    promote_wave8_hospitallers_contracts,
    validate_wave8_hospitallers_integration_dispositions,
    validate_wave8_hospitallers_queue_contracts,
    wave8_hospitallers_cohort_counts,
    wave8_hospitallers_counts,
)
from .wave8_murids import (
    WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_MURIDS_CONTRACT_IDS,
    WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS,
    WAVE8_MURIDS_ENTITIES,
    WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT,
    WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_MURIDS_HOLD_IDS,
    WAVE8_MURIDS_HOLDS,
    WAVE8_MURIDS_INTEGRATION_DISPOSITIONS,
    WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_MURIDS_OUTCOME_OVERRIDES,
    WAVE8_MURIDS_RESERVED_IDS,
    WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
    WAVE8_MURIDS_SOURCES,
    WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS,
    WAVE8_MURIDS_TERMINAL_EXCLUSIONS,
    install_wave8_murids_entities,
    install_wave8_murids_sources,
    promote_wave8_murids_contracts,
    validate_wave8_murids_integration_dispositions,
    validate_wave8_murids_queue_contracts,
    wave8_murids_cohort_counts,
    wave8_murids_counts,
    wave8_murids_metadata,
)
from .wave8_punjabi_sikhs import (
    WAVE8_PUNJABI_SIKHS_CONTRACT_IDS,
    WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS,
    WAVE8_PUNJABI_SIKHS_ENTITIES,
    WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_PUNJABI_SIKHS_HOLD_IDS,
    WAVE8_PUNJABI_SIKHS_HOLDS,
    WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS,
    WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES,
    WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS,
    WAVE8_PUNJABI_SIKHS_RESERVED_IDS,
    WAVE8_PUNJABI_SIKHS_SOURCES,
    WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS,
    WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS,
    install_wave8_punjabi_sikhs_entities,
    install_wave8_punjabi_sikhs_sources,
    promote_wave8_punjabi_sikhs_contracts,
    validate_wave8_punjabi_sikhs_integration_dispositions,
    validate_wave8_punjabi_sikhs_queue_contracts,
    wave8_punjabi_sikhs_cohort_counts,
    wave8_punjabi_sikhs_counts,
)
from .wave8_modoc import (
    WAVE8_MODOC_CONTRACT_IDS,
    WAVE8_MODOC_CROSS_EVENT_BOUNDARIES,
    WAVE8_MODOC_ENTITIES,
    WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_MODOC_HOLD_IDS,
    WAVE8_MODOC_HOLDS,
    WAVE8_MODOC_INTEGRATION_DISPOSITIONS,
    WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_MODOC_OUTCOME_OVERRIDES,
    WAVE8_MODOC_RESERVED_IDS,
    WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
    WAVE8_MODOC_SOURCES,
    WAVE8_MODOC_TERMINAL_EXCLUSION_IDS,
    WAVE8_MODOC_TERMINAL_EXCLUSIONS,
    install_wave8_modoc_entities,
    install_wave8_modoc_sources,
    promote_wave8_modoc_contracts,
    validate_wave8_modoc_integration_dispositions,
    validate_wave8_modoc_queue_contracts,
    wave8_modoc_cohort_counts,
    wave8_modoc_counts,
    wave8_modoc_metadata,
)
from .wave8_sauk import (
    WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_SAUK_CONTRACT_IDS,
    WAVE8_SAUK_CROSS_LANE_DISPOSITIONS,
    WAVE8_SAUK_ENTITIES,
    WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_SAUK_HOLD_IDS,
    WAVE8_SAUK_HOLDS,
    WAVE8_SAUK_INTEGRATION_DISPOSITIONS,
    WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SAUK_OUTCOME_OVERRIDES,
    WAVE8_SAUK_RESERVED_IDS,
    WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
    WAVE8_SAUK_SOURCES,
    WAVE8_SAUK_TERMINAL_EXCLUSION_IDS,
    WAVE8_SAUK_TERMINAL_EXCLUSIONS,
    install_wave8_sauk_entities,
    install_wave8_sauk_sources,
    promote_wave8_sauk_contracts,
    validate_wave8_sauk_integration_dispositions,
    validate_wave8_sauk_queue_contracts,
    wave8_sauk_cohort_counts,
    wave8_sauk_counts,
    wave8_sauk_metadata,
)
from .wave8_ute import (
    WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_UTE_ALTERNATE_LABEL_AUDIT,
    WAVE8_UTE_CONTRACT_IDS,
    WAVE8_UTE_CROSS_LANE_DISPOSITIONS,
    WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT,
    WAVE8_UTE_ENTITIES,
    WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_UTE_HOLD_IDS,
    WAVE8_UTE_HOLDS,
    WAVE8_UTE_INTEGRATION_DISPOSITIONS,
    WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_UTE_OPPOSITE_RESULT_AUDIT,
    WAVE8_UTE_OUTCOME_OVERRIDES,
    WAVE8_UTE_RELATED_HCED_DISPOSITIONS,
    WAVE8_UTE_RESERVED_IDS,
    WAVE8_UTE_SOURCES,
    WAVE8_UTE_TERMINAL_EXCLUSION_IDS,
    WAVE8_UTE_TERMINAL_EXCLUSIONS,
    install_wave8_ute_entities,
    install_wave8_ute_sources,
    promote_wave8_ute_contracts,
    validate_wave8_ute_integration_dispositions,
    validate_wave8_ute_queue_contracts,
    wave8_ute_cohort_counts,
    wave8_ute_counts,
)
from .wave8_yakima import (
    WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_YAKIMA_CONTRACT_IDS,
    WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS,
    WAVE8_YAKIMA_ENTITIES,
    WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_YAKIMA_HOLD_IDS,
    WAVE8_YAKIMA_HOLDS,
    WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS,
    WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_YAKIMA_OUTCOME_OVERRIDES,
    WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS,
    WAVE8_YAKIMA_RESERVED_IDS,
    WAVE8_YAKIMA_SOURCES,
    WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
    WAVE8_YAKIMA_TERMINAL_EXCLUSIONS,
    WAVE8_YAKIMA_WAR_CANDIDATE_IDS,
    install_wave8_yakima_entities,
    install_wave8_yakima_sources,
    promote_wave8_yakima_contracts,
    validate_wave8_yakima_integration_dispositions,
    validate_wave8_yakima_queue_contracts,
    wave8_yakima_cohort_counts,
    wave8_yakima_counts,
)
from .wave8_taliban_al_qaeda import (
    WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS,
    WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_ENTITIES,
    WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES,
    WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS,
    WAVE8_TALIBAN_AL_QAEDA_HOLDS,
    WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES,
    WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS,
    WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS,
    WAVE8_TALIBAN_AL_QAEDA_SOURCES,
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS,
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS,
    WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS,
    install_wave8_taliban_al_qaeda_entities,
    install_wave8_taliban_al_qaeda_sources,
    promote_wave8_taliban_al_qaeda_contracts,
    validate_wave8_taliban_al_qaeda_integration_dispositions,
    validate_wave8_taliban_al_qaeda_queue_contracts,
    wave8_taliban_al_qaeda_cohort_counts,
    wave8_taliban_al_qaeda_counts,
    wave8_taliban_al_qaeda_metadata,
)
from .wave8_french_religious_forces import (
    WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES,
    WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES,
    WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES,
    WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES,
    WAVE8_FRENCH_RELIGIOUS_FORCES_RESERVED_IDS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES,
    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS,
    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS,
    install_wave8_french_religious_forces_entities,
    install_wave8_french_religious_forces_sources,
    promote_wave8_french_religious_forces_contracts,
    validate_wave8_french_religious_forces_integration_dispositions,
    validate_wave8_french_religious_forces_queue_contracts,
    wave8_french_religious_forces_cohort_counts,
    wave8_french_religious_forces_counts,
    wave8_french_religious_forces_metadata,
)
from .wave8_chadian_rebels import (
    WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS,
    WAVE8_CHADIAN_REBELS_CONTRACT_IDS,
    WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES,
    WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS,
    WAVE8_CHADIAN_REBELS_ENTITIES,
    WAVE8_CHADIAN_REBELS_HOLD_IDS,
    WAVE8_CHADIAN_REBELS_HOLDS,
    WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES,
    WAVE8_CHADIAN_REBELS_RESERVED_IDS,
    WAVE8_CHADIAN_REBELS_SOURCES,
    WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSION_IDS,
    WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS,
    WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS,
    install_wave8_chadian_rebels_entities,
    install_wave8_chadian_rebels_sources,
    promote_wave8_chadian_rebels_contracts,
    validate_wave8_chadian_rebels_integration_dispositions,
    validate_wave8_chadian_rebels_queue_contracts,
    wave8_chadian_rebels_cohort_counts,
    wave8_chadian_rebels_counts,
    wave8_chadian_rebels_metadata,
)
from .wave8_saudi_rashidi_forces import (
    WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
    WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES,
    WAVE8_SAUDI_RASHIDI_ENTITIES,
    WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_HOLD_IDS,
    WAVE8_SAUDI_RASHIDI_HOLDS,
    WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT,
    WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES,
    WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT,
    WAVE8_SAUDI_RASHIDI_RESERVED_IDS,
    WAVE8_SAUDI_RASHIDI_SOURCES,
    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS,
    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS,
    install_wave8_saudi_rashidi_entities,
    install_wave8_saudi_rashidi_sources,
    promote_wave8_saudi_rashidi_contracts,
    validate_wave8_saudi_rashidi_integration_dispositions,
    validate_wave8_saudi_rashidi_queue_contracts,
    wave8_saudi_rashidi_cohort_counts,
    wave8_saudi_rashidi_counts,
)
from .wave8_yaqui import (
    WAVE8_YAQUI_CONTRACT_IDS,
    WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS,
    WAVE8_YAQUI_ENTITIES,
    WAVE8_YAQUI_EVENT_BOUNDARIES,
    WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_YAQUI_HOLD_IDS,
    WAVE8_YAQUI_HOLDS,
    WAVE8_YAQUI_INTEGRATION_DISPOSITIONS,
    WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_YAQUI_OUTCOME_OVERRIDES,
    WAVE8_YAQUI_RESERVED_IDS,
    WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
    WAVE8_YAQUI_SOURCES,
    WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS,
    WAVE8_YAQUI_TERMINAL_EXCLUSIONS,
    WAVE8_YAQUI_WAR_CANDIDATE_IDS,
    install_wave8_yaqui_entities,
    install_wave8_yaqui_sources,
    promote_wave8_yaqui_contracts,
    validate_wave8_yaqui_integration_dispositions,
    validate_wave8_yaqui_queue_contracts,
    wave8_yaqui_cohort_counts,
    wave8_yaqui_counts,
    wave8_yaqui_metadata,
)
from .wave8_egypt_forces import (
    WAVE8_EGYPT_FORCES_CONTRACT_IDS,
    WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT,
    WAVE8_EGYPT_FORCES_ENTITIES,
    WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT,
    WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE,
    WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS,
    WAVE8_EGYPT_FORCES_HOLD_IDS,
    WAVE8_EGYPT_FORCES_HOLDS,
    WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT,
    WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_EGYPT_FORCES_IWD_AUDIT,
    WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS,
    WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES,
    WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_EGYPT_FORCES_RESERVED_IDS,
    WAVE8_EGYPT_FORCES_SOURCES,
    WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS,
    WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS,
    install_wave8_egypt_forces_entities,
    install_wave8_egypt_forces_sources,
    promote_wave8_egypt_forces_contracts,
    validate_wave8_egypt_forces_identity_boundaries,
    validate_wave8_egypt_forces_integration_dispositions,
    validate_wave8_egypt_forces_queue_contracts,
    wave8_egypt_forces_audit_signature,
    wave8_egypt_forces_cohort_counts,
    wave8_egypt_forces_counts,
)
from .wave8_haiti_regimes import (
    WAVE8_HAITI_REGIMES_CONTRACT_IDS,
    WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_HAITI_REGIMES_ENTITIES,
    WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE,
    WAVE8_HAITI_REGIMES_FUNNEL_AUDIT,
    WAVE8_HAITI_REGIMES_HOLDS,
    WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS,
    WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_HAITI_REGIMES_RESERVED_IDS,
    WAVE8_HAITI_REGIMES_SOURCES,
    install_wave8_haiti_regimes_entities,
    install_wave8_haiti_regimes_sources,
    promote_wave8_haiti_regimes_contracts,
    validate_wave8_haiti_regimes_integration_dispositions,
    validate_wave8_haiti_regimes_queue_contracts,
    wave8_haiti_regimes_audit_signature,
    wave8_haiti_regimes_cohort_counts,
    wave8_haiti_regimes_counts,
)
from .wave8_zulu_forces import (
    WAVE8_ZULU_FORCES_CONTRACT_IDS,
    WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ZULU_FORCES_ENTITIES,
    WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE,
    WAVE8_ZULU_FORCES_FUNNEL_AUDIT,
    WAVE8_ZULU_FORCES_HOLDS,
    WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS,
    WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ZULU_FORCES_RESERVED_IDS,
    WAVE8_ZULU_FORCES_SOURCES,
    install_wave8_zulu_forces_entities,
    install_wave8_zulu_forces_sources,
    promote_wave8_zulu_forces_contracts,
    validate_wave8_zulu_forces_integration_dispositions,
    validate_wave8_zulu_forces_queue_contracts,
    wave8_zulu_forces_audit_signature,
    wave8_zulu_forces_cohort_counts,
    wave8_zulu_forces_counts,
)
from .wave8_montenegro_1796 import (
    WAVE8_MONTENEGRO_1796_CONTRACT_IDS,
    WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MONTENEGRO_1796_ENTITIES,
    WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE,
    WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT,
    WAVE8_MONTENEGRO_1796_HOLDS,
    WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS,
    WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MONTENEGRO_1796_RESERVED_IDS,
    WAVE8_MONTENEGRO_1796_SOURCES,
    install_wave8_montenegro_1796_entities,
    install_wave8_montenegro_1796_sources,
    promote_wave8_montenegro_1796_contracts,
    validate_wave8_montenegro_1796_integration_dispositions,
    validate_wave8_montenegro_1796_queue_contracts,
    wave8_montenegro_1796_audit_signature,
    wave8_montenegro_1796_cohort_counts,
    wave8_montenegro_1796_counts,
)
from .wave8_bohemia import (
    WAVE8_BOHEMIA_CONTRACT_IDS,
    WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_BOHEMIA_ENTITIES,
    WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE,
    WAVE8_BOHEMIA_FUNNEL_AUDIT,
    WAVE8_BOHEMIA_HOLDS,
    WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS,
    WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_BOHEMIA_RESERVED_IDS,
    WAVE8_BOHEMIA_SOURCES,
    install_wave8_bohemia_entities,
    install_wave8_bohemia_sources,
    promote_wave8_bohemia_contracts,
    validate_wave8_bohemia_integration_dispositions,
    validate_wave8_bohemia_queue_contracts,
    wave8_bohemia_audit_signature,
    wave8_bohemia_cohort_counts,
    wave8_bohemia_counts,
)
from .wave8_spanish_liberals import (
    WAVE8_SPANISH_LIBERALS_CONTRACT_IDS,
    WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SPANISH_LIBERALS_ENTITIES,
    WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE,
    WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT,
    WAVE8_SPANISH_LIBERALS_HOLDS,
    WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS,
    WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SPANISH_LIBERALS_RESERVED_IDS,
    WAVE8_SPANISH_LIBERALS_SOURCES,
    install_wave8_spanish_liberals_entities,
    install_wave8_spanish_liberals_sources,
    promote_wave8_spanish_liberals_contracts,
    validate_wave8_spanish_liberals_integration_dispositions,
    validate_wave8_spanish_liberals_queue_contracts,
    wave8_spanish_liberals_audit_signature,
    wave8_spanish_liberals_cohort_counts,
    wave8_spanish_liberals_counts,
)
from .wave8_achea import (
    WAVE8_ACHEA_CONTRACT_IDS,
    WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ACHEA_ENTITIES,
    WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE,
    WAVE8_ACHEA_FUNNEL_AUDIT,
    WAVE8_ACHEA_HOLDS,
    WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS,
    WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ACHEA_RESERVED_IDS,
    WAVE8_ACHEA_SOURCES,
    install_wave8_achea_entities,
    install_wave8_achea_sources,
    promote_wave8_achea_contracts,
    validate_wave8_achea_integration_dispositions,
    validate_wave8_achea_queue_contracts,
    wave8_achea_audit_signature,
    wave8_achea_cohort_counts,
    wave8_achea_counts,
)
from .wave8_oran import (
    WAVE8_ORAN_CONTRACT_IDS,
    WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_ORAN_FINAL_AUDIT_SIGNATURE,
    WAVE8_ORAN_FUNNEL_AUDIT,
    WAVE8_ORAN_HOLDS,
    WAVE8_ORAN_RESERVED_IDS,
    WAVE8_ORAN_SOURCES,
    install_wave8_oran_entities,
    install_wave8_oran_sources,
    promote_wave8_oran_contracts,
    validate_wave8_oran_integration_dispositions,
    validate_wave8_oran_queue_contracts,
    wave8_oran_audit_signature,
    wave8_oran_cohort_counts,
    wave8_oran_counts,
)
from .wave8_cheyenne_dog_soldiers import (
    WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES,
    WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE,
    WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT,
    WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS,
    WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES,
    WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS,
    install_wave8_cheyenne_dog_soldiers_entities,
    install_wave8_cheyenne_dog_soldiers_sources,
    promote_wave8_cheyenne_dog_soldiers_contracts,
    validate_wave8_cheyenne_dog_soldiers_integration_dispositions,
    validate_wave8_cheyenne_dog_soldiers_queue_contracts,
    wave8_cheyenne_dog_soldiers_audit_signature,
    wave8_cheyenne_dog_soldiers_cohort_counts,
    wave8_cheyenne_dog_soldiers_counts,
)
from .wave8_libya import (
    WAVE8_LIBYA_CONTRACT_IDS,
    WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_LIBYA_ENTITIES,
    WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE,
    WAVE8_LIBYA_FUNNEL_AUDIT,
    WAVE8_LIBYA_HOLDS,
    WAVE8_LIBYA_IWBD_DISPOSITIONS,
    WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS,
    WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_LIBYA_RESERVED_IDS,
    WAVE8_LIBYA_SOURCES,
    install_wave8_libya_entities,
    install_wave8_libya_sources,
    promote_wave8_libya_contracts,
    validate_wave8_libya_frozen_chadian_rebels,
    validate_wave8_libya_integration_dispositions,
    validate_wave8_libya_queue_contracts,
    wave8_libya_audit_signature,
    wave8_libya_cohort_counts,
    wave8_libya_counts,
    wave8_libya_metadata,
)
from .wave8_kievan_rus import (
    WAVE8_KIEVAN_RUS_CONTRACT_IDS,
    WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_KIEVAN_RUS_ENTITIES,
    WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE,
    WAVE8_KIEVAN_RUS_FUNNEL_AUDIT,
    WAVE8_KIEVAN_RUS_HOLDS,
    WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS,
    WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_KIEVAN_RUS_RESERVED_IDS,
    WAVE8_KIEVAN_RUS_SOURCES,
    install_wave8_kievan_rus_entities,
    install_wave8_kievan_rus_sources,
    promote_wave8_kievan_rus_contracts,
    validate_wave8_kievan_rus_integration_dispositions,
    validate_wave8_kievan_rus_queue_contracts,
    wave8_kievan_rus_audit_signature,
    wave8_kievan_rus_cohort_counts,
    wave8_kievan_rus_counts,
)
from .wave8_carnatic import (
    WAVE8_CARNATIC_CONTRACT_IDS,
    WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_CARNATIC_ENTITIES,
    WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE,
    WAVE8_CARNATIC_FUNNEL_AUDIT,
    WAVE8_CARNATIC_HOLDS,
    WAVE8_CARNATIC_LEGACY_IDS,
    WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS,
    WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS,
    WAVE8_CARNATIC_RESERVED_IDS,
    WAVE8_CARNATIC_SOURCES,
    install_wave8_carnatic_entities,
    install_wave8_carnatic_sources,
    promote_wave8_carnatic_contracts,
    validate_wave8_carnatic_integration_dispositions,
    validate_wave8_carnatic_queue_contracts,
    wave8_carnatic_audit_signature,
    wave8_carnatic_cohort_counts,
    wave8_carnatic_counts,
)
from .wave8_goguryeo import (
    WAVE8_GOGURYEO_CONTRACT_IDS,
    WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GOGURYEO_ENTITIES,
    WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE,
    WAVE8_GOGURYEO_FUNNEL_AUDIT,
    WAVE8_GOGURYEO_HOLDS,
    WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS,
    WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GOGURYEO_RESERVED_IDS,
    WAVE8_GOGURYEO_SOURCES,
    install_wave8_goguryeo_entities,
    install_wave8_goguryeo_sources,
    promote_wave8_goguryeo_contracts,
    validate_wave8_goguryeo_integration_dispositions,
    validate_wave8_goguryeo_queue_contracts,
    wave8_goguryeo_audit_signature,
    wave8_goguryeo_cohort_counts,
    wave8_goguryeo_counts,
)
from .wave8_fln import (
    WAVE8_FLN_CONTRACT_IDS,
    WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_FLN_ENTITIES,
    WAVE8_FLN_FINAL_AUDIT_SIGNATURE,
    WAVE8_FLN_FUNNEL_AUDIT,
    WAVE8_FLN_HOLDS,
    WAVE8_FLN_LOCATION_QUARANTINE_REASONS,
    WAVE8_FLN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_FLN_RESERVED_IDS,
    WAVE8_FLN_SOURCES,
    install_wave8_fln_entities,
    install_wave8_fln_sources,
    promote_wave8_fln_contracts,
    validate_wave8_fln_integration_dispositions,
    validate_wave8_fln_queue_contracts,
    wave8_fln_audit_signature,
    wave8_fln_cohort_counts,
    wave8_fln_counts,
)
from .wave8_sindh import (
    WAVE8_SINDH_CONTRACT_IDS,
    WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SINDH_ENTITIES,
    WAVE8_SINDH_FINAL_AUDIT_SIGNATURE,
    WAVE8_SINDH_FUNNEL_AUDIT,
    WAVE8_SINDH_HOLDS,
    WAVE8_SINDH_LOCATION_QUARANTINE_REASONS,
    WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SINDH_RESERVED_IDS,
    WAVE8_SINDH_SOURCES,
    install_wave8_sindh_entities,
    install_wave8_sindh_sources,
    promote_wave8_sindh_contracts,
    validate_wave8_sindh_integration_dispositions,
    validate_wave8_sindh_queue_contracts,
    wave8_sindh_audit_signature,
    wave8_sindh_cohort_counts,
    wave8_sindh_counts,
)
from .wave8_oman import (
    WAVE8_OMAN_CONTRACT_IDS,
    WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_OMAN_ENTITIES,
    WAVE8_OMAN_FINAL_AUDIT_SIGNATURE,
    WAVE8_OMAN_FUNNEL_AUDIT,
    WAVE8_OMAN_HOLDS,
    WAVE8_OMAN_LOCATION_QUARANTINE_REASONS,
    WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_OMAN_RESERVED_IDS,
    WAVE8_OMAN_SOURCES,
    install_wave8_oman_entities,
    install_wave8_oman_sources,
    promote_wave8_oman_contracts,
    validate_wave8_oman_integration_dispositions,
    validate_wave8_oman_queue_contracts,
    wave8_oman_audit_signature,
    wave8_oman_cohort_counts,
    wave8_oman_counts,
)
from .wave8_irish_civil_war import (
    WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS,
    WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_IRISH_CIVIL_WAR_ENTITIES,
    WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE,
    WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT,
    WAVE8_IRISH_CIVIL_WAR_HOLDS,
    WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS,
    WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS,
    WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS,
    WAVE8_IRISH_CIVIL_WAR_SOURCES,
    install_wave8_irish_civil_war_sources,
    promote_wave8_irish_civil_war_contracts,
    validate_wave8_irish_civil_war_integration_dispositions,
    validate_wave8_irish_civil_war_queue_contracts,
    wave8_irish_civil_war_audit_signature,
    wave8_irish_civil_war_cohort_counts,
    wave8_irish_civil_war_counts,
)
from .wave8_bannock_sheepeater import (
    WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS,
    WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_BANNOCK_SHEEPEATER_ENTITIES,
    WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE,
    WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT,
    WAVE8_BANNOCK_SHEEPEATER_HOLDS,
    WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS,
    WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS,
    WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS,
    WAVE8_BANNOCK_SHEEPEATER_SOURCES,
    install_wave8_bannock_sheepeater_entities,
    install_wave8_bannock_sheepeater_sources,
    promote_wave8_bannock_sheepeater_contracts,
    validate_wave8_bannock_sheepeater_integration_dispositions,
    validate_wave8_bannock_sheepeater_queue_contracts,
    wave8_bannock_sheepeater_audit_signature,
    wave8_bannock_sheepeater_cohort_counts,
    wave8_bannock_sheepeater_counts,
)
from .wave8_catholic_rebels import (
    WAVE8_CATHOLIC_REBELS_CONTRACT_IDS,
    WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_CATHOLIC_REBELS_ENTITIES,
    WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE,
    WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT,
    WAVE8_CATHOLIC_REBELS_HOLDS,
    WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS,
    WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_CATHOLIC_REBELS_RESERVED_IDS,
    WAVE8_CATHOLIC_REBELS_SOURCES,
    install_wave8_catholic_rebels_entities,
    install_wave8_catholic_rebels_sources,
    promote_wave8_catholic_rebels_contracts,
    validate_wave8_catholic_rebels_integration_dispositions,
    validate_wave8_catholic_rebels_queue_contracts,
    wave8_catholic_rebels_audit_signature,
    wave8_catholic_rebels_cohort_counts,
    wave8_catholic_rebels_counts,
)
from .wave8_macedon import (
    WAVE8_MACEDON_CONTRACT_IDS,
    WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MACEDON_ENTITIES,
    WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE,
    WAVE8_MACEDON_FUNNEL_AUDIT,
    WAVE8_MACEDON_HOLDS,
    WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS,
    WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MACEDON_RESERVED_IDS,
    WAVE8_MACEDON_SOURCES,
    install_wave8_macedon_entities,
    install_wave8_macedon_sources,
    promote_wave8_macedon_contracts,
    validate_wave8_macedon_integration_dispositions,
    validate_wave8_macedon_queue_contracts,
    wave8_macedon_audit_signature,
    wave8_macedon_cohort_counts,
    wave8_macedon_counts,
)
from .wave8_uzbeks import (
    WAVE8_UZBEKS_CONTRACT_IDS,
    WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_UZBEKS_ENTITIES,
    WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE,
    WAVE8_UZBEKS_FUNNEL_AUDIT,
    WAVE8_UZBEKS_HOLDS,
    WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS,
    WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_UZBEKS_RESERVED_IDS,
    WAVE8_UZBEKS_SOURCES,
    install_wave8_uzbeks_entities,
    install_wave8_uzbeks_sources,
    promote_wave8_uzbeks_contracts,
    validate_wave8_uzbeks_integration_dispositions,
    validate_wave8_uzbeks_queue_contracts,
    wave8_uzbeks_audit_signature,
    wave8_uzbeks_cohort_counts,
    wave8_uzbeks_counts,
)
from .wave8_etruria import (
    WAVE8_ETRURIA_CONTRACT_IDS,
    WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ETRURIA_ENTITIES,
    WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE,
    WAVE8_ETRURIA_FUNNEL_AUDIT,
    WAVE8_ETRURIA_HOLDS,
    WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS,
    WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ETRURIA_RESERVED_IDS,
    WAVE8_ETRURIA_SOURCES,
    install_wave8_etruria_entities,
    install_wave8_etruria_sources,
    promote_wave8_etruria_contracts,
    validate_wave8_etruria_integration_dispositions,
    validate_wave8_etruria_queue_contracts,
    wave8_etruria_audit_signature,
    wave8_etruria_cohort_counts,
    wave8_etruria_counts,
)
from .wave8_first_saudi import (
    WAVE8_FIRST_SAUDI_CONTRACT_IDS,
    WAVE8_FIRST_SAUDI_ENTITIES,
    WAVE8_FIRST_SAUDI_HOLD_IDS,
    WAVE8_FIRST_SAUDI_HOLDS,
    WAVE8_FIRST_SAUDI_RESERVED_IDS,
    WAVE8_FIRST_SAUDI_SOURCES,
    install_wave8_first_saudi_entities,
    install_wave8_first_saudi_sources,
    promote_wave8_first_saudi_contracts,
    validate_wave8_first_saudi_queue_contracts,
    wave8_first_saudi_counts,
)


EFFECTIVE_HCED_RESERVED_IDS = (
    WAVE6_HCED_RESERVED_IDS
    | WAVE7_ROOT_RESERVED_IDS
    | WAVE7_CENTRAL_RESERVED_IDS
    | (
        WAVE7_CENTRAL_PASS2_RESERVED_IDS
        - WAVE7_CENTRAL_PASS2_PUBLISHED_DUPLICATE_IDS
    )
    | (WAVE7_GLOBAL_RESERVED_IDS - WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS)
    | (WAVE7_WEST_HCED_RESERVED_IDS - WAVE7_WEST_PROTECTED_RATED_IDS)
    | WAVE8_AFRICAN_STATES_RESERVED_IDS
    | WAVE8_NEW_ZEALAND_RESERVED_IDS
    | WAVE8_NORTH_AMERICA_RESERVED_IDS
    | WAVE8_POLISH_AUDIT_RESERVED_IDS
    | WAVE8_XHOSA_RESERVED_IDS
    | WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS
    | WAVE8_FIRST_SAUDI_RESERVED_IDS
    | WAVE8_EARLY_STATES_RESERVED_IDS
    | WAVE8_JUDEAN_REVOLTS_RESERVED_IDS
    | WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS
    | WAVE8_WALES_RESERVED_IDS
    | WAVE8_COSSACK_RESERVED_IDS
    | WAVE8_FAST17_RESERVED_IDS
    | WAVE8_NAPLES_RESERVED_IDS
    | WAVE8_SOMALI_IRISH_SA_RESERVED_IDS
    | WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS
    | WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS
    | WAVE8_COMANCHE_RESERVED_IDS
    | WAVE8_GARIBALDI_RESERVED_IDS
    | WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS
    | WAVE8_DAGESTAN_RESERVED_IDS
    | WAVE8_IRISH_HISTORY_RESERVED_IDS
    | WAVE8_MUSLIM_FORCES_RESERVED_IDS
    | WAVE8_MOROS_RESERVED_IDS
    | WAVE8_MANCHUS_RESERVED_IDS
    | WAVE8_PERUVIAN_REBELS_RESERVED_IDS
    | WAVE8_GERMANY_RESERVED_IDS
    | WAVE8_SELJUKS_RESERVED_IDS
    | WAVE8_DANISH_VIKINGS_RESERVED_IDS
    | WAVE8_EPIRUS_RESERVED_IDS
    | WAVE8_SAVOY_RESERVED_IDS
    | WAVE8_NEZ_PERCE_RESERVED_IDS
    | WAVE8_DACIA_RESERVED_IDS
    | WAVE8_CHEROKEE_RESERVED_IDS
    | WAVE8_DRUZE_REBELS_RESERVED_IDS
    | WAVE8_INSUBRIAN_GAULS_RESERVED_IDS
    | WAVE8_KIOWA_RESERVED_IDS
    | WAVE8_UZBEKISTAN_RESERVED_IDS
    | WAVE8_VIETNAM_RESERVED_IDS
    | WAVE8_HUSSITES_RESERVED_IDS
    | WAVE8_LIVONIAN_ORDER_RESERVED_IDS
    | WAVE8_SATSUMA_RESERVED_IDS
    | WAVE8_RAJPUTS_RESERVED_IDS
    | WAVE8_MAMLUK_EGYPT_RESERVED_IDS
    | WAVE8_REBEL_BARONS_RESERVED_IDS
    | WAVE8_THEBES_RESERVED_IDS
    | WAVE8_ALEMANNI_RESERVED_IDS
    | WAVE8_MADAGASCAR_RESERVED_IDS
    | WAVE8_KICKAPOO_RESERVED_IDS
    | WAVE8_LORDSHIP_ISLES_RESERVED_IDS
    | WAVE8_ARMENIA_RESERVED_IDS
    | WAVE8_COMANCHES_RESERVED_IDS
    | WAVE8_SIKH_PUNJAB_RESERVED_IDS
    | WAVE8_ERITREA_RESERVED_IDS
    | WAVE8_FLANDERS_RESERVED_IDS
    | WAVE8_FRANCE_BAVARIA_RESERVED_IDS
    | WAVE8_ERITREAN_REBELS_RESERVED_IDS
    | WAVE8_INCA_REBELS_RESERVED_IDS
    | WAVE8_HAITIAN_REBELS_RESERVED_IDS
    | WAVE8_KINGDOM_KANDY_RESERVED_IDS
    | WAVE8_HOSPITALLERS_RESERVED_IDS
    | WAVE8_MURIDS_RESERVED_IDS
    | WAVE8_PUNJABI_SIKHS_RESERVED_IDS
    | WAVE8_MODOC_RESERVED_IDS
    | WAVE8_SAUK_RESERVED_IDS
    | WAVE8_UTE_RESERVED_IDS
    | WAVE8_YAKIMA_RESERVED_IDS
    | WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS
    | WAVE8_FRENCH_RELIGIOUS_FORCES_RESERVED_IDS
    | WAVE8_CHADIAN_REBELS_RESERVED_IDS
    | WAVE8_SAUDI_RASHIDI_RESERVED_IDS
    | WAVE8_YAQUI_RESERVED_IDS
    | WAVE8_EGYPT_FORCES_RESERVED_IDS
    | WAVE8_HAITI_REGIMES_RESERVED_IDS
    | WAVE8_ZULU_FORCES_RESERVED_IDS
    | WAVE8_MONTENEGRO_1796_RESERVED_IDS
    | WAVE8_BOHEMIA_RESERVED_IDS
    | WAVE8_SPANISH_LIBERALS_RESERVED_IDS
    | WAVE8_ACHEA_RESERVED_IDS
    | WAVE8_ORAN_RESERVED_IDS
    | WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS
    | WAVE8_LIBYA_RESERVED_IDS
    | WAVE8_KIEVAN_RUS_RESERVED_IDS
    | WAVE8_CARNATIC_RESERVED_IDS
    | WAVE8_GOGURYEO_RESERVED_IDS
    | WAVE8_FLN_RESERVED_IDS
    | WAVE8_SINDH_RESERVED_IDS
    | WAVE8_OMAN_RESERVED_IDS
    | WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS
    | WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS
    | WAVE8_CATHOLIC_REBELS_RESERVED_IDS
    | WAVE8_MACEDON_RESERVED_IDS
    | WAVE8_UZBEKS_RESERVED_IDS
    | WAVE8_ETRURIA_RESERVED_IDS
)
EFFECTIVE_HCED_CURATED_EXCLUSIONS = {
    **HCED_CURATED_EXCLUSIONS,
    **WAVE6_PRE1500_CURATED_EXCLUSIONS,
    **WAVE6_HCED_CURATED_EXCLUSIONS,
}
EFFECTIVE_IWD_CURATED_PARENT_EXCLUSIONS = {
    **IWD_CURATED_PARENT_EXCLUSIONS,
    **WAVE6_IWD_CURATED_PARENT_EXCLUSIONS,
}
EFFECTIVE_IWD_REVIEWED_PARENT_CONTRACTS = {
    **IWD_REVIEWED_PARENT_CONTRACTS,
    **WAVE6_IWD_REVIEWED_PARENT_CONTRACTS,
    **WAVE6_IWD_HELD_PARENT_CONTRACTS,
}
EFFECTIVE_IWBD_CURATED_EXCLUSIONS = {
    **WAVE6_IWBD_CURATED_EXCLUSIONS,
    **{
        candidate_id: str(contract["hold_reason"])
        for candidate_id, contract in WAVE8_FAST17_IWBD_DUPLICATE_HOLDS.items()
    },
    **{
        candidate_id: str(contract["reason"])
        for candidate_id, contract in (
            WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        candidate_id: str(contract["reason"])
        for candidate_id, contract in (
            WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        candidate_id: str(contract["reason"])
        for candidate_id, contract in (
            WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        candidate_id: (
            "duplicate of canonical HCED owner "
            f"{contract['owner_hced_candidate_id']}"
        )
        for candidate_id, contract in (
            WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    # Preserve the older candidate-specific adjudication when a Wave 6 audit
    # fingerprints the same row under a broader hold inventory.
    **IWBD_CURATED_EXCLUSIONS,
    # The later Chadian cross-source audit fingerprints the contradictory Erdi
    # pair and supplies the narrower reason for retaining the hold.
    **{
        candidate_id: str(contract["reason"])
        for candidate_id, contract in (
            WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
}
EFFECTIVE_IWBD_REVIEWED_IDENTITY_BINDINGS = {
    **IWBD_REVIEWED_IDENTITY_BINDINGS,
    **WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
}
EFFECTIVE_IWBD_REVIEWED_IDENTITY_COHORTS = {
    **IWBD_REVIEWED_IDENTITY_COHORTS,
    **WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS,
}
WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS = {
    **{
        candidate_id: contract["source_contract"]
        for candidate_id, contract in WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS.items()
    },
    **WAVE6_HCED_HELD_SOURCE_CONTRACTS,
}
WAVE6_IWBD_VALIDATED_SOURCE_CONTRACTS = {
    **{
        candidate_id: contract["source_contract"]
        for candidate_id, contract in WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS.items()
    },
    **WAVE6_IWBD_HELD_SOURCE_CONTRACTS,
}


def _sorted_newline_sha256(values: list[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(values))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _index_hced_candidates(
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        candidate_id = hced_candidate_id(candidate)
        if candidate_id in indexed:
            raise ValueError(
                f"Duplicate HCED candidate_id in authoritative queue: {candidate_id}"
            )
        indexed[candidate_id] = candidate
    return indexed


def _validate_hced_event_source_parity(
    event: dict[str, Any],
    candidate: dict[str, Any],
) -> None:
    """Require one event's published location values to equal its source row."""

    candidate_id = hced_candidate_id(candidate)
    event_id = event.get("id")
    if event.get("hced_candidate_id") != candidate_id:
        raise ValueError(
            f"HCED event {event_id} does not match its exact candidate binding"
        )
    source_ids = event.get("source_ids")
    if not isinstance(source_ids, list) or "hced_dataset" not in source_ids:
        raise ValueError(f"HCED event {event_id} must link hced_dataset")

    source_point = parse_hced_point(
        candidate.get("latitude"), candidate.get("longitude")
    )
    if source_point is None:
        raise ValueError(
            f"Rated HCED candidate {candidate_id} lacks a strict source Point"
        )
    expected_point = None if candidate_id in HCED_POINT_QUARANTINE_IDS else source_point
    if expected_point is None:
        if "geometry" in event:
            raise ValueError(
                f"HCED event {event_id} must withhold its quarantined Point"
            )
    elif event.get("geometry") != expected_point:
        raise ValueError(
            f"HCED event {event_id} Point differs from its exact source ordinates"
        )

    source_country = candidate.get("modern_location_country")
    if source_country is not None and not isinstance(source_country, str):
        raise TypeError(
            f"HCED candidate {candidate_id} modern_location_country must be text or null"
        )
    if (
        isinstance(source_country, str)
        and source_country.strip()
        and source_country != source_country.strip()
    ):
        raise ValueError(
            f"HCED candidate {candidate_id} country assertion has surrounding whitespace"
        )
    expected_country = (
        source_country
        if candidate_id not in HCED_COUNTRY_QUARANTINE_IDS
        and isinstance(source_country, str)
        and bool(source_country.strip())
        else None
    )
    if expected_country is None:
        if "modern_location_country" in event:
            raise ValueError(
                f"HCED event {event_id} must withhold its country assertion"
            )
    elif event.get("modern_location_country") != expected_country:
        raise ValueError(
            f"HCED event {event_id} jurisdiction label differs from its exact source text"
        )

    has_location = expected_point is not None or expected_country is not None
    if not has_location:
        if "location_provenance" in event:
            raise ValueError(
                f"HCED event {event_id} must omit provenance when all locations are withheld"
            )
        return
    source_record_id = candidate.get("source_record_id")
    if (
        not isinstance(source_record_id, str)
        or not source_record_id.strip()
        or source_record_id != source_record_id.strip()
    ):
        raise ValueError(
            f"HCED candidate {candidate_id} has an invalid source_record_id"
        )
    expected_provenance = {
        "source_id": "hced_dataset",
        "source_record_id": source_record_id,
        "assertion_status": "unreviewed_source_assertion",
        "coordinate_precision": "unknown",
    }
    if event.get("location_provenance") != expected_provenance:
        raise ValueError(
            f"HCED event {event_id} location provenance differs from its exact source row"
        )


def _validate_hced_location_release(
    hced_events: list[dict[str, Any]],
    hced_candidates_by_id: dict[str, dict[str, Any]],
    reviewed_candidate_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    """Fail closed unless the audited HCED location release is exact."""

    candidate_ids: list[str] = []
    point_event_ids: list[str] = []
    country_event_ids: list[str] = []
    provenance_keys: set[tuple[str, str]] = set()
    point_count = 0
    country_count = 0
    provenance_count = 0
    crosswalk_count = 0
    label_count = 0
    reviewed_event_candidate_ids: set[str] = set()

    for event in hced_events:
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("Every promoted HCED event must carry a stable event ID")
        crosswalk_count += int(event_id.startswith("hced_hced_"))
        label_count += int(event_id.startswith("hced_label_"))

        candidate_id = event.get("hced_candidate_id")
        if (
            not isinstance(candidate_id, str)
            or not candidate_id.strip()
            or candidate_id != candidate_id.strip()
        ):
            raise ValueError(
                "Every promoted HCED event must carry an exact candidate ID"
            )
        candidate_ids.append(candidate_id)
        if candidate_id in reviewed_candidate_ids:
            reviewed_event_candidate_ids.add(candidate_id)
            if not event_id.startswith(
                ("hced_wave6_", "hced_wave7_", "hced_wave8_")
            ):
                raise ValueError(
                    f"Reviewed HCED candidate {candidate_id} has a non-lane event ID"
                )
        candidate = hced_candidates_by_id.get(candidate_id)
        if candidate is None:
            raise ValueError(
                f"HCED event {event_id} has no exact authoritative candidate row"
            )
        _validate_hced_event_source_parity(event, candidate)
        source_ids = event.get("source_ids")
        if not isinstance(source_ids, list) or "hced_dataset" not in source_ids:
            raise ValueError(f"HCED event {event_id} must link the hced_dataset source")
        if "location_name" in event:
            raise ValueError(f"HCED event {event_id} must never publish location_name")

        has_point = "geometry" in event
        expected_point = candidate_id not in HCED_POINT_QUARANTINE_IDS
        if has_point != expected_point:
            raise ValueError(
                f"HCED event {event_id} violates the point quarantine manifest"
            )
        if has_point:
            geometry_error = hced_point_geometry_validation_error(event["geometry"])
            if geometry_error is not None:
                raise ValueError(f"HCED event {event_id}: {geometry_error}")
            point_count += 1
        if candidate_id in HCED_POINT_QUARANTINE_IDS:
            point_event_ids.append(event_id)

        has_country = "modern_location_country" in event
        expected_country = candidate_id not in (
            HCED_COUNTRY_QUARANTINE_IDS | HCED_SOURCE_BLANK_COUNTRY_IDS
        )
        if has_country != expected_country:
            raise ValueError(
                f"HCED event {event_id} violates the country quarantine manifest"
            )
        if has_country:
            country = event["modern_location_country"]
            if (
                not isinstance(country, str)
                or not country.strip()
                or country != country.strip()
            ):
                raise ValueError(
                    f"HCED event {event_id} has an invalid source-transcribed jurisdiction label"
                )
            country_count += 1
        if candidate_id in HCED_COUNTRY_QUARANTINE_IDS:
            country_event_ids.append(event_id)

        has_location = has_point or has_country
        has_provenance = "location_provenance" in event
        if has_provenance != has_location:
            raise ValueError(
                f"HCED event {event_id} must publish provenance exactly when a location survives"
            )
        if not has_provenance:
            continue
        provenance = event["location_provenance"]
        if not isinstance(provenance, dict) or set(provenance) != {
            "source_id",
            "source_record_id",
            "assertion_status",
            "coordinate_precision",
        }:
            raise ValueError(
                f"HCED event {event_id} has noncanonical location provenance"
            )
        source_record_id = provenance.get("source_record_id")
        if (
            provenance.get("source_id") != "hced_dataset"
            or not isinstance(source_record_id, str)
            or not source_record_id.strip()
            or source_record_id != source_record_id.strip()
            or provenance.get("assertion_status") != "unreviewed_source_assertion"
            or provenance.get("coordinate_precision") != "unknown"
        ):
            raise ValueError(
                f"HCED event {event_id} has invalid location provenance values"
            )
        provenance_key = ("hced_dataset", source_record_id)
        if provenance_key in provenance_keys:
            raise ValueError(
                "HCED publishable location provenance must be unique by source record"
            )
        provenance_keys.add(provenance_key)
        provenance_count += 1

    pre1500_candidate_ids = frozenset(WAVE6_PRE1500_SAFE_CANDIDATE_IDS)
    modern_candidate_ids = frozenset(WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS)
    lane_candidate_sets = {
        "pre1500": pre1500_candidate_ids,
        "candidate_keyed": reviewed_candidate_ids,
        "modern": modern_candidate_ids,
    }
    duplicate_lane_ids = {
        candidate_id
        for lane_name, lane_ids in lane_candidate_sets.items()
        for other_name, other_ids in lane_candidate_sets.items()
        if lane_name < other_name
        for candidate_id in lane_ids & other_ids
    }
    if duplicate_lane_ids:
        raise ValueError(
            "Candidate-keyed HCED lanes overlap by candidate ID: "
            f"{sorted(duplicate_lane_ids)}"
        )
    additional_candidate_ids = (
        reviewed_candidate_ids | pre1500_candidate_ids | modern_candidate_ids
    )

    if reviewed_event_candidate_ids != reviewed_candidate_ids:
        missing = sorted(reviewed_candidate_ids - reviewed_event_candidate_ids)
        unexpected = sorted(reviewed_event_candidate_ids - reviewed_candidate_ids)
        raise ValueError(
            "Reviewed HCED candidate/location bijection changed: "
            f"missing={missing}, unexpected={unexpected}"
        )
    promoted_candidate_ids = set(candidate_ids)
    for lane_name, lane_ids in lane_candidate_sets.items():
        if not lane_ids <= promoted_candidate_ids:
            raise ValueError(
                f"Wave 6 {lane_name} HCED location bindings are incomplete: "
                f"missing={sorted(lane_ids - promoted_candidate_ids)}"
            )
    expected_candidate_bindings = HCED_WAVE5_CANDIDATE_BINDINGS + len(
        additional_candidate_ids
    )
    if len(candidate_ids) != expected_candidate_bindings:
        raise ValueError(
            "HCED candidate binding count changed: "
            f"{len(candidate_ids)} != {expected_candidate_bindings}"
        )
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("Promoted HCED events must map one-to-one to candidate IDs")
    if (crosswalk_count, label_count, len(reviewed_event_candidate_ids)) != (
        1_827 + len(modern_candidate_ids),
        2_426 + len(pre1500_candidate_ids),
        len(reviewed_candidate_ids),
    ):
        raise ValueError(
            "HCED promotion tranche counts changed: "
            f"{crosswalk_count} crosswalk, {label_count} label, and "
            f"{len(reviewed_event_candidate_ids)} candidate-keyed reviewed"
        )
    extra_point_count = 0
    extra_country_count = 0
    extra_provenance_count = 0
    for candidate_id in additional_candidate_ids:
        candidate = hced_candidates_by_id.get(candidate_id)
        if candidate is None:
            raise ValueError(f"Reviewed HCED candidate is missing: {candidate_id}")
        has_point = (
            candidate_id not in HCED_POINT_QUARANTINE_IDS
            and parse_hced_point(candidate.get("latitude"), candidate.get("longitude"))
            is not None
        )
        country = candidate.get("modern_location_country")
        has_country = (
            candidate_id
            not in (HCED_COUNTRY_QUARANTINE_IDS | HCED_SOURCE_BLANK_COUNTRY_IDS)
            and isinstance(country, str)
            and bool(country.strip())
        )
        extra_point_count += int(has_point)
        extra_country_count += int(has_country)
        extra_provenance_count += int(has_point or has_country)
    if (point_count, country_count, provenance_count) != (
        HCED_WAVE5_POINT_ASSERTIONS + extra_point_count,
        HCED_WAVE5_COUNTRY_ASSERTIONS + extra_country_count,
        HCED_WAVE5_PROVENANCE_OBJECTS + extra_provenance_count,
    ):
        raise ValueError(
            "HCED location assertion counts changed: "
            f"{point_count} Points, {country_count} jurisdiction labels, "
            f"{provenance_count} provenance objects"
        )
    if _sorted_newline_sha256(point_event_ids) != HCED_POINT_QUARANTINE_EVENT_SHA256:
        raise ValueError("HCED point-quarantine event binding hash changed")
    if (
        _sorted_newline_sha256(country_event_ids)
        != HCED_COUNTRY_QUARANTINE_EVENT_SHA256
    ):
        raise ValueError("HCED country-quarantine event binding hash changed")
    if (
        len(HCED_POINT_QUARANTINE_IDS) != 357
        or len(HCED_COUNTRY_QUARANTINE_IDS) != 94
        or len(HCED_SOURCE_BLANK_COUNTRY_IDS) != 1
        or len(HCED_POINT_QUARANTINE_IDS & HCED_COUNTRY_QUARANTINE_IDS)
        != HCED_EXPECTED_QUARANTINE_OVERLAP
        or len(HCED_POINT_QUARANTINE_IDS | HCED_COUNTRY_QUARANTINE_IDS)
        != HCED_EXPECTED_QUARANTINE_UNION
        or _sorted_newline_sha256(list(HCED_POINT_QUARANTINE_IDS))
        != HCED_POINT_QUARANTINE_CANDIDATE_SHA256
        or _sorted_newline_sha256(list(HCED_COUNTRY_QUARANTINE_IDS))
        != HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256
    ):
        raise ValueError("HCED location quarantine policy constants changed")

    return {
        "hced_candidate_bindings": len(candidate_ids),
        "candidate_keyed_reviewed_contracts": len(reviewed_event_candidate_ids),
        "geojson_points": point_count,
        "modern_location_country_assertions": country_count,
        "location_provenance_objects": provenance_count,
        "point_fields_withheld_by_quarantine": len(HCED_POINT_QUARANTINE_IDS),
        "country_or_jurisdiction_fields_withheld_by_quarantine": len(
            HCED_COUNTRY_QUARANTINE_IDS
        ),
        "source_blank_country_fields": len(HCED_SOURCE_BLANK_COUNTRY_IDS),
        "point_country_quarantine_overlap": len(
            HCED_POINT_QUARANTINE_IDS & HCED_COUNTRY_QUARANTINE_IDS
        ),
        "unique_events_with_any_quarantined_field": len(
            HCED_POINT_QUARANTINE_IDS | HCED_COUNTRY_QUARANTINE_IDS
        ),
        "point_quarantine_candidate_manifest_sha256": (
            HCED_POINT_QUARANTINE_CANDIDATE_SHA256
        ),
        "country_quarantine_candidate_manifest_sha256": (
            HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256
        ),
        "quarantine_policy_sha256": HCED_LOCATION_QUARANTINE_POLICY_SHA256,
        "assertion_status": {
            "unreviewed_source_assertion": provenance_count,
        },
        "verified_location_assertions": {
            "availability": "not_available",
            "count": None,
            "reason": (
                "HCED location fields are source transcriptions pending review; "
                "the release has no reviewed-location provenance contract."
            ),
        },
    }


def build_expanded_release(
    seed_dir: str | Path,
    review_root: str | Path,
    release_dir: str | Path,
    registry_path: str | Path,
) -> dict[str, Any]:
    seed_root = Path(seed_dir)
    review = Path(review_root)
    release = Path(release_dir)
    seed_entities: list[dict[str, Any]] = json.loads(
        (seed_root / "entities.json").read_text(encoding="utf-8")
    )
    seed_events: list[dict[str, Any]] = json.loads(
        (seed_root / "events.json").read_text(encoding="utf-8")
    )
    sources: list[dict[str, Any]] = json.loads(
        (seed_root / "sources.json").read_text(encoding="utf-8")
    )
    seed_metadata: dict[str, Any] = json.loads(
        (seed_root / "metadata.json").read_text(encoding="utf-8")
    )
    seed_entity_ids = {str(entity["id"]) for entity in seed_entities}
    wave6_entity_ids = {str(entity["id"]) for entity in WAVE6_PRE1500_ENTITIES}
    entity_id_collisions = sorted(seed_entity_ids & wave6_entity_ids)
    if entity_id_collisions:
        raise ValueError(
            f"Wave 6 pre-1500 entity IDs collide with the seed: {entity_id_collisions}"
        )
    seed_entities.extend(dict(entity) for entity in WAVE6_PRE1500_ENTITIES)

    seed_source_ids = {str(source["id"]) for source in sources}
    wave6_sources = [
        *WAVE6_PRE1500_SOURCES,
        *WAVE6_1800_2021_SOURCES,
    ]
    wave6_source_ids = {str(source["id"]) for source in wave6_sources}
    if len(wave6_source_ids) != len(wave6_sources):
        raise ValueError("Wave 6 source IDs are not unique across lanes")
    if any(
        not str(source.get("source_family_id") or "").strip()
        or not source.get("evidence_roles")
        for source in wave6_sources
    ):
        raise ValueError(
            "Wave 6 sources require explicit family and evidence-role metadata"
        )
    source_id_collisions = sorted(seed_source_ids & wave6_source_ids)
    if source_id_collisions:
        raise ValueError(
            f"Wave 6 source IDs collide with the seed: {source_id_collisions}"
        )
    sources.extend(dict(source) for source in wave6_sources)

    seed_by_id = {str(entity["id"]): entity for entity in seed_entities}
    _validate_seed_event_intervals(seed_events, seed_by_id)
    seed_label_index: dict[str, set[str]] = {}
    for entity in seed_entities:
        for label in [entity.get("name"), *entity.get("aliases", [])]:
            normalized = normalize_label(label)
            if normalized:
                seed_label_index.setdefault(normalized, set()).add(str(entity["id"]))

    cliopatria = read_jsonl(review / "cliopatria-entity-candidates.jsonl")
    polities = [row for row in cliopatria if row.get("record_type") == "POLITY"]
    hced = read_jsonl(review / "hced-candidates.jsonl")
    validate_wave6_pre1500_candidates(hced)
    wave7_root_queue_validation = validate_wave7_root_candidates(hced)
    wave7_central_queue_validation = validate_wave7_central_queue_contracts(hced)
    wave7_central_pass2_queue_validation = validate_wave7_central_pass2_queue_contracts(
        hced
    )
    wave7_global_queue_validation = validate_wave7_global_queue_contracts(hced)
    wave7_west_queue_validation = validate_wave7_west_queue_contracts(hced)
    wave8_african_states_queue_validation = (
        validate_wave8_african_states_queue_contracts(hced)
    )
    wave8_new_zealand_queue_validation = validate_wave8_new_zealand_queue_contracts(
        hced
    )
    wave8_north_america_queue_validation = (
        validate_wave8_north_america_queue_contracts(hced)
    )
    wave8_polish_audit_queue_validation = (
        validate_wave8_polish_audit_queue_contracts(hced)
    )
    wave8_xhosa_queue_validation = validate_wave8_xhosa_queue_contracts(hced)
    wave8_namibia_resistance_queue_validation = (
        validate_wave8_namibia_resistance_queue_contracts(hced)
    )
    wave8_first_saudi_queue_validation = validate_wave8_first_saudi_queue_contracts(
        hced
    )
    wave8_early_states_queue_validation = validate_wave8_early_states_queue_contracts(
        hced
    )
    wave8_judean_revolts_queue_validation = (
        validate_wave8_judean_revolts_queue_contracts(hced)
    )
    wave8_canadian_resistance_queue_validation = (
        validate_wave8_canadian_resistance_queue_contracts(hced)
    )
    wave8_wales_queue_validation = validate_wave8_wales_queue_contracts(hced)
    wave8_cossack_queue_validation = validate_wave8_cossack_inventory(hced)
    wave8_fast17_queue_validation = validate_wave8_fast17_queue_contracts(hced)
    wave8_naples_queue_validation = validate_wave8_naples_queue_contracts(hced)
    wave8_somali_irish_sa_queue_validation = (
        validate_wave8_somali_irish_sa_queue_contracts(hced)
    )
    wave8_argentine_independence_queue_validation = (
        validate_wave8_argentine_independence_queue_contracts(hced)
    )
    wave8_ecuador_independence_queue_validation = (
        validate_wave8_ecuador_independence_queue_contracts(hced)
    )
    wave8_comanche_queue_validation = validate_wave8_comanche_queue_contracts(hced)
    wave8_garibaldi_queue_validation = validate_wave8_garibaldi_queue_contracts(hced)
    wave8_algiers_cheyenne_queue_validation = (
        validate_wave8_algiers_cheyenne_queue_contracts(hced)
    )
    wave8_dagestan_queue_validation = validate_wave8_dagestan_queue_contracts(hced)
    wave8_irish_history_queue_validation = (
        validate_wave8_irish_history_queue_contracts(hced)
    )
    wave8_muslim_forces_queue_validation = (
        validate_wave8_muslim_forces_queue_contracts(hced)
    )
    wave8_moros_queue_validation = validate_wave8_moros_queue_contracts(hced)
    wave8_manchus_queue_validation = validate_wave8_manchus_queue_contracts(hced)
    wave8_peruvian_rebels_queue_validation = (
        validate_wave8_peruvian_rebels_queue_contracts(hced)
    )
    wave8_germany_queue_validation = validate_wave8_germany_queue_contracts(hced)
    wave8_seljuks_queue_validation = validate_wave8_seljuks_queue_contracts(hced)
    wave8_danish_vikings_queue_validation = (
        validate_wave8_danish_vikings_queue_contracts(hced)
    )
    wave8_epirus_queue_validation = validate_wave8_epirus_queue_contracts(hced)
    wave8_savoy_queue_validation = validate_wave8_savoy_queue_contracts(hced)
    wave8_nez_perce_queue_validation = validate_wave8_nez_perce_queue_contracts(
        hced
    )
    wave8_dacia_queue_validation = validate_wave8_dacia_queue_contracts(hced)
    wave8_cherokee_queue_validation = validate_wave8_cherokee_queue_contracts(hced)
    wave8_druze_rebels_queue_validation = (
        validate_wave8_druze_rebels_queue_contracts(hced)
    )
    wave8_insubrian_gauls_queue_validation = (
        validate_wave8_insubrian_gauls_queue_contracts(hced)
    )
    wave8_kiowa_queue_validation = validate_wave8_kiowa_queue_contracts(hced)
    wave8_uzbekistan_queue_validation = validate_wave8_uzbekistan_queue_contracts(
        hced
    )
    wave8_vietnam_queue_validation = validate_wave8_vietnam_queue_contracts(hced)
    wave8_hussites_queue_validation = validate_wave8_hussites_queue_contracts(hced)
    wave8_livonian_order_queue_validation = (
        validate_wave8_livonian_order_queue_contracts(hced)
    )
    wave8_satsuma_queue_validation = validate_wave8_satsuma_queue_contracts(hced)
    wave8_rajputs_queue_validation = validate_wave8_rajputs_queue_contracts(hced)
    wave8_mamluk_egypt_queue_validation = (
        validate_wave8_mamluk_egypt_queue_contracts(hced)
    )
    wave8_rebel_barons_queue_validation = (
        validate_wave8_rebel_barons_queue_contracts(hced)
    )
    wave8_thebes_queue_validation = validate_wave8_thebes_queue_contracts(hced)
    wave8_alemanni_queue_validation = validate_wave8_alemanni_queue_contracts(hced)
    wave8_madagascar_queue_validation = (
        validate_wave8_madagascar_queue_contracts(hced)
    )
    wave8_kickapoo_queue_validation = validate_wave8_kickapoo_queue_contracts(hced)
    wave8_lordship_isles_queue_validation = (
        validate_wave8_lordship_isles_queue_contracts(hced)
    )
    wave8_armenia_queue_validation = validate_wave8_armenia_queue_contracts(hced)
    wave8_comanches_queue_validation = validate_wave8_comanches_queue_contracts(hced)
    wave8_sikh_punjab_queue_validation = (
        validate_wave8_sikh_punjab_queue_contracts(hced)
    )
    wave8_eritrea_queue_validation = validate_wave8_eritrea_queue_contracts(hced)
    wave8_flanders_queue_validation = validate_wave8_flanders_queue_contracts(hced)
    wave8_france_bavaria_queue_validation = (
        validate_wave8_france_bavaria_queue_contracts(hced)
    )
    wave8_eritrean_rebels_queue_validation = (
        validate_wave8_eritrean_rebels_queue_contracts(hced)
    )
    wave8_inca_rebels_queue_validation = validate_wave8_inca_rebels_queue_contracts(
        hced
    )
    wave8_haitian_rebels_queue_validation = (
        validate_wave8_haitian_rebels_queue_contracts(hced)
    )
    wave8_kingdom_kandy_queue_validation = (
        validate_wave8_kingdom_kandy_queue_contracts(hced)
    )
    wave8_hospitallers_queue_validation = (
        validate_wave8_hospitallers_queue_contracts(hced)
    )
    wave8_murids_queue_validation = validate_wave8_murids_queue_contracts(hced)
    wave8_punjabi_sikhs_queue_validation = (
        validate_wave8_punjabi_sikhs_queue_contracts(hced)
    )
    wave8_modoc_queue_validation = validate_wave8_modoc_queue_contracts(hced)
    wave8_sauk_queue_validation = validate_wave8_sauk_queue_contracts(hced)
    wave8_ute_queue_validation = validate_wave8_ute_queue_contracts(hced)
    wave8_yakima_queue_validation = validate_wave8_yakima_queue_contracts(hced)
    wave8_taliban_al_qaeda_queue_validation = (
        validate_wave8_taliban_al_qaeda_queue_contracts(hced)
    )
    wave8_french_religious_forces_queue_validation = (
        validate_wave8_french_religious_forces_queue_contracts(hced)
    )
    wave8_chadian_rebels_queue_validation = (
        validate_wave8_chadian_rebels_queue_contracts(hced)
    )
    wave8_saudi_rashidi_queue_validation = (
        validate_wave8_saudi_rashidi_queue_contracts(hced)
    )
    wave8_yaqui_queue_validation = validate_wave8_yaqui_queue_contracts(hced)
    wave8_egypt_forces_queue_validation = (
        validate_wave8_egypt_forces_queue_contracts(hced)
    )
    wave8_haiti_regimes_queue_validation = (
        validate_wave8_haiti_regimes_queue_contracts(hced)
    )
    wave8_zulu_forces_queue_validation = validate_wave8_zulu_forces_queue_contracts(
        hced
    )
    wave8_montenegro_1796_queue_validation = (
        validate_wave8_montenegro_1796_queue_contracts(hced)
    )
    wave8_bohemia_queue_validation = validate_wave8_bohemia_queue_contracts(hced)
    wave8_spanish_liberals_queue_validation = (
        validate_wave8_spanish_liberals_queue_contracts(hced)
    )
    wave8_achea_queue_validation = validate_wave8_achea_queue_contracts(hced)
    wave8_oran_queue_validation = validate_wave8_oran_queue_contracts(hced)
    wave8_cheyenne_dog_soldiers_queue_validation = (
        validate_wave8_cheyenne_dog_soldiers_queue_contracts(hced)
    )
    wave8_libya_frozen_chadian_rebels_pre_validation = (
        validate_wave8_libya_frozen_chadian_rebels()
    )
    wave8_libya_queue_validation = validate_wave8_libya_queue_contracts(hced)
    wave8_kievan_rus_queue_validation = validate_wave8_kievan_rus_queue_contracts(
        hced
    )
    wave8_carnatic_queue_validation = validate_wave8_carnatic_queue_contracts(hced)
    wave8_goguryeo_queue_validation = validate_wave8_goguryeo_queue_contracts(hced)
    wave8_fln_queue_validation = validate_wave8_fln_queue_contracts(hced)
    wave8_sindh_queue_validation = validate_wave8_sindh_queue_contracts(hced)
    wave8_oman_queue_validation = validate_wave8_oman_queue_contracts(hced)
    wave8_irish_civil_war_queue_validation = (
        validate_wave8_irish_civil_war_queue_contracts(hced)
    )
    wave8_bannock_sheepeater_queue_validation = (
        validate_wave8_bannock_sheepeater_queue_contracts(hced)
    )
    wave8_catholic_rebels_queue_validation = (
        validate_wave8_catholic_rebels_queue_contracts(hced)
    )
    wave8_macedon_queue_validation = validate_wave8_macedon_queue_contracts(hced)
    wave8_uzbeks_queue_validation = validate_wave8_uzbeks_queue_contracts(hced)
    wave8_etruria_queue_validation = validate_wave8_etruria_queue_contracts(hced)
    wave7_global_registry_supersessions = validate_wave7_global_supersession_candidates(
        cliopatria
    )
    hced_candidates_by_id = _index_hced_candidates(hced)
    wikidata_path = review / "wikidata-candidates.jsonl"
    wikidata_candidates = read_jsonl(wikidata_path) if wikidata_path.exists() else []
    wave6_queue_validation = validate_wave6_queue_contracts(
        hced,
        wikidata_candidates,
    )
    owners: dict[str, list[dict[str, Any]]] = {}
    for candidate in polities:
        for code in candidate.get("seshat_ids", []):
            owners.setdefault(str(code), []).append(candidate)

    release_entities = {str(entity["id"]): dict(entity) for entity in seed_entities}
    modern_override_ids = {
        str(entity["id"]) for entity in WAVE6_1800_2021_ENTITY_OVERRIDES
    }
    modern_entity_collisions = sorted(modern_override_ids & release_entities.keys())
    if modern_entity_collisions:
        raise ValueError(
            "Wave 6 modern entity overrides collide with existing identities: "
            f"{modern_entity_collisions}"
        )
    release_entities.update(
        {str(entity["id"]): dict(entity) for entity in WAVE6_1800_2021_ENTITY_OVERRIDES}
    )
    candidate_by_release_id: dict[str, dict[str, Any]] = {}
    iwd_events: list[dict[str, Any]] = []
    iwd_rejections: Counter[str] = Counter()
    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }

    def resolve_reviewed_identity(
        entity_id: str | None,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, None]:
        """Resolve one contract-pinned ID without opening a label fallback."""

        if entity_id is None:
            return None, None
        entity = release_entities.get(entity_id)
        if entity is None or not _entity_covers(entity, low_year, high_year):
            return None, None
        return entity_id, None

    def ensure_candidate_entity(polity: dict[str, Any]) -> str:
        entity_id = _candidate_entity_id(polity)
        candidate_by_release_id[entity_id] = polity
        if entity_id in release_entities:
            if entity_id in WAVE6_PRE1500_REUSED_ENTITY_IDS:
                # Wave 6 supplies a stronger curated boundary for two already
                # rated Cliopatria identities. Preserve the source-candidate
                # provenance and aliases while keeping the reviewed boundary;
                # replacing the payload outright would erase its lineage.
                entity = release_entities[entity_id]
                candidate_aliases = [
                    *map(str, polity.get("aliases", [])),
                    *map(str, polity.get("wikipedia_titles", [])),
                ]
                entity["aliases"] = list(
                    dict.fromkeys(
                        [
                            *map(str, entity.get("aliases", [])),
                            *(
                                alias
                                for alias in candidate_aliases
                                if normalize_label(alias)
                                != normalize_label(entity.get("name"))
                            ),
                        ]
                    )
                )
                entity["source_ids"] = list(
                    dict.fromkeys(
                        [*map(str, entity.get("source_ids", [])), "cliopatria_v020"]
                    )
                )
            return entity_id
        canonical_name = str(polity["canonical_name_candidate"])
        release_entities[entity_id] = {
            "id": entity_id,
            "name": canonical_name,
            "kind": _infer_kind(canonical_name),
            "start_year": int(polity["start_year"]),
            "end_year": int(polity["end_year"]),
            "region": "Unclassified",
            "aliases": _deduplicate(
                [
                    *map(str, polity.get("aliases", [])),
                    *map(str, polity.get("wikipedia_titles", [])),
                ]
            ),
            "predecessors": [],
            "continuity_note": (
                "Time-bounded Cliopatria interval. Namesakes, predecessors, and successors "
                "receive no inherited rating without an explicit continuity decision."
            ),
            "source_ids": ["cliopatria_v020"],
        }
        return entity_id

    hced_crosswalk_pass = promote_hced_crosswalk_rows(
        hced,
        owners,
        curated_seed_keys,
        ensure_candidate_entity,
        reviewed_identity_bindings=HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
        reviewed_candidate_contracts=WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
        validated_source_contracts=WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
        curated_exclusions=EFFECTIVE_HCED_CURATED_EXCLUSIONS,
        resolve_reviewed_id=resolve_reviewed_identity,
        require_complete_reviewed_identity_bindings=True,
        reserved_candidate_ids=EFFECTIVE_HCED_RESERVED_IDS,
    )
    source_events: list[dict[str, Any]] = hced_crosswalk_pass["events"]
    rejections: Counter[str] = hced_crosswalk_pass["rejections"]
    deferred_label_rows: list[dict[str, Any]] = hced_crosswalk_pass[
        "deferred_label_rows"
    ]
    promoted_hced_keys: set[tuple[str, int]] = hced_crosswalk_pass[
        "promoted_event_keys"
    ]
    label_observations: dict[str, list[tuple[int, int, str]]] = hced_crosswalk_pass[
        "label_observations"
    ]
    hced_cluster_spans: dict[str, list[Any]] = hced_crosswalk_pass["cluster_spans"]

    polity_alias_index: dict[str, list[dict[str, Any]]] = {}
    for polity in polities:
        labels = _deduplicate(
            [
                str(polity.get("canonical_name_candidate") or ""),
                *map(str, polity.get("aliases", [])),
                *map(str, polity.get("wikipedia_titles", [])),
            ]
        )
        for label in labels:
            normalized = normalize_label(label)
            if normalized:
                polity_alias_index.setdefault(normalized, []).append(polity)

    # Own-label sets per entity, used by the observation-coherence guard in the
    # HCED label pass (the IWD path keeps the tier unguarded so the committed
    # IWD promotion stays pinned).
    entity_labels: dict[str, set[str]] = {
        str(entity["id"]): _seed_entity_labels(entity) for entity in seed_entities
    }
    for polity in polities:
        entity_labels.setdefault(_candidate_entity_id(polity), set()).update(
            _candidate_labels(polity)
        )

    label_context: dict[str, Any] = {
        "seed_entities": seed_entities,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": label_observations,
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }

    # Composite members enter through the ordinary label resolver, but any
    # raw identity it returns must be canonicalized before coalition assembly.
    # Keep this inventory data-driven and wave-neutral: the pre-1500 and
    # fingerprint-validated Wave 7 supersessions are normalized to generated
    # source entity IDs, while eventual curated targets are made available for
    # interval checks without adding their aliases to the generic label index.
    composite_identity_supersessions: dict[str, tuple[str, ...]] = {
        str(source_id): (str(target_id),)
        for source_id, target_id in WAVE6_PRE1500_REGISTRY_SUPERSESSIONS.items()
    }
    for candidate_id, replacement_ids in wave7_global_registry_supersessions.items():
        contract = WAVE7_GLOBAL_SUPERSESSIONS[candidate_id]
        composite_identity_supersessions[str(contract["source_entity_id"])] = tuple(
            map(str, replacement_ids)
        )
    composite_supersession_targets = {
        **release_entities,
        **{
            str(entity["id"]): entity
            for entity in WAVE7_GLOBAL_ENTITIES
        },
    }

    def canonicalize_composite_identity(
        entity_id: str,
        polity: dict[str, Any] | None,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        return _canonicalize_superseded_identity(
            entity_id,
            polity,
            low_year,
            high_year,
            composite_identity_supersessions,
            composite_supersession_targets,
        )

    def resolve_iwd_label(
        label: str,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        entity_id, polity, _ = _resolve_label_tiers(
            normalize_label(label),
            low_year,
            high_year,
            label_context,
            require_observation_coherence=False,
        )
        return entity_id, polity

    def resolve_iwd_party(
        name: str,
        cow_code: Any,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        code = str(cow_code) if cow_code else ""
        if code in IWD_COW_CODE_POLICIES:
            # An explicit COW-code policy is authoritative: outside its
            # intervals the party stays unresolved instead of falling back to
            # name matching.
            return _cow_policy_seed_id(code, low_year, high_year), None
        return resolve_iwd_label(name, low_year, high_year)

    iwd_path = review / "iwd-1.21-candidates.jsonl"
    iwd_candidates = read_jsonl(iwd_path) if iwd_path.exists() else []
    # IWD component records repeat one umbrella war across many dyads, so they
    # are rated only through parent-war coalition aggregation: at most one
    # strategic update per largerwarid, with every component row retained as
    # provenance. Parents whose sides, outcomes, or identities cannot be
    # reconstructed defensibly stay staged.
    iwd_aggregation = aggregate_iwd_parent_wars(
        iwd_candidates,
        _seed_war_token_spans(seed_events),
        resolve_iwd_party,
        curated_parent_exclusions=EFFECTIVE_IWD_CURATED_PARENT_EXCLUSIONS,
        reviewed_parent_contracts=EFFECTIVE_IWD_REVIEWED_PARENT_CONTRACTS,
        resolve_reviewed_party=resolve_reviewed_identity,
        require_complete_reviewed_parents=True,
    )
    iwd_events.extend(iwd_aggregation["events"])
    iwd_rejections.update(iwd_aggregation["parent_rejections"])
    for polity in iwd_aggregation["resolved_polities"].values():
        ensure_candidate_entity(polity)

    # Second HCED pass: rows deferred for missing Seshat coding re-enter
    # through the declared label-resolution ruleset. It runs after IWD
    # aggregation so the IWD inputs are identical with or without the label
    # pass, and entities materialize only after every gate has passed.
    hced_label_pass = promote_hced_label_rows(
        deferred_label_rows,
        curated_seed_keys,
        promoted_hced_keys,
        lambda code, low_year, high_year: _resolve_code(
            code, low_year, high_year, owners
        ),
        lambda label, low_year, high_year: resolve_hced_side_label(
            label, low_year, high_year, label_context
        ),
        resolve_candidate_side_label=lambda candidate, label, low_year, high_year: (
            resolve_wave6_pre1500_candidate_side_label(
                candidate,
                label,
                low_year,
                high_year,
                label_context,
                lambda generic_label, generic_low, generic_high: (
                    resolve_hced_side_label(
                        generic_label,
                        generic_low,
                        generic_high,
                        label_context,
                    )
                ),
            )
        ),
        canonicalize_composite_identity=canonicalize_composite_identity,
    )
    label_events: list[dict[str, Any]] = hced_label_pass["events"]
    annotate_and_validate_wave6_pre1500_events(source_events, label_events)
    hced_label_rejections: Counter[str] = hced_label_pass["rejections"]
    for polity in hced_label_pass["resolved_polities"].values():
        ensure_candidate_entity(polity)
    for cluster_id, (tokens, low_year, high_year) in hced_label_pass[
        "cluster_spans"
    ].items():
        span = hced_cluster_spans.setdefault(cluster_id, [tokens, low_year, high_year])
        span[1] = min(span[1], low_year)
        span[2] = max(span[2], high_year)

    # Install candidate-keyed lane identities only after the generic HCED
    # label pass, so their names cannot become fallback mappings for unrelated
    # rows. Exact events then join one global HCED stream before IWBD dedup.
    install_wave6_entities(release_entities)
    wave6_events = promote_wave6_hced_contracts(
        hced,
        release_entities,
        [*seed_events, *source_events, *iwd_events, *label_events],
    )
    install_wave7_root_entities(release_entities)
    install_wave7_central_entities(release_entities)
    install_wave7_central_pass2_entities(release_entities)
    install_wave7_global_entities(release_entities)
    install_wave7_west_entities(release_entities)
    install_wave8_african_states_entities(release_entities)
    install_wave8_new_zealand_entities(release_entities)
    install_wave8_north_america_entities(release_entities)
    install_wave8_polish_audit_entities(release_entities)
    install_wave8_xhosa_entities(release_entities)
    install_wave8_namibia_resistance_entities(release_entities)
    install_wave8_first_saudi_entities(release_entities)
    install_wave8_early_states_entities(release_entities)
    install_wave8_judean_revolts_entities(release_entities)
    install_wave8_canadian_resistance_entities(release_entities)
    install_wave8_wales_entities(release_entities)
    install_wave8_cossack_entities(release_entities)
    install_wave8_fast17_entities(release_entities)
    install_wave8_naples_entities(release_entities)
    install_wave8_somali_irish_sa_entities(release_entities)
    install_wave8_argentine_independence_entities(release_entities)
    install_wave8_ecuador_independence_entities(release_entities)
    install_wave8_comanche_entities(release_entities)
    install_wave8_garibaldi_entities(release_entities)
    install_wave8_algiers_cheyenne_entities(release_entities)
    install_wave8_dagestan_entities(release_entities)
    install_wave8_irish_history_entities(release_entities)
    install_wave8_muslim_forces_entities(release_entities)
    install_wave8_moros_entities(release_entities)
    install_wave8_manchus_entities(release_entities)
    install_wave8_peruvian_rebels_entities(release_entities)
    install_wave8_germany_entities(release_entities)
    install_wave8_seljuks_entities(release_entities)
    install_wave8_danish_vikings_entities(release_entities)
    install_wave8_epirus_entities(release_entities)
    install_wave8_savoy_entities(release_entities)
    install_wave8_nez_perce_entities(release_entities)
    install_wave8_dacia_entities(release_entities)
    install_wave8_cherokee_entities(release_entities)
    install_wave8_druze_rebels_entities(release_entities)
    install_wave8_insubrian_gauls_entities(release_entities)
    install_wave8_kiowa_entities(release_entities)
    install_wave8_uzbekistan_entities(release_entities)
    install_wave8_vietnam_entities(release_entities)
    install_wave8_hussites_entities(release_entities)
    install_wave8_livonian_order_entities(release_entities)
    install_wave8_satsuma_entities(release_entities)
    install_wave8_rajputs_entities(release_entities)
    install_wave8_mamluk_egypt_entities(release_entities)
    install_wave8_rebel_barons_entities(release_entities)
    install_wave8_thebes_entities(release_entities)
    install_wave8_alemanni_entities(release_entities)
    install_wave8_madagascar_entities(release_entities)
    install_wave8_kickapoo_entities(release_entities)
    install_wave8_lordship_isles_entities(release_entities)
    install_wave8_armenia_entities(release_entities)
    install_wave8_comanches_entities(release_entities)
    install_wave8_sikh_punjab_entities(release_entities)
    install_wave8_eritrea_entities(release_entities)
    install_wave8_flanders_entities(release_entities)
    install_wave8_france_bavaria_entities(release_entities)
    install_wave8_eritrean_rebels_entities(release_entities)
    install_wave8_inca_rebels_entities(release_entities)
    install_wave8_haitian_rebels_entities(release_entities)
    install_wave8_kingdom_kandy_entities(release_entities)
    install_wave8_hospitallers_entities(release_entities)
    install_wave8_murids_entities(release_entities)
    install_wave8_punjabi_sikhs_entities(release_entities)
    install_wave8_modoc_entities(release_entities)
    install_wave8_sauk_entities(release_entities)
    install_wave8_ute_entities(release_entities)
    install_wave8_yakima_entities(release_entities)
    install_wave8_taliban_al_qaeda_entities(release_entities)
    install_wave8_french_religious_forces_entities(release_entities)
    install_wave8_chadian_rebels_entities(release_entities)
    install_wave8_saudi_rashidi_entities(release_entities)
    install_wave8_yaqui_entities(release_entities)
    install_wave8_egypt_forces_entities(release_entities)
    install_wave8_haiti_regimes_entities(release_entities)
    install_wave8_zulu_forces_entities(release_entities)
    install_wave8_montenegro_1796_entities(release_entities)
    install_wave8_bohemia_entities(release_entities)
    install_wave8_spanish_liberals_entities(release_entities)
    install_wave8_achea_entities(release_entities)
    install_wave8_oran_entities(release_entities)
    install_wave8_cheyenne_dog_soldiers_entities(release_entities)
    install_wave8_libya_entities(release_entities)
    install_wave8_kievan_rus_entities(release_entities)
    install_wave8_carnatic_entities(release_entities)
    install_wave8_goguryeo_entities(release_entities)
    install_wave8_fln_entities(release_entities)
    install_wave8_sindh_entities(release_entities)
    install_wave8_oman_entities(release_entities)
    install_wave8_bannock_sheepeater_entities(release_entities)
    install_wave8_catholic_rebels_entities(release_entities)
    install_wave8_macedon_entities(release_entities)
    install_wave8_uzbeks_entities(release_entities)
    install_wave8_etruria_entities(release_entities)
    # Five already-rated Orange rows are rebuilt through the legacy label pass
    # solely so this exact, complete-event fingerprint migration can replace
    # their old source-candidate identity atomically. Any upstream drift aborts.
    label_events = migrate_wave7_global_orange_events(hced, label_events)
    wave7_root_events = promote_wave7_root_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
        ],
    )
    wave7_central_events = promote_wave7_central_hced_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
        ],
    )
    polish_correction_partition_size = len(source_events)
    polish_corrected_events = apply_wave8_polish_audit_corrections(
        [*source_events, *wave7_central_events]
    )
    source_events = polish_corrected_events[:polish_correction_partition_size]
    wave7_central_events = polish_corrected_events[polish_correction_partition_size:]
    wave7_central_pass2_events = promote_wave7_central_pass2_hced_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
        ],
    )
    wave7_global_events = promote_wave7_global_hced_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
        ],
    )
    wave7_west_events = promote_wave7_west_hced_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
        ],
    )
    wave8_african_states_events = promote_wave8_african_states_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
        ],
    )
    wave8_new_zealand_events = promote_wave8_new_zealand_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
        ],
    )
    wave8_north_america_events = promote_wave8_north_america_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
        ],
    )
    wave8_xhosa_events = promote_wave8_xhosa_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
        ],
    )
    wave8_polish_audit_events = promote_wave8_polish_audit_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
        ],
    )
    wave8_namibia_resistance_events = promote_wave8_namibia_resistance_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
        ],
    )
    wave8_first_saudi_events = promote_wave8_first_saudi_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
        ],
    )
    wave8_early_states_events = promote_wave8_early_states_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
        ],
    )
    wave8_judean_revolts_events = promote_wave8_judean_revolts_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
        ],
    )
    wave8_canadian_resistance_events = promote_wave8_canadian_resistance_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
        ],
    )
    wave8_wales_events = promote_wave8_wales_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
        ],
    )
    wave8_cossack_events = promote_wave8_cossack_events(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
        ],
    )
    wave8_fast17_events = promote_wave8_fast17_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
        ],
    )
    wave8_naples_events = promote_wave8_naples_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
        ],
    )
    wave8_somali_irish_sa_events = promote_wave8_somali_irish_sa_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
        ],
    )
    wave8_argentine_independence_events = (
        promote_wave8_argentine_independence_contracts(
            hced,
            release_entities,
            [
                *seed_events,
                *source_events,
                *iwd_events,
                *label_events,
                *wave6_events,
                *wave7_root_events,
                *wave7_central_events,
                *wave7_central_pass2_events,
                *wave7_global_events,
                *wave7_west_events,
                *wave8_african_states_events,
                *wave8_new_zealand_events,
                *wave8_north_america_events,
                *wave8_xhosa_events,
                *wave8_polish_audit_events,
                *wave8_namibia_resistance_events,
                *wave8_first_saudi_events,
                *wave8_early_states_events,
                *wave8_judean_revolts_events,
                *wave8_canadian_resistance_events,
                *wave8_wales_events,
                *wave8_cossack_events,
                *wave8_fast17_events,
                *wave8_naples_events,
                *wave8_somali_irish_sa_events,
            ],
        )
    )
    wave8_ecuador_independence_events = promote_wave8_ecuador_independence_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
        ],
    )
    wave8_comanche_events = promote_wave8_comanche_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
        ],
    )
    wave8_garibaldi_events = promote_wave8_garibaldi_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
        ],
    )
    wave8_algiers_cheyenne_events = promote_wave8_algiers_cheyenne_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
        ],
    )
    wave8_dagestan_events = promote_wave8_dagestan_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
        ],
    )
    wave8_irish_history_events = promote_wave8_irish_history_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
        ],
    )
    wave8_muslim_forces_events = promote_wave8_muslim_forces_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
        ],
    )
    wave8_moros_events = promote_wave8_moros_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
        ],
    )
    wave8_manchus_events = promote_wave8_manchus_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
        ],
    )
    wave8_peruvian_rebels_events = promote_wave8_peruvian_rebels_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
            *wave8_manchus_events,
        ],
    )
    wave8_germany_events = promote_wave8_germany_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
            *wave8_manchus_events,
            *wave8_peruvian_rebels_events,
        ],
    )
    wave8_seljuks_events = promote_wave8_seljuks_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
            *wave8_manchus_events,
            *wave8_peruvian_rebels_events,
            *wave8_germany_events,
        ],
    )
    wave8_danish_vikings_events = promote_wave8_danish_vikings_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
            *wave8_manchus_events,
            *wave8_peruvian_rebels_events,
            *wave8_germany_events,
            *wave8_seljuks_events,
        ],
    )
    wave8_epirus_events = promote_wave8_epirus_contracts(
        hced,
        release_entities,
        [
            *seed_events,
            *source_events,
            *iwd_events,
            *label_events,
            *wave6_events,
            *wave7_root_events,
            *wave7_central_events,
            *wave7_central_pass2_events,
            *wave7_global_events,
            *wave7_west_events,
            *wave8_african_states_events,
            *wave8_new_zealand_events,
            *wave8_north_america_events,
            *wave8_xhosa_events,
            *wave8_polish_audit_events,
            *wave8_namibia_resistance_events,
            *wave8_first_saudi_events,
            *wave8_early_states_events,
            *wave8_judean_revolts_events,
            *wave8_canadian_resistance_events,
            *wave8_wales_events,
            *wave8_cossack_events,
            *wave8_fast17_events,
            *wave8_naples_events,
            *wave8_somali_irish_sa_events,
            *wave8_argentine_independence_events,
            *wave8_ecuador_independence_events,
            *wave8_comanche_events,
            *wave8_garibaldi_events,
            *wave8_algiers_cheyenne_events,
            *wave8_dagestan_events,
            *wave8_irish_history_events,
            *wave8_muslim_forces_events,
            *wave8_moros_events,
            *wave8_manchus_events,
            *wave8_peruvian_rebels_events,
            *wave8_germany_events,
            *wave8_seljuks_events,
            *wave8_danish_vikings_events,
        ],
    )
    wave8_savoy_existing_events = [
        *seed_events,
        *source_events,
        *iwd_events,
        *label_events,
        *wave6_events,
        *wave7_root_events,
        *wave7_central_events,
        *wave7_central_pass2_events,
        *wave7_global_events,
        *wave7_west_events,
        *wave8_african_states_events,
        *wave8_new_zealand_events,
        *wave8_north_america_events,
        *wave8_xhosa_events,
        *wave8_polish_audit_events,
        *wave8_namibia_resistance_events,
        *wave8_first_saudi_events,
        *wave8_early_states_events,
        *wave8_judean_revolts_events,
        *wave8_canadian_resistance_events,
        *wave8_wales_events,
        *wave8_cossack_events,
        *wave8_fast17_events,
        *wave8_naples_events,
        *wave8_somali_irish_sa_events,
        *wave8_argentine_independence_events,
        *wave8_ecuador_independence_events,
        *wave8_comanche_events,
        *wave8_garibaldi_events,
        *wave8_algiers_cheyenne_events,
        *wave8_dagestan_events,
        *wave8_irish_history_events,
        *wave8_muslim_forces_events,
        *wave8_moros_events,
        *wave8_manchus_events,
        *wave8_peruvian_rebels_events,
        *wave8_germany_events,
        *wave8_seljuks_events,
        *wave8_danish_vikings_events,
        *wave8_epirus_events,
    ]
    wave8_savoy_events = promote_wave8_savoy_contracts(
        hced,
        release_entities,
        wave8_savoy_existing_events,
    )
    wave8_nez_perce_existing_events = [
        *wave8_savoy_existing_events,
        *wave8_savoy_events,
    ]
    wave8_nez_perce_events = promote_wave8_nez_perce_contracts(
        hced,
        release_entities,
        wave8_nez_perce_existing_events,
    )
    wave8_dacia_existing_events = [
        *wave8_nez_perce_existing_events,
        *wave8_nez_perce_events,
    ]
    wave8_dacia_events = promote_wave8_dacia_contracts(
        hced,
        release_entities,
        wave8_dacia_existing_events,
    )
    wave8_cherokee_existing_events = [
        *wave8_dacia_existing_events,
        *wave8_dacia_events,
    ]
    wave8_cherokee_events = promote_wave8_cherokee_contracts(
        hced,
        release_entities,
        wave8_cherokee_existing_events,
    )
    wave8_druze_rebels_existing_events = [
        *wave8_cherokee_existing_events,
        *wave8_cherokee_events,
    ]
    wave8_druze_rebels_events = promote_wave8_druze_rebels_contracts(
        hced,
        release_entities,
        wave8_druze_rebels_existing_events,
    )
    wave8_insubrian_gauls_existing_events = [
        *wave8_druze_rebels_existing_events,
        *wave8_druze_rebels_events,
    ]
    wave8_insubrian_gauls_events = promote_wave8_insubrian_gauls_contracts(
        hced,
        release_entities,
        wave8_insubrian_gauls_existing_events,
    )
    wave8_kiowa_existing_events = [
        *wave8_insubrian_gauls_existing_events,
        *wave8_insubrian_gauls_events,
    ]
    wave8_kiowa_events = promote_wave8_kiowa_contracts(
        hced,
        release_entities,
        wave8_kiowa_existing_events,
    )
    wave8_uzbekistan_existing_events = [
        *wave8_kiowa_existing_events,
        *wave8_kiowa_events,
    ]
    wave8_uzbekistan_events = promote_wave8_uzbekistan_contracts(
        hced,
        release_entities,
        wave8_uzbekistan_existing_events,
    )
    wave8_vietnam_existing_events = [
        *wave8_uzbekistan_existing_events,
        *wave8_uzbekistan_events,
    ]
    wave8_vietnam_events = promote_wave8_vietnam_contracts(
        hced,
        release_entities,
        wave8_vietnam_existing_events,
    )
    wave8_hussites_existing_events = [
        *wave8_vietnam_existing_events,
        *wave8_vietnam_events,
    ]
    wave8_hussites_events = promote_wave8_hussites_contracts(
        hced,
        release_entities,
        wave8_hussites_existing_events,
    )
    wave8_livonian_order_existing_events = [
        *wave8_hussites_existing_events,
        *wave8_hussites_events,
    ]
    wave8_livonian_order_events = promote_wave8_livonian_order_contracts(
        hced,
        release_entities,
        wave8_livonian_order_existing_events,
    )
    wave8_satsuma_existing_events = [
        *wave8_livonian_order_existing_events,
        *wave8_livonian_order_events,
    ]
    wave8_satsuma_events = promote_wave8_satsuma_contracts(
        hced,
        release_entities,
        wave8_satsuma_existing_events,
    )
    wave8_rajputs_existing_events = [
        *wave8_satsuma_existing_events,
        *wave8_satsuma_events,
    ]
    wave8_rajputs_events = promote_wave8_rajputs_contracts(
        hced,
        release_entities,
        wave8_rajputs_existing_events,
    )
    wave8_mamluk_egypt_existing_events = [
        *wave8_rajputs_existing_events,
        *wave8_rajputs_events,
    ]
    wave8_mamluk_egypt_events = promote_wave8_mamluk_egypt_contracts(
        hced,
        release_entities,
        wave8_mamluk_egypt_existing_events,
    )
    wave8_rebel_barons_existing_events = [
        *wave8_mamluk_egypt_existing_events,
        *wave8_mamluk_egypt_events,
    ]
    wave8_rebel_barons_events = promote_wave8_rebel_barons_contracts(
        hced,
        release_entities,
        wave8_rebel_barons_existing_events,
    )
    wave8_thebes_existing_events = [
        *wave8_rebel_barons_existing_events,
        *wave8_rebel_barons_events,
    ]
    wave8_thebes_events = promote_wave8_thebes_contracts(
        hced,
        release_entities,
        wave8_thebes_existing_events,
    )
    wave8_alemanni_existing_events = [
        *wave8_thebes_existing_events,
        *wave8_thebes_events,
    ]
    wave8_alemanni_events = promote_wave8_alemanni_contracts(
        hced,
        release_entities,
        wave8_alemanni_existing_events,
    )
    wave8_madagascar_existing_events = [
        *wave8_alemanni_existing_events,
        *wave8_alemanni_events,
    ]
    wave8_madagascar_events = promote_wave8_madagascar_contracts(
        hced,
        release_entities,
        wave8_madagascar_existing_events,
    )
    wave8_kickapoo_existing_events = [
        *wave8_madagascar_existing_events,
        *wave8_madagascar_events,
    ]
    wave8_kickapoo_events = promote_wave8_kickapoo_contracts(
        hced,
        release_entities,
        wave8_kickapoo_existing_events,
    )
    wave8_lordship_isles_existing_events = [
        *wave8_kickapoo_existing_events,
        *wave8_kickapoo_events,
    ]
    wave8_lordship_isles_events = promote_wave8_lordship_isles_contracts(
        hced,
        release_entities,
        wave8_lordship_isles_existing_events,
    )
    wave8_armenia_existing_events = [
        *wave8_lordship_isles_existing_events,
        *wave8_lordship_isles_events,
    ]
    wave8_armenia_events = promote_wave8_armenia_contracts(
        hced,
        release_entities,
        wave8_armenia_existing_events,
    )
    wave8_comanches_existing_events = [
        *wave8_armenia_existing_events,
        *wave8_armenia_events,
    ]
    wave8_comanches_events = promote_wave8_comanches_contracts(
        hced,
        release_entities,
        wave8_comanches_existing_events,
    )
    wave8_sikh_punjab_existing_events = [
        *wave8_comanches_existing_events,
        *wave8_comanches_events,
    ]
    wave8_sikh_punjab_events = promote_wave8_sikh_punjab_contracts(
        hced,
        release_entities,
        wave8_sikh_punjab_existing_events,
    )
    wave8_eritrea_existing_events = [
        *wave8_sikh_punjab_existing_events,
        *wave8_sikh_punjab_events,
    ]
    wave8_eritrea_events = promote_wave8_eritrea_contracts(
        hced,
        release_entities,
        wave8_eritrea_existing_events,
    )
    wave8_flanders_existing_events = [
        *wave8_eritrea_existing_events,
        *wave8_eritrea_events,
    ]
    wave8_flanders_events = promote_wave8_flanders_contracts(
        hced,
        release_entities,
        wave8_flanders_existing_events,
    )
    wave8_france_bavaria_existing_events = [
        *wave8_flanders_existing_events,
        *wave8_flanders_events,
    ]
    wave8_france_bavaria_events = promote_wave8_france_bavaria_contracts(
        hced,
        release_entities,
        wave8_france_bavaria_existing_events,
    )
    wave8_eritrean_rebels_existing_events = [
        *wave8_france_bavaria_existing_events,
        *wave8_france_bavaria_events,
    ]
    wave8_eritrean_rebels_events = promote_wave8_eritrean_rebels_contracts(
        hced,
        release_entities,
        wave8_eritrean_rebels_existing_events,
    )
    wave8_inca_rebels_existing_events = [
        *wave8_eritrean_rebels_existing_events,
        *wave8_eritrean_rebels_events,
    ]
    wave8_inca_rebels_events = promote_wave8_inca_rebels_contracts(
        hced,
        release_entities,
        wave8_inca_rebels_existing_events,
    )
    wave8_haitian_rebels_existing_events = [
        *wave8_inca_rebels_existing_events,
        *wave8_inca_rebels_events,
    ]
    wave8_haitian_rebels_events = promote_wave8_haitian_rebels_contracts(
        hced,
        release_entities,
        wave8_haitian_rebels_existing_events,
    )
    wave8_kingdom_kandy_existing_events = [
        *wave8_haitian_rebels_existing_events,
        *wave8_haitian_rebels_events,
    ]
    wave8_kingdom_kandy_events = promote_wave8_kingdom_kandy_contracts(
        hced,
        release_entities,
        wave8_kingdom_kandy_existing_events,
    )
    wave8_hospitallers_existing_events = [
        *wave8_kingdom_kandy_existing_events,
        *wave8_kingdom_kandy_events,
    ]
    wave8_hospitallers_events = promote_wave8_hospitallers_contracts(
        hced,
        release_entities,
        wave8_hospitallers_existing_events,
    )
    wave8_murids_existing_events = [
        *wave8_hospitallers_existing_events,
        *wave8_hospitallers_events,
    ]
    wave8_murids_events = promote_wave8_murids_contracts(
        hced,
        release_entities,
        wave8_murids_existing_events,
    )
    wave8_punjabi_sikhs_existing_events = [
        *wave8_murids_existing_events,
        *wave8_murids_events,
    ]
    wave8_punjabi_sikhs_events = promote_wave8_punjabi_sikhs_contracts(
        hced,
        release_entities,
        wave8_punjabi_sikhs_existing_events,
    )
    wave8_modoc_existing_events = [
        *wave8_punjabi_sikhs_existing_events,
        *wave8_punjabi_sikhs_events,
    ]
    wave8_modoc_events = promote_wave8_modoc_contracts(
        hced,
        release_entities,
        wave8_modoc_existing_events,
    )
    wave8_sauk_existing_events = [
        *wave8_modoc_existing_events,
        *wave8_modoc_events,
    ]
    wave8_sauk_events = promote_wave8_sauk_contracts(
        hced,
        release_entities,
        wave8_sauk_existing_events,
    )
    wave8_ute_existing_events = [
        *wave8_sauk_existing_events,
        *wave8_sauk_events,
    ]
    wave8_ute_events = promote_wave8_ute_contracts(
        hced,
        release_entities,
        wave8_ute_existing_events,
    )
    wave8_yakima_existing_events = [
        *wave8_ute_existing_events,
        *wave8_ute_events,
    ]
    wave8_yakima_events = promote_wave8_yakima_contracts(
        hced,
        release_entities,
        wave8_yakima_existing_events,
    )
    wave8_taliban_al_qaeda_existing_events = [
        *wave8_yakima_existing_events,
        *wave8_yakima_events,
    ]
    wave8_taliban_al_qaeda_events = promote_wave8_taliban_al_qaeda_contracts(
        hced,
        release_entities,
        wave8_taliban_al_qaeda_existing_events,
    )
    wave8_french_religious_forces_existing_events = [
        *wave8_taliban_al_qaeda_existing_events,
        *wave8_taliban_al_qaeda_events,
    ]
    wave8_french_religious_forces_events = (
        promote_wave8_french_religious_forces_contracts(
            hced,
            release_entities,
            wave8_french_religious_forces_existing_events,
        )
    )
    wave8_chadian_rebels_existing_events = [
        *wave8_french_religious_forces_existing_events,
        *wave8_french_religious_forces_events,
    ]
    wave8_chadian_rebels_events = promote_wave8_chadian_rebels_contracts(
        hced,
        release_entities,
        wave8_chadian_rebels_existing_events,
    )
    wave8_saudi_rashidi_existing_events = [
        *wave8_chadian_rebels_existing_events,
        *wave8_chadian_rebels_events,
    ]
    wave8_saudi_rashidi_events = promote_wave8_saudi_rashidi_contracts(
        hced,
        release_entities,
        wave8_saudi_rashidi_existing_events,
    )
    wave8_yaqui_existing_events = [
        *wave8_saudi_rashidi_existing_events,
        *wave8_saudi_rashidi_events,
    ]
    wave8_yaqui_events = promote_wave8_yaqui_contracts(
        hced,
        release_entities,
        wave8_yaqui_existing_events,
    )
    wave8_egypt_forces_existing_events = [
        *wave8_yaqui_existing_events,
        *wave8_yaqui_events,
    ]
    wave8_egypt_forces_events = promote_wave8_egypt_forces_contracts(
        hced,
        release_entities,
        wave8_egypt_forces_existing_events,
    )
    wave8_haiti_regimes_existing_events = [
        *wave8_egypt_forces_existing_events,
        *wave8_egypt_forces_events,
    ]
    wave8_haiti_regimes_events = promote_wave8_haiti_regimes_contracts(
        hced,
        release_entities,
        wave8_haiti_regimes_existing_events,
    )
    wave8_zulu_forces_existing_events = [
        *wave8_haiti_regimes_existing_events,
        *wave8_haiti_regimes_events,
    ]
    wave8_zulu_forces_events = promote_wave8_zulu_forces_contracts(
        hced,
        release_entities,
        wave8_zulu_forces_existing_events,
    )
    wave8_montenegro_1796_existing_events = [
        *wave8_zulu_forces_existing_events,
        *wave8_zulu_forces_events,
    ]
    wave8_montenegro_1796_events = promote_wave8_montenegro_1796_contracts(
        hced,
        release_entities,
        wave8_montenegro_1796_existing_events,
    )
    wave8_bohemia_existing_events = [
        *wave8_montenegro_1796_existing_events,
        *wave8_montenegro_1796_events,
    ]
    wave8_bohemia_events = promote_wave8_bohemia_contracts(
        hced,
        release_entities,
        wave8_bohemia_existing_events,
    )
    wave8_spanish_liberals_existing_events = [
        *wave8_bohemia_existing_events,
        *wave8_bohemia_events,
    ]
    wave8_spanish_liberals_events = promote_wave8_spanish_liberals_contracts(
        hced,
        release_entities,
        wave8_spanish_liberals_existing_events,
    )
    wave8_achea_existing_events = [
        *wave8_spanish_liberals_existing_events,
        *wave8_spanish_liberals_events,
    ]
    wave8_achea_events = promote_wave8_achea_contracts(
        hced,
        release_entities,
        wave8_achea_existing_events,
    )
    wave8_oran_existing_events = [
        *wave8_achea_existing_events,
        *wave8_achea_events,
    ]
    wave8_oran_events = promote_wave8_oran_contracts(
        hced,
        release_entities,
        wave8_oran_existing_events,
    )
    wave8_cheyenne_dog_soldiers_existing_events = [
        *wave8_oran_existing_events,
        *wave8_oran_events,
    ]
    wave8_cheyenne_dog_soldiers_events = (
        promote_wave8_cheyenne_dog_soldiers_contracts(
            hced,
            release_entities,
            wave8_cheyenne_dog_soldiers_existing_events,
        )
    )
    wave8_algiers_cheyenne_post_dog_soldiers_validation = (
        validate_wave8_algiers_cheyenne_queue_contracts(hced)
    )
    if (
        wave8_algiers_cheyenne_post_dog_soldiers_validation
        != wave8_algiers_cheyenne_queue_validation
    ):
        raise ValueError(
            "Wave 8 Cheyenne Dog Soldiers lane changed the frozen "
            "Algiers/Cheyenne inventory"
        )
    wave8_libya_existing_events = [
        *wave8_cheyenne_dog_soldiers_existing_events,
        *wave8_cheyenne_dog_soldiers_events,
    ]
    wave8_libya_events = promote_wave8_libya_contracts(
        hced,
        release_entities,
        wave8_libya_existing_events,
    )
    wave8_libya_frozen_chadian_rebels_post_validation = (
        validate_wave8_libya_frozen_chadian_rebels()
    )
    if (
        wave8_libya_frozen_chadian_rebels_post_validation
        != wave8_libya_frozen_chadian_rebels_pre_validation
    ):
        raise ValueError(
            "Wave 8 Libya lane changed the frozen Chadian Rebels lane"
        )
    wave8_kievan_rus_existing_events = [
        *wave8_libya_existing_events,
        *wave8_libya_events,
    ]
    wave8_kievan_rus_events = promote_wave8_kievan_rus_contracts(
        hced,
        release_entities,
        wave8_kievan_rus_existing_events,
    )
    wave8_carnatic_existing_events = [
        *wave8_kievan_rus_existing_events,
        *wave8_kievan_rus_events,
    ]
    wave8_carnatic_events = promote_wave8_carnatic_contracts(
        hced,
        release_entities,
        wave8_carnatic_existing_events,
    )
    wave8_goguryeo_existing_events = [
        *wave8_carnatic_existing_events,
        *wave8_carnatic_events,
    ]
    wave8_goguryeo_events = promote_wave8_goguryeo_contracts(
        hced,
        release_entities,
        wave8_goguryeo_existing_events,
    )
    wave8_fln_existing_events = [
        *wave8_goguryeo_existing_events,
        *wave8_goguryeo_events,
    ]
    wave8_fln_events = promote_wave8_fln_contracts(
        hced,
        release_entities,
        wave8_fln_existing_events,
    )
    wave8_sindh_existing_events = [
        *wave8_fln_existing_events,
        *wave8_fln_events,
    ]
    wave8_sindh_events = promote_wave8_sindh_contracts(
        hced,
        release_entities,
        wave8_sindh_existing_events,
    )
    wave8_oman_existing_events = [
        *wave8_sindh_existing_events,
        *wave8_sindh_events,
    ]
    wave8_oman_events = promote_wave8_oman_contracts(
        hced,
        release_entities,
        wave8_oman_existing_events,
    )
    wave8_irish_civil_war_existing_events = [
        *wave8_oman_existing_events,
        *wave8_oman_events,
    ]
    wave8_irish_civil_war_events = promote_wave8_irish_civil_war_contracts(
        hced,
        release_entities,
        wave8_irish_civil_war_existing_events,
    )
    wave8_bannock_sheepeater_existing_events = [
        *wave8_irish_civil_war_existing_events,
        *wave8_irish_civil_war_events,
    ]
    wave8_bannock_sheepeater_events = promote_wave8_bannock_sheepeater_contracts(
        hced,
        release_entities,
        wave8_bannock_sheepeater_existing_events,
    )
    wave8_catholic_rebels_existing_events = [
        *wave8_bannock_sheepeater_existing_events,
        *wave8_bannock_sheepeater_events,
    ]
    wave8_catholic_rebels_events = promote_wave8_catholic_rebels_contracts(
        hced,
        release_entities,
        wave8_catholic_rebels_existing_events,
    )
    wave8_macedon_existing_events = [
        *wave8_catholic_rebels_existing_events,
        *wave8_catholic_rebels_events,
    ]
    wave8_macedon_events = promote_wave8_macedon_contracts(
        hced,
        release_entities,
        wave8_macedon_existing_events,
    )
    wave8_uzbeks_existing_events = [
        *wave8_macedon_existing_events,
        *wave8_macedon_events,
    ]
    wave8_uzbeks_events = promote_wave8_uzbeks_contracts(
        hced,
        release_entities,
        wave8_uzbeks_existing_events,
    )
    wave8_etruria_existing_events = [
        *wave8_uzbeks_existing_events,
        *wave8_uzbeks_events,
    ]
    wave8_etruria_events = promote_wave8_etruria_contracts(
        hced,
        release_entities,
        wave8_etruria_existing_events,
    )
    for event in (
        *wave6_events,
        *wave7_root_events,
        *wave7_central_events,
        *wave7_central_pass2_events,
        *wave7_global_events,
        *wave7_west_events,
        *wave8_african_states_events,
        *wave8_new_zealand_events,
        *wave8_north_america_events,
        *wave8_xhosa_events,
        *wave8_polish_audit_events,
        *wave8_namibia_resistance_events,
        *wave8_first_saudi_events,
        *wave8_early_states_events,
        *wave8_judean_revolts_events,
        *wave8_canadian_resistance_events,
        *wave8_wales_events,
        *wave8_cossack_events,
        *wave8_fast17_events,
        *wave8_naples_events,
        *wave8_somali_irish_sa_events,
        *wave8_argentine_independence_events,
        *wave8_ecuador_independence_events,
        *wave8_comanche_events,
        *wave8_garibaldi_events,
        *wave8_algiers_cheyenne_events,
        *wave8_dagestan_events,
        *wave8_irish_history_events,
        *wave8_muslim_forces_events,
        *wave8_moros_events,
        *wave8_manchus_events,
        *wave8_peruvian_rebels_events,
        *wave8_germany_events,
        *wave8_seljuks_events,
        *wave8_danish_vikings_events,
        *wave8_epirus_events,
        *wave8_savoy_events,
        *wave8_nez_perce_events,
        *wave8_dacia_events,
        *wave8_cherokee_events,
        *wave8_druze_rebels_events,
        *wave8_insubrian_gauls_events,
        *wave8_kiowa_events,
        *wave8_uzbekistan_events,
        *wave8_vietnam_events,
        *wave8_hussites_events,
        *wave8_livonian_order_events,
        *wave8_satsuma_events,
        *wave8_rajputs_events,
        *wave8_mamluk_egypt_events,
        *wave8_rebel_barons_events,
        *wave8_thebes_events,
        *wave8_alemanni_events,
        *wave8_madagascar_events,
        *wave8_kickapoo_events,
        *wave8_lordship_isles_events,
        *wave8_armenia_events,
        *wave8_comanches_events,
        *wave8_sikh_punjab_events,
        *wave8_eritrea_events,
        *wave8_flanders_events,
        *wave8_france_bavaria_events,
        *wave8_eritrean_rebels_events,
        *wave8_inca_rebels_events,
        *wave8_haitian_rebels_events,
        *wave8_kingdom_kandy_events,
        *wave8_hospitallers_events,
        *wave8_murids_events,
        *wave8_punjabi_sikhs_events,
        *wave8_modoc_events,
        *wave8_sauk_events,
        *wave8_ute_events,
        *wave8_yakima_events,
        *wave8_taliban_al_qaeda_events,
        *wave8_french_religious_forces_events,
        *wave8_chadian_rebels_events,
        *wave8_saudi_rashidi_events,
        *wave8_yaqui_events,
        *wave8_egypt_forces_events,
        *wave8_haiti_regimes_events,
        *wave8_zulu_forces_events,
        *wave8_montenegro_1796_events,
        *wave8_bohemia_events,
        *wave8_spanish_liberals_events,
        *wave8_achea_events,
        *wave8_oran_events,
        *wave8_cheyenne_dog_soldiers_events,
        *wave8_libya_events,
        *wave8_kievan_rus_events,
        *wave8_carnatic_events,
        *wave8_goguryeo_events,
        *wave8_fln_events,
        *wave8_sindh_events,
        *wave8_oman_events,
        *wave8_irish_civil_war_events,
        *wave8_bannock_sheepeater_events,
        *wave8_catholic_rebels_events,
        *wave8_macedon_events,
        *wave8_uzbeks_events,
        *wave8_etruria_events,
    ):
        candidate = hced_candidates_by_id[str(event["hced_candidate_id"])]
        war_names = list(map(str, candidate.get("war_names", [])))
        if not war_names or event.get("cluster_id") is None:
            continue
        cluster_id = str(event["cluster_id"])
        low_year = int(event["year"])
        high_year = int(event["end_year"])
        span = hced_cluster_spans.setdefault(
            cluster_id,
            [_war_tokens(war_names[0]), low_year, high_year],
        )
        span[1] = min(span[1], low_year)
        span[2] = max(span[2], high_year)

    # IWBD battles are deduplicated against curated seed events and every
    # non-curated-excluded HCED candidate — promoted or staged, over the
    # candidate's full year range — because a mechanically rejected HCED row
    # may promote later and no event may ever enter the tactical stream twice.
    hced_event_keys: dict[tuple[str, int], dict[str, Any]] = {}

    def hced_index_entry(key: tuple[str, int]) -> dict[str, Any]:
        return hced_event_keys.setdefault(key, {"exact": False, "outcomes": set()})

    for candidate in hced:
        if str(candidate.get("candidate_id")) in {
            *EFFECTIVE_HCED_CURATED_EXCLUSIONS,
            *HCED_LABEL_CURATED_EXCLUSIONS,
            *WAVE6_HCED_NONPROMOTED_IDS,
            *WAVE7_ROOT_HOLD_IDS,
            *WAVE7_CENTRAL_HOLD_IDS,
            *WAVE7_CENTRAL_PASS2_HOLD_IDS,
            *WAVE7_GLOBAL_HCED_HOLD_IDS,
            *WAVE7_WEST_HCED_HOLDS,
            *WAVE8_NEW_ZEALAND_HOLD_IDS,
            *WAVE8_NORTH_AMERICA_HOLD_IDS,
            *WAVE8_POLISH_AUDIT_HOLD_IDS,
            *WAVE8_XHOSA_HOLD_IDS,
            *WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS,
            *WAVE8_FIRST_SAUDI_HOLD_IDS,
            *WAVE8_EARLY_STATES_HOLD_IDS,
            *WAVE8_JUDEAN_REVOLTS_HOLD_IDS,
            *WAVE8_CANADIAN_RESISTANCE_HOLD_IDS,
            *WAVE8_WALES_HOLD_IDS,
            *WAVE8_COSSACK_HOLD_IDS,
            *WAVE8_FAST17_HOLD_IDS,
            *WAVE8_NAPLES_HOLD_IDS,
            *WAVE8_SOMALI_IRISH_SA_HOLD_IDS,
            *WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS,
            *WAVE8_ECUADOR_INDEPENDENCE_HOLD_IDS,
            *WAVE8_COMANCHE_HOLD_IDS,
            *WAVE8_GARIBALDI_HOLD_IDS,
            *WAVE8_ALGIERS_CHEYENNE_HOLD_IDS,
            *WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
            *WAVE8_DAGESTAN_HOLD_IDS,
            *WAVE8_IRISH_HISTORY_HOLD_IDS,
            *WAVE8_MUSLIM_FORCES_HOLD_IDS,
            *WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_MOROS_HOLD_IDS,
            *WAVE8_MANCHUS_HOLD_IDS,
            *WAVE8_PERUVIAN_REBELS_HOLD_IDS,
            *WAVE8_GERMANY_HOLD_IDS,
            *WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
            *WAVE8_SELJUKS_HOLD_IDS,
            *WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_DANISH_VIKINGS_HOLD_IDS,
            *WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_EPIRUS_HOLD_IDS,
            *WAVE8_SAVOY_HOLD_IDS,
            *WAVE8_SAVOY_EXCLUSION_IDS,
            *WAVE8_NEZ_PERCE_HOLD_IDS,
            *WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS,
            *WAVE8_DACIA_HOLD_IDS,
            *WAVE8_DACIA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_CHEROKEE_HOLD_IDS,
            *WAVE8_CHEROKEE_EXCLUSION_IDS,
            *WAVE8_DRUZE_REBELS_HOLD_IDS,
            *WAVE8_INSUBRIAN_GAULS_HOLD_IDS,
            *WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_KIOWA_HOLD_IDS,
            *WAVE8_UZBEKISTAN_HOLD_IDS,
            *WAVE8_VIETNAM_HOLD_IDS,
            *WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
            *WAVE8_HUSSITES_HOLD_IDS,
            *WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_LIVONIAN_ORDER_HOLD_IDS,
            *WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSION_IDS,
            *WAVE8_SATSUMA_HOLD_IDS,
            *WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_RAJPUTS_HOLD_IDS,
            *WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_MAMLUK_EGYPT_HOLD_IDS,
            *WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS,
            *WAVE8_REBEL_BARONS_HOLD_IDS,
            *WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_THEBES_HOLD_IDS,
            *WAVE8_THEBES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_ALEMANNI_HOLD_IDS,
            *WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
            *WAVE8_MADAGASCAR_HOLD_IDS,
            *WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS,
            *WAVE8_KICKAPOO_HOLD_IDS,
            *WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
            *WAVE8_LORDSHIP_ISLES_HOLD_IDS,
            *WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_ARMENIA_HOLD_IDS,
            *WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_COMANCHES_HOLD_IDS,
            *WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_SIKH_PUNJAB_HOLD_IDS,
            *WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS,
            *WAVE8_ERITREA_HOLD_IDS,
            *WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_FLANDERS_HOLD_IDS,
            *WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_FRANCE_BAVARIA_HOLD_IDS,
            *WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_ERITREAN_REBELS_HOLD_IDS,
            *WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_INCA_REBELS_HOLD_IDS,
            *WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_HAITIAN_REBELS_HOLD_IDS,
            *WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_KINGDOM_KANDY_HOLD_IDS,
            *WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS,
            *WAVE8_HOSPITALLERS_HOLD_IDS,
            *WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_MURIDS_HOLD_IDS,
            *WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_PUNJABI_SIKHS_HOLD_IDS,
            *WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_MODOC_HOLD_IDS,
            *WAVE8_MODOC_TERMINAL_EXCLUSION_IDS,
            *WAVE8_SAUK_HOLD_IDS,
            *WAVE8_SAUK_TERMINAL_EXCLUSION_IDS,
            *WAVE8_UTE_HOLD_IDS,
            *WAVE8_UTE_TERMINAL_EXCLUSION_IDS,
            *WAVE8_YAKIMA_HOLD_IDS,
            *WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS,
            *WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS,
            *WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS,
            *WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS,
            *WAVE8_CHADIAN_REBELS_HOLD_IDS,
            *WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSION_IDS,
            *WAVE8_SAUDI_RASHIDI_HOLD_IDS,
            *WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS,
            *WAVE8_YAQUI_HOLD_IDS,
            *WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS,
            *WAVE8_EGYPT_FORCES_HOLD_IDS,
            *WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS,
        }:
            continue
        name = str(candidate.get("name") or "")
        if not name:
            continue
        year_low = candidate.get("year_low")
        year_high = candidate.get("year_high")
        if year_low is None or year_high is None:
            for year in {
                candidate.get("year_low"),
                candidate.get("year_best"),
                candidate.get("year_high"),
            }:
                if year is not None:
                    hced_index_entry(_event_key(name, int(year)))["exact"] = True
            continue
        for year in range(int(year_low), int(year_high) + 1):
            hced_index_entry(_event_key(name, year))["exact"] = True

    # Fuzzy ordinal/base-name matches require one recognized suffix path to be
    # a strict extension of the other in the same year, with the same resolved
    # sides and outcome orientation. Different suffix branches never share a
    # key. Only promoted HCED rows can supply that identity signature; exact
    # names above continue to block against staged rows.
    for event in (
        *source_events,
        *label_events,
        *wave6_events,
        *wave7_root_events,
        *wave7_central_events,
        *wave7_central_pass2_events,
        *wave7_global_events,
        *wave7_west_events,
        *wave8_african_states_events,
        *wave8_new_zealand_events,
        *wave8_north_america_events,
        *wave8_xhosa_events,
        *wave8_polish_audit_events,
        *wave8_namibia_resistance_events,
        *wave8_first_saudi_events,
        *wave8_early_states_events,
        *wave8_judean_revolts_events,
        *wave8_canadian_resistance_events,
        *wave8_wales_events,
        *wave8_cossack_events,
        *wave8_fast17_events,
        *wave8_naples_events,
        *wave8_somali_irish_sa_events,
        *wave8_argentine_independence_events,
        *wave8_ecuador_independence_events,
        *wave8_comanche_events,
        *wave8_garibaldi_events,
        *wave8_algiers_cheyenne_events,
        *wave8_dagestan_events,
        *wave8_irish_history_events,
        *wave8_muslim_forces_events,
        *wave8_moros_events,
        *wave8_manchus_events,
        *wave8_peruvian_rebels_events,
        *wave8_germany_events,
        *wave8_seljuks_events,
        *wave8_danish_vikings_events,
        *wave8_epirus_events,
        *wave8_savoy_events,
        *wave8_nez_perce_events,
        *wave8_dacia_events,
        *wave8_cherokee_events,
        *wave8_druze_rebels_events,
        *wave8_insubrian_gauls_events,
        *wave8_kiowa_events,
        *wave8_uzbekistan_events,
        *wave8_vietnam_events,
        *wave8_hussites_events,
        *wave8_livonian_order_events,
        *wave8_satsuma_events,
        *wave8_rajputs_events,
        *wave8_mamluk_egypt_events,
        *wave8_rebel_barons_events,
        *wave8_thebes_events,
        *wave8_alemanni_events,
        *wave8_madagascar_events,
        *wave8_kickapoo_events,
        *wave8_lordship_isles_events,
        *wave8_armenia_events,
        *wave8_comanches_events,
        *wave8_sikh_punjab_events,
        *wave8_eritrea_events,
        *wave8_flanders_events,
        *wave8_france_bavaria_events,
        *wave8_eritrean_rebels_events,
        *wave8_inca_rebels_events,
        *wave8_haitian_rebels_events,
        *wave8_kingdom_kandy_events,
        *wave8_hospitallers_events,
        *wave8_murids_events,
        *wave8_punjabi_sikhs_events,
        *wave8_modoc_events,
        *wave8_sauk_events,
        *wave8_ute_events,
        *wave8_yakima_events,
        *wave8_taliban_al_qaeda_events,
        *wave8_french_religious_forces_events,
        *wave8_chadian_rebels_events,
        *wave8_saudi_rashidi_events,
        *wave8_yaqui_events,
        *wave8_egypt_forces_events,
        *wave8_haiti_regimes_events,
        *wave8_zulu_forces_events,
        *wave8_montenegro_1796_events,
        *wave8_bohemia_events,
        *wave8_spanish_liberals_events,
        *wave8_achea_events,
        *wave8_oran_events,
        *wave8_cheyenne_dog_soldiers_events,
        *wave8_libya_events,
        *wave8_kievan_rus_events,
        *wave8_carnatic_events,
        *wave8_goguryeo_events,
        *wave8_fln_events,
        *wave8_sindh_events,
        *wave8_oman_events,
        *wave8_irish_civil_war_events,
        *wave8_bannock_sheepeater_events,
        *wave8_catholic_rebels_events,
        *wave8_macedon_events,
        *wave8_uzbeks_events,
        *wave8_etruria_events,
    ):
        winners = frozenset(
            str(participant["entity_id"])
            for participant in event["participants"]
            if "victory" in str(participant.get("termination", ""))
        )
        losers = frozenset(
            str(participant["entity_id"])
            for participant in event["participants"]
            if "defeat" in str(participant.get("termination", ""))
        )
        if winners or losers:
            outcome_signature = (winners, losers)
        else:
            outcome_signature = (
                frozenset(str(p["entity_id"]) for p in event["participants"]),
                frozenset(),
            )
        for year in range(int(event["year"]), int(event["end_year"]) + 1):
            for key in _cross_source_event_keys(str(event["name"]), year):
                hced_index_entry(key)["outcomes"].add(outcome_signature)

    iwbd_path = review / "iwbd-candidates.jsonl"
    iwbd_candidates = read_jsonl(iwbd_path) if iwbd_path.exists() else []
    wave8_garibaldi_integration_validation = (
        validate_wave8_garibaldi_integration_dispositions(hced, iwbd_candidates)
    )
    wave8_dagestan_integration_validation = (
        validate_wave8_dagestan_integration_dispositions(hced, iwbd_candidates)
    )
    wave8_irish_history_integration_validation = (
        validate_wave8_irish_history_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *seed_events,
                *source_events,
                *iwd_events,
                *label_events,
                *wave6_events,
                *wave7_root_events,
                *wave7_central_events,
                *wave7_central_pass2_events,
                *wave7_global_events,
                *wave7_west_events,
                *wave8_african_states_events,
                *wave8_new_zealand_events,
                *wave8_north_america_events,
                *wave8_xhosa_events,
                *wave8_polish_audit_events,
                *wave8_namibia_resistance_events,
                *wave8_first_saudi_events,
                *wave8_early_states_events,
                *wave8_judean_revolts_events,
                *wave8_canadian_resistance_events,
                *wave8_wales_events,
                *wave8_cossack_events,
                *wave8_fast17_events,
                *wave8_naples_events,
                *wave8_somali_irish_sa_events,
                *wave8_argentine_independence_events,
                *wave8_ecuador_independence_events,
                *wave8_comanche_events,
                *wave8_garibaldi_events,
                *wave8_algiers_cheyenne_events,
                *wave8_dagestan_events,
            ],
        )
    )
    wave8_manchus_integration_validation = (
        validate_wave8_manchus_integration_dispositions(hced, iwbd_candidates)
    )
    wave8_peruvian_rebels_integration_validation = (
        validate_wave8_peruvian_rebels_integration_dispositions(
            hced, iwbd_candidates
        )
    )
    wave8_germany_integration_validation = (
        validate_wave8_germany_integration_dispositions(hced, iwbd_candidates)
    )
    wave8_seljuks_integration_validation = (
        validate_wave8_seljuks_integration_dispositions(
            hced, iwbd_candidates, wave8_germany_events
        )
    )
    wave8_danish_vikings_integration_validation = (
        validate_wave8_danish_vikings_integration_dispositions(
            hced, iwbd_candidates, wave8_germany_events
        )
    )
    wave8_epirus_integration_validation = (
        validate_wave8_epirus_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *seed_events,
                *source_events,
                *label_events,
                *wave6_events,
                *wave7_root_events,
                *wave7_central_events,
                *wave7_central_pass2_events,
                *wave7_global_events,
                *wave7_west_events,
                *wave8_african_states_events,
                *wave8_new_zealand_events,
                *wave8_north_america_events,
                *wave8_xhosa_events,
                *wave8_polish_audit_events,
                *wave8_namibia_resistance_events,
                *wave8_first_saudi_events,
                *wave8_early_states_events,
                *wave8_judean_revolts_events,
                *wave8_canadian_resistance_events,
                *wave8_wales_events,
                *wave8_cossack_events,
                *wave8_fast17_events,
                *wave8_naples_events,
                *wave8_somali_irish_sa_events,
                *wave8_argentine_independence_events,
                *wave8_ecuador_independence_events,
                *wave8_comanche_events,
                *wave8_garibaldi_events,
                *wave8_algiers_cheyenne_events,
                *wave8_dagestan_events,
                *wave8_irish_history_events,
                *wave8_muslim_forces_events,
                *wave8_moros_events,
                *wave8_manchus_events,
                *wave8_peruvian_rebels_events,
                *wave8_germany_events,
                *wave8_seljuks_events,
                *wave8_danish_vikings_events,
            ],
        )
    )
    wave8_savoy_integration_validation = (
        validate_wave8_savoy_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_savoy_existing_events,
        )
    )
    wave8_nez_perce_integration_validation = (
        validate_wave8_nez_perce_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_nez_perce_existing_events,
        )
    )
    wave8_dacia_integration_validation = (
        validate_wave8_dacia_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_dacia_existing_events,
        )
    )
    wave8_cherokee_integration_validation = (
        validate_wave8_cherokee_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_cherokee_existing_events,
        )
    )
    wave8_druze_rebels_integration_validation = (
        validate_wave8_druze_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_druze_rebels_existing_events,
        )
    )
    wave8_insubrian_gauls_integration_validation = (
        validate_wave8_insubrian_gauls_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_insubrian_gauls_existing_events,
        )
    )
    wave8_kiowa_integration_validation = (
        validate_wave8_kiowa_integration_dispositions(hced, iwbd_candidates)
    )
    wave8_uzbekistan_integration_validation = (
        validate_wave8_uzbekistan_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_uzbekistan_existing_events,
        )
    )
    wave8_vietnam_integration_validation = (
        validate_wave8_vietnam_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_vietnam_existing_events,
        )
    )
    wave8_hussites_integration_validation = (
        validate_wave8_hussites_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_hussites_existing_events,
        )
    )
    wave8_livonian_order_integration_validation = (
        validate_wave8_livonian_order_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_livonian_order_existing_events,
        )
    )
    wave8_satsuma_integration_validation = (
        validate_wave8_satsuma_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_satsuma_existing_events,
        )
    )
    wave8_rajputs_integration_validation = (
        validate_wave8_rajputs_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_rajputs_existing_events,
        )
    )
    wave8_mamluk_egypt_integration_validation = (
        validate_wave8_mamluk_egypt_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_mamluk_egypt_existing_events,
        )
    )
    wave8_rebel_barons_integration_validation = (
        validate_wave8_rebel_barons_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_rebel_barons_existing_events,
        )
    )
    wave8_thebes_integration_validation = (
        validate_wave8_thebes_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_thebes_existing_events,
        )
    )
    wave8_alemanni_integration_validation = (
        validate_wave8_alemanni_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_alemanni_existing_events,
        )
    )
    wave8_madagascar_integration_validation = (
        validate_wave8_madagascar_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_madagascar_existing_events,
        )
    )
    wave8_kickapoo_integration_validation = (
        validate_wave8_kickapoo_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_kickapoo_existing_events,
        )
    )
    wave8_lordship_isles_integration_validation = (
        validate_wave8_lordship_isles_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_lordship_isles_existing_events,
        )
    )
    wave8_armenia_integration_validation = (
        validate_wave8_armenia_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_armenia_existing_events,
        )
    )
    wave8_comanches_integration_validation = (
        validate_wave8_comanches_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_comanches_existing_events,
        )
    )
    wave8_sikh_punjab_integration_validation = (
        validate_wave8_sikh_punjab_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_sikh_punjab_existing_events,
        )
    )
    wave8_eritrea_integration_validation = (
        validate_wave8_eritrea_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_eritrea_existing_events,
        )
    )
    wave8_flanders_integration_validation = (
        validate_wave8_flanders_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_flanders_existing_events,
        )
    )
    wave8_france_bavaria_integration_validation = (
        validate_wave8_france_bavaria_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_france_bavaria_existing_events,
        )
    )
    wave8_eritrean_rebels_integration_validation = (
        validate_wave8_eritrean_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_eritrean_rebels_existing_events,
        )
    )
    wave8_inca_rebels_integration_validation = (
        validate_wave8_inca_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_inca_rebels_existing_events,
        )
    )
    wave8_haitian_rebels_integration_validation = (
        validate_wave8_haitian_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_haitian_rebels_existing_events,
        )
    )
    wave8_kingdom_kandy_integration_validation = (
        validate_wave8_kingdom_kandy_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_kingdom_kandy_existing_events,
        )
    )
    wave8_hospitallers_integration_validation = (
        validate_wave8_hospitallers_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_hospitallers_existing_events,
        )
    )
    wave8_murids_integration_validation = (
        validate_wave8_murids_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_murids_existing_events,
        )
    )
    wave8_punjabi_sikhs_integration_validation = (
        validate_wave8_punjabi_sikhs_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_punjabi_sikhs_existing_events,
        )
    )
    wave8_modoc_integration_validation = (
        validate_wave8_modoc_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_modoc_existing_events,
        )
    )
    wave8_sauk_integration_validation = (
        validate_wave8_sauk_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_sauk_existing_events,
        )
    )
    wave8_ute_integration_validation = validate_wave8_ute_integration_dispositions(
        hced,
        iwbd_candidates,
        wave8_ute_existing_events,
    )
    wave8_yakima_integration_validation = (
        validate_wave8_yakima_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_yakima_existing_events,
        )
    )
    wave8_taliban_al_qaeda_ucdp_rows = [
        row
        for filename in (
            "ucdp-conflict-26.1-candidates.jsonl",
            "ucdp-dyadic-26.1-candidates.jsonl",
            "ucdp-termination-conflict-candidates.jsonl",
            "ucdp-termination-dyad-candidates.jsonl",
        )
        for row in read_jsonl(review / filename)
    ]
    wave8_taliban_al_qaeda_integration_validation = (
        validate_wave8_taliban_al_qaeda_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_taliban_al_qaeda_existing_events,
            wave8_taliban_al_qaeda_ucdp_rows,
        )
    )
    wave8_french_religious_forces_integration_validation = (
        validate_wave8_french_religious_forces_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_french_religious_forces_existing_events,
        )
    )
    wave8_saudi_rashidi_integration_validation = (
        validate_wave8_saudi_rashidi_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_saudi_rashidi_existing_events,
        )
    )
    wave8_yaqui_integration_validation = (
        validate_wave8_yaqui_integration_dispositions(
            hced,
            iwbd_candidates,
            wave8_yaqui_existing_events,
        )
    )
    wave8_haiti_regimes_integration_validation = (
        validate_wave8_haiti_regimes_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_haiti_regimes_existing_events,
                *wave8_haiti_regimes_events,
            ],
        )
    )
    wave8_zulu_forces_integration_validation = (
        validate_wave8_zulu_forces_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_zulu_forces_existing_events,
                *wave8_zulu_forces_events,
            ],
        )
    )
    wave8_montenegro_1796_integration_validation = (
        validate_wave8_montenegro_1796_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_montenegro_1796_existing_events,
                *wave8_montenegro_1796_events,
            ],
        )
    )
    wave8_bohemia_integration_validation = (
        validate_wave8_bohemia_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_bohemia_existing_events, *wave8_bohemia_events],
        )
    )
    wave8_spanish_liberals_integration_validation = (
        validate_wave8_spanish_liberals_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_spanish_liberals_existing_events,
                *wave8_spanish_liberals_events,
            ],
        )
    )
    wave8_oran_integration_validation = (
        validate_wave8_oran_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_oran_existing_events, *wave8_oran_events],
        )
    )
    wave8_cheyenne_dog_soldiers_integration_validation = (
        validate_wave8_cheyenne_dog_soldiers_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_cheyenne_dog_soldiers_existing_events,
                *wave8_cheyenne_dog_soldiers_events,
            ],
        )
    )
    wave8_achea_integration_validation = (
        validate_wave8_achea_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_achea_existing_events, *wave8_achea_events],
        )
    )
    wave8_kievan_rus_integration_validation = (
        validate_wave8_kievan_rus_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_kievan_rus_existing_events, *wave8_kievan_rus_events],
        )
    )
    wave8_carnatic_integration_validation = (
        validate_wave8_carnatic_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_carnatic_existing_events, *wave8_carnatic_events],
        )
    )
    wave8_goguryeo_integration_validation = (
        validate_wave8_goguryeo_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_goguryeo_existing_events, *wave8_goguryeo_events],
        )
    )
    wave8_fln_integration_validation = validate_wave8_fln_integration_dispositions(
        hced,
        iwbd_candidates,
        [*wave8_fln_existing_events, *wave8_fln_events],
    )
    wave8_sindh_integration_validation = (
        validate_wave8_sindh_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_sindh_existing_events, *wave8_sindh_events],
        )
    )
    wave8_oman_integration_validation = (
        validate_wave8_oman_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_oman_existing_events, *wave8_oman_events],
        )
    )
    wave8_irish_civil_war_integration_validation = (
        validate_wave8_irish_civil_war_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_irish_civil_war_existing_events,
                *wave8_irish_civil_war_events,
            ],
        )
    )
    wave8_bannock_sheepeater_integration_validation = (
        validate_wave8_bannock_sheepeater_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_bannock_sheepeater_existing_events,
                *wave8_bannock_sheepeater_events,
            ],
        )
    )
    wave8_catholic_rebels_integration_validation = (
        validate_wave8_catholic_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_catholic_rebels_existing_events,
                *wave8_catholic_rebels_events,
            ],
        )
    )
    wave8_macedon_integration_validation = (
        validate_wave8_macedon_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_macedon_existing_events, *wave8_macedon_events],
        )
    )
    wave8_uzbeks_integration_validation = (
        validate_wave8_uzbeks_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_uzbeks_existing_events, *wave8_uzbeks_events],
        )
    )
    wave8_etruria_integration_validation = (
        validate_wave8_etruria_integration_dispositions(
            hced,
            iwbd_candidates,
            [*wave8_etruria_existing_events, *wave8_etruria_events],
        )
    )
    iwd_parent_ids = {
        str(candidate.get("parent_war_id"))
        for candidate in iwd_candidates
        if candidate.get("parent_war_id") is not None
    }
    iwbd_promotion = promote_iwbd_battles(
        iwbd_candidates,
        curated_seed_keys,
        hced_event_keys,
        resolve_iwd_label,
        hced_cluster_spans,
        iwd_parent_ids,
        curated_exclusions=EFFECTIVE_IWBD_CURATED_EXCLUSIONS,
        reviewed_identity_bindings=EFFECTIVE_IWBD_REVIEWED_IDENTITY_BINDINGS,
        validated_source_contracts=WAVE6_IWBD_VALIDATED_SOURCE_CONTRACTS,
        reviewed_identity_cohorts=EFFECTIVE_IWBD_REVIEWED_IDENTITY_COHORTS,
        resolve_reviewed_id=resolve_reviewed_identity,
        require_complete_reviewed_identity_cohorts=True,
    )
    iwbd_events: list[dict[str, Any]] = iwbd_promotion["events"]
    iwbd_rejections: Counter[str] = iwbd_promotion["rejections"]
    for polity in iwbd_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)
    wave8_chadian_rebels_integration_validation = (
        validate_wave8_chadian_rebels_integration_dispositions(
            hced,
            iwbd_candidates,
            [
                *wave8_chadian_rebels_existing_events,
                *wave8_chadian_rebels_events,
                *iwbd_events,
            ],
            wave8_taliban_al_qaeda_ucdp_rows,
        )
    )

    # UCDP conflict-termination episodes: the strategic-layer promotion path.
    # The promoted-war index (curated seed wars plus IWD parents) drives the
    # entity-and-year duplicate gate so an episode already represented in the
    # ledger is never rated twice.
    ucdp_conflict_path = review / "ucdp-termination-conflict-candidates.jsonl"
    ucdp_dyad_path = review / "ucdp-termination-dyad-candidates.jsonl"
    ucdp_conflict_rows = (
        read_jsonl(ucdp_conflict_path) if ucdp_conflict_path.exists() else []
    )
    ucdp_dyad_rows = read_jsonl(ucdp_dyad_path) if ucdp_dyad_path.exists() else []
    promoted_war_index = [
        (
            str(event["id"]),
            event.get("cluster_id"),
            int(event["year"]),
            int(event.get("end_year", event["year"])),
            frozenset(
                str(participant["entity_id"]) for participant in event["participants"]
            ),
            {
                str(participant["entity_id"]): str(participant.get("termination", ""))
                for participant in event["participants"]
            },
        )
        for event in (*seed_events, *iwd_events)
        if event.get("event_type") == "war"
    ]
    ucdp_promotion = promote_ucdp_termination_episodes(
        ucdp_conflict_rows,
        ucdp_dyad_rows,
        promoted_war_index,
        lambda name, gwno, low_year, high_year: resolve_ucdp_party(
            name, gwno, low_year, high_year, label_context
        ),
    )
    ucdp_events: list[dict[str, Any]] = ucdp_promotion["events"]
    ucdp_rejections: Counter[str] = ucdp_promotion["rejections"]
    for polity in ucdp_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)

    sources_by_id = {str(source["id"]): source for source in sources}
    for source in (
        {
            "id": "hced_dataset",
            "title": "Historical Conflict Event Dataset (HCED), version 5.0 / data v3",
            "url": "https://doi.org/10.7910/DVN/6ZFC0V",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "hced",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "hced_seshat_crosswalk",
            "title": "HCED-to-Seshat polity crosswalk",
            "url": "https://dataverse.harvard.edu/api/access/datafile/11018172?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "identity_crosswalk",
            "accessed": "2026-07-13",
            "source_family_id": "hced_seshat_crosswalk_file_11018172",
            "evidence_roles": ["identity_crosswalk"],
        },
        {
            "id": "cliopatria_v020",
            "title": "Cliopatria historical polity registry v0.2.0",
            "url": "https://doi.org/10.5281/zenodo.20274630",
            "publisher": "Seshat Global History Databank / Zenodo",
            "license": "CC-BY-4.0",
            "source_type": "historical_polity_registry",
            "accessed": "2026-07-13",
            "source_family_id": "cliopatria_v0_2_0",
            "evidence_roles": ["identity_registry"],
        },
        {
            "id": "iwd_dataset",
            "title": "Interstate War Data v1.21",
            "url": "https://doi.org/10.7910/DVN/WGS1YX",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "iwd",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "iwbd_dataset",
            "title": "Interstate War Battle dataset (IWBD)",
            "url": "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "iwbd",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "ucdp_termination_conflict",
            "title": "UCDP Conflict Termination Dataset v4-2024, conflict level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "ucdp_conflict_termination",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "ucdp_termination_dyad",
            "title": "UCDP Conflict Termination Dataset v4-2024, dyad level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Dyad.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "ucdp_conflict_termination",
            "evidence_roles": ["outcome_consistency_crosscheck"],
        },
    ):
        sources_by_id[source["id"]] = source

    install_wave6_sources(sources_by_id)
    install_wave7_root_sources(sources_by_id)
    install_wave7_central_sources(sources_by_id)
    install_wave7_central_pass2_sources(sources_by_id)
    install_wave7_global_sources(sources_by_id)
    install_wave7_west_sources(sources_by_id)
    install_wave8_african_states_sources(sources_by_id)
    install_wave8_new_zealand_sources(sources_by_id)
    install_wave8_north_america_sources(sources_by_id)
    install_wave8_polish_audit_sources(sources_by_id)
    install_wave8_xhosa_sources(sources_by_id)
    install_wave8_namibia_resistance_sources(sources_by_id)
    install_wave8_first_saudi_sources(sources_by_id)
    install_wave8_early_states_sources(sources_by_id)
    install_wave8_judean_revolts_sources(sources_by_id)
    install_wave8_canadian_resistance_sources(sources_by_id)
    install_wave8_wales_sources(sources_by_id)
    install_wave8_cossack_sources(sources_by_id)
    install_wave8_fast17_sources(sources_by_id)
    install_wave8_naples_sources(sources_by_id)
    install_wave8_somali_irish_sa_sources(sources_by_id)
    install_wave8_argentine_independence_sources(sources_by_id)
    install_wave8_ecuador_independence_sources(sources_by_id)
    install_wave8_comanche_sources(sources_by_id)
    install_wave8_garibaldi_sources(sources_by_id)
    install_wave8_algiers_cheyenne_sources(sources_by_id)
    install_wave8_dagestan_sources(sources_by_id)
    install_wave8_irish_history_sources(sources_by_id)
    install_wave8_muslim_forces_sources(sources_by_id)
    install_wave8_moros_sources(sources_by_id)
    install_wave8_manchus_sources(sources_by_id)
    install_wave8_peruvian_rebels_sources(sources_by_id)
    install_wave8_germany_sources(sources_by_id)
    install_wave8_seljuks_sources(sources_by_id)
    install_wave8_danish_vikings_sources(sources_by_id)
    install_wave8_epirus_sources(sources_by_id)
    install_wave8_savoy_sources(sources_by_id)
    install_wave8_nez_perce_sources(sources_by_id)
    install_wave8_dacia_sources(sources_by_id)
    install_wave8_cherokee_sources(sources_by_id)
    install_wave8_druze_rebels_sources(sources_by_id)
    install_wave8_insubrian_gauls_sources(sources_by_id)
    install_wave8_kiowa_sources(sources_by_id)
    install_wave8_uzbekistan_sources(sources_by_id)
    install_wave8_vietnam_sources(sources_by_id)
    install_wave8_hussites_sources(sources_by_id)
    install_wave8_livonian_order_sources(sources_by_id)
    install_wave8_satsuma_sources(sources_by_id)
    install_wave8_rajputs_sources(sources_by_id)
    install_wave8_mamluk_egypt_sources(sources_by_id)
    install_wave8_rebel_barons_sources(sources_by_id)
    install_wave8_thebes_sources(sources_by_id)
    install_wave8_alemanni_sources(sources_by_id)
    install_wave8_madagascar_sources(sources_by_id)
    install_wave8_kickapoo_sources(sources_by_id)
    install_wave8_lordship_isles_sources(sources_by_id)
    install_wave8_armenia_sources(sources_by_id)
    install_wave8_comanches_sources(sources_by_id)
    install_wave8_sikh_punjab_sources(sources_by_id)
    install_wave8_eritrea_sources(sources_by_id)
    install_wave8_flanders_sources(sources_by_id)
    install_wave8_france_bavaria_sources(sources_by_id)
    install_wave8_eritrean_rebels_sources(sources_by_id)
    install_wave8_inca_rebels_sources(sources_by_id)
    install_wave8_haitian_rebels_sources(sources_by_id)
    install_wave8_kingdom_kandy_sources(sources_by_id)
    install_wave8_hospitallers_sources(sources_by_id)
    install_wave8_murids_sources(sources_by_id)
    install_wave8_punjabi_sikhs_sources(sources_by_id)
    install_wave8_modoc_sources(sources_by_id)
    install_wave8_sauk_sources(sources_by_id)
    install_wave8_ute_sources(sources_by_id)
    install_wave8_yakima_sources(sources_by_id)
    install_wave8_taliban_al_qaeda_sources(sources_by_id)
    install_wave8_french_religious_forces_sources(sources_by_id)
    install_wave8_chadian_rebels_sources(sources_by_id)
    install_wave8_saudi_rashidi_sources(sources_by_id)
    install_wave8_yaqui_sources(sources_by_id)
    install_wave8_egypt_forces_sources(sources_by_id)
    install_wave8_haiti_regimes_sources(sources_by_id)
    install_wave8_zulu_forces_sources(sources_by_id)
    install_wave8_montenegro_1796_sources(sources_by_id)
    install_wave8_bohemia_sources(sources_by_id)
    install_wave8_spanish_liberals_sources(sources_by_id)
    install_wave8_achea_sources(sources_by_id)
    install_wave8_oran_sources(sources_by_id)
    install_wave8_cheyenne_dog_soldiers_sources(sources_by_id)
    install_wave8_libya_sources(sources_by_id)
    install_wave8_kievan_rus_sources(sources_by_id)
    install_wave8_carnatic_sources(sources_by_id)
    install_wave8_goguryeo_sources(sources_by_id)
    install_wave8_fln_sources(sources_by_id)
    install_wave8_sindh_sources(sources_by_id)
    install_wave8_oman_sources(sources_by_id)
    install_wave8_irish_civil_war_sources(sources_by_id)
    install_wave8_bannock_sheepeater_sources(sources_by_id)
    install_wave8_catholic_rebels_sources(sources_by_id)
    install_wave8_macedon_sources(sources_by_id)
    install_wave8_uzbeks_sources(sources_by_id)
    install_wave8_etruria_sources(sources_by_id)

    all_events = [
        *seed_events,
        *source_events,
        *iwd_events,
        *label_events,
        *wave6_events,
        *wave7_root_events,
        *wave7_central_events,
        *wave7_central_pass2_events,
        *wave7_global_events,
        *wave7_west_events,
        *wave8_african_states_events,
        *wave8_new_zealand_events,
        *wave8_north_america_events,
        *wave8_xhosa_events,
        *wave8_polish_audit_events,
        *wave8_namibia_resistance_events,
        *wave8_first_saudi_events,
        *wave8_early_states_events,
        *wave8_judean_revolts_events,
        *wave8_canadian_resistance_events,
        *wave8_wales_events,
        *wave8_cossack_events,
        *wave8_fast17_events,
        *wave8_naples_events,
        *wave8_somali_irish_sa_events,
        *wave8_argentine_independence_events,
        *wave8_ecuador_independence_events,
        *wave8_comanche_events,
        *wave8_garibaldi_events,
        *wave8_algiers_cheyenne_events,
        *wave8_dagestan_events,
        *wave8_irish_history_events,
        *wave8_muslim_forces_events,
        *wave8_moros_events,
        *wave8_manchus_events,
        *wave8_peruvian_rebels_events,
        *wave8_germany_events,
        *wave8_seljuks_events,
        *wave8_danish_vikings_events,
        *wave8_epirus_events,
        *wave8_savoy_events,
        *wave8_nez_perce_events,
        *wave8_dacia_events,
        *wave8_cherokee_events,
        *wave8_druze_rebels_events,
        *wave8_insubrian_gauls_events,
        *wave8_kiowa_events,
        *wave8_uzbekistan_events,
        *wave8_vietnam_events,
        *wave8_hussites_events,
        *wave8_livonian_order_events,
        *wave8_satsuma_events,
        *wave8_rajputs_events,
        *wave8_mamluk_egypt_events,
        *wave8_rebel_barons_events,
        *wave8_thebes_events,
        *wave8_alemanni_events,
        *wave8_madagascar_events,
        *wave8_kickapoo_events,
        *wave8_lordship_isles_events,
        *wave8_armenia_events,
        *wave8_comanches_events,
        *wave8_sikh_punjab_events,
        *wave8_eritrea_events,
        *wave8_flanders_events,
        *wave8_france_bavaria_events,
        *wave8_eritrean_rebels_events,
        *wave8_inca_rebels_events,
        *wave8_haitian_rebels_events,
        *wave8_kingdom_kandy_events,
        *wave8_hospitallers_events,
        *wave8_murids_events,
        *wave8_punjabi_sikhs_events,
        *wave8_modoc_events,
        *wave8_sauk_events,
        *wave8_ute_events,
        *wave8_yakima_events,
        *wave8_taliban_al_qaeda_events,
        *wave8_french_religious_forces_events,
        *wave8_chadian_rebels_events,
        *wave8_saudi_rashidi_events,
        *wave8_yaqui_events,
        *wave8_egypt_forces_events,
        *wave8_haiti_regimes_events,
        *wave8_zulu_forces_events,
        *wave8_montenegro_1796_events,
        *wave8_bohemia_events,
        *wave8_spanish_liberals_events,
        *wave8_achea_events,
        *wave8_oran_events,
        *wave8_cheyenne_dog_soldiers_events,
        *wave8_libya_events,
        *wave8_kievan_rus_events,
        *wave8_carnatic_events,
        *wave8_goguryeo_events,
        *wave8_fln_events,
        *wave8_sindh_events,
        *wave8_oman_events,
        *wave8_irish_civil_war_events,
        *wave8_bannock_sheepeater_events,
        *wave8_catholic_rebels_events,
        *wave8_macedon_events,
        *wave8_uzbeks_events,
        *wave8_etruria_events,
        *iwbd_events,
        *ucdp_events,
    ]
    # This audit is pinned from the committed release ledger, so validate the
    # fully assembled ledger rather than the mid-chain duplicate-detection
    # view that precedes later Wave 8 lanes such as Macedon.
    wave8_libya_integration_validation = (
        validate_wave8_libya_integration_dispositions(
            hced,
            iwbd_candidates,
            all_events,
        )
    )
    wave8_egypt_forces_identity_validation = (
        validate_wave8_egypt_forces_identity_boundaries(
            seed_entities,
            release_entities,
            seed_events,
            all_events,
        )
    )
    wave8_egypt_forces_integration_validation = (
        validate_wave8_egypt_forces_integration_dispositions(
            hced,
            iwbd_candidates,
            all_events,
            iwd_candidates,
        )
    )
    hced_events = [
        *source_events,
        *label_events,
        *wave6_events,
        *wave7_root_events,
        *wave7_central_events,
        *wave7_central_pass2_events,
        *wave7_global_events,
        *wave7_west_events,
        *wave8_african_states_events,
        *wave8_new_zealand_events,
        *wave8_north_america_events,
        *wave8_xhosa_events,
        *wave8_polish_audit_events,
        *wave8_namibia_resistance_events,
        *wave8_first_saudi_events,
        *wave8_early_states_events,
        *wave8_judean_revolts_events,
        *wave8_canadian_resistance_events,
        *wave8_wales_events,
        *wave8_cossack_events,
        *wave8_fast17_events,
        *wave8_naples_events,
        *wave8_somali_irish_sa_events,
        *wave8_argentine_independence_events,
        *wave8_ecuador_independence_events,
        *wave8_comanche_events,
        *wave8_garibaldi_events,
        *wave8_algiers_cheyenne_events,
        *wave8_dagestan_events,
        *wave8_irish_history_events,
        *wave8_muslim_forces_events,
        *wave8_moros_events,
        *wave8_manchus_events,
        *wave8_peruvian_rebels_events,
        *wave8_germany_events,
        *wave8_seljuks_events,
        *wave8_danish_vikings_events,
        *wave8_epirus_events,
        *wave8_savoy_events,
        *wave8_nez_perce_events,
        *wave8_dacia_events,
        *wave8_cherokee_events,
        *wave8_druze_rebels_events,
        *wave8_insubrian_gauls_events,
        *wave8_kiowa_events,
        *wave8_uzbekistan_events,
        *wave8_vietnam_events,
        *wave8_hussites_events,
        *wave8_livonian_order_events,
        *wave8_satsuma_events,
        *wave8_rajputs_events,
        *wave8_mamluk_egypt_events,
        *wave8_rebel_barons_events,
        *wave8_thebes_events,
        *wave8_alemanni_events,
        *wave8_madagascar_events,
        *wave8_kickapoo_events,
        *wave8_lordship_isles_events,
        *wave8_armenia_events,
        *wave8_comanches_events,
        *wave8_sikh_punjab_events,
        *wave8_eritrea_events,
        *wave8_flanders_events,
        *wave8_france_bavaria_events,
        *wave8_eritrean_rebels_events,
        *wave8_inca_rebels_events,
        *wave8_haitian_rebels_events,
        *wave8_kingdom_kandy_events,
        *wave8_hospitallers_events,
        *wave8_murids_events,
        *wave8_punjabi_sikhs_events,
        *wave8_modoc_events,
        *wave8_sauk_events,
        *wave8_ute_events,
        *wave8_yakima_events,
        *wave8_taliban_al_qaeda_events,
        *wave8_french_religious_forces_events,
        *wave8_chadian_rebels_events,
        *wave8_saudi_rashidi_events,
        *wave8_yaqui_events,
        *wave8_egypt_forces_events,
        *wave8_haiti_regimes_events,
        *wave8_zulu_forces_events,
        *wave8_montenegro_1796_events,
        *wave8_bohemia_events,
        *wave8_spanish_liberals_events,
        *wave8_achea_events,
        *wave8_oran_events,
        *wave8_cheyenne_dog_soldiers_events,
        *wave8_libya_events,
        *wave8_kievan_rus_events,
        *wave8_carnatic_events,
        *wave8_goguryeo_events,
        *wave8_fln_events,
        *wave8_sindh_events,
        *wave8_oman_events,
        *wave8_irish_civil_war_events,
        *wave8_bannock_sheepeater_events,
        *wave8_catholic_rebels_events,
        *wave8_macedon_events,
        *wave8_uzbeks_events,
        *wave8_etruria_events,
    ]
    hced_location_coverage = _validate_hced_location_release(
        hced_events,
        hced_candidates_by_id,
        reviewed_candidate_ids=(
            WAVE6_HCED_CONTRACT_IDS
            | WAVE7_ROOT_CONTRACT_IDS
            | WAVE7_CENTRAL_PROMOTION_IDS
            | WAVE7_CENTRAL_PASS2_PROMOTION_IDS
            | WAVE7_GLOBAL_HCED_CONTRACT_IDS
            | WAVE7_WEST_HCED_CONTRACT_IDS
            | WAVE8_AFRICAN_STATES_CONTRACT_IDS
            | WAVE8_NEW_ZEALAND_CONTRACT_IDS
            | WAVE8_NORTH_AMERICA_CONTRACT_IDS
            | WAVE8_POLISH_AUDIT_CONTRACT_IDS
            | WAVE8_XHOSA_CONTRACT_IDS
            | WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS
            | WAVE8_FIRST_SAUDI_CONTRACT_IDS
            | WAVE8_EARLY_STATES_CONTRACT_IDS
            | WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS
            | WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS
            | WAVE8_WALES_CONTRACT_IDS
            | WAVE8_COSSACK_CONTRACT_IDS
            | WAVE8_FAST17_CONTRACT_IDS
            | WAVE8_NAPLES_CONTRACT_IDS
            | WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS
            | WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS
            | WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS
            | WAVE8_COMANCHE_CONTRACT_IDS
            | WAVE8_GARIBALDI_CONTRACT_IDS
            | WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
            | WAVE8_DAGESTAN_CONTRACT_IDS
            | WAVE8_IRISH_HISTORY_CONTRACT_IDS
            | WAVE8_MUSLIM_FORCES_CONTRACT_IDS
            | WAVE8_MOROS_CONTRACT_IDS
            | WAVE8_MANCHUS_CONTRACT_IDS
            | WAVE8_PERUVIAN_REBELS_CONTRACT_IDS
            | WAVE8_GERMANY_CONTRACT_IDS
            | WAVE8_SELJUKS_CONTRACT_IDS
            | WAVE8_DANISH_VIKINGS_CONTRACT_IDS
            | WAVE8_EPIRUS_CONTRACT_IDS
            | WAVE8_SAVOY_CONTRACT_IDS
            | WAVE8_NEZ_PERCE_CONTRACT_IDS
            | WAVE8_DACIA_CONTRACT_IDS
            | WAVE8_CHEROKEE_CONTRACT_IDS
            | WAVE8_DRUZE_REBELS_CONTRACT_IDS
            | WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS
            | WAVE8_KIOWA_CONTRACT_IDS
            | WAVE8_UZBEKISTAN_CONTRACT_IDS
            | WAVE8_VIETNAM_CONTRACT_IDS
            | WAVE8_HUSSITES_CONTRACT_IDS
            | WAVE8_LIVONIAN_ORDER_CONTRACT_IDS
            | WAVE8_SATSUMA_CONTRACT_IDS
            | WAVE8_RAJPUTS_CONTRACT_IDS
            | WAVE8_MAMLUK_EGYPT_CONTRACT_IDS
            | WAVE8_REBEL_BARONS_CONTRACT_IDS
            | WAVE8_THEBES_CONTRACT_IDS
            | WAVE8_ALEMANNI_CONTRACT_IDS
            | WAVE8_MADAGASCAR_CONTRACT_IDS
            | WAVE8_KICKAPOO_CONTRACT_IDS
            | WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
            | WAVE8_ARMENIA_CONTRACT_IDS
            | WAVE8_COMANCHES_CONTRACT_IDS
            | WAVE8_SIKH_PUNJAB_CONTRACT_IDS
            | WAVE8_ERITREA_CONTRACT_IDS
            | WAVE8_FLANDERS_CONTRACT_IDS
            | WAVE8_FRANCE_BAVARIA_CONTRACT_IDS
            | WAVE8_ERITREAN_REBELS_CONTRACT_IDS
            | WAVE8_INCA_REBELS_CONTRACT_IDS
            | WAVE8_HAITIAN_REBELS_CONTRACT_IDS
            | WAVE8_KINGDOM_KANDY_CONTRACT_IDS
            | WAVE8_HOSPITALLERS_CONTRACT_IDS
            | WAVE8_MURIDS_CONTRACT_IDS
            | WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
            | WAVE8_MODOC_CONTRACT_IDS
            | WAVE8_SAUK_CONTRACT_IDS
            | WAVE8_UTE_CONTRACT_IDS
            | WAVE8_YAKIMA_CONTRACT_IDS
            | WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
            | WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
            | WAVE8_CHADIAN_REBELS_CONTRACT_IDS
            | WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
            | WAVE8_YAQUI_CONTRACT_IDS
            | WAVE8_EGYPT_FORCES_CONTRACT_IDS
            | WAVE8_HAITI_REGIMES_CONTRACT_IDS
            | WAVE8_ZULU_FORCES_CONTRACT_IDS
            | WAVE8_MONTENEGRO_1796_CONTRACT_IDS
            | WAVE8_BOHEMIA_CONTRACT_IDS
            | WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
            | WAVE8_ACHEA_CONTRACT_IDS
            | WAVE8_ORAN_CONTRACT_IDS
            | WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
            | WAVE8_LIBYA_CONTRACT_IDS
            | WAVE8_KIEVAN_RUS_CONTRACT_IDS
            | WAVE8_CARNATIC_CONTRACT_IDS
            | WAVE8_GOGURYEO_CONTRACT_IDS
            | WAVE8_FLN_CONTRACT_IDS
            | WAVE8_SINDH_CONTRACT_IDS
            | WAVE8_OMAN_CONTRACT_IDS
            | WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
            | WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
            | WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
            | WAVE8_MACEDON_CONTRACT_IDS
            | WAVE8_UZBEKS_CONTRACT_IDS
            | WAVE8_ETRURIA_CONTRACT_IDS
        ),
    )
    used_entity_ids = {
        str(participant["entity_id"])
        for event in all_events
        for participant in event["participants"]
    }
    release_entity_rows = sorted(
        release_entities.values(),
        key=lambda entity: (
            int(entity["start_year"]),
            str(entity["name"]),
            str(entity["id"]),
        ),
    )
    review_counts = _count_review_records(review)

    curated_release_entity_ids = {
        *map(lambda entity: str(entity["id"]), seed_entities),
        *map(lambda entity: str(entity["id"]), WAVE6_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE6_1800_2021_ENTITY_OVERRIDES),
        *map(lambda entity: str(entity["id"]), WAVE7_ROOT_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE7_CENTRAL_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE7_CENTRAL_PASS2_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE7_GLOBAL_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE7_WEST_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_AFRICAN_STATES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_NEW_ZEALAND_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_NORTH_AMERICA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_POLISH_AUDIT_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_XHOSA_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_NAMIBIA_RESISTANCE_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_FIRST_SAUDI_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_EARLY_STATES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_JUDEAN_REVOLTS_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_CANADIAN_RESISTANCE_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_WALES_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_COSSACK_REBELLIONS_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_FAST17_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_NAPLES_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_SOMALI_IRISH_SA_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_ECUADOR_INDEPENDENCE_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_COMANCHE_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_GARIBALDI_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_ALGIERS_CHEYENNE_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_DAGESTAN_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_IRISH_HISTORY_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MUSLIM_FORCES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MOROS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MANCHUS_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_PERUVIAN_REBELS_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_GERMANY_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SELJUKS_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_DANISH_VIKINGS_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_EPIRUS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SAVOY_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_NEZ_PERCE_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_DACIA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_CHEROKEE_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_DRUZE_REBELS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_INSUBRIAN_GAULS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_KIOWA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_UZBEKISTAN_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_VIETNAM_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_HUSSITES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_LIVONIAN_ORDER_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SATSUMA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_RAJPUTS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MAMLUK_EGYPT_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_REBEL_BARONS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_THEBES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ALEMANNI_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MADAGASCAR_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_KICKAPOO_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_LORDSHIP_ISLES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ARMENIA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_COMANCHES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SIKH_PUNJAB_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ERITREA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_FLANDERS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_FRANCE_BAVARIA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ERITREAN_REBELS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_INCA_REBELS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_HAITIAN_REBELS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_KINGDOM_KANDY_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_HOSPITALLERS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MURIDS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_PUNJABI_SIKHS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_MODOC_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SAUK_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_UTE_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_YAKIMA_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_TALIBAN_AL_QAEDA_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_CHADIAN_REBELS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SAUDI_RASHIDI_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_YAQUI_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_EGYPT_FORCES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_HAITI_REGIMES_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ZULU_FORCES_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_MONTENEGRO_1796_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_BOHEMIA_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_SPANISH_LIBERALS_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_LIBYA_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_KIEVAN_RUS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_CARNATIC_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_GOGURYEO_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_FLN_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_SINDH_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_OMAN_ENTITIES),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_IRISH_CIVIL_WAR_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_BANNOCK_SHEEPEATER_ENTITIES,
        ),
        *map(
            lambda entity: str(entity["id"]),
            WAVE8_CATHOLIC_REBELS_ENTITIES,
        ),
        *map(lambda entity: str(entity["id"]), WAVE8_MACEDON_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_UZBEKS_ENTITIES),
        *map(lambda entity: str(entity["id"]), WAVE8_ETRURIA_ENTITIES),
    }
    registry_entities: dict[str, dict[str, Any]] = {}
    for entity in release_entity_rows:
        entity_id = str(entity["id"])
        is_curated = entity_id in curated_release_entity_ids
        registry_entities[entity_id] = {
            "id": entity_id,
            "name": str(entity["name"]),
            "kind": str(entity.get("kind") or "polity"),
            "start_year": int(entity["start_year"]),
            "end_year": (
                int(entity["end_year"]) if entity.get("end_year") is not None else None
            ),
            "status": (
                "rated"
                if is_curated and entity_id in used_entity_ids
                else "unrated"
                if is_curated or entity_id not in used_entity_ids
                else "provisional"
            ),
            "identity_status": "curated" if is_curated else "source_candidate",
            "region": str(entity.get("region") or "Unclassified"),
        }
    used_candidate_ids = {
        str(candidate["candidate_id"]) for candidate in candidate_by_release_id.values()
    }
    for candidate in polities:
        entity_id = _candidate_entity_id(candidate)
        global_replacements = wave7_global_registry_supersessions.get(
            str(candidate.get("candidate_id"))
        )
        if global_replacements:
            contract = WAVE7_GLOBAL_SUPERSESSIONS[str(candidate["candidate_id"])]
            if str(contract["source_entity_id"]) != entity_id:
                raise ValueError(
                    f"Wave 7 Global supersession source ID drift: {entity_id}"
                )
            if entity_id in used_entity_ids:
                raise ValueError(
                    f"Wave 7 Global superseded identity remains rated: {entity_id}"
                )
            replacement_rows = []
            for replacement_id in global_replacements:
                replacement = registry_entities.get(replacement_id)
                if replacement is None:
                    raise ValueError(
                        "Wave 7 Global registry supersession target is missing: "
                        f"{entity_id} -> {replacement_id}"
                    )
                replacement_rows.append(replacement)
            candidate_low = int(candidate["start_year"])
            candidate_high = int(candidate["end_year"])
            if any(
                not any(
                    int(replacement["start_year"]) <= year
                    and (
                        replacement.get("end_year") is None
                        or int(replacement["end_year"]) >= year
                    )
                    for replacement in replacement_rows
                )
                for year in range(candidate_low, candidate_high + 1)
            ):
                raise ValueError(
                    f"Wave 7 Global supersession leaves a temporal gap for {entity_id}"
                )
            superseded_row = {
                "id": entity_id,
                "name": str(candidate["canonical_name_candidate"]),
                "kind": _infer_kind(str(candidate["canonical_name_candidate"])),
                "start_year": candidate_low,
                "end_year": candidate_high,
                "status": "unrated",
                "identity_status": "superseded",
                "superseded_by_ids": list(global_replacements),
                "supersession_note": str(contract["boundary_note"]),
                "coverage_discontinuous": len(
                    candidate.get("temporal_coverage_groups", [])
                )
                > 1,
                "region": "Unclassified",
            }
            if len(global_replacements) == 1:
                superseded_row["superseded_by"] = global_replacements[0]
            registry_entities[entity_id] = superseded_row
            continue
        superseded_by = WAVE6_PRE1500_REGISTRY_SUPERSESSIONS.get(entity_id)
        if superseded_by:
            replacement = registry_entities.get(superseded_by)
            if replacement is None:
                raise ValueError(
                    f"registry supersession target is missing: {entity_id} -> "
                    f"{superseded_by}"
                )
            if normalize_label(
                candidate.get("canonical_name_candidate")
            ) != normalize_label(
                replacement.get("name")
            ) or not _candidate_overlaps_entity(candidate, replacement):
                raise ValueError(
                    f"registry supersession identity drift: {entity_id} -> "
                    f"{superseded_by}"
                )
            registry_entities[entity_id] = {
                "id": entity_id,
                "name": str(candidate["canonical_name_candidate"]),
                "kind": _infer_kind(str(candidate["canonical_name_candidate"])),
                "start_year": int(candidate["start_year"]),
                "end_year": int(candidate["end_year"]),
                "status": "unrated",
                "identity_status": "superseded",
                "superseded_by": superseded_by,
                "coverage_discontinuous": len(
                    candidate.get("temporal_coverage_groups", [])
                )
                > 1,
                "region": "Unclassified",
            }
            continue
        if entity_id in registry_entities:
            continue
        mapped_seed = _candidate_policy_seed(candidate, seed_by_id)
        if not mapped_seed:
            name_matches = seed_label_index.get(
                normalize_label(candidate.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                # A name match alone must not bridge eras: a same-named polity
                # from a different century keeps its own registry row.
                if named_entity and _candidate_overlaps_entity(candidate, named_entity):
                    mapped_seed = named_seed
        if mapped_seed and mapped_seed in registry_entities:
            continue
        registry_entities[entity_id] = {
            "id": entity_id,
            "name": str(candidate["canonical_name_candidate"]),
            "kind": _infer_kind(str(candidate["canonical_name_candidate"])),
            "start_year": int(candidate["start_year"]),
            "end_year": int(candidate["end_year"]),
            "status": (
                "provisional"
                if str(candidate["candidate_id"]) in used_candidate_ids
                else "unrated"
            ),
            "identity_status": "source_candidate",
            "coverage_discontinuous": len(candidate.get("temporal_coverage_groups", []))
            > 1,
            "region": "Unclassified",
        }

    registry_rows = sorted(
        registry_entities.values(),
        key=lambda entity: (
            str(entity["name"]),
            int(entity["start_year"]),
            str(entity["id"]),
        ),
    )
    staged_source_records = sum(review_counts.values())
    identity_queue_names = {
        "cliopatria-entity-candidates.jsonl",
        "ucdp-actor-26.1-candidates.jsonl",
    }
    unresolved_event_candidates = max(
        0,
        sum(
            count
            for name, count in review_counts.items()
            if name not in identity_queue_names
        )
        - len(source_events)
        - len(label_events)
        - len(wave6_events)
        - len(wave7_root_events)
        - len(wave7_central_events)
        - len(wave7_central_pass2_events)
        - len(wave7_global_events)
        - len(wave7_west_events)
        - len(wave8_african_states_events)
        - len(wave8_new_zealand_events)
        - len(wave8_north_america_events)
        - len(wave8_xhosa_events)
        - len(wave8_polish_audit_events)
        - len(wave8_namibia_resistance_events)
        - len(wave8_first_saudi_events)
        - len(wave8_early_states_events)
        - len(wave8_judean_revolts_events)
        - len(wave8_canadian_resistance_events)
        - len(wave8_wales_events)
        - len(wave8_cossack_events)
        - len(wave8_fast17_events)
        - len(wave8_naples_events)
        - len(wave8_somali_irish_sa_events)
        - len(wave8_argentine_independence_events)
        - len(wave8_ecuador_independence_events)
        - len(wave8_comanche_events)
        - len(wave8_garibaldi_events)
        - len(wave8_algiers_cheyenne_events)
        - len(wave8_dagestan_events)
        - len(wave8_irish_history_events)
        - len(wave8_muslim_forces_events)
        - len(wave8_moros_events)
        - len(wave8_manchus_events)
        - len(wave8_peruvian_rebels_events)
        - len(wave8_germany_events)
        - len(wave8_seljuks_events)
        - len(wave8_danish_vikings_events)
        - len(wave8_epirus_events)
        - len(wave8_savoy_events)
        - len(wave8_nez_perce_events)
        - len(wave8_dacia_events)
        - len(wave8_cherokee_events)
        - len(wave8_druze_rebels_events)
        - len(wave8_insubrian_gauls_events)
        - len(wave8_kiowa_events)
        - len(wave8_uzbekistan_events)
        - len(wave8_vietnam_events)
        - len(wave8_hussites_events)
        - len(wave8_livonian_order_events)
        - len(wave8_satsuma_events)
        - len(wave8_rajputs_events)
        - len(wave8_mamluk_egypt_events)
        - len(wave8_rebel_barons_events)
        - len(wave8_thebes_events)
        - len(wave8_alemanni_events)
        - len(wave8_madagascar_events)
        - len(wave8_kickapoo_events)
        - len(wave8_lordship_isles_events)
        - len(wave8_armenia_events)
        - len(wave8_comanches_events)
        - len(wave8_sikh_punjab_events)
        - len(wave8_eritrea_events)
        - len(wave8_flanders_events)
        - len(wave8_france_bavaria_events)
        - len(wave8_eritrean_rebels_events)
        - len(wave8_inca_rebels_events)
        - len(wave8_haitian_rebels_events)
        - len(wave8_kingdom_kandy_events)
        - len(wave8_hospitallers_events)
        - len(wave8_murids_events)
        - len(wave8_punjabi_sikhs_events)
        - len(wave8_modoc_events)
        - len(wave8_sauk_events)
        - len(wave8_ute_events)
        - len(wave8_yakima_events)
        - len(wave8_taliban_al_qaeda_events)
        - len(wave8_french_religious_forces_events)
        - len(wave8_chadian_rebels_events)
        - len(wave8_saudi_rashidi_events)
        - len(wave8_yaqui_events)
        - len(wave8_egypt_forces_events)
        - len(wave8_haiti_regimes_events)
        - len(wave8_zulu_forces_events)
        - len(wave8_montenegro_1796_events)
        - len(wave8_bohemia_events)
        - len(wave8_spanish_liberals_events)
        - len(wave8_achea_events)
        - len(wave8_oran_events)
        - len(wave8_cheyenne_dog_soldiers_events)
        - len(wave8_libya_events)
        - len(wave8_kievan_rus_events)
        - len(wave8_carnatic_events)
        - len(wave8_goguryeo_events)
        - len(wave8_fln_events)
        - len(wave8_sindh_events)
        - len(wave8_oman_events)
        - len(wave8_irish_civil_war_events)
        - len(wave8_bannock_sheepeater_events)
        - len(wave8_catholic_rebels_events)
        - len(wave8_macedon_events)
        - len(wave8_uzbeks_events)
        - len(wave8_etruria_events)
        - len(iwbd_events)
        - len(ucdp_events)
        - iwd_aggregation["components_attached"],
    )
    latest_rated_event_year = max(int(event["end_year"]) for event in all_events)
    coverage = {
        "registry_polities": len(registry_rows),
        "rated_entities": len(used_entity_ids),
        "rated_events": len(all_events),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "latest_rated_event_year": latest_rated_event_year,
        "curated_seed_events": len(seed_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "candidate_keyed_wave6_hced_events": len(wave6_events),
        "candidate_keyed_wave7_root_hced_events": len(wave7_root_events),
        "candidate_keyed_wave7_central_hced_events": len(wave7_central_events),
        "candidate_keyed_wave7_central_pass2_hced_events": len(
            wave7_central_pass2_events
        ),
        "candidate_keyed_wave7_global_hced_events": len(wave7_global_events),
        "candidate_keyed_wave7_west_hced_events": len(wave7_west_events),
        "candidate_keyed_wave8_african_states_hced_events": len(
            wave8_african_states_events
        ),
        "candidate_keyed_wave8_new_zealand_hced_events": len(
            wave8_new_zealand_events
        ),
        "candidate_keyed_wave8_north_america_hced_events": len(
            wave8_north_america_events
        ),
        "candidate_keyed_wave8_xhosa_hced_events": len(wave8_xhosa_events),
        "candidate_keyed_wave8_polish_audit_hced_events": len(
            wave8_polish_audit_events
        ),
        "candidate_keyed_wave8_namibia_resistance_hced_events": len(
            wave8_namibia_resistance_events
        ),
        "candidate_keyed_wave8_first_saudi_hced_events": len(
            wave8_first_saudi_events
        ),
        "candidate_keyed_wave8_early_states_hced_events": len(
            wave8_early_states_events
        ),
        "candidate_keyed_wave8_judean_revolts_hced_events": len(
            wave8_judean_revolts_events
        ),
        "candidate_keyed_wave8_canadian_resistance_hced_events": len(
            wave8_canadian_resistance_events
        ),
        "candidate_keyed_wave8_wales_hced_events": len(wave8_wales_events),
        "candidate_keyed_wave8_cossack_hced_events": len(wave8_cossack_events),
        "candidate_keyed_wave8_fast17_hced_events": len(wave8_fast17_events),
        "candidate_keyed_wave8_naples_hced_events": len(wave8_naples_events),
        "candidate_keyed_wave8_somali_irish_sa_hced_events": len(
            wave8_somali_irish_sa_events
        ),
        "candidate_keyed_wave8_argentine_independence_hced_events": len(
            wave8_argentine_independence_events
        ),
        "candidate_keyed_wave8_ecuador_independence_hced_events": len(
            wave8_ecuador_independence_events
        ),
        "candidate_keyed_wave8_comanche_hced_events": len(wave8_comanche_events),
        "candidate_keyed_wave8_garibaldi_hced_events": len(wave8_garibaldi_events),
        "candidate_keyed_wave8_algiers_cheyenne_hced_events": len(
            wave8_algiers_cheyenne_events
        ),
        "candidate_keyed_wave8_dagestan_hced_events": len(wave8_dagestan_events),
        "candidate_keyed_wave8_irish_history_hced_events": len(
            wave8_irish_history_events
        ),
        "candidate_keyed_wave8_muslim_forces_hced_events": len(
            wave8_muslim_forces_events
        ),
        "candidate_keyed_wave8_moros_hced_events": len(wave8_moros_events),
        "candidate_keyed_wave8_manchus_hced_events": len(wave8_manchus_events),
        "candidate_keyed_wave8_peruvian_rebels_hced_events": len(
            wave8_peruvian_rebels_events
        ),
        "candidate_keyed_wave8_germany_hced_events": len(wave8_germany_events),
        "candidate_keyed_wave8_seljuks_hced_events": len(wave8_seljuks_events),
        "candidate_keyed_wave8_danish_vikings_hced_events": len(
            wave8_danish_vikings_events
        ),
        "candidate_keyed_wave8_epirus_hced_events": len(wave8_epirus_events),
        "candidate_keyed_wave8_savoy_hced_events": len(wave8_savoy_events),
        "candidate_keyed_wave8_nez_perce_hced_events": len(
            wave8_nez_perce_events
        ),
        "candidate_keyed_wave8_dacia_hced_events": len(wave8_dacia_events),
        "candidate_keyed_wave8_cherokee_hced_events": len(
            wave8_cherokee_events
        ),
        "candidate_keyed_wave8_druze_rebels_hced_events": len(
            wave8_druze_rebels_events
        ),
        "candidate_keyed_wave8_insubrian_gauls_hced_events": len(
            wave8_insubrian_gauls_events
        ),
        "candidate_keyed_wave8_kiowa_hced_events": len(wave8_kiowa_events),
        "candidate_keyed_wave8_uzbekistan_hced_events": len(
            wave8_uzbekistan_events
        ),
        "candidate_keyed_wave8_vietnam_hced_events": len(wave8_vietnam_events),
        "candidate_keyed_wave8_hussites_hced_events": len(wave8_hussites_events),
        "candidate_keyed_wave8_livonian_order_hced_events": len(
            wave8_livonian_order_events
        ),
        "candidate_keyed_wave8_satsuma_hced_events": len(wave8_satsuma_events),
        "candidate_keyed_wave8_rajputs_hced_events": len(wave8_rajputs_events),
        "candidate_keyed_wave8_mamluk_egypt_hced_events": len(
            wave8_mamluk_egypt_events
        ),
        "candidate_keyed_wave8_rebel_barons_hced_events": len(
            wave8_rebel_barons_events
        ),
        "candidate_keyed_wave8_thebes_hced_events": len(wave8_thebes_events),
        "candidate_keyed_wave8_alemanni_hced_events": len(wave8_alemanni_events),
        "candidate_keyed_wave8_madagascar_hced_events": len(
            wave8_madagascar_events
        ),
        "candidate_keyed_wave8_kickapoo_hced_events": len(wave8_kickapoo_events),
        "candidate_keyed_wave8_lordship_isles_hced_events": len(
            wave8_lordship_isles_events
        ),
        "candidate_keyed_wave8_armenia_hced_events": len(wave8_armenia_events),
        "candidate_keyed_wave8_comanches_hced_events": len(wave8_comanches_events),
        "candidate_keyed_wave8_sikh_punjab_hced_events": len(
            wave8_sikh_punjab_events
        ),
        "candidate_keyed_wave8_eritrea_hced_events": len(wave8_eritrea_events),
        "candidate_keyed_wave8_flanders_hced_events": len(wave8_flanders_events),
        "candidate_keyed_wave8_france_bavaria_hced_events": len(
            wave8_france_bavaria_events
        ),
        "candidate_keyed_wave8_eritrean_rebels_hced_events": len(
            wave8_eritrean_rebels_events
        ),
        "candidate_keyed_wave8_inca_rebels_hced_events": len(
            wave8_inca_rebels_events
        ),
        "candidate_keyed_wave8_haitian_rebels_hced_events": len(
            wave8_haitian_rebels_events
        ),
        "candidate_keyed_wave8_kingdom_kandy_hced_events": len(
            wave8_kingdom_kandy_events
        ),
        "candidate_keyed_wave8_hospitallers_hced_events": len(
            wave8_hospitallers_events
        ),
        "candidate_keyed_wave8_murids_hced_events": len(wave8_murids_events),
        "candidate_keyed_wave8_punjabi_sikhs_hced_events": len(
            wave8_punjabi_sikhs_events
        ),
        "candidate_keyed_wave8_modoc_hced_events": len(wave8_modoc_events),
        "candidate_keyed_wave8_sauk_hced_events": len(wave8_sauk_events),
        "candidate_keyed_wave8_ute_hced_events": len(wave8_ute_events),
        "candidate_keyed_wave8_yakima_hced_events": len(wave8_yakima_events),
        "candidate_keyed_wave8_taliban_al_qaeda_hced_events": len(
            wave8_taliban_al_qaeda_events
        ),
        "candidate_keyed_wave8_french_religious_forces_hced_events": len(
            wave8_french_religious_forces_events
        ),
        "candidate_keyed_wave8_chadian_rebels_hced_events": len(
            wave8_chadian_rebels_events
        ),
        "candidate_keyed_wave8_saudi_rashidi_hced_events": len(
            wave8_saudi_rashidi_events
        ),
        "candidate_keyed_wave8_yaqui_hced_events": len(wave8_yaqui_events),
        "candidate_keyed_wave8_egypt_forces_hced_events": len(
            wave8_egypt_forces_events
        ),
        "candidate_keyed_wave8_haiti_regimes_hced_events": len(
            wave8_haiti_regimes_events
        ),
        "candidate_keyed_wave8_zulu_forces_hced_events": len(
            wave8_zulu_forces_events
        ),
        "candidate_keyed_wave8_montenegro_1796_hced_events": len(
            wave8_montenegro_1796_events
        ),
        "candidate_keyed_wave8_bohemia_hced_events": len(wave8_bohemia_events),
        "candidate_keyed_wave8_spanish_liberals_hced_events": len(
            wave8_spanish_liberals_events
        ),
        "candidate_keyed_wave8_achea_hced_events": len(wave8_achea_events),
        "candidate_keyed_wave8_oran_hced_events": len(wave8_oran_events),
        "candidate_keyed_wave8_cheyenne_dog_soldiers_hced_events": len(
            wave8_cheyenne_dog_soldiers_events
        ),
        "candidate_keyed_wave8_libya_hced_events": len(wave8_libya_events),
        "candidate_keyed_wave8_kievan_rus_hced_events": len(
            wave8_kievan_rus_events
        ),
        "candidate_keyed_wave8_carnatic_hced_events": len(
            wave8_carnatic_events
        ),
        "candidate_keyed_wave8_goguryeo_hced_events": len(
            wave8_goguryeo_events
        ),
        "candidate_keyed_wave8_fln_hced_events": len(wave8_fln_events),
        "candidate_keyed_wave8_sindh_hced_events": len(wave8_sindh_events),
        "candidate_keyed_wave8_oman_hced_events": len(wave8_oman_events),
        "candidate_keyed_wave8_irish_civil_war_hced_events": len(
            wave8_irish_civil_war_events
        ),
        "candidate_keyed_wave8_bannock_sheepeater_hced_events": len(
            wave8_bannock_sheepeater_events
        ),
        "candidate_keyed_wave8_catholic_rebels_hced_events": len(
            wave8_catholic_rebels_events
        ),
        "candidate_keyed_wave8_macedon_hced_events": len(wave8_macedon_events),
        "candidate_keyed_wave8_uzbeks_hced_events": len(wave8_uzbeks_events),
        "candidate_keyed_wave8_etruria_hced_events": len(wave8_etruria_events),
        "wave7_global_identity_migrations": len(WAVE7_GLOBAL_ORANGE_MIGRATIONS),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "iwbd_battles_total": iwbd_promotion["battles_total"],
        "provisional_ucdp_events": len(ucdp_events),
        "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
        "iwd_parent_wars_total": iwd_aggregation["parents_total"],
        "iwd_component_records": iwd_aggregation["components_total"],
        "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
        "hced_location_assertions": hced_location_coverage,
        "source_queue_counts": review_counts,
    }
    registry = {"entities": registry_rows, "coverage": coverage}

    existing_coverage_warnings = seed_metadata.get("coverage_warnings")
    if existing_coverage_warnings is None:
        coverage_warnings: list[Any] = []
    elif isinstance(existing_coverage_warnings, list):
        coverage_warnings = list(existing_coverage_warnings)
    else:
        coverage_warnings = [existing_coverage_warnings]
    if HCED_LOCATION_WARNING not in coverage_warnings:
        coverage_warnings.append(HCED_LOCATION_WARNING)

    metadata = {
        **seed_metadata,
        "dataset_id": "military-elo-expanded-provisional-v0.2",
        "title": "Expanded provisional Military History Elo evidence release",
        "version": "0.2.0",
        "coverage_status": "expanded_provisional",
        "comprehensive": False,
        "coverage_warnings": coverage_warnings,
        "description": (
            "The curated seed plus source-derived tactical tranches (crosswalk-resolved and "
            "label-resolved HCED engagements, deduplicated IWBD battles) and strategic "
            "tranches (aggregated IWD coalition wars, UCDP terminal-victory episodes). "
            "The separate registry publishes time-bounded Cliopatria polity candidates, "
            "including unrated entries, without assigning them invented Elo results."
        ),
        "coverage_note": (
            "Registry coverage is much broader than rating coverage. Source-derived HCED "
            "and IWBD engagements remain provisional; IWD component wars enter only as one "
            "aggregated coalition update per parent conflict, UCDP termination records only "
            "as conflict-level terminal victory episodes, and unresolved records do not affect Elo. "
            f"The latest rated event ends in {latest_rated_event_year}; later timeline years carry ratings forward."
        ),
        "footer_note": (
            "Known polities, entities with Elo, and staged source records are reported separately. "
            "Absence from the rating ledger is not evidence of military failure."
        ),
        "record_counts_expected": {
            "entities": len(release_entity_rows),
            "events": len(all_events),
            "sources": len(sources_by_id),
            "registry_polities": len(registry_rows),
        },
        "year_range": {
            "start": min(int(event["year"]) for event in all_events),
            "end": max(int(event["end_year"]) for event in all_events),
            "calendar_note": seed_metadata.get("year_range", {}).get(
                "calendar_note", ""
            ),
        },
        "promotion": {
            "policy": (
                "Only nonduplicate HCED rows with aligned outcomes, both Seshat-coded sides, "
                "and unique time-valid polity identities enter the provisional tactical ledger. "
                "Rows lacking Seshat coding on one or both sides are retried in a second, "
                "declared label-resolution pass: sides resolve only through explicit "
                "time-bounded label policies or exact-normalized alias matching with "
                "uniqueness, full event-interval validity, and name-coherence for "
                "observation-derived pairings; faction and collective-peoples labels never "
                "resolve; polity labels pending identity splits never resolve; ambiguity "
                "always stays staged. For post-1500 rows only, an otherwise unresolved side "
                "may split on commas, semicolons, or ampersands as a coalition only when "
                "every member independently resolves through those ordinary label rules to "
                "a distinct identity valid for the full event interval. The shared canonical "
                "supersession remap runs before coalition assembly; this path is unavailable "
                "to the frozen pre-1500 cohort. Label-resolved events carry reduced identity "
                "confidence and an identity_resolution provenance marker. One independently dated "
                "HCED crosswalk candidate (Piraja 1822) uses a complete candidate fingerprint "
                "and exact-ID binding to cross an otherwise fail-closed within-year Portugal "
                "boundary; it does not populate a generic label observation. "
                "The 1500-1799 Wave 6 lane reviewed exactly 80 candidate-keyed HCED "
                "contracts whose complete raw rows, canonical event keys, outcomes, "
                "participant rosters, and entity windows are pinned. Seventy-six are "
                "active and four exact coalition-evidence holds remain staged. Its 39 "
                "HCED exclusions and eight Wikidata war umbrellas are likewise candidate-keyed and "
                "fingerprinted; none creates a label fallback, and all generic Holy "
                "Roman Empire rows remain staged. "
                "Wave 7 adds five candidate-keyed lanes covering 192 exact engagements, "
                "plus five atomic identity migrations of already-rated Orange events. "
                "Every admitted or held row is pinned by its complete queue-row hash, "
                "uses an alias-free time-bounded actor identity or an already curated "
                "identity, and bypasses generic label fallback. Eight HCED outcomes are "
                "corrected only where a direct historical reference contradicts the source "
                "assertion; each correction carries its own outcome provenance. The WEST "
                "lane also corrects four bad date, actor, or coalition records. Forty-two "
                "additional rows "
                "remain explicit holds, including Kadesh as a duplicate with a conflicting "
                "source outcome. "
                "Wave 8 reviews 62 additional candidate-keyed HCED rows across African "
                "state, New Zealand, and North American conflict lanes: 46 exact tactical "
                "engagements enter and 16 massacre, civilian-camp, umbrella-identity, or "
                "outcome-dispute rows remain explicit holds. Every new actor is "
                "conflict- or engagement-bounded and alias-free; no rating is inherited "
                "by a generic ethnic label. Four source outcomes are corrected only from "
                "direct official-history or museum evidence, with that source family "
                "recorded as outcome provenance. "
                "IWD component wars never enter individually: each parent conflict is rated at "
                "most once, as a coalition event aggregated from its component dyads, and only "
                "when the reconstructed sides are consistent, the component outcomes are "
                "unanimous, no curated seed war overlaps, and every belligerent resolves to a "
                "unique time-bounded identity. Eight transition-era parents use exact "
                "parent-keyed contracts that pin the complete component set, source "
                "semantics, party codes, and target IDs; they do not open generic COW-code "
                "fallbacks. All other parent wars stay staged. "
                "IWBD battles enter only when they are not a duplicate of any curated seed "
                "event, any non-curated-excluded HCED candidate (promoted or staged), or an "
                "earlier accepted IWBD row by exact normalized battle name and year within "
                "one year; "
                "broader ordinal/part matches require one recognized suffix path to extend "
                "the other in the same year with the same resolved outcome sides; "
                "their date span does not contain a differently-named battle of the same "
                "war (campaign umbrellas stay staged); the coded victor matches a named "
                "side; and both sides resolve to unique time-bounded identities outside "
                "declared deny windows. Twenty transition-era candidates use exact "
                "source fingerprints and exact-ID bindings; only those contracts can pass "
                "an otherwise applicable deny window, so bare Turkey remains denied in "
                "1919-1923 everywhere else. Two additional candidate-keyed contracts are narrow "
                "exceptions: Abtao reconstructs the exact Chile-Peru coalition, and Mishan "
                "may overlap the pinned concurrent-distinct Chalainor 2 sibling. Both "
                "contracts fail closed on source, sibling-set, or resolver drift and do not "
                "enable generic punctuation splitting or containment bypasses. Severity is "
                "capped at limited. Duplicate matches are excluded, never merged. "
                "UCDP conflict-termination episodes promote only as conflict-level terminal "
                "victory episodes (outcome codes 3/4): peace agreements, ceasefires, low "
                "activity, and actor cessation stay staged; every primary party must be a "
                "state resolving to a unique time-bounded identity through explicit "
                "Gleditsch-Ward code policies or exact time-valid alias matching; episodes "
                "duplicating an already-promoted strategic event, contradicted by a terminal "
                "dyad row, linked by end date to an oppositely-oriented victory assertion, or "
                "carrying a documented side-attribution dispute stay staged; severity is "
                "capped at limited and secondary supporters carry no outcome. "
                "A curated tranche of time-bounded state identities and label/code policy "
                "windows (second reviewer pending) resolves previously blocked bare labels "
                "and orphaned source codes era-correctly, with deliberate gaps for eras "
                "without a defensible single identity, and enumerated curated row exclusions "
                "for known wrong-actor and variant-spelling records - counted, never merged. "
                "A declared set of curated non-state actor identities moves seven former "
                "blocklist labels to authoritative time-bounded policies and covers five "
                "additional labels that were never blocklisted; labels for "
                "umbrella movements without unified command stay blocked. UCDP "
                "terminal-victory episodes may include a curated non-state primary party "
                "only through conflict-scoped actor policies whose windows are the actor's "
                "attested existence bounds; the government side must independently resolve. "
                "UCDP war_type follows the source's type_of_conflict under an exhaustive "
                "declared mapping; unmapped types are rejected, never coerced."
            ),
            "accepted_hced_events": len(source_events),
            "accepted_hced_label_events": len(label_events),
            "accepted_wave6_1500_1799_hced_events": len(wave6_events),
            "accepted_wave7_root_hced_events": len(wave7_root_events),
            "accepted_wave7_central_hced_events": len(wave7_central_events),
            "accepted_wave7_central_pass2_hced_events": len(wave7_central_pass2_events),
            "accepted_wave7_global_hced_events": len(wave7_global_events),
            "accepted_wave7_west_hced_events": len(wave7_west_events),
            "accepted_wave8_african_states_hced_events": len(
                wave8_african_states_events
            ),
            "accepted_wave8_new_zealand_hced_events": len(
                wave8_new_zealand_events
            ),
            "accepted_wave8_north_america_hced_events": len(
                wave8_north_america_events
            ),
            "accepted_wave8_xhosa_hced_events": len(wave8_xhosa_events),
            "accepted_wave8_polish_audit_hced_events": len(
                wave8_polish_audit_events
            ),
            "accepted_wave8_namibia_resistance_hced_events": len(
                wave8_namibia_resistance_events
            ),
            "accepted_wave8_first_saudi_hced_events": len(
                wave8_first_saudi_events
            ),
            "accepted_wave8_early_states_hced_events": len(
                wave8_early_states_events
            ),
            "accepted_wave8_judean_revolts_hced_events": len(
                wave8_judean_revolts_events
            ),
            "accepted_wave8_canadian_resistance_hced_events": len(
                wave8_canadian_resistance_events
            ),
            "accepted_wave8_wales_hced_events": len(wave8_wales_events),
            "accepted_wave8_cossack_hced_events": len(wave8_cossack_events),
            "accepted_wave8_fast17_hced_events": len(wave8_fast17_events),
            "accepted_wave8_naples_hced_events": len(wave8_naples_events),
            "accepted_wave8_somali_irish_sa_hced_events": len(
                wave8_somali_irish_sa_events
            ),
            "accepted_wave8_argentine_independence_hced_events": len(
                wave8_argentine_independence_events
            ),
            "accepted_wave8_ecuador_independence_hced_events": len(
                wave8_ecuador_independence_events
            ),
            "accepted_wave8_comanche_hced_events": len(wave8_comanche_events),
            "accepted_wave8_garibaldi_hced_events": len(wave8_garibaldi_events),
            "accepted_wave8_algiers_cheyenne_hced_events": len(
                wave8_algiers_cheyenne_events
            ),
            "accepted_wave8_dagestan_hced_events": len(wave8_dagestan_events),
            "accepted_wave8_irish_history_hced_events": len(
                wave8_irish_history_events
            ),
            "accepted_wave8_muslim_forces_hced_events": len(
                wave8_muslim_forces_events
            ),
            "accepted_wave8_moros_hced_events": len(wave8_moros_events),
            "accepted_wave8_manchus_hced_events": len(wave8_manchus_events),
            "accepted_wave8_peruvian_rebels_hced_events": len(
                wave8_peruvian_rebels_events
            ),
            "accepted_wave8_germany_hced_events": len(wave8_germany_events),
            "accepted_wave8_seljuks_hced_events": len(wave8_seljuks_events),
            "accepted_wave8_danish_vikings_hced_events": len(
                wave8_danish_vikings_events
            ),
            "accepted_wave8_epirus_hced_events": len(wave8_epirus_events),
            "accepted_wave8_savoy_hced_events": len(wave8_savoy_events),
            "accepted_wave8_nez_perce_hced_events": len(
                wave8_nez_perce_events
            ),
            "accepted_wave8_dacia_hced_events": len(wave8_dacia_events),
            "accepted_wave8_cherokee_hced_events": len(wave8_cherokee_events),
            "accepted_wave8_druze_rebels_hced_events": len(
                wave8_druze_rebels_events
            ),
            "accepted_wave8_insubrian_gauls_hced_events": len(
                wave8_insubrian_gauls_events
            ),
            "accepted_wave8_kiowa_hced_events": len(wave8_kiowa_events),
            "accepted_wave8_uzbekistan_hced_events": len(
                wave8_uzbekistan_events
            ),
            "accepted_wave8_vietnam_hced_events": len(wave8_vietnam_events),
            "accepted_wave8_hussites_hced_events": len(wave8_hussites_events),
            "accepted_wave8_livonian_order_hced_events": len(
                wave8_livonian_order_events
            ),
            "accepted_wave8_satsuma_hced_events": len(wave8_satsuma_events),
            "accepted_wave8_rajputs_hced_events": len(wave8_rajputs_events),
            "accepted_wave8_mamluk_egypt_hced_events": len(
                wave8_mamluk_egypt_events
            ),
            "accepted_wave8_rebel_barons_hced_events": len(
                wave8_rebel_barons_events
            ),
            "accepted_wave8_thebes_hced_events": len(wave8_thebes_events),
            "accepted_wave8_alemanni_hced_events": len(wave8_alemanni_events),
            "accepted_wave8_madagascar_hced_events": len(
                wave8_madagascar_events
            ),
            "accepted_wave8_kickapoo_hced_events": len(wave8_kickapoo_events),
            "accepted_wave8_lordship_isles_hced_events": len(
                wave8_lordship_isles_events
            ),
            "accepted_wave8_armenia_hced_events": len(wave8_armenia_events),
            "accepted_wave8_comanches_hced_events": len(wave8_comanches_events),
            "accepted_wave8_sikh_punjab_hced_events": len(
                wave8_sikh_punjab_events
            ),
            "accepted_wave8_eritrea_hced_events": len(wave8_eritrea_events),
            "accepted_wave8_flanders_hced_events": len(wave8_flanders_events),
            "accepted_wave8_france_bavaria_hced_events": len(
                wave8_france_bavaria_events
            ),
            "accepted_wave8_eritrean_rebels_hced_events": len(
                wave8_eritrean_rebels_events
            ),
            "accepted_wave8_inca_rebels_hced_events": len(
                wave8_inca_rebels_events
            ),
            "accepted_wave8_haitian_rebels_hced_events": len(
                wave8_haitian_rebels_events
            ),
            "accepted_wave8_kingdom_kandy_hced_events": len(
                wave8_kingdom_kandy_events
            ),
            "accepted_wave8_hospitallers_hced_events": len(
                wave8_hospitallers_events
            ),
            "accepted_wave8_murids_hced_events": len(wave8_murids_events),
            "accepted_wave8_punjabi_sikhs_hced_events": len(
                wave8_punjabi_sikhs_events
            ),
            "accepted_wave8_modoc_hced_events": len(wave8_modoc_events),
            "accepted_wave8_sauk_hced_events": len(wave8_sauk_events),
            "accepted_wave8_ute_hced_events": len(wave8_ute_events),
            "accepted_wave8_yakima_hced_events": len(wave8_yakima_events),
            "accepted_wave8_taliban_al_qaeda_hced_events": len(
                wave8_taliban_al_qaeda_events
            ),
            "accepted_wave8_french_religious_forces_hced_events": len(
                wave8_french_religious_forces_events
            ),
            "accepted_wave8_chadian_rebels_hced_events": len(
                wave8_chadian_rebels_events
            ),
            "accepted_wave8_saudi_rashidi_hced_events": len(
                wave8_saudi_rashidi_events
            ),
            "accepted_wave8_yaqui_hced_events": len(wave8_yaqui_events),
            "accepted_wave8_egypt_forces_hced_events": len(
                wave8_egypt_forces_events
            ),
            "accepted_wave8_haiti_regimes_hced_events": len(
                wave8_haiti_regimes_events
            ),
            "accepted_wave8_zulu_forces_hced_events": len(
                wave8_zulu_forces_events
            ),
            "accepted_wave8_montenegro_1796_hced_events": len(
                wave8_montenegro_1796_events
            ),
            "accepted_wave8_bohemia_hced_events": len(wave8_bohemia_events),
            "accepted_wave8_spanish_liberals_hced_events": len(
                wave8_spanish_liberals_events
            ),
            "accepted_wave8_achea_hced_events": len(wave8_achea_events),
            "accepted_wave8_oran_hced_events": len(wave8_oran_events),
            "accepted_wave8_cheyenne_dog_soldiers_hced_events": len(
                wave8_cheyenne_dog_soldiers_events
            ),
            "accepted_wave8_libya_hced_events": len(wave8_libya_events),
            "accepted_wave8_kievan_rus_hced_events": len(
                wave8_kievan_rus_events
            ),
            "accepted_wave8_carnatic_hced_events": len(
                wave8_carnatic_events
            ),
            "accepted_wave8_goguryeo_hced_events": len(
                wave8_goguryeo_events
            ),
            "accepted_wave8_fln_hced_events": len(wave8_fln_events),
            "accepted_wave8_sindh_hced_events": len(wave8_sindh_events),
            "accepted_wave8_oman_hced_events": len(wave8_oman_events),
            "accepted_wave8_irish_civil_war_hced_events": len(
                wave8_irish_civil_war_events
            ),
            "accepted_wave8_bannock_sheepeater_hced_events": len(
                wave8_bannock_sheepeater_events
            ),
            "accepted_wave8_catholic_rebels_hced_events": len(
                wave8_catholic_rebels_events
            ),
            "accepted_wave8_macedon_hced_events": len(wave8_macedon_events),
            "accepted_wave8_uzbeks_hced_events": len(wave8_uzbeks_events),
            "accepted_wave8_etruria_hced_events": len(wave8_etruria_events),
            "wave8_polish_audit_corrections": WAVE8_POLISH_AUDIT_CORRECTION_COUNT,
            "wave6_1500_1799_cohort_counts": wave6_cohort_counts(),
            "wave6_1500_1799_queue_validation": wave6_queue_validation,
            "wave6_1500_1799_candidate_ids": sorted(WAVE6_HCED_CONTRACTS),
            "wave6_1500_1799_hced_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE6_HCED_HOLDS.items())
            ],
            "wave6_1500_1799_hced_exclusions": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["category"],
                    "reason": contract["reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE6_HCED_EXCLUSIONS.items())
            ],
            "wave6_1500_1799_wikidata_exclusions": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["category"],
                    "reason": contract["reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE6_WIKIDATA_EXCLUSIONS.items())
            ],
            "wave7_root_cohort_counts": wave7_root_cohort_counts(),
            "wave7_root_queue_validation": wave7_root_queue_validation,
            "wave7_root_candidate_ids": sorted(WAVE7_ROOT_CONTRACT_IDS),
            "wave7_root_holds": [
                {
                    "candidate_id": candidate_id,
                    "reason": contract["reason"],
                    "raw_row_sha256": contract["raw_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_ROOT_HOLDS.items())
            ],
            "wave7_root_outcome_correction_ids": sorted(
                WAVE7_ROOT_OUTCOME_CORRECTION_IDS
            ),
            "wave7_root_entities_added": len(WAVE7_ROOT_ENTITIES),
            "wave7_root_sources_added": len(WAVE7_ROOT_SOURCES),
            "wave7_central_cohort_counts": wave7_central_cohort_counts(),
            "wave7_central_queue_validation": wave7_central_queue_validation,
            "wave7_central_candidate_ids": sorted(WAVE7_CENTRAL_PROMOTION_IDS),
            "wave7_central_holds": [
                {
                    "candidate_id": candidate_id,
                    "cohort": contract["cohort"],
                    "reason": contract["reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_CENTRAL_HOLDS.items())
            ],
            "wave7_central_entities_added": len(WAVE7_CENTRAL_ENTITIES),
            "wave7_central_sources_added": len(WAVE7_CENTRAL_SOURCES),
            "wave7_central_pass2_cohort_counts": (wave7_central_pass2_cohort_counts()),
            "wave7_central_pass2_hold_counts": wave7_central_pass2_hold_counts(),
            "wave7_central_pass2_queue_validation": (
                wave7_central_pass2_queue_validation
            ),
            "wave7_central_pass2_candidate_ids": sorted(
                WAVE7_CENTRAL_PASS2_PROMOTION_IDS
            ),
            "wave7_central_pass2_holds": [
                {
                    "candidate_id": candidate_id,
                    "cohort": contract["cohort"],
                    "category": contract["category"],
                    "reason": contract["reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_CENTRAL_PASS2_HOLDS.items())
            ],
            "wave7_central_pass2_entities_added": len(WAVE7_CENTRAL_PASS2_ENTITIES),
            "wave7_central_pass2_sources_added": len(WAVE7_CENTRAL_PASS2_SOURCES),
            "wave7_global_cohort_counts": wave7_global_cohort_counts(),
            "wave7_global_queue_validation": wave7_global_queue_validation,
            "wave7_global_candidate_ids": sorted(WAVE7_GLOBAL_HCED_CONTRACT_IDS),
            "wave7_global_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_GLOBAL_HCED_HOLDS.items())
            ],
            "wave7_global_identity_migrations": [
                {
                    "event_id": event_id,
                    "candidate_id": contract["candidate_id"],
                    "from_entity_id": contract["from_entity_id"],
                    "to_entity_id": contract["to_entity_id"],
                    "source_event_sha256": contract["source_event_sha256"],
                }
                for event_id, contract in sorted(WAVE7_GLOBAL_ORANGE_MIGRATIONS.items())
            ],
            "wave7_global_registry_supersessions": {
                candidate_id: list(replacements)
                for candidate_id, replacements in sorted(
                    wave7_global_registry_supersessions.items()
                )
            },
            "wave7_global_entities_added": len(WAVE7_GLOBAL_ENTITIES),
            "wave7_global_sources_added": len(WAVE7_GLOBAL_SOURCES),
            "wave7_west_cohort_counts": wave7_west_cohort_counts(),
            "wave7_west_queue_validation": wave7_west_queue_validation,
            "wave7_west_candidate_ids": sorted(WAVE7_WEST_HCED_CONTRACT_IDS),
            "wave7_west_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_WEST_HCED_HOLDS.items())
            ],
            "wave7_west_protected_existing": [
                {
                    "candidate_id": candidate_id,
                    "expected_event_id": contract["expected_event_id"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE7_WEST_PROTECTED_RATED.items())
            ],
            "wave7_west_entities_added": len(WAVE7_WEST_ENTITIES),
            "wave7_west_sources_added": len(WAVE7_WEST_SOURCES),
            "wave8_african_states_cohort_counts": (
                wave8_african_states_cohort_counts()
            ),
            "wave8_african_states_queue_validation": (
                wave8_african_states_queue_validation
            ),
            "wave8_african_states_candidate_ids": sorted(
                WAVE8_AFRICAN_STATES_CONTRACT_IDS
            ),
            "wave8_african_states_entities_added": len(
                WAVE8_AFRICAN_STATES_ENTITIES
            ),
            "wave8_african_states_sources_added": len(WAVE8_AFRICAN_STATES_SOURCES),
            "wave8_new_zealand_cohort_counts": wave8_new_zealand_cohort_counts(),
            "wave8_new_zealand_queue_validation": (
                wave8_new_zealand_queue_validation
            ),
            "wave8_new_zealand_candidate_ids": sorted(
                WAVE8_NEW_ZEALAND_CONTRACT_IDS
            ),
            "wave8_new_zealand_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_NEW_ZEALAND_HOLDS.items())
            ],
            "wave8_new_zealand_entities_added": len(WAVE8_NEW_ZEALAND_ENTITIES),
            "wave8_new_zealand_sources_added": len(WAVE8_NEW_ZEALAND_SOURCES),
            "wave8_north_america_cohort_counts": (
                wave8_north_america_cohort_counts()
            ),
            "wave8_north_america_queue_validation": (
                wave8_north_america_queue_validation
            ),
            "wave8_north_america_candidate_ids": sorted(
                WAVE8_NORTH_AMERICA_CONTRACT_IDS
            ),
            "wave8_north_america_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_NORTH_AMERICA_HOLDS.items()
                )
            ],
            "wave8_north_america_entities_added": len(WAVE8_NORTH_AMERICA_ENTITIES),
            "wave8_north_america_sources_added": len(WAVE8_NORTH_AMERICA_SOURCES),
            "wave8_xhosa_cohort_counts": wave8_xhosa_cohort_counts(),
            "wave8_xhosa_queue_validation": wave8_xhosa_queue_validation,
            "wave8_xhosa_candidate_ids": sorted(WAVE8_XHOSA_CONTRACT_IDS),
            "wave8_xhosa_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_XHOSA_HOLDS.items())
            ],
            "wave8_xhosa_entities_added": len(WAVE8_XHOSA_ENTITIES),
            "wave8_xhosa_sources_added": len(WAVE8_XHOSA_SOURCES),
            "wave8_polish_audit_counts": wave8_polish_audit_counts(),
            "wave8_polish_audit_queue_validation": (
                wave8_polish_audit_queue_validation
            ),
            "wave8_polish_audit_candidate_ids": sorted(
                WAVE8_POLISH_AUDIT_CONTRACT_IDS
            ),
            "wave8_polish_audit_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_POLISH_AUDIT_HOLDS.items()
                )
            ],
            "wave8_polish_audit_entities_added": len(
                WAVE8_POLISH_AUDIT_ENTITIES
            ),
            "wave8_polish_audit_sources_added": len(WAVE8_POLISH_AUDIT_SOURCES),
            "wave8_namibia_resistance_cohort_counts": (
                wave8_namibia_resistance_cohort_counts()
            ),
            "wave8_namibia_resistance_queue_validation": (
                wave8_namibia_resistance_queue_validation
            ),
            "wave8_namibia_resistance_candidate_ids": sorted(
                WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS
            ),
            "wave8_namibia_resistance_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                    "full_row_sha256": contract["full_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_NAMIBIA_RESISTANCE_HOLDS.items()
                )
            ],
            "wave8_namibia_resistance_entities_added": len(
                WAVE8_NAMIBIA_RESISTANCE_ENTITIES
            ),
            "wave8_namibia_resistance_sources_added": len(
                WAVE8_NAMIBIA_RESISTANCE_SOURCES
            ),
            "wave8_first_saudi_counts": wave8_first_saudi_counts(),
            "wave8_first_saudi_queue_validation": (
                wave8_first_saudi_queue_validation
            ),
            "wave8_first_saudi_candidate_ids": sorted(
                WAVE8_FIRST_SAUDI_CONTRACT_IDS
            ),
            "wave8_first_saudi_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_FIRST_SAUDI_HOLDS.items())
            ],
            "wave8_first_saudi_entities_added": len(WAVE8_FIRST_SAUDI_ENTITIES),
            "wave8_first_saudi_sources_added": len(WAVE8_FIRST_SAUDI_SOURCES),
            "wave8_early_states_cohort_counts": wave8_early_states_cohort_counts(),
            "wave8_early_states_queue_validation": wave8_early_states_queue_validation,
            "wave8_early_states_candidate_ids": sorted(
                WAVE8_EARLY_STATES_CONTRACT_IDS
            ),
            "wave8_early_states_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_EARLY_STATES_HOLDS.items())
            ],
            "wave8_early_states_entities_added": len(WAVE8_EARLY_STATES_ENTITIES),
            "wave8_early_states_sources_added": len(WAVE8_EARLY_STATES_SOURCES),
            "wave8_judean_revolts_counts": wave8_judean_revolts_counts(),
            "wave8_judean_revolts_queue_validation": (
                wave8_judean_revolts_queue_validation
            ),
            "wave8_judean_revolts_candidate_ids": sorted(
                WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS
            ),
            "wave8_judean_revolts_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_JUDEAN_REVOLTS_HOLDS.items()
                )
            ],
            "wave8_judean_revolts_entities_added": len(
                WAVE8_JUDEAN_REVOLTS_ENTITIES
            ),
            "wave8_judean_revolts_sources_added": len(WAVE8_JUDEAN_REVOLTS_SOURCES),
            "wave8_canadian_resistance_counts": wave8_canadian_resistance_counts(),
            "wave8_canadian_resistance_queue_validation": (
                wave8_canadian_resistance_queue_validation
            ),
            "wave8_canadian_resistance_candidate_ids": sorted(
                WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS
            ),
            "wave8_canadian_resistance_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_CANADIAN_RESISTANCE_HOLDS.items()
                )
            ],
            "wave8_canadian_resistance_entities_added": len(
                WAVE8_CANADIAN_RESISTANCE_ENTITIES
            ),
            "wave8_canadian_resistance_sources_added": len(
                WAVE8_CANADIAN_RESISTANCE_SOURCES
            ),
            "wave8_wales_counts": wave8_wales_counts(),
            "wave8_wales_cohort_counts": wave8_wales_cohort_counts(),
            "wave8_wales_queue_validation": wave8_wales_queue_validation,
            "wave8_wales_candidate_ids": sorted(WAVE8_WALES_CONTRACT_IDS),
            "wave8_wales_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_WALES_HOLDS.items())
            ],
            "wave8_wales_entities_added": len(WAVE8_WALES_ENTITIES),
            "wave8_wales_sources_added": len(WAVE8_WALES_SOURCES),
            "wave8_cossack_counts": wave8_cossack_counts(),
            "wave8_cossack_cohort_counts": wave8_cossack_cohort_counts(),
            "wave8_cossack_queue_validation": wave8_cossack_queue_validation,
            "wave8_cossack_candidate_ids": sorted(WAVE8_COSSACK_CONTRACT_IDS),
            "wave8_cossack_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_COSSACK_REBELLIONS_HOLDS.items()
                )
            ],
            "wave8_cossack_entities_added": len(
                WAVE8_COSSACK_REBELLIONS_ENTITIES
            ),
            "wave8_cossack_sources_added": len(WAVE8_COSSACK_REBELLIONS_SOURCES),
            "wave8_fast17_counts": wave8_fast17_counts(),
            "wave8_fast17_cohort_counts": wave8_fast17_cohort_counts(),
            "wave8_fast17_queue_validation": wave8_fast17_queue_validation,
            "wave8_fast17_candidate_ids": sorted(WAVE8_FAST17_CONTRACT_IDS),
            "wave8_fast17_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_FAST17_HOLDS.items())
            ],
            "wave8_fast17_iwbd_duplicate_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FAST17_IWBD_DUPLICATE_HOLDS.items()
                )
            ],
            "wave8_fast17_entities_added": len(WAVE8_FAST17_ENTITIES),
            "wave8_fast17_sources_added": len(WAVE8_FAST17_SOURCES),
            "wave8_naples_counts": wave8_naples_counts(),
            "wave8_naples_cohort_counts": wave8_naples_cohort_counts(),
            "wave8_naples_queue_validation": wave8_naples_queue_validation,
            "wave8_naples_candidate_ids": sorted(WAVE8_NAPLES_CONTRACT_IDS),
            "wave8_naples_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_NAPLES_HOLDS.items())
            ],
            "wave8_naples_entities_added": len(WAVE8_NAPLES_ENTITIES),
            "wave8_naples_sources_added": len(WAVE8_NAPLES_SOURCES),
            "wave8_somali_irish_sa_counts": wave8_somali_irish_sa_counts(),
            "wave8_somali_irish_sa_cohort_counts": (
                wave8_somali_irish_sa_cohort_counts()
            ),
            "wave8_somali_irish_sa_queue_validation": (
                wave8_somali_irish_sa_queue_validation
            ),
            "wave8_somali_irish_sa_candidate_ids": sorted(
                WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS
            ),
            "wave8_somali_irish_sa_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_SOMALI_IRISH_SA_HOLDS.items()
                )
            ],
            "wave8_somali_irish_sa_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_somali_irish_sa_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_somali_irish_sa_entities_added": len(
                WAVE8_SOMALI_IRISH_SA_ENTITIES
            ),
            "wave8_somali_irish_sa_sources_added": len(
                WAVE8_SOMALI_IRISH_SA_SOURCES
            ),
            "wave8_argentine_independence_counts": (
                wave8_argentine_independence_counts()
            ),
            "wave8_argentine_independence_cohort_counts": (
                wave8_argentine_independence_cohort_counts()
            ),
            "wave8_argentine_independence_queue_validation": (
                wave8_argentine_independence_queue_validation
            ),
            "wave8_argentine_independence_candidate_ids": sorted(
                WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS
            ),
            "wave8_argentine_independence_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_ARGENTINE_INDEPENDENCE_HOLDS.items()
                )
            ],
            "wave8_argentine_independence_entities_added": len(
                WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES
            ),
            "wave8_argentine_independence_sources_added": len(
                WAVE8_ARGENTINE_INDEPENDENCE_SOURCES
            ),
            "wave8_ecuador_independence_counts": (
                wave8_ecuador_independence_counts()
            ),
            "wave8_ecuador_independence_cohort_counts": (
                wave8_ecuador_independence_cohort_counts()
            ),
            "wave8_ecuador_independence_queue_validation": (
                wave8_ecuador_independence_queue_validation
            ),
            "wave8_ecuador_independence_candidate_ids": sorted(
                WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS
            ),
            "wave8_ecuador_independence_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(
                    WAVE8_ECUADOR_INDEPENDENCE_HOLDS.items()
                )
            ],
            "wave8_ecuador_independence_entities_added": len(
                WAVE8_ECUADOR_INDEPENDENCE_ENTITIES
            ),
            "wave8_ecuador_independence_sources_added": len(
                WAVE8_ECUADOR_INDEPENDENCE_SOURCES
            ),
            "wave8_comanche_counts": wave8_comanche_counts(),
            "wave8_comanche_cohort_counts": wave8_comanche_cohort_counts(),
            "wave8_comanche_queue_validation": wave8_comanche_queue_validation,
            "wave8_comanche_candidate_ids": sorted(WAVE8_COMANCHE_CONTRACT_IDS),
            "wave8_comanche_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_COMANCHE_HOLDS.items())
            ],
            "wave8_comanche_entities_added": len(WAVE8_COMANCHE_ENTITIES),
            "wave8_comanche_sources_added": len(WAVE8_COMANCHE_SOURCES),
            "wave8_garibaldi_counts": wave8_garibaldi_counts(),
            "wave8_garibaldi_cohort_counts": wave8_garibaldi_cohort_counts(),
            "wave8_garibaldi_queue_validation": wave8_garibaldi_queue_validation,
            "wave8_garibaldi_integration_validation": (
                wave8_garibaldi_integration_validation
            ),
            "wave8_garibaldi_candidate_ids": sorted(WAVE8_GARIBALDI_CONTRACT_IDS),
            "wave8_garibaldi_holds": [
                {
                    "candidate_id": candidate_id,
                    "category": contract["hold_category"],
                    "reason": contract["hold_reason"],
                    "raw_row_sha256": contract["raw_row_sha256"],
                }
                for candidate_id, contract in sorted(WAVE8_GARIBALDI_HOLDS.items())
            ],
            "wave8_garibaldi_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_garibaldi_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GARIBALDI_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_garibaldi_entities_added": len(WAVE8_GARIBALDI_ENTITIES),
            "wave8_garibaldi_sources_added": len(WAVE8_GARIBALDI_SOURCES),
            "wave8_algiers_cheyenne_counts": wave8_algiers_cheyenne_counts(),
            "wave8_algiers_cheyenne_cohort_counts": (
                wave8_algiers_cheyenne_cohort_counts()
            ),
            "wave8_algiers_cheyenne_queue_validation": (
                wave8_algiers_cheyenne_queue_validation
            ),
            "wave8_algiers_cheyenne_candidate_ids": sorted(
                WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
            ),
            "wave8_algiers_cheyenne_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ALGIERS_CHEYENNE_HOLDS.items()
                )
            ],
            "wave8_algiers_cheyenne_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_algiers_cheyenne_entities_added": len(
                WAVE8_ALGIERS_CHEYENNE_ENTITIES
            ),
            "wave8_algiers_cheyenne_sources_added": len(
                WAVE8_ALGIERS_CHEYENNE_SOURCES
            ),
            "wave8_dagestan_counts": wave8_dagestan_counts(),
            "wave8_dagestan_cohort_counts": wave8_dagestan_cohort_counts(),
            "wave8_dagestan_queue_validation": wave8_dagestan_queue_validation,
            "wave8_dagestan_integration_validation": (
                wave8_dagestan_integration_validation
            ),
            "wave8_dagestan_candidate_ids": sorted(WAVE8_DAGESTAN_CONTRACT_IDS),
            "wave8_dagestan_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_DAGESTAN_HOLDS.items())
            ],
            "wave8_dagestan_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DAGESTAN_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_dagestan_entities_added": len(WAVE8_DAGESTAN_ENTITIES),
            "wave8_dagestan_sources_added": len(WAVE8_DAGESTAN_SOURCES),
            "wave8_irish_history_counts": wave8_irish_history_counts(),
            "wave8_irish_history_cohort_counts": (
                wave8_irish_history_cohort_counts()
            ),
            "wave8_irish_history_queue_validation": (
                wave8_irish_history_queue_validation
            ),
            "wave8_irish_history_integration_validation": (
                wave8_irish_history_integration_validation
            ),
            "wave8_irish_history_candidate_ids": sorted(
                WAVE8_IRISH_HISTORY_CONTRACT_IDS
            ),
            "wave8_irish_history_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_irish_history_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_irish_history_entities_added": len(
                WAVE8_IRISH_HISTORY_ENTITIES
            ),
            "wave8_irish_history_sources_added": len(WAVE8_IRISH_HISTORY_SOURCES),
            "wave8_muslim_forces_counts": wave8_muslim_forces_counts(),
            "wave8_muslim_forces_cohort_counts": (
                wave8_muslim_forces_cohort_counts()
            ),
            "wave8_muslim_forces_queue_validation": (
                wave8_muslim_forces_queue_validation
            ),
            "wave8_muslim_forces_candidate_ids": sorted(
                WAVE8_MUSLIM_FORCES_CONTRACT_IDS
            ),
            "wave8_muslim_forces_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MUSLIM_FORCES_HOLDS.items()
                )
            ],
            "wave8_muslim_forces_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_muslim_forces_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_muslim_forces_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_muslim_forces_entities_added": len(
                WAVE8_MUSLIM_FORCES_ENTITIES
            ),
            "wave8_muslim_forces_sources_added": len(WAVE8_MUSLIM_FORCES_SOURCES),
            "wave8_moros_counts": wave8_moros_counts(),
            "wave8_moros_cohort_counts": wave8_moros_cohort_counts(),
            "wave8_moros_queue_validation": wave8_moros_queue_validation,
            "wave8_moros_candidate_ids": sorted(WAVE8_MOROS_CONTRACT_IDS),
            "wave8_moros_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_MOROS_HOLDS.items())
            ],
            "wave8_moros_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MOROS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_moros_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MOROS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_moros_entities_added": len(WAVE8_MOROS_ENTITIES),
            "wave8_moros_sources_added": len(WAVE8_MOROS_SOURCES),
            "wave8_manchus_counts": wave8_manchus_counts(),
            "wave8_manchus_cohort_counts": wave8_manchus_cohort_counts(),
            "wave8_manchus_queue_validation": wave8_manchus_queue_validation,
            "wave8_manchus_integration_validation": (
                wave8_manchus_integration_validation
            ),
            "wave8_manchus_candidate_ids": sorted(WAVE8_MANCHUS_CONTRACT_IDS),
            "wave8_manchus_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_MANCHUS_HOLDS.items())
            ],
            "wave8_manchus_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_manchus_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_manchus_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_manchus_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MANCHUS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_manchus_entities_added": len(WAVE8_MANCHUS_ENTITIES),
            "wave8_manchus_sources_added": len(WAVE8_MANCHUS_SOURCES),
            "wave8_peruvian_rebels_counts": wave8_peruvian_rebels_counts(),
            "wave8_peruvian_rebels_cohort_counts": (
                wave8_peruvian_rebels_cohort_counts()
            ),
            "wave8_peruvian_rebels_queue_validation": (
                wave8_peruvian_rebels_queue_validation
            ),
            "wave8_peruvian_rebels_integration_validation": (
                wave8_peruvian_rebels_integration_validation
            ),
            "wave8_peruvian_rebels_candidate_ids": sorted(
                WAVE8_PERUVIAN_REBELS_CONTRACT_IDS
            ),
            "wave8_peruvian_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PERUVIAN_REBELS_HOLDS.items()
                )
            ],
            "wave8_peruvian_rebels_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_peruvian_rebels_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_peruvian_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_peruvian_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_peruvian_rebels_entities_added": len(
                WAVE8_PERUVIAN_REBELS_ENTITIES
            ),
            "wave8_peruvian_rebels_sources_added": len(
                WAVE8_PERUVIAN_REBELS_SOURCES
            ),
            "wave8_germany_counts": wave8_germany_counts(),
            "wave8_germany_cohort_counts": wave8_germany_cohort_counts(),
            "wave8_germany_queue_validation": wave8_germany_queue_validation,
            "wave8_germany_integration_validation": (
                wave8_germany_integration_validation
            ),
            "wave8_germany_candidate_ids": sorted(WAVE8_GERMANY_CONTRACT_IDS),
            "wave8_germany_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_GERMANY_HOLDS.items())
            ],
            "wave8_germany_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GERMANY_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_germany_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_germany_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_germany_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_GERMANY_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_germany_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GERMANY_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_germany_entities_added": len(WAVE8_GERMANY_ENTITIES),
            "wave8_germany_sources_added": len(WAVE8_GERMANY_SOURCES),
            "wave8_seljuks_counts": wave8_seljuks_counts(),
            "wave8_seljuks_cohort_counts": wave8_seljuks_cohort_counts(),
            "wave8_seljuks_queue_validation": wave8_seljuks_queue_validation,
            "wave8_seljuks_integration_validation": (
                wave8_seljuks_integration_validation
            ),
            "wave8_seljuks_candidate_ids": sorted(WAVE8_SELJUKS_CONTRACT_IDS),
            "wave8_seljuks_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SELJUKS_HOLDS.items())
            ],
            "wave8_seljuks_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_seljuks_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_seljuks_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_seljuks_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SELJUKS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_seljuks_entities_added": len(WAVE8_SELJUKS_ENTITIES),
            "wave8_seljuks_sources_added": len(WAVE8_SELJUKS_SOURCES),
            "wave8_danish_vikings_counts": wave8_danish_vikings_counts(),
            "wave8_danish_vikings_cohort_counts": (
                wave8_danish_vikings_cohort_counts()
            ),
            "wave8_danish_vikings_queue_validation": (
                wave8_danish_vikings_queue_validation
            ),
            "wave8_danish_vikings_integration_validation": (
                wave8_danish_vikings_integration_validation
            ),
            "wave8_danish_vikings_candidate_ids": sorted(
                WAVE8_DANISH_VIKINGS_CONTRACT_IDS
            ),
            "wave8_danish_vikings_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_HOLDS.items()
                )
            ],
            "wave8_danish_vikings_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_danish_vikings_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_danish_vikings_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_danish_vikings_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_danish_vikings_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_danish_vikings_entities_added": len(
                WAVE8_DANISH_VIKINGS_ENTITIES
            ),
            "wave8_danish_vikings_sources_added": len(
                WAVE8_DANISH_VIKINGS_SOURCES
            ),
            "wave8_epirus_counts": wave8_epirus_counts(),
            "wave8_epirus_cohort_counts": wave8_epirus_cohort_counts(),
            "wave8_epirus_queue_validation": wave8_epirus_queue_validation,
            "wave8_epirus_integration_validation": (
                wave8_epirus_integration_validation
            ),
            "wave8_epirus_candidate_ids": sorted(WAVE8_EPIRUS_CONTRACT_IDS),
            "wave8_epirus_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_EPIRUS_HOLDS.items())
            ],
            "wave8_epirus_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_EPIRUS_EXCLUSIONS.items())
            ],
            "wave8_epirus_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_epirus_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_epirus_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_epirus_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EPIRUS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_epirus_entities_added": len(WAVE8_EPIRUS_ENTITIES),
            "wave8_epirus_sources_added": len(WAVE8_EPIRUS_SOURCES),
            "wave8_savoy_counts": wave8_savoy_counts(),
            "wave8_savoy_cohort_counts": wave8_savoy_cohort_counts(),
            "wave8_savoy_queue_validation": wave8_savoy_queue_validation,
            "wave8_savoy_integration_validation": (
                wave8_savoy_integration_validation
            ),
            "wave8_savoy_candidate_ids": sorted(WAVE8_SAVOY_CONTRACT_IDS),
            "wave8_savoy_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SAVOY_HOLDS.items())
            ],
            "wave8_savoy_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SAVOY_EXCLUSIONS.items())
            ],
            "wave8_savoy_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_savoy_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_savoy_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAVOY_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_savoy_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAVOY_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_savoy_entities_added": len(WAVE8_SAVOY_ENTITIES),
            "wave8_savoy_sources_added": len(WAVE8_SAVOY_SOURCES),
            "wave8_nez_perce_counts": wave8_nez_perce_counts(),
            "wave8_nez_perce_cohort_counts": wave8_nez_perce_cohort_counts(),
            "wave8_nez_perce_queue_validation": (
                wave8_nez_perce_queue_validation
            ),
            "wave8_nez_perce_integration_validation": (
                wave8_nez_perce_integration_validation
            ),
            "wave8_nez_perce_candidate_ids": sorted(
                WAVE8_NEZ_PERCE_CONTRACT_IDS
            ),
            "wave8_nez_perce_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_NEZ_PERCE_HOLDS.items()
                )
            ],
            "wave8_nez_perce_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_nez_perce_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_nez_perce_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_nez_perce_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_nez_perce_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_nez_perce_entities_added": len(WAVE8_NEZ_PERCE_ENTITIES),
            "wave8_nez_perce_sources_added": len(WAVE8_NEZ_PERCE_SOURCES),
            "wave8_dacia_counts": wave8_dacia_counts(),
            "wave8_dacia_cohort_counts": wave8_dacia_cohort_counts(),
            "wave8_dacia_queue_validation": wave8_dacia_queue_validation,
            "wave8_dacia_integration_validation": (
                wave8_dacia_integration_validation
            ),
            "wave8_dacia_candidate_ids": sorted(WAVE8_DACIA_CONTRACT_IDS),
            "wave8_dacia_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_DACIA_HOLDS.items())
            ],
            "wave8_dacia_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DACIA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_dacia_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_dacia_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DACIA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_dacia_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DACIA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_dacia_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DACIA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_dacia_entities_added": len(WAVE8_DACIA_ENTITIES),
            "wave8_dacia_sources_added": len(WAVE8_DACIA_SOURCES),
            "wave8_cherokee_counts": wave8_cherokee_counts(),
            "wave8_cherokee_cohort_counts": wave8_cherokee_cohort_counts(),
            "wave8_cherokee_queue_validation": wave8_cherokee_queue_validation,
            "wave8_cherokee_integration_validation": (
                wave8_cherokee_integration_validation
            ),
            "wave8_cherokee_candidate_ids": sorted(WAVE8_CHEROKEE_CONTRACT_IDS),
            "wave8_cherokee_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_CHEROKEE_HOLDS.items())
            ],
            "wave8_cherokee_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHEROKEE_EXCLUSIONS.items()
                )
            ],
            "wave8_cherokee_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_cherokee_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_cherokee_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_cherokee_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHEROKEE_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_cherokee_entities_added": len(WAVE8_CHEROKEE_ENTITIES),
            "wave8_cherokee_sources_added": len(WAVE8_CHEROKEE_SOURCES),
            "wave8_druze_rebels_counts": wave8_druze_rebels_counts(),
            "wave8_druze_rebels_cohort_counts": (
                wave8_druze_rebels_cohort_counts()
            ),
            "wave8_druze_rebels_queue_validation": (
                wave8_druze_rebels_queue_validation
            ),
            "wave8_druze_rebels_integration_validation": (
                wave8_druze_rebels_integration_validation
            ),
            "wave8_druze_rebels_candidate_ids": sorted(
                WAVE8_DRUZE_REBELS_CONTRACT_IDS
            ),
            "wave8_druze_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DRUZE_REBELS_HOLDS.items()
                )
            ],
            "wave8_druze_rebels_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_druze_rebels_cross_lane_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_druze_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_druze_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_druze_rebels_entities_added": len(
                WAVE8_DRUZE_REBELS_ENTITIES
            ),
            "wave8_druze_rebels_sources_added": len(WAVE8_DRUZE_REBELS_SOURCES),
            "wave8_insubrian_gauls_counts": wave8_insubrian_gauls_counts(),
            "wave8_insubrian_gauls_cohort_counts": (
                wave8_insubrian_gauls_cohort_counts()
            ),
            "wave8_insubrian_gauls_queue_validation": (
                wave8_insubrian_gauls_queue_validation
            ),
            "wave8_insubrian_gauls_integration_validation": (
                wave8_insubrian_gauls_integration_validation
            ),
            "wave8_insubrian_gauls_candidate_ids": sorted(
                WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS
            ),
            "wave8_insubrian_gauls_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_HOLDS.items()
                )
            ],
            "wave8_insubrian_gauls_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_insubrian_gauls_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_insubrian_gauls_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_insubrian_gauls_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_insubrian_gauls_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_insubrian_gauls_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_insubrian_gauls_entities_added": len(
                WAVE8_INSUBRIAN_GAULS_ENTITIES
            ),
            "wave8_insubrian_gauls_sources_added": len(
                WAVE8_INSUBRIAN_GAULS_SOURCES
            ),
            "wave8_kiowa_counts": wave8_kiowa_counts(),
            "wave8_kiowa_cohort_counts": wave8_kiowa_cohort_counts(),
            "wave8_kiowa_queue_validation": wave8_kiowa_queue_validation,
            "wave8_kiowa_integration_validation": (
                wave8_kiowa_integration_validation
            ),
            "wave8_kiowa_candidate_ids": sorted(WAVE8_KIOWA_CONTRACT_IDS),
            "wave8_kiowa_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_KIOWA_HOLDS.items())
            ],
            "wave8_kiowa_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_kiowa_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_kiowa_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_kiowa_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KIOWA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_kiowa_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KIOWA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_kiowa_entities_added": len(WAVE8_KIOWA_ENTITIES),
            "wave8_kiowa_sources_added": len(WAVE8_KIOWA_SOURCES),
            "wave8_uzbekistan_counts": wave8_uzbekistan_counts(),
            "wave8_uzbekistan_cohort_counts": wave8_uzbekistan_cohort_counts(),
            "wave8_uzbekistan_queue_validation": (
                wave8_uzbekistan_queue_validation
            ),
            "wave8_uzbekistan_integration_validation": (
                wave8_uzbekistan_integration_validation
            ),
            "wave8_uzbekistan_candidate_ids": sorted(
                WAVE8_UZBEKISTAN_CONTRACT_IDS
            ),
            "wave8_uzbekistan_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UZBEKISTAN_HOLDS.items()
                )
            ],
            "wave8_uzbekistan_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_uzbekistan_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_uzbekistan_internal_relationship_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS.items()
                )
            ],
            "wave8_uzbekistan_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_uzbekistan_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_uzbekistan_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_uzbekistan_entities_added": len(WAVE8_UZBEKISTAN_ENTITIES),
            "wave8_uzbekistan_sources_added": len(WAVE8_UZBEKISTAN_SOURCES),
            "wave8_vietnam_counts": wave8_vietnam_counts(),
            "wave8_vietnam_cohort_counts": wave8_vietnam_cohort_counts(),
            "wave8_vietnam_queue_validation": wave8_vietnam_queue_validation,
            "wave8_vietnam_integration_validation": (
                wave8_vietnam_integration_validation
            ),
            "wave8_vietnam_candidate_ids": sorted(WAVE8_VIETNAM_CONTRACT_IDS),
            "wave8_vietnam_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_VIETNAM_HOLDS.items())
            ],
            "wave8_vietnam_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_VIETNAM_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_vietnam_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_vietnam_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_vietnam_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_vietnam_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_vietnam_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_VIETNAM_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_vietnam_entities_added": len(WAVE8_VIETNAM_ENTITIES),
            "wave8_vietnam_sources_added": len(WAVE8_VIETNAM_SOURCES),
            "wave8_hussites_counts": wave8_hussites_counts(),
            "wave8_hussites_cohort_counts": wave8_hussites_cohort_counts(),
            "wave8_hussites_queue_validation": wave8_hussites_queue_validation,
            "wave8_hussites_integration_validation": (
                wave8_hussites_integration_validation
            ),
            "wave8_hussites_candidate_ids": sorted(WAVE8_HUSSITES_CONTRACT_IDS),
            "wave8_hussites_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_HUSSITES_HOLDS.items())
            ],
            "wave8_hussites_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HUSSITES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_hussites_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_hussites_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_hussites_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_hussites_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_hussites_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HUSSITES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_hussites_entities_added": len(WAVE8_HUSSITES_ENTITIES),
            "wave8_hussites_sources_added": len(WAVE8_HUSSITES_SOURCES),
            "wave8_livonian_order_counts": wave8_livonian_order_counts(),
            "wave8_livonian_order_cohort_counts": (
                wave8_livonian_order_cohort_counts()
            ),
            "wave8_livonian_order_queue_validation": (
                wave8_livonian_order_queue_validation
            ),
            "wave8_livonian_order_integration_validation": (
                wave8_livonian_order_integration_validation
            ),
            "wave8_livonian_order_candidate_ids": sorted(
                WAVE8_LIVONIAN_ORDER_CONTRACT_IDS
            ),
            "wave8_livonian_order_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_HOLDS.items()
                )
            ],
            "wave8_livonian_order_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_livonian_order_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_livonian_order_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_livonian_order_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_livonian_order_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_livonian_order_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_livonian_order_entities_added": len(
                WAVE8_LIVONIAN_ORDER_ENTITIES
            ),
            "wave8_livonian_order_sources_added": len(
                WAVE8_LIVONIAN_ORDER_SOURCES
            ),
            "wave8_satsuma_counts": wave8_satsuma_counts(),
            "wave8_satsuma_cohort_counts": wave8_satsuma_cohort_counts(),
            "wave8_satsuma_queue_validation": wave8_satsuma_queue_validation,
            "wave8_satsuma_integration_validation": (
                wave8_satsuma_integration_validation
            ),
            "wave8_satsuma_candidate_ids": sorted(WAVE8_SATSUMA_CONTRACT_IDS),
            "wave8_satsuma_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SATSUMA_HOLDS.items())
            ],
            "wave8_satsuma_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SATSUMA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_satsuma_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_satsuma_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_satsuma_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_satsuma_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_satsuma_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_satsuma_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SATSUMA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_satsuma_entities_added": len(WAVE8_SATSUMA_ENTITIES),
            "wave8_satsuma_sources_added": len(WAVE8_SATSUMA_SOURCES),
            "wave8_rajputs_counts": wave8_rajputs_counts(),
            "wave8_rajputs_cohort_counts": wave8_rajputs_cohort_counts(),
            "wave8_rajputs_queue_validation": wave8_rajputs_queue_validation,
            "wave8_rajputs_integration_validation": (
                wave8_rajputs_integration_validation
            ),
            "wave8_rajputs_candidate_ids": sorted(WAVE8_RAJPUTS_CONTRACT_IDS),
            "wave8_rajputs_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_RAJPUTS_HOLDS.items())
            ],
            "wave8_rajputs_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_rajputs_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_rajputs_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_rajputs_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_rajputs_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_rajputs_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_rajputs_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_RAJPUTS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_rajputs_entities_added": len(WAVE8_RAJPUTS_ENTITIES),
            "wave8_rajputs_sources_added": len(WAVE8_RAJPUTS_SOURCES),
            "wave8_mamluk_egypt_counts": wave8_mamluk_egypt_counts(),
            "wave8_mamluk_egypt_cohort_counts": (
                wave8_mamluk_egypt_cohort_counts()
            ),
            "wave8_mamluk_egypt_queue_validation": (
                wave8_mamluk_egypt_queue_validation
            ),
            "wave8_mamluk_egypt_integration_validation": (
                wave8_mamluk_egypt_integration_validation
            ),
            "wave8_mamluk_egypt_candidate_ids": sorted(
                WAVE8_MAMLUK_EGYPT_CONTRACT_IDS
            ),
            "wave8_mamluk_egypt_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_HOLDS.items()
                )
            ],
            "wave8_mamluk_egypt_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_mamluk_egypt_cross_lane_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_mamluk_egypt_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_mamluk_egypt_integration_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_mamluk_egypt_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_mamluk_egypt_entities_added": len(
                WAVE8_MAMLUK_EGYPT_ENTITIES
            ),
            "wave8_mamluk_egypt_sources_added": len(
                WAVE8_MAMLUK_EGYPT_SOURCES
            ),
            "wave8_rebel_barons_counts": wave8_rebel_barons_counts(),
            "wave8_rebel_barons_cohort_counts": (
                wave8_rebel_barons_cohort_counts()
            ),
            "wave8_rebel_barons_queue_validation": (
                wave8_rebel_barons_queue_validation
            ),
            "wave8_rebel_barons_integration_validation": (
                wave8_rebel_barons_integration_validation
            ),
            "wave8_rebel_barons_candidate_ids": sorted(
                WAVE8_REBEL_BARONS_CONTRACT_IDS
            ),
            "wave8_rebel_barons_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_REBEL_BARONS_HOLDS.items()
                )
            ],
            "wave8_rebel_barons_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_rebel_barons_external_owner_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS.items()
                )
            ],
            "wave8_rebel_barons_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_rebel_barons_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_rebel_barons_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_rebel_barons_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_rebel_barons_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_rebel_barons_entities_added": len(
                WAVE8_REBEL_BARONS_ENTITIES
            ),
            "wave8_rebel_barons_sources_added": len(
                WAVE8_REBEL_BARONS_SOURCES
            ),
            "wave8_thebes_counts": wave8_thebes_counts(),
            "wave8_thebes_cohort_counts": wave8_thebes_cohort_counts(),
            "wave8_thebes_queue_validation": wave8_thebes_queue_validation,
            "wave8_thebes_integration_validation": (
                wave8_thebes_integration_validation
            ),
            "wave8_thebes_candidate_ids": sorted(WAVE8_THEBES_CONTRACT_IDS),
            "wave8_thebes_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_THEBES_HOLDS.items())
            ],
            "wave8_thebes_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_THEBES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_thebes_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_THEBES_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_thebes_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_thebes_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_thebes_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_THEBES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_thebes_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_THEBES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_thebes_entities_added": len(WAVE8_THEBES_ENTITIES),
            "wave8_thebes_sources_added": len(WAVE8_THEBES_SOURCES),
            "wave8_alemanni_counts": wave8_alemanni_counts(),
            "wave8_alemanni_cohort_counts": wave8_alemanni_cohort_counts(),
            "wave8_alemanni_spelling_counts": wave8_alemanni_spelling_counts(),
            "wave8_alemanni_queue_validation": wave8_alemanni_queue_validation,
            "wave8_alemanni_integration_validation": (
                wave8_alemanni_integration_validation
            ),
            "wave8_alemanni_candidate_ids": sorted(WAVE8_ALEMANNI_CONTRACT_IDS),
            "wave8_alemanni_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ALEMANNI_HOLDS.items())
            ],
            "wave8_alemanni_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_alemanni_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_alemanni_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_alemanni_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_alemanni_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_alemanni_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ALEMANNI_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_alemanni_entities_added": len(WAVE8_ALEMANNI_ENTITIES),
            "wave8_alemanni_sources_added": len(WAVE8_ALEMANNI_SOURCES),
            "wave8_madagascar_counts": wave8_madagascar_counts(),
            "wave8_madagascar_cohort_counts": wave8_madagascar_cohort_counts(),
            "wave8_madagascar_queue_validation": (
                wave8_madagascar_queue_validation
            ),
            "wave8_madagascar_integration_validation": (
                wave8_madagascar_integration_validation
            ),
            "wave8_madagascar_candidate_ids": sorted(
                WAVE8_MADAGASCAR_CONTRACT_IDS
            ),
            "wave8_madagascar_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MADAGASCAR_HOLDS.items()
                )
            ],
            "wave8_madagascar_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_madagascar_external_owner_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_madagascar_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MADAGASCAR_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_madagascar_entities_added": len(WAVE8_MADAGASCAR_ENTITIES),
            "wave8_madagascar_sources_added": len(WAVE8_MADAGASCAR_SOURCES),
            "wave8_kickapoo_counts": wave8_kickapoo_counts(),
            "wave8_kickapoo_cohort_counts": wave8_kickapoo_cohort_counts(),
            "wave8_kickapoo_queue_validation": wave8_kickapoo_queue_validation,
            "wave8_kickapoo_integration_validation": (
                wave8_kickapoo_integration_validation
            ),
            "wave8_kickapoo_candidate_ids": sorted(WAVE8_KICKAPOO_CONTRACT_IDS),
            "wave8_kickapoo_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_KICKAPOO_HOLDS.items())
            ],
            "wave8_kickapoo_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_kickapoo_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_kickapoo_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_kickapoo_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_kickapoo_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_kickapoo_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_kickapoo_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KICKAPOO_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_kickapoo_entities_added": len(WAVE8_KICKAPOO_ENTITIES),
            "wave8_kickapoo_sources_added": len(WAVE8_KICKAPOO_SOURCES),
            "wave8_lordship_isles_counts": wave8_lordship_isles_counts(),
            "wave8_lordship_isles_cohort_counts": (
                wave8_lordship_isles_cohort_counts()
            ),
            "wave8_lordship_isles_row_dispositions": (
                wave8_lordship_isles_row_dispositions()
            ),
            "wave8_lordship_isles_queue_validation": (
                wave8_lordship_isles_queue_validation
            ),
            "wave8_lordship_isles_integration_validation": (
                wave8_lordship_isles_integration_validation
            ),
            "wave8_lordship_isles_candidate_ids": sorted(
                WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
            ),
            "wave8_lordship_isles_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_HOLDS.items()
                )
            ],
            "wave8_lordship_isles_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_lordship_isles_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_lordship_isles_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_lordship_isles_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_lordship_isles_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_lordship_isles_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_lordship_isles_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_lordship_isles_entities_added": len(
                WAVE8_LORDSHIP_ISLES_ENTITIES
            ),
            "wave8_lordship_isles_sources_added": len(
                WAVE8_LORDSHIP_ISLES_SOURCES
            ),
            "wave8_armenia_counts": wave8_armenia_counts(),
            "wave8_armenia_cohort_counts": wave8_armenia_cohort_counts(),
            "wave8_armenia_queue_validation": wave8_armenia_queue_validation,
            "wave8_armenia_integration_validation": (
                wave8_armenia_integration_validation
            ),
            "wave8_armenia_candidate_ids": sorted(WAVE8_ARMENIA_CONTRACT_IDS),
            "wave8_armenia_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ARMENIA_HOLDS.items())
            ],
            "wave8_armenia_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ARMENIA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_armenia_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_armenia_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_armenia_existing_release_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_armenia_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_armenia_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ARMENIA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_armenia_entities_added": len(WAVE8_ARMENIA_ENTITIES),
            "wave8_armenia_sources_added": len(WAVE8_ARMENIA_SOURCES),
            "wave8_comanches_counts": wave8_comanches_counts(),
            "wave8_comanches_cohort_counts": wave8_comanches_cohort_counts(),
            "wave8_comanches_queue_validation": wave8_comanches_queue_validation,
            "wave8_comanches_integration_validation": (
                wave8_comanches_integration_validation
            ),
            "wave8_comanches_candidate_ids": sorted(WAVE8_COMANCHES_CONTRACT_IDS),
            "wave8_comanches_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_COMANCHES_HOLDS.items())
            ],
            "wave8_comanches_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_COMANCHES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_comanches_related_singular_lane_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_comanches_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_comanches_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_comanches_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_comanches_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_COMANCHES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_comanches_entities_added": len(WAVE8_COMANCHES_ENTITIES),
            "wave8_comanches_sources_added": len(WAVE8_COMANCHES_SOURCES),
            "wave8_sikh_punjab_counts": wave8_sikh_punjab_counts(),
            "wave8_sikh_punjab_cohort_counts": wave8_sikh_punjab_cohort_counts(),
            "wave8_sikh_punjab_queue_validation": (
                wave8_sikh_punjab_queue_validation
            ),
            "wave8_sikh_punjab_integration_validation": (
                wave8_sikh_punjab_integration_validation
            ),
            "wave8_sikh_punjab_candidate_ids": sorted(
                WAVE8_SIKH_PUNJAB_CONTRACT_IDS
            ),
            "wave8_sikh_punjab_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_HOLDS.items()
                )
            ],
            "wave8_sikh_punjab_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_sikh_punjab_external_owner_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_DISPOSITIONS.items()
                )
            ],
            "wave8_sikh_punjab_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_sikh_punjab_iwbd_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_sikh_punjab_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_sikh_punjab_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_sikh_punjab_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_sikh_punjab_entities_added": len(WAVE8_SIKH_PUNJAB_ENTITIES),
            "wave8_sikh_punjab_sources_added": len(WAVE8_SIKH_PUNJAB_SOURCES),
            "wave8_eritrea_counts": wave8_eritrea_counts(),
            "wave8_eritrea_cohort_counts": wave8_eritrea_cohort_counts(),
            "wave8_eritrea_queue_validation": wave8_eritrea_queue_validation,
            "wave8_eritrea_integration_validation": (
                wave8_eritrea_integration_validation
            ),
            "wave8_eritrea_candidate_ids": sorted(WAVE8_ERITREA_CONTRACT_IDS),
            "wave8_eritrea_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ERITREA_HOLDS.items())
            ],
            "wave8_eritrea_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_eritrea_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_related_iwbd_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_eritrea_existing_release_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ERITREA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrea_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_eritrea_entities_added": len(WAVE8_ERITREA_ENTITIES),
            "wave8_eritrea_sources_added": len(WAVE8_ERITREA_SOURCES),
            "wave8_flanders_counts": wave8_flanders_counts(),
            "wave8_flanders_cohort_counts": wave8_flanders_cohort_counts(),
            "wave8_flanders_queue_validation": wave8_flanders_queue_validation,
            "wave8_flanders_integration_validation": (
                wave8_flanders_integration_validation
            ),
            "wave8_flanders_candidate_ids": sorted(WAVE8_FLANDERS_CONTRACT_IDS),
            "wave8_flanders_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_FLANDERS_HOLDS.items())
            ],
            "wave8_flanders_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FLANDERS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_flanders_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_flanders_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_flanders_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_flanders_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_flanders_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_flanders_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_flanders_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FLANDERS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_flanders_entities_added": len(WAVE8_FLANDERS_ENTITIES),
            "wave8_flanders_sources_added": len(WAVE8_FLANDERS_SOURCES),
            "wave8_france_bavaria_counts": wave8_france_bavaria_counts(),
            "wave8_france_bavaria_cohort_counts": (
                wave8_france_bavaria_cohort_counts()
            ),
            "wave8_france_bavaria_queue_validation": (
                wave8_france_bavaria_queue_validation
            ),
            "wave8_france_bavaria_integration_validation": (
                wave8_france_bavaria_integration_validation
            ),
            "wave8_france_bavaria_candidate_ids": sorted(
                WAVE8_FRANCE_BAVARIA_CONTRACT_IDS
            ),
            "wave8_france_bavaria_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_HOLDS.items()
                )
            ],
            "wave8_france_bavaria_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_france_bavaria_existing_lane_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_france_bavaria_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_france_bavaria_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_france_bavaria_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_france_bavaria_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_france_bavaria_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_france_bavaria_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_france_bavaria_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_france_bavaria_entities_added": len(
                WAVE8_FRANCE_BAVARIA_ENTITIES
            ),
            "wave8_france_bavaria_sources_added": len(
                WAVE8_FRANCE_BAVARIA_SOURCES
            ),
            "wave8_eritrean_rebels_counts": wave8_eritrean_rebels_counts(),
            "wave8_eritrean_rebels_cohort_counts": (
                wave8_eritrean_rebels_cohort_counts()
            ),
            "wave8_eritrean_rebels_queue_validation": (
                wave8_eritrean_rebels_queue_validation
            ),
            "wave8_eritrean_rebels_integration_validation": (
                wave8_eritrean_rebels_integration_validation
            ),
            "wave8_eritrean_rebels_candidate_ids": sorted(
                WAVE8_ERITREAN_REBELS_CONTRACT_IDS
            ),
            "wave8_eritrean_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_HOLDS.items()
                )
            ],
            "wave8_eritrean_rebels_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_eritrean_rebels_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_eritrean_rebels_existing_release_duplicate_dispositions": [
                {"event_id": event_id, **contract}
                for event_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_eritrean_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_eritrean_rebels_entities_added": len(
                WAVE8_ERITREAN_REBELS_ENTITIES
            ),
            "wave8_eritrean_rebels_sources_added": len(
                WAVE8_ERITREAN_REBELS_SOURCES
            ),
            "wave8_inca_rebels_counts": wave8_inca_rebels_counts(),
            "wave8_inca_rebels_cohort_counts": wave8_inca_rebels_cohort_counts(),
            "wave8_inca_rebels_queue_validation": wave8_inca_rebels_queue_validation,
            "wave8_inca_rebels_integration_validation": (
                wave8_inca_rebels_integration_validation
            ),
            "wave8_inca_rebels_candidate_ids": sorted(
                WAVE8_INCA_REBELS_CONTRACT_IDS
            ),
            "wave8_inca_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INCA_REBELS_HOLDS.items()
                )
            ],
            "wave8_inca_rebels_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_inca_rebels_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_inca_rebels_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_inca_rebels_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_inca_rebels_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_inca_rebels_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_inca_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_inca_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_INCA_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_inca_rebels_entities_added": len(WAVE8_INCA_REBELS_ENTITIES),
            "wave8_inca_rebels_sources_added": len(WAVE8_INCA_REBELS_SOURCES),
            "wave8_haitian_rebels_counts": wave8_haitian_rebels_counts(),
            "wave8_haitian_rebels_cohort_counts": (
                wave8_haitian_rebels_cohort_counts()
            ),
            "wave8_haitian_rebels_queue_validation": (
                wave8_haitian_rebels_queue_validation
            ),
            "wave8_haitian_rebels_integration_validation": (
                wave8_haitian_rebels_integration_validation
            ),
            "wave8_haitian_rebels_candidate_ids": sorted(
                WAVE8_HAITIAN_REBELS_CONTRACT_IDS
            ),
            "wave8_haitian_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_HOLDS.items()
                )
            ],
            "wave8_haitian_rebels_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_haitian_rebels_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_haitian_rebels_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_haitian_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_haitian_rebels_entities_added": len(
                WAVE8_HAITIAN_REBELS_ENTITIES
            ),
            "wave8_haitian_rebels_sources_added": len(
                WAVE8_HAITIAN_REBELS_SOURCES
            ),
            "wave8_kingdom_kandy_counts": wave8_kingdom_kandy_counts(),
            "wave8_kingdom_kandy_cohort_counts": (
                wave8_kingdom_kandy_cohort_counts()
            ),
            "wave8_kingdom_kandy_queue_validation": (
                wave8_kingdom_kandy_queue_validation
            ),
            "wave8_kingdom_kandy_integration_validation": (
                wave8_kingdom_kandy_integration_validation
            ),
            "wave8_kingdom_kandy_candidate_ids": sorted(
                WAVE8_KINGDOM_KANDY_CONTRACT_IDS
            ),
            "wave8_kingdom_kandy_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_HOLDS.items()
                )
            ],
            "wave8_kingdom_kandy_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_kingdom_kandy_external_owner_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_kingdom_kandy_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_kingdom_kandy_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_kingdom_kandy_entities_added": len(
                WAVE8_KINGDOM_KANDY_ENTITIES
            ),
            "wave8_kingdom_kandy_sources_added": len(
                WAVE8_KINGDOM_KANDY_SOURCES
            ),
            "wave8_hospitallers_counts": wave8_hospitallers_counts(),
            "wave8_hospitallers_cohort_counts": wave8_hospitallers_cohort_counts(),
            "wave8_hospitallers_queue_validation": (
                wave8_hospitallers_queue_validation
            ),
            "wave8_hospitallers_integration_validation": (
                wave8_hospitallers_integration_validation
            ),
            "wave8_hospitallers_candidate_ids": sorted(
                WAVE8_HOSPITALLERS_CONTRACT_IDS
            ),
            "wave8_hospitallers_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_HOLDS.items()
                )
            ],
            "wave8_hospitallers_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_hospitallers_cross_lane_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_hospitallers_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_hospitallers_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_hospitallers_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_hospitallers_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_hospitallers_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_hospitallers_cross_spelling_duplicate_audit": (
                WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT
            ),
            "wave8_hospitallers_opposite_result_audit": (
                WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT
            ),
            "wave8_hospitallers_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_hospitallers_entities_added": len(WAVE8_HOSPITALLERS_ENTITIES),
            "wave8_hospitallers_sources_added": len(WAVE8_HOSPITALLERS_SOURCES),
            "wave8_murids_counts": wave8_murids_counts(),
            "wave8_murids_cohort_counts": wave8_murids_cohort_counts(),
            "wave8_murids_metadata": wave8_murids_metadata(),
            "wave8_murids_queue_validation": wave8_murids_queue_validation,
            "wave8_murids_integration_validation": (
                wave8_murids_integration_validation
            ),
            "wave8_murids_candidate_ids": sorted(WAVE8_MURIDS_CONTRACT_IDS),
            "wave8_murids_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_MURIDS_HOLDS.items())
            ],
            "wave8_murids_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MURIDS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_murids_dagestan_lane_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_murids_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_murids_existing_lane_overlap_audit": [
                {"entity_id": entity_id, **contract}
                for entity_id, contract in sorted(
                    WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_murids_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_murids_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_murids_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_murids_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MURIDS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_murids_scope_and_opposite_result_audit": (
                WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT
            ),
            "wave8_murids_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MURIDS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_murids_entities_added": len(WAVE8_MURIDS_ENTITIES),
            "wave8_murids_sources_added": len(WAVE8_MURIDS_SOURCES),
            "wave8_punjabi_sikhs_counts": wave8_punjabi_sikhs_counts(),
            "wave8_punjabi_sikhs_cohort_counts": (
                wave8_punjabi_sikhs_cohort_counts()
            ),
            "wave8_punjabi_sikhs_queue_validation": (
                wave8_punjabi_sikhs_queue_validation
            ),
            "wave8_punjabi_sikhs_integration_validation": (
                wave8_punjabi_sikhs_integration_validation
            ),
            "wave8_punjabi_sikhs_candidate_ids": sorted(
                WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
            ),
            "wave8_punjabi_sikhs_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_HOLDS.items()
                )
            ],
            "wave8_punjabi_sikhs_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_punjabi_sikhs_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_punjabi_sikhs_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_punjabi_sikhs_entities_added": len(
                WAVE8_PUNJABI_SIKHS_ENTITIES
            ),
            "wave8_punjabi_sikhs_sources_added": len(
                WAVE8_PUNJABI_SIKHS_SOURCES
            ),
            "wave8_modoc_counts": wave8_modoc_counts(),
            "wave8_modoc_cohort_counts": wave8_modoc_cohort_counts(),
            "wave8_modoc_metadata": wave8_modoc_metadata(),
            "wave8_modoc_queue_validation": wave8_modoc_queue_validation,
            "wave8_modoc_integration_validation": wave8_modoc_integration_validation,
            "wave8_modoc_candidate_ids": sorted(WAVE8_MODOC_CONTRACT_IDS),
            "wave8_modoc_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_MODOC_HOLDS.items())
            ],
            "wave8_modoc_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MODOC_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_modoc_cross_event_boundaries": [
                {"boundary_id": boundary_id, **contract}
                for boundary_id, contract in sorted(
                    WAVE8_MODOC_CROSS_EVENT_BOUNDARIES.items()
                )
            ],
            "wave8_modoc_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_modoc_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_modoc_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_modoc_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_MODOC_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_modoc_scope_and_opposite_result_audit": (
                WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT
            ),
            "wave8_modoc_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MODOC_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_modoc_entities_added": len(WAVE8_MODOC_ENTITIES),
            "wave8_modoc_sources_added": len(WAVE8_MODOC_SOURCES),
            "wave8_sauk_counts": wave8_sauk_counts(),
            "wave8_sauk_cohort_counts": wave8_sauk_cohort_counts(),
            "wave8_sauk_metadata": wave8_sauk_metadata(),
            "wave8_sauk_queue_validation": wave8_sauk_queue_validation,
            "wave8_sauk_integration_validation": wave8_sauk_integration_validation,
            "wave8_sauk_candidate_ids": sorted(WAVE8_SAUK_CONTRACT_IDS),
            "wave8_sauk_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SAUK_HOLDS.items())
            ],
            "wave8_sauk_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUK_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_sauk_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAUK_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_sauk_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAUK_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_sauk_scope_and_opposite_result_audit": (
                WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT
            ),
            "wave8_sauk_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUK_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_sauk_entities_added": len(WAVE8_SAUK_ENTITIES),
            "wave8_sauk_sources_added": len(WAVE8_SAUK_SOURCES),
            "wave8_ute_counts": wave8_ute_counts(),
            "wave8_ute_cohort_counts": wave8_ute_cohort_counts(),
            "wave8_ute_queue_validation": wave8_ute_queue_validation,
            "wave8_ute_integration_validation": wave8_ute_integration_validation,
            "wave8_ute_candidate_ids": sorted(WAVE8_UTE_CONTRACT_IDS),
            "wave8_ute_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_UTE_HOLDS.items())
            ],
            "wave8_ute_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_ute_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_cross_lane_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_alternate_label_audit": WAVE8_UTE_ALTERNATE_LABEL_AUDIT,
            "wave8_ute_opposite_result_audit": WAVE8_UTE_OPPOSITE_RESULT_AUDIT,
            "wave8_ute_cross_spelling_duplicate_audit": (
                WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT
            ),
            "wave8_ute_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_ute_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_UTE_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_ute_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UTE_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_ute_entities_added": len(WAVE8_UTE_ENTITIES),
            "wave8_ute_sources_added": len(WAVE8_UTE_SOURCES),
            "wave8_yakima_counts": wave8_yakima_counts(),
            "wave8_yakima_cohort_counts": wave8_yakima_cohort_counts(),
            "wave8_yakima_queue_validation": wave8_yakima_queue_validation,
            "wave8_yakima_integration_validation": (
                wave8_yakima_integration_validation
            ),
            "wave8_yakima_candidate_ids": sorted(WAVE8_YAKIMA_CONTRACT_IDS),
            "wave8_yakima_war_candidate_ids": sorted(
                WAVE8_YAKIMA_WAR_CANDIDATE_IDS
            ),
            "wave8_yakima_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_YAKIMA_HOLDS.items())
            ],
            "wave8_yakima_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAKIMA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_yakima_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_yakima_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_yakima_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAKIMA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_yakima_entities_added": len(WAVE8_YAKIMA_ENTITIES),
            "wave8_yakima_sources_added": len(WAVE8_YAKIMA_SOURCES),
            "wave8_taliban_al_qaeda_counts": wave8_taliban_al_qaeda_counts(),
            "wave8_taliban_al_qaeda_cohort_counts": (
                wave8_taliban_al_qaeda_cohort_counts()
            ),
            "wave8_taliban_al_qaeda_metadata": (
                wave8_taliban_al_qaeda_metadata()
            ),
            "wave8_taliban_al_qaeda_queue_validation": (
                wave8_taliban_al_qaeda_queue_validation
            ),
            "wave8_taliban_al_qaeda_integration_validation": (
                wave8_taliban_al_qaeda_integration_validation
            ),
            "wave8_taliban_al_qaeda_candidate_ids": sorted(
                WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
            ),
            "wave8_taliban_al_qaeda_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_HOLDS.items()
                )
            ],
            "wave8_taliban_al_qaeda_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_related_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_existing_release_boundaries": [
                {"event_id": event_id, **contract}
                for event_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES.items()
                )
            ],
            "wave8_taliban_al_qaeda_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_ucdp_overlap_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_taliban_al_qaeda_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_taliban_al_qaeda_entities_added": len(
                WAVE8_TALIBAN_AL_QAEDA_ENTITIES
            ),
            "wave8_taliban_al_qaeda_sources_added": len(
                WAVE8_TALIBAN_AL_QAEDA_SOURCES
            ),
            "wave8_french_religious_forces_counts": (
                wave8_french_religious_forces_counts()
            ),
            "wave8_french_religious_forces_cohort_counts": (
                wave8_french_religious_forces_cohort_counts()
            ),
            "wave8_french_religious_forces_metadata": (
                wave8_french_religious_forces_metadata()
            ),
            "wave8_french_religious_forces_queue_validation": (
                wave8_french_religious_forces_queue_validation
            ),
            "wave8_french_religious_forces_integration_validation": (
                wave8_french_religious_forces_integration_validation
            ),
            "wave8_french_religious_forces_candidate_ids": sorted(
                WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
            ),
            "wave8_french_religious_forces_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS.items()
                )
            ],
            "wave8_french_religious_forces_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_french_religious_forces_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_cross_label_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_french_religious_forces_existing_release_boundaries": [
                {"event_id": event_id, **contract}
                for event_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES.items()
                )
            ],
            "wave8_french_religious_forces_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_cross_event_boundaries": [
                {"boundary_id": boundary_id, **contract}
                for boundary_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES.items()
                )
            ],
            "wave8_french_religious_forces_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_french_religious_forces_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_french_religious_forces_entities_added": len(
                WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES
            ),
            "wave8_french_religious_forces_sources_added": len(
                WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES
            ),
            "wave8_chadian_rebels_counts": wave8_chadian_rebels_counts(),
            "wave8_chadian_rebels_cohort_counts": (
                wave8_chadian_rebels_cohort_counts()
            ),
            "wave8_chadian_rebels_metadata": wave8_chadian_rebels_metadata(),
            "wave8_chadian_rebels_queue_validation": (
                wave8_chadian_rebels_queue_validation
            ),
            "wave8_chadian_rebels_integration_validation": (
                wave8_chadian_rebels_integration_validation
            ),
            "wave8_chadian_rebels_candidate_ids": sorted(
                WAVE8_CHADIAN_REBELS_CONTRACT_IDS
            ),
            "wave8_chadian_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_HOLDS.items()
                )
            ],
            "wave8_chadian_rebels_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_chadian_rebels_adjacent_hced_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS.items()
                )
            ],
            "wave8_chadian_rebels_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_chadian_rebels_ucdp_overlap_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS.items()
                )
            ],
            "wave8_chadian_rebels_current_release_boundaries": [
                {"event_id": event_id, **contract}
                for event_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES.items()
                )
            ],
            "wave8_chadian_rebels_duplicate_audits": (
                WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS
            ),
            "wave8_chadian_rebels_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_chadian_rebels_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_chadian_rebels_entities_added": len(
                WAVE8_CHADIAN_REBELS_ENTITIES
            ),
            "wave8_chadian_rebels_sources_added": len(
                WAVE8_CHADIAN_REBELS_SOURCES
            ),
            "wave8_saudi_rashidi_counts": wave8_saudi_rashidi_counts(),
            "wave8_saudi_rashidi_cohort_counts": (
                wave8_saudi_rashidi_cohort_counts()
            ),
            "wave8_saudi_rashidi_queue_validation": (
                wave8_saudi_rashidi_queue_validation
            ),
            "wave8_saudi_rashidi_integration_validation": (
                wave8_saudi_rashidi_integration_validation
            ),
            "wave8_saudi_rashidi_candidate_ids": sorted(
                WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
            ),
            "wave8_saudi_rashidi_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_HOLDS.items()
                )
            ],
            "wave8_saudi_rashidi_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_saudi_rashidi_label_ownership_audit": (
                WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT
            ),
            "wave8_saudi_rashidi_first_saudi_ownership_audit": (
                WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT
            ),
            "wave8_saudi_rashidi_release_ownership_audit": [
                {"event_id": event_id, **contract}
                for event_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT.items()
                )
            ],
            "wave8_saudi_rashidi_cross_label_boundaries": [
                {"boundary_id": boundary_id, **contract}
                for boundary_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES.items()
                )
            ],
            "wave8_saudi_rashidi_hced_twin_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS.items()
                )
            ],
            "wave8_saudi_rashidi_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_saudi_rashidi_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_saudi_rashidi_iwbd_outside_lane_audit": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT.items()
                )
            ],
            "wave8_saudi_rashidi_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_saudi_rashidi_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_saudi_rashidi_entities_added": len(
                WAVE8_SAUDI_RASHIDI_ENTITIES
            ),
            "wave8_saudi_rashidi_sources_added": len(
                WAVE8_SAUDI_RASHIDI_SOURCES
            ),
            "wave8_yaqui_counts": wave8_yaqui_counts(),
            "wave8_yaqui_cohort_counts": wave8_yaqui_cohort_counts(),
            "wave8_yaqui_metadata": wave8_yaqui_metadata(),
            "wave8_yaqui_queue_validation": wave8_yaqui_queue_validation,
            "wave8_yaqui_integration_validation": wave8_yaqui_integration_validation,
            "wave8_yaqui_candidate_ids": sorted(WAVE8_YAQUI_CONTRACT_IDS),
            "wave8_yaqui_war_candidate_ids": sorted(
                WAVE8_YAQUI_WAR_CANDIDATE_IDS
            ),
            "wave8_yaqui_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_YAQUI_HOLDS.items())
            ],
            "wave8_yaqui_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAQUI_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_yaqui_event_boundaries": [
                {"boundary_id": boundary_id, **contract}
                for boundary_id, contract in sorted(
                    WAVE8_YAQUI_EVENT_BOUNDARIES.items()
                )
            ],
            "wave8_yaqui_cross_lane_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS.items()
                )
            ],
            "wave8_yaqui_scope_and_opposite_result_audit": (
                WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT
            ),
            "wave8_yaqui_hced_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_yaqui_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_yaqui_iwbd_zero_overlap_audit": [
                {"audit_id": audit_id, **contract}
                for audit_id, contract in sorted(
                    WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT.items()
                )
            ],
            "wave8_yaqui_existing_release_duplicate_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_yaqui_integration_dispositions": [
                {"disposition_id": disposition_id, **contract}
                for disposition_id, contract in sorted(
                    WAVE8_YAQUI_INTEGRATION_DISPOSITIONS.items()
                )
            ],
            "wave8_yaqui_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_YAQUI_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_yaqui_entities_added": len(WAVE8_YAQUI_ENTITIES),
            "wave8_yaqui_sources_added": len(WAVE8_YAQUI_SOURCES),
            "wave8_egypt_forces_counts": wave8_egypt_forces_counts(),
            "wave8_egypt_forces_cohort_counts": (
                wave8_egypt_forces_cohort_counts()
            ),
            "wave8_egypt_forces_audit_signature": (
                wave8_egypt_forces_audit_signature()
            ),
            "wave8_egypt_forces_final_audit_signature": (
                WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_egypt_forces_queue_validation": (
                wave8_egypt_forces_queue_validation
            ),
            "wave8_egypt_forces_identity_validation": (
                wave8_egypt_forces_identity_validation
            ),
            "wave8_egypt_forces_integration_validation": (
                wave8_egypt_forces_integration_validation
            ),
            "wave8_egypt_forces_candidate_ids": sorted(
                WAVE8_EGYPT_FORCES_CONTRACT_IDS
            ),
            "wave8_egypt_forces_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_HOLDS.items()
                )
            ],
            "wave8_egypt_forces_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_egypt_forces_exact_label_funnel_audit": (
                WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT
            ),
            "wave8_egypt_forces_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_egypt_forces_identity_boundary_audit": (
                WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT
            ),
            "wave8_egypt_forces_current_release_event_audit": (
                WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT
            ),
            "wave8_egypt_forces_hced_twin_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS.items()
                )
            ],
            "wave8_egypt_forces_iwbd_duplicate_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            ],
            "wave8_egypt_forces_iwd_audit": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_IWD_AUDIT.items()
                )
            ],
            "wave8_egypt_forces_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_egypt_forces_point_quarantine_additions": sorted(
                WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_egypt_forces_country_quarantine_additions": sorted(
                WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_egypt_forces_outcome_overrides": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES.items()
                )
            ],
            "wave8_egypt_forces_entities_added": len(
                WAVE8_EGYPT_FORCES_ENTITIES
            ),
            "wave8_egypt_forces_sources_added": len(WAVE8_EGYPT_FORCES_SOURCES),
            "wave8_haiti_regimes_counts": wave8_haiti_regimes_counts(),
            "wave8_haiti_regimes_cohort_counts": (
                wave8_haiti_regimes_cohort_counts()
            ),
            "wave8_haiti_regimes_audit_signature": (
                wave8_haiti_regimes_audit_signature()
            ),
            "wave8_haiti_regimes_final_audit_signature": (
                WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_haiti_regimes_queue_validation": (
                wave8_haiti_regimes_queue_validation
            ),
            "wave8_haiti_regimes_integration_validation": (
                wave8_haiti_regimes_integration_validation
            ),
            "wave8_haiti_regimes_candidate_ids": sorted(
                WAVE8_HAITI_REGIMES_CONTRACT_IDS
            ),
            "wave8_haiti_regimes_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITI_REGIMES_HOLDS.items()
                )
            ],
            "wave8_haiti_regimes_exact_label_funnel_audit": (
                WAVE8_HAITI_REGIMES_FUNNEL_AUDIT
            ),
            "wave8_haiti_regimes_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_haiti_regimes_point_quarantine_additions": sorted(
                WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_haiti_regimes_country_quarantine_additions": sorted(
                WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_haiti_regimes_entities_added": len(
                WAVE8_HAITI_REGIMES_ENTITIES
            ),
            "wave8_haiti_regimes_sources_added": len(
                WAVE8_HAITI_REGIMES_SOURCES
            ),
            "wave8_zulu_forces_counts": wave8_zulu_forces_counts(),
            "wave8_zulu_forces_cohort_counts": wave8_zulu_forces_cohort_counts(),
            "wave8_zulu_forces_audit_signature": (
                wave8_zulu_forces_audit_signature()
            ),
            "wave8_zulu_forces_final_audit_signature": (
                WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_zulu_forces_queue_validation": wave8_zulu_forces_queue_validation,
            "wave8_zulu_forces_integration_validation": (
                wave8_zulu_forces_integration_validation
            ),
            "wave8_zulu_forces_candidate_ids": sorted(
                WAVE8_ZULU_FORCES_CONTRACT_IDS
            ),
            "wave8_zulu_forces_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ZULU_FORCES_HOLDS.items())
            ],
            "wave8_zulu_forces_exact_label_funnel_audit": (
                WAVE8_ZULU_FORCES_FUNNEL_AUDIT
            ),
            "wave8_zulu_forces_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_zulu_forces_point_quarantine_additions": sorted(
                WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_zulu_forces_country_quarantine_additions": sorted(
                WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_zulu_forces_entities_added": len(WAVE8_ZULU_FORCES_ENTITIES),
            "wave8_zulu_forces_sources_added": len(WAVE8_ZULU_FORCES_SOURCES),
            "wave8_montenegro_1796_counts": wave8_montenegro_1796_counts(),
            "wave8_montenegro_1796_cohort_counts": (
                wave8_montenegro_1796_cohort_counts()
            ),
            "wave8_montenegro_1796_audit_signature": (
                wave8_montenegro_1796_audit_signature()
            ),
            "wave8_montenegro_1796_final_audit_signature": (
                WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_montenegro_1796_queue_validation": (
                wave8_montenegro_1796_queue_validation
            ),
            "wave8_montenegro_1796_integration_validation": (
                wave8_montenegro_1796_integration_validation
            ),
            "wave8_montenegro_1796_candidate_ids": sorted(
                WAVE8_MONTENEGRO_1796_CONTRACT_IDS
            ),
            "wave8_montenegro_1796_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MONTENEGRO_1796_HOLDS.items()
                )
            ],
            "wave8_montenegro_1796_exact_label_funnel_audit": (
                WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT
            ),
            "wave8_montenegro_1796_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_montenegro_1796_point_quarantine_additions": sorted(
                WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_montenegro_1796_country_quarantine_additions": sorted(
                WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_montenegro_1796_entities_added": len(
                WAVE8_MONTENEGRO_1796_ENTITIES
            ),
            "wave8_montenegro_1796_sources_added": len(
                WAVE8_MONTENEGRO_1796_SOURCES
            ),
            "wave8_bohemia_counts": wave8_bohemia_counts(),
            "wave8_bohemia_cohort_counts": wave8_bohemia_cohort_counts(),
            "wave8_bohemia_audit_signature": wave8_bohemia_audit_signature(),
            "wave8_bohemia_final_audit_signature": (
                WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_bohemia_queue_validation": wave8_bohemia_queue_validation,
            "wave8_bohemia_integration_validation": (
                wave8_bohemia_integration_validation
            ),
            "wave8_bohemia_candidate_ids": sorted(WAVE8_BOHEMIA_CONTRACT_IDS),
            "wave8_bohemia_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_BOHEMIA_HOLDS.items())
            ],
            "wave8_bohemia_exact_label_funnel_audit": WAVE8_BOHEMIA_FUNNEL_AUDIT,
            "wave8_bohemia_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_bohemia_point_quarantine_additions": sorted(
                WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_bohemia_country_quarantine_additions": sorted(
                WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_bohemia_entities_added": len(WAVE8_BOHEMIA_ENTITIES),
            "wave8_bohemia_sources_added": len(WAVE8_BOHEMIA_SOURCES),
            "wave8_spanish_liberals_counts": wave8_spanish_liberals_counts(),
            "wave8_spanish_liberals_cohort_counts": (
                wave8_spanish_liberals_cohort_counts()
            ),
            "wave8_spanish_liberals_audit_signature": (
                wave8_spanish_liberals_audit_signature()
            ),
            "wave8_spanish_liberals_final_audit_signature": (
                WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_spanish_liberals_queue_validation": (
                wave8_spanish_liberals_queue_validation
            ),
            "wave8_spanish_liberals_integration_validation": (
                wave8_spanish_liberals_integration_validation
            ),
            "wave8_spanish_liberals_candidate_ids": sorted(
                WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
            ),
            "wave8_spanish_liberals_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SPANISH_LIBERALS_HOLDS.items()
                )
            ],
            "wave8_spanish_liberals_exact_label_funnel_audit": (
                WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT
            ),
            "wave8_spanish_liberals_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_spanish_liberals_point_quarantine_additions": sorted(
                WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_spanish_liberals_country_quarantine_additions": sorted(
                WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_spanish_liberals_entities_added": len(
                WAVE8_SPANISH_LIBERALS_ENTITIES
            ),
            "wave8_spanish_liberals_sources_added": len(
                WAVE8_SPANISH_LIBERALS_SOURCES
            ),
            "wave8_achea_counts": wave8_achea_counts(),
            "wave8_achea_cohort_counts": wave8_achea_cohort_counts(),
            "wave8_achea_audit_signature": wave8_achea_audit_signature(),
            "wave8_achea_final_audit_signature": (
                WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_achea_queue_validation": wave8_achea_queue_validation,
            "wave8_achea_integration_validation": (
                wave8_achea_integration_validation
            ),
            "wave8_achea_candidate_ids": sorted(WAVE8_ACHEA_CONTRACT_IDS),
            "wave8_achea_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ACHEA_HOLDS.items())
            ],
            "wave8_achea_exact_label_funnel_audit": WAVE8_ACHEA_FUNNEL_AUDIT,
            "wave8_achea_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_achea_point_quarantine_additions": sorted(
                WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_achea_country_quarantine_additions": sorted(
                WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_achea_entities_added": len(WAVE8_ACHEA_ENTITIES),
            "wave8_achea_sources_added": len(WAVE8_ACHEA_SOURCES),
            "wave8_oran_counts": wave8_oran_counts(),
            "wave8_oran_cohort_counts": wave8_oran_cohort_counts(),
            "wave8_oran_audit_signature": wave8_oran_audit_signature(),
            "wave8_oran_final_audit_signature": (
                WAVE8_ORAN_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_oran_queue_validation": wave8_oran_queue_validation,
            "wave8_oran_integration_validation": (
                wave8_oran_integration_validation
            ),
            "wave8_oran_candidate_ids": sorted(WAVE8_ORAN_CONTRACT_IDS),
            "wave8_oran_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ORAN_HOLDS.items())
            ],
            "wave8_oran_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_oran_exact_label_funnel_audit": WAVE8_ORAN_FUNNEL_AUDIT,
            "wave8_oran_entities_added": 0,
            "wave8_oran_sources_added": len(WAVE8_ORAN_SOURCES),
            "wave8_cheyenne_dog_soldiers_counts": (
                wave8_cheyenne_dog_soldiers_counts()
            ),
            "wave8_cheyenne_dog_soldiers_cohort_counts": (
                wave8_cheyenne_dog_soldiers_cohort_counts()
            ),
            "wave8_cheyenne_dog_soldiers_audit_signature": (
                wave8_cheyenne_dog_soldiers_audit_signature()
            ),
            "wave8_cheyenne_dog_soldiers_final_audit_signature": (
                WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_cheyenne_dog_soldiers_queue_validation": (
                wave8_cheyenne_dog_soldiers_queue_validation
            ),
            "wave8_cheyenne_dog_soldiers_frozen_lane_post_validation": (
                wave8_algiers_cheyenne_post_dog_soldiers_validation
            ),
            "wave8_cheyenne_dog_soldiers_integration_validation": (
                wave8_cheyenne_dog_soldiers_integration_validation
            ),
            "wave8_cheyenne_dog_soldiers_candidate_ids": sorted(
                WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
            ),
            "wave8_cheyenne_dog_soldiers_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS.items()
                )
            ],
            "wave8_cheyenne_dog_soldiers_terminal_exclusions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS.items()
                )
            ],
            "wave8_cheyenne_dog_soldiers_exact_label_funnel_audit": (
                WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT
            ),
            "wave8_cheyenne_dog_soldiers_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_cheyenne_dog_soldiers_point_quarantine_additions": sorted(
                WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_cheyenne_dog_soldiers_country_quarantine_additions": sorted(
                WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_cheyenne_dog_soldiers_entities_added": len(
                WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES
            ),
            "wave8_cheyenne_dog_soldiers_sources_added": len(
                WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES
            ),
            "wave8_libya_metadata": wave8_libya_metadata(),
            "wave8_libya_counts": wave8_libya_counts(),
            "wave8_libya_cohort_counts": wave8_libya_cohort_counts(),
            "wave8_libya_audit_signature": wave8_libya_audit_signature(),
            "wave8_libya_final_audit_signature": (
                WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_libya_queue_validation": wave8_libya_queue_validation,
            "wave8_libya_frozen_chadian_rebels_pre_validation": (
                wave8_libya_frozen_chadian_rebels_pre_validation
            ),
            "wave8_libya_frozen_chadian_rebels_post_validation": (
                wave8_libya_frozen_chadian_rebels_post_validation
            ),
            "wave8_libya_integration_validation": (
                wave8_libya_integration_validation
            ),
            "wave8_libya_candidate_ids": sorted(WAVE8_LIBYA_CONTRACT_IDS),
            "wave8_libya_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_LIBYA_HOLDS.items())
            ],
            "wave8_libya_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_libya_iwbd_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIBYA_IWBD_DISPOSITIONS.items()
                )
            ],
            "wave8_libya_exact_label_funnel_audit": WAVE8_LIBYA_FUNNEL_AUDIT,
            "wave8_libya_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_libya_point_quarantine_additions": sorted(
                WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_libya_country_quarantine_additions": sorted(
                WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_libya_entities_added": len(WAVE8_LIBYA_ENTITIES),
            "wave8_libya_sources_added": len(WAVE8_LIBYA_SOURCES),
            "wave8_kievan_rus_counts": wave8_kievan_rus_counts(),
            "wave8_kievan_rus_cohort_counts": wave8_kievan_rus_cohort_counts(),
            "wave8_kievan_rus_audit_signature": (
                wave8_kievan_rus_audit_signature()
            ),
            "wave8_kievan_rus_final_audit_signature": (
                WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_kievan_rus_queue_validation": (
                wave8_kievan_rus_queue_validation
            ),
            "wave8_kievan_rus_integration_validation": (
                wave8_kievan_rus_integration_validation
            ),
            "wave8_kievan_rus_candidate_ids": sorted(
                WAVE8_KIEVAN_RUS_CONTRACT_IDS
            ),
            "wave8_kievan_rus_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KIEVAN_RUS_HOLDS.items()
                )
            ],
            "wave8_kievan_rus_exact_label_funnel_audit": (
                WAVE8_KIEVAN_RUS_FUNNEL_AUDIT
            ),
            "wave8_kievan_rus_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_kievan_rus_point_quarantine_additions": sorted(
                WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_kievan_rus_country_quarantine_additions": sorted(
                WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_kievan_rus_entities_added": len(WAVE8_KIEVAN_RUS_ENTITIES),
            "wave8_kievan_rus_sources_added": len(WAVE8_KIEVAN_RUS_SOURCES),
            "wave8_carnatic_counts": wave8_carnatic_counts(),
            "wave8_carnatic_cohort_counts": wave8_carnatic_cohort_counts(),
            "wave8_carnatic_audit_signature": wave8_carnatic_audit_signature(),
            "wave8_carnatic_final_audit_signature": (
                WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_carnatic_queue_validation": wave8_carnatic_queue_validation,
            "wave8_carnatic_integration_validation": (
                wave8_carnatic_integration_validation
            ),
            "wave8_carnatic_candidate_ids": sorted(WAVE8_CARNATIC_CONTRACT_IDS),
            "wave8_carnatic_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CARNATIC_HOLDS.items()
                )
            ],
            "wave8_carnatic_legacy_candidate_ids": sorted(
                WAVE8_CARNATIC_LEGACY_IDS
            ),
            "wave8_carnatic_exact_label_funnel_audit": (
                WAVE8_CARNATIC_FUNNEL_AUDIT
            ),
            "wave8_carnatic_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_carnatic_point_quarantine_additions": sorted(
                WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_carnatic_country_quarantine_additions": sorted(
                WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_carnatic_entities_added": len(WAVE8_CARNATIC_ENTITIES),
            "wave8_carnatic_sources_added": len(WAVE8_CARNATIC_SOURCES),
            "wave8_goguryeo_counts": wave8_goguryeo_counts(),
            "wave8_goguryeo_cohort_counts": wave8_goguryeo_cohort_counts(),
            "wave8_goguryeo_audit_signature": wave8_goguryeo_audit_signature(),
            "wave8_goguryeo_final_audit_signature": (
                WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_goguryeo_queue_validation": wave8_goguryeo_queue_validation,
            "wave8_goguryeo_integration_validation": (
                wave8_goguryeo_integration_validation
            ),
            "wave8_goguryeo_candidate_ids": sorted(
                WAVE8_GOGURYEO_CONTRACT_IDS
            ),
            "wave8_goguryeo_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GOGURYEO_HOLDS.items()
                )
            ],
            "wave8_goguryeo_exact_label_funnel_audit": (
                WAVE8_GOGURYEO_FUNNEL_AUDIT
            ),
            "wave8_goguryeo_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_goguryeo_point_quarantine_additions": sorted(
                WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_goguryeo_country_quarantine_additions": sorted(
                WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_goguryeo_entities_added": len(WAVE8_GOGURYEO_ENTITIES),
            "wave8_goguryeo_sources_added": len(WAVE8_GOGURYEO_SOURCES),
            "wave8_fln_counts": wave8_fln_counts(),
            "wave8_fln_cohort_counts": wave8_fln_cohort_counts(),
            "wave8_fln_audit_signature": wave8_fln_audit_signature(),
            "wave8_fln_final_audit_signature": WAVE8_FLN_FINAL_AUDIT_SIGNATURE,
            "wave8_fln_queue_validation": wave8_fln_queue_validation,
            "wave8_fln_integration_validation": wave8_fln_integration_validation,
            "wave8_fln_candidate_ids": sorted(WAVE8_FLN_CONTRACT_IDS),
            "wave8_fln_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_FLN_HOLDS.items())
            ],
            "wave8_fln_exact_label_funnel_audit": WAVE8_FLN_FUNNEL_AUDIT,
            "wave8_fln_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_FLN_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_fln_point_quarantine_additions": sorted(
                WAVE8_FLN_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_fln_country_quarantine_additions": sorted(
                WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_fln_entities_added": len(WAVE8_FLN_ENTITIES),
            "wave8_fln_sources_added": len(WAVE8_FLN_SOURCES),
            "wave8_sindh_counts": wave8_sindh_counts(),
            "wave8_sindh_cohort_counts": wave8_sindh_cohort_counts(),
            "wave8_sindh_audit_signature": wave8_sindh_audit_signature(),
            "wave8_sindh_final_audit_signature": (
                WAVE8_SINDH_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_sindh_queue_validation": wave8_sindh_queue_validation,
            "wave8_sindh_integration_validation": (
                wave8_sindh_integration_validation
            ),
            "wave8_sindh_candidate_ids": sorted(WAVE8_SINDH_CONTRACT_IDS),
            "wave8_sindh_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_SINDH_HOLDS.items())
            ],
            "wave8_sindh_exact_label_funnel_audit": WAVE8_SINDH_FUNNEL_AUDIT,
            "wave8_sindh_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_SINDH_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_sindh_point_quarantine_additions": sorted(
                WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_sindh_country_quarantine_additions": sorted(
                WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_sindh_entities_added": len(WAVE8_SINDH_ENTITIES),
            "wave8_sindh_sources_added": len(WAVE8_SINDH_SOURCES),
            "wave8_oman_counts": wave8_oman_counts(),
            "wave8_oman_cohort_counts": wave8_oman_cohort_counts(),
            "wave8_oman_audit_signature": wave8_oman_audit_signature(),
            "wave8_oman_final_audit_signature": WAVE8_OMAN_FINAL_AUDIT_SIGNATURE,
            "wave8_oman_queue_validation": wave8_oman_queue_validation,
            "wave8_oman_integration_validation": (
                wave8_oman_integration_validation
            ),
            "wave8_oman_candidate_ids": sorted(WAVE8_OMAN_CONTRACT_IDS),
            "wave8_oman_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_OMAN_HOLDS.items())
            ],
            "wave8_oman_exact_label_funnel_audit": WAVE8_OMAN_FUNNEL_AUDIT,
            "wave8_oman_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_OMAN_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_oman_point_quarantine_additions": sorted(
                WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_oman_country_quarantine_additions": sorted(
                WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_oman_entities_added": len(WAVE8_OMAN_ENTITIES),
            "wave8_oman_sources_added": len(WAVE8_OMAN_SOURCES),
            "wave8_irish_civil_war_counts": wave8_irish_civil_war_counts(),
            "wave8_irish_civil_war_cohort_counts": (
                wave8_irish_civil_war_cohort_counts()
            ),
            "wave8_irish_civil_war_audit_signature": (
                wave8_irish_civil_war_audit_signature()
            ),
            "wave8_irish_civil_war_final_audit_signature": (
                WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_irish_civil_war_queue_validation": (
                wave8_irish_civil_war_queue_validation
            ),
            "wave8_irish_civil_war_integration_validation": (
                wave8_irish_civil_war_integration_validation
            ),
            "wave8_irish_civil_war_candidate_ids": sorted(
                WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
            ),
            "wave8_irish_civil_war_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_IRISH_CIVIL_WAR_HOLDS.items()
                )
            ],
            "wave8_irish_civil_war_exact_label_funnel_audit": (
                WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT
            ),
            "wave8_irish_civil_war_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_irish_civil_war_point_quarantine_additions": sorted(
                WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_irish_civil_war_country_quarantine_additions": sorted(
                WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_irish_civil_war_entities_added": len(
                WAVE8_IRISH_CIVIL_WAR_ENTITIES
            ),
            "wave8_irish_civil_war_sources_added": len(
                WAVE8_IRISH_CIVIL_WAR_SOURCES
            ),
            "wave8_bannock_sheepeater_counts": (
                wave8_bannock_sheepeater_counts()
            ),
            "wave8_bannock_sheepeater_cohort_counts": (
                wave8_bannock_sheepeater_cohort_counts()
            ),
            "wave8_bannock_sheepeater_audit_signature": (
                wave8_bannock_sheepeater_audit_signature()
            ),
            "wave8_bannock_sheepeater_final_audit_signature": (
                WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_bannock_sheepeater_queue_validation": (
                wave8_bannock_sheepeater_queue_validation
            ),
            "wave8_bannock_sheepeater_integration_validation": (
                wave8_bannock_sheepeater_integration_validation
            ),
            "wave8_bannock_sheepeater_candidate_ids": sorted(
                WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
            ),
            "wave8_bannock_sheepeater_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_BANNOCK_SHEEPEATER_HOLDS.items()
                )
            ],
            "wave8_bannock_sheepeater_exact_label_funnel_audit": (
                WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT
            ),
            "wave8_bannock_sheepeater_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_bannock_sheepeater_point_quarantine_additions": sorted(
                WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_bannock_sheepeater_country_quarantine_additions": sorted(
                WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_bannock_sheepeater_entities_added": len(
                WAVE8_BANNOCK_SHEEPEATER_ENTITIES
            ),
            "wave8_bannock_sheepeater_sources_added": len(
                WAVE8_BANNOCK_SHEEPEATER_SOURCES
            ),
            "wave8_catholic_rebels_counts": wave8_catholic_rebels_counts(),
            "wave8_catholic_rebels_cohort_counts": (
                wave8_catholic_rebels_cohort_counts()
            ),
            "wave8_catholic_rebels_audit_signature": (
                wave8_catholic_rebels_audit_signature()
            ),
            "wave8_catholic_rebels_final_audit_signature": (
                WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_catholic_rebels_queue_validation": (
                wave8_catholic_rebels_queue_validation
            ),
            "wave8_catholic_rebels_integration_validation": (
                wave8_catholic_rebels_integration_validation
            ),
            "wave8_catholic_rebels_candidate_ids": sorted(
                WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
            ),
            "wave8_catholic_rebels_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CATHOLIC_REBELS_HOLDS.items()
                )
            ],
            "wave8_catholic_rebels_exact_label_funnel_audit": (
                WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT
            ),
            "wave8_catholic_rebels_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_catholic_rebels_point_quarantine_additions": sorted(
                WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_catholic_rebels_country_quarantine_additions": sorted(
                WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_catholic_rebels_entities_added": len(
                WAVE8_CATHOLIC_REBELS_ENTITIES
            ),
            "wave8_catholic_rebels_sources_added": len(
                WAVE8_CATHOLIC_REBELS_SOURCES
            ),
            "wave8_macedon_counts": wave8_macedon_counts(),
            "wave8_macedon_cohort_counts": wave8_macedon_cohort_counts(),
            "wave8_macedon_audit_signature": wave8_macedon_audit_signature(),
            "wave8_macedon_final_audit_signature": (
                WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_macedon_queue_validation": wave8_macedon_queue_validation,
            "wave8_macedon_integration_validation": (
                wave8_macedon_integration_validation
            ),
            "wave8_macedon_candidate_ids": sorted(WAVE8_MACEDON_CONTRACT_IDS),
            "wave8_macedon_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_MACEDON_HOLDS.items())
            ],
            "wave8_macedon_exact_label_funnel_audit": WAVE8_MACEDON_FUNNEL_AUDIT,
            "wave8_macedon_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_macedon_point_quarantine_additions": sorted(
                WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_macedon_country_quarantine_additions": sorted(
                WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_macedon_entities_added": len(WAVE8_MACEDON_ENTITIES),
            "wave8_macedon_sources_added": len(WAVE8_MACEDON_SOURCES),
            "wave8_uzbeks_counts": wave8_uzbeks_counts(),
            "wave8_uzbeks_cohort_counts": wave8_uzbeks_cohort_counts(),
            "wave8_uzbeks_audit_signature": wave8_uzbeks_audit_signature(),
            "wave8_uzbeks_final_audit_signature": (
                WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_uzbeks_queue_validation": wave8_uzbeks_queue_validation,
            "wave8_uzbeks_integration_validation": (
                wave8_uzbeks_integration_validation
            ),
            "wave8_uzbeks_candidate_ids": sorted(WAVE8_UZBEKS_CONTRACT_IDS),
            "wave8_uzbeks_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_UZBEKS_HOLDS.items())
            ],
            "wave8_uzbeks_exact_label_funnel_audit": WAVE8_UZBEKS_FUNNEL_AUDIT,
            "wave8_uzbeks_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_uzbeks_point_quarantine_additions": sorted(
                WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_uzbeks_country_quarantine_additions": sorted(
                WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_uzbeks_entities_added": len(WAVE8_UZBEKS_ENTITIES),
            "wave8_uzbeks_sources_added": len(WAVE8_UZBEKS_SOURCES),
            "wave8_etruria_counts": wave8_etruria_counts(),
            "wave8_etruria_cohort_counts": wave8_etruria_cohort_counts(),
            "wave8_etruria_audit_signature": wave8_etruria_audit_signature(),
            "wave8_etruria_final_audit_signature": (
                WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_etruria_queue_validation": wave8_etruria_queue_validation,
            "wave8_etruria_integration_validation": (
                wave8_etruria_integration_validation
            ),
            "wave8_etruria_candidate_ids": sorted(WAVE8_ETRURIA_CONTRACT_IDS),
            "wave8_etruria_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(WAVE8_ETRURIA_HOLDS.items())
            ],
            "wave8_etruria_exact_label_funnel_audit": WAVE8_ETRURIA_FUNNEL_AUDIT,
            "wave8_etruria_location_quarantine_reasons": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS.items()
                )
            ],
            "wave8_etruria_point_quarantine_additions": sorted(
                WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS
            ),
            "wave8_etruria_country_quarantine_additions": sorted(
                WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "wave8_etruria_entities_added": len(WAVE8_ETRURIA_ENTITIES),
            "wave8_etruria_sources_added": len(WAVE8_ETRURIA_SOURCES),
            "hced_label_pass_input_rows": hced_label_pass["rows_total"],
            "accepted_iwd_wars": len(iwd_events),
            "iwd_parent_wars_total": iwd_aggregation["parents_total"],
            "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
            "iwd_components_attached_to_rated_parents": iwd_aggregation[
                "components_attached"
            ],
            "hced_rejections": dict(sorted(rejections.items())),
            "hced_label_rejections": _declared_rejections(
                hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
            ),
            "hced_label_policy_labels": sorted(HCED_LABEL_POLICIES),
            "hced_faction_labels_staged": sorted(HCED_FACTION_LABELS),
            "hced_pending_split_labels": sorted(HCED_PENDING_SPLIT_LABELS),
            "hced_label_observation_resolutions": hced_label_pass[
                "observation_resolutions"
            ],
            "hced_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(EFFECTIVE_HCED_CURATED_EXCLUSIONS.items())
            ],
            "wave6_pre1500_safe_candidate_ids": list(WAVE6_PRE1500_SAFE_CANDIDATE_IDS),
            "wave6_pre1500_holds": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(WAVE6_PRE1500_HOLD_REASONS.items())
            ],
            "wave6_pre1500_target_entity_ids": sorted(WAVE6_PRE1500_ENTITY_IDS),
            "wave6_pre1500_source_families": list(WAVE6_PRE1500_SOURCE_FAMILY_METADATA),
            "hced_reviewed_crosswalk_identity_candidate_ids": sorted(
                HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS
            ),
            "hced_wave6_reviewed_candidate_ids": sorted(
                WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS
            ),
            "hced_label_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(HCED_LABEL_CURATED_EXCLUSIONS.items())
            ],
            "iwbd_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(EFFECTIVE_IWBD_CURATED_EXCLUSIONS.items())
            ],
            "iwd_curated_parent_exclusions": [
                {"parent_war_id": key, "reason": reason}
                for key, reason in sorted(
                    EFFECTIVE_IWD_CURATED_PARENT_EXCLUSIONS.items()
                )
            ],
            "iwd_reviewed_parent_contract_ids": sorted(
                EFFECTIVE_IWD_REVIEWED_PARENT_CONTRACTS,
                key=int,
            ),
            "iwbd_reviewed_identity_candidate_ids": sorted(
                EFFECTIVE_IWBD_REVIEWED_IDENTITY_BINDINGS
            ),
            "iwbd_reviewed_identity_cohorts": {
                cohort: list(candidate_ids)
                for cohort, candidate_ids in sorted(
                    EFFECTIVE_IWBD_REVIEWED_IDENTITY_COHORTS.items()
                )
            },
            "seed_event_interval_exemptions": [
                {
                    "event_id": key[0],
                    "entity_id": key[1],
                    "event_interval": list(exemption["event_interval"]),
                    "entity_interval": list(exemption["entity_interval"]),
                    "reason": exemption["reason"],
                }
                for key, exemption in sorted(SEED_EVENT_INTERVAL_EXEMPTIONS.items())
            ],
            "ucdp_actor_party_policies": [
                {
                    "conflict_id": conflict_id,
                    "party_label": party,
                    "windows": [list(window) for window in windows],
                }
                for (conflict_id, party), windows in sorted(
                    UCDP_ACTOR_PARTY_POLICIES.items()
                )
            ],
            "ucdp_war_types": UCDP_WAR_TYPES,
            "iwd_rejections": dict(sorted(iwd_rejections.items())),
            "accepted_iwbd_battles": len(iwbd_events),
            "iwbd_battles_total": iwbd_promotion["battles_total"],
            "iwbd_rejections": _declared_rejections(
                iwbd_rejections, IWBD_REJECTION_COUNTERS
            ),
            "accepted_ucdp_events": len(ucdp_events),
            "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
            "ucdp_rejections": _declared_rejections(
                ucdp_rejections, UCDP_REJECTION_COUNTERS
            ),
            "ucdp_curated_exclusions": [
                {"conflict_id": key[0], "episode_number": key[1], "reason": reason}
                for key, reason in sorted(UCDP_CURATED_EXCLUSIONS.items())
            ],
            "ucdp_duplicate_details": ucdp_promotion["duplicate_details"],
            "ucdp_dyad_rows_total": ucdp_promotion["dyad_rows_total"],
            "ucdp_dyad_rows_quarantined_corrupt": ucdp_promotion[
                "dyad_rows_quarantined_corrupt"
            ],
            "ucdp_dyad_terminal_blank_outcome": ucdp_promotion[
                "dyad_terminal_blank_outcome"
            ],
            "source_queue_counts": review_counts,
        },
        "known_limitations": [
            "The release is not a complete census and must not be presented as a definitive all-history ranking.",
            "Strategic war outcomes remain much less complete than tactical engagement outcomes.",
            "HCED winner labels and the Seshat crosswalk are source assertions pending claim-level human review.",
            "Label-resolved HCED events rest on side-name identity policies and exact alias matches rather than the Seshat crosswalk; they carry lower confidence and remain source assertions pending claim-level human review, and the label-policy entries are entity-boundary decisions pending second-reviewer sign-off.",
            "Cliopatria intervals are split at temporal gaps; final historiographic continuity still requires explicit decisions.",
            "Some Cliopatria identity intervals span successive regimes (for example one Cambodia identity covering 1956-2024), so events resolved to them can share a rating line across regime changes until those identities receive explicit curated splits.",
            "Aggregated IWD coalition events use declared uniform defaults for contribution, role, scale, and stakes because the source carries no per-participant data.",
            "IWBD events use declared uniform defaults for scale, stakes, contribution, and role because the source carries no per-battle magnitude data, and IWBD war-level victor codes are ignored: battle records never update strategic outcomes.",
            "Coalition-labelled IWBD battles and sibling-containing spans remain staged unless an exact candidate-keyed reviewed composition or concurrent-distinct relation is present; the current exceptions are Abtao and Mishan only, and both fail closed on source or resolver drift.",
            "IWBD-HCED name and date matches are counted as exclusions only; they are not treated as independent corroboration and no HCED record is modified.",
            "UCDP episode-level termination outcomes may not describe every supporter: secondary parties are recorded without outcomes, and uniform strategic vectors with scale-linked participant uniforms are declared defaults, as with IWD.",
            "The 1967 Arab-Israeli fronts and the 1974 Paracel episode stay staged: the source carries mutually contradictory orientations for the former and a documented side-attribution dispute for the latter.",
            "Ancient, non-literate, small, defeated, and non-European polities remain systematically under-recorded.",
        ],
        "prohibited_interpretation": (
            "Do not treat provisional ratings or unrated registry entries as a definitive ranking "
            "of every country and empire in history."
        ),
    }

    _write_json(release / "entities.json", release_entity_rows)
    _write_json(release / "events.json", all_events)
    _write_json(
        release / "sources.json",
        sorted(sources_by_id.values(), key=lambda row: row["id"]),
    )
    _write_json(release / "metadata.json", metadata)
    _write_json(registry_path, registry)
    return {
        "entities": len(release_entity_rows),
        "rated_entities": len(used_entity_ids),
        "events": len(all_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "candidate_keyed_wave6_hced_events": len(wave6_events),
        "candidate_keyed_wave7_root_hced_events": len(wave7_root_events),
        "candidate_keyed_wave7_central_hced_events": len(wave7_central_events),
        "candidate_keyed_wave7_central_pass2_hced_events": len(
            wave7_central_pass2_events
        ),
        "candidate_keyed_wave7_global_hced_events": len(wave7_global_events),
        "candidate_keyed_wave7_west_hced_events": len(wave7_west_events),
        "candidate_keyed_wave8_african_states_hced_events": len(
            wave8_african_states_events
        ),
        "candidate_keyed_wave8_new_zealand_hced_events": len(
            wave8_new_zealand_events
        ),
        "candidate_keyed_wave8_north_america_hced_events": len(
            wave8_north_america_events
        ),
        "candidate_keyed_wave8_xhosa_hced_events": len(wave8_xhosa_events),
        "candidate_keyed_wave8_polish_audit_hced_events": len(
            wave8_polish_audit_events
        ),
        "candidate_keyed_wave8_namibia_resistance_hced_events": len(
            wave8_namibia_resistance_events
        ),
        "candidate_keyed_wave8_first_saudi_hced_events": len(
            wave8_first_saudi_events
        ),
        "candidate_keyed_wave8_early_states_hced_events": len(
            wave8_early_states_events
        ),
        "candidate_keyed_wave8_judean_revolts_hced_events": len(
            wave8_judean_revolts_events
        ),
        "candidate_keyed_wave8_canadian_resistance_hced_events": len(
            wave8_canadian_resistance_events
        ),
        "candidate_keyed_wave8_wales_hced_events": len(wave8_wales_events),
        "candidate_keyed_wave8_cossack_hced_events": len(wave8_cossack_events),
        "candidate_keyed_wave8_fast17_hced_events": len(wave8_fast17_events),
        "candidate_keyed_wave8_naples_hced_events": len(wave8_naples_events),
        "candidate_keyed_wave8_somali_irish_sa_hced_events": len(
            wave8_somali_irish_sa_events
        ),
        "candidate_keyed_wave8_argentine_independence_hced_events": len(
            wave8_argentine_independence_events
        ),
        "candidate_keyed_wave8_ecuador_independence_hced_events": len(
            wave8_ecuador_independence_events
        ),
        "candidate_keyed_wave8_comanche_hced_events": len(wave8_comanche_events),
        "candidate_keyed_wave8_garibaldi_hced_events": len(wave8_garibaldi_events),
        "candidate_keyed_wave8_algiers_cheyenne_hced_events": len(
            wave8_algiers_cheyenne_events
        ),
        "candidate_keyed_wave8_dagestan_hced_events": len(wave8_dagestan_events),
        "candidate_keyed_wave8_irish_history_hced_events": len(
            wave8_irish_history_events
        ),
        "candidate_keyed_wave8_muslim_forces_hced_events": len(
            wave8_muslim_forces_events
        ),
        "candidate_keyed_wave8_moros_hced_events": len(wave8_moros_events),
        "candidate_keyed_wave8_manchus_hced_events": len(wave8_manchus_events),
        "candidate_keyed_wave8_peruvian_rebels_hced_events": len(
            wave8_peruvian_rebels_events
        ),
        "candidate_keyed_wave8_germany_hced_events": len(wave8_germany_events),
        "candidate_keyed_wave8_seljuks_hced_events": len(wave8_seljuks_events),
        "candidate_keyed_wave8_danish_vikings_hced_events": len(
            wave8_danish_vikings_events
        ),
        "candidate_keyed_wave8_epirus_hced_events": len(wave8_epirus_events),
        "candidate_keyed_wave8_savoy_hced_events": len(wave8_savoy_events),
        "candidate_keyed_wave8_nez_perce_hced_events": len(
            wave8_nez_perce_events
        ),
        "candidate_keyed_wave8_dacia_hced_events": len(wave8_dacia_events),
        "candidate_keyed_wave8_cherokee_hced_events": len(
            wave8_cherokee_events
        ),
        "candidate_keyed_wave8_druze_rebels_hced_events": len(
            wave8_druze_rebels_events
        ),
        "candidate_keyed_wave8_insubrian_gauls_hced_events": len(
            wave8_insubrian_gauls_events
        ),
        "candidate_keyed_wave8_kiowa_hced_events": len(wave8_kiowa_events),
        "candidate_keyed_wave8_uzbekistan_hced_events": len(
            wave8_uzbekistan_events
        ),
        "candidate_keyed_wave8_vietnam_hced_events": len(wave8_vietnam_events),
        "candidate_keyed_wave8_hussites_hced_events": len(wave8_hussites_events),
        "candidate_keyed_wave8_livonian_order_hced_events": len(
            wave8_livonian_order_events
        ),
        "candidate_keyed_wave8_satsuma_hced_events": len(wave8_satsuma_events),
        "candidate_keyed_wave8_rajputs_hced_events": len(wave8_rajputs_events),
        "candidate_keyed_wave8_mamluk_egypt_hced_events": len(
            wave8_mamluk_egypt_events
        ),
        "candidate_keyed_wave8_rebel_barons_hced_events": len(
            wave8_rebel_barons_events
        ),
        "candidate_keyed_wave8_thebes_hced_events": len(wave8_thebes_events),
        "candidate_keyed_wave8_alemanni_hced_events": len(wave8_alemanni_events),
        "candidate_keyed_wave8_madagascar_hced_events": len(
            wave8_madagascar_events
        ),
        "candidate_keyed_wave8_kickapoo_hced_events": len(wave8_kickapoo_events),
        "candidate_keyed_wave8_lordship_isles_hced_events": len(
            wave8_lordship_isles_events
        ),
        "candidate_keyed_wave8_armenia_hced_events": len(wave8_armenia_events),
        "candidate_keyed_wave8_comanches_hced_events": len(wave8_comanches_events),
        "candidate_keyed_wave8_sikh_punjab_hced_events": len(
            wave8_sikh_punjab_events
        ),
        "candidate_keyed_wave8_eritrea_hced_events": len(wave8_eritrea_events),
        "candidate_keyed_wave8_flanders_hced_events": len(wave8_flanders_events),
        "candidate_keyed_wave8_france_bavaria_hced_events": len(
            wave8_france_bavaria_events
        ),
        "candidate_keyed_wave8_eritrean_rebels_hced_events": len(
            wave8_eritrean_rebels_events
        ),
        "candidate_keyed_wave8_inca_rebels_hced_events": len(
            wave8_inca_rebels_events
        ),
        "candidate_keyed_wave8_haitian_rebels_hced_events": len(
            wave8_haitian_rebels_events
        ),
        "candidate_keyed_wave8_kingdom_kandy_hced_events": len(
            wave8_kingdom_kandy_events
        ),
        "candidate_keyed_wave8_hospitallers_hced_events": len(
            wave8_hospitallers_events
        ),
        "candidate_keyed_wave8_murids_hced_events": len(wave8_murids_events),
        "candidate_keyed_wave8_punjabi_sikhs_hced_events": len(
            wave8_punjabi_sikhs_events
        ),
        "candidate_keyed_wave8_modoc_hced_events": len(wave8_modoc_events),
        "candidate_keyed_wave8_sauk_hced_events": len(wave8_sauk_events),
        "candidate_keyed_wave8_ute_hced_events": len(wave8_ute_events),
        "candidate_keyed_wave8_yakima_hced_events": len(wave8_yakima_events),
        "candidate_keyed_wave8_taliban_al_qaeda_hced_events": len(
            wave8_taliban_al_qaeda_events
        ),
        "candidate_keyed_wave8_french_religious_forces_hced_events": len(
            wave8_french_religious_forces_events
        ),
        "candidate_keyed_wave8_chadian_rebels_hced_events": len(
            wave8_chadian_rebels_events
        ),
        "candidate_keyed_wave8_saudi_rashidi_hced_events": len(
            wave8_saudi_rashidi_events
        ),
        "candidate_keyed_wave8_yaqui_hced_events": len(wave8_yaqui_events),
        "candidate_keyed_wave8_egypt_forces_hced_events": len(
            wave8_egypt_forces_events
        ),
        "candidate_keyed_wave8_haiti_regimes_hced_events": len(
            wave8_haiti_regimes_events
        ),
        "candidate_keyed_wave8_zulu_forces_hced_events": len(
            wave8_zulu_forces_events
        ),
        "candidate_keyed_wave8_montenegro_1796_hced_events": len(
            wave8_montenegro_1796_events
        ),
        "candidate_keyed_wave8_bohemia_hced_events": len(wave8_bohemia_events),
        "candidate_keyed_wave8_spanish_liberals_hced_events": len(
            wave8_spanish_liberals_events
        ),
        "candidate_keyed_wave8_achea_hced_events": len(wave8_achea_events),
        "candidate_keyed_wave8_oran_hced_events": len(wave8_oran_events),
        "candidate_keyed_wave8_cheyenne_dog_soldiers_hced_events": len(
            wave8_cheyenne_dog_soldiers_events
        ),
        "candidate_keyed_wave8_libya_hced_events": len(wave8_libya_events),
        "candidate_keyed_wave8_kievan_rus_hced_events": len(
            wave8_kievan_rus_events
        ),
        "candidate_keyed_wave8_carnatic_hced_events": len(
            wave8_carnatic_events
        ),
        "candidate_keyed_wave8_goguryeo_hced_events": len(
            wave8_goguryeo_events
        ),
        "candidate_keyed_wave8_fln_hced_events": len(wave8_fln_events),
        "candidate_keyed_wave8_sindh_hced_events": len(wave8_sindh_events),
        "candidate_keyed_wave8_oman_hced_events": len(wave8_oman_events),
        "wave7_global_identity_migrations": len(WAVE7_GLOBAL_ORANGE_MIGRATIONS),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "provisional_ucdp_events": len(ucdp_events),
        "registry_polities": len(registry_rows),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "hced_rejections": dict(sorted(rejections.items())),
        "hced_label_rejections": _declared_rejections(
            hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
        ),
        "iwd_rejections": dict(sorted(iwd_rejections.items())),
        "iwbd_rejections": _declared_rejections(
            iwbd_rejections, IWBD_REJECTION_COUNTERS
        ),
        "ucdp_rejections": _declared_rejections(
            ucdp_rejections, UCDP_REJECTION_COUNTERS
        ),
    }
