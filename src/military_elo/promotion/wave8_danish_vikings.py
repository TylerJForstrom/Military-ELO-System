"""Candidate-keyed Wave 8 audit for HCED's ``Danish Vikings`` label.

The seven exact-label rows do not describe a timeless Danish or Viking polity.
They cover four separate ninth-century expeditions.  This lane therefore rates
only source-bounded campaign armies.  It shares an identity across engagements
only when the chronicles identify the same continuing host.  Thanet 851 is a
noncompetitive overwintering notice, not a Danish battlefield victory.
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
    "WAVE8_DANISH_VIKINGS_CONTRACTS",
    "WAVE8_DANISH_VIKINGS_CONTRACT_IDS",
    "WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_DANISH_VIKINGS_ENTITIES",
    "WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS",
    "WAVE8_DANISH_VIKINGS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_DANISH_VIKINGS_HOLDS",
    "WAVE8_DANISH_VIKINGS_HOLD_IDS",
    "WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS",
    "WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_DANISH_VIKINGS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES",
    "WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_DANISH_VIKINGS_RESERVED_IDS",
    "WAVE8_DANISH_VIKINGS_SOURCES",
    "WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS",
    "WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS",
    "install_wave8_danish_vikings_entities",
    "install_wave8_danish_vikings_sources",
    "promote_wave8_danish_vikings_contracts",
    "validate_wave8_danish_vikings_integration_dispositions",
    "validate_wave8_danish_vikings_queue_contracts",
    "wave8_danish_vikings_audit_signature",
    "wave8_danish_vikings_cohort_counts",
    "wave8_danish_vikings_counts",
    "wave8_danish_vikings_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Danish-Viking expedition forces"
_EVENT_ID_PREFIX = "hced_wave8_danish_vikings_"

_ACLEA_WESSEX_ID = "aethelwulf_aethelbald_aclea_army_851"
_ACLEA_VIKING_ID = "thames_viking_host_aclea_851"
_WESSEX_871_ID = "aethelred_alfred_wessex_campaign_army_871"
_GREAT_ARMY_871_ID = "great_heathen_army_wessex_campaign_871"
_FARNHAM_WESSEX_ID = "edward_west_saxon_field_army_farnham_893"
_FARNHAM_VIKING_ID = "appledore_raiding_detachment_farnham_893"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
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


WAVE8_DANISH_VIKINGS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_danish_vikings_yale_asc_ninth_century",
        "The Anglo-Saxon Chronicle: Ninth Century",
        "https://avalon.law.yale.edu/medieval/ang09.asp",
        "Lillian Goldman Law Library, Yale Law School",
        "institutional_translation_of_primary_chronicle",
        "anglo_saxon_chronicle_ingram_yale",
    ),
    _source(
        "wave8_danish_vikings_aethelweard_book_four",
        "The Fourth Book of the Chronicle of Æthelweard",
        (
            "https://deremilitari.org/2013/09/"
            "the-fourth-book-of-the-chronicle-of-aethelweard/"
        ),
        "De Re Militari: The Society for Medieval Military History",
        "translated_near_contemporary_primary_chronicle",
        "aethelweard_chronicle_book_four",
        crosscheck=True,
    ),
    _source(
        "wave8_danish_vikings_he_aclea",
        "Historic England Research Record: Battle of Aclea",
        (
            "https://www.heritagegateway.org.uk/Gateway/Results_Single.aspx?"
            "resourceID=19191&uid=397119"
        ),
        "Historic England via Heritage Gateway",
        "national_historic_environment_record",
        "historic_england_research_records",
        outcome=False,
    ),
    _source(
        "wave8_danish_vikings_he_ashdown",
        "West Berkshire HER: Ashdown, Battle of",
        (
            "https://www.heritagegateway.org.uk/Gateway/Results_Single.aspx?"
            "resourceID=1030&uid=MWB4187"
        ),
        "West Berkshire Historic Environment Record via Heritage Gateway",
        "local_authority_historic_environment_record",
        "historic_england_research_records",
        outcome=False,
    ),
    _source(
        "wave8_danish_vikings_he_farnham",
        "Historic England Research Record: Battle of Farnham 893 AD",
        (
            "https://www.heritagegateway.org.uk/Gateway/Results_Single.aspx?"
            "resourceID=19191&uid=1553910"
        ),
        "Historic England via Heritage Gateway",
        "national_historic_environment_record",
        "historic_england_research_records",
        outcome=False,
    ),
    _source(
        "wave8_danish_vikings_surrey_farnham",
        "The so-called Battle of Farnham in 893",
        "https://www.surreyarchaeology.org.uk/system/files/SAS%20SP%20497.pdf",
        "Surrey Archaeological Society, Surrey's Past 497",
        "scholarly_archaeological_society_article",
        "surrey_archaeological_society_farnham_893",
        crosscheck=True,
    ),
    _source(
        "wave8_danish_vikings_cambridge_alfred",
        "Alfred, King of the Anglo-Saxons",
        (
            "https://www.cambridge.org/core/books/abs/alfred-the-great/"
            "alfred-king-of-the-anglosaxons/1DD9F17FD759F2F9FABC44DE497C7A36"
        ),
        "Cambridge University Press",
        "scholarly_book_chapter",
        "anlezark_alfred_the_great_2021",
        outcome=False,
    ),
    _source(
        "wave8_danish_vikings_he_sandwich_851",
        "Historic England Research Record: Battle of Sandwich 851",
        (
            "https://www.heritagegateway.org.uk/Gateway/Results_Single.aspx?"
            "resourceID=19191&uid=8755225b-5477-4896-ac2a-8ecf4e1a942b"
        ),
        "Historic England via Heritage Gateway",
        "national_historic_environment_record",
        "historic_england_research_records",
        outcome=False,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    year: int,
    kind: str,
    region: str,
    scope_note: str,
    source_ids: list[str],
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
            scope_note
            + " No rating is inherited by Denmark, a Danish dynasty, Wessex, "
            "East Francia, any generic Viking or Northman label, another "
            "expedition, or a successor formation."
        ),
        "source_ids": sorted(set(source_ids)),
    }


WAVE8_DANISH_VIKINGS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ACLEA_WESSEX_ID,
        "Æthelwulf and Æthelbald's West Saxon Army at Aclea (851)",
        851,
        "engagement_force",
        "Wessex and Surrey",
        "Identity limited to the West Saxon royal army in the Aclea engagement.",
        [
            "wave8_danish_vikings_he_aclea",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
    _entity(
        _ACLEA_VIKING_ID,
        "Thames-Invasion Host at Aclea (851)",
        851,
        "engagement_force",
        "Thames valley and Surrey",
        (
            "Identity limited to the host from the Chronicle's 350-ship Thames "
            "incursion that fought at Aclea."
        ),
        [
            "wave8_danish_vikings_he_aclea",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
    _entity(
        _WESSEX_871_ID,
        "Æthelred and Alfred's West Saxon Campaign Army (871)",
        871,
        "campaign_army",
        "Wessex",
        (
            "Identity limited to the royal West Saxon army in the 871 Reading-"
            "to-Meretun campaign; it is reused only at Ashdown and Meretun here."
        ),
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_cambridge_alfred",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
    _entity(
        _GREAT_ARMY_871_ID,
        "Great Army in the Wessex Campaign (871)",
        871,
        "campaign_army",
        "Wessex",
        (
            "Identity limited to the continuing Great Army opposed by Æthelred "
            "and Alfred in 871; it is reused only at Ashdown and Meretun here."
        ),
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_cambridge_alfred",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
    _entity(
        _FARNHAM_WESSEX_ID,
        "Edward's West Saxon Field Army at Farnham (893)",
        893,
        "engagement_force",
        "Wessex and Surrey",
        "Identity limited to the English intercepting force at Farnham.",
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_he_farnham",
            "wave8_danish_vikings_surrey_farnham",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
    _entity(
        _FARNHAM_VIKING_ID,
        "Appledore Army's Raiding Detachment at Farnham (893)",
        893,
        "engagement_force",
        "Kent, Hampshire, Berkshire, and Surrey",
        (
            "Identity limited to the plunder-bearing detachment intercepted at "
            "Farnham after leaving the Appledore army's position."
        ),
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_he_farnham",
            "wave8_danish_vikings_surrey_farnham",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_DANISH_VIKINGS_SOURCES
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


_ROW_HASHES = {
    "hced-Aclea851-1": (
        "a937b401c5cd89ef8a6525c1a47a95a2134c679ba8aa63662d28024f41fb9c31"
    ),
    "hced-Ashdown871-1": (
        "89effd46d7ebc1acdbbf3adebb9bde1b20c7ab57d8cfad384dbab70e1deb7d85"
    ),
    "hced-Dyle891-1": (
        "2f33f1a8acb214c89abc890958622091d462899165fa0ee07f76a4f49b9bfeef"
    ),
    "hced-Farnham893-1": (
        "932c3f72caacc1d44fe9e102fcd180a758c226921f0ccf735cacfcd2a106dc4c"
    ),
    "hced-La Gueule891-1": (
        "3e968135745eaf6e62b3c33b7854a1c85ce5fe5382c98e10e641321b9b9eaf3e"
    ),
    "hced-Merton871-1": (
        "4355b88b26dec575774b3918d4a44abe7baa3dbc18b49208be55deccdb1e12d0"
    ),
    "hced-Thanet851-1": (
        "0d8a932fa39470ac9303c78faa6a3591071f38cc65021ecc16784d4084895f15"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    winner_side: int,
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(outcome_source_ids))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(set(evidence_refs)),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_DANISH_VIKINGS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Aclea851-1": _contract(
        "hced-Aclea851-1",
        _canonical("Battle of Aclea", 851, "851"),
        "thames_invasion_851",
        [_ACLEA_WESSEX_ID],
        [_ACLEA_VIKING_ID],
        1,
        [
            "wave8_danish_vikings_he_aclea",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        ["wave8_danish_vikings_yale_asc_ninth_century"],
        (
            "The Chronicle identifies Æthelwulf and Æthelbald's West Saxon army "
            "as defeating the host from the 350-ship Thames incursion. The host "
            "is not equated with the separate force overwintering on Thanet. "
            "Aclea's location remains disputed, so the staged point is withheld."
        ),
        confidence=0.94,
    ),
    "hced-Ashdown871-1": _contract(
        "hced-Ashdown871-1",
        _canonical(
            "Battle of Ashdown",
            871,
            "January 871",
            date_precision="month",
        ),
        "great_army_wessex_campaign_871",
        [_WESSEX_871_ID],
        [_GREAT_ARMY_871_ID],
        1,
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_cambridge_alfred",
            "wave8_danish_vikings_he_ashdown",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        (
            "Both chronicles record the West Saxon victory over the two divisions "
            "of the continuing Great Army. The exact battlefield within the "
            "Berkshire Downs remains disputed, and HCED's Sussex point is withheld."
        ),
        confidence=0.97,
    ),
    "hced-Farnham893-1": _contract(
        "hced-Farnham893-1",
        _canonical(
            "Battle of Farnham",
            893,
            "893 (Chronicle annal 894, recte 893)",
        ),
        "appledore_raiding_campaign_893",
        [_FARNHAM_WESSEX_ID],
        [_FARNHAM_VIKING_ID],
        1,
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_he_farnham",
            "wave8_danish_vikings_surrey_farnham",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_surrey_farnham",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        (
            "The sources record the English interception, rout, and recovery of "
            "the raiders' booty; Æthelweard names Edward. The force is the exact "
            "Appledore-derived detachment, not every army active later at "
            "Buttington or Benfleet. The exact battlefield is unknown, so the "
            "town-centre point is withheld."
        ),
        confidence=0.95,
    ),
    "hced-Merton871-1": _contract(
        "hced-Merton871-1",
        _canonical(
            "Battle of Meretun",
            871,
            "March 871",
            date_precision="month",
        ),
        "great_army_wessex_campaign_871",
        [_GREAT_ARMY_871_ID],
        [_WESSEX_871_ID],
        1,
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_cambridge_alfred",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        [
            "wave8_danish_vikings_aethelweard_book_four",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        (
            "Both chronicles say the West Saxons initially drove the two divisions "
            "back but the Great Army held the battlefield and won. Meretun's site "
            "is unidentified; HCED's Devon coordinate is therefore withheld."
        ),
        confidence=0.94,
    ),
}


WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Thanet851-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Thanet851-1"],
        "canonical_event": _canonical(
            "First recorded Viking overwintering on Thanet",
            851,
            "851",
            granularity="noncompetitive_overwintering_notice",
        ),
        "cohort": "thames_invasion_851",
        "disposition": "terminal_exclusion",
        "hold_category": "noncompetitive_overwintering_misattributed_as_battle",
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": [
            "wave8_danish_vikings_he_sandwich_851",
            "wave8_danish_vikings_yale_asc_ninth_century",
        ],
        "hold_reason": (
            "The Chronicle says only that a force first overwintered on Thanet. "
            "It separately records the naval Battle of Sandwich, where Æthelstan "
            "and Ealhhere captured ships and drove the remaining force off, and "
            "the later Aclea battle. No competitive Thanet engagement or Danish "
            "victory can be recovered from the row; unknown is excluded, never drawn."
        ),
    }
}

# The common exact-lane API calls every nonpromotion a hold.  This disposition
# is terminal because the source describes no competitive engagement to revisit.
WAVE8_DANISH_VIKINGS_HOLDS = WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS
WAVE8_DANISH_VIKINGS_CONTRACT_IDS = frozenset(WAVE8_DANISH_VIKINGS_CONTRACTS)
WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS
)
WAVE8_DANISH_VIKINGS_HOLD_IDS = WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSION_IDS
WAVE8_DANISH_VIKINGS_RESERVED_IDS = (
    WAVE8_DANISH_VIKINGS_CONTRACT_IDS | WAVE8_DANISH_VIKINGS_HOLD_IDS
)
WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS = WAVE8_DANISH_VIKINGS_RESERVED_IDS
WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_DANISH_VIKINGS_CONTRACT_IDS
)
WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_DANISH_VIKINGS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}

# There is no matching ancient battle in the locked IWBD snapshot.  The names
# are signed so a future snapshot cannot introduce a probable twin silently.
WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "851": (
        "aclea",
        "battle of aclea",
        "battle of oakley",
        "battle of ockley",
        "battle of thanet",
        "oakley",
        "ockley",
        "thanet",
    ),
    "871": (
        "aescesdun",
        "ashdown",
        "battle of aescesdun",
        "battle of ashdown",
        "battle of marden",
        "battle of marton",
        "battle of meretun",
        "battle of merton",
        "marden",
        "marton",
        "meretun",
        "merton",
    ),
    "891": (
        "battle of dyle",
        "battle of leuven",
        "battle of leuven dyle",
        "battle of maastricht",
        "battle of the dyle leuven",
        "battle of the geul",
        "battle on the geul",
        "dyle",
        "geul",
        "la gueule",
        "leuven",
        "louvain",
        "maastricht",
    ),
    "893": ("battle of farnham", "farnham"),
}


# The concurrent Germany lane already owns the two exact 891 contracts because
# it resolves that cohort's remaining Germany rows and signs both sides of this
# continuing campaign.  This lane fingerprints but never reserves or emits them.
# The composite 877 row is a separate ownership boundary outside the exact label.
WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Dyle891-1": {
        "source_dataset": "hced",
        "disposition": "external_lane_owner",
        "owner_module": "military_elo.promotion.wave8_germany",
        "raw_row_sha256": _ROW_HASHES["hced-Dyle891-1"],
        "canonical_event_name": "Battle of the Dyle (Leuven)",
        "year": 891,
        "reason": (
            "The concurrent Germany lane owns the exact East Frankish-versus-"
            "Viking campaign contract, its bounded actors, and the required Dyle "
            "point quarantine. Emitting it here would double-rate one battle."
        ),
    },
    "hced-La Gueule891-1": {
        "source_dataset": "hced",
        "disposition": "external_lane_owner",
        "owner_module": "military_elo.promotion.wave8_germany",
        "raw_row_sha256": _ROW_HASHES["hced-La Gueule891-1"],
        "canonical_event_name": "Battle on the Geul",
        "year": 891,
        "reason": (
            "The concurrent Germany lane owns the exact Geul contract and shares "
            "only its bounded 891 Viking campaign army with Dyle. Emitting the "
            "same candidate in this lane would invent a second Elo update."
        ),
    },
    "hced-Inverdovat877-1": {
        "source_dataset": "hced",
        "disposition": "not_owned_composite_label",
        "relationship": "distinct_composite_dublin_and_danish_force",
        "raw_row_sha256": (
            "af130b8630beadb653872552ffa2038821e3edd4aac9cb8e8f69560f642d1303"
        ),
        "reason": (
            "Its exact side string is 'Vikings of Dublin, Danish Vikings', not "
            "the Danish Vikings label. Neither this lane nor wave8_irish_history "
            "has evidence to collapse that composite into one of its bounded forces."
        ),
    }
}
WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS = frozenset(
    candidate_id
    for candidate_id, disposition in WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS.items()
    if disposition["disposition"] == "external_lane_owner"
)
WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS = {
    **WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS,
    **WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_DANISH_VIKINGS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_DANISH_VIKINGS_ENTITIES,
        "expected_candidate_ids": sorted(
            WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS
        ),
        "holds": WAVE8_DANISH_VIKINGS_HOLDS,
        "integration_dispositions": WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_DANISH_VIKINGS_SOURCES,
    }


def wave8_danish_vikings_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Patched after the final payload is measured.
WAVE8_DANISH_VIKINGS_FINAL_AUDIT_SIGNATURE = (
    "4347a70e2f3d213902def5fac80d5c0fe30b54ae03c459a001a98b4f3635250f"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_DANISH_VIKINGS_CONTRACTS), len(WAVE8_DANISH_VIKINGS_HOLDS)) != (
        4,
        1,
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_DANISH_VIKINGS_ENTITIES),
        len(WAVE8_DANISH_VIKINGS_SOURCES),
    ) != (6, 8):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_DANISH_VIKINGS_RESERVED_IDS
        != WAVE8_DANISH_VIKINGS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_DANISH_VIKINGS_CONTRACT_IDS & WAVE8_DANISH_VIKINGS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and exclusions overlap")
    if (
        WAVE8_DANISH_VIKINGS_RESERVED_IDS
        | WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS
    ) != WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory is incomplete")
    if WAVE8_DANISH_VIKINGS_RESERVED_IDS & WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS:
        raise ValueError(f"{_LANE_NAME} reserves an externally owned candidate")
    if (
        wave8_danish_vikings_audit_signature()
        != WAVE8_DANISH_VIKINGS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_DANISH_VIKINGS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_DANISH_VIKINGS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_DANISH_VIKINGS_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_DANISH_VIKINGS_ENTITIES
    }
    forbidden_exact_names = {
        "danes",
        "danish vikings",
        "denmark",
        "east francia",
        "northmen",
        "vikings",
        "wessex",
    }
    for entity in WAVE8_DANISH_VIKINGS_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} opened a non-campaign identity window")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic fallback")
        if str(entity["name"]).casefold() in forbidden_exact_names:
            raise ValueError(f"{_LANE_NAME} created a timeless actor")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_DANISH_VIKINGS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} has an invalid queue hash")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if (
            canonical["canonical_key"] != expected_key
            or canonical["granularity"] != "engagement"
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded identity")
        year = int(canonical["year_low"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if (entity["start_year"], entity["end_year"]) != (year, year):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        used_entities.update(side_1 | side_2)

        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} changed a source outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} used a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_DANISH_VIKINGS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )

    exclusion = WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS["hced-Thanet851-1"]
    if (
        exclusion["disposition"] != "terminal_exclusion"
        or exclusion["result_type"] != "unknown"
        or exclusion["reviewed_outcome"] != "unknown"
        or exclusion["unknown_is_never_draw"] is not True
        or "winner_side" in exclusion
    ):
        raise ValueError(f"{_LANE_NAME} Thanet exclusion changed")
    if exclusion["canonical_event"]["granularity"] == "engagement":
        raise ValueError(f"{_LANE_NAME} converted Thanet into a battle")
    if not _is_sorted_unique(exclusion["evidence_refs"]):
        raise ValueError(f"{_LANE_NAME} Thanet evidence is not canonical")
    used_sources.update(map(str, exclusion["evidence_refs"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} invented an outcome override")
    if WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    for names in WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(names) or any(
            name != normalize_label(name) for name in names
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
    audited_names = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    canonical_names = {
        (
            int(contract["canonical_event"]["year_low"]),
            normalize_label(contract["canonical_event"]["name"]),
        )
        for contract in WAVE8_DANISH_VIKINGS_CONTRACTS.values()
    }
    canonical_names.update(
        (
            int(disposition["year"]),
            normalize_label(disposition["canonical_event_name"]),
        )
        for candidate_id, disposition in (
            WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS.items()
        )
        if candidate_id in WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS
    )
    if not canonical_names <= audited_names:
        raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")
    if set(WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS) != {
        "hced-Dyle891-1",
        "hced-Inverdovat877-1",
        "hced-La Gueule891-1",
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane boundary changed")
    if WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS != {
        "hced-Dyle891-1",
        "hced-La Gueule891-1",
    }:
        raise ValueError(f"{_LANE_NAME} external ownership changed")
    for candidate_id in WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS:
        disposition = WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS[candidate_id]
        if (
            disposition["owner_module"]
            != "military_elo.promotion.wave8_germany"
            or disposition["raw_row_sha256"] != _ROW_HASHES[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} Germany ownership contract changed")
    if WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_DANISH_VIKINGS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")


def validate_wave8_danish_vikings_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_DANISH_VIKINGS_CONTRACTS,
        WAVE8_DANISH_VIKINGS_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id in WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS:
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} external owner {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        expected = WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS[candidate_id][
            "raw_row_sha256"
        ]
        if canonical_hced_row_sha256(rows[0]) != expected:
            raise ValueError(
                f"{_LANE_NAME} external owner {candidate_id} raw-row fingerprint "
                "changed"
            )
    return {
        "external_owner_contracts": len(WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": (
            result["reviewed_hced_rows"]
            + len(WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS)
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best"):
        try:
            value = row.get(field)
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def validate_wave8_danish_vikings_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on external owners, the composite row, and probable twins."""

    validate_wave8_danish_vikings_queue_contracts(hced_rows)
    existing = list(existing_events)
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for related_id, disposition in (
        WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS.items()
    ):
        related = hced_by_id.get(related_id, [])
        if len(related) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related {related_id} row, "
                f"found {len(related)}"
            )
        if canonical_hced_row_sha256(related[0]) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} {related_id} ownership fingerprint changed"
            )

    external_release = [
        event
        for event in existing
        if event.get("hced_candidate_id")
        in WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS
    ]
    external_counts = Counter(
        str(event["hced_candidate_id"]) for event in external_release
    )
    if any(count != 1 for count in external_counts.values()) or any(
        not str(event.get("id") or "").startswith("hced_wave8_germany_")
        for event in external_release
    ):
        raise ValueError(f"{_LANE_NAME} external owner release contract changed")

    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_DANISH_VIKINGS_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _row_year(row) is not None
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {iwbd_matches}"
        )

    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if _row_year(event) is not None
        and (_row_year(event), normalize_label(event.get("name"))) in audited
        and event.get("hced_candidate_id")
        not in (
            WAVE8_DANISH_VIKINGS_CONTRACT_IDS
            | WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS
        )
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": 3,
        "external_owner_hced_dispositions": 2,
        "integration_dispositions": 3,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "release_probable_twins": 0,
    }


def install_wave8_danish_vikings_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_DANISH_VIKINGS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_danish_vikings_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_DANISH_VIKINGS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_danish_vikings_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_danish_vikings_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_DANISH_VIKINGS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_danish_vikings_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_DANISH_VIKINGS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_danish_vikings_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_DANISH_VIKINGS_CROSS_LANE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_DANISH_VIKINGS_EXTERNAL_OWNER_IDS
        ),
        "holds": len(WAVE8_DANISH_VIKINGS_HOLDS),
        "integration_dispositions": len(
            WAVE8_DANISH_VIKINGS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_DANISH_VIKINGS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_DANISH_VIKINGS_ENTITIES),
        "new_sources": len(WAVE8_DANISH_VIKINGS_SOURCES),
        "newly_rated_events": len(WAVE8_DANISH_VIKINGS_CONTRACTS),
        "outcome_overrides": len(WAVE8_DANISH_VIKINGS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_DANISH_VIKINGS_CONTRACTS),
        "locally_reserved_hced_rows": len(WAVE8_DANISH_VIKINGS_RESERVED_IDS),
        "reviewed_hced_rows": len(WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS),
        "terminal_exclusions": len(
            WAVE8_DANISH_VIKINGS_TERMINAL_EXCLUSIONS
        ),
        "touched_hced_rows": len(WAVE8_DANISH_VIKINGS_TOUCHED_CANDIDATE_IDS),
    }


def wave8_danish_vikings_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_DANISH_VIKINGS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_DANISH_VIKINGS_POINT_QUARANTINE_ADDITIONS,
    }
