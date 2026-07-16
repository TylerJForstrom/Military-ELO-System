"""Candidate-keyed Wave 8 contracts for the New Zealand Wars."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


WAVE8_NEW_ZEALAND_FINAL_AUDIT_SIGNATURE = (
    "772cf55241319f5b6ab6413ebd13b258aa875b21c7c579901beaa197cf06def8"
)

WAVE8_NEW_ZEALAND_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "nzhistory_kororareka_1845",
        "title": "The fall of Kororāreka",
        "url": "https://nzhistory.govt.nz/the-flagstaff-is-cut-down-for-the-fourth-and-last-time-and-kororareka-is-invaded",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["outcome", "identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_boulcott_1846",
        "title": "Eight killed in attack on Boulcott Farm",
        "url": "https://nzhistory.govt.nz/page/eight-killed-attack-boulcott-farm",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["outcome", "identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_waikato_opening_1863",
        "title": "War in Waikato: the opening phase",
        "url": "https://nzhistory.govt.nz/war/war-in-waikato/opening-phase",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_taranaki_second_war",
        "title": "The second Taranaki war",
        "url": "https://nzhistory.govt.nz/war/taranaki-wars/second-taranaki-war",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_moutoa_1864",
        "title": "Moutoa Gardens NZ Wars memorial",
        "url": "https://nzhistory.govt.nz/memorial/moutoa-gardens-nz-wars-memorial",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_titokowaru_1868",
        "title": "Tītokowaru's war: Turuturumōkai to Moturoa",
        "url": "https://nzhistory.govt.nz/page/turuturumokai-moturoa",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_te_kooti_war",
        "title": "Te Kooti's war",
        "url": "https://nzhistory.govt.nz/war/te-kootis-war",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzhistory_te_porere_1869",
        "title": "Te Pōrere and retreat",
        "url": "https://nzhistory.govt.nz/war/te-kootis-war/te-porere-and-retreat",
        "publisher": "Manatū Taonga — Ministry for Culture and Heritage",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "nzhistory",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nzpolice_te_kooti_campaign",
        "title": "New Zealand Police history: 1860s",
        "url": "https://www.police.govt.nz/about-us/history-museum/museum/exhibitions/he-matapihi-o-nehe-ra/1860s",
        "publisher": "New Zealand Police",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "new_zealand_police_history",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "teara_te_arawa_wars",
        "title": "Te Arawa: wars and resistance",
        "url": "https://teara.govt.nz/en/te-arawa/print",
        "publisher": "Te Ara — The Encyclopedia of New Zealand",
        "license": "linked_reference",
        "source_type": "national_encyclopedia",
        "accessed": "2026-07-16",
        "source_family_id": "te_ara",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start: int,
    end: int,
    sources: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start,
        "end_year": end,
        "region": "Aotearoa New Zealand",
        "aliases": [],
        "predecessors": [],
        "continuity_note": note + " No rating is inherited by broader Māori, iwi, Crown, or successor identities.",
        "source_ids": sources,
    }


WAVE8_NEW_ZEALAND_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity("heke_kawiti_ngapuhi_coalition_1845", "Heke–Kawiti Ngāpuhi coalition", "indigenous_coalition", 1845, 1846, ["nzhistory_kororareka_1845"], "Exact Northern War coalition under Hōne Heke and Te Ruki Kawiti."),
    _entity("te_mamaku_ngati_haua_force_1846", "Te Mamaku's Ngāti Hāua-te-rangi force", "war_party", 1846, 1846, ["nzhistory_boulcott_1846"], "Exact Boulcott's Farm attacking force led by Te Mamaku."),
    _entity("kingitanga_waikato_forces_1863", "Kīngitanga forces in the Waikato War", "indigenous_coalition", 1863, 1864, ["nzhistory_waikato_opening_1863"], "Conflict-bounded Māori King movement forces resisting the Waikato invasion."),
    _entity("taranaki_resistance_forces_1863", "Taranaki resistance forces (1863–1864)", "indigenous_coalition", 1863, 1864, ["nzhistory_taranaki_second_war"], "Conflict-bounded Te Ātiawa, Taranaki, Ngāti Ruanui, Ngāti Rauru, and Whanganui resistance."),
    _entity("pai_marire_forces_1864", "Pai Mārire forces (1864–1865)", "religious_movement_force", 1864, 1865, ["nzhistory_taranaki_second_war", "nzhistory_moutoa_1864"], "Conflict-bounded Pai Mārire combatants; later Tītokowaru and Te Kooti forces remain separate."),
    _entity("putiki_kupapa_1864", "Pūtiki kūpapa at Moutoa", "indigenous_allied_force", 1864, 1864, ["nzhistory_moutoa_1864"], "Exact lower-Whanganui government-aligned force at Moutoa."),
    _entity("titokowaru_ngati_ruanui_forces_1868", "Tītokowaru's Ngāti Ruanui-led forces", "indigenous_resistance_force", 1868, 1869, ["nzhistory_titokowaru_1868"], "Conflict-bounded South Taranaki command under Riwha Tītokowaru."),
    _entity("te_kooti_whakarau_1868", "Te Kooti's whakarau", "guerrilla_force", 1868, 1872, ["nzhistory_te_kooti_war"], "Conflict-bounded followers and allied fighting force commanded by Te Kooti."),
    _entity("new_zealand_colonial_forces_1867", "New Zealand colonial forces (1867–1872)", "colonial_state_force", 1867, 1872, ["nzhistory_titokowaru_1868", "nzhistory_te_kooti_war", "nzpolice_te_kooti_campaign"], "Armed Constabulary and colonial formations after imperial troop withdrawal."),
    _entity("ngati_porou_government_contingent_1868", "Ngāti Porou government contingent (1868)", "indigenous_allied_force", 1868, 1869, ["nzhistory_te_kooti_war", "nzpolice_te_kooti_campaign"], "Conflict-bounded Ngāti Porou force operating against Te Kooti."),
    _entity("whanganui_kupapa_1869", "Whanganui kūpapa under Te Keepa", "indigenous_allied_force", 1869, 1870, ["nzhistory_te_porere_1869"], "Conflict-bounded Whanganui contingent serving under Te Keepa Te Rangihiwinui."),
    _entity("te_arawa_flying_column_1870", "Te Arawa Flying Column", "indigenous_allied_force", 1870, 1872, ["teara_te_arawa_wars"], "Conflict-bounded Te Arawa force pursuing Te Kooti."),
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {"canonical_key": f"{_slug(name)}:{year}:{year}", "date_precision": "year", "granularity": "engagement", "name": name, "year_low": year, "year_high": year}


_ROW_DATA = {
    "hced-Boulcotts Farm1846-1": ("1130f2a8d283a6ce5e1ff7e0e991a26d2c48354f5f022cca8926e009ea0686ab", "Boulcott's Farm", 1846),
    "hced-Kaitake1864-1": ("e7d16e037a3a20c57369ade348ddc75c76101ba25f922f9f715f7e467364148d", "Kaitake", 1864),
    "hced-Koheroa1863-1": ("a270591b01abdc9297ab1cb82b964f9b8cd6ac0970d45bd73ca72bb714afa6b5", "Koheroa", 1863),
    "hced-Kororareka1845-1": ("accbfdd57591efcfb072a9d821db28d937d9b329c396207d36fd714d5b870d4c", "Fall of Kororāreka", 1845),
    "hced-Makaretu1868-1": ("0e021e171a7b0d9597220871b5d2cfb77c0a70c89d8a8127403a946e99e8464e", "Makaretu", 1868),
    "hced-Mangapiko1864-1": ("6001af8fd616fcb863a86c24c36dd191e8899faef1bf9884aa05d332d821a288", "Mangapiko", 1864),
    "hced-Matawhero1868-1": ("3310a36427abd5f550383fffd6881367556d99348afd927ee711280b294d5b3b", "Matawhero", 1868),
    "hced-Mauku1863-1": ("d8905712216276f22970bfd17508faba20cd852292ee0715affa11b0055575f8", "Mauku", 1863),
    "hced-Moturoa1868-1": ("babf1052b3d5c552844bf827f91886d3226004aa5b69caaa95d02c366c623fe0", "Moturoa", 1868),
    "hced-Moutoa1864-1": ("93110e02e53c4609b4f34e0852f1ab270a05ace3a63b12a0e411598a16eac930", "Moutoa", 1864),
    "hced-Nukumaru1865-1": ("ae8dfdfc4f05640e5944909f4f8bcb2e82e2bf09f8d03d4b2acfb8e7b59f73fa", "Nukumaru", 1865),
    "hced-Poutoko1863-1": ("b4d8eccd7578f527af7d6a7c7309c4d91293089fa326fd098168fed804ea6d27", "Poutoko", 1863),
    "hced-Te Ahuahu, Taranaki1864-1": ("c452555c7c9e5c1f2dd3f9b70336455ebe3b0028803beaffd57123a24eb561bf", "Te Ahuahu, Taranaki", 1864),
    "hced-Te Ngutu-o-te-manu1868-1": ("552962e5579d6459f33060d10aae17bf2e100598c59122e2f1bc696989f2732d", "Te Ngutu-o-te-manu", 1868),
    "hced-Te Porere1869-1": ("f8414a800d5644f1e4d3a1ffd1165aa6c7cc3607af2d381800302c7bacf602c0", "Te Pōrere", 1869),
    "hced-Waikorowhiti1870-1": ("08ba2c48b85a2fa75331a1bb5d2660fbe25ae43b53cc8d4bc43bcdabca48ac8f", "Waikorowhiti", 1870),
}


def _contract(candidate_id: str, cohort: str, side_1: list[str], side_2: list[str], winner: int, evidence: list[str], note: str, *, override: bool = False) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    result = {"raw_row_sha256": row_hash, "canonical_event": _canonical(name, year), "cohort": cohort, "side_1_entity_ids": side_1, "side_2_entity_ids": side_2, "winner_side": winner, "evidence_refs": evidence, "audit_note": note, "source_outcome_override": override}
    if override:
        result["outcome_source_ids"] = evidence
        result["outcome_source_family_ids"] = ["nzhistory"]
    return result


WAVE8_NEW_ZEALAND_CONTRACTS = {
    "hced-Kororareka1845-1": _contract("hced-Kororareka1845-1", "northern_war", ["heke_kawiti_ngapuhi_coalition_1845"], ["united_kingdom"], 1, ["nzhistory_kororareka_1845"], "The official account replaces HCED's non-outcome 'Massacre' marker with the documented Heke–Kawiti tactical victory.", override=True),
    "hced-Boulcotts Farm1846-1": _contract("hced-Boulcotts Farm1846-1", "wellington_war", ["united_kingdom"], ["te_mamaku_ngati_haua_force_1846"], 2, ["nzhistory_boulcott_1846"], "The official account contradicts HCED's UK orientation and documents Te Mamaku's successful attack; the outcome is corrected directly.", override=True),
    "hced-Koheroa1863-1": _contract("hced-Koheroa1863-1", "kingitanga_waikato", ["united_kingdom"], ["kingitanga_waikato_forces_1863"], 1, ["nzhistory_waikato_opening_1863"], "Exact Kīngitanga Waikato-war binding."),
    "hced-Mauku1863-1": _contract("hced-Mauku1863-1", "kingitanga_waikato", ["united_kingdom"], ["kingitanga_waikato_forces_1863"], 1, ["nzhistory_waikato_opening_1863"], "Exact Kīngitanga Waikato-war binding."),
    "hced-Mangapiko1864-1": _contract("hced-Mangapiko1864-1", "kingitanga_waikato", ["united_kingdom"], ["kingitanga_waikato_forces_1863"], 1, ["nzhistory_waikato_opening_1863"], "Exact Kīngitanga Waikato-war binding."),
    "hced-Poutoko1863-1": _contract("hced-Poutoko1863-1", "taranaki_resistance", ["united_kingdom"], ["taranaki_resistance_forces_1863"], 1, ["nzhistory_taranaki_second_war"], "Exact Second Taranaki War resistance binding."),
    "hced-Kaitake1864-1": _contract("hced-Kaitake1864-1", "taranaki_resistance", ["united_kingdom"], ["taranaki_resistance_forces_1863"], 1, ["nzhistory_taranaki_second_war"], "Exact Second Taranaki War resistance binding."),
    "hced-Moutoa1864-1": _contract("hced-Moutoa1864-1", "pai_marire", ["putiki_kupapa_1864"], ["pai_marire_forces_1864"], 1, ["nzhistory_moutoa_1864"], "Both Māori sides are reconstructed from the official Moutoa account."),
    "hced-Te Ahuahu, Taranaki1864-1": _contract("hced-Te Ahuahu, Taranaki1864-1", "pai_marire", ["pai_marire_forces_1864"], ["united_kingdom"], 1, ["nzhistory_taranaki_second_war"], "Exact Pai Mārire attack binding."),
    "hced-Nukumaru1865-1": _contract("hced-Nukumaru1865-1", "pai_marire", ["united_kingdom"], ["pai_marire_forces_1864"], 1, ["nzhistory_taranaki_second_war"], "Conflict-bounded Pai Mārire binding."),
    "hced-Moturoa1868-1": _contract("hced-Moturoa1868-1", "titokowaru", ["titokowaru_ngati_ruanui_forces_1868"], ["new_zealand_colonial_forces_1867"], 1, ["nzhistory_titokowaru_1868"], "HCED's generic Hauhau/UK labels are corrected to Tītokowaru and the colonial force."),
    "hced-Te Ngutu-o-te-manu1868-1": _contract("hced-Te Ngutu-o-te-manu1868-1", "titokowaru", ["titokowaru_ngati_ruanui_forces_1868"], ["new_zealand_colonial_forces_1867"], 1, ["nzhistory_titokowaru_1868"], "HCED's generic Hauhau/UK labels are corrected to Tītokowaru and the colonial force."),
    "hced-Makaretu1868-1": _contract("hced-Makaretu1868-1", "te_kooti", ["new_zealand_colonial_forces_1867", "ngati_porou_government_contingent_1868"], ["te_kooti_whakarau_1868"], 1, ["nzhistory_te_kooti_war", "nzpolice_te_kooti_campaign"], "The generic labels are replaced by the documented colonial–Ngāti Porou coalition and Te Kooti's whakarau."),
    "hced-Te Porere1869-1": _contract("hced-Te Porere1869-1", "te_kooti", ["new_zealand_colonial_forces_1867", "whanganui_kupapa_1869"], ["te_kooti_whakarau_1868"], 1, ["nzhistory_te_porere_1869"], "The official account supplies the colonial–Whanganui coalition and Te Kooti identity."),
    "hced-Waikorowhiti1870-1": _contract("hced-Waikorowhiti1870-1", "te_kooti", ["new_zealand_colonial_forces_1867", "te_arawa_flying_column_1870"], ["te_kooti_whakarau_1868"], 1, ["nzhistory_te_kooti_war", "teara_te_arawa_wars"], "The generic labels are replaced by the colonial–Te Arawa column and Te Kooti's force."),
}

_mata_hash, _mata_name, _mata_year = _ROW_DATA["hced-Matawhero1868-1"]
WAVE8_NEW_ZEALAND_HOLDS = {
    "hced-Matawhero1868-1": {
        "raw_row_sha256": _mata_hash,
        "canonical_event": _canonical(_mata_name, _mata_year),
        "hold_category": "massacre_without_competitive_outcome",
        "hold_reason": "The row records targeted killings and supplies no competitive battlefield outcome; it must never be converted into a win or draw.",
        "evidence_refs": ["nzhistory_te_kooti_war"],
    }
}

WAVE8_NEW_ZEALAND_CONTRACT_IDS = frozenset(WAVE8_NEW_ZEALAND_CONTRACTS)
WAVE8_NEW_ZEALAND_HOLD_IDS = frozenset(WAVE8_NEW_ZEALAND_HOLDS)
WAVE8_NEW_ZEALAND_RESERVED_IDS = WAVE8_NEW_ZEALAND_CONTRACT_IDS | WAVE8_NEW_ZEALAND_HOLD_IDS


def _audit_signature() -> str:
    lines = []
    for disposition, inventory in (("promote", WAVE8_NEW_ZEALAND_CONTRACTS), ("hold", WAVE8_NEW_ZEALAND_HOLDS)):
        for candidate_id, contract in sorted(inventory.items()):
            lines.append(f"{disposition}|{candidate_id}|{contract['raw_row_sha256']}|{contract['canonical_event']['canonical_key']}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def _validate_static() -> None:
    if len(WAVE8_NEW_ZEALAND_CONTRACTS) != 15 or len(WAVE8_NEW_ZEALAND_HOLDS) != 1:
        raise ValueError("Wave 8 New Zealand disposition inventory changed")
    if len(WAVE8_NEW_ZEALAND_ENTITIES) != 12 or len(WAVE8_NEW_ZEALAND_SOURCES) != 10:
        raise ValueError("Wave 8 New Zealand identity/source inventory changed")
    if _audit_signature() != WAVE8_NEW_ZEALAND_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 New Zealand final audit signature changed")
    source_ids = {source["id"] for source in WAVE8_NEW_ZEALAND_SOURCES}
    for entity in WAVE8_NEW_ZEALAND_ENTITIES:
        if entity["aliases"] or entity["predecessors"] or "No rating" not in entity["continuity_note"]:
            raise ValueError(f"Wave 8 New Zealand identity invariant failed: {entity['id']}")
        if not set(entity["source_ids"]) <= source_ids:
            raise ValueError(f"Wave 8 New Zealand unknown entity source: {entity['id']}")
    for contract in [*WAVE8_NEW_ZEALAND_CONTRACTS.values(), *WAVE8_NEW_ZEALAND_HOLDS.values()]:
        if not set(contract["evidence_refs"]) <= source_ids:
            raise ValueError("Wave 8 New Zealand contract has an unknown source")


def validate_wave8_new_zealand_queue_contracts(hced_rows: list[dict[str, Any]]) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(hced_rows, WAVE8_NEW_ZEALAND_CONTRACTS, WAVE8_NEW_ZEALAND_HOLDS, lane_name="Wave 8 New Zealand")


def install_wave8_new_zealand_entities(release_entities: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_entities(release_entities, WAVE8_NEW_ZEALAND_ENTITIES, lane_name="Wave 8 New Zealand")


def install_wave8_new_zealand_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_sources(sources_by_id, WAVE8_NEW_ZEALAND_SOURCES, lane_name="Wave 8 New Zealand")


def promote_wave8_new_zealand_contracts(hced_rows: list[dict[str, Any]], release_entities: Mapping[str, Mapping[str, Any]], existing_events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    validate_wave8_new_zealand_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(hced_rows, release_entities, existing_events, WAVE8_NEW_ZEALAND_CONTRACTS, lane_name="Wave 8 New Zealand", event_id_prefix="hced_wave8_new_zealand_")


def wave8_new_zealand_cohort_counts() -> dict[str, int]:
    return dict(sorted(Counter(contract["cohort"] for contract in WAVE8_NEW_ZEALAND_CONTRACTS.values()).items()))
