"""Candidate-keyed Wave 8 audit for HCED's exact ``Armenia`` label.

The unresolved funnel contains four exact-label rows spanning more than twelve
centuries.  They cannot share a timeless Armenia identity.  Three rows have a
source-attested tactical result and receive event-bounded field formations:
Tigranocerta (69 BCE), Avarayr (451), and Mamistra/Mopsuestia (1152).

The fourth unresolved row, Artaxata (58), is terminally excluded.  Tacitus and
the modern scholarship agree that Tiridates withdrew and Artaxata opened its
gates without resistance; encoding Rome's subsequent occupation and demolition
as a battle victory would invent an engagement.  A fifth exact-label row,
Sardarapat (1918), already has one release event and an exact IWBD twin, so this
lane fingerprints both ownership boundaries instead of rating it again.

No generic Armenia alias is installed, unknown is never converted into a draw,
and every promoted row has its unaudited point withheld while retaining the
source-supported modern country.
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
    "WAVE8_ARMENIA_CONTRACT_IDS",
    "WAVE8_ARMENIA_CONTRACTS",
    "WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_ARMENIA_ENTITIES",
    "WAVE8_ARMENIA_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_ARMENIA_EXCLUSION_IDS",
    "WAVE8_ARMENIA_EXCLUSIONS",
    "WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ARMENIA_EXTERNAL_OWNER_IDS",
    "WAVE8_ARMENIA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ARMENIA_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_ARMENIA_HOLD_IDS",
    "WAVE8_ARMENIA_HOLDS",
    "WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS",
    "WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_ARMENIA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_ARMENIA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ARMENIA_NONPROMOTIONS",
    "WAVE8_ARMENIA_OUTCOME_OVERRIDES",
    "WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ARMENIA_RESERVED_IDS",
    "WAVE8_ARMENIA_SOURCES",
    "WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_ARMENIA_TERMINAL_EXCLUSIONS",
    "WAVE8_ARMENIA_TOUCHED_CANDIDATE_IDS",
    "install_wave8_armenia_entities",
    "install_wave8_armenia_sources",
    "promote_wave8_armenia_contracts",
    "validate_wave8_armenia_integration_dispositions",
    "validate_wave8_armenia_queue_contracts",
    "wave8_armenia_audit_signature",
    "wave8_armenia_cohort_counts",
    "wave8_armenia_counts",
    "wave8_armenia_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Armenia actor audit"
_EVENT_ID_PREFIX = "hced_wave8_armenia_"
_MODULE_OWNER = "military_elo.promotion.wave8_armenia"
_SARDARAPAT_ID = "hced-Sardarapat1918-1"
_SARDARAPAT_RELEASE_EVENT_ID = "hced_label_hced_sardarapat1918_1"
_SARDARAPAT_IWBD_ID = "iwbd-106-38-742"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
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


WAVE8_ARMENIA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_armenia_tacitus_annals_13",
        "Tacitus, Annals 13.34-41: Corbulo's Armenian campaign",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A"
            "1999.02.0078%3Abook%3D13"
        ),
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "tacitus_annals_fisher",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_iranica_artaxata",
        "Artaxata",
        "https://www.iranicaonline.org/articles/artaxata-gk/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_artaxata_1986",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_iranica_armenia_iran",
        "Armenia and Iran ii. The pre-Islamic period",
        "https://www.iranicaonline.org/articles/armenia-ii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_armenia_iran_pre_islamic",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_iranica_avarayr",
        "Avarayr",
        (
            "https://www.iranicaonline.org/articles/avarayr-a-village-in-armenia-"
            "in-the-principality-of-artaz-southeast-of-the-iranian-town-of-maku/"
        ),
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_avarayr_1987",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_iranica_elise",
        "Ełišē",
        "https://www.iranicaonline.org/articles/elise/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_elise_thomson_1998",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_elishe_nla",
        "The History of Vartan and of the Battle of the Armenians",
        "https://dspace.nla.am/handle/123456789/14223",
        "National Library of Armenia digital repository",
        "digitized_translated_primary_source",
        "elishe_neumann_translation_1830",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_der_nersessian_cilicia",
        "The Kingdom of Cilician Armenia",
        "https://www.attalus.org/armenian/KCA1.htm",
        "A History of the Crusades, vol. II; Attalus transcription",
        "scholarly_history_chapter",
        "der_nersessian_cilician_armenia_1962",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_smbat_chronicle",
        "Smbat Sparapet's Chronicle",
        "https://www.attalus.org/armenian/cssint.htm",
        "Attalus; Robert Bedrosian translation",
        "translated_primary_chronicle",
        "smbat_sparapet_chronicle_bedrosian",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_ghazarian_cilicia",
        "The Armenian Kingdom in Cilicia During the Crusades",
        (
            "https://www.routledge.com/The-Armenian-Kingdom-in-Cilicia-During-"
            "the-Crusades-The-Integration-of-Cilician-Armenians-with-the-Latins-"
            "1080-1393/Ghazarian/p/book/9780700714186"
        ),
        "Routledge",
        "scholarly_monograph",
        "ghazarian_cilician_armenia_2000",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_plutarch_lucullus",
        "Plutarch, Life of Lucullus 24-29",
        "https://classics.mit.edu/Plutarch/lucullus.html",
        "MIT Internet Classics Archive",
        "translated_primary_source",
        "plutarch_lucullus_dryden_clough",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_demir_tigranocerta",
        "The Battle of Tigranocerta (69 BC): A Reconsideration",
        "https://doi.org/10.26650/anar.2021.24.898025",
        "Anatolian Research / Istanbul University Press",
        "peer_reviewed_scholarly_article",
        "demir_tigranocerta_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_oxford_tigranocerta",
        "Tigranocerta",
        (
            "https://academic.oup.com/edited-volume/61673/"
            "chapter-abstract/548214284"
        ),
        "Oxford Classical Dictionary / Oxford University Press",
        "scholarly_reference_entry",
        "oxford_classical_dictionary_tigranocerta",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_history_museum_sardarapat",
        "Heroic Battles in May 1918 and the First Republic of Armenia",
        (
            "https://historymuseum.am/en/map_content_type/heroic-battles-in-may-"
            "1918-the-first-republic-of-armenia-1918-1920/"
        ),
        "History Museum of Armenia",
        "official_museum_history",
        "history_museum_armenia_sardarapat",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_armenia_central_bank_sardarapat",
        "100th Anniversary of Sardarapat Battle",
        "https://www.cba.am/en/collector-coins/284/",
        "Central Bank of Armenia",
        "official_government_history",
        "central_bank_armenia_sardarapat_2018",
        outcome=True,
        crosscheck=True,
    ),
)


_TIGRANOCERTA_ROMAN_ID = "lucullus_roman_army_tigranocerta_69_bce"
_TIGRANOCERTA_ARMENIAN_ID = (
    "tigranes_ii_armenian_royal_army_tigranocerta_69_bce"
)
_AVARAYR_SASANIAN_ID = "yazdegerd_ii_sasanian_army_avarayr_451"
_AVARAYR_ARMENIAN_ID = "vardan_mamikonian_armenian_rebel_army_avarayr_451"
_MAMISTRA_ARMENIAN_ID = "thoros_ii_rubenid_cilician_army_mamistra_1152"
_MAMISTRA_BYZANTINE_ID = (
    "andronikos_komnenos_byzantine_allied_army_mamistra_1152"
)


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
            + " No rating is inherited from or passed to another Armenian, "
            "Roman, Sasanian, Byzantine, Cilician, dynastic, ethnic, or modern "
            "state identity."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ARMENIA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TIGRANOCERTA_ROMAN_ID,
        "Lucullus's Roman army at Tigranocerta (69 BCE)",
        "event_bounded_field_army",
        -69,
        "Tigranocerta and Arzanene",
        (
            "Bounded to Lucullus's Roman expeditionary army and the detachments "
            "engaged against Tigranes during the 69 BCE battle and siege."
        ),
        [
            "wave8_armenia_demir_tigranocerta",
            "wave8_armenia_oxford_tigranocerta",
            "wave8_armenia_plutarch_lucullus",
        ],
    ),
    _entity(
        _TIGRANOCERTA_ARMENIAN_ID,
        "Tigranes II's Armenian royal army at Tigranocerta (69 BCE)",
        "event_bounded_field_coalition",
        -69,
        "Tigranocerta and Arzanene",
        (
            "Bounded to Tigranes II's Armenian royal army and its subject and "
            "allied contingents in the pitched battle; it is not timeless Armenia."
        ),
        [
            "wave8_armenia_demir_tigranocerta",
            "wave8_armenia_oxford_tigranocerta",
            "wave8_armenia_plutarch_lucullus",
        ],
    ),
    _entity(
        _AVARAYR_SASANIAN_ID,
        "Yazdegerd II's Sasanian army at Avarayr (451)",
        "event_bounded_imperial_army",
        451,
        "Avarayr plain, Vaspurakan",
        (
            "Bounded to the Sasanian imperial army, including its elephant corps "
            "and aligned contingents, that fought the Armenian uprising."
        ),
        [
            "wave8_armenia_elishe_nla",
            "wave8_armenia_iranica_avarayr",
            "wave8_armenia_iranica_elise",
        ],
    ),
    _entity(
        _AVARAYR_ARMENIAN_ID,
        "Vardan Mamikonian's Armenian rebel army at Avarayr (451)",
        "event_bounded_rebel_army",
        451,
        "Avarayr plain, Vaspurakan",
        (
            "Bounded to Vardan Mamikonian's Christian Armenian nobles, retainers, "
            "clergy, and common soldiers in the 451 uprising."
        ),
        [
            "wave8_armenia_elishe_nla",
            "wave8_armenia_iranica_avarayr",
            "wave8_armenia_iranica_elise",
        ],
    ),
    _entity(
        _MAMISTRA_ARMENIAN_ID,
        "Thoros II's Rubenid Cilician army at Mamistra (1152)",
        "event_bounded_siege_relief_force",
        1152,
        "Mamistra, Cilicia",
        (
            "Bounded to Thoros II and his brothers' Cilician Armenian force that "
            "sortied from besieged Mamistra and routed the besiegers."
        ),
        [
            "wave8_armenia_der_nersessian_cilicia",
            "wave8_armenia_ghazarian_cilicia",
            "wave8_armenia_smbat_chronicle",
        ],
    ),
    _entity(
        _MAMISTRA_BYZANTINE_ID,
        "Andronikos Komnenos's Byzantine-allied army at Mamistra (1152)",
        "event_bounded_besieging_army",
        1152,
        "Mamistra, Cilicia",
        (
            "Bounded to Andronikos Komnenos's Byzantine expedition and the local "
            "Armenian baronial contingents that joined its siege of Mamistra."
        ),
        [
            "wave8_armenia_der_nersessian_cilicia",
            "wave8_armenia_ghazarian_cilicia",
            "wave8_armenia_smbat_chronicle",
        ],
    ),
)


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


_ROW_HASHES = {
    "hced-Artaxata58-1": (
        "4b33aa2b5bf713252f4660ee2c37eb7a9e33dbcd82a66ef398fc1d8f0e60a1b9"
    ),
    "hced-Avarayr451-1": (
        "62e955a5290af2a6839b9bf26ac9eb7e5f5f63ed4889d13a8693bcdbb2c35636"
    ),
    "hced-Mopsuestia1152-1": (
        "844321410459f46630938488c1cb2f3db29eb222e12fd1643b931520976cc4d5"
    ),
    "hced-Sardarapat1918-1": (
        "dc25d91b404dfceef4b161ce23fb1b338a48af3e1f47631e08c087036502dd1a"
    ),
    "hced-Tigranocerta-69-1": (
        "5482d052687ff1604b320251f066df8571a9952837d347421957cf943e831bef"
    ),
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_ARMENIA_SOURCES
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
    war_type: str,
    *,
    confidence: float,
    winner_side: int,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcome_sources = sorted(set(map(str, outcome_source_ids)))
    return {
        "audit_note": audit_note,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcome_sources}
        ),
        "outcome_source_ids": outcome_sources,
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "result_type": "win",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": war_type,
        "winner_side": winner_side,
    }


WAVE8_ARMENIA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Tigranocerta-69-1": _contract(
        "hced-Tigranocerta-69-1",
        _canonical(
            "Battle of Tigranocerta",
            -69,
            "October 69 BCE",
            date_precision="month",
            granularity="pitched_battle",
        ),
        "third_mithridatic_war_armenia_69_bce",
        [_TIGRANOCERTA_ROMAN_ID],
        [_TIGRANOCERTA_ARMENIAN_ID],
        [
            "wave8_armenia_demir_tigranocerta",
            "wave8_armenia_oxford_tigranocerta",
            "wave8_armenia_plutarch_lucullus",
        ],
        [
            "wave8_armenia_demir_tigranocerta",
            "wave8_armenia_oxford_tigranocerta",
            "wave8_armenia_plutarch_lucullus",
        ],
        (
            "Plutarch and the modern studies attest that Lucullus defeated "
            "Tigranes II's army outside Tigranocerta. The contract is the pitched "
            "battle, not the city's later capitulation or a generic Roman-Armenian "
            "war result."
        ),
        "interstate_limited",
        confidence=0.97,
        winner_side=1,
    ),
    "hced-Avarayr451-1": _contract(
        "hced-Avarayr451-1",
        _canonical(
            "Battle of Avarayr",
            451,
            "2 June 451",
            date_precision="day",
            granularity="pitched_battle",
        ),
        "vardanants_rebellion_451",
        [_AVARAYR_SASANIAN_ID],
        [_AVARAYR_ARMENIAN_ID],
        [
            "wave8_armenia_elishe_nla",
            "wave8_armenia_iranica_avarayr",
            "wave8_armenia_iranica_elise",
        ],
        [
            "wave8_armenia_elishe_nla",
            "wave8_armenia_iranica_avarayr",
            "wave8_armenia_iranica_elise",
        ],
        (
            "The Sasanian army crushed the Armenian field army after committing "
            "its elephant corps; Vardan and eight other generals were killed. The "
            "later easing of religious persecution makes the victory pyrrhic at "
            "strategic scale but does not turn the tactical battle into a draw."
        ),
        "internal_rebellion",
        confidence=0.97,
        winner_side=1,
    ),
    "hced-Mopsuestia1152-1": _contract(
        "hced-Mopsuestia1152-1",
        _canonical(
            "Battle of Mamistra",
            1152,
            "1152",
            granularity="siege_sortie_and_field_rout",
        ),
        "rubenid_byzantine_war_1152",
        [_MAMISTRA_ARMENIAN_ID],
        [_MAMISTRA_BYZANTINE_ID],
        [
            "wave8_armenia_der_nersessian_cilicia",
            "wave8_armenia_ghazarian_cilicia",
            "wave8_armenia_smbat_chronicle",
        ],
        [
            "wave8_armenia_der_nersessian_cilicia",
            "wave8_armenia_ghazarian_cilicia",
            "wave8_armenia_smbat_chronicle",
        ],
        (
            "Der Nersessian and the Cilician chronicle attest that Thoros II "
            "sortied from Mamistra under cover of darkness, routed Andronikos's "
            "besieging army, and captured leading allies. HCED's Mopsuestia label "
            "is retained as an alias, not a second battle."
        ),
        "interstate_limited",
        confidence=0.96,
        winner_side=1,
    ),
}


WAVE8_ARMENIA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ARMENIA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Artaxata58-1": {
        "disposition": "terminal_exclusion",
        "evidence_refs": [
            "wave8_armenia_iranica_armenia_iran",
            "wave8_armenia_iranica_artaxata",
            "wave8_armenia_tacitus_annals_13",
        ],
        "exclusion_reason": "no_attested_battle_unopposed_surrender",
        "raw_row_sha256": _ROW_HASHES["hced-Artaxata58-1"],
        "reviewed_granularity": "city_surrender_and_subsequent_demolition",
        "reviewed_outcome": "not_rateable_no_contested_engagement",
        "unknown_is_never_draw": True,
        "audit_note": (
            "Tiridates withdrew; Artaxata opened its gates without resistance. "
            "Corbulo occupied the city and later destroyed it because he could "
            "not garrison it. Those facts support a campaign disposition, not a "
            "battle Elo update between armies at Artaxata."
        ),
    }
}
WAVE8_ARMENIA_EXCLUSIONS = WAVE8_ARMENIA_TERMINAL_EXCLUSIONS
WAVE8_ARMENIA_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ARMENIA_HOLDS,
    **WAVE8_ARMENIA_TERMINAL_EXCLUSIONS,
}

WAVE8_ARMENIA_CONTRACT_IDS = frozenset(WAVE8_ARMENIA_CONTRACTS)
WAVE8_ARMENIA_HOLD_IDS = frozenset(WAVE8_ARMENIA_HOLDS)
WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ARMENIA_TERMINAL_EXCLUSIONS
)
WAVE8_ARMENIA_EXCLUSION_IDS = WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS
WAVE8_ARMENIA_RESERVED_IDS = frozenset(
    WAVE8_ARMENIA_CONTRACT_IDS
    | WAVE8_ARMENIA_HOLD_IDS
    | WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS
)


WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    _SARDARAPAT_ID: {
        "canonical_event_name": "Battle of Sardarapat",
        "disposition": "existing_release_owner",
        "evidence_refs": [
            "wave8_armenia_central_bank_sardarapat",
            "wave8_armenia_history_museum_sardarapat",
        ],
        "owner_event_id": _SARDARAPAT_RELEASE_EVENT_ID,
        "raw_row_sha256": _ROW_HASHES[_SARDARAPAT_ID],
        "source_dataset": "hced",
        "year": 1918,
        "reason": (
            "The current release already rates this exact HCED candidate once. "
            "Official Armenian sources corroborate the Armenian tactical victory; "
            "this lane must not emit a second event."
        ),
    }
}
WAVE8_ARMENIA_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
)


WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _SARDARAPAT_IWBD_ID: {
        "disposition": "deduplicate_to_existing_hced_release_event",
        "existing_release_event_id": _SARDARAPAT_RELEASE_EVENT_ID,
        "fingerprint": {
            "source_row": "742",
            "source_snapshot": (
                "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin"
            ),
            "name": "Sardarapat",
            "war_name": "World War I (Caucasus Front)",
            "start_date": "1918-05-28",
            "end_date": "1918-05-28",
            "duration_days": "1",
            "attacker_raw": "Central Powers",
            "defender_raw": "Allied Powers",
            "winner_raw": "Allied Powers",
            "battle_level_victor_role": "Defender",
        },
        "hced_candidate_id": _SARDARAPAT_ID,
        "relationship": "same_battle_same_year_matching_defender_victory",
        "source_dataset": "iwbd",
        "reason": (
            "IWBD's one-day Sardarapat row is the same battle already represented "
            "by the HCED release event. Its alliance labels are less actor-specific, "
            "so it is retained only as a deduplication disposition."
        ),
    }
}

WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    **WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS,
}
WAVE8_ARMENIA_TOUCHED_CANDIDATE_IDS = frozenset(
    WAVE8_ARMENIA_RESERVED_IDS | WAVE8_ARMENIA_EXTERNAL_OWNER_IDS
)
WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS = WAVE8_ARMENIA_TOUCHED_CANDIDATE_IDS
WAVE8_ARMENIA_EXACT_CANDIDATE_ID_SHA256 = (
    "e42bc9cc32d9583c8874ee63b150e021fcff11c1c927fea2459cd7af0048177f"
)
WAVE8_ARMENIA_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    "eddd94efa5a6c1abf0aa2457a62c3b28c741fc383a4a7631df5a9386cb9e6740"
)


WAVE8_ARMENIA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Tigranocerta-69-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_armenia_demir_tigranocerta",
            "wave8_armenia_oxford_tigranocerta",
        ],
        "raw_point": [40.868743, 38.1197169],
        "retained_country": "Turkey",
        "reason": (
            "The ancient city's precise site remains disputed, and HCED's single "
            "point is not an authenticated coordinate for the pitched battle."
        ),
    },
    "hced-Avarayr451-1": {
        "actions": ["withhold_point"],
        "evidence_refs": ["wave8_armenia_iranica_avarayr"],
        "raw_point": [44.1610327, 39.3659927],
        "retained_country": "Iran",
        "reason": (
            "Iranica identifies the Avarayr plain southeast of Maku, but does not "
            "authenticate HCED's single coordinate as the armies' clash point."
        ),
    },
    "hced-Mopsuestia1152-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_armenia_der_nersessian_cilicia",
            "wave8_armenia_smbat_chronicle",
        ],
        "raw_point": [35.625096, 36.960485],
        "retained_country": "Turkey",
        "reason": (
            "A Mopsuestia locality point cannot represent the besieging camp, "
            "night sortie, pursuit, and fighting before the city gates."
        ),
    },
}
WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_ARMENIA_LOCATION_QUARANTINE_REASONS
)
WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_ARMENIA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_ARMENIA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted(set(map(normalize_label, aliases))),
        "years": [year, year],
    }


WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Tigranocerta-69-1": _duplicate_audit(
        -69,
        "Battle of Tigranocerta",
        "Battle of Tigranokerta",
        "Tigranocerta",
        "Tigranokerta",
    ),
    "hced-Artaxata58-1": _duplicate_audit(
        58,
        "Artaxata",
        "Artashat",
        "Capture of Artaxata",
    ),
    "hced-Avarayr451-1": _duplicate_audit(
        451,
        "Avarayr",
        "Awarayr",
        "Battle of Avarayr",
        "Battle of Awarayr",
    ),
    "hced-Mopsuestia1152-1": _duplicate_audit(
        1152,
        "Battle of Mamistra",
        "Battle of Mopsuestia",
        "Mamistra",
        "Mopsuestia",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ARMENIA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_ARMENIA_ENTITIES,
        "exact_candidate_ids": sorted(WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS),
        "existing_release_duplicate_dispositions": (
            WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_ARMENIA_HOLDS,
        "integration_dispositions": WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_ARMENIA_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_ARMENIA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_ARMENIA_SOURCES,
        "terminal_exclusions": WAVE8_ARMENIA_TERMINAL_EXCLUSIONS,
    }


def wave8_armenia_audit_signature() -> str:
    """Return the immutable digest of the complete Armenia adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Patched to the measured payload after the fixtures are complete.
WAVE8_ARMENIA_FINAL_AUDIT_SIGNATURE = (
    "7096d416fe67b186544c655fb37e46b54a54b6808d095f2f2505dce9dbdff41d"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _candidate_id_sha256(values: Iterable[str]) -> str:
    return hashlib.sha256("\n".join(sorted(map(str, values))).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_ARMENIA_CONTRACTS),
        len(WAVE8_ARMENIA_HOLDS),
        len(WAVE8_ARMENIA_TERMINAL_EXCLUSIONS),
        len(WAVE8_ARMENIA_EXTERNAL_OWNER_IDS),
    ) != (3, 0, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_ARMENIA_ENTITIES), len(WAVE8_ARMENIA_SOURCES)) != (6, 14):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if len(WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS) != 5:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    if WAVE8_ARMENIA_RESERVED_IDS != {
        "hced-Artaxata58-1",
        "hced-Avarayr451-1",
        "hced-Mopsuestia1152-1",
        "hced-Tigranocerta-69-1",
    }:
        raise ValueError(f"{_LANE_NAME} unresolved reservation inventory changed")
    if WAVE8_ARMENIA_EXTERNAL_OWNER_IDS != {_SARDARAPAT_ID}:
        raise ValueError(f"{_LANE_NAME} Sardarapat ownership changed")
    disposition_sets = (
        WAVE8_ARMENIA_CONTRACT_IDS,
        WAVE8_ARMENIA_HOLD_IDS,
        WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS,
        WAVE8_ARMENIA_EXTERNAL_OWNER_IDS,
    )
    for index, left in enumerate(disposition_sets):
        for right in disposition_sets[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if _candidate_id_sha256(WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_ARMENIA_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if wave8_armenia_audit_signature() != WAVE8_ARMENIA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_ARMENIA_SOURCES
    }
    if len(source_by_id) != len(WAVE8_ARMENIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    source_families = {
        str(source["source_family_id"]) for source in WAVE8_ARMENIA_SOURCES
    }
    if len(source_families) != len(WAVE8_ARMENIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in WAVE8_ARMENIA_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_ARMENIA_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_ARMENIA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_entity_names = {
        "armenia",
        "byzantium",
        "persia",
        "rome",
        "sasanian empire",
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for entity in WAVE8_ARMENIA_ENTITIES:
        if normalize_label(entity["name"]) in forbidden_entity_names:
            raise ValueError(f"{_LANE_NAME} installed a generic actor")
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} entity is not event-bounded")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity source references changed")
        used_sources.update(source_ids)

    for candidate_id, contract in WAVE8_ARMENIA_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        for field in ("evidence_refs", "outcome_source_ids", "outcome_source_family_ids"):
            if not _is_sorted_unique(contract[field]) or not contract[field]:
                raise ValueError(f"{_LANE_NAME} contract evidence is not canonical")
        evidence = set(map(str, contract["evidence_refs"]))
        outcomes = set(map(str, contract["outcome_source_ids"]))
        if not outcomes <= evidence or not evidence <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} contract evidence references changed")
        expected_families = {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        if set(contract["outcome_source_family_ids"]) != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome-family references changed")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} contract sides changed")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract references unknown entity")
        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} invented a non-victory contract")
        if contract["source_outcome_override"] is not False:
            raise ValueError(f"{_LANE_NAME} invented an outcome override")
        used_sources.update(evidence)
        used_entities.update(side_1 | side_2)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entity fixture is not exactly consumed")

    exclusion = WAVE8_ARMENIA_TERMINAL_EXCLUSIONS["hced-Artaxata58-1"]
    forbidden_exclusion_keys = {
        "result_type",
        "winner_entity_ids",
        "winner_side",
    }
    if (
        exclusion["raw_row_sha256"] != _ROW_HASHES["hced-Artaxata58-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["reviewed_outcome"] != "not_rateable_no_contested_engagement"
        or exclusion["unknown_is_never_draw"] is not True
        or forbidden_exclusion_keys & set(exclusion)
    ):
        raise ValueError(f"{_LANE_NAME} Artaxata exclusion changed")
    exclusion_sources = list(map(str, exclusion["evidence_refs"]))
    if not _is_sorted_unique(exclusion_sources):
        raise ValueError(f"{_LANE_NAME} Artaxata evidence is not canonical")
    used_sources.update(exclusion_sources)

    sardarapat = WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS[
        _SARDARAPAT_ID
    ]
    if (
        sardarapat["owner_event_id"] != _SARDARAPAT_RELEASE_EVENT_ID
        or sardarapat["raw_row_sha256"] != _ROW_HASHES[_SARDARAPAT_ID]
        or sardarapat["disposition"] != "existing_release_owner"
    ):
        raise ValueError(f"{_LANE_NAME} Sardarapat release ownership changed")
    used_sources.update(map(str, sardarapat["evidence_refs"]))

    if set(WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS) != {
        _SARDARAPAT_IWBD_ID
    }:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    iwbd_disposition = WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS[
        _SARDARAPAT_IWBD_ID
    ]
    if (
        iwbd_disposition["hced_candidate_id"] != _SARDARAPAT_ID
        or iwbd_disposition["existing_release_event_id"]
        != _SARDARAPAT_RELEASE_EVENT_ID
    ):
        raise ValueError(f"{_LANE_NAME} IWBD owner changed")
    if set(WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS) != {
        _SARDARAPAT_ID,
        _SARDARAPAT_IWBD_ID,
    }:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")

    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS != WAVE8_ARMENIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if WAVE8_ARMENIA_OUTCOME_OVERRIDES or WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_ARMENIA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(audit["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")


def _is_exact_armenia_label(value: Any) -> bool:
    return normalize_label(value) == "armenia"


def validate_wave8_armenia_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all five exact-label rows and the four unresolved dispositions."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ARMENIA_CONTRACTS,
        WAVE8_ARMENIA_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed: dict[str, list[dict[str, Any]]] = {}
    exact_ids: set[str] = set()
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        indexed.setdefault(candidate_id, []).append(row)
        if _is_exact_armenia_label(row.get("side_1_raw")) or _is_exact_armenia_label(
            row.get("side_2_raw")
        ):
            exact_ids.add(candidate_id)
    if exact_ids != WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Armenia inventory changed: {sorted(exact_ids)}"
        )
    for candidate_id in (
        WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS | WAVE8_ARMENIA_EXTERNAL_OWNER_IDS
    ):
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} disposition {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} disposition hash changed for {candidate_id}")
    return {
        "external_owner_contracts": len(WAVE8_ARMENIA_EXTERNAL_OWNER_IDS),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_ARMENIA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_ARMENIA_TERMINAL_EXCLUSION_IDS),
    }


def _iwbd_fingerprint(row: Mapping[str, Any]) -> dict[str, str]:
    fields = (
        "source_row",
        "source_snapshot",
        "name",
        "war_name",
        "start_date",
        "end_date",
        "duration_days",
        "attacker_raw",
        "defender_raw",
        "winner_raw",
        "battle_level_victor_role",
    )
    return {
        field: "" if row.get(field) is None else str(row.get(field))
        for field in fields
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def validate_wave8_armenia_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on Sardarapat ownership and all probable event twins."""

    validate_wave8_armenia_queue_contracts(hced_rows)
    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    disposition = WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS[_SARDARAPAT_IWBD_ID]
    duplicate_rows = iwbd_by_id.get(_SARDARAPAT_IWBD_ID, [])
    if len(duplicate_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one IWBD Sardarapat twin, "
            f"found {len(duplicate_rows)}"
        )
    if _iwbd_fingerprint(duplicate_rows[0]) != disposition["fingerprint"]:
        raise ValueError(f"{_LANE_NAME} IWBD Sardarapat fingerprint changed")

    existing = list(existing_events)
    owner_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") == _SARDARAPAT_ID
    ]
    if existing and len(owner_events) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one existing Sardarapat owner, "
            f"found {len(owner_events)}"
        )
    if owner_events:
        owner = owner_events[0]
        participant_ids = {
            str(participant.get("entity_id"))
            for participant in owner.get("participants", [])
        }
        if (
            owner.get("id") != _SARDARAPAT_RELEASE_EVENT_ID
            or owner.get("name") != "Sardarapat"
            or int(owner.get("year")) != 1918
            or participant_ids != {"clio_q399_1918_2f11ffcf", "ottoman_empire"}
        ):
            raise ValueError(f"{_LANE_NAME} existing Sardarapat owner changed")

    audited = {
        (int(audit["years"][0]), alias)
        for audit in WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT.values()
        for alias in audit["aliases"]
    }
    unexpected_iwbd = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id") or "") != _SARDARAPAT_IWBD_ID
        and _row_year(row) is not None
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if unexpected_iwbd:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {unexpected_iwbd}"
        )
    unexpected_release = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in (WAVE8_ARMENIA_RESERVED_IDS | WAVE8_ARMENIA_EXTERNAL_OWNER_IDS)
        and _row_year(event) is not None
        and (_row_year(event), normalize_label(event.get("name"))) in audited
    )
    if unexpected_release:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): "
            f"{unexpected_release}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 1,
        "external_owner_hced_dispositions": 1,
        "integration_dispositions": len(WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 1,
        "iwbd_probable_twins": 0,
        "release_probable_twins": 0,
    }


def install_wave8_armenia_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ARMENIA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_armenia_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ARMENIA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_armenia_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_armenia_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ARMENIA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_armenia_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ARMENIA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_armenia_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_ARMENIA_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_ARMENIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_ARMENIA_EXTERNAL_OWNER_IDS
        ),
        "holds": len(WAVE8_ARMENIA_HOLDS),
        "integration_dispositions": len(
            WAVE8_ARMENIA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ARMENIA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_ARMENIA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_ARMENIA_ENTITIES),
        "new_sources": len(WAVE8_ARMENIA_SOURCES),
        "newly_rated_events": len(WAVE8_ARMENIA_CONTRACTS),
        "outcome_overrides": len(WAVE8_ARMENIA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ARMENIA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ARMENIA_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_ARMENIA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_ARMENIA_TERMINAL_EXCLUSIONS),
        "touched_hced_rows": len(WAVE8_ARMENIA_TOUCHED_CANDIDATE_IDS),
    }


def wave8_armenia_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_ARMENIA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_ARMENIA_POINT_QUARANTINE_ADDITIONS,
    }
