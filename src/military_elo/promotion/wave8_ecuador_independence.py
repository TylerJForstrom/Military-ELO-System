"""Exact Wave 8 contracts for the Quito/Guayaquil independence campaign.

HCED calls every patriot side ``Ecuadorian Rebels`` even though Ecuador did
not yet exist as the later republic.  This lane distinguishes Guayaquil's
state force, Sucre's multinational campaign army, and Gran Colombia in 1823.
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


_LANE_NAME = "Wave 8 Ecuador independence"


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
        "evidence_roles": sorted(roles),
    }


WAVE8_ECUADOR_INDEPENDENCE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_ecuador_anh_independence_campaign",
        "The Quito independence campaign and the Battle of Pichincha",
        "https://academiahistoria.org.ec/index.php/boletinesANHE/article/download/293/560/1087",
        "Academia Nacional de Historia del Ecuador",
        "scholarly_history",
        "ecuador_academia_nacional_historia",
    ),
    _source(
        "wave8_ecuador_anh_guayaquil_flags",
        "The flags of Guayaquil in the independence process, 1820-1822",
        "https://www.academiahistoria.org.ec/index.php/boletinesANHE/article/download/313/598",
        "Academia Nacional de Historia del Ecuador",
        "scholarly_history",
        "ecuador_academia_nacional_historia",
        outcome=False,
    ),
    _source(
        "wave8_ecuador_army_independence_arms_history",
        "Ecuadorian Army arms history: independence campaigns",
        (
            "https://mail.ejercitoecuatoriano.mil.ec/contact-us/categoria/"
            "139-sistema-de-armas/images/IMAGENES/RENDICION_2025/13BI/"
            "procesos_de_contratacin_2024.pdf"
        ),
        "Ecuadorian Army",
        "official_military_history",
        "ecuadorian_army_history",
    ),
    _source(
        "wave8_ecuador_army_pichincha_composition",
        "Infantry history and the Battle of Pichincha",
        "https://ejercitoecuatoriano.mil.ec/index.php/pages/ejercito/ccasefe/infanteria",
        "Ecuadorian Army",
        "official_military_history",
        "ecuadorian_army_history",
    ),
    _source(
        "wave8_ecuador_anh_ibarra_1823",
        "Bolivar, Agualongo, and the Battle of Ibarra",
        "https://academiahistoria.org.ec/index.php/boletinesANHE/article/download/293/560",
        "Academia Nacional de Historia del Ecuador",
        "scholarly_history",
        "ecuador_academia_nacional_historia",
    ),
    _source(
        "wave8_ecuador_cuenca_independence_history",
        "La Campana Libertadora de 1820-1822",
        (
            "https://biblioteca.ucuenca.edu.ec/digital/files/original/"
            "b4faeac57c685ebe3f10ab61ac65cdcee34b5dc0.pdf"
        ),
        "University of Cuenca Digital Library",
        "academic_history",
        "university_cuenca_independence_history",
    ),
)


WAVE8_ECUADOR_INDEPENDENCE_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "free_province_guayaquil_1820_1822",
        "name": "Free Province of Guayaquil",
        "kind": "independent_province",
        "start_year": 1820,
        "end_year": 1822,
        "region": "Pacific South America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Independent Guayaquil polity and its Division Protectora de Quito, "
            "bounded from the October 1820 revolution to incorporation into "
            "Gran Colombia in 1822. No rating is inherited by modern Ecuador, "
            "Guayaquil city, or Gran Colombia."
        ),
        "source_ids": [
            "wave8_ecuador_anh_guayaquil_flags",
            "wave8_ecuador_cuenca_independence_history",
        ],
    },
    {
        "id": "sucre_quito_liberating_army_1821_1822",
        "name": "Sucre's multinational Quito liberating army",
        "kind": "campaign_coalition_army",
        "start_year": 1821,
        "end_year": 1822,
        "region": "Pacific South America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Campaign-bounded army combining Gran Colombian, Guayaquilean, "
            "Peruvian, Rioplatense, British-volunteer, and other formations under "
            "Antonio Jose de Sucre. Components do not receive separate inferred "
            "outcomes and no modern state inherits this rating."
        ),
        "source_ids": [
            "wave8_ecuador_anh_independence_campaign",
            "wave8_ecuador_army_pichincha_composition",
        ],
    },
    {
        "id": "gran_colombia_1819_1831",
        "name": "Republic of Colombia (Gran Colombia)",
        "kind": "republic",
        "start_year": 1819,
        "end_year": 1831,
        "region": "Northern South America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The Republic of Colombia conventionally called Gran Colombia. Its "
            "rating is not inherited by modern Colombia, Ecuador, Panama, or "
            "Venezuela, and the generic label Colombia is not opened."
        ),
        "source_ids": ["wave8_ecuador_anh_ibarra_1823"],
    },
    {
        "id": "agualongo_pasto_royalist_force_ibarra_1823",
        "name": "Agualongo's Pasto royalist force at Ibarra",
        "kind": "royalist_insurgent_force",
        "start_year": 1823,
        "end_year": 1823,
        "region": "Northern Andes",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded Pasto royalist force led by Agustin Agualongo in the "
            "1823 Ibarra campaign. No rating is inherited by Spain, Pasto, an "
            "ethnic population, or later royalist movements."
        ),
        "source_ids": ["wave8_ecuador_anh_ibarra_1823"],
    },
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    row_hash: str,
    name: str,
    year: int,
    cohort: str,
    side_1: list[str],
    side_2: list[str],
    evidence: list[str],
    outcome_sources: list[str],
    outcome_families: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "cohort": cohort,
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(evidence),
        "outcome_source_ids": sorted(outcome_sources),
        "outcome_source_family_ids": sorted(set(outcome_families)),
        "source_outcome_override": False,
        "actor_override": True,
        "audit_note": note,
    }


_CAMPAIGN_SOURCES = [
    "wave8_ecuador_anh_independence_campaign",
    "wave8_ecuador_army_independence_arms_history",
    "wave8_ecuador_cuenca_independence_history",
]


WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Huachi1820-1": _contract(
        "38d23b8ad651932286d6c036b2c514453c12a79ab022706ea9c09cad5e7e677a",
        "First Battle of Huachi",
        1820,
        "guayaquil_independence_campaign",
        ["spanish_empire"],
        ["free_province_guayaquil_1820_1822"],
        _CAMPAIGN_SOURCES,
        ["wave8_ecuador_anh_independence_campaign", "wave8_ecuador_army_independence_arms_history"],
        ["ecuador_academia_nacional_historia", "ecuadorian_army_history"],
        "Francisco Gonzalez's royalists defeated the Division Protectora de Quito on 22 November 1820; the patriot polity was Guayaquil, not a later Ecuadorian republic.",
    ),
    "hced-Tanizahua1821-1": _contract(
        "9fc091464b9a564727c6abfda6111ba974ddc550d875000ca63622f4291cddfc",
        "Battle of Tanizahua",
        1821,
        "guayaquil_independence_campaign",
        ["spanish_empire"],
        ["free_province_guayaquil_1820_1822"],
        _CAMPAIGN_SOURCES,
        ["wave8_ecuador_anh_independence_campaign", "wave8_ecuador_army_independence_arms_history"],
        ["ecuador_academia_nacional_historia", "ecuadorian_army_history"],
        "The 3 January 1821 defeat of the Guayaquilean Division Protectora is retained without turning the generic source label into modern Ecuador.",
    ),
    "hced-Yaguachi1821-1": _contract(
        "d220deb8ec713baeb41fa1b79a4c63922580de5b514990745b0dea6b91fe91a4",
        "Battle of Yaguachi (Cone)",
        1821,
        "sucre_quito_campaign",
        ["sucre_quito_liberating_army_1821_1822"],
        ["spanish_empire"],
        _CAMPAIGN_SOURCES,
        ["wave8_ecuador_anh_independence_campaign", "wave8_ecuador_army_independence_arms_history"],
        ["ecuador_academia_nacional_historia", "ecuadorian_army_history"],
        "Sucre's combined patriot army defeated Gonzalez at Cone near Yaguachi on 19 August 1821. Coalition components are not each given a full inferred result.",
    ),
    "hced-Huachi1821-1": _contract(
        "ce04b44994ebe9d3046547e91af766be4febdeeeb862fa1b62c7b626a4b4d0d8",
        "Second Battle of Huachi",
        1821,
        "sucre_quito_campaign",
        ["spanish_empire"],
        ["sucre_quito_liberating_army_1821_1822"],
        _CAMPAIGN_SOURCES,
        ["wave8_ecuador_anh_independence_campaign", "wave8_ecuador_army_independence_arms_history"],
        ["ecuador_academia_nacional_historia", "ecuadorian_army_history"],
        "Melchor Aymerich's royalists defeated Sucre's reorganized multinational army on 12 September 1821; this is distinct from Huachi 1820.",
    ),
    "hced-Pichincha1822-1": _contract(
        "2939a8a9d229655a8d7f52279a077f00d2192d30ab55880ca1ebb84c17671a2a",
        "Battle of Pichincha",
        1822,
        "sucre_quito_campaign",
        ["sucre_quito_liberating_army_1821_1822"],
        ["spanish_empire"],
        [*_CAMPAIGN_SOURCES, "wave8_ecuador_army_pichincha_composition"],
        ["wave8_ecuador_anh_independence_campaign", "wave8_ecuador_army_pichincha_composition"],
        ["ecuador_academia_nacional_historia", "ecuadorian_army_history"],
        "Sucre's multinational army defeated Aymerich on 24 May 1822. The campaign-coalition identity avoids assigning equal full credit to every contributing polity or modern Ecuador.",
    ),
    "hced-Ibarra1823-1": _contract(
        "0fe76bfe3abbc8ca7ec782ac7f17282e0a3ef5622d17990d884d744b549eb402",
        "Battle of Ibarra",
        1823,
        "pasto_royalist_rebellion",
        ["gran_colombia_1819_1831"],
        ["agualongo_pasto_royalist_force_ibarra_1823"],
        ["wave8_ecuador_anh_ibarra_1823"],
        ["wave8_ecuador_anh_ibarra_1823"],
        ["ecuador_academia_nacional_historia"],
        "Bolivar's Gran Colombian force defeated Agualongo's Pasto royalists on 17 July 1823. Neither side is mechanically equated with Ecuador or Spain.",
    ),
}


WAVE8_ECUADOR_INDEPENDENCE_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS = frozenset(
    WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS
)
WAVE8_ECUADOR_INDEPENDENCE_HOLD_IDS = frozenset()
WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS = (
    WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS
)


def _signature() -> str:
    payload = {
        "contracts": WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS,
        "entities": WAVE8_ECUADOR_INDEPENDENCE_ENTITIES,
        "holds": WAVE8_ECUADOR_INDEPENDENCE_HOLDS,
        "sources": WAVE8_ECUADOR_INDEPENDENCE_SOURCES,
    }
    return hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


WAVE8_ECUADOR_INDEPENDENCE_FINAL_AUDIT_SIGNATURE = (
    "7e364e908ab81cf894016b216d169c02178c22a63ef42ab10f49433d93c9fc75"
)


def validate_wave8_ecuador_independence_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    if _signature() != WAVE8_ECUADOR_INDEPENDENCE_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Ecuador independence audit signature changed")
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS,
        WAVE8_ECUADOR_INDEPENDENCE_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_ecuador_independence_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    install_exact_entities(
        release_entities, WAVE8_ECUADOR_INDEPENDENCE_ENTITIES, lane_name=_LANE_NAME
    )


def install_wave8_ecuador_independence_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    install_exact_sources(
        sources_by_id, WAVE8_ECUADOR_INDEPENDENCE_SOURCES, lane_name=_LANE_NAME
    )


def promote_wave8_ecuador_independence_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_ecuador_independence_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_ecuador_independence_",
    )


def wave8_ecuador_independence_counts() -> dict[str, int]:
    return {
        "promotion_contracts": len(WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS),
        "holds": 0,
        "reviewed_hced_rows": len(WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS),
        "new_entities": len(WAVE8_ECUADOR_INDEPENDENCE_ENTITIES),
        "new_sources": len(WAVE8_ECUADOR_INDEPENDENCE_SOURCES),
    }


def wave8_ecuador_independence_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS.values()
            ).items()
        )
    )
