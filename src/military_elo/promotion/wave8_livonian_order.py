"""Candidate-keyed Wave 8 audit for HCED's exact ``Livonian Order`` label.

The queue's seven exact-label rows span 1279-1560 and cannot be resolved by
opening one generic medieval-order identity.  In particular, the Livonian
Brothers of the Sword ended as an independent order when their survivors were
incorporated into the Teutonic Order in 1237; the later Livonian branch was
also distinct from the Teutonic Order's Prussian branch, the wider Livonian
Confederation, its auxiliaries, and its secular successors.

Only the four rows pinned by the authoritative funnel as sole blockers are
promoted.  Their actors are era- or event-bounded, and their tactical outcomes
are supported by direct institutional or academic sources.  The three other
exact rows remain explicit paired-identity or coalition holds.  A held or
unknown result is never converted to a draw.
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
    "WAVE8_LIVONIAN_ORDER_CONTRACT_IDS",
    "WAVE8_LIVONIAN_ORDER_CONTRACTS",
    "WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_LIVONIAN_ORDER_ENTITIES",
    "WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS",
    "WAVE8_LIVONIAN_ORDER_FINAL_AUDIT_SIGNATURE",
    "WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT",
    "WAVE8_LIVONIAN_ORDER_HOLD_IDS",
    "WAVE8_LIVONIAN_ORDER_HOLDS",
    "WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS",
    "WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_LIVONIAN_ORDER_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS",
    "WAVE8_LIVONIAN_ORDER_NONPROMOTIONS",
    "WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES",
    "WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS",
    "WAVE8_LIVONIAN_ORDER_RESERVED_IDS",
    "WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS",
    "WAVE8_LIVONIAN_ORDER_SOURCES",
    "WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSION_IDS",
    "WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS",
    "install_wave8_livonian_order_entities",
    "install_wave8_livonian_order_sources",
    "promote_wave8_livonian_order_contracts",
    "validate_wave8_livonian_order_funnel",
    "validate_wave8_livonian_order_integration_dispositions",
    "validate_wave8_livonian_order_queue_contracts",
    "wave8_livonian_order_audit_signature",
    "wave8_livonian_order_cohort_counts",
    "wave8_livonian_order_counts",
    "wave8_livonian_order_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Livonian Order exact-label audit"
_EVENT_ID_PREFIX = "hced_wave8_livonian_order_"
_MODULE_OWNER = "wave8_livonian_order"

_TSARDOM_OF_RUSSIA_ID = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"


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


WAVE8_LIVONIAN_ORDER_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_livonian_order_oxford_baltic_crusades",
        "Baltic Crusades",
        "https://doi.org/10.1093/obo/9780199791279-0257",
        "Oxford University Press, Oxford Bibliographies",
        "scholarly_reference_article",
        "oxford_bibliographies_baltic_crusades",
    ),
    _source(
        "wave8_livonian_order_rudolph_viterbo",
        (
            "Die Union von Viterbo (1237): Zur Inkorporation der "
            "Schwertbrüder in den Deutschen Orden im urkundlichen Befund"
        ),
        "https://doi.org/10.18452/20180",
        "Humboldt-Universität zu Berlin",
        "scholarly_article",
        "rudolph_viterbo_incorporation_study",
    ),
    _source(
        "wave8_livonian_order_militzer_recruitment",
        "The Recruitment of Brethren for the Teutonic Order in Livonia, 1237-1562",
        "https://doi.org/10.4324/9781315085937-28",
        "Routledge",
        "scholarly_book_chapter",
        "militzer_livonian_branch_recruitment",
    ),
    _source(
        "wave8_livonian_order_vle_aizkraukle",
        "Aizkrauklės mūšis",
        "https://www.vle.lt/straipsnis/aizkraukles-musis/",
        "Visuotinė lietuvių enciklopedija",
        "national_scholarly_encyclopedia",
        "vle_aizkraukle_battle",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_kirby_northern_europe",
        "Northern Europe in the Early Modern Period: The Baltic World 1492-1772",
        (
            "https://www.routledge.com/Northern-Europe-in-the-Early-Modern-"
            "Period-The-Baltic-World-1492-1772/Kirby/p/book/9780582004115"
        ),
        "Routledge",
        "scholarly_monograph",
        "kirby_baltic_world_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_ostrowski_poe_old_russia",
        "Portraits of Old Russia: Imagined Lives of Ordinary People, 1300-1745",
        (
            "https://www.routledge.com/Portraits-of-Old-Russia-Imagined-Lives-"
            "of-Ordinary-People-1300-1745/Ostrowski-Poe/p/book/9780765627292"
        ),
        "Routledge",
        "scholarly_monograph",
        "ostrowski_poe_old_russia_chronology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_baranov_smolino",
        (
            "Contra Multitudinem Ruthenorum Armatorum: The Russian-Livonian "
            "Battle of Lake Smolino (1502) Reconsidered"
        ),
        "https://doi.org/10.2307/j.ctv13nb9q8.28",
        "Brill",
        "peer_reviewed_book_chapter",
        "baranov_lake_smolino_reconsidered",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_sproule_mercenary",
        "Livonian Mercenary Warfare and Fiscal Responses to the Military Crisis of 1558-1561",
        "https://doi.org/10.1017/S0008938921000042",
        "Cambridge University Press, Central European History",
        "peer_reviewed_journal_article",
        "sproule_livonian_mercenary_warfare",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_viljandi_museum_fellin",
        "The Livonian War and the Fall of Fellin",
        "https://muuseum.viljandimaa.ee/vana/indexbf72.html?id=52&op=body",
        "Museum of Viljandi",
        "institutional_museum_history",
        "viljandi_museum_fellin_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_narva_city_history",
        "Narva linn: ajalugu",
        "https://www.narva.ee/linn-uudised-kontaktid/linn/narva-linn",
        "City of Narva",
        "official_municipal_history",
        "narva_city_official_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_narva_museum_history",
        "Our History",
        "https://narvamuuseum.ee/en/muuseum/meie-ajalugu/",
        "Narva Museum",
        "institutional_museum_history",
        "narva_museum_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_esper_russia_baltic",
        "Russia and the Baltic 1494-1558",
        "https://doi.org/10.2307/2492857",
        "Cambridge University Press, Slavic Review",
        "peer_reviewed_journal_article",
        "esper_russia_baltic_article",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_frost_northern_wars",
        "The Northern Wars: War, State and Society in Northeastern Europe, 1558-1721",
        "https://doi.org/10.4324/9781315845678",
        "Routledge",
        "scholarly_monograph",
        "frost_northern_wars_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_balcerek_daugava",
        "Wars on the Daugava River in the Sixteenth Century on the Margins of Vitalii Penskoi's Books",
        "https://doi.org/10.22364/lviz.117.10",
        "Institute of Latvian History, University of Latvia",
        "peer_reviewed_journal_article",
        "balcerek_daugava_wars_review",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_baranauskas_dissertation",
        "The Battle of Pabaiskas 1435: Pivotal Years in the Development of Lithuanian Statehood",
        "https://hdl.handle.net/20.500.12259/36823",
        "Vytautas Magnus University",
        "doctoral_dissertation",
        "baranauskas_pabaiskas_dissertation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_livonian_order_baranauskas_armies",
        "The Composition and Sizes of the Armies at the Battle of Pabaiskas",
        "https://doi.org/10.6001/lituanistica.v62i3.3374",
        "Lithuanian Academy of Sciences, Lituanistica",
        "peer_reviewed_journal_article",
        "baranauskas_pabaiskas_armies_article",
        outcome=True,
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or transferred to the independent "
            "Livonian Brothers of the Sword, another Teutonic branch, the wider "
            "Livonian Confederation, an omitted coalition ally, or a secular "
            "successor."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_LIVONIAN_BRANCH_ID = "livonian_branch_teutonic_order_1237_1561"
_SMOLINO_MUSCOVITE_COALITION_ID = (
    "muscovite_novgorodian_pskovian_smolino_coalition_1502"
)
_FELLIN_DEFENCE_ID = "fellin_order_garrison_defence_1560"
_NARVA_DEFENCE_ID = "narva_order_city_castle_defence_1558"
_ERGEME_FORCE_ID = "ergeme_order_auxiliary_field_force_1560"


WAVE8_LIVONIAN_ORDER_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _LIVONIAN_BRANCH_ID,
        "Livonian branch of the Teutonic Order (1237-1561)",
        "era_bounded_military_order_branch",
        1237,
        1561,
        "Livonia",
        [
            "wave8_livonian_order_baranov_smolino",
            "wave8_livonian_order_militzer_recruitment",
            "wave8_livonian_order_oxford_baltic_crusades",
            "wave8_livonian_order_rudolph_viterbo",
        ],
        (
            "Bounded to the Livonian branch formed after the documented 1237 "
            "incorporation and ending with its secular dissolution. It is not an "
            "alias for the pre-1237 Sword Brothers, the Prussian Teutonic state, "
            "all five Livonian territorial polities, or their coalition partners."
        ),
    ),
    _entity(
        _SMOLINO_MUSCOVITE_COALITION_ID,
        "Muscovite, Novgorodian, and Pskovian field coalition at Lake Smolino (1502)",
        "event_bounded_field_coalition",
        1502,
        1502,
        "Pskov region",
        [
            "wave8_livonian_order_baranov_smolino",
            "wave8_livonian_order_kirby_northern_europe",
        ],
        (
            "Bounded to the combined host directly identified at Lake Smolino; "
            "it does not reduce Novgorodian and Pskovian forces to a timeless "
            "Moscow label or rate every force of the Grand Duchy of Moscow."
        ),
    ),
    _entity(
        _FELLIN_DEFENCE_ID,
        "Fellin city and Order-castle defence (1560)",
        "event_bounded_mixed_garrison",
        1560,
        1560,
        "Fellin (Viljandi), Livonia",
        [
            "wave8_livonian_order_oxford_baltic_crusades",
            "wave8_livonian_order_sproule_mercenary",
            "wave8_livonian_order_viljandi_museum_fellin",
        ],
        (
            "Bounded to the citizens, Order servants, mercenaries, and local "
            "defenders of Fellin's city and castle under Wilhelm von Fürstenberg. "
            "It is not a proxy for every Livonian Order formation in 1560."
        ),
    ),
    _entity(
        _NARVA_DEFENCE_ID,
        "Narva city and Order-castle defence (1558)",
        "event_bounded_city_castle_defence",
        1558,
        1558,
        "Narva, Livonia",
        [
            "wave8_livonian_order_narva_city_history",
            "wave8_livonian_order_narva_museum_history",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
        (
            "Bounded to the city and castle defenders during the May 1558 "
            "Russian capture. It does not treat Narva's inhabitants, the whole "
            "Order branch, or the Livonian Confederation as interchangeable."
        ),
    ),
    _entity(
        _ERGEME_FORCE_ID,
        "Livonian Order and auxiliary field force at Ērģeme (1560)",
        "event_bounded_order_auxiliary_force",
        1560,
        1560,
        "Ērģeme, Livonia",
        [
            "wave8_livonian_order_balcerek_daugava",
            "wave8_livonian_order_frost_northern_wars",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
        (
            "Bounded to the few hundred Order members and roughly five hundred "
            "auxiliaries under Philipp Schall von Bell at Ērģeme. Auxiliary "
            "partners are kept inside this one event-specific formation."
        ),
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Aizkraulke1279-1": (
        "0b72cf4fed12e0d8aeca1dc2dca7c500d22a8e449566fc55ad2ebe536384c4b9"
    ),
    "hced-Fellin1560-1": (
        "33a499d0eec87a755e3d6d17b6573b2c1ca83733e0f73d4ca0d1f5e1dccadfc1"
    ),
    "hced-Helmed1501-1": (
        "50fa7b8198b114a0bbe117dea2d1d740264273038cf0ebed49e5e1f473049296"
    ),
    "hced-Lake Smolino1502-1": (
        "c30748c23294daf6ae8134b9cb5c32d46adfa360b7677118f2b1425bf05dc6f7"
    ),
    "hced-Narva1558-1": (
        "4abe069abd81fcda6a1b8da1bac616dc266b6eb7456ed4482bce142f0083bea6"
    ),
    "hced-Oomuli1560-1": (
        "5bfdf717361f61308ab1be22a3efa69007c2255a42021a19a248e24119411c42"
    ),
    "hced-Wilkomierz1435-1": (
        "319ba2bb8c3cb1dcf9d2f18d23433c8ad67da6a1cfe23fa24581de193f5840c5"
    ),
}


_SOLE_BLOCKER_IDS = frozenset(
    {
        "hced-Fellin1560-1",
        "hced-Lake Smolino1502-1",
        "hced-Narva1558-1",
        "hced-Oomuli1560-1",
    }
)
_OTHER_IDENTITY_BLOCKER_IDS = frozenset(_ROW_HASHES) - _SOLE_BLOCKER_IDS


WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "57fce904f7f47658baca08f28413afa99111f7d465efe0a7520c061c68e57adf"
    ),
    "events_touched": 7,
    "failure_case": "zero_time_valid_candidates",
    "failure_case_count": 7,
    "label": "livonian order",
    "marginal_events": 4,
    "newly_unblocked_candidate_id_sha256": (
        "8d35ae2da31bf0da56b17ff6d5540d49513268b3142da604291f960c12a019a1"
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
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
    outcome_reversal: bool = False,
) -> dict[str, Any]:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_LIVONIAN_ORDER_SOURCES
    }
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": outcome_reversal,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_LIVONIAN_ORDER_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Fellin1560-1": _contract(
        "hced-Fellin1560-1",
        _canonical(
            "Siege and capture of Fellin (Viljandi)",
            1560,
            "August 1560",
            date_precision="month",
            granularity="siege_and_capture",
        ),
        "livonian_war_1558_1561",
        [_TSARDOM_OF_RUSSIA_ID],
        [_FELLIN_DEFENCE_ID],
        1,
        [
            "wave8_livonian_order_oxford_baltic_crusades",
            "wave8_livonian_order_sproule_mercenary",
            "wave8_livonian_order_viljandi_museum_fellin",
        ],
        [
            "wave8_livonian_order_sproule_mercenary",
            "wave8_livonian_order_viljandi_museum_fellin",
        ],
        (
            "The peer-reviewed fiscal study dates Fellin's fall to August 1560 "
            "and identifies the unpaid garrison's surrender to the Muscovite "
            "army. Viljandi Museum independently details the siege, city breach, "
            "and castle mutiny. The loser is the bounded mixed defence, not a "
            "generic Order or every polity of the Livonian Confederation."
        ),
        confidence=0.94,
    ),
    "hced-Lake Smolino1502-1": _contract(
        "hced-Lake Smolino1502-1",
        _canonical(
            "Battle of Lake Smolino",
            1502,
            "13 September 1502",
            date_precision="day",
        ),
        "muscovite_livonian_war_1501_1503",
        [_LIVONIAN_BRANCH_ID],
        [_SMOLINO_MUSCOVITE_COALITION_ID],
        1,
        [
            "wave8_livonian_order_baranov_smolino",
            "wave8_livonian_order_kirby_northern_europe",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
        [
            "wave8_livonian_order_baranov_smolino",
            "wave8_livonian_order_kirby_northern_europe",
        ],
        (
            "HCED's incomplete Draw is rejected rather than treated as evidence. "
            "Baranov's source-based study dates the battle to 13 September 1502 "
            "and identifies an outnumbered Livonian victory over Muscovite, "
            "Novgorodian, and Pskovian forces; Kirby independently records the "
            "Livonian victory. Unknown is never converted to a draw."
        ),
        confidence=0.95,
        source_outcome_override=True,
    ),
    "hced-Narva1558-1": _contract(
        "hced-Narva1558-1",
        _canonical(
            "Capture of Narva",
            1558,
            "11 May 1558",
            date_precision="day",
            granularity="city_capture",
        ),
        "livonian_war_1558_1561",
        [_NARVA_DEFENCE_ID],
        [_TSARDOM_OF_RUSSIA_ID],
        2,
        [
            "wave8_livonian_order_esper_russia_baltic",
            "wave8_livonian_order_narva_city_history",
            "wave8_livonian_order_narva_museum_history",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
        [
            "wave8_livonian_order_esper_russia_baltic",
            "wave8_livonian_order_narva_city_history",
            "wave8_livonian_order_narva_museum_history",
        ],
        (
            "The official city history dates the fire-assisted Muscovite capture "
            "to 11 May 1558 and the museum confirms Ivan IV's conquest; Esper's "
            "academic study independently identifies Russia's conquest of Narva. "
            "This directly reverses HCED's proposed Livonian winner while rating "
            "only the bounded city-and-castle defence."
        ),
        confidence=0.96,
        source_outcome_override=True,
        outcome_reversal=True,
    ),
    "hced-Oomuli1560-1": _contract(
        "hced-Oomuli1560-1",
        _canonical(
            "Battle of Ērģeme",
            1560,
            "2 August 1560",
            date_precision="day",
        ),
        "livonian_war_1558_1561",
        [_TSARDOM_OF_RUSSIA_ID],
        [_ERGEME_FORCE_ID],
        1,
        [
            "wave8_livonian_order_balcerek_daugava",
            "wave8_livonian_order_frost_northern_wars",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
        [
            "wave8_livonian_order_balcerek_daugava",
            "wave8_livonian_order_frost_northern_wars",
        ],
        (
            "Frost dates the engagement near Ermes/Ērģeme to 2 August 1560 and "
            "describes the small Order-and-auxiliary force being overwhelmed by "
            "several thousand Muscovites. The University of Latvia review "
            "independently records the Russian defeat of the Livonians at Ermes. "
            "The raw Oomuli name is retained only as an alias."
        ),
        confidence=0.95,
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


WAVE8_LIVONIAN_ORDER_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Aizkraulke1279-1": _hold(
        "hced-Aizkraulke1279-1",
        _canonical(
            "Battle of Aizkraukle",
            1279,
            "5 March 1279",
            date_precision="day",
        ),
        "paired_identity_and_livonian_coalition_hold",
        "lithuanian_victory_attested_but_not_rateable_in_this_tranche",
        [
            "the Lithuanian force",
            (
                "the later Livonian branch's army with a Danish Tallinn "
                "contingent and Curonian and Semigallian auxiliaries"
            ),
        ],
        (
            "The national scholarly encyclopedia establishes the Lithuanian "
            "victory and names the Danish, Curonian, and Semigallian components. "
            "The exact row is also blocked on Lithuania, and its raw dyad omits "
            "coalition partners. It is not promoted in this single-label tranche; "
            "the unrated result remains unknown and is never encoded as a draw."
        ),
        [
            "wave8_livonian_order_oxford_baltic_crusades",
            "wave8_livonian_order_rudolph_viterbo",
            "wave8_livonian_order_vle_aizkraukle",
        ],
    ),
    "hced-Helmed1501-1": _hold(
        "hced-Helmed1501-1",
        _canonical(
            "Battle near Helme",
            1501,
            "November 1501",
            date_precision="month",
        ),
        "paired_pre_tsardom_identity_and_force_composition_hold",
        "russian_victory_attested_but_not_rateable_in_this_tranche",
        [
            "the pre-tsardom Muscovite and allied Russian host",
            "the bounded Livonian force defeated near Helme",
        ],
        (
            "Kirby and the Old Russia chronology attest the November 1501 "
            "Russian defeat of the Livonian force, but HCED's Russia opponent is "
            "outside the current Tsardom window and the exact host is not bounded "
            "here. The row is not promoted; its unrated result is unknown, never "
            "a draw."
        ),
        [
            "wave8_livonian_order_kirby_northern_europe",
            "wave8_livonian_order_ostrowski_poe_old_russia",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
    ),
    "hced-Wilkomierz1435-1": _hold(
        "hced-Wilkomierz1435-1",
        _canonical(
            "Battle of Pabaiskas (Wiłkomierz)",
            1435,
            "1 September 1435",
            date_precision="day",
        ),
        "raw_dyad_omits_both_coalitions",
        "sigismund_coalition_victory_attested_but_not_rateable_in_this_tranche",
        [
            "Žygimantas Kęstutaitis's Lithuanian army with Polish auxiliaries",
            (
                "Švitrigaila's Lithuanian coalition with the Livonian landmaster's "
                "force and Tatar allies"
            ),
        ],
        (
            "The dissertation and peer-reviewed army study establish the 1 "
            "September 1435 victory and show that HCED's Poland-versus-Livonian-"
            "Order dyad omits the principal Lithuanian formations and Tatar "
            "partners on both sides. It is not promoted until both coalitions are "
            "independently owned; the unrated result remains unknown, not a draw."
        ),
        [
            "wave8_livonian_order_baranauskas_armies",
            "wave8_livonian_order_baranauskas_dissertation",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
    ),
}


WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_LIVONIAN_ORDER_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_LIVONIAN_ORDER_HOLDS,
    **WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS,
}
WAVE8_LIVONIAN_ORDER_CONTRACT_IDS = frozenset(WAVE8_LIVONIAN_ORDER_CONTRACTS)
WAVE8_LIVONIAN_ORDER_HOLD_IDS = frozenset(WAVE8_LIVONIAN_ORDER_HOLDS)
WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS
)
WAVE8_LIVONIAN_ORDER_RESERVED_IDS = frozenset(
    {
        *WAVE8_LIVONIAN_ORDER_CONTRACTS,
        *WAVE8_LIVONIAN_ORDER_NONPROMOTIONS,
    }
)
WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS = {
    candidate_id: (
        "promote" if candidate_id in WAVE8_LIVONIAN_ORDER_CONTRACT_IDS else "hold"
    )
    for candidate_id in sorted(WAVE8_LIVONIAN_ORDER_RESERVED_IDS)
}


# These are local, promoted-only declarations for later coordinated integration.
# The lane intentionally does not mutate the shared location manifests.
WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Lake Smolino1502-1",
        "hced-Oomuli1560-1",
    }
)
WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_LIVONIAN_ORDER_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Fellin1560-1": {
        "country_disposition": "retain_estonia",
        "point_disposition": "retain_viljandi_city_for_city_and_castle_siege",
        "reason": (
            "The reviewed event encompasses Fellin/Viljandi's city and Order "
            "castle, so the city point is a suitable representational location."
        ),
        "evidence_refs": [
            "wave8_livonian_order_sproule_mercenary",
            "wave8_livonian_order_viljandi_museum_fellin",
        ],
    },
    "hced-Lake Smolino1502-1": {
        "country_disposition": "retain_russia",
        "point_disposition": "quarantine_unverified_lake_geocode",
        "reason": (
            "The direct study places the battle on Lake Smolino's shores south "
            "of Pskov and notes location uncertainty; the HCED coordinate is not "
            "a reviewed battlefield point."
        ),
        "evidence_refs": [
            "wave8_livonian_order_baranov_smolino",
            "wave8_livonian_order_kirby_northern_europe",
        ],
    },
    "hced-Narva1558-1": {
        "country_disposition": "retain_estonia",
        "point_disposition": "retain_narva_city_for_city_capture",
        "reason": (
            "The canonical event is the capture of Narva city and its Order "
            "castle, for which the Narva city point is representational."
        ),
        "evidence_refs": [
            "wave8_livonian_order_narva_city_history",
            "wave8_livonian_order_narva_museum_history",
        ],
    },
    "hced-Oomuli1560-1": {
        "country_disposition": "retain_latvia",
        "point_disposition": "quarantine_oomuli_geocode_not_ergeme_battlefield",
        "reason": (
            "The reviewed engagement was near Ērģeme/Ermes; the raw Oomuli "
            "coordinate is not source-verified as the battlefield."
        ),
        "evidence_refs": [
            "wave8_livonian_order_balcerek_daugava",
            "wave8_livonian_order_frost_northern_wars",
        ],
    },
}


WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Lake Smolino1502-1": {
        "raw_winner_raw": "Draw",
        "raw_loser_raw": None,
        "raw_winner_loser_complete": False,
        "corrected_result_type": "win",
        "corrected_winner_side": 1,
        "corrected_winner_entity_ids": [_LIVONIAN_BRANCH_ID],
        "corrected_loser_entity_ids": [_SMOLINO_MUSCOVITE_COALITION_ID],
        "override_kind": "unknown_draw_placeholder_to_sourced_livonian_victory",
        "rationale": (
            "The raw Draw is incomplete, while the direct academic sources "
            "identify a Livonian tactical victory over the combined Russian host."
        ),
        "outcome_source_ids": WAVE8_LIVONIAN_ORDER_CONTRACTS[
            "hced-Lake Smolino1502-1"
        ]["outcome_source_ids"],
        "outcome_source_family_ids": WAVE8_LIVONIAN_ORDER_CONTRACTS[
            "hced-Lake Smolino1502-1"
        ]["outcome_source_family_ids"],
    },
    "hced-Narva1558-1": {
        "raw_winner_raw": "Livonian Order",
        "raw_loser_raw": "Russia",
        "raw_winner_loser_complete": True,
        "corrected_result_type": "win",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_TSARDOM_OF_RUSSIA_ID],
        "corrected_loser_entity_ids": [_NARVA_DEFENCE_ID],
        "override_kind": "sourced_tactical_outcome_reversal",
        "rationale": (
            "The official and academic histories agree that Ivan IV's forces "
            "captured Narva, directly reversing HCED's proposed orientation."
        ),
        "outcome_source_ids": WAVE8_LIVONIAN_ORDER_CONTRACTS[
            "hced-Narva1558-1"
        ]["outcome_source_ids"],
        "outcome_source_family_ids": WAVE8_LIVONIAN_ORDER_CONTRACTS[
            "hced-Narva1558-1"
        ]["outcome_source_family_ids"],
    },
}


WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Aizkraulke1279-1": {
        "aliases": (
            "aizkraukle",
            "aizkraulke",
            "ascheraden",
            "battle of aizkraukle",
            "battle of ascheraden",
        ),
        "years": (1279, 1279),
    },
    "hced-Fellin1560-1": {
        "aliases": (
            "capture of fellin",
            "capture of viljandi",
            "fellin",
            "siege and capture of fellin",
            "siege of fellin",
            "siege of viljandi",
            "viljandi",
        ),
        "years": (1560, 1560),
    },
    "hced-Helmed1501-1": {
        "aliases": ("battle of helme", "battle of helmed", "helme", "helmed"),
        "years": (1501, 1501),
    },
    "hced-Lake Smolino1502-1": {
        "aliases": (
            "battle of lake smolino",
            "battle of smolina",
            "battle of smolino",
            "lake smolina",
            "lake smolino",
            "smolina",
            "smolino",
        ),
        "years": (1502, 1502),
    },
    "hced-Narva1558-1": {
        "aliases": ("capture of narva", "narva", "siege of narva"),
        "years": (1558, 1558),
    },
    "hced-Oomuli1560-1": {
        "aliases": (
            "battle of ergeme",
            "battle of ermes",
            "battle of oomuli",
            "ergeme",
            "ermes",
            "oomuli",
        ),
        "years": (1560, 1560),
    },
    "hced-Wilkomierz1435-1": {
        "aliases": (
            "battle of pabaiskas",
            "battle of wilkomierz",
            "pabaiskas",
            "swienta",
            "wilkomierz",
        ),
        "years": (1435, 1435),
    },
}


WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Seritsa1501-1": {
        "raw_row_sha256": (
            "99228750fd4befc033f4d0334bef4038647e11c9343d7a9511055e70c3174a4f"
        ),
        "related_candidate_ids": ["hced-Helmed1501-1"],
        "disposition": "defer_non_exact_composite_side_for_independent_coalition_audit",
        "owner_module": None,
        "reason": (
            "Kirby identifies the Livonian victory at Seritsa, but HCED's non-"
            "exact side string combines an anachronistically named Lithuanian-"
            "Polish Commonwealth with the Livonian Order. This exact-label lane "
            "does not split or claim that composite coalition."
        ),
        "evidence_refs": [
            "wave8_livonian_order_kirby_northern_europe",
            "wave8_livonian_order_oxford_baltic_crusades",
        ],
    }
}
WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    f"related_hced:{candidate_id}": disposition
    for candidate_id, disposition in WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS.items()
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_LIVONIAN_ORDER_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_LIVONIAN_ORDER_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS
        ),
        "funnel_audit": WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT,
        "holds": WAVE8_LIVONIAN_ORDER_HOLDS,
        "integration_dispositions": WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT,
        "location_reviews": WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS,
        "outcome_overrides": WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS,
        "row_dispositions": WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS,
        "sources": WAVE8_LIVONIAN_ORDER_SOURCES,
        "terminal_exclusions": WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS,
    }


def wave8_livonian_order_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label audit state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_LIVONIAN_ORDER_FINAL_AUDIT_SIGNATURE = (
    "03c1efc405bbf7befde877442d9186f2cdd40d3484bffbebeaa1f9e8fe35a892"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_LIVONIAN_ORDER_CONTRACTS),
        len(WAVE8_LIVONIAN_ORDER_HOLDS),
        len(WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS),
    ) != (4, 3, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_LIVONIAN_ORDER_ENTITIES),
        len(WAVE8_LIVONIAN_ORDER_SOURCES),
    ) != (5, 16):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_LIVONIAN_ORDER_RESERVED_IDS != WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_LIVONIAN_ORDER_CONTRACT_IDS != _SOLE_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} promotions no longer match sole blockers")
    if WAVE8_LIVONIAN_ORDER_HOLD_IDS != _OTHER_IDENTITY_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} non-sole rows are not fully held")
    if set(WAVE8_LIVONIAN_ORDER_ROW_DISPOSITIONS) != WAVE8_LIVONIAN_ORDER_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} explicit row dispositions are incomplete")
    if wave8_livonian_order_audit_signature() != (
        WAVE8_LIVONIAN_ORDER_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if _sorted_newline_sha256(WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS) != str(
        WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} funnel exact-cohort digest drifted")
    if _sorted_newline_sha256(_SOLE_BLOCKER_IDS) != str(
        WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT[
            "newly_unblocked_candidate_id_sha256"
        ]
    ):
        raise ValueError(f"{_LANE_NAME} funnel sole-blocker digest drifted")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_LIVONIAN_ORDER_SOURCES
    }
    if len(source_by_id) != len(WAVE8_LIVONIAN_ORDER_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {
            str(source["source_family_id"])
            for source in WAVE8_LIVONIAN_ORDER_SOURCES
        }
    ) != len(WAVE8_LIVONIAN_ORDER_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not explicit and unique")
    for source in WAVE8_LIVONIAN_ORDER_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are nondeterministic")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_LIVONIAN_ORDER_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_LIVONIAN_ORDER_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "livonia",
        "livonian brothers of the sword",
        "livonian confederation",
        "livonian order",
        "order of the sword brothers",
        "teutonic order",
    }
    for entity in WAVE8_LIVONIAN_ORDER_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a continuity alias")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity has an invalid era window")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic order identity")
        note = str(entity["continuity_note"]).casefold()
        if (
            "no rating is inherited" not in note
            or "livonian brothers of the sword" not in note
            or "coalition" not in note
        ):
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are nondeterministic")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")
    branch = entity_by_id[_LIVONIAN_BRANCH_ID]
    if (
        int(branch["start_year"]),
        int(branch["end_year"]),
    ) != (1237, 1561):
        raise ValueError(f"{_LANE_NAME} Livonian branch boundary drifted")
    for entity_id, entity in entity_by_id.items():
        if entity_id == _LIVONIAN_BRANCH_ID:
            continue
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} event force is not event-bounded")

    allowed_entity_ids = {*entity_by_id, _TSARDOM_OF_RUSSIA_ID}
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_orientations = {
        "hced-Fellin1560-1": (1, False, False),
        "hced-Lake Smolino1502-1": (1, True, False),
        "hced-Narva1558-1": (2, True, True),
        "hced-Oomuli1560-1": (1, False, False),
    }
    existing_windows = {_TSARDOM_OF_RUSSIA_ID: (1547, 1720)}
    for candidate_id, contract in WAVE8_LIVONIAN_ORDER_CONTRACTS.items():
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
        if not (side_1 | side_2) <= allowed_entity_ids:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_new_entities.update((side_1 | side_2) & set(entity_by_id))
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in side_1 | side_2:
            if entity_id in entity_by_id:
                entity = entity_by_id[entity_id]
                start = int(entity["start_year"])
                end = int(entity["end_year"])
            else:
                start, end = existing_windows[entity_id]
            if not start <= low <= high <= end:
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        winner_side, override, reversal = expected_orientations[candidate_id]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or int(contract["winner_side"]) != winner_side
            or contract["source_outcome_override"] is not override
            or contract["outcome_reversal"] is not reversal
            or contract["actor_override"] != "bounded_exact_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor contract drifted")
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
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)
    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")

    for candidate_id, hold in WAVE8_LIVONIAN_ORDER_HOLDS.items():
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
        if "not promoted" not in reason or "draw" not in reason:
            raise ValueError(f"{_LANE_NAME} hold lost the no-draw policy")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES) != {
        "hced-Lake Smolino1502-1",
        "hced-Narva1558-1",
    }:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    for candidate_id, override in WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES.items():
        contract = WAVE8_LIVONIAN_ORDER_CONTRACTS[candidate_id]
        winner_side = int(override["corrected_winner_side"])
        loser_side = 3 - winner_side
        if (
            winner_side != int(contract["winner_side"])
            or override["corrected_winner_entity_ids"]
            != contract[f"side_{winner_side}_entity_ids"]
            or override["corrected_loser_entity_ids"]
            != contract[f"side_{loser_side}_entity_ids"]
            or override["outcome_source_ids"] != contract["outcome_source_ids"]
            or override["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")

    if set(WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS) != WAVE8_LIVONIAN_ORDER_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    if WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS != {
        "hced-Lake Smolino1502-1",
        "hced-Oomuli1560-1",
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if not WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS <= (
        WAVE8_LIVONIAN_ORDER_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine is not promoted-only")
    if WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    for review in WAVE8_LIVONIAN_ORDER_LOCATION_REVIEWS.values():
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_LIVONIAN_ORDER_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, item["aliases"]))
        if not _is_sorted_unique(aliases) or aliases != list(
            map(normalize_label, aliases)
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are nondeterministic")
        years = tuple(map(int, item["years"]))
        if len(years) != 2 or years[0] > years[1]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
    if (
        WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired a duplicate disposition")

    if set(WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS) != {
        "hced-Seritsa1501-1"
    }:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for disposition in WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS.values():
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_LIVONIAN_ORDER_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")


def _is_exact_livonian_order_label(value: Any) -> bool:
    return normalize_label(value) == "livonian order"


def validate_wave8_livonian_order_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the seven exact ``Livonian Order`` queue rows."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_LIVONIAN_ORDER_CONTRACTS,
        WAVE8_LIVONIAN_ORDER_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_livonian_order_label(row.get("side_1_raw"))
        or _is_exact_livonian_order_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Livonian Order inventory changed: {sorted(exact_ids)}"
        )
    by_id = {
        str(row.get("candidate_id")): row
        for row in hced_rows
        if str(row.get("candidate_id")) in WAVE8_LIVONIAN_ORDER_RESERVED_IDS
    }
    for candidate_id, row in by_id.items():
        exact_sides = sum(
            _is_exact_livonian_order_label(row.get(field))
            for field in ("side_1_raw", "side_2_raw")
        )
        if exact_sides != 1:
            raise ValueError(f"{_LANE_NAME} exact-side ownership changed: {candidate_id}")
    return {
        **counts,
        "terminal_exclusions": len(WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_livonian_order_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the authoritative seven-row funnel and its four sole blockers."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    label_rows = [item for item in labels if item.get("label") == "livonian order"]
    if len(label_rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = label_rows[0]
    expected_fields = {
        "event_candidate_id_sha256": WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT[
            "event_candidate_id_sha256"
        ],
        "events_touched": 7,
        "sole_blocker_events": 4,
    }
    for key, expected in expected_fields.items():
        if label.get(key) != expected:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = label.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get(
        "zero_time_valid_candidates"
    ) != 7:
        raise ValueError(f"{_LANE_NAME} funnel failure case changed")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} funnel greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == "livonian order"]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one greedy ranking row")
    if (
        ranked[0].get("events_touched") != 7
        or ranked[0].get("marginal_events") != 4
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != WAVE8_LIVONIAN_ORDER_FUNNEL_AUDIT[
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
        matching = (
            [
                failure
                for failure in label_failures
                if failure.get("label") == "livonian order"
            ]
            if isinstance(label_failures, list)
            else []
        )
        if matching:
            if len(matching) != 1 or matching[0].get("failure_case") != (
                "zero_time_valid_candidates"
            ):
                raise ValueError(f"{_LANE_NAME} funnel row failure changed")
            audited_rows.append(row)
    audited_ids = {str(row.get("candidate_id")) for row in audited_rows}
    sole_ids = {
        str(row.get("candidate_id"))
        for row in audited_rows
        if row.get("sole_blocker_label") == "livonian order"
    }
    if audited_ids != WAVE8_LIVONIAN_ORDER_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel exact cohort changed")
    if sole_ids != WAVE8_LIVONIAN_ORDER_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} funnel sole blockers changed")
    return {
        "exact_label_rows": len(audited_ids),
        "held_other_identity_rows": len(audited_ids - sole_ids),
        "sole_blocker_rows": len(sole_ids),
    }


def _year_from_date(value: Any) -> int | None:
    text = str(value or "")
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _row_interval(row: Mapping[str, Any]) -> tuple[int, int] | None:
    for field in ("year", "year_best"):
        value = row.get(field)
        try:
            if value is not None:
                year = int(value)
                return year, year
        except (TypeError, ValueError):
            pass
    start = _year_from_date(row.get("start_date"))
    end = _year_from_date(row.get("end_date"))
    if start is None and end is None:
        return None
    if start is None:
        start = end
    if end is None:
        end = start
    assert start is not None and end is not None
    return min(start, end), max(start, end)


def _normalized_duplicate_audit() -> dict[str, dict[str, Any]]:
    return {
        candidate_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for candidate_id, item in WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT.items()
    }


def _matches_duplicate_audit(
    names: Iterable[Any],
    interval: tuple[int, int] | None,
    audit: Mapping[str, Mapping[str, Any]],
) -> str | None:
    if interval is None:
        return None
    normalized_names = {normalize_label(name) for name in names}
    start, end = interval
    for candidate_id, item in audit.items():
        low, high = map(int, item["years"])
        if start <= high and end >= low and normalized_names & set(item["aliases"]):
            return candidate_id
    return None


def validate_wave8_livonian_order_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin related HCED rows and fail on future HCED/IWBD/release twins."""

    validate_wave8_livonian_order_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in (
        WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} related HCED fingerprint changed: {candidate_id}"
            )

    audit = _normalized_duplicate_audit()
    related_ids = set(WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS)
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in WAVE8_LIVONIAN_ORDER_RESERVED_IDS or candidate_id in related_ids:
            continue
        matched = _matches_duplicate_audit(
            [row.get("name")],
            _row_interval(row),
            audit,
        )
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed cross-lane HCED twin "
                f"{candidate_id or '<missing-id>'} for {matched}"
            )

    for row in iwbd_rows:
        matched = _matches_duplicate_audit(
            [row.get("name")],
            _row_interval(row),
            audit,
        )
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed probable IWBD duplicate "
                f"{row.get('candidate_id') or '<missing-id>'} for {matched}"
            )

    existing = list(existing_events)
    owned_collisions = sorted(
        {
            str(event.get("hced_candidate_id"))
            for event in existing
            if event.get("hced_candidate_id") in WAVE8_LIVONIAN_ORDER_RESERVED_IDS
        }
    )
    if owned_collisions:
        raise ValueError(
            f"{_LANE_NAME} candidate ownership collision in release: "
            f"{owned_collisions}"
        )
    for event in existing:
        raw_aliases = event.get("aliases", [])
        aliases = [raw_aliases] if isinstance(raw_aliases, str) else list(raw_aliases)
        matched = _matches_duplicate_audit(
            [event.get("name"), *aliases],
            _row_interval(event),
            audit,
        )
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed existing-release twin "
                f"{event.get('id') or '<missing-id>'} for {matched}"
            )

    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
    }


def install_wave8_livonian_order_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_LIVONIAN_ORDER_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_livonian_order_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_LIVONIAN_ORDER_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_livonian_order_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_livonian_order_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_LIVONIAN_ORDER_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_livonian_order_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_LIVONIAN_ORDER_CONTRACTS.values()
            ).items()
        )
    )


def wave8_livonian_order_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_LIVONIAN_ORDER_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_LIVONIAN_ORDER_HOLDS),
        "integration_dispositions": len(
            WAVE8_LIVONIAN_ORDER_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LIVONIAN_ORDER_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_LIVONIAN_ORDER_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_LIVONIAN_ORDER_ENTITIES),
        "new_sources": len(WAVE8_LIVONIAN_ORDER_SOURCES),
        "newly_rated_events": len(WAVE8_LIVONIAN_ORDER_CONTRACTS),
        "outcome_overrides": len(WAVE8_LIVONIAN_ORDER_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_LIVONIAN_ORDER_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_LIVONIAN_ORDER_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_LIVONIAN_ORDER_RESERVED_IDS),
        "sole_blocker_rows": len(_SOLE_BLOCKER_IDS),
        "terminal_exclusions": len(WAVE8_LIVONIAN_ORDER_TERMINAL_EXCLUSIONS),
    }


def wave8_livonian_order_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return local promoted-only quarantine additions for later integration."""

    _validate_static()
    return {
        "country": WAVE8_LIVONIAN_ORDER_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_LIVONIAN_ORDER_POINT_QUARANTINE_ADDITIONS,
    }
