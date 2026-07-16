"""Exact Wave 8 disposition for unresolved medieval Wales HCED rows.

The lane is deliberately candidate-keyed and fail-closed.  It never resolves the
HCED label ``Wales`` as a timeless polity: promoted Welsh participants are bound
to one documented campaign, regime, or engagement, and every other row remains
an explicit semantic-fingerprint hold.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 Wales"
_ENGLAND_ENTITY_ID = "kingdom_england"
_WESSEX_ENTITY_ID = "clio_gb_anglo_saxon_1_534_747d30b5"

WAVE8_WALES_FINAL_AUDIT_SIGNATURE = (
    "547cd0435d6c1e8ef94c6ff05256edfcbdefe8b4089650b9a7832f5c8106136c"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "linked_reference",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": roles,
    }


WAVE8_WALES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_wales_coflein_irfon_bridge_1282",
        "Irfon Bridge; Pont Irfon; Battle of Orewin Bridge, Builth Wells",
        "https://coflein.gov.uk/en/sites/403411",
        (
            "Royal Commission on the Ancient and Historical Monuments of Wales "
            "(Coflein)"
        ),
        "official_battlefield_inventory",
        "rcahmw_coflein_battlefields",
        outcome=True,
    ),
    _source(
        "wave8_wales_coflein_bridge_of_boats_1282",
        "Moel-y-Don: possible site of the Bridge of Boats battle",
        "https://coflein.gov.uk/en/sites/404319",
        (
            "Royal Commission on the Ancient and Historical Monuments of Wales "
            "(Coflein)"
        ),
        "official_battlefield_inventory",
        "rcahmw_coflein_battlefields",
        outcome=True,
    ),
    _source(
        "wave8_wales_coflein_coleshill_1157",
        "Coleshill; Cwnsyllt, supposed site of battle in 1157, near Flint",
        "https://coflein.gov.uk/en/sites/402325",
        (
            "Royal Commission on the Ancient and Historical Monuments of Wales "
            "(Coflein)"
        ),
        "official_battlefield_inventory",
        "rcahmw_coflein_battlefields",
        outcome=True,
    ),
    _source(
        "wave8_wales_coflein_bryn_glas_1402",
        "Bryn Glas battlefield, Pilleth",
        "https://coflein.gov.uk/en/sites/306352",
        (
            "Royal Commission on the Ancient and Historical Monuments of Wales "
            "(Coflein)"
        ),
        "official_battlefield_inventory",
        "rcahmw_coflein_battlefields",
        outcome=True,
    ),
    _source(
        "wave8_wales_dwb_rhys_ap_tewdwr_1093",
        "Rhys ap Tewdwr (died 1093), king of Deheubarth (1078-1093)",
        "https://biography.wales/article/s11-RHYS-APT-1093.html",
        (
            "Dictionary of Welsh Biography, National Library of Wales and "
            "University of Wales Centre for Advanced Welsh and Celtic Studies"
        ),
        "academic_national_biography",
        "dictionary_of_welsh_biography",
    ),
    _source(
        "wave8_wales_cvhs_aberdare_legend",
        "Cynon Valley historical timeline: the Norman conquest tradition",
        "https://www.cvhs.org.uk/timeline/chron.html",
        "Cynon Valley History Society",
        "local_historical_research",
        "cynon_valley_history_society",
    ),
    _source(
        "wave8_wales_oen_beandun_614",
        (
            "The Year's Work in Old English Studies: review of 'The Anglo-Saxon "
            "Chronicle for 614 and Brean Down, Somerset'"
        ),
        "https://www.oenewsletter.org/OEN/archive/OEN39_2.pdf",
        "Old English Newsletter",
        "academic_review",
        "old_english_newsletter",
    ),
    _source(
        "wave8_wales_antiquaries_lulworth_beandun",
        "An Early Iron Age 'beach-head' at Lulworth, Dorset",
        (
            "https://www.cambridge.org/core/journals/antiquaries-journal/article/"
            "an-early-iron-age-beachhead-at-lulworth-dorset/"
            "5C9BC3CE22AC55020C27738FD12A8730"
        ),
        "The Antiquaries Journal, Cambridge University Press",
        "academic_journal_article",
        "antiquaries_journal",
    ),
    _source(
        "wave8_wales_battlefields_maes_moydog_1295",
        "Maes Moydog (5 March 1295): historical and documentary research",
        (
            "https://www.walesher1974.org/her/app/php/herumd.php?"
            "docid=301448840&group=CPAT&level=3"
        ),
        "Welsh Battlefields Project / Clwyd-Powys Archaeological Trust",
        "commissioned_battlefield_research",
        "welsh_battlefields_research",
    ),
    _source(
        "wave8_wales_epns_peonnum_658",
        "Canon and King's Pyon and Pyon Wood, Herefordshire",
        (
            "https://www.nottingham.ac.uk/research/groups/epns/documents/"
            "journal/53-2021/jepns-53-2021-freeman.pdf"
        ),
        "Journal of the English Place-Name Society",
        "academic_journal_article",
        "english_place_name_society",
    ),
    _source(
        "wave8_wales_ystradowen_archaeology_2012",
        (
            "Land at Ystradowen, Vale of Glamorgan, Wales: Heritage Desk-Based "
            "Assessment"
        ),
        (
            "https://www.walesher1974.org/her/groups/GGAT/media/ReportPDF/"
            "3344_LandatYstradowenDBA.pdf"
        ),
        "Cotswold Archaeology / Glamorgan-Gwent Archaeological Trust",
        "archaeological_assessment",
        "cotswold_archaeology",
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: list[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Wales",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited by a generic Wales identity, another Welsh "
            "dynasty or regime, or any predecessor or successor."
        ),
        "source_ids": source_ids,
    }


WAVE8_WALES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "llywelyn_ap_gruffudd_final_war_forces_1282",
        "Llywelyn ap Gruffudd's final-war forces (1282)",
        "regime_bounded_princely_force",
        1282,
        [
            "wave8_wales_coflein_bridge_of_boats_1282",
            "wave8_wales_coflein_irfon_bridge_1282",
        ],
        (
            "Conflict- and regime-bounded forces resisting Edward I in the final "
            "1282 war under Llywelyn ap Gruffudd."
        ),
    ),
    _entity(
        "dafydd_cynan_gwynedd_ambush_force_1157",
        "Dafydd and Cynan's Gwynedd ambush force at Coleshill (1157)",
        "event_bounded_princely_force",
        1157,
        ["wave8_wales_coflein_coleshill_1157"],
        (
            "The event-bounded force of Owain Gwynedd's sons Dafydd and Cynan in "
            "the wooded-pass engagement against Henry II."
        ),
    ),
    _entity(
        "owain_glyndwr_bryn_glas_force_1402",
        "Owain Glyndŵr's force at Bryn Glas (1402)",
        "event_bounded_rebel_force",
        1402,
        ["wave8_wales_coflein_bryn_glas_1402"],
        (
            "The event-bounded Glyndŵr force that fought Edmund Mortimer's army at "
            "Bryn Glas on 22 June 1402."
        ),
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


WAVE8_WALES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Aber Edw1282-1": {
        "raw_row_sha256": (
            "6c8705e0a66bff324340e75441c610ac14994191a80073bb9b0cfead2e7e6ac9"
        ),
        "canonical_event": _canonical(
            "Battle of Irfon Bridge",
            1282,
            "11 December 1282",
            date_precision="day",
        ),
        "cohort": "llywelyn_final_war_1282",
        "side_1_entity_ids": [_ENGLAND_ENTITY_ID],
        "side_2_entity_ids": [
            "llywelyn_ap_gruffudd_final_war_forces_1282"
        ],
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": 0.88,
        "evidence_refs": ["wave8_wales_coflein_irfon_bridge_1282"],
        "outcome_source_ids": ["wave8_wales_coflein_irfon_bridge_1282"],
        "outcome_source_family_ids": ["rcahmw_coflein_battlefields"],
        "source_outcome_override": False,
        "reservation": (
            "The rating is the English tactical victory over Llywelyn's field force "
            "on 11 December only; the exact place where Llywelyn himself was killed "
            "remains uncertain and no later Welsh regime inherits this result."
        ),
        "audit_note": (
            "Aber Edw is normalized to the documented Irfon/Orewin Bridge engagement "
            "of 11 December 1282 between Edward I's host and Llywelyn ap Gruffudd's "
            "final-war force. Reservation: the exact place where Llywelyn himself "
            "was killed remains uncertain, and only the tactical field result is rated."
        ),
    },
    "hced-Bangor1282-1": {
        "raw_row_sha256": (
            "b6d39c216c267517338e77d3fc3366c4aa2db4070b54a6237e3cbe39acf2b4c5"
        ),
        "canonical_event": _canonical(
            "Bridge of Boats",
            1282,
            "6 November 1282",
            date_precision="day",
        ),
        "cohort": "llywelyn_final_war_1282",
        "side_1_entity_ids": [
            "llywelyn_ap_gruffudd_final_war_forces_1282"
        ],
        "side_2_entity_ids": [_ENGLAND_ENTITY_ID],
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": 0.86,
        "evidence_refs": ["wave8_wales_coflein_bridge_of_boats_1282"],
        "outcome_source_ids": [
            "wave8_wales_coflein_bridge_of_boats_1282"
        ],
        "outcome_source_family_ids": ["rcahmw_coflein_battlefields"],
        "source_outcome_override": False,
        "reservation": (
            "The traditional Moel-y-don location is not accepted as exact; Bangor is "
            "one of two modern site hypotheses, so the HCED point remains unreviewed "
            "source provenance rather than a verified battlefield coordinate."
        ),
        "audit_note": (
            "The Bangor row is bound to the Bridge of Boats disaster of 6 November "
            "1282, when Luke de Tany's stranded English force was defeated by the "
            "forces resisting Edward under Llywelyn's regime. Reservation: the "
            "traditional Moel-y-don site is misleading and the exact bridge site is "
            "not asserted."
        ),
    },
    "hced-Coleshill1157-1": {
        "raw_row_sha256": (
            "0288d1c578bfa73edc3e532e7f3a69d2a9ff2bee611ffd1f4d7795b2d2261132"
        ),
        "canonical_event": _canonical(
            "Battle of Coleshill",
            1157,
            "1157 (exact day unresolved)",
        ),
        "cohort": "owain_gwynedd_1157",
        "side_1_entity_ids": [_ENGLAND_ENTITY_ID],
        "side_2_entity_ids": ["dafydd_cynan_gwynedd_ambush_force_1157"],
        "winner_side": 2,
        "war_type": "interstate",
        "confidence": 0.80,
        "evidence_refs": ["wave8_wales_coflein_coleshill_1157"],
        "outcome_source_ids": ["wave8_wales_coflein_coleshill_1157"],
        "outcome_source_family_ids": ["rcahmw_coflein_battlefields"],
        "source_outcome_override": True,
        "reservation": (
            "The override scores only Dafydd and Cynan's successful wooded-pass "
            "ambush against Henry II's detachment; it does not turn Owain's later "
            "withdrawal or Henry's wider campaign settlement into a Welsh victory."
        ),
        "audit_note": (
            "The near-contemporary narrative records Dafydd and Cynan giving sharp "
            "battle, killing many of the king's men, and Henry's surviving troops "
            "escaping. That narrow tactical result reverses HCED's English-victory "
            "orientation. Reservation: the wider 1157 campaign and peace are not rated."
        ),
    },
    "hced-Pilleth1402-1": {
        "raw_row_sha256": (
            "53596a66b9293c758f5a5165fe6bfb002256e8c1effca462e32e355c5aaf456e"
        ),
        "canonical_event": _canonical(
            "Battle of Bryn Glas",
            1402,
            "22 June 1402",
            date_precision="day",
        ),
        "cohort": "glyndwr_revolt_1402",
        "side_1_entity_ids": ["owain_glyndwr_bryn_glas_force_1402"],
        "side_2_entity_ids": [_ENGLAND_ENTITY_ID],
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": 0.90,
        "evidence_refs": ["wave8_wales_coflein_bryn_glas_1402"],
        "outcome_source_ids": ["wave8_wales_coflein_bryn_glas_1402"],
        "outcome_source_family_ids": ["rcahmw_coflein_battlefields"],
        "source_outcome_override": False,
        "reservation": (
            "The exact hill footprint remains debated; the rating is confined to "
            "Glyndŵr's force defeating Edmund Mortimer's English army on 22 June "
            "1402 and does not create a successor Wales identity."
        ),
        "audit_note": (
            "Pilleth is normalized to Bryn Glas on 22 June 1402, where Owain "
            "Glyndŵr's force defeated Edmund Mortimer's English army, killed many of "
            "its men, and captured Mortimer. Reservation: the exact hill footprint "
            "is not asserted."
        ),
    },
}


WAVE8_WALES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Aberdare, Wales1093-1": {
        "raw_row_sha256": (
            "0f6373655de9c46d5fe2e2447a02649be011666fe834a014fc2929ff0f31ab32"
        ),
        "canonical_event": _canonical(
            "Claimed battle at Aberdare",
            1093,
            "HCED asserts 1093; the local legend also circulates as 1091",
            granularity="claimed_engagement",
        ),
        "hold_category": "claimed_event_not_historically_supported",
        "hold_reason": (
            "Modern scholarship places Rhys ap Tewdwr's Easter 1093 death near "
            "Brecon against Bernard de Neufmarché's Norman settlers, while the "
            "Fitzhamon-Iestyn battle at Aberdare/Hirwaun is a rejected late legend."
        ),
        "reviewed_outcome": "no rateable Aberdare engagement established",
        "known_side_entity_ids": [],
        "unresolved_fields": [
            "engagement_authenticity",
            "event_location",
            "exact_sides",
        ],
        "reservation": (
            "Do not remap the row to Rhys's distinct and uncertain-circumstance death "
            "near Brecon, and do not credit a Kingdom of England victory from the "
            "legend's Norman adventurers."
        ),
        "evidence_refs": [
            "wave8_wales_dwb_rhys_ap_tewdwr_1093",
            "wave8_wales_cvhs_aberdare_legend",
        ],
    },
    "hced-Beandun614-1": {
        "raw_row_sha256": (
            "d2600f40646b4b011c8bf18828d87d978f75072b951c123a8f52d9b064493b3f"
        ),
        "canonical_event": _canonical("Beandun", 614, "614"),
        "hold_category": "exact_brittonic_belligerent_unresolved",
        "hold_reason": (
            "The Anglo-Saxon Chronicle supports a victory by Cynegils and Cwichelm "
            "over Britons, but scholarship still disputes Beandun's location and "
            "does not securely identify the defeated Brittonic polity."
        ),
        "reviewed_outcome": "West Saxon victory asserted by the Chronicle",
        "known_side_entity_ids": [_WESSEX_ENTITY_ID],
        "unresolved_fields": [
            "battlefield_location",
            "exact_brittonic_belligerent",
        ],
        "reservation": (
            "Old English Wealas/Britons is not modern or timeless Wales; neither "
            "Dumnonia nor a south-Welsh kingdom is inferred from a disputed place-name."
        ),
        "evidence_refs": [
            "wave8_wales_oen_beandun_614",
            "wave8_wales_antiquaries_lulworth_beandun",
        ],
    },
    "hced-Conwy1295-1": {
        "raw_row_sha256": (
            "131269b6a288ef243e8031ccce79eee11b3083a4eacc8266c80b26680c579233"
        ),
        "canonical_event": _canonical(
            "Conwy 1295 assertion",
            1295,
            (
                "HCED asserts 1295; Maes Moydog is securely dated 5 March 1295"
            ),
            granularity="unresolved_engagement",
        ),
        "hold_category": "event_conflation_and_location_unresolved",
        "hold_reason": (
            "The commissioned battlefield study distinguishes Edward I's winter "
            "blockade and eventual recovery at Conwy from Warwick's 5 March victory "
            "at Maes Moydog, and identifies the older placement of that battle near "
            "Conwy as erroneous. HCED's row cannot be bound safely to one event."
        ),
        "reviewed_outcome": (
            "English victory at Maes Moydog is secure, but not attributable to this "
            "Conwy-labelled candidate"
        ),
        "known_side_entity_ids": [_ENGLAND_ENTITY_ID],
        "unresolved_fields": [
            "engagement_identity",
            "battlefield_location",
            "exact_rebel_force",
        ],
        "reservation": (
            "Do not silently rename the candidate to Maes Moydog or convert the "
            "multi-week confinement at Conwy into a single competitive English win."
        ),
        "evidence_refs": ["wave8_wales_battlefields_maes_moydog_1295"],
    },
    "hced-Penselwood658-1": {
        "raw_row_sha256": (
            "ea1bd8ad44cc8ca2061dfc8868dc974a54cd10eb8a18f611614862f21b2dc8ef"
        ),
        "canonical_event": _canonical("Peonnum", 658, "658"),
        "hold_category": "exact_brittonic_belligerent_unresolved",
        "hold_reason": (
            "The Chronicle supports Cenwalh's victory over Britons and pursuit to "
            "the Parrett, but academic place-name analysis treats identification of "
            "Peonnum with Penselwood as traditional and qualified; the source does "
            "not name the defeated polity."
        ),
        "reviewed_outcome": "West Saxon victory asserted by the Chronicle",
        "known_side_entity_ids": [_WESSEX_ENTITY_ID],
        "unresolved_fields": [
            "battlefield_location",
            "exact_brittonic_belligerent",
        ],
        "reservation": (
            "A likely south-western British or Dumnonian context is not enough to "
            "open a rateable Dumnonia identity, and the Britons are not generic Wales."
        ),
        "evidence_refs": ["wave8_wales_epns_peonnum_658"],
    },
    "hced-Ystradowen1032-1": {
        "raw_row_sha256": (
            "e0b05bd28c68bde1e62c3b0ba2f385ae8a0ace584a91a6ac113992512d601217"
        ),
        "canonical_event": _canonical(
            "Claimed battle of Cae'r Gywr",
            1032,
            "HCED asserts 1032; the antiquarian claim is dated 1031",
            granularity="claimed_engagement",
        ),
        "hold_category": "spurious_claimed_event",
        "hold_reason": (
            "The archaeological desk assessment finds no evidence for the battle, "
            "traces it only to Samuel Lewis's unspecified annals, and reports that "
            "the notice likely derives from a document forged by Iolo Morganwg."
        ),
        "reviewed_outcome": "no historical competitive outcome established",
        "known_side_entity_ids": [],
        "unresolved_fields": [
            "engagement_authenticity",
            "event_date",
            "exact_sides",
        ],
        "reservation": (
            "Do not create an English defeat, a Welsh victory, or any actor identity "
            "from an unsupported antiquarian claim."
        ),
        "evidence_refs": ["wave8_wales_ystradowen_archaeology_2012"],
    },
}


WAVE8_WALES_CONTRACT_IDS = frozenset(WAVE8_WALES_CONTRACTS)
WAVE8_WALES_HOLD_IDS = frozenset(WAVE8_WALES_HOLDS)
WAVE8_WALES_RESERVED_IDS = WAVE8_WALES_CONTRACT_IDS | WAVE8_WALES_HOLD_IDS
WAVE8_WALES_OUTCOME_OVERRIDE_IDS = frozenset(
    candidate_id
    for candidate_id, contract in WAVE8_WALES_CONTRACTS.items()
    if contract.get("source_outcome_override")
)

_EXPECTED_CONTRACT_IDS = frozenset(
    {
        "hced-Aber Edw1282-1",
        "hced-Bangor1282-1",
        "hced-Coleshill1157-1",
        "hced-Pilleth1402-1",
    }
)
_EXPECTED_HOLD_IDS = frozenset(
    {
        "hced-Aberdare, Wales1093-1",
        "hced-Beandun614-1",
        "hced-Conwy1295-1",
        "hced-Penselwood658-1",
        "hced-Ystradowen1032-1",
    }
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def wave8_wales_signature() -> str:
    """Return the signature over every audited disposition and fixture."""

    payload = {
        "contracts": WAVE8_WALES_CONTRACTS,
        "entities": WAVE8_WALES_ENTITIES,
        "holds": WAVE8_WALES_HOLDS,
        "sources": WAVE8_WALES_SOURCES,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if WAVE8_WALES_CONTRACT_IDS != _EXPECTED_CONTRACT_IDS:
        raise ValueError("Wave 8 Wales promotion inventory changed")
    if WAVE8_WALES_HOLD_IDS != _EXPECTED_HOLD_IDS:
        raise ValueError("Wave 8 Wales hold inventory changed")
    if WAVE8_WALES_CONTRACT_IDS & WAVE8_WALES_HOLD_IDS:
        raise ValueError("Wave 8 Wales promotion and hold inventories overlap")
    if wave8_wales_signature() != WAVE8_WALES_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Wales final audit signature changed")
    if WAVE8_WALES_OUTCOME_OVERRIDE_IDS != frozenset(
        {"hced-Coleshill1157-1"}
    ):
        raise ValueError("Wave 8 Wales outcome override inventory changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_WALES_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_WALES_ENTITIES}
    if len(source_by_id) != len(WAVE8_WALES_SOURCES):
        raise ValueError("Wave 8 Wales source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_WALES_ENTITIES):
        raise ValueError("Wave 8 Wales entity IDs are not unique")
    if {"wales", "welsh", "cymru"} & set(entity_by_id):
        raise ValueError("Wave 8 Wales may not install a generic Wales identity")

    for entity in WAVE8_WALES_ENTITIES:
        entity_id = str(entity["id"])
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 8 Wales identity must be alias-free: {entity_id}")
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"Wave 8 Wales identity is not event bounded: {entity_id}")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"Wave 8 Wales identity lacks a rating reset: {entity_id}")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 Wales identity has an unknown source: {entity_id}")

    for candidate_id, item in {
        **WAVE8_WALES_CONTRACTS,
        **WAVE8_WALES_HOLDS,
    }.items():
        if len(str(item["raw_row_sha256"])) != 64:
            raise ValueError(f"Wave 8 Wales row hash is invalid: {candidate_id}")
        if not str(item.get("reservation", "")).strip():
            raise ValueError(f"Wave 8 Wales reservation is missing: {candidate_id}")
        evidence = set(map(str, item["evidence_refs"]))
        if not evidence or not evidence <= set(source_by_id):
            raise ValueError(f"Wave 8 Wales evidence is invalid: {candidate_id}")

    allowed_external_entities = {_ENGLAND_ENTITY_ID}
    for candidate_id, contract in WAVE8_WALES_CONTRACTS.items():
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"Wave 8 Wales sides are invalid: {candidate_id}")
        participants = side_1 | side_2
        if not participants & set(entity_by_id):
            raise ValueError(f"Wave 8 Wales contract lacks a lane identity: {candidate_id}")
        if participants - set(entity_by_id) - allowed_external_entities:
            raise ValueError(f"Wave 8 Wales contract has an unknown identity: {candidate_id}")
        outcome_ids = set(map(str, contract["outcome_source_ids"]))
        if not outcome_ids or not outcome_ids <= set(map(str, contract["evidence_refs"])):
            raise ValueError(f"Wave 8 Wales outcome sources are invalid: {candidate_id}")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcome_ids
        ):
            raise ValueError(
                f"Wave 8 Wales outcome source lacks an outcome role: {candidate_id}"
            )

    for candidate_id, hold in WAVE8_WALES_HOLDS.items():
        if not str(hold.get("hold_reason", "")).strip():
            raise ValueError(f"Wave 8 Wales hold reason is missing: {candidate_id}")
        if not hold.get("unresolved_fields"):
            raise ValueError(f"Wave 8 Wales hold gate is missing: {candidate_id}")


def validate_wave8_wales_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_WALES_CONTRACTS,
        WAVE8_WALES_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_wales_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_WALES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_wales_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_WALES_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_wales_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_wales_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_WALES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_wales_",
    )


def wave8_wales_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_WALES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_wales_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_WALES_HOLDS),
        "newly_rated_events": len(WAVE8_WALES_CONTRACTS),
        "outcome_overrides": len(WAVE8_WALES_OUTCOME_OVERRIDE_IDS),
        "promotion_contracts": len(WAVE8_WALES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_WALES_RESERVED_IDS),
    }
