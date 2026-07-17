"""Candidate-keyed Wave 8 audit for HCED's exact ``Uzbekistan`` label.

The locked HCED queue uses the modern country name for ten events between
1501 and 1740.  None of those rows can inherit the identity of the Republic
of Uzbekistan (1991-present).  This lane promotes only the four rows that the
authoritative unresolved-label funnel identifies as sole blockers, and does so
with event-bounded Safavid, Shaybanid, Afsharid, and Khivan formations.

The remaining six rows are still owned and hash-pinned here.  Four require a
separate pre-Mughal Babur/Timurid opponent audit; two lack a sufficiently
stable event/date/outcome match.  A held or unknown result is never converted
to a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_UZBEKISTAN_CONTRACT_IDS",
    "WAVE8_UZBEKISTAN_CONTRACTS",
    "WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_UZBEKISTAN_ENTITIES",
    "WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS",
    "WAVE8_UZBEKISTAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_UZBEKISTAN_FUNNEL_AUDIT",
    "WAVE8_UZBEKISTAN_HOLD_IDS",
    "WAVE8_UZBEKISTAN_HOLDS",
    "WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_UZBEKISTAN_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_UZBEKISTAN_LOCATION_REVIEW",
    "WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES",
    "WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_RESERVED_IDS",
    "WAVE8_UZBEKISTAN_ROW_DISPOSITIONS",
    "WAVE8_UZBEKISTAN_SOURCES",
    "install_wave8_uzbekistan_entities",
    "install_wave8_uzbekistan_sources",
    "promote_wave8_uzbekistan_contracts",
    "validate_wave8_uzbekistan_funnel",
    "validate_wave8_uzbekistan_integration_dispositions",
    "validate_wave8_uzbekistan_queue_contracts",
    "wave8_uzbekistan_audit_signature",
    "wave8_uzbekistan_cohort_counts",
    "wave8_uzbekistan_counts",
    "wave8_uzbekistan_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Uzbekistan exact-label audit"
_EVENT_ID_PREFIX = "hced_wave8_uzbekistan_"
_MODULE_OWNER = "wave8_uzbekistan"


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
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_UZBEKISTAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_uzbekistan_iranica_damghan",
        "Dāmḡān",
        "https://www.iranicaonline.org/articles/damgan-persian-town/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_damgan_town",
        outcome=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_khorasan_safavid",
        "Khorasan x. History in the Safavid and Afsharid Periods",
        (
            "https://www.iranicaonline.org/articles/"
            "khorasan-x-history-in-the-safavid-and-afsharid-periods/"
        ),
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_khorasan_safavid_afsharid",
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_tahmasp",
        "Ṭahmāsp I",
        "https://www.iranicaonline.org/articles/tahmasp-i/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_tahmasp_i",
        outcome=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_chronology",
        "Chronology of Iranian History, Part 1",
        (
            "https://www.iranicaonline.org/articles/"
            "chronology-of-iranian-history-part-1/"
        ),
        "Encyclopaedia Iranica",
        "scholarly_reference_chronology",
        "iranica_iranian_history_chronology_1",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_allahverdi",
        "Allāhverdī Khan (1)",
        "https://www.iranicaonline.org/articles/allahverdi-khan-d-1/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_allahverdi_khan_1",
        outcome=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_abbas",
        "ʿAbbās I",
        "https://www.iranicaonline.org/articles/abbas-i/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_abbas_i",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_ilbars",
        "Ilbārs Khan",
        "https://www.iranicaonline.org/articles/ilbars-khan/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_ilbars_khan",
        outcome=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_khiva",
        "Khiva",
        "https://www.iranicaonline.org/articles/khiva/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_khiva",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_central_asia_vii",
        "Central Asia vii. In the 18th-19th Centuries",
        "https://www.iranicaonline.org/articles/central-asia-vii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_central_asia_vii",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_kandahar",
        "Kandahar iv. From the Mongol Invasion Through the Safavid Era",
        (
            "https://www.iranicaonline.org/articles/"
            "kandahar-from-the-mongol-invasion-through-the-safavid-era/"
        ),
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_kandahar_mongol_safavid",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_iranica_herat",
        "Herat iii. History, Medieval Period",
        "https://www.iranicaonline.org/articles/herat-iii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_herat_medieval_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_baburnama_beveridge",
        "The Bābur-nāma in English (Annette Beveridge translation)",
        "https://uzbekliterature.uz/sites/default/files/baburnama_2.pdf",
        "Uzbek Literature digital library; public-domain translation",
        "digitized_translated_primary_narrative",
        "baburnama_beveridge_translation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_cambridge_babur",
        "Mulkgirliq: The Act of Kingdom-Seizing",
        (
            "https://www.cambridge.org/core/books/abs/babur/"
            "mulkgirliq-the-act-of-kingdomseizing/"
            "4C018974330644B7B2FFB92C722ECBAC"
        ),
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "dale_babur_2018_chapter_3",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_cambridge_shaybanids",
        "The Shaybanids",
        (
            "https://www.cambridge.org/core/books/abs/history-of-inner-asia/"
            "shaybanids/681328EFAC754EF2B9D3E7CF4BFE8CB7"
        ),
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "sinor_history_inner_asia_shaybanids",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_uzbekistan_turk_dunyasi_babur",
        "Bâbür",
        "https://turkdunyasiansiklopedisi.gov.tr/detay/9662/B%C3%A2b%C3%BCr",
        "Atatürk Culture, Language and History High Institution",
        "government_scholarly_encyclopedia",
        "turk_dunyasi_ansiklopedisi_babur",
        outcome=True,
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
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
            + " No rating is inherited by a dynasty as a whole, an ethnic label, "
            "a descendant population, a later armed force, or any modern state "
            "including the Republic of Uzbekistan."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_DAMGHAN_SAFAVID = "tahmasp_safavid_damghan_recapture_force_1528"
_DAMGHAN_UZBEK = "uzbek_damghan_occupation_force_1528"
_JAM_SAFAVID = "tahmasp_safavid_jam_relief_army_1528"
_JAM_SHAYBANID = "ubaydallah_shaybanid_jam_army_1528"
_RABAT_SAFAVID = "abbas_safavid_rebat_parian_army_1598"
_RABAT_SHAYBANID = "din_muhammad_shaybanid_rebat_parian_army_1598"
_PETNAK_AFSHARID = "nader_afsharid_petnak_campaign_army_1740"
_PETNAK_KHIVAN = "ilbars_khivan_petnak_field_army_1740"


WAVE8_UZBEKISTAN_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _DAMGHAN_SAFAVID,
        "Shah Tahmasp's Safavid force retaking Damghan (1528)",
        "event_bounded_recapture_force",
        1528,
        "Damghan, Iran",
        [
            "wave8_uzbekistan_iranica_damghan",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "Bounded to the force involved in the documented 1528 recovery of "
            "Damghan; it does not stand for every Safavid formation in the wider "
            "Khorasan campaign."
        ),
    ),
    _entity(
        _DAMGHAN_UZBEK,
        "Uzbek occupation force at Damghan (1528)",
        "event_bounded_occupation_force",
        1528,
        "Damghan, Iran",
        [
            "wave8_uzbekistan_iranica_damghan",
            "wave8_uzbekistan_iranica_khorasan_safavid",
        ],
        (
            "Bounded to the Uzbek force holding Damghan before its documented "
            "Safavid recovery, not to Uzbeks generally or a generic khanate."
        ),
    ),
    _entity(
        _JAM_SAFAVID,
        "Shah Tahmasp's Safavid relief army at Jam (1528)",
        "event_bounded_field_army",
        1528,
        "Khorasan, Iran",
        [
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "Bounded to Tahmasp's relief army in the Battle of Jam/Sāruqameš "
            "after the siege of Herat was lifted."
        ),
    ),
    _entity(
        _JAM_SHAYBANID,
        "Ubaydallah Khan's Shaybanid army at Jam (1528)",
        "event_bounded_field_army",
        1528,
        "Khorasan, Iran",
        [
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "Bounded to Ubaydallah Khan's opposing army at Jam/Sāruqameš; it "
            "does not merge other Shaybanid commands or the Uzbek population."
        ),
    ),
    _entity(
        _RABAT_SAFAVID,
        "Shah Abbas's Safavid army at Rebāt-e Pariān (1598)",
        "event_bounded_field_army",
        1598,
        "Herat region, Afghanistan",
        [
            "wave8_uzbekistan_iranica_abbas",
            "wave8_uzbekistan_iranica_allahverdi",
            "wave8_uzbekistan_iranica_khorasan_safavid",
        ],
        (
            "Bounded to Shah Abbas's army in the August 1598 battle that opened "
            "the recovery of Herat."
        ),
    ),
    _entity(
        _RABAT_SHAYBANID,
        "Din Muhammad Khan's Uzbek army at Rebāt-e Pariān (1598)",
        "event_bounded_field_army",
        1598,
        "Herat region, Afghanistan",
        [
            "wave8_uzbekistan_iranica_abbas",
            "wave8_uzbekistan_iranica_allahverdi",
            "wave8_uzbekistan_iranica_khorasan_safavid",
        ],
        (
            "Bounded to Din Muhammad Khan's defeated army at Rebāt-e Pariān, "
            "not to every Shaybanid formation or the inhabitants of Transoxiana."
        ),
    ),
    _entity(
        _PETNAK_AFSHARID,
        "Nader Shah's Afsharid army near Petnak (1740)",
        "event_bounded_campaign_army",
        1740,
        "Khwarazm, Uzbekistan",
        [
            "wave8_uzbekistan_iranica_central_asia_vii",
            "wave8_uzbekistan_iranica_ilbars",
            "wave8_uzbekistan_iranica_khiva",
        ],
        (
            "Bounded to Nader Shah's Khwarazm campaign army in the documented "
            "battle near Petnak, before the Khanqah siege and Khiva surrender."
        ),
    ),
    _entity(
        _PETNAK_KHIVAN,
        "Ilbars Khan's Khivan army near Petnak (1740)",
        "event_bounded_field_army",
        1740,
        "Khwarazm, Uzbekistan",
        [
            "wave8_uzbekistan_iranica_central_asia_vii",
            "wave8_uzbekistan_iranica_ilbars",
            "wave8_uzbekistan_iranica_khiva",
        ],
        (
            "Bounded to Ilbars Khan's routed field army near Petnak; the later "
            "Khanqah siege, Khiva population, and other Khivan forces are outside "
            "the identity."
        ),
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Damghan1528-1": (
        "140c5601cae5c0036cc8f6c0c178f851ecdec5d49fdf844e05eae4103a33b010"
    ),
    "hced-Ghujduwan1512-1": (
        "3f3c4155aa3f8599b9dac243798812260fceb3b225024bd38cf386748a8c894c"
    ),
    "hced-Kandahar1508-1": (
        "2a5105c6c0e051d1f1267bebf3060a6fe8c43752628e1cb0b0486206684b9883"
    ),
    "hced-Khiva1740-1": (
        "d951f05fd1a933b5192b09782b5b640fa63c448efc3c84f45bf9165596867efe"
    ),
    "hced-Kul-i-Malik1512-1": (
        "b33bd75c639f58ba5a24652c1f167166d36ab1be17a3d2b024521d9b17946b5f"
    ),
    "hced-Maruchak1507-1": (
        "dabaf0de5cadeb1edb7c8699cf13e1c7f70ed2cf134ecdb50292d715ec5c209b"
    ),
    "hced-Pul-i-Sanghin1511-1": (
        "a89ae290d9371f71141e9dc4d1c40194a84e9f6c8b74103c3549564ac556faa2"
    ),
    "hced-Rabat-i-Pariyan1598-1": (
        "c7b1ecf9924f81efab76a1bda6f8326d0fb8f58758ef4e1ed4d10e7bd460c5a9"
    ),
    "hced-Sar-i-Pul1501-1": (
        "2c71302cbd529bbd5807195f3ad86c5654e6328942107bb2e295d0a35966e81e"
    ),
    "hced-Torbat-i-Jam1528-1": (
        "b36a6201b5395f2b0a7810db4c9a23150dcc40f201d15d0657debd4d8b38d89d"
    ),
}


_SOLE_BLOCKER_IDS = frozenset(
    {
        "hced-Damghan1528-1",
        "hced-Khiva1740-1",
        "hced-Rabat-i-Pariyan1598-1",
        "hced-Torbat-i-Jam1528-1",
    }
)
_OTHER_IDENTITY_BLOCKER_IDS = frozenset(_ROW_HASHES) - _SOLE_BLOCKER_IDS


WAVE8_UZBEKISTAN_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "46857510596b58250321ea401b73c39f1d4f643e7ac1635e6890e5dd5e7b40e4"
    ),
    "events_touched": 10,
    "failure_case": "one_wrong_interval_candidate",
    "failure_case_count": 10,
    "label": "uzbekistan",
    "marginal_events": 4,
    "newly_unblocked_candidate_id_sha256": (
        "e77d2e5ab725775c715de98155e8c5186c2c6fa2064df2f8db50174477f7ca5a"
    ),
    "other_identity_blocker_candidate_ids": sorted(_OTHER_IDENTITY_BLOCKER_IDS),
    "sole_blocker_candidate_ids": sorted(_SOLE_BLOCKER_IDS),
    "sole_blocker_events": 4,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "year",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    source_by_id = {str(source["id"]): source for source in WAVE8_UZBEKISTAN_SOURCES}
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_UZBEKISTAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Damghan1528-1": _contract(
        "hced-Damghan1528-1",
        _canonical("Safavid recapture of Damghan", 1528, "1528"),
        "safavid_uzbek_khorasan_1528",
        [_DAMGHAN_SAFAVID],
        [_DAMGHAN_UZBEK],
        [
            "wave8_uzbekistan_iranica_damghan",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        ["wave8_uzbekistan_iranica_damghan"],
        (
            "Iranica directly records the Uzbek reoccupation in 1527 and Shah "
            "Tahmasp's definitive recovery in 1528. The contract rates only that "
            "bounded recapture, not HCED's uncorroborated massacre field or the "
            "entire 1528 campaign; the city-centroid point is withheld."
        ),
        confidence=0.84,
    ),
    "hced-Khiva1740-1": _contract(
        "hced-Khiva1740-1",
        _canonical("Battle near Petnak", 1740, "1740"),
        "afsharid_khwarazm_campaign_1740",
        [_PETNAK_AFSHARID],
        [_PETNAK_KHIVAN],
        [
            "wave8_uzbekistan_iranica_central_asia_vii",
            "wave8_uzbekistan_iranica_ilbars",
            "wave8_uzbekistan_iranica_khiva",
        ],
        [
            "wave8_uzbekistan_iranica_central_asia_vii",
            "wave8_uzbekistan_iranica_ilbars",
        ],
        (
            "The raw umbrella name is narrowed to the directly documented battle "
            "near Petnak, where Nader routed Ilbars Khan's army. The later Khanqah "
            "siege, execution, and Khiva surrender are not collapsed into extra "
            "Elo assertions, and the raw Khiva-city point is withheld."
        ),
        confidence=0.96,
    ),
    "hced-Rabat-i-Pariyan1598-1": _contract(
        "hced-Rabat-i-Pariyan1598-1",
        _canonical(
            "Battle of Rebāt-e Pariān",
            1598,
            "August 1598",
            date_precision="month",
        ),
        "safavid_reconquest_khorasan_1598",
        [_RABAT_SAFAVID],
        [_RABAT_SHAYBANID],
        [
            "wave8_uzbekistan_iranica_abbas",
            "wave8_uzbekistan_iranica_allahverdi",
            "wave8_uzbekistan_iranica_khorasan_safavid",
        ],
        [
            "wave8_uzbekistan_iranica_abbas",
            "wave8_uzbekistan_iranica_allahverdi",
        ],
        (
            "The sources identify Shah Abbas's August 1598 victory over Din "
            "Muhammad's Uzbek army at Rebāt-e Pariān (also localized near Herat "
            "as Pol-e Salar) and the ensuing recovery of Herat. HCED's "
            "modern-country value says Uzbekistan despite a Herat-region point; "
            "both unverified location assertions are withheld."
        ),
        confidence=0.95,
    ),
    "hced-Torbat-i-Jam1528-1": _contract(
        "hced-Torbat-i-Jam1528-1",
        _canonical(
            "Battle of Jam (Sāruqameš)",
            1528,
            "1528 (converted day varies across the cited scholarly chronologies)",
        ),
        "safavid_uzbek_khorasan_1528",
        [_JAM_SAFAVID],
        [_JAM_SHAYBANID],
        [
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        [
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "Iranica's Tahmasp biography and chronology identify a Safavid "
            "victory at Jam in 1528. A newer Khorasan synthesis places the action "
            "at Sāruqameš and converts the chronicle date differently, so only the "
            "year is asserted. The Torbat-e Jam city point is not the reviewed "
            "battle site and is withheld."
        ),
        confidence=0.83,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: dict[str, Any],
    category: str,
    reviewed_outcome: str,
    actor_description: Iterable[str],
    reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": "hold",
        "hold_category": category,
        "reviewed_outcome": reviewed_outcome,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": list(map(str, actor_description)),
        "reviewed_granularity": canonical_event["granularity"],
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }


WAVE8_UZBEKISTAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Ghujduwan1512-1": _hold(
        "hced-Ghujduwan1512-1",
        _canonical("Battle of Ghujduwan", 1512, "1512"),
        "composite_opponent_and_pre_mughal_identity_blocker",
        "attested_uzbek_victory_but_not_rateable_in_this_tranche",
        [
            "Ubaydallah Khan's bounded Shaybanid force",
            "Najm-e Sani's Safavid force with Babur's pre-Mughal Timurid contingent",
        ],
        (
            "The broad Uzbek victory is attested, but HCED's composite 'Persia, "
            "Mughal Empire' opponent crosses two formations and calls Babur's 1512 "
            "force Mughal fourteen years before the empire's 1526 start. The row "
            "remains an explicit other-identity hold; it is not promoted and the "
            "unrated result is never encoded as a draw."
        ),
        [
            "wave8_uzbekistan_cambridge_babur",
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_turk_dunyasi_babur",
        ],
    ),
    "hced-Kandahar1508-1": _hold(
        "hced-Kandahar1508-1",
        _canonical(
            "HCED Kandahar claim",
            1508,
            "1508 in HCED; the matched academic sequence is in 1507",
            granularity="unresolved_event_claim",
        ),
        "date_actor_and_outcome_conflict",
        "unknown",
        [
            "Shaybani Khan's 1507 besieging force",
            "Nasir Mirza's Timurid Kandahar garrison",
            "the Arghun force that subsequently recovered Kandahar",
        ],
        (
            "The academic Kandahar chronology places Shaybani's encroachment in "
            "1507 and says Nasir Mirza defended the city before the Arghuns, not "
            "Shaybani, recovered it. It does not establish HCED's 1508 Uzbek win "
            "over 'Babur of Kabul.' The candidate stays unknown and is not "
            "promoted; unknown is never a draw."
        ),
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_babur",
            "wave8_uzbekistan_iranica_kandahar",
        ],
    ),
    "hced-Kul-i-Malik1512-1": _hold(
        "hced-Kul-i-Malik1512-1",
        _canonical("Battle of Kul-i Malik", 1512, "1512"),
        "pre_mughal_babur_identity_blocker",
        "attested_shaybanid_victory_but_not_rateable_in_this_tranche",
        [
            "Ubaydallah Khan's bounded Shaybanid force",
            "Babur's 1512 Timurid-Safavid client force",
        ],
        (
            "The battle and Babur's defeat are attested, but the raw opponent is "
            "the Mughal Empire before its 1526 foundation. A separate candidate-"
            "keyed Babur formation is required. This row is held, not promoted or "
            "treated as a draw."
        ),
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_babur",
            "wave8_uzbekistan_turk_dunyasi_babur",
        ],
    ),
    "hced-Maruchak1507-1": _hold(
        "hced-Maruchak1507-1",
        _canonical(
            "HCED Maruchak claim",
            1507,
            "1507",
            granularity="unresolved_event_claim",
        ),
        "unbounded_event_and_possible_campaign_overlap",
        "unknown",
        [
            "Muhammad Shaybani's 1507 Khorasan campaign force",
            "unresolved Timurid or Arghun opponent rather than a Mughal Empire",
        ],
        (
            "The academic and primary narratives establish Shaybani's 1507 "
            "Khorasan campaign and Herat takeover but do not supply a sufficiently "
            "bounded Maruchak engagement matching HCED's Mughal opponent and "
            "outcome. A related Herat row is separately pinned as a possible "
            "campaign overlap. This claim remains unknown, is not promoted, and "
            "is never a draw."
        ),
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_shaybanids",
            "wave8_uzbekistan_iranica_herat",
        ],
    ),
    "hced-Pul-i-Sanghin1511-1": _hold(
        "hced-Pul-i-Sanghin1511-1",
        _canonical("Battle of Pul-i Sanghin", 1511, "1511"),
        "pre_mughal_babur_identity_blocker",
        "attested_babur_victory_but_not_rateable_in_this_tranche",
        [
            "Babur's bounded 1511 Timurid force with Safavid support",
            "the opposing bounded Shaybanid force",
        ],
        (
            "Babur's victory over the Uzbek force belongs to his pre-1526 Timurid "
            "restoration campaign, not to the Mughal Empire identity in HCED. It "
            "requires a paired Babur audit, is not promoted here, and is not "
            "converted to a draw."
        ),
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_babur",
        ],
    ),
    "hced-Sar-i-Pul1501-1": _hold(
        "hced-Sar-i-Pul1501-1",
        _canonical("Battle of Sar-i Pul", 1501, "1501"),
        "pre_mughal_babur_identity_blocker",
        "attested_shaybanid_victory_but_not_rateable_in_this_tranche",
        [
            "Muhammad Shaybani's bounded 1501 force",
            "Babur's bounded Timurid force contesting Samarkand",
        ],
        (
            "The Shaybanid victory is attested, but Babur's 1501 force cannot be "
            "rated as the Mughal Empire founded in 1526. The row remains a paired-"
            "identity hold, is not promoted, and is not encoded as a draw."
        ),
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_shaybanids",
        ],
    ),
}


WAVE8_UZBEKISTAN_CONTRACT_IDS = frozenset(WAVE8_UZBEKISTAN_CONTRACTS)
WAVE8_UZBEKISTAN_HOLD_IDS = frozenset(WAVE8_UZBEKISTAN_HOLDS)
WAVE8_UZBEKISTAN_RESERVED_IDS = (
    WAVE8_UZBEKISTAN_CONTRACT_IDS | WAVE8_UZBEKISTAN_HOLD_IDS
)
WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_UZBEKISTAN_ROW_DISPOSITIONS = {
    candidate_id: (
        "promote" if candidate_id in WAVE8_UZBEKISTAN_CONTRACT_IDS else "hold"
    )
    for candidate_id in sorted(WAVE8_UZBEKISTAN_RESERVED_IDS)
}


# All four raw points are city geocodes rather than reviewed battle points.
# Rabat-i-Pariyan's raw modern country is also wrong (Uzbekistan for the Herat
# region).  These are local, promoted-only declarations for coordinated later
# integration; this module deliberately does not edit the global manifest.
WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_UZBEKISTAN_CONTRACT_IDS
)
WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Rabat-i-Pariyan1598-1"}
)
WAVE8_UZBEKISTAN_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_UZBEKISTAN_LOCATION_REVIEW: dict[str, dict[str, Any]] = {
    "hced-Damghan1528-1": {
        "country_disposition": "retain_iran",
        "point_disposition": "quarantine_unverified_city_centroid",
        "reason": "The source verifies Damghan, not the exact HCED coordinate.",
        "evidence_refs": ["wave8_uzbekistan_iranica_damghan"],
    },
    "hced-Khiva1740-1": {
        "country_disposition": "retain_uzbekistan",
        "point_disposition": "quarantine_wrong_city_for_petnak_battle",
        "reason": "The reviewed battle was near Petnak, not at the Khiva point.",
        "evidence_refs": [
            "wave8_uzbekistan_iranica_central_asia_vii",
            "wave8_uzbekistan_iranica_ilbars",
        ],
    },
    "hced-Rabat-i-Pariyan1598-1": {
        "country_disposition": "quarantine_wrong_uzbekistan_value",
        "point_disposition": "quarantine_unverified_rabat_geocode",
        "reason": "The battle belongs to the Herat campaign, not modern Uzbekistan.",
        "evidence_refs": [
            "wave8_uzbekistan_iranica_abbas",
            "wave8_uzbekistan_iranica_allahverdi",
            "wave8_uzbekistan_iranica_khorasan_safavid",
        ],
    },
    "hced-Torbat-i-Jam1528-1": {
        "country_disposition": "retain_iran",
        "point_disposition": "quarantine_torbat_city_not_saruqamesh_site",
        "reason": "The synthesis locates the battle at Sāruqameš north of Jam.",
        "evidence_refs": ["wave8_uzbekistan_iranica_khorasan_safavid"],
    },
}


# The locked IWBD queue has no same-name, overlapping-year twin for any of the
# ten exact-label rows.  Aliases are deliberately broad enough to fail closed
# if a later queue introduces a plausible duplicate.
WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Damghan1528-1": {
        "aliases": ("damghan", "recapture of damghan", "safavid recapture of damghan"),
        "years": (1528, 1528),
    },
    "hced-Ghujduwan1512-1": {
        "aliases": ("battle of ghazdewan", "battle of ghujduwan", "ghazdewan", "ghujduwan", "gijduvan"),
        "years": (1512, 1512),
    },
    "hced-Kandahar1508-1": {
        "aliases": ("kandahar", "siege of kandahar"),
        "years": (1507, 1508),
    },
    "hced-Khiva1740-1": {
        "aliases": ("battle near petnak", "battle of pitnak", "khiva", "petnak", "pitnak"),
        "years": (1740, 1740),
    },
    "hced-Kul-i-Malik1512-1": {
        "aliases": ("battle of kul i malik", "kul i malik", "kuli malik"),
        "years": (1512, 1512),
    },
    "hced-Maruchak1507-1": {
        "aliases": ("maruchak", "maruchaq"),
        "years": (1507, 1507),
    },
    "hced-Pul-i-Sanghin1511-1": {
        "aliases": ("battle of pul i sanghin", "pul i sanghin"),
        "years": (1511, 1511),
    },
    "hced-Rabat-i-Pariyan1598-1": {
        "aliases": ("battle of rebat e parian", "rabat i pariyan", "rebat e parian"),
        "years": (1598, 1598),
    },
    "hced-Sar-i-Pul1501-1": {
        "aliases": ("battle of sar i pul", "sar e pul", "sar i pul"),
        "years": (1501, 1501),
    },
    "hced-Torbat-i-Jam1528-1": {
        "aliases": ("battle of jam", "battle of saruqamesh", "saruqamesh", "torbat i jam", "zurabad"),
        "years": (1528, 1528),
    },
}


# Nearby same-campaign HCED rows are pinned to prevent future accidental
# umbrella deduplication or double ownership.
WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Charjui1740-1": {
        "raw_row_sha256": (
            "eb7e4da86b51dd510a5a0e55317ded9dae974edc468bfa9795e74339118fa9f5"
        ),
        "related_candidate_id": "hced-Khiva1740-1",
        "disposition": "distinct_preceding_bukhara_campaign_action",
        "owner_module": None,
        "reason": (
            "Charjui precedes Nader's receipt of Bukhara's submission; the Khiva "
            "row is narrowed to the later Petnak battle in Khwarazm."
        ),
        "evidence_refs": ["wave8_uzbekistan_iranica_central_asia_vii"],
    },
    "hced-Herat1507-1": {
        "raw_row_sha256": (
            "53460fb224c6bbaac3f54e5c5d85b4a4f8829ab09a3cf4a0105b80fcf988c9cb"
        ),
        "related_candidate_id": "hced-Maruchak1507-1",
        "disposition": "possible_campaign_overlap_keeps_maruchak_on_hold",
        "owner_module": None,
        "reason": (
            "The sourced 1507 endpoint is Shaybani's Herat takeover; a separate "
            "bounded Maruchak engagement has not been established."
        ),
        "evidence_refs": ["wave8_uzbekistan_iranica_herat"],
    },
    "hced-Herat1528-1": {
        "raw_row_sha256": (
            "d9f4a2ab2537692214c3ac693774b3a26ee1541eb077ca154567835039186e2a"
        ),
        "related_candidate_id": "hced-Torbat-i-Jam1528-1",
        "disposition": "distinct_siege_relief_and_field_battle_claims",
        "owner_module": None,
        "reason": (
            "The Herat siege/lifting and the later field battle at Sāruqameš are "
            "related campaign actions, not interchangeable event keys."
        ),
        "evidence_refs": [
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
    },
}


WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "damghan_and_jam_1528": {
        "candidate_ids": ["hced-Damghan1528-1", "hced-Torbat-i-Jam1528-1"],
        "raw_row_sha256s": [
            _ROW_HASHES["hced-Damghan1528-1"],
            _ROW_HASHES["hced-Torbat-i-Jam1528-1"],
        ],
        "disposition": "distinct_actions_in_one_khorasan_campaign",
        "reason": (
            "Damghan's recovery and the later Jam/Sāruqameš field battle occurred "
            "at different places and retain separate bounded forces and keys."
        ),
        "evidence_refs": [
            "wave8_uzbekistan_iranica_damghan",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
    }
}


WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"internal:{key}": disposition
        for key, disposition in WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS.items()
    },
}


# All four promoted orientations agree with HCED and the direct evidence.
WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_UZBEKISTAN_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_UZBEKISTAN_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS),
        "funnel_audit": WAVE8_UZBEKISTAN_FUNNEL_AUDIT,
        "holds": WAVE8_UZBEKISTAN_HOLDS,
        "integration_dispositions": WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS,
        "internal_relationship_dispositions": (
            WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT,
        "location_review": WAVE8_UZBEKISTAN_LOCATION_REVIEW,
        "outcome_overrides": WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS,
        "row_dispositions": WAVE8_UZBEKISTAN_ROW_DISPOSITIONS,
        "sources": WAVE8_UZBEKISTAN_SOURCES,
    }


def wave8_uzbekistan_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label audit state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_UZBEKISTAN_FINAL_AUDIT_SIGNATURE = (
    "c2e86d443fe060030b7f8213a31b05c066ddb6885a2c0aff3ef90aef0bcc81bb"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_UZBEKISTAN_CONTRACTS), len(WAVE8_UZBEKISTAN_HOLDS)) != (4, 6):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_UZBEKISTAN_ENTITIES), len(WAVE8_UZBEKISTAN_SOURCES)) != (8, 15):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_UZBEKISTAN_RESERVED_IDS != WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_UZBEKISTAN_CONTRACT_IDS != _SOLE_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} promotions no longer match sole blockers")
    if WAVE8_UZBEKISTAN_HOLD_IDS != _OTHER_IDENTITY_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} non-sole rows are not fully held")
    if set(WAVE8_UZBEKISTAN_ROW_DISPOSITIONS) != WAVE8_UZBEKISTAN_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} explicit row dispositions are incomplete")
    if wave8_uzbekistan_audit_signature() != WAVE8_UZBEKISTAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if _sorted_newline_sha256(WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS) != str(
        WAVE8_UZBEKISTAN_FUNNEL_AUDIT["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} funnel exact-cohort digest drifted")
    if _sorted_newline_sha256(_SOLE_BLOCKER_IDS) != str(
        WAVE8_UZBEKISTAN_FUNNEL_AUDIT["newly_unblocked_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} funnel sole-blocker digest drifted")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_UZBEKISTAN_SOURCES
    }
    if len(source_by_id) != len(WAVE8_UZBEKISTAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({str(source["source_family_id"]) for source in WAVE8_UZBEKISTAN_SOURCES}) != len(
        WAVE8_UZBEKISTAN_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independent and explicit")
    for source in WAVE8_UZBEKISTAN_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_UZBEKISTAN_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_UZBEKISTAN_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "afsharid iran",
        "khanate of bukhara",
        "khanate of khiva",
        "persia",
        "safavid iran",
        "uzbek",
        "uzbekistan",
        "uzbeks",
    }
    for entity in WAVE8_UZBEKISTAN_ENTITIES:
        if (
            int(entity["start_year"]) != int(entity["end_year"])
            or entity["aliases"]
            or entity["predecessors"]
        ):
            raise ValueError(f"{_LANE_NAME} identity is not event/time bounded")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern" not in note:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_UZBEKISTAN_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(side_1 | side_2)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] != "bounded_exact_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    for candidate_id, hold in WAVE8_UZBEKISTAN_HOLDS.items():
        if (
            hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]
            or hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold became rateable")
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            if forbidden in hold:
                raise ValueError(f"{_LANE_NAME} hold asserts a forbidden result field")
        reason = str(hold["hold_reason"]).casefold()
        if "draw" not in reason or "not promoted" not in reason:
            raise ValueError(f"{_LANE_NAME} hold lost unknown/draw policy text")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_UZBEKISTAN_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for collection in (
        WAVE8_UZBEKISTAN_LOCATION_REVIEW,
        WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS,
        WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS,
    ):
        for disposition in collection.values():
            refs = list(map(str, disposition["evidence_refs"]))
            if not set(refs) <= set(source_by_id):
                raise ValueError(f"{_LANE_NAME} integration evidence drifted")
            used_sources.update(refs)
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS != WAVE8_UZBEKISTAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if not WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS <= WAVE8_UZBEKISTAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} country quarantine is not promoted-only")
    if set(WAVE8_UZBEKISTAN_LOCATION_REVIEW) != WAVE8_UZBEKISTAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    if WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an IWBD duplicate")
    if set(WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_UZBEKISTAN_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    if set(WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS) != {
        "hced-Charjui1740-1",
        "hced-Herat1507-1",
        "hced-Herat1528-1",
    }:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    if set(WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS) != {
        "damghan_and_jam_1528"
    }:
        raise ValueError(f"{_LANE_NAME} internal relationship inventory changed")
    if WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an existing-release duplicate")


def _is_exact_uzbekistan_label(value: Any) -> bool:
    return normalize_label(value) == "uzbekistan"


def validate_wave8_uzbekistan_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate every exact-label row and its canonical raw-row fingerprint."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_UZBEKISTAN_CONTRACTS,
        WAVE8_UZBEKISTAN_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_uzbekistan_label(row.get("side_1_raw"))
        or _is_exact_uzbekistan_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Uzbekistan inventory changed: {sorted(exact_ids)}"
        )
    return counts


def validate_wave8_uzbekistan_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the authoritative funnel cohort and its four sole blockers."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    label_rows = [item for item in labels if item.get("label") == "uzbekistan"]
    if len(label_rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = label_rows[0]
    expected_label_fields = {
        "event_candidate_id_sha256": WAVE8_UZBEKISTAN_FUNNEL_AUDIT[
            "event_candidate_id_sha256"
        ],
        "events_touched": 10,
        "sole_blocker_events": 4,
    }
    for key, expected in expected_label_fields.items():
        if label.get(key) != expected:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = label.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get(
        "one_wrong_interval_candidate"
    ) != 10:
        raise ValueError(f"{_LANE_NAME} funnel failure case changed")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} funnel greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == "uzbekistan"]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one greedy ranking row")
    if (
        ranked[0].get("events_touched") != 10
        or ranked[0].get("marginal_events") != 4
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != WAVE8_UZBEKISTAN_FUNNEL_AUDIT[
            "newly_unblocked_candidate_id_sha256"
        ]
    ):
        raise ValueError(f"{_LANE_NAME} greedy sole-blocker audit changed")

    row_label_data = funnel.get("row_label_data")
    if not isinstance(row_label_data, list):
        raise ValueError(f"{_LANE_NAME} funnel row-label data are unavailable")
    audited_rows = []
    for row in row_label_data:
        label_failures = row.get("label_failures")
        if isinstance(label_failures, list) and any(
            failure.get("label") == "uzbekistan" for failure in label_failures
        ):
            audited_rows.append(row)
    audited_ids = {str(row.get("candidate_id")) for row in audited_rows}
    sole_ids = {
        str(row.get("candidate_id"))
        for row in audited_rows
        if row.get("sole_blocker_label") == "uzbekistan"
    }
    if audited_ids != WAVE8_UZBEKISTAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel exact cohort changed")
    if sole_ids != WAVE8_UZBEKISTAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} funnel sole blockers changed")
    for row in audited_rows:
        for failure in row["label_failures"]:
            if failure.get("label") == "uzbekistan" and failure.get(
                "failure_case"
            ) != "one_wrong_interval_candidate":
                raise ValueError(f"{_LANE_NAME} funnel failure classification changed")
    return {
        "exact_label_rows": len(audited_ids),
        "held_other_identity_rows": len(audited_ids - sole_ids),
        "sole_blocker_rows": len(sole_ids),
    }


def _date_year(value: Any) -> int | None:
    text = str(value or "")
    if len(text) < 4 or not text[:4].isdigit():
        return None
    return int(text[:4])


def _normalized_duplicate_audit() -> dict[str, dict[str, Any]]:
    return {
        candidate_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for candidate_id, item in WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT.items()
    }


def validate_wave8_uzbekistan_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Pin related HCED rows and fail on future IWBD/release duplicates."""

    validate_wave8_uzbekistan_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} related HCED fingerprint changed: {candidate_id}")

    duplicate_audit = _normalized_duplicate_audit()
    for row in iwbd_rows:
        start = _date_year(row.get("start_date"))
        end = _date_year(row.get("end_date"))
        if start is None or end is None:
            continue
        name = normalize_label(row.get("name"))
        for hced_id, audit in duplicate_audit.items():
            low, high = audit["years"]
            if start <= high and end >= low and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed plausible IWBD overlap "
                    f"{row.get('candidate_id')} for {hced_id}"
                )

    existing = list(existing_events)
    owned_collisions = sorted(
        {
            str(event.get("hced_candidate_id"))
            for event in existing
            if event.get("hced_candidate_id") in WAVE8_UZBEKISTAN_RESERVED_IDS
        }
    )
    if owned_collisions:
        raise ValueError(
            f"{_LANE_NAME} candidate ownership collision in release: {owned_collisions}"
        )
    for event in existing:
        start = _date_year(event.get("year"))
        end = _date_year(event.get("end_year")) or start
        if start is None or end is None:
            continue
        name = normalize_label(event.get("name"))
        for hced_id, audit in duplicate_audit.items():
            low, high = audit["years"]
            if start <= high and end >= low and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed existing-release overlap "
                    f"{event.get('id')} for {hced_id}"
                )

    return {
        "existing_release_duplicate_dispositions": len(
            WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS),
        "internal_relationship_dispositions": len(
            WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_uzbekistan_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_UZBEKISTAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_uzbekistan_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_UZBEKISTAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_uzbekistan_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_uzbekistan_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_UZBEKISTAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_uzbekistan_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_UZBEKISTAN_CONTRACTS.values()
            ).items()
        )
    )


def wave8_uzbekistan_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_UZBEKISTAN_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_UZBEKISTAN_HOLDS),
        "integration_dispositions": len(WAVE8_UZBEKISTAN_INTEGRATION_DISPOSITIONS),
        "internal_relationship_dispositions": len(
            WAVE8_UZBEKISTAN_INTERNAL_RELATIONSHIP_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_UZBEKISTAN_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_UZBEKISTAN_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_UZBEKISTAN_ENTITIES),
        "new_sources": len(WAVE8_UZBEKISTAN_SOURCES),
        "newly_rated_events": len(WAVE8_UZBEKISTAN_CONTRACTS),
        "outcome_overrides": len(WAVE8_UZBEKISTAN_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_UZBEKISTAN_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_UZBEKISTAN_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_UZBEKISTAN_RESERVED_IDS),
        "sole_blocker_rows": len(_SOLE_BLOCKER_IDS),
    }


def wave8_uzbekistan_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return local promoted-only quarantine additions for later integration."""

    _validate_static()
    return {
        "country": WAVE8_UZBEKISTAN_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_UZBEKISTAN_POINT_QUARANTINE_ADDITIONS,
    }
