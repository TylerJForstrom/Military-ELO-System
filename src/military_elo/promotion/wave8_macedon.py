"""Candidate-keyed audit of HCED's six unresolved ``Macedon`` rows.

The label spans different Antigonid kings, a one-battle Hellenic coalition,
and one malformed Fourth-century record.  This lane therefore opens no global
``Macedon`` alias.  Four fingerprinted rows receive narrow, source-backed
tactical dispositions; Chios remains staged because the reviewed sources do
not agree on a competitive result, and ``Thessaly353`` remains staged because
its positive year and generic name cannot identify either of the two Phocian
victories described by Diodorus.
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
    "WAVE8_MACEDON_CONTRACT_IDS",
    "WAVE8_MACEDON_CONTRACTS",
    "WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MACEDON_ENTITIES",
    "WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MACEDON_FUNNEL_AUDIT",
    "WAVE8_MACEDON_HOLD_IDS",
    "WAVE8_MACEDON_HOLDS",
    "WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS",
    "WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MACEDON_RESERVED_IDS",
    "WAVE8_MACEDON_ROW_HASHES",
    "WAVE8_MACEDON_SOURCES",
    "install_wave8_macedon_entities",
    "install_wave8_macedon_sources",
    "promote_wave8_macedon_contracts",
    "validate_wave8_macedon_funnel",
    "validate_wave8_macedon_integration_dispositions",
    "validate_wave8_macedon_queue_contracts",
    "wave8_macedon_audit_signature",
    "wave8_macedon_cohort_counts",
    "wave8_macedon_counts",
    "wave8_macedon_metadata",
)


_LANE_NAME = "Wave 8 exact Macedon actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_macedon"
_EVENT_ID_PREFIX = "hced_wave8_macedon_"
_EXACT_LABELS = frozenset({"macedon"})

_ANTIGONID = "clio_gr_antigonid_emp_bce277_3bbcbfdf"
_ATHENIAN_DEFENDERS = "athenian_defenders_chremonidean_siege_264_262_bce"
_SELLASIA_ALLIANCE = "antigonus_hellenic_alliance_sellasia_222_bce"
_PTOLEMAIC_EGYPT = "ptolemaic_egypt_305_bce"
_ROME = "roman_republic"
_SPARTA = "sparta"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_MACEDON_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_macedon_met_antigonid",
        "Pergamon and the Hellenistic Kingdoms of the Ancient World",
        (
            "https://resources.metmuseum.org/resources/metpublications/pdf/"
            "Pergamon_and_the_Hellenistic_Kingdoms_of_the_Ancient_World.pdf"
        ),
        "The Metropolitan Museum of Art",
        "museum_scholarly_catalogue",
        "met_pergamon_hellenistic_kingdoms",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_macedon_coskun_andros",
        (
            "Ptolemaioi as Commanders in 3rd-Century Asia Minor and Some "
            "Glimpses on Ephesos and Mylasa during the Second and Third Syrian Wars"
        ),
        "https://dergipark.org.tr/tr/download/article-file/501353",
        "Altay Coşkun / Vir Doctus Anatolicus",
        "peer_reviewed_historical_article",
        "coskun_ptolemaioi_commanders",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_livius_andros",
        "Third Syrian War",
        "https://www.livius.org/articles/concept/syrian-war-3/",
        "Livius.org",
        "expert_historical_reference",
        "livius_third_syrian_war",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_pausanias_athens",
        "Pausanias, Description of Greece 3.6.4-6",
        "https://www.theoi.com/Text/Pausanias3A.html",
        "Theoi Classical Texts Library",
        "translated_primary_source",
        "pausanias_description_greece",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_wallace_athens",
        (
            "The Freedom of the Greeks in the Early Hellenistic Period "
            "(337-262 BC): A Study in Ruler-City Relations"
        ),
        (
            "https://era.ed.ac.uk/server/api/core/bitstreams/"
            "7709d1d1-e06e-429b-b5be-2f5e35d92bbd/content"
        ),
        "Shane Wallace / University of Edinburgh",
        "doctoral_historical_thesis",
        "wallace_freedom_greeks_thesis",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_livy_callinicus",
        "Livy, History of Rome, Book 42",
        (
            "https://spiritualpilgrim.net/08_Classics-Library/"
            "hellenist-roman/livy/rome-6-42.htm"
        ),
        "Livy / Spiritual Pilgrim Classics Library",
        "translated_primary_source",
        "livy_ab_urbe_condita",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_appian_callinicus",
        "Appian, The Macedonian Wars 6",
        (
            "https://www.livius.org/sources/content/appian/"
            "appian-the-macedonian-wars/appian-the-macedonian-wars-6/"
        ),
        "Appian / Livius.org",
        "translated_primary_source",
        "appian_macedonian_wars",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_polybius_sellasia",
        "Polybius, Histories, Book 2: Battle of Sellasia",
        "https://penelope.uchicago.edu/thayer/e/roman/texts/polybius/2%2A.html",
        "Polybius / LacusCurtius",
        "translated_primary_source",
        "polybius_histories",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_wiley_sellasia",
        "Sellasia, Battle of",
        "https://onlinelibrary.wiley.com/doi/abs/10.1002/9781444338386.wbeah09220",
        "Ioanna Kralli / The Encyclopedia of Ancient History",
        "scholarly_encyclopedia_entry",
        "kralli_sellasia_encyclopedia",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_macedon_almagor_sellasia",
        "A Literary Passage: Polybius and Plutarch's Narrator",
        "https://histos.org/index.php/histos/article/download/122/116",
        "Eran Almagor / Histos Supplement",
        "peer_reviewed_historical_article",
        "almagor_polybius_plutarch",
        [
            "identity_boundary_or_context_reference",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_macedon_polybius_chios",
        "Polybius, Histories, Book 16: Battle of Chios",
        "https://penelope.uchicago.edu/Thayer/e/roman/texts/polybius/16%2A.html",
        "Polybius / LacusCurtius",
        "translated_primary_source",
        "polybius_histories",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_macedon_panovski_chios",
        "Comfortably Sunk: Philip, the Battle of Chios and the List of Losses in Polybius",
        (
            "https://repository.ukim.mk/bitstream/20.500.12188/791/1/"
            "Comfortably_Sunk_Philip_the_Battle_of_Ch.pdf"
        ),
        "Stefan Panovski and Vojislav Sarakinski / Kratistos",
        "scholarly_historical_article",
        "panovski_sarakinski_chios",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_macedon_diodorus_thessaly",
        "Diodorus Siculus, Library of History, Book 16.35",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Diodorus_Siculus/16B%2A.html"
        ),
        "Diodorus Siculus / LacusCurtius",
        "translated_primary_source",
        "diodorus_library_history",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_macedon_ocd_onomarchus",
        "Onomarchus",
        (
            "https://academic.oup.com/edited-volume/61673/"
            "chapter-abstract/549696210"
        ),
        "Oxford Classical Dictionary",
        "scholarly_encyclopedia_entry",
        "oxford_classical_dictionary",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_MACEDON_SOURCES}


WAVE8_MACEDON_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _ANTIGONID,
        "name": "Antigonid Macedonia",
        "kind": "hellenistic_kingdom",
        "start_year": -277,
        "end_year": -168,
        "region": "Macedonia and the southern Balkans",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated Antigonid dynastic-state identity from Antigonus II Gonatas' "
            "accession through the Roman defeat and abolition of the monarchy in "
            "168 BCE. It reuses the Cliopatria candidate ID but opens no generic "
            "Macedon or Macedonia alias and inherits no rating from Alexander's "
            "kingdom, successor coalitions, or Roman provincial Macedonia."
        ),
        "source_ids": ["cliopatria_v020", "wave8_macedon_met_antigonid"],
    },
    {
        "id": _ATHENIAN_DEFENDERS,
        "name": "Athenian defenders during Antigonus's siege (264-262 BCE)",
        "kind": "siege_bounded_city_defender",
        "start_year": -264,
        "end_year": -262,
        "region": "Athens and Attica",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Athenian civic defenders under Antigonus II's blockade "
            "and siege in the closing phase of the Chremonidean War. Sparta and "
            "Ptolemaic forces attempted separate relief operations but are not "
            "folded into this defender rating because Pausanias says the forces "
            "did not unite. This is not a generic Athens identity."
        ),
        "source_ids": [
            "wave8_macedon_pausanias_athens",
            "wave8_macedon_wallace_athens",
        ],
    },
    {
        "id": _SELLASIA_ALLIANCE,
        "name": "Antigonus's Hellenic alliance at Sellasia (222 BCE)",
        "kind": "engagement_bounded_multistate_coalition",
        "start_year": -222,
        "end_year": -222,
        "region": "Laconia and the Peloponnese",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the coalition commanded by Antigonus III Doson at "
            "Sellasia: Macedonian, Achaean, Megalopolitan, Boeotian, Epirote, "
            "Acarnanian, Illyrian, mercenary, and other contingents. One coalition "
            "rating avoids inventing contribution shares and does not extend to "
            "Macedon, the Achaean League, or any later Hellenic alliance."
        ),
        "source_ids": [
            "wave8_macedon_almagor_sellasia",
            "wave8_macedon_polybius_sellasia",
            "wave8_macedon_wiley_sellasia",
        ],
    },
)


WAVE8_MACEDON_ROW_HASHES: dict[str, str] = {
    "hced-Andros-245-1": "4e947f4d8b747454250c16e6a83b4bc00cf0d288dae964215bafdaa86b0570a1",
    "hced-Athens, Greece-264-1": "5c04e70ab1eac2d55dbf186a4536e8cae700bc277b230d956617a78c92dcaa89",
    "hced-Callicinus-171-1": "e74c368e250da1b71a750a5712b615b98ab5b98c959eba797dbd310312a1e83a",
    "hced-Chios-201-1": "560f737d00941d4c5f9c64e8a22ea6f03c3f7a2947c5beae5ed995b93a2e4723",
    "hced-Sellasia-222-1": "d9cb804fac2308ea845e19585397b1092b7c356142fc158d6c7c1b2dd978e48a",
    "hced-Thessaly353-1": "e24d9202e46b27111ef4d9e9e2db6df8b1ce744f00a8faff07b04bca05d1b1ba",
}

WAVE8_MACEDON_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "macedon": {
        "candidate_ids": [],
        "centuries": {"BCE_02": 1, "BCE_03": 4, "CE_04": 1},
        "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": (
            "c7c53c77e71580b3c9a5d18fcc690779e5f80c207e5d2e09c8b55b752d8fefeb"
        ),
        "events_touched": 6,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 6,
        },
        "label": "macedon",
        "rated_counterpart_entities": 3,
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 6,
    }
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    granularity: str = "pitched_battle",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": "year" if year_low == year_high else "range",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    actor_override: str,
    date_source_ids: Iterable[str] = (),
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    date_sources = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_MACEDON_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "source_date_override": bool(date_sources),
        "date_source_ids": date_sources,
        "actor_override": actor_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_MACEDON_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Andros-245-1": _contract(
        "hced-Andros-245-1",
        _canonical(
            "Battle of Andros",
            -246,
            -245,
            (
                "Most scholarship dates the naval victory to 246 or 245 BCE; "
                "Coşkun narrows it to autumn 246 through spring 245 and argues "
                "for August 246"
            ),
            "naval_battle",
        ),
        "antigonid_macedonia_hellenistic_wars",
        [_ANTIGONID],
        [_PTOLEMAIC_EGYPT],
        {"wave8_macedon_coskun_andros", "wave8_macedon_livius_andros"},
        {"wave8_macedon_coskun_andros", "wave8_macedon_livius_andros"},
        (
            "Trogus's prologue as analyzed by Coşkun and the independent Livius "
            "chronology identify Antigonus's fleet as victor over the Ptolemaic "
            "fleet. The date span records published uncertainty instead of "
            "pretending HCED's single 245 BCE value is exact."
        ),
        confidence=0.89,
        actor_override="source_backed_antigonid_and_ptolemaic_states",
        date_source_ids={"wave8_macedon_coskun_andros", "wave8_macedon_livius_andros"},
    ),
    "hced-Athens, Greece-264-1": _contract(
        "hced-Athens, Greece-264-1",
        _canonical(
            "Antigonid siege and capture of Athens",
            -264,
            -262,
            (
                "HCED supplies 264 BCE; the reviewed reconstruction treats the "
                "closing siege and capitulation as a 264-262 BCE interval"
            ),
            "siege",
        ),
        "chremonidean_war_athens_siege",
        [_ANTIGONID],
        [_ATHENIAN_DEFENDERS],
        {"wave8_macedon_pausanias_athens", "wave8_macedon_wallace_athens"},
        {"wave8_macedon_pausanias_athens", "wave8_macedon_wallace_athens"},
        (
            "Pausanias says Antigonus invested Athens, the Spartan and Ptolemaic "
            "relief forces never united with its defenders, and Athens ultimately "
            "accepted a Macedonian garrison. The broad HCED loser coalition is "
            "therefore narrowed to the city defenders actually captured."
        ),
        confidence=0.92,
        actor_override="source_backed_siege_defender_split",
        date_source_ids={"wave8_macedon_pausanias_athens", "wave8_macedon_wallace_athens"},
    ),
    "hced-Callicinus-171-1": _contract(
        "hced-Callicinus-171-1",
        _canonical(
            "Battle of Callinicus",
            -171,
            -171,
            "171 BCE in Livy and Appian",
        ),
        "third_macedonian_war_callinicus",
        [_ANTIGONID],
        [_ROME],
        {"wave8_macedon_appian_callinicus", "wave8_macedon_livy_callinicus"},
        {"wave8_macedon_appian_callinicus", "wave8_macedon_livy_callinicus"},
        (
            "Livy records Roman grief and withdrawal after defeat, while Appian "
            "explicitly calls the engagement Perseus's victory. Only the tactical "
            "engagement is rated; the Third Macedonian War's strategic result is "
            "not inferred from it."
        ),
        confidence=0.98,
        actor_override="source_backed_antigonid_and_roman_states",
    ),
    "hced-Sellasia-222-1": _contract(
        "hced-Sellasia-222-1",
        _canonical(
            "Battle of Sellasia",
            -222,
            -222,
            "Summer 222 BCE in Polybius and the reviewed scholarship",
        ),
        "cleomenean_war_sellasia",
        [_SELLASIA_ALLIANCE],
        [_SPARTA],
        {
            "wave8_macedon_almagor_sellasia",
            "wave8_macedon_polybius_sellasia",
            "wave8_macedon_wiley_sellasia",
        },
        {"wave8_macedon_polybius_sellasia", "wave8_macedon_wiley_sellasia"},
        (
            "Polybius enumerates Antigonus's multi-polity army and narrates its "
            "victory; the encyclopedia independently describes Antigonus at the "
            "head of a Hellenic alliance. The coalition is rated once so no "
            "unsupported contribution shares are manufactured."
        ),
        confidence=0.98,
        actor_override="source_backed_engagement_bounded_hellenic_coalition",
    ),
}


WAVE8_MACEDON_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Chios-201-1": {
        "raw_row_sha256": WAVE8_MACEDON_ROW_HASHES["hced-Chios-201-1"],
        "disposition": "hold",
        "hold_category": "contradictory_outcome_sources",
        "hold_reason": (
            "HCED calls Chios a Macedonian victory, but Polybius says Philip was "
            "decidedly worsted and labels his victory claim imaginary. Panovski "
            "and Sarakinski reject a crushing defeat yet characterize the result "
            "as inconclusive or a draw by losses. These are materially different "
            "competitive labels, so unknown is not converted into either a win "
            "or a draw."
        ),
        "evidence_refs": [
            "wave8_macedon_panovski_chios",
            "wave8_macedon_polybius_chios",
        ],
    },
    "hced-Thessaly353-1": {
        "raw_row_sha256": WAVE8_MACEDON_ROW_HASHES["hced-Thessaly353-1"],
        "disposition": "hold",
        "hold_category": "date_and_engagement_ambiguity",
        "hold_reason": (
            "The positive 353 year conflicts with the BCE Third Sacred War. "
            "Diodorus and the Oxford Classical Dictionary report that Onomarchus "
            "defeated Philip twice in Thessaly, but the generic HCED name does not "
            "identify which engagement it means. Correcting the sign and choosing "
            "one of two battles would invent a unique event."
        ),
        "evidence_refs": [
            "wave8_macedon_diodorus_thessaly",
            "wave8_macedon_ocd_onomarchus",
        ],
    },
}

WAVE8_MACEDON_CONTRACT_IDS = frozenset(WAVE8_MACEDON_CONTRACTS)
WAVE8_MACEDON_HOLD_IDS = frozenset(WAVE8_MACEDON_HOLDS)
WAVE8_MACEDON_RESERVED_IDS = frozenset(
    {*WAVE8_MACEDON_CONTRACT_IDS, *WAVE8_MACEDON_HOLD_IDS}
)
WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS = WAVE8_MACEDON_CONTRACT_IDS
WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named action and modern Greek "
            "jurisdiction, but do not bind HCED's exact coordinate to the closed "
            "release location-provenance contract. Retain the source-transcribed "
            "country and withhold the unexplained point."
        ),
        "evidence_refs": sorted(contract["evidence_refs"]),
    }
    for candidate_id, contract in sorted(WAVE8_MACEDON_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MACEDON_CONTRACTS,
        "entities": WAVE8_MACEDON_ENTITIES,
        "funnel": WAVE8_MACEDON_FUNNEL_AUDIT,
        "holds": WAVE8_MACEDON_HOLDS,
        "location_reasons": WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_MACEDON_ROW_HASHES,
        "sources": WAVE8_MACEDON_SOURCES,
    }


def wave8_macedon_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE = (
    "72f9e67abee0a05c258cc20ca868940f68c09117c66b121de51301e52e812498"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_MACEDON_ENTITIES}
    if len(source_ids) != len(WAVE8_MACEDON_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_ANTIGONID, _ATHENIAN_DEFENDERS, _SELLASIA_ALLIANCE}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_MACEDON_RESERVED_IDS != set(WAVE8_MACEDON_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS != WAVE8_MACEDON_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_MACEDON_LOCATION_QUARANTINE_REASONS) != WAVE8_MACEDON_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_windows = {
        _ANTIGONID: (-277, -168),
        _ATHENIAN_DEFENDERS: (-264, -262),
        _SELLASIA_ALLIANCE: (-222, -222),
    }
    used_sources: set[str] = set()
    for entity in WAVE8_MACEDON_ENTITIES:
        entity_id = str(entity["id"])
        if (
            entity["aliases"]
            or (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]
            or normalize_label(entity["name"]) in _EXACT_LABELS
            or not _is_sorted_unique(entity["source_ids"])
        ):
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    expected_canonicals = {
        "hced-Andros-245-1": (-246, -245, _ANTIGONID, _PTOLEMAIC_EGYPT),
        "hced-Athens, Greece-264-1": (-264, -262, _ANTIGONID, _ATHENIAN_DEFENDERS),
        "hced-Callicinus-171-1": (-171, -171, _ANTIGONID, _ROME),
        "hced-Sellasia-222-1": (-222, -222, _SELLASIA_ALLIANCE, _SPARTA),
    }
    for candidate_id, contract in WAVE8_MACEDON_CONTRACTS.items():
        low, high, side_1, side_2 = expected_canonicals[candidate_id]
        canonical = contract["canonical_event"]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or (canonical["year_low"], canonical["year_high"]) != (low, high)
            or contract["side_1_entity_ids"] != [side_1]
            or contract["side_2_entity_ids"] != [side_2]
        ):
            raise ValueError(f"{_LANE_NAME} contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or not _is_sorted_unique(date_sources)
            or not set(outcomes) <= set(evidence) <= source_ids
            or not set(date_sources) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        expected_date_override = candidate_id in {
            "hced-Andros-245-1",
            "hced-Athens, Greece-264-1",
        }
        if contract["source_date_override"] is not expected_date_override:
            raise ValueError(f"{_LANE_NAME} date-override drift: {candidate_id}")
        used_sources.update(evidence)

    expected_holds = {
        "hced-Chios-201-1": "contradictory_outcome_sources",
        "hced-Thessaly353-1": "date_and_engagement_ambiguity",
    }
    for candidate_id, hold in WAVE8_MACEDON_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != expected_holds[candidate_id]
            or not _is_sorted_unique(hold["evidence_refs"])
            or not set(hold["evidence_refs"]) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        used_sources.update(map(str, hold["evidence_refs"]))

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_macedon_audit_signature() != WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_macedon_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _EXACT_LABELS
        or normalize_label(row.get("side_2_raw")) in _EXACT_LABELS
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_MACEDON_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected_rows = {
        "hced-Andros-245-1": (-245, "Macedon", "Ptolmeic Egypt", "Macedon"),
        "hced-Athens, Greece-264-1": (
            -264,
            "Macedon",
            "Athens, Sparta, Egypt",
            "Macedon",
        ),
        "hced-Callicinus-171-1": (-171, "Macedon", "Rome", "Macedon"),
        "hced-Chios-201-1": (-201, "Macedon", "Pergamum, Rhodes", "Macedon"),
        "hced-Sellasia-222-1": (-222, "Macedon", "Sparta", "Macedon"),
        "hced-Thessaly353-1": (353, "Phocis", "Macedon", "Phocis"),
    }
    for candidate_id, expected_hash in WAVE8_MACEDON_ROW_HASHES.items():
        row = by_id[candidate_id]
        year, side_1, side_2, winner = expected_rows[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            (row.get("year_low"), row.get("year_high")) != (year, year)
            or row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != winner
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} raw-row semantics changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MACEDON_CONTRACTS,
        WAVE8_MACEDON_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_macedon_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    rows = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if row.get("label") in _EXACT_LABELS
    }
    if set(rows) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label missing")
    row = rows["macedon"]
    checks = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "centuries": dict(row.get("centuries", {})),
        "components_bridged": int(row.get("components_bridged", -1)),
        "components_touched": int(row.get("components_touched", -1)),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_MACEDON_FUNNEL_AUDIT["macedon"]["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    expected = WAVE8_MACEDON_FUNNEL_AUDIT["macedon"]
    if checks != expected:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {checks}")
    return {
        "events_touched": expected["events_touched"],
        "holds": len(WAVE8_MACEDON_HOLDS),
        "sole_blocker_events": expected["sole_blocker_events"],
        "unresolved_side_attempts": expected["unresolved_side_attempts"],
        "zero_time_valid_candidates": expected["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_DUPLICATE_ALIASES: dict[int, set[str]] = {
    -246: {"Andros", "Battle of Andros"},
    -245: {"Andros", "Battle of Andros"},
    -264: {"Athens, Greece", "Siege of Athens", "Capture of Athens"},
    -263: {"Siege of Athens", "Capture of Athens"},
    -262: {"Siege of Athens", "Capture of Athens"},
    -222: {"Sellasia", "Battle of Sellasia"},
    -171: {"Callicinus", "Callinicus", "Battle of Callinicus"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for year, aliases in _DUPLICATE_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_macedon_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_macedon_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_MACEDON_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_MACEDON_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_macedon_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MACEDON_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_macedon_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MACEDON_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_macedon_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_macedon_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MACEDON_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_macedon_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MACEDON_CONTRACTS.values()
            ).items()
        )
    )


def wave8_macedon_counts() -> dict[str, int]:
    return {
        "country_quarantine_additions": len(WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS),
        "holds": len(WAVE8_MACEDON_HOLDS),
        "new_entities": len(WAVE8_MACEDON_ENTITIES),
        "new_sources": len(WAVE8_MACEDON_SOURCES),
        "newly_rated_events": len(WAVE8_MACEDON_CONTRACTS),
        "outcome_overrides": sum(
            bool(contract.get("source_outcome_override"))
            for contract in WAVE8_MACEDON_CONTRACTS.values()
        ),
        "point_quarantine_additions": len(WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_MACEDON_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MACEDON_RESERVED_IDS),
        "source_date_overrides": sum(
            bool(contract.get("source_date_override"))
            for contract in WAVE8_MACEDON_CONTRACTS.values()
        ),
        "terminal_exclusions": 0,
    }


def wave8_macedon_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_macedon_counts(),
        "cohorts": wave8_macedon_cohort_counts(),
        "final_audit_signature": WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_MACEDON_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_MACEDON_HOLD_IDS),
    }


_validate_static()
