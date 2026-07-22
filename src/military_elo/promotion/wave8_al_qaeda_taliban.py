"""Fail-closed Wave 8 audit for HCED's ``al Qaeda, Taliban`` label.

This lane owns exactly two HCED rows.  Operation Anaconda is corrected from
HCED's internally inconsistent 2001 year fields to 2002 and from raw scale 1
to reviewed battle scale 3.  Operation Mongoose remains a 2003 skirmish, but
its opposing side is deliberately neutral and event-bounded because official
U.S. records identify HIG/Hekmatyar followers while a scholarly archival
history identifies Taliban forces.

Both outcomes are local tactical wins.  Neither becomes a strategic result,
an unknown outcome never becomes a draw, and no discovery row emits a rating.
The lane fingerprints every exact or near candidate reviewed across HCED,
IWBD, IWD, UCDP, and both Wikidata discovery queues.  All ten participant
identities are alias-free one-year formations with no generic inheritance.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_AL_QAEDA_TALIBAN_ALL_CANDIDATE_ID_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_AUDITED_EXCLUSION_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_AUDITED_HOLD_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_CONTRACTS",
    "WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS",
    "WAVE8_AL_QAEDA_TALIBAN_ENTITIES",
    "WAVE8_AL_QAEDA_TALIBAN_EXCLUSION_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES",
    "WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT",
    "WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_HCED_QUEUE_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_HOLD_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_IWBD_QUEUE_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_IWD_QUEUE_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS",
    "WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_REUSED_SOURCE_BOUNDARIES",
    "WAVE8_AL_QAEDA_TALIBAN_RESERVED_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES",
    "WAVE8_AL_QAEDA_TALIBAN_SOURCES",
    "WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS",
    "WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_QUEUE_SHA256",
    "WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS",
    "WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_QUEUE_SHA256",
    "install_wave8_al_qaeda_taliban_entities",
    "install_wave8_al_qaeda_taliban_sources",
    "promote_wave8_al_qaeda_taliban_contracts",
    "validate_wave8_al_qaeda_taliban_funnel",
    "validate_wave8_al_qaeda_taliban_integration_dispositions",
    "validate_wave8_al_qaeda_taliban_queue_contracts",
    "validate_wave8_al_qaeda_taliban_reused_sources",
    "wave8_al_qaeda_taliban_audit_signature",
    "wave8_al_qaeda_taliban_cohort_counts",
    "wave8_al_qaeda_taliban_counts",
    "wave8_al_qaeda_taliban_location_quarantine_additions",
    "wave8_al_qaeda_taliban_metadata",
)


_LANE_NAME = "Wave 8 exact al Qaeda Taliban actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_al_qaeda_taliban"
_EVENT_ID_PREFIX = "hced_wave8_al_qaeda_taliban_"
_EXACT_LABEL = "al qaeda taliban"
_REUSED_ARMY_SOURCE_ID = "wave8_taliban_al_qaeda_army_oef"


WAVE8_AL_QAEDA_TALIBAN_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_AL_QAEDA_TALIBAN_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_AL_QAEDA_TALIBAN_IWD_QUEUE_SHA256 = (
    "0867947dadfb29e93a4697efa308fcf1acd78f90c90f8d860d344ac12dd883fd"
)
WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256: dict[str, str] = {
    "ucdp-actor-26.1-candidates.jsonl": (
        "3cc79938ebac46e1edd99d6116e50610b5753875c023b69128343be816c94788"
    ),
    "ucdp-conflict-26.1-candidates.jsonl": (
        "cbc28e8d06b5fdd83b688ca0be45695e2d2d3bcc59b486d8f92522593ba619ee"
    ),
    "ucdp-dyadic-26.1-candidates.jsonl": (
        "c6e6f7deda305d38e78c987713817410ba3c4045904e22e86e12389fb4a622e4"
    ),
    "ucdp-termination-conflict-candidates.jsonl": (
        "4ce351ab0b0654b341ca8aba42ba82bd5a1955e7c6900351d0f179aae02a3219"
    ),
    "ucdp-termination-dyad-candidates.jsonl": (
        "49c8bead50aa966ee0c70ac023eca9dd81060668db180c1dcfd116c0e827218d"
    ),
}
WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_QUEUE_SHA256 = (
    "5f67b193c58fe06947f965283c534d53a43d8ad8644a15995af39c6d6f55f22b"
)
WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_QUEUE_SHA256 = (
    "9a57ed9dbf4e2c59ea6185c699f00bbea6d07f5c90d5356ce501da449e8d0dd4"
)


WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT: dict[str, Any] = {
    "label": _EXACT_LABEL,
    "event_candidate_id_sha256": (
        "0031583c270791343041dbcbef62486e53976bf50c05765c3df97b3133265474"
    ),
    "events_touched": 2,
    "unresolved_side_attempts": 2,
    "sole_blocker_events": 2,
    "candidate_ids": [],
    "time_valid_candidate_ids": [],
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 2,
    },
    "centuries": {"CE_21": 2},
    "components_touched": 1,
    "components_bridged": 0,
    "rated_counterpart_entities": 1,
}


def _canonical_object_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _event_id(candidate_id: str) -> str:
    return f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_AL_QAEDA_TALIBAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_al_qaeda_taliban_canadian_army_anaconda",
        "The Canadian Army in Afghanistan, Volume I: A Nation Under Fire, 2001-2006",
        "https://www.canada.ca/content/dam/dnd-mdn/army/lineofsight/articleimages/2023/11/CAIA-Vol1-EN.pdf",
        "Canadian Army",
        "official_military_history",
        "canadian_army_afghanistan_volume_1_2023",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_awm_anaconda",
        "Finishing the job",
        "https://www.awm.gov.au/wartime/104/finishing-the-job",
        "Australian War Memorial",
        "official_military_history_article",
        "australian_war_memorial_anaconda_2023",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_hansard_anaconda",
        "Afghanistan: Lords Chamber, 25 March 2002",
        "https://hansard.parliament.uk/Lords/2002-03-25/debates/5c2ae04d-4e39-4503-9354-89a8847876ce/LordsChamber",
        "UK Parliament",
        "official_parliamentary_record",
        "uk_hansard_afghanistan_2002_03_25",
    ),
    _source(
        "wave8_al_qaeda_taliban_oxford_anaconda_review",
        "Operation Anaconda",
        "https://doi.org/10.1093/ohr/ohs065",
        "The Oral History Review, Oxford University Press",
        "peer_reviewed_history_article",
        "caruso_ohr_anaconda_2012",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_army_oef_2002_2005",
        "Operation Enduring Freedom, March 2002-April 2005",
        "https://www.govinfo.gov/content/pkg/GOVPUB-D114-PURL-gpo39933/pdf/GOVPUB-D114-PURL-gpo39933.pdf",
        "U.S. Army Center of Military History",
        "official_military_history",
        "neumann_mundey_mikolashek_army_cmh_2013",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_dvids_mongoose_0205",
        "Cave-Clearing Ops Proceed in Spin Boldak Area",
        "https://www.dvidshub.net/news/printable/532087",
        "American Forces Press Service",
        "contemporaneous_official_defense_dispatch",
        "american_forces_press_service_mongoose_2003",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_dvids_mongoose_0211",
        "12 Afghans Surrender After Firefight",
        "https://www.dvidshub.net/news/532121/12-afghans-surrender-after-firefight",
        "American Forces Press Service",
        "contemporaneous_official_defense_dispatch",
        "american_forces_press_service_mongoose_2003",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_sjms_epaf",
        "Joining Forces Over Afghanistan: The EPAF Experiment",
        "https://sjms.nu/articles/10.31374/sjms.101",
        "Scandinavian Journal of Military Studies",
        "peer_reviewed_archival_history_article",
        "van_der_vegt_sjms_epaf_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_al_qaeda_taliban_senate_afghanistan_2003",
        "The Reconstruction of Afghanistan: An Update",
        "https://www.congress.gov/108/chrg/CHRG-108shrg87575/CHRG-108shrg87575.pdf",
        "U.S. Senate Committee on Foreign Relations",
        "official_congressional_hearing",
        "us_senate_foreign_relations_afghanistan_2003",
        outcome=True,
        crosscheck=True,
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_AL_QAEDA_TALIBAN_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}
_SOURCE_FAMILY_BY_ID[_REUSED_ARMY_SOURCE_ID] = "folse_army_cmh_oef_2022"


WAVE8_AL_QAEDA_TALIBAN_REUSED_SOURCE_BOUNDARIES: dict[str, dict[str, Any]] = {
    _REUSED_ARMY_SOURCE_ID: {
        "canonical_object_sha256": (
            "e21ec79c3ffa7b8874eb35737aed50e88c4bfc3b757f9ef525c508ba811699e6"
        ),
        "source_family_id": "folse_army_cmh_oef_2022",
        "publisher": "U.S. Army Center of Military History",
        "disposition": "reuse_existing_authoritative_source_without_duplication",
    }
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    boundary_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or passed to generic Afghanistan, "
            "United States, United Kingdom, Australia, Canada, Taliban, "
            "al-Qaeda, Hizb-i Islami Gulbuddin, another Afghan faction, or the "
            "strategic War in Afghanistan."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_ANACONDA_US = "us_cjtf_mountain_anaconda_force_2002"
_ANACONDA_AFGHAN = "zia_haidar_afghan_militia_anaconda_force_2002"
_ANACONDA_CANADIAN = "canadian_3_ppcli_sniper_anaconda_contingent_2002"
_ANACONDA_AUSTRALIAN = "australian_sas_anaconda_contingent_2002"
_ANACONDA_AQ = "al_qaeda_shahi_kot_force_2002"
_ANACONDA_TALIBAN = "taliban_shahi_kot_contingent_2002"
_MONGOOSE_US = "us_mongoose_ground_force_2003"
_MONGOOSE_AFGHAN = "afghan_militia_mongoose_contingent_2003"
_MONGOOSE_EPAF = "epaf_mongoose_strike_detachment_2003"
_MONGOOSE_OPPOSITION = "adi_ghar_mongoose_opposition_force_2003"


WAVE8_AL_QAEDA_TALIBAN_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ANACONDA_US,
        "U.S. CJTF Mountain force in Operation Anaconda (2002)",
        "event_bounded_joint_task_force",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to the U.S. formations operating under CJTF Mountain during the reviewed Anaconda principal-combat phase.",
        [_REUSED_ARMY_SOURCE_ID, "wave8_al_qaeda_taliban_oxford_anaconda_review"],
    ),
    _entity(
        _ANACONDA_AFGHAN,
        "Zia-Haidar Afghan militia force in Operation Anaconda (2002)",
        "event_bounded_afghan_militia",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to the Afghan militia columns directly committed to the Shahi Kot assault; it is not a state or nationwide Afghan force.",
        [_REUSED_ARMY_SOURCE_ID, "wave8_al_qaeda_taliban_oxford_anaconda_review"],
    ),
    _entity(
        _ANACONDA_CANADIAN,
        "3 PPCLI sniper contingent in Operation Anaconda (2002)",
        "event_bounded_military_contingent",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to the Canadian 3 PPCLI sniper participation directly documented for Operation Anaconda.",
        ["wave8_al_qaeda_taliban_canadian_army_anaconda"],
    ),
    _entity(
        _ANACONDA_AUSTRALIAN,
        "Australian SAS contingent in Operation Anaconda (2002)",
        "event_bounded_special_operations_contingent",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to Australian SAS participation directly documented for Operation Anaconda.",
        ["wave8_al_qaeda_taliban_awm_anaconda"],
    ),
    _entity(
        _ANACONDA_AQ,
        "Al-Qaeda Shahi Kot force in Operation Anaconda (2002)",
        "event_bounded_nonstate_formation",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to al-Qaeda forces defending the Anaconda operational area; enemy escape prevents any strategic continuity claim.",
        [_REUSED_ARMY_SOURCE_ID, "wave8_al_qaeda_taliban_oxford_anaconda_review"],
    ),
    _entity(
        _ANACONDA_TALIBAN,
        "Taliban Shahi Kot contingent in Operation Anaconda (2002)",
        "event_bounded_nonstate_contingent",
        2002,
        "Shahi Kot Valley, Paktia, Afghanistan",
        "Bounded to separately attested Taliban elements defending the Anaconda operational area.",
        [_REUSED_ARMY_SOURCE_ID, "wave8_al_qaeda_taliban_oxford_anaconda_review"],
    ),
    _entity(
        _MONGOOSE_US,
        "U.S. ground force in Operation Mongoose (2003)",
        "event_bounded_ground_force",
        2003,
        "Adi/Hade Ghar Mountains near Spin Boldak, Afghanistan",
        "Bounded to the U.S. Special Forces, 82d Airborne, infantry, and engineer elements clearing the Mongoose cave complex.",
        [
            "wave8_al_qaeda_taliban_army_oef_2002_2005",
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_dvids_mongoose_0211",
        ],
    ),
    _entity(
        _MONGOOSE_AFGHAN,
        "Afghan militia contingent in Operation Mongoose (2003)",
        "event_bounded_afghan_militia",
        2003,
        "Adi/Hade Ghar Mountains near Spin Boldak, Afghanistan",
        "Bounded to the Afghan militia directly accompanying coalition cave-clearing forces in Operation Mongoose.",
        [
            "wave8_al_qaeda_taliban_army_oef_2002_2005",
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
        ],
    ),
    _entity(
        _MONGOOSE_EPAF,
        "EPAF strike detachment supporting Operation Mongoose (2003)",
        "event_bounded_multinational_air_detachment",
        2003,
        "Air operations over the Adi Ghar area, Afghanistan",
        "Bounded to the Norwegian, Danish, and Dutch EPAF strike participation documented for Mongoose; it is one integrated event contingent, not three generic state actors.",
        [
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_sjms_epaf",
        ],
    ),
    _entity(
        _MONGOOSE_OPPOSITION,
        "Adi Ghar opposition force in Operation Mongoose (2003)",
        "event_bounded_disputed_nonstate_force",
        2003,
        "Adi/Hade Ghar Mountains near Spin Boldak, Afghanistan",
        (
            "Bounded neutrally to the force fought in the Mongoose cave complex. "
            "The U.S. Army history and contemporaneous defense dispatches identify "
            "HIG or Hekmatyar followers, while the peer-reviewed EPAF archival "
            "history identifies Taliban; the conflict is preserved and not resolved "
            "into a broad alias."
        ),
        [
            "wave8_al_qaeda_taliban_army_oef_2002_2005",
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_dvids_mongoose_0211",
            "wave8_al_qaeda_taliban_sjms_epaf",
        ],
    ),
)


WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES: dict[str, str] = {
    "hced-Operation Anaconda2002-1": (
        "1ea7a5ce4a1046bff20415235654d91dec102b2c6e6743bcee03852531a58981"
    ),
    "hced-Operation Mongoose2003-1": (
        "005bfbacf0527db7d168b6dcd891aa8c227005b6d3338e2580dc92926da7c39f"
    ),
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    date_precision: str,
    granularity: str,
    **date_bounds: Any,
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": year,
        "year_high": year,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        **date_bounds,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    date_source_ids: Iterable[str],
    audit_note: str,
    actor_boundary_note: str,
    *,
    confidence: float,
    expected_scale_level: int,
    source_date_override: bool,
    source_scale_override: bool,
    actor_override: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    date_sources = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "civil_war_foreign_intervention",
        "confidence": confidence,
        "expected_scale_level": expected_scale_level,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "date_source_ids": date_sources,
        "cohort": "afghanistan_2002_2003_tactical",
        "disposition": "promote",
        "source_date_override": source_date_override,
        "source_scale_override": source_scale_override,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": actor_override,
        "actor_boundary_note": actor_boundary_note,
        "outcome_scope": "local_tactical_objective_only",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "owner_event_id": _event_id(candidate_id),
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_AL_QAEDA_TALIBAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Operation Anaconda2002-1": _contract(
        "hced-Operation Anaconda2002-1",
        _canonical(
            "Operation Anaconda",
            2002,
            (
                "2-11 March 2002 principal combat; ridge clearance through "
                "18 March and operation over by 19 March"
            ),
            "day_range_source_variance",
            "principal_combat_phase_of_named_multi_phase_shahi_kot_operation",
            principal_start_date="2002-03-02",
            principal_end_date="2002-03-11",
            clearance_through_date="2002-03-18",
            operation_over_by_date="2002-03-19",
        ),
        [_ANACONDA_US, _ANACONDA_AFGHAN, _ANACONDA_CANADIAN, _ANACONDA_AUSTRALIAN],
        [_ANACONDA_AQ, _ANACONDA_TALIBAN],
        [
            _REUSED_ARMY_SOURCE_ID,
            "wave8_al_qaeda_taliban_awm_anaconda",
            "wave8_al_qaeda_taliban_canadian_army_anaconda",
            "wave8_al_qaeda_taliban_hansard_anaconda",
            "wave8_al_qaeda_taliban_oxford_anaconda_review",
        ],
        [
            _REUSED_ARMY_SOURCE_ID,
            "wave8_al_qaeda_taliban_awm_anaconda",
            "wave8_al_qaeda_taliban_canadian_army_anaconda",
            "wave8_al_qaeda_taliban_oxford_anaconda_review",
        ],
        [_REUSED_ARMY_SOURCE_ID, "wave8_al_qaeda_taliban_canadian_army_anaconda"],
        (
            "The reviewed coalition cleared the principal Shahi Kot objectives, "
            "but many opposing fighters escaped. Only limited tactical field "
            "control and the named operation's local objective are rated; no "
            "strategic defeat of al-Qaeda or the Taliban is inferred. Takur Ghar "
            "is nested inside this owner and is not rated again."
        ),
        (
            "Directly attested U.S., Afghan militia, Canadian 3 PPCLI sniper, "
            "and Australian SAS formations are emitted. HCED's broad United "
            "Kingdom token and context-only coalition states are not invented "
            "as equal-weight tactical participants."
        ),
        confidence=0.84,
        expected_scale_level=3,
        source_date_override=True,
        source_scale_override=True,
        actor_override="source_attested_alias_free_event_bounded_formations",
    ),
    "hced-Operation Mongoose2003-1": _contract(
        "hced-Operation Mongoose2003-1",
        _canonical(
            "Operation Mongoose",
            2003,
            "27 January-at least 11 February 2003",
            "open_day_range_source_variance",
            "adi_hade_ghar_cave_complex_assault_and_clearance_near_spin_boldak",
            initial_contact_date="2003-01-27",
            organized_clearance_start_date="2003-01-28",
            last_attested_date="2003-02-11",
            closure_unknown=True,
        ),
        [_MONGOOSE_US, _MONGOOSE_AFGHAN, _MONGOOSE_EPAF],
        [_MONGOOSE_OPPOSITION],
        [
            "wave8_al_qaeda_taliban_army_oef_2002_2005",
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_dvids_mongoose_0211",
            "wave8_al_qaeda_taliban_senate_afghanistan_2003",
            "wave8_al_qaeda_taliban_sjms_epaf",
        ],
        [
            "wave8_al_qaeda_taliban_army_oef_2002_2005",
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_dvids_mongoose_0211",
            "wave8_al_qaeda_taliban_senate_afghanistan_2003",
            "wave8_al_qaeda_taliban_sjms_epaf",
        ],
        [
            "wave8_al_qaeda_taliban_dvids_mongoose_0205",
            "wave8_al_qaeda_taliban_dvids_mongoose_0211",
            "wave8_al_qaeda_taliban_sjms_epaf",
        ],
        (
            "Coalition forces entered and cleared the cave complex and seized "
            "materiel. Only that local sanctuary and cave-clearance result is "
            "rated. The exact closure is unknown after the 11 February winding-"
            "down report, and neither the wider insurgency nor the Afghanistan "
            "war receives a strategic result."
        ),
        (
            "The opposing force remains a neutral event-bounded identity. The "
            "official Army history and contemporaneous defense dispatches identify "
            "HIG/Hekmatyar followers; the scholarly EPAF history calls the force "
            "Taliban. No HIG, Taliban, or al-Qaeda generic actor inherits the rating."
        ),
        confidence=0.78,
        expected_scale_level=1,
        source_date_override=False,
        source_scale_override=False,
        actor_override="disputed_source_preserving_event_bounded_opposition_force",
    ),
}


WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS = frozenset(
    WAVE8_AL_QAEDA_TALIBAN_CONTRACTS
)


def _disposition(
    raw_row_sha256: str,
    source: str,
    disposition: str,
    boundary_note: str,
    *,
    owner_event_id: str | None = None,
    nesting_owner_event_id: str | None = None,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": raw_row_sha256,
        "source": source,
        "disposition": disposition,
        "owner_event_id": owner_event_id,
        "nesting_owner_event_id": nesting_owner_event_id,
        "automated_rating_authorized": False,
        "boundary_note": boundary_note,
    }


_OLD_LANE_PREFIX = "hced_wave8_taliban_al_qaeda_"
WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Kabul1996-1": _disposition(
        "1b4e5f7d13f1dbad2bfed1ed96f96d78098ed15fe07b45ff614b8ab5e120f224",
        "hced",
        "hold_for_exact_taliban_lane",
        "A distinct 1996 single-Taliban-label civil-war event; this lane neither rates nor aliases it.",
    ),
    "hced-Kabul2001-1": _disposition(
        "71db0d14c3a117ac25349bad9173f51eee4ea9578472f2cbda82d13cc9c83233",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The separately released capture of Kabul is not Anaconda or Mongoose.",
        owner_event_id="hced_label_hced_kabul2001_1",
    ),
    "hced-Kandahar2001-1": _disposition(
        "bd54205d98c29e082856703a277c0063e1600143e89edf53e61f31dda0e57e26",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The separately released Kandahar surrender is not Anaconda or Mongoose.",
        owner_event_id="hced_label_hced_kandahar2001_1",
    ),
    "hced-Kunduz2001-1": _disposition(
        "bd4b2a3a84688c4d5c75422a4622193b8fca5369ce4a83897f56a9720600e6b8",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The 2001 Kunduz tactical event belongs to the exact Taliban/al-Qaeda lane.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_kunduz2001_1",
    ),
    "hced-Mazar-i-Sharif2001-1": _disposition(
        "c0f532d8be75594c945830dd7ded3b408792c1992d7413aeeef56b2f00ee7401",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The 2001 Mazar-e Sharif tactical event belongs to the exact Taliban/al-Qaeda lane.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_mazar_i_sharif2001_1",
    ),
    "hced-Operation Anaconda2002-1": _disposition(
        WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES["hced-Operation Anaconda2002-1"],
        "hced",
        "promote_canonical_hced_owner",
        "Promote once with explicit 2002 year and battle-scale overrides.",
        owner_event_id=_event_id("hced-Operation Anaconda2002-1"),
    ),
    "hced-Operation Mongoose2003-1": _disposition(
        WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES["hced-Operation Mongoose2003-1"],
        "hced",
        "promote_canonical_hced_owner",
        "Promote once with a disputed, neutrally named event-bounded opposition force.",
        owner_event_id=_event_id("hced-Operation Mongoose2003-1"),
    ),
    "hced-Qala-i-Jangi2001-1": _disposition(
        "be36eaed6345c599d4255dff2d6c8a15d2a0ba1eafd24dd09b0ba1fdb3f7c7f7",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The 2001 Qala-i-Jangi tactical event belongs to the exact Taliban/al-Qaeda lane.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_qala_i_jangi2001_1",
    ),
    "hced-Tora Bora2001-1": _disposition(
        "0565c9f3aec81a775e512a2ea50de30752ccc12069f54929d5fe2f0059267c03",
        "hced",
        "exclude_from_lane_distinct_existing_owner",
        "The 2001 Tora Bora tactical event belongs to the exact Taliban/al-Qaeda lane.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_tora_bora2001_1",
    ),
}


WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-225-87-1698": _disposition(
        "6ea7d620b53b198a0c6884b3e4387ed2ae74d54a069f108e7d347e2abb3d7b2c",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Mazar-i-Sharif IWBD twin; no second rating.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_mazar_i_sharif2001_1",
    ),
    "iwbd-225-87-1699": _disposition(
        "345868175fb282599838bf6c62b0bbbabef840270c3bfe390f572f453d87417e",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Kabul IWBD twin; no second rating.",
        owner_event_id="hced_label_hced_kabul2001_1",
    ),
    "iwbd-225-87-1700": _disposition(
        "1b5423dd77f2941791954d22ae82c0bf093478c4eb9e99da6151e9174b74d16b",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Kunduz IWBD twin; no second rating.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_kunduz2001_1",
    ),
    "iwbd-225-87-1701": _disposition(
        "30d81e05299d516ca86a57cb4b0f0649c72d4ab57bfb8e35e4904c09c1376b50",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Qala-i-Jangi IWBD twin; no second rating.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_qala_i_jangi2001_1",
    ),
    "iwbd-225-87-1702": _disposition(
        "774004b8eac580fb01b50561bab47a788e0ebf2deff72f0f170328dbfb7f40e4",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Kandahar IWBD twin; no second rating.",
        owner_event_id="hced_label_hced_kandahar2001_1",
    ),
    "iwbd-225-87-1703": _disposition(
        "c056c6407ca0f1a14fd91bcd167fe1dce31813dcfccbabad19c66c97c5298485",
        "iwbd",
        "exclude_duplicate_of_existing_hced_owner",
        "Tora Bora IWBD twin; no second rating.",
        owner_event_id=f"{_OLD_LANE_PREFIX}hced_tora_bora2001_1",
    ),
}


_IWD_HASHES = {
    "iwd-243": "26db0de6acb6f87ceb6018251cd8d0ca3d8b479ca93bebccdb77a9b4dc4928e9",
    "iwd-244": "ab7f14d3f0c311183acc0b50822a4649f9c4e2f06caa181ad951177048b35eae",
    "iwd-245": "a8eac6b91ed4e6b64d675873ec9367b2b2610b941705f7e0cbb8b549f65b4422",
    "iwd-246": "f208b297ce41740a99013c8c8beb9c90f9507367e8663e5ae1c809e280ec1b5d",
    "iwd-247": "cef1d9f8df920986fa9323d32b32fcbdd54256017927ab080aeceecc8ca71157",
}
WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    candidate_id: _disposition(
        row_hash,
        "iwd-1.21",
        "hold_strategic_component_under_existing_war_owner",
        (
            "Parent war 87 is strategic 2001 coalition participation, not an "
            "Anaconda or Mongoose tactical outcome; retain staged under the "
            "existing War in Afghanistan owner."
        ),
        nesting_owner_event_id="afghanistan_war_2001_2021",
    )
    for candidate_id, row_hash in _IWD_HASHES.items()
}


_UCDP_HASHES = {
    "ucdp-actor-26.1-3--3": "c799dbc7fc135a92cc124226c422b6f41c50c1aaab4e161a414bc11d9ecf8a8f",
    "ucdp-actor-26.1-130--130": "f68ebfe14cc94bb7de5063483bd31d4486dafb40466a1c10b450ea4023c69d09",
    "ucdp-actor-26.1-296--296": "215b47f4b589c4377d573603cbd7efd2d6c60147a2d6b50ea3af483ddb770916",
    "ucdp-actor-26.1-300--300": "e5e12da37e443465becc355f609cc7274eb496529233d0e3c93a5dcf7eb5c504",
    "ucdp-actor-26.1-755--755": "57895819a38e40690492d86089687c2978f7272a79afc170bac363163fac5bc8",
    "ucdp-conflict-26.1-333-2001-1715": "7ca7b4ec1017476e3c048cd059524052edc19f640bb16eea0e54f4a68811deaa",
    "ucdp-conflict-26.1-418-2001-2388": "76ba1738bcfb205d951294abe791a8c5bf2038a9913e6a5c5f70eab31a658c58",
    "ucdp-dyadic-26.1-736-2001-2113": "81476d93b029414b7b06fea8278bfe125c52922fe7bd93b760f1facc1c893583",
    "ucdp-dyadic-26.1-878-2001-2754": "4270f6a9e0011326dbff943f5eb9d06c9dcd07316bf65b0b2c7cab20b52ced28",
    "ucdp-termination-conflict-333-1691": "226a79a6015c95241e337cda420b3766e5938c46579520b96616150a3209cc2a",
    "ucdp-termination-conflict-418-2358": "ca6276768e464a4d9e622ea835857e2dd8d6f255d631431482ad9756d41a65e5",
    "ucdp-termination-dyad-333-2102": "6a5975df7513155c5f0c6b987f3f2a31383fc55dab666f19773ffe3a430f69b4",
    "ucdp-termination-dyad-418-2734": "a91f1a9e89ccac9d242d252f7ccc33d0d09ea202902227b1775121c8612d2653",
    "ucdp-conflict-26.1-418-2002-2389": "8828b9011902f01b0285db8e54fd0c417e257ca33d9db3ce9432a4d5b984243e",
    "ucdp-dyadic-26.1-878-2002-2755": "9301eb1bc7a2566f29f4988420a9e3274430481ffacbbfd49c306e6710c07c9f",
    "ucdp-termination-conflict-418-2359": "ae18ca8057a39de86030a1e072006bb00f62778971c71e6845379fefa1148a30",
    "ucdp-termination-dyad-418-2735": "38deb0f16843eeb1624f460d7f0ca023e59bd916f3f98f18658b9763d32ceac8",
    "ucdp-conflict-26.1-333-2003-1717": "15b10ac0a18897ae430dc988b7f00053489691f5ec43b0327e8e03cb96a74ff2",
    "ucdp-dyadic-26.1-726-2003-2035": "41262aa7affca06b8f052271e4751fca75104393ca35d5d139695239b739d95c",
    "ucdp-dyadic-26.1-735-2003-2095": "c63c51b3b0510c8f5ccba2ce9fbb416ba0c2b86377d68cc3db7ac9cafb03c156",
    "ucdp-conflict-26.1-418-2003-2394": "696c3bbb8c32139234ba2a66efac8bce17e5f9aac0d6fb54b4344eaf0c316302",
    "ucdp-dyadic-26.1-878-2003-2756": "c4e62925d0fd4ef9baad4045ee66ad3b77ecc3a9a918539b0f2eb5b4d7a5270e",
    "ucdp-termination-conflict-333-1693": "9fb26cf0a89e6fc2d30b1c06a3d92dd8b0d21a4170b508deeddbe8eee828085d",
    "ucdp-termination-dyad-333-2018": "67bbeb57daf2af2442dadfd45add533eac77a68dbc1fe74b864665dce731f054",
    "ucdp-termination-dyad-333-2078": "f36067d86505bc1d6786688aa9378849dcd6346dfb327448a80f1d44a7beda57",
    "ucdp-termination-conflict-418-2360": "22d527b6fbad25aff6dbf28bdc0c074142b8912a61d29d3b67f2a5fddff42a70",
    "ucdp-termination-dyad-418-2736": "ca13c5bf511a39e1956b4beda94a7d6633a6832c77b47dabc68f69e29ce3a701",
}


def _ucdp_scope(candidate_id: str) -> str:
    if candidate_id.startswith("ucdp-actor"):
        return "actor_registry_context_only"
    if candidate_id.startswith("ucdp-conflict"):
        return "annual_strategic_conflict_context_only"
    if candidate_id.startswith("ucdp-dyadic"):
        return "annual_strategic_dyad_context_only"
    if "termination-conflict" in candidate_id:
        return "strategic_conflict_episode_context_only"
    return "strategic_dyad_episode_context_only"


WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        **_disposition(
            row_hash,
            "ucdp",
            "hold_context_not_tactical_outcome",
            (
                "Actor, annual-conflict, dyad, or termination context cannot "
                "establish the bounded participants or local outcome of Anaconda "
                "or Mongoose and remains nonemitting."
            ),
            nesting_owner_event_id=(
                None
                if candidate_id.startswith("ucdp-actor") or "-418-" in candidate_id
                else "afghanistan_war_2001_2021"
            ),
        ),
        "scope": _ucdp_scope(candidate_id),
    }
    for candidate_id, row_hash in _UCDP_HASHES.items()
}


WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "Q1476042": {
        **_disposition(
            "1b623e43d6fa543ba9c4a1b019d20dc0c9c2bed43687e228c1bbc9cab5f4d8c8",
            "wikidata-battles",
            "exclude_duplicate_discovery_record",
            (
                "Operation Anaconda discovery record has no winner. Its "
                "2002-01-01 timestamp is year-precision serialization, not a "
                "1 January battle date, and HCED is the canonical owner."
            ),
            owner_event_id=_event_id("hced-Operation Anaconda2002-1"),
        ),
        "wikidata_time_precision": "year_only_not_january_1",
    },
    "Q4872492": _disposition(
        "94cb8f37e0095c271b5767a702ddd57d97111035ecedf690f58e7bbd07708f1e",
        "wikidata-battles",
        "exclude_nested_constituent_no_second_rating",
        "Takur Ghar is a constituent action nested inside the Anaconda owner.",
        nesting_owner_event_id=_event_id("hced-Operation Anaconda2002-1"),
    ),
    "Q281145": _disposition(
        "c0cba57f036ce82caf1fc70ce195127bb23725158b9167d1a13cd58a90859b58",
        "wikidata-battles",
        "exclude_lexical_false_positive",
        "The 2007 Battle of Firebase Anaconda is a distinct later event.",
    ),
}
WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"hced:{candidate_id}": copy.deepcopy(disposition)
        for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS.items()
    },
    **{
        f"iwbd:{candidate_id}": copy.deepcopy(disposition)
        for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS.items()
    },
    **{
        f"iwd:{candidate_id}": copy.deepcopy(disposition)
        for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS.items()
    },
    **{
        f"ucdp:{candidate_id}": copy.deepcopy(disposition)
        for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS.items()
    },
    **{
        f"wikidata_battle:{candidate_id}": copy.deepcopy(disposition)
        for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS.items()
    },
}


WAVE8_AL_QAEDA_TALIBAN_AUDITED_HOLD_IDS = frozenset(
    {
        candidate_id
        for dispositions in (
            WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS,
        )
        for candidate_id, item in dispositions.items()
        if str(item["disposition"]).startswith("hold")
    }
)
WAVE8_AL_QAEDA_TALIBAN_AUDITED_EXCLUSION_IDS = frozenset(
    {
        candidate_id
        for dispositions in (
            WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
        )
        for candidate_id, item in dispositions.items()
        if str(item["disposition"]).startswith("exclude")
    }
)
WAVE8_AL_QAEDA_TALIBAN_HOLD_IDS: frozenset[str] = frozenset()
WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS: frozenset[str] = frozenset()
WAVE8_AL_QAEDA_TALIBAN_EXCLUSION_IDS = (
    WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS
)
WAVE8_AL_QAEDA_TALIBAN_RESERVED_IDS = frozenset(
    WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
    | WAVE8_AL_QAEDA_TALIBAN_HOLD_IDS
    | WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS
)
_ALL_AUDITED_CANDIDATE_IDS = frozenset(
    {
        candidate_id
        for dispositions in (
            WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS,
        )
        for candidate_id in dispositions
    }
)
WAVE8_AL_QAEDA_TALIBAN_ALL_CANDIDATE_ID_SHA256 = (
    "c8b5ade046e1eb3be286d828f2a1fe6b3b7e2178be85f1656e39d0af80cf981e"
)
WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS: dict[str, dict[str, int]] = {
    "hced": {"promote": 2, "hold": 1, "exclude": 6, "total": 9},
    "iwbd": {"promote": 0, "hold": 0, "exclude": 6, "total": 6},
    "iwd": {"promote": 0, "hold": 5, "exclude": 0, "total": 5},
    "ucdp": {"promote": 0, "hold": 27, "exclude": 0, "total": 27},
    "wikidata_battle": {"promote": 0, "hold": 0, "exclude": 3, "total": 3},
    "wikidata_generic": {"promote": 0, "hold": 0, "exclude": 0, "total": 0},
    "all": {"promote": 2, "hold": 33, "exclude": 15, "total": 50},
}


WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
)
WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS,
}
WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS: dict[str, str] = {
    "hced-Operation Anaconda2002-1": (
        "hced-Operation Anaconda2002-1\t"
        "hced_wave8_al_qaeda_taliban_hced_operation_anaconda2002_1\t"
        "geometry\tbroad_campaign_centroid_proxy"
    ),
    "hced-Operation Mongoose2003-1": (
        "hced-Operation Mongoose2003-1\t"
        "hced_wave8_al_qaeda_taliban_hced_operation_mongoose2003_1\t"
        "geometry\tcandidate_keyed_point_not_independently_verified"
    ),
}
WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Operation Anaconda2002-1": {
        "actions": ["withhold_point"],
        "retained_country": "Afghanistan",
        "reason_code": "broad_campaign_centroid_proxy",
        "reason": (
            "HCED's point is a broad Shahi Kot operational-area proxy, not an "
            "independently verified footprint for the reviewed principal phase."
        ),
    },
    "hced-Operation Mongoose2003-1": {
        "actions": ["withhold_point"],
        "retained_country": "Afghanistan",
        "reason_code": "candidate_keyed_point_not_independently_verified",
        "reason": (
            "The candidate-keyed point is not independently verified to the "
            "Adi/Hade Ghar cave-complex footprint."
        ),
    },
}


WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES: dict[
    str, dict[str, Any]
] = {
    "afghanistan_war_2001_2021": {
        "canonical_object_sha256": "4357141a51b0d15fee16a22853b6f9d6a03263d6ba7c143c1ef58ed2801ee1f9",
        "disposition": "distinct_strategic_owner_for_iwd_and_war_context",
    },
    "taliban_offensive_2021": {
        "canonical_object_sha256": "b6c966d48c1b9e81a977edef24114fd5aa5f32975947fb6e5563d5fb7ea430c5",
        "disposition": "distinct_later_campaign_owner",
    },
    "hced_label_hced_kabul2001_1": {
        "canonical_object_sha256": "05067b362d43e6a7b91f5f4546f6f79a659458313bbeee8c1a0274877dd81456",
        "disposition": "distinct_2001_tactical_owner",
    },
    "hced_label_hced_kandahar2001_1": {
        "canonical_object_sha256": "8e99a1e9de2273d07cd4be8c5febd16a5f07a025b17d9f206542080bdddead7d",
        "disposition": "distinct_2001_tactical_owner",
    },
    f"{_OLD_LANE_PREFIX}hced_mazar_i_sharif2001_1": {
        "canonical_object_sha256": "ca5c78576ed3a890603f419495bd9ad6d65a2b8f7f4e295042e8cc0e8d078d8a",
        "disposition": "distinct_2001_tactical_owner",
    },
    f"{_OLD_LANE_PREFIX}hced_kunduz2001_1": {
        "canonical_object_sha256": "8fae46b0e201e38bcf21324e801b4bf4ccba76ad2abd3fed3176c13420e504a0",
        "disposition": "distinct_2001_tactical_owner",
    },
    f"{_OLD_LANE_PREFIX}hced_qala_i_jangi2001_1": {
        "canonical_object_sha256": "1dac9f4490648a87c027a6e99f5a854c9e52df1a1d7eda05ace81789d74ea371",
        "disposition": "distinct_2001_tactical_owner",
    },
    f"{_OLD_LANE_PREFIX}hced_tora_bora2001_1": {
        "canonical_object_sha256": "1531754c7af7ee4bbecce0aecc5d3d6a5c5763c144b39a8808f3eb2901c4f0cc",
        "disposition": "distinct_2001_tactical_owner",
    },
}


def _signature_payload() -> dict[str, Any]:
    return {
        "all_candidate_id_sha256": WAVE8_AL_QAEDA_TALIBAN_ALL_CANDIDATE_ID_SHA256,
        "contracts": WAVE8_AL_QAEDA_TALIBAN_CONTRACTS,
        "disposition_counts": WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS,
        "entities": WAVE8_AL_QAEDA_TALIBAN_ENTITIES,
        "existing_release_boundaries": WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES,
        "funnel_audit": WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT,
        "hced_dispositions": WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
        "integration_dispositions": WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS,
        "iwbd_dispositions": WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS,
        "iwd_dispositions": WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS,
        "location_quarantine_declarations": WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS,
        "location_quarantine_reasons": WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_REASONS,
        "queue_sha256": {
            "hced": WAVE8_AL_QAEDA_TALIBAN_HCED_QUEUE_SHA256,
            "iwbd": WAVE8_AL_QAEDA_TALIBAN_IWBD_QUEUE_SHA256,
            "iwd": WAVE8_AL_QAEDA_TALIBAN_IWD_QUEUE_SHA256,
            "ucdp": WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256,
            "wikidata_battle": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_QUEUE_SHA256,
            "wikidata_generic": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_QUEUE_SHA256,
        },
        "reused_source_boundaries": WAVE8_AL_QAEDA_TALIBAN_REUSED_SOURCE_BOUNDARIES,
        "row_hashes": WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES,
        "sources": WAVE8_AL_QAEDA_TALIBAN_SOURCES,
        "ucdp_dispositions": WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS,
        "wikidata_battle_dispositions": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
        "wikidata_generic_dispositions": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS,
    }


def wave8_al_qaeda_taliban_audit_signature() -> str:
    """Return the immutable digest of the complete 50-row adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE = (
    "76bf7179043d5d5ee1b040de3b47d24d11b7b7a5e57a1b22919d78a745197362"
)


_GENERIC_ENTITY_IDS = frozenset(
    {
        "afghanistan",
        "al_qaeda",
        "australia",
        "canada",
        "hizb_i_islami_afghanistan",
        "islamic_republic_afghanistan",
        "taliban",
        "united_kingdom",
        "united_states",
        "us_united_states_of_america_contemporary",
    }
)
_DISCOVERY_SOURCE_TOKENS = frozenset(
    {"iwbd", "iwd", "ucdp", "wikidata", "wikidata-battles"}
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _participant_ids(event: Mapping[str, Any]) -> set[str]:
    participants = event.get("participants", [])
    if not isinstance(participants, list):
        return set()
    return {
        str(participant.get("entity_id"))
        for participant in participants
        if isinstance(participant, Mapping) and participant.get("entity_id")
    }


def _validate_static() -> None:
    if (
        len(WAVE8_AL_QAEDA_TALIBAN_CONTRACTS),
        len(WAVE8_AL_QAEDA_TALIBAN_ENTITIES),
        len(WAVE8_AL_QAEDA_TALIBAN_SOURCES),
    ) != (2, 10, 9):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    expected_dataset_sizes = (9, 6, 5, 27, 3, 0)
    actual_dataset_sizes = tuple(
        len(dispositions)
        for dispositions in (
            WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS,
        )
    )
    if actual_dataset_sizes != expected_dataset_sizes:
        raise ValueError(f"{_LANE_NAME} audited dataset inventory changed")
    if len(WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS) != 50:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")
    if WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS["all"] != {
        "promote": 2,
        "hold": 33,
        "exclude": 15,
        "total": 50,
    }:
        raise ValueError(f"{_LANE_NAME} disposition count contract changed")
    if (
        len(WAVE8_AL_QAEDA_TALIBAN_AUDITED_HOLD_IDS),
        len(WAVE8_AL_QAEDA_TALIBAN_AUDITED_EXCLUSION_IDS),
    ) != (33, 15):
        raise ValueError(f"{_LANE_NAME} hold/exclusion partition changed")
    if WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS & (
        WAVE8_AL_QAEDA_TALIBAN_AUDITED_HOLD_IDS
        | WAVE8_AL_QAEDA_TALIBAN_AUDITED_EXCLUSION_IDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition partitions overlap")
    if (
        WAVE8_AL_QAEDA_TALIBAN_HOLD_IDS
        or WAVE8_AL_QAEDA_TALIBAN_TERMINAL_EXCLUSION_IDS
        or WAVE8_AL_QAEDA_TALIBAN_RESERVED_IDS
        != WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact promotion inventory changed")

    digests = {
        "all": (_ALL_AUDITED_CANDIDATE_IDS, WAVE8_AL_QAEDA_TALIBAN_ALL_CANDIDATE_ID_SHA256),
        "hced": (
            WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS,
            "653c95aa3f74783452d0e67c5642a449bef6a4ed3a8ca05e83ee1e6718640d38",
        ),
        "iwbd": (
            WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS,
            "7256d616e86876625ddf9961050186eeecf55dc6632e136b2ed3a53d5a7ac0dd",
        ),
        "iwd": (
            WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS,
            "6b70c5bb34dca6b76155eb103807df9deb9f8145f3833a94ab2c03c1ae941c72",
        ),
        "ucdp": (
            WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS,
            "190d6f41b33edfc68c88859be698de2da108630bf1b30069e5920c264caff163",
        ),
        "wikidata": (
            WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
            "ecc87c189c78468442086b9d8f4126f588ff641fc803b5253c66cf6259494bf3",
        ),
        "contracts": (
            WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS,
            WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT["event_candidate_id_sha256"],
        ),
    }
    for label, (values, expected_digest) in digests.items():
        if _sorted_newline_sha256(values) != expected_digest:
            raise ValueError(f"{_LANE_NAME} {label} candidate digest changed")

    source_ids = set(_SOURCE_BY_ID)
    source_families = {
        str(source["source_family_id"])
        for source in WAVE8_AL_QAEDA_TALIBAN_SOURCES
    }
    if len(source_ids) != 9 or len(source_families) != 8:
        raise ValueError(f"{_LANE_NAME} source IDs/families changed")
    if _sorted_newline_sha256(source_ids) != (
        "1ec7767ffb42579759b7791a61e149baa5f37c3bd5988740acca8e8f5fc59c9a"
    ):
        raise ValueError(f"{_LANE_NAME} source ID digest changed")
    for source in WAVE8_AL_QAEDA_TALIBAN_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} non-HTTPS source URL")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} noncanonical source roles")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_AL_QAEDA_TALIBAN_ENTITIES
    }
    if len(entity_by_id) != 10 or set(entity_by_id) & _GENERIC_ENTITY_IDS:
        raise ValueError(f"{_LANE_NAME} generic or duplicate entity ID")
    if _sorted_newline_sha256(entity_by_id) != (
        "06c57e5a65556a568e775e023cd9793d1a2224a0575118899e3a129c81b4045b"
    ):
        raise ValueError(f"{_LANE_NAME} entity ID digest changed")
    year_counts = Counter(int(entity["start_year"]) for entity in entity_by_id.values())
    if year_counts != Counter({2002: 6, 2003: 4}):
        raise ValueError(f"{_LANE_NAME} entity-year inventory changed")
    for entity in entity_by_id.values():
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} opened an entity window")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened an alias bridge")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "strategic war" not in note:
            raise ValueError(f"{_LANE_NAME} continuity boundary weakened")
        refs = list(map(str, entity["source_ids"]))
        if (
            not _is_sorted_unique(refs)
            or not set(refs) <= source_ids | {_REUSED_ARMY_SOURCE_ID}
        ):
            raise ValueError(f"{_LANE_NAME} entity provenance changed")

    used_entities: set[str] = set()
    used_new_sources: set[str] = set()
    for candidate_id, contract in WAVE8_AL_QAEDA_TALIBAN_CONTRACTS.items():
        canonical = contract["canonical_event"]
        year = int(canonical["year_low"])
        if (
            canonical["year_high"] != year
            or canonical["canonical_key"]
            != f"{_slug(str(canonical['name']))}:{year}:{year}"
            or not canonical["date_text"]
            or not canonical["granularity"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event changed")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            not side_1
            or not side_2
            or set(side_1) & set(side_2)
            or not set(side_1 + side_2) <= set(entity_by_id)
            or set(side_1 + side_2) & _GENERIC_ENTITY_IDS
        ):
            raise ValueError(f"{_LANE_NAME} actor boundary changed")
        used_entities.update(side_1 + side_2)
        if (
            contract["raw_row_sha256"]
            != WAVE8_AL_QAEDA_TALIBAN_ROW_HASHES[candidate_id]
            or contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["outcome_scope"] != "local_tactical_objective_only"
            or not contract["actor_boundary_note"]
        ):
            raise ValueError(f"{_LANE_NAME} promotion semantics changed")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= source_ids | {_REUSED_ARMY_SOURCE_ID}
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or not _is_sorted_unique(families)
            or set(families)
            != {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
            or not _is_sorted_unique(date_sources)
            or not set(date_sources) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} source provenance changed")
        if any(
            token in source_id.casefold()
            for source_id in outcomes
            for token in _DISCOVERY_SOURCE_TOKENS
        ):
            raise ValueError(f"{_LANE_NAME} discovery source became outcome evidence")
        used_new_sources.update(set(evidence) & source_ids)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")
    used_new_sources.update(
        source_id
        for entity in WAVE8_AL_QAEDA_TALIBAN_ENTITIES
        for source_id in map(str, entity["source_ids"])
        if source_id in source_ids
    )
    if used_new_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    anaconda = WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[
        "hced-Operation Anaconda2002-1"
    ]
    mongoose = WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[
        "hced-Operation Mongoose2003-1"
    ]
    if (
        anaconda["canonical_event"]["year_low"] != 2002
        or anaconda["canonical_event"]["date_precision"]
        != "day_range_source_variance"
        or anaconda["expected_scale_level"] != 3
        or anaconda["source_date_override"] is not True
        or anaconda["source_scale_override"] is not True
        or any("uk" in entity_id or "brit" in entity_id for entity_id in anaconda["side_1_entity_ids"])
    ):
        raise ValueError(f"{_LANE_NAME} Anaconda override boundary changed")
    mongoose_note = (
        str(mongoose["actor_boundary_note"]) + " " + str(
            next(
                entity["continuity_note"]
                for entity in WAVE8_AL_QAEDA_TALIBAN_ENTITIES
                if entity["id"] == _MONGOOSE_OPPOSITION
            )
        )
    ).casefold()
    if (
        mongoose["canonical_event"]["date_precision"]
        != "open_day_range_source_variance"
        or mongoose["canonical_event"].get("closure_unknown") is not True
        or mongoose["expected_scale_level"] != 1
        or mongoose["source_date_override"] is not False
        or mongoose["source_scale_override"] is not False
        or mongoose["side_2_entity_ids"] != [_MONGOOSE_OPPOSITION]
        or not all(term in mongoose_note for term in ("hig", "taliban", "conflict"))
    ):
        raise ValueError(f"{_LANE_NAME} Mongoose dispute boundary changed")

    expected_event_ids = {_event_id(candidate_id) for candidate_id in WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS}
    if _sorted_newline_sha256(expected_event_ids) != (
        "a3a260f83bdec3594655ac090537f0053eff1ff6334afde441070b4f7a90fca5"
    ):
        raise ValueError(f"{_LANE_NAME} event ID digest changed")
    if WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS != WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented country quarantine")
    if set(WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS) != WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine declaration inventory changed")
    expected_line_hashes = {
        "hced-Operation Anaconda2002-1": "3aff84cf591e15b8dcb3c9801cb3b33d72f45aecbd28e8f0df4160170882d4d5",
        "hced-Operation Mongoose2003-1": "6ca1cf72b7fdef07565bb82984562fffe7248d9a89c3fac27c0a8ad5ddc5ef0a",
    }
    for candidate_id, line in WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS.items():
        if hashlib.sha256(f"{line}\n".encode("utf-8")).hexdigest() != expected_line_hashes[candidate_id]:
            raise ValueError(f"{_LANE_NAME} quarantine declaration changed")
    combined_quarantine = "".join(
        f"{line}\n"
        for line in sorted(WAVE8_AL_QAEDA_TALIBAN_LOCATION_QUARANTINE_DECLARATIONS.values())
    )
    if hashlib.sha256(combined_quarantine.encode("utf-8")).hexdigest() != (
        "a59ff22657b5cb7d5a23836c08befba2faf5ed4969f5e0c8f76570af2d47719b"
    ):
        raise ValueError(f"{_LANE_NAME} quarantine declaration digest changed")

    for item in WAVE8_AL_QAEDA_TALIBAN_INTEGRATION_DISPOSITIONS.values():
        if item["automated_rating_authorized"] is not False:
            raise ValueError(f"{_LANE_NAME} automated discovery became rateable")
    if wave8_al_qaeda_taliban_audit_signature() != (
        WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _rows_by_id(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return result


def _validate_fingerprinted_rows(
    rows: Iterable[Mapping[str, Any]],
    dispositions: Mapping[str, Mapping[str, Any]],
    dataset_name: str,
) -> None:
    indexed = _rows_by_id(rows)
    for candidate_id, disposition in dispositions.items():
        matches = indexed.get(candidate_id, [])
        if len(matches) != 1:
            raise ValueError(
                f"{_LANE_NAME} {dataset_name} {candidate_id} expected one row, "
                f"found {len(matches)}"
            )
        if _canonical_object_sha256(matches[0]) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} {dataset_name} fingerprint changed: {candidate_id}"
            )
        if matches[0].get("do_not_rate_automatically") is not True:
            raise ValueError(
                f"{_LANE_NAME} {dataset_name} automated-rating guard changed: "
                f"{candidate_id}"
            )


_EXPECTED_HCED_RAW: dict[str, dict[str, Any]] = {
    "hced-Operation Anaconda2002-1": {
        "name": "Operation Anaconda",
        "source_record_id": "Operation Anaconda2002",
        "source_row": 11825,
        "side_1_raw": "United States, United Kingdom, Australia, Afghanistan",
        "side_2_raw": "al Qaeda, Taliban",
        "winner_raw": "United States, United Kingdom, Australia, Afghanistan",
        "loser_raw": "al Qaeda, Taliban",
        "year_low": 2001,
        "year_best": 2001,
        "year_high": 2001,
        "scale_raw": "1",
        "latitude": "33.3667426",
        "longitude": "69.1813053",
    },
    "hced-Operation Mongoose2003-1": {
        "name": "Operation Mongoose",
        "source_record_id": "Operation Mongoose2003",
        "source_row": 11827,
        "side_1_raw": "United States",
        "side_2_raw": "al Qaeda, Taliban",
        "winner_raw": "United States",
        "loser_raw": "al Qaeda, Taliban",
        "year_low": 2003,
        "year_best": 2003,
        "year_high": 2003,
        "scale_raw": "1",
        "latitude": "31.3169436",
        "longitude": "66.3198563",
    },
}


def validate_wave8_al_qaeda_taliban_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate both exact rows and all seven adjacent HCED boundaries."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_AL_QAEDA_TALIBAN_CONTRACTS,
        {},
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    }
    if exact_ids != WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    if _sorted_newline_sha256(exact_ids) != WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT["event_candidate_id_sha256"]:
        raise ValueError(f"{_LANE_NAME} exact-label digest changed")
    for candidate_id, expected in _EXPECTED_HCED_RAW.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing exact row {candidate_id}")
        row = rows[0]
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} raw semantics changed for {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("do_not_rate_automatically") is not True
            or row.get("winner_raw") != row.get("side_1_raw")
            or normalize_label(row.get("winner_raw"))
            in {"draw", "inconclusive", "stalemate", "unknown"}
        ):
            raise ValueError(f"{_LANE_NAME} outcome guard changed for {candidate_id}")
    for candidate_id, disposition in WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS.items():
        rows = indexed.get(candidate_id, [])
        if (
            len(rows) != 1
            or canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]
        ):
            raise ValueError(f"{_LANE_NAME} HCED boundary changed: {candidate_id}")
    return {
        "adjacent_hced_dispositions": 7,
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_AL_QAEDA_TALIBAN_HCED_DISPOSITIONS),
        "exact_label_rows": 2,
        "holds": 1,
        "lane_exclusions": 6,
    }


def validate_wave8_al_qaeda_taliban_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the historical two-row sole-blocker funnel record."""

    records = [
        record
        for record in funnel.get("labels", [])
        if record.get("label") == _EXACT_LABEL
    ]
    if len(records) != 1:
        raise ValueError(f"{_LANE_NAME} funnel label inventory changed")
    record = records[0]
    for key, expected in WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT.items():
        if record.get(key) != expected:
            raise ValueError(f"{_LANE_NAME} funnel field changed: {key}")
    return {
        "exact_label_rows": int(record["events_touched"]),
        "shared_label_rows": int(record["events_touched"])
        - int(record["sole_blocker_events"]),
        "sole_blocker_rows": int(record["sole_blocker_events"]),
    }


def validate_wave8_al_qaeda_taliban_reused_sources(
    sources: Iterable[Mapping[str, Any]] | Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    """Require the pre-existing Army source to remain byte-for-byte canonical."""

    _validate_static()
    by_id = (
        {str(source_id): source for source_id, source in sources.items()}
        if isinstance(sources, Mapping)
        else {str(source.get("id")): source for source in sources}
    )
    for source_id, boundary in WAVE8_AL_QAEDA_TALIBAN_REUSED_SOURCE_BOUNDARIES.items():
        source = by_id.get(source_id)
        if source is None:
            raise ValueError(f"{_LANE_NAME} reused source disappeared: {source_id}")
        if _canonical_object_sha256(source) != boundary["canonical_object_sha256"]:
            raise ValueError(f"{_LANE_NAME} reused source changed: {source_id}")
        if source.get("source_family_id") != boundary["source_family_id"]:
            raise ValueError(f"{_LANE_NAME} reused source family changed: {source_id}")
    return {"reused_sources": len(WAVE8_AL_QAEDA_TALIBAN_REUSED_SOURCE_BOUNDARIES)}


def _validate_emitted_event(event: Mapping[str, Any]) -> None:
    candidate_id = str(event.get("hced_candidate_id"))
    contract = WAVE8_AL_QAEDA_TALIBAN_CONTRACTS.get(candidate_id)
    if contract is None:
        raise ValueError(f"{_LANE_NAME} foreign emitted event")
    canonical = contract["canonical_event"]
    expected_level = int(contract["expected_scale_level"])
    expected_scale = {1: "skirmish", 3: "battle"}[expected_level]
    expected_participants = expected_exact_hced_win_participants(
        contract["side_1_entity_ids"],
        contract["side_2_entity_ids"],
        confidence=float(contract["confidence"]),
        scale_level=expected_level,
        lane_name=_LANE_NAME,
    )
    if (
        event.get("id") != _event_id(candidate_id)
        or event.get("name") != canonical["name"]
        or (event.get("year"), event.get("end_year"))
        != (canonical["year_low"], canonical["year_high"])
        or event.get("event_type") != "engagement"
        or event.get("scale") != expected_scale
        or event.get("stakes") != "limited"
        or event.get("date_precision") != canonical["date_precision"]
        or event.get("reviewed_granularity") != canonical["granularity"]
        or event.get("canonical_event_key") != canonical["canonical_key"]
        or event.get("identity_resolution") != "candidate_keyed_exact"
        or event.get("participants") != expected_participants
        or event.get("outcome_source_ids") != contract["outcome_source_ids"]
        or event.get("outcome_source_family_ids")
        != contract["outcome_source_family_ids"]
        or event.get("source_ids") != ["hced_dataset", *contract["evidence_refs"]]
        or event.get("domain") != "land"
        or "geometry" in event
        or event.get("modern_location_country") != "Afghanistan"
        or "location_provenance" not in event
    ):
        raise ValueError(f"{_LANE_NAME} emitted event changed: {candidate_id}")
    if _participant_ids(event) & _GENERIC_ENTITY_IDS:
        raise ValueError(f"{_LANE_NAME} generic identity leaked: {candidate_id}")


def validate_wave8_al_qaeda_taliban_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: Iterable[Mapping[str, Any]],
    iwd_rows: Iterable[Mapping[str, Any]],
    ucdp_rows: Iterable[Mapping[str, Any]],
    wikidata_battle_rows: Iterable[Mapping[str, Any]],
    wikidata_generic_rows: Iterable[Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    release_sources: Iterable[Mapping[str, Any]] | Mapping[str, Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Validate all 50 dispositions, nesting owners, and nonrating guards."""

    validate_wave8_al_qaeda_taliban_queue_contracts(hced_rows)
    iwbd = list(iwbd_rows)
    iwd = list(iwd_rows)
    ucdp = list(ucdp_rows)
    wikidata_battles = list(wikidata_battle_rows)
    wikidata_generic = list(wikidata_generic_rows)
    _validate_fingerprinted_rows(iwbd, WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS, "IWBD")
    _validate_fingerprinted_rows(iwd, WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS, "IWD")
    _validate_fingerprinted_rows(ucdp, WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS, "UCDP")
    _validate_fingerprinted_rows(
        wikidata_battles,
        WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS,
        "Wikidata battle",
    )

    iwd_index = _rows_by_id(iwd)
    for candidate_id in WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS:
        row = iwd_index[candidate_id][0]
        if (
            row.get("parent_war_id") != "87"
            or row.get("parent_war_name") != "Afghanistan2001"
            or (row.get("start_year"), row.get("end_year")) != (2001, 2001)
        ):
            raise ValueError(f"{_LANE_NAME} IWD strategic boundary changed: {candidate_id}")
    ucdp_index = _rows_by_id(ucdp)
    taliban_dyad = ucdp_index["ucdp-dyadic-26.1-735-2003-2095"][0]
    if taliban_dyad.get("raw", {}).get("start_date2") != "2003-02-14":
        raise ValueError(f"{_LANE_NAME} UCDP Taliban date boundary changed")
    if taliban_dyad.get("raw", {}).get("start_date2") <= "2003-02-11":
        raise ValueError(f"{_LANE_NAME} UCDP Taliban dyad improperly covers Mongoose")

    wikidata_index = _rows_by_id(wikidata_battles)
    for candidate_id in WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS:
        row = wikidata_index[candidate_id][0]
        if row.get("winners") != []:
            raise ValueError(f"{_LANE_NAME} Wikidata discovery gained an outcome")
    anaconda_discovery = wikidata_index["Q1476042"][0]
    if anaconda_discovery.get("date") != "2002-01-01T00:00:00Z":
        raise ValueError(f"{_LANE_NAME} Wikidata year-precision boundary changed")

    generic_near = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in wikidata_generic
        if any(
            token in normalize_label(row.get("name") or row.get("canonical_name_candidate"))
            for token in ("anaconda", "mongoose", "takur ghar")
        )
    )
    if generic_near or WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} unreviewed generic Wikidata near hit: {generic_near}")

    existing = list(existing_events)
    if release_sources:
        validate_wave8_al_qaeda_taliban_reused_sources(release_sources)
    lane_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    lane_candidates = {str(event.get("hced_candidate_id")) for event in lane_events}
    if lane_candidates not in (set(), set(WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS)) or len(lane_events) not in (0, 2):
        raise ValueError(f"{_LANE_NAME} release candidate overlap is partial")
    for event in lane_events:
        _validate_emitted_event(event)

    if existing:
        by_event_id = {str(event.get("id")): event for event in existing}
        for event_id, boundary in WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES.items():
            event = by_event_id.get(event_id)
            if event is None:
                raise ValueError(f"{_LANE_NAME} existing owner disappeared: {event_id}")
            if _canonical_object_sha256(event) != boundary["canonical_object_sha256"]:
                raise ValueError(f"{_LANE_NAME} existing owner changed: {event_id}")

        allowed_near_ids = set(WAVE8_AL_QAEDA_TALIBAN_EXISTING_RELEASE_BOUNDARIES) | {
            _event_id(candidate_id) for candidate_id in WAVE8_AL_QAEDA_TALIBAN_CONTRACT_IDS
        }
        release_near = sorted(
            str(event.get("id") or "<missing-id>")
            for event in existing
            if str(event.get("id")) not in allowed_near_ids
            and int(event.get("year", -999999)) in {2002, 2003, 2007}
            and any(
                token in normalize_label(event.get("name"))
                for token in ("operation anaconda", "operation mongoose", "takur ghar", "firebase anaconda")
            )
        )
        if release_near:
            raise ValueError(f"{_LANE_NAME} unreviewed existing-release near hit: {release_near}")

    blocked_candidate_ids = (
        set(WAVE8_AL_QAEDA_TALIBAN_IWBD_DISPOSITIONS)
        | set(WAVE8_AL_QAEDA_TALIBAN_IWD_DISPOSITIONS)
        | set(WAVE8_AL_QAEDA_TALIBAN_UCDP_DISPOSITIONS)
        | set(WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_DISPOSITIONS)
    )
    for event in existing:
        candidate_refs = {
            str(event.get(field))
            for field in (
                "iwbd_candidate_id",
                "iwd_candidate_id",
                "ucdp_candidate_id",
                "wikidata_candidate_id",
                "source_candidate_id",
            )
            if event.get(field) is not None
        }
        if candidate_refs & blocked_candidate_ids:
            raise ValueError(f"{_LANE_NAME} nonrating discovery row was released")

    return {
        "audited_candidates": 50,
        "hced_dispositions": 9,
        "iwbd_dispositions": 6,
        "iwd_dispositions": 5,
        "ucdp_dispositions": 27,
        "wikidata_battle_dispositions": 3,
        "wikidata_generic_dispositions": 0,
        "release_lane_overlap": len(lane_events),
        "automated_discovery_ratings": 0,
    }


def install_wave8_al_qaeda_taliban_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_AL_QAEDA_TALIBAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_al_qaeda_taliban_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    """Install only the nine new fixtures; the Army source is reused in place."""

    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_AL_QAEDA_TALIBAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def _apply_reviewed_scale(event: dict[str, Any], contract: Mapping[str, Any]) -> None:
    scale_level = int(contract["expected_scale_level"])
    event["scale"] = {1: "skirmish", 3: "battle"}[scale_level]
    event["stakes"] = "limited"
    event["decisiveness"] = round(min(0.90, 0.54 + 0.06 * scale_level), 2)
    event["geographic_scope"] = round(min(0.70, 0.08 + 0.09 * scale_level), 2)
    event["participants"] = expected_exact_hced_win_participants(
        contract["side_1_entity_ids"],
        contract["side_2_entity_ids"],
        confidence=float(contract["confidence"]),
        scale_level=scale_level,
        lane_name=_LANE_NAME,
    )


def promote_wave8_al_qaeda_taliban_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit exactly two local tactical wins with reviewed year/scale/actors."""

    validate_wave8_al_qaeda_taliban_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_AL_QAEDA_TALIBAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        contract = WAVE8_AL_QAEDA_TALIBAN_CONTRACTS[
            str(event["hced_candidate_id"])
        ]
        _apply_reviewed_scale(event, contract)
    _apply_location_quarantine(events)
    for event in events:
        _validate_emitted_event(event)
    return events


def wave8_al_qaeda_taliban_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_AL_QAEDA_TALIBAN_CONTRACTS.values()
            ).items()
        )
    )


def wave8_al_qaeda_taliban_counts() -> dict[str, int]:
    _validate_static()
    return {
        "audited_candidates": 50,
        "promotion_contracts": 2,
        "newly_rated_events": 2,
        "participant_rows": 10,
        "new_entities": 10,
        "new_sources": 9,
        "new_source_families": 8,
        "reused_sources": 1,
        "holds": 33,
        "lane_exclusions": 15,
        "point_quarantine_additions": 2,
        "country_quarantine_additions": 0,
        "automated_discovery_ratings": 0,
        "source_date_overrides": 1,
        "source_scale_overrides": 1,
        "source_outcome_overrides": 0,
    }


def wave8_al_qaeda_taliban_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_AL_QAEDA_TALIBAN_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_AL_QAEDA_TALIBAN_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_al_qaeda_taliban_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_compound_actor_fail_closed",
        "counts": wave8_al_qaeda_taliban_counts(),
        "cohorts": wave8_al_qaeda_taliban_cohort_counts(),
        "disposition_counts": copy.deepcopy(
            WAVE8_AL_QAEDA_TALIBAN_DISPOSITION_COUNTS
        ),
        "final_audit_signature": WAVE8_AL_QAEDA_TALIBAN_FINAL_AUDIT_SIGNATURE,
        "funnel_audit": copy.deepcopy(WAVE8_AL_QAEDA_TALIBAN_FUNNEL_AUDIT),
        "module_owner": _MODULE_OWNER,
        "queue_sha256": {
            "hced": WAVE8_AL_QAEDA_TALIBAN_HCED_QUEUE_SHA256,
            "iwbd": WAVE8_AL_QAEDA_TALIBAN_IWBD_QUEUE_SHA256,
            "iwd": WAVE8_AL_QAEDA_TALIBAN_IWD_QUEUE_SHA256,
            "ucdp": dict(WAVE8_AL_QAEDA_TALIBAN_UCDP_QUEUE_SHA256),
            "wikidata_battle": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_BATTLE_QUEUE_SHA256,
            "wikidata_generic": WAVE8_AL_QAEDA_TALIBAN_WIKIDATA_GENERIC_QUEUE_SHA256,
        },
    }


_validate_static()
