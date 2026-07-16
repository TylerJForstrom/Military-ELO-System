"""Exact Wave 8 disposition for HCED's generic ``Cossack Rebels`` rows.

The source label collapses three unrelated forces across 136 years.  This lane
keeps them separate: the Pugachev uprising, Krychevsky's Loyew army, and the
Ostryanyn-Hunia force at Zhovnyne.  No generic Cossack alias is introduced.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 Cossack rebellions"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    family: str,
    *,
    outcome: bool = True,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": roles,
    }


WAVE8_COSSACK_REBELLIONS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_great_russian_encyclopedia_pugachev",
        "Pugachev Uprising, 1773-1775",
        "https://old.bigenc.ru/domestic_history/text/3172674",
        "Great Russian Encyclopedia",
        "scholarly_encyclopedia",
        "great_russian_encyclopedia_pugachev",
    ),
    _source(
        "wave8_harvard_imperiia_pugachev_bashkir",
        "Pugachev's Rebellion in the Bashkir Lands: 1773-1775",
        (
            "https://scalar.fas.harvard.edu/imperiia/"
            "pugachevs-rebellion-in-the-bashkir-lands-1773-1775"
        ),
        "Imperiia Project, Harvard University",
        "academic_public_history",
        "harvard_imperiia_pugachev",
    ),
    _source(
        "wave8_ssau_campaign_kazan_pugachev",
        "Campaign against Kazan: the fatal misadventure of Pugachev's Rebellion",
        "https://journals.ssau.ru/hpp/article/view/29591",
        "Vestnik of Samara University",
        "peer_reviewed_journal",
        "samara_university_pugachev_kazan",
    ),
    _source(
        "wave8_nas_ukraine_loyew_1649",
        "Battle of Loyew in 1649",
        "https://nasplib.isofts.kiev.ua/items/710a7079-2da7-409a-a3ac-e9ab2d422ed4",
        (
            "M. S. Hrushevsky Institute of Ukrainian Archaeography and Source "
            "Studies, National Academy of Sciences of Ukraine"
        ),
        "peer_reviewed_history",
        "nas_ukraine_loyew_study",
    ),
    _source(
        "wave8_encyclopedia_history_ukraine_zhovnyne",
        "Battle of Zhovnyne, 1638",
        (
            "https://resource.history.org.ua/cgi-bin/eiu/history.exe?"
            "C21COM=S&I21DBN=DOP&P21DBN=EIU&S21CNR=20&S21COLORTERMS=0&"
            "S21FMT=eiu_all&S21P01=0&S21P02=0&S21P03=TRN%3D&S21REF=10&"
            "S21STN=1&S21STR=Zhovnynska_bytva_1638&Z21ID="
        ),
        "Encyclopedia of the History of Ukraine, NAS of Ukraine",
        "scholarly_encyclopedia",
        "encyclopedia_history_ukraine",
    ),
    _source(
        "wave8_encyclopedia_ukraine_ostryanyn",
        "Ostrianyn, Yakiv",
        (
            "https://www.encyclopediaofukraine.com/display.asp?"
            "linkpath=pages%5CO%5CS%5COstrianynYakiv.htm"
        ),
        "Internet Encyclopedia of Ukraine, Canadian Institute of Ukrainian Studies",
        "scholarly_encyclopedia",
        "encyclopedia_of_ukraine",
    ),
)


WAVE8_COSSACK_REBELLIONS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "pugachev_rebellion_forces_1773_1775",
        "name": "Pugachev Rebellion forces",
        "kind": "insurgent_coalition",
        "start_year": 1773,
        "end_year": 1775,
        "region": "Volga-Ural region",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded umbrella for Pugachev's main rebel army and the "
            "named mobile formations operating under the uprising's command. "
            "It does not transfer a rating to Yaik Cossacks, Bashkirs, peasants, "
            "later Cossack hosts, or any ethnic population."
        ),
        "source_ids": [
            "wave8_great_russian_encyclopedia_pugachev",
            "wave8_harvard_imperiia_pugachev_bashkir",
        ],
    },
    {
        "id": "krychevsky_zaporozhian_army_loyew_1649",
        "name": "Krychevsky's Zaporozhian army at Loyew",
        "kind": "campaign_army",
        "start_year": 1649,
        "end_year": 1649,
        "region": "Polish-Lithuanian Commonwealth",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded force under Mykhailo Krychevsky in the 1649 Loyew "
            "campaign. No rating is inherited by the Zaporozhian Host generally, "
            "modern Ukraine, or unrelated Cossack rebellions."
        ),
        "source_ids": ["wave8_nas_ukraine_loyew_1649"],
    },
    {
        "id": "ostryanyn_hunia_rebel_force_1638",
        "name": "Ostryanyn-Hunia rebel force at Zhovnyne",
        "kind": "insurgent_army",
        "start_year": 1638,
        "end_year": 1638,
        "region": "Kyiv Voivodeship",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded force led successively by Yakiv Ostryanyn and "
            "Dmytro Hunia in the 1638 uprising. No generic Cossack, Ukrainian, "
            "or later insurgent continuity is inferred."
        ),
        "source_ids": [
            "wave8_encyclopedia_history_ukraine_zhovnyne",
            "wave8_encyclopedia_ukraine_ostryanyn",
        ],
    },
)


def _canonical(name: str, low: int, high: int | None = None) -> dict[str, Any]:
    high = low if high is None else high
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": low,
        "year_high": high,
    }


_PUGACHEV_EVIDENCE = [
    "wave8_great_russian_encyclopedia_pugachev",
    "wave8_harvard_imperiia_pugachev_bashkir",
]


WAVE8_COSSACK_REBELLIONS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Kazan1774-1": {
        "raw_row_sha256": "4e8fd3a094fae60810a8bf4402a80c25ccb43f7d79f40cce262c888d38a764ef",
        "canonical_event": _canonical("Battle of Kazan", 1774),
        "cohort": "pugachev_rebellion",
        "side_1_entity_ids": ["russian_empire"],
        "side_2_entity_ids": ["pugachev_rebellion_forces_1773_1775"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": [*_PUGACHEV_EVIDENCE, "wave8_ssau_campaign_kazan_pugachev"],
        "outcome_source_ids": [
            "wave8_great_russian_encyclopedia_pugachev",
            "wave8_ssau_campaign_kazan_pugachev",
        ],
        "outcome_source_family_ids": [
            "great_russian_encyclopedia_pugachev",
            "samara_university_pugachev_kazan",
        ],
        "audit_note": (
            "Pugachev's army occupied most of Kazan on 12/23 July but was "
            "defeated by Mikhelson that evening and again on 15/26 July. The "
            "contract rates the completed battle, not the uprising as a whole."
        ),
    },
    "hced-Orenburg1773-1774-1": {
        "raw_row_sha256": "5c91acbac41ddb87911449124a6b5dc1b84dce42e9eeacccec4ae877fee6a06b",
        "canonical_event": _canonical("Siege of Orenburg", 1773, 1774),
        "cohort": "pugachev_rebellion",
        "side_1_entity_ids": ["russian_empire"],
        "side_2_entity_ids": ["pugachev_rebellion_forces_1773_1775"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": _PUGACHEV_EVIDENCE,
        "outcome_source_ids": ["wave8_great_russian_encyclopedia_pugachev"],
        "outcome_source_family_ids": ["great_russian_encyclopedia_pugachev"],
        "audit_note": (
            "The rebel main army besieged Orenburg from October 1773. The siege "
            "was lifted immediately after the rebel defeat at Tatishcheva in "
            "March/April 1774; the siege and relief battle remain distinct rows."
        ),
    },
    "hced-Tatishchevo1774-1": {
        "raw_row_sha256": "191f50038c84fe1f4bef1ca24fdfe827df7bd5f1aa6a2eacc4b49f436930814c",
        "canonical_event": _canonical("Battle of Tatishcheva Fortress", 1774),
        "cohort": "pugachev_rebellion",
        "side_1_entity_ids": ["russian_empire"],
        "side_2_entity_ids": ["pugachev_rebellion_forces_1773_1775"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": _PUGACHEV_EVIDENCE,
        "outcome_source_ids": ["wave8_great_russian_encyclopedia_pugachev"],
        "outcome_source_family_ids": ["great_russian_encyclopedia_pugachev"],
        "audit_note": (
            "Bibikov's imperial relief force defeated the rebels by Tatishcheva "
            "Fortress on 22 March/2 April 1774. HCED's coordinate identifies a "
            "different Tatishchevo and is withheld."
        ),
    },
    "hced-Ufa1773-1774-1": {
        "raw_row_sha256": "3dbeeb6c15932b8a2bdf1384b709bb6f36c1d695c85fe545a2f38c515a7475ca",
        "canonical_event": _canonical("Siege and relief of Ufa", 1773, 1774),
        "cohort": "pugachev_rebellion",
        "side_1_entity_ids": ["russian_empire"],
        "side_2_entity_ids": ["pugachev_rebellion_forces_1773_1775"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": _PUGACHEV_EVIDENCE,
        "outcome_source_ids": [
            "wave8_great_russian_encyclopedia_pugachev",
            "wave8_harvard_imperiia_pugachev_bashkir",
        ],
        "outcome_source_family_ids": [
            "great_russian_encyclopedia_pugachev",
            "harvard_imperiia_pugachev",
        ],
        "audit_note": (
            "Rebel formations blockaded Ufa through the winter; Mikhelson's force "
            "defeated them near Ufa on 24 March/4 April 1774 and relieved the city."
        ),
    },
    "hced-Loyew1649-1": {
        "raw_row_sha256": "d12103c1c7940328fe32c94ca2647e598e1d0208741315cceb988e629aa17e63",
        "canonical_event": _canonical("Battle of Loyew", 1649),
        "cohort": "khmelnytsky_uprising",
        "side_1_entity_ids": ["polish_lithuanian_commonwealth"],
        "side_2_entity_ids": ["krychevsky_zaporozhian_army_loyew_1649"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": ["wave8_nas_ukraine_loyew_1649"],
        "outcome_source_ids": ["wave8_nas_ukraine_loyew_1649"],
        "outcome_source_family_ids": ["nas_ukraine_loyew_study"],
        "audit_note": (
            "The 31 July/10 August 1649 battle ended with Krychevsky's army "
            "defeated by Janusz Radziwill's Commonwealth force. The exact field "
            "army is rated, not a timeless Cossack population."
        ),
    },
    "hced-Zhovnyne1638-1": {
        "raw_row_sha256": "2bd36376b2b7910d473ab710528bcf0f98cebb6604f1fb4beedef5f212f6bf55",
        "canonical_event": _canonical("Battle of Zhovnyne", 1638),
        "cohort": "ostryanyn_uprising",
        "side_1_entity_ids": ["polish_lithuanian_commonwealth"],
        "side_2_entity_ids": ["ostryanyn_hunia_rebel_force_1638"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": [
            "wave8_encyclopedia_history_ukraine_zhovnyne",
            "wave8_encyclopedia_ukraine_ostryanyn",
        ],
        "outcome_source_ids": ["wave8_encyclopedia_history_ukraine_zhovnyne"],
        "outcome_source_family_ids": ["encyclopedia_history_ukraine"],
        "audit_note": (
            "The Commonwealth assault broke into the fortified camp, after which "
            "Ostryanyn fled and Hunia's remaining force withdrew to the Starzec "
            "position. This rates the Zhovnyne engagement only, not the later siege."
        ),
    },
}


WAVE8_COSSACK_REBELLIONS_HOLDS: dict[str, dict[str, Any]] = {}

# HCED points for Tatishchevo and Zhovnyne identify nearby or same-named places,
# not the reviewed battle locations.  Values are withheld, never corrected.
WAVE8_COSSACK_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Tatishchevo1774-1", "hced-Zhovnyne1638-1"}
)
WAVE8_COSSACK_COUNTRY_QUARANTINE_ADDITIONS = frozenset()

WAVE8_COSSACK_RESERVED_IDS = frozenset(WAVE8_COSSACK_REBELLIONS_CONTRACTS)
WAVE8_COSSACK_CONTRACT_IDS = frozenset(WAVE8_COSSACK_REBELLIONS_CONTRACTS)
WAVE8_COSSACK_HOLD_IDS = frozenset(WAVE8_COSSACK_REBELLIONS_HOLDS)


def wave8_cossack_audit_signature() -> str:
    payload = {
        "contracts": WAVE8_COSSACK_REBELLIONS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_COSSACK_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_COSSACK_REBELLIONS_ENTITIES,
        "holds": WAVE8_COSSACK_REBELLIONS_HOLDS,
        "point_quarantine_additions": sorted(WAVE8_COSSACK_POINT_QUARANTINE_ADDITIONS),
        "sources": WAVE8_COSSACK_REBELLIONS_SOURCES,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


WAVE8_COSSACK_FINAL_AUDIT_SIGNATURE = (
    "f6e96c7f18df3cee6aa29034caef3634d0bb47e6860d6088175ee2d6d83a848d"
)


def validate_wave8_cossack_inventory(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_COSSACK_REBELLIONS_CONTRACTS,
        WAVE8_COSSACK_REBELLIONS_HOLDS,
        lane_name=_LANE_NAME,
    )


def wave8_cossack_counts() -> dict[str, int]:
    return {
        "promotion_contracts": len(WAVE8_COSSACK_REBELLIONS_CONTRACTS),
        "holds": len(WAVE8_COSSACK_REBELLIONS_HOLDS),
        "reviewed_hced_rows": len(WAVE8_COSSACK_RESERVED_IDS),
        "entities": len(WAVE8_COSSACK_REBELLIONS_ENTITIES),
        "sources": len(WAVE8_COSSACK_REBELLIONS_SOURCES),
    }


def wave8_cossack_cohort_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for contract in WAVE8_COSSACK_REBELLIONS_CONTRACTS.values():
        cohort = str(contract["cohort"])
        counts[cohort] = counts.get(cohort, 0) + 1
    return dict(sorted(counts.items()))


def install_wave8_cossack_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    install_exact_entities(
        release_entities, WAVE8_COSSACK_REBELLIONS_ENTITIES, lane_name=_LANE_NAME
    )


def install_wave8_cossack_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    install_exact_sources(
        sources_by_id, WAVE8_COSSACK_REBELLIONS_SOURCES, lane_name=_LANE_NAME
    )


def promote_wave8_cossack_events(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_COSSACK_REBELLIONS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_cossack_",
    )
