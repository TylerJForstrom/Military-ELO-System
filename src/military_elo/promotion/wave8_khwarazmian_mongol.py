"""Exact-candidate audit of the Khwarazmian-Mongol campaign rows.

Six HCED rows from the 1219-1221 Mongol invasion have complete, independently
attested tactical outcomes and are promoted against the existing time-bounded
Khwarezmid and Mongol identities.  Ten neighboring rows remain explicit holds:
four mix battle and massacre/city-capture scope, two have a bad date or
counterpart, three predate the selected identity, and the 1244 Jerusalem force
was a post-imperial mercenary formation.

No spelling of Khwarazm is opened as an alias.  Every disposition is keyed to a
fingerprinted HCED row, matching outcome-less Wikidata records remain discovery
only, and unknown or ambiguous scope is never converted into a draw.
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
    "WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS",
    "WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS",
    "WAVE8_KHWARAZMIAN_MONGOL_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES",
    "WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS",
    "WAVE8_KHWARAZMIAN_MONGOL_ENTITIES",
    "WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES",
    "WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE",
    "WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT",
    "WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS",
    "WAVE8_KHWARAZMIAN_MONGOL_HOLDS",
    "WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS",
    "WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS",
    "WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS",
    "WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES",
    "WAVE8_KHWARAZMIAN_MONGOL_SOURCES",
    "install_wave8_khwarazmian_mongol_entities",
    "install_wave8_khwarazmian_mongol_sources",
    "promote_wave8_khwarazmian_mongol_contracts",
    "validate_wave8_khwarazmian_mongol_discovery_dispositions",
    "validate_wave8_khwarazmian_mongol_funnel",
    "validate_wave8_khwarazmian_mongol_integration_dispositions",
    "validate_wave8_khwarazmian_mongol_queue_contracts",
    "wave8_khwarazmian_mongol_audit_signature",
    "wave8_khwarazmian_mongol_cohort_counts",
    "wave8_khwarazmian_mongol_counts",
    "wave8_khwarazmian_mongol_metadata",
)


_LANE_NAME = "Wave 8 exact Khwarazmian-Mongol campaign audit"
_MODULE_OWNER = "military_elo.promotion.wave8_khwarazmian_mongol"
_EVENT_ID_PREFIX = "hced_wave8_khwarazmian_mongol_"
_CAMPAIGN_COHORT = "mongol_invasion_promotions_1219_1221"

_KHWAREZMID_EMPIRE = "clio_tm_khwarezmid_emp_1202_3ad0d483"
_MONGOL_EMPIRE = "mongol_empire"


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
        "accessed": "2026-07-20",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_KHWARAZMIAN_MONGOL_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_khwarazmian_mongol_army_upress_beckenbaugh",
        "Terry Beckenbaugh, Genghis Khan, in Great Commanders",
        (
            "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/"
            "csi-books/GreatCommanders.pdf"
        ),
        "Combat Studies Institute Press, US Army Combined Arms Center",
        "official_military_history_chapter",
        "army_upress_beckenbaugh_genghis_khan",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_khwarazmian_mongol_cambridge_history_iran_v5",
        "The Cambridge History of Iran, Volume 5: The Saljuq and Mongol Periods",
        (
            "https://www.cambridge.org/core/books/the-cambridge-history-of-iran/"
            "D0BEE51C0C239F497ADBC0CA18796A5B"
        ),
        "Cambridge University Press",
        "scholarly_reference_volume",
        "cambridge_history_iran_volume_5",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_khwarazmian_mongol_cambridge_otrar_campbell",
        (
            "Katie Campbell, The City of Otrar, Kazakhstan: Using Archaeology "
            "to Better Understand the Impact of the Mongol Conquest of Central Asia"
        ),
        "https://doi.org/10.17863/CAM.87960",
        "Harrassowitz Verlag / University of Cambridge Apollo Repository",
        "peer_reviewed_archaeology_article",
        "campbell_otrar_archaeology_2020",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_khwarazmian_mongol_iranica_bosworth_jalal",
        "C. E. Bosworth, Jalal-al-Din Khvarazmsah Mengubirni",
        (
            "https://www.iranicaonline.org/articles/"
            "jalal-al-din-kvarazmsahi-mengbirni/"
        ),
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_bosworth_jalal_al_din",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_khwarazmian_mongol_juvaini_boyle",
        (
            "Ata-Malik Juvaini, The History of the World-Conqueror, Volume I, "
            "translated by John Andrew Boyle"
        ),
        "https://archive.org/details/historyoftheworl011691mbp",
        "Manchester University Press / Harvard University Press",
        "translated_primary_chronicle_scholarly_edition",
        "juvaini_history_world_conqueror_boyle",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_KHWARAZMIAN_MONGOL_SOURCES
}


# This is the existing Cliopatria/registry identity, copied without widening its
# window and with an intentionally empty alias list.  Exact contracts are the
# only path by which this lane can activate it.
WAVE8_KHWARAZMIAN_MONGOL_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _KHWAREZMID_EMPIRE,
        "name": "Khwarezmid Empire",
        "kind": "empire",
        "start_year": 1202,
        "end_year": 1235,
        "region": "Khwarazm, Transoxiana, Khorasan, and Iran",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate while "
            "retaining its 1202-1235 source window exactly. Only fingerprinted, "
            "candidate-keyed events may use this identity: no spelling of "
            "Khwarazm becomes a resolver alias, predecessors inherit no Elo, and "
            "the post-imperial Khwarazmian mercenary force at Jerusalem in 1244 "
            "is explicitly excluded."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_khwarazmian_mongol_cambridge_history_iran_v5",
            "wave8_khwarazmian_mongol_iranica_bosworth_jalal",
        ],
    },
)


WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES: dict[str, str] = {
    "hced-Andkhui1205-1": (
        "8f68118420680ae141945c1e74092f44feda65f60243e35dbc09e79acb4d51d6"
    ),
    "hced-Bamian1221-1": (
        "cd359ddc6d79b4d4a8daa27bfcc3bdf4a2e7b2cddd30ef077fa7feff34ae4ba7"
    ),
    "hced-Bokhara1220-1": (
        "6e787ef800779d389aa806840e4d4f8608455f4ba40fe65443c2eca6ca34f666"
    ),
    "hced-Dabusiyya1032-1": (
        "c45c1078fc7647dd100a363d29023e9d587a19405527ae61f2b5cfad6b35d425"
    ),
    "hced-Gurganj1221-1": (
        "463e321828609de15725925c2acc1073a5c4ccaad00696c09a7ad850b7041ccd"
    ),
    "hced-Hamadan1220-1": (
        "ab0ec0211c31bf4fe47de29743cf8c027a5e3c0bc48d45fc9f63464244a6c9f3"
    ),
    "hced-Hazarasp1017-1": (
        "4c8cbe8c73d69c93a4075cd8bff3239aa01e6c0f18321345d5762ae682accadb"
    ),
    "hced-Indus1221-1": (
        "a39a51f869b65235f24be512cca5b61a0ce1d2953a70ad676cbc073aa3d0ebe7"
    ),
    "hced-Jand1218-1": (
        "16bf7cffc627565e03e86b1d618bbee795371b57003922684ee0669789de411a"
    ),
    "hced-Jerusalem1244-1": (
        "4064c4bc57f411bfe62601e156e0d6355662582c79013e34c02785fc61d428db"
    ),
    "hced-Khojend1220-1": (
        "2015b72c689c0c0c0a8d60437c93a5e559f97e260c99ee9a7e8682337306dbe3"
    ),
    "hced-Merv1221-1": (
        "7d601a8a42232e31aae8d4ceafb7baf3e60e32aaa9825334f09a7f7763edfb95"
    ),
    "hced-Otrar1219-1": (
        "081c576844c2319597ee205e5d9b8ea00324061bf8e2715dccd80d2ac7c5bb5b"
    ),
    "hced-Parwan Durrah1221-1": (
        "dc94076821782f07c4bb62ca0358d3fb98a06436bb160bd020e4377fb58da2f3"
    ),
    "hced-Samarkand1220-1": (
        "7f2f2fba186b5b184eb62060e5c4e6597f52ecb7303f441fe037a646b8ae9cdf"
    ),
    "hced-Shahr Rey1194-1": (
        "79e29314237bb760a5615084c220e8513e0bb99bbaff3e05d26ba87751f27e9f"
    ),
}


def _raw(
    year: int,
    side_1: str,
    side_2: str,
    winner: str,
    loser: str,
    massacre: str,
) -> dict[str, Any]:
    return {
        "year_low": year,
        "year_best": year,
        "year_high": year,
        "side_1_raw": side_1,
        "side_2_raw": side_2,
        "winner_raw": winner,
        "loser_raw": loser,
        "massacre_raw": massacre,
    }


WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES: dict[str, dict[str, Any]] = {
    "hced-Andkhui1205-1": _raw(
        1205,
        "Khwarezmian Empire",
        "Afghanistan",
        "Khwarezmian Empire",
        "Afghanistan",
        "No",
    ),
    "hced-Bamian1221-1": _raw(
        1221,
        "Mongols",
        "Khwarezm",
        "Mongols",
        "Khwarezm",
        "Battle followed by massacre",
    ),
    "hced-Bokhara1220-1": _raw(
        1220,
        "Mongols",
        "Khwarezmian Empire",
        "Mongols",
        "Khwarezmian Empire",
        "No",
    ),
    "hced-Dabusiyya1032-1": _raw(
        1032,
        "Seljuk Turks",
        "Khwarezm",
        "Seljuk Turks",
        "Khwarezm",
        "No",
    ),
    "hced-Gurganj1221-1": _raw(
        1221,
        "Mongols",
        "Khwarezm Empire",
        "Mongols",
        "Khwarezm Empire",
        "Battle followed by massacre",
    ),
    "hced-Hamadan1220-1": _raw(
        1220,
        "Mongols",
        "Khwarezmian Empire",
        "Mongols",
        "Khwarezmian Empire",
        "Battle followed by massacre",
    ),
    "hced-Hazarasp1017-1": _raw(
        1017,
        "Mahmud of Ghazni",
        "Khwarezm Rebels",
        "Mahmud of Ghazni",
        "Khwarezm Rebels",
        "Battle followed by massacre",
    ),
    "hced-Indus1221-1": _raw(
        1221,
        "Mongols",
        "Khwarezm",
        "Mongols",
        "Khwarezm",
        "No",
    ),
    "hced-Jand1218-1": _raw(
        1218,
        "Mongols",
        "Khwarezm",
        "Mongols",
        "Khwarezm",
        "No",
    ),
    "hced-Jerusalem1244-1": _raw(
        1244,
        "Khwarezem",
        "Kingdom of Jerusalem",
        "Khwarezem",
        "Kingdom of Jerusalem",
        "No",
    ),
    "hced-Khojend1220-1": _raw(
        1220,
        "Mongols",
        "Khwarezm Empire",
        "Mongols",
        "Khwarezm Empire",
        "No",
    ),
    "hced-Merv1221-1": _raw(
        1221,
        "Mongols",
        "Khwarezm Empire",
        "Mongols",
        "Khwarezm Empire",
        "Battle followed by massacre",
    ),
    "hced-Otrar1219-1": _raw(
        1219,
        "Mongols",
        "Khwarezmian Empire",
        "Mongols",
        "Khwarezmian Empire",
        "No",
    ),
    "hced-Parwan Durrah1221-1": _raw(
        1221,
        "Khwarezm",
        "Mongols",
        "Khwarezm",
        "Mongols",
        "No",
    ),
    "hced-Samarkand1220-1": _raw(
        1220,
        "Mongols",
        "Khwarezmian Empire",
        "Mongols",
        "Khwarezmian Empire",
        "No",
    ),
    "hced-Shahr Rey1194-1": _raw(
        1194,
        "Khwarezmian Empire",
        "Seljuk Sultanate of Iran",
        "Khwarezmian Empire",
        "Seljuk Sultanate of Iran",
        "No",
    ),
}


WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS: dict[str, tuple[str, ...]] = {
    "khwarezem": ("hced-Jerusalem1244-1",),
    "khwarezm": (
        "hced-Bamian1221-1",
        "hced-Dabusiyya1032-1",
        "hced-Indus1221-1",
        "hced-Jand1218-1",
        "hced-Parwan Durrah1221-1",
    ),
    "khwarezm empire": (
        "hced-Gurganj1221-1",
        "hced-Khojend1220-1",
        "hced-Merv1221-1",
    ),
    "khwarezm rebels": ("hced-Hazarasp1017-1",),
    "khwarezmian empire": (
        "hced-Andkhui1205-1",
        "hced-Bokhara1220-1",
        "hced-Hamadan1220-1",
        "hced-Otrar1219-1",
        "hced-Samarkand1220-1",
        "hced-Shahr Rey1194-1",
    ),
}

_EXACT_LABELS = frozenset(WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS)

WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "khwarezem": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "911a4bea28a93c7839e563885c4f5df2d0537f5f3fe3501f0dc3c408ff269f2e"
        ),
        "events_touched": 1,
        "label": "khwarezem",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 1,
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "khwarezm": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "a588302c13e93a00376c4710794ccd3b6c6de2ac7570a6ebd2ea08da668df51f"
        ),
        "events_touched": 5,
        "label": "khwarezm",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "unresolved_side_attempts": 5,
        "zero_time_valid_candidates": 5,
    },
    "khwarezm empire": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "0c89b23c28502e82566d891a90cc981a205bb013ef71d465d0c41337b9e4f543"
        ),
        "events_touched": 3,
        "label": "khwarezm empire",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 1,
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "khwarezm rebels": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "e40fbefc74c3de7383b7466897ce121b503d3e1fec4dbef3158458978ca928c5"
        ),
        "events_touched": 1,
        "label": "khwarezm rebels",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "khwarezmian empire": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "70b7926ecc30df78de98ff909cbf39236402dabfcc31989d8022fa25e351ff67"
        ),
        "events_touched": 6,
        "label": "khwarezmian empire",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "unresolved_side_attempts": 6,
        "zero_time_valid_candidates": 6,
    },
}


def _canonical(name: str, year: int, granularity: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "date_text": str(year),
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_id: str,
    side_2_entity_id: str,
    outcome_roles: Mapping[str, str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_roles)))
    return {
        "raw_row_sha256": WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _CAMPAIGN_COHORT,
        "side_1_entity_ids": [side_1_entity_id],
        "side_2_entity_ids": [side_2_entity_id],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": {
            source_id: str(outcome_roles[source_id]) for source_id in outcomes
        },
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_existing_khwarezmid_empire_identity",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


_ARMY = "wave8_khwarazmian_mongol_army_upress_beckenbaugh"
_CAMBRIDGE_OTRAR = "wave8_khwarazmian_mongol_cambridge_otrar_campbell"
_IRANICA_JALAL = "wave8_khwarazmian_mongol_iranica_bosworth_jalal"
_JUVAINI = "wave8_khwarazmian_mongol_juvaini_boyle"


WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Otrar1219-1": _contract(
        "hced-Otrar1219-1",
        _canonical("Siege of Otrar", 1219, "siege_and_capture"),
        _MONGOL_EMPIRE,
        _KHWAREZMID_EMPIRE,
        {
            _ARMY: (
                "Independently records Otrar's siege by Chagatai and Ogedei and "
                "their successful conclusion before joining at Samarkand."
            ),
            _CAMBRIDGE_OTRAR: (
                "Peer-reviewed site study identifies the 1219 Mongol siege, "
                "capture, and destruction of Khwarazmian Otrar."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle narrates the Mongol investment "
                "and eventual capture of Otrar and its citadel."
            ),
        },
        (
            "Three independent publication families agree that the Khwarazmian "
            "frontier city fell after the Mongol siege. Only the tactical capture "
            "is rated; later destruction and killing are not separate outcomes."
        ),
        confidence=0.97,
    ),
    "hced-Bokhara1220-1": _contract(
        "hced-Bokhara1220-1",
        _canonical("Siege and Capture of Bukhara", 1220, "siege_and_capture"),
        _MONGOL_EMPIRE,
        _KHWAREZMID_EMPIRE,
        {
            _ARMY: (
                "Official military-history synthesis records Genghis Khan's "
                "desert approach and easy capture of Bukhara in 1220."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle narrates Bukhara's surrender "
                "and the Mongol reduction of the remaining citadel."
            ),
        },
        (
            "Juvaini and the US Army campaign study independently attest the "
            "Mongol capture. The contract rates the siege/capture result and does "
            "not turn subsequent coercion or destruction into another event."
        ),
        confidence=0.96,
    ),
    "hced-Khojend1220-1": _contract(
        "hced-Khojend1220-1",
        _canonical("Siege of Khujand", 1220, "siege_and_capture"),
        _MONGOL_EMPIRE,
        _KHWAREZMID_EMPIRE,
        {
            _ARMY: (
                "Official military-history synthesis identifies Jochi's wing as "
                "the Mongol force assigned to attack Khujand."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle records Temur Malik's defense "
                "and the Mongol defeat of the Khujand resistance."
            ),
        },
        (
            "The two source families support the HCED polarity and actor pair. "
            "The exact contract does not generalize either raw polity spelling."
        ),
        confidence=0.92,
    ),
    "hced-Samarkand1220-1": _contract(
        "hced-Samarkand1220-1",
        _canonical("Siege of Samarkand", 1220, "siege_and_capitulation"),
        _MONGOL_EMPIRE,
        _KHWAREZMID_EMPIRE,
        {
            _ARMY: (
                "Official military-history synthesis records Samarkand's March "
                "1220 surrender and the Mongol reduction of its citadel."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle narrates the Mongol siege, "
                "surrender, and capture of Samarkand."
            ),
        },
        (
            "Both publication families attest a Mongol tactical victory at the "
            "city. The contract rates the siege/capitulation only, not civilian "
            "harm or the campaign's strategic termination."
        ),
        confidence=0.97,
    ),
    "hced-Indus1221-1": _contract(
        "hced-Indus1221-1",
        _canonical("Battle of the Indus", 1221, "single_land_battle"),
        _MONGOL_EMPIRE,
        _KHWAREZMID_EMPIRE,
        {
            _ARMY: (
                "Official military-history synthesis records Genghis Khan's "
                "defeat of Jalal al-Din and destruction of his army at the Indus."
            ),
            _IRANICA_JALAL: (
                "Bosworth's scholarly biography records the battle on the Indus "
                "and Jalal al-Din's escape across the river from the Mongols."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle narrates Jalal al-Din's defeat "
                "by Genghis Khan and flight across the Indus."
            ),
        },
        (
            "Three authoritative families preserve the Mongol battlefield win. "
            "The escape of Jalal al-Din does not negate the tactical defeat and "
            "no later Indian campaign outcome is inferred."
        ),
        confidence=0.98,
    ),
    "hced-Parwan Durrah1221-1": _contract(
        "hced-Parwan Durrah1221-1",
        _canonical("Battle of Parwan", 1221, "single_land_battle"),
        _KHWAREZMID_EMPIRE,
        _MONGOL_EMPIRE,
        {
            _ARMY: (
                "Official military-history synthesis records Jalal al-Din's "
                "defeat of Shigi Qutuqu's Mongol field force in Afghanistan."
            ),
            _IRANICA_JALAL: (
                "Bosworth's scholarly biography explicitly calls Parwan a serious "
                "defeat inflicted on the pursuing Mongols."
            ),
            _JUVAINI: (
                "Translated contemporary chronicle narrates Jalal al-Din's victory "
                "over Shigi Qutuqu before the retreat toward the Indus."
            ),
        },
        (
            "All three families agree on the exceptional Khwarazmian tactical "
            "victory. The contract does not infer campaign victory from that "
            "battle or reverse the later Indus result."
        ),
        confidence=0.98,
    ),
}


def _hold(
    candidate_id: str,
    cohort: str,
    hold_category: str,
    evidence_refs: Iterable[str],
    hold_reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES[candidate_id],
        "cohort": cohort,
        "disposition": "hold",
        "hold_category": hold_category,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_reason": hold_reason,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    }


_CAMBRIDGE_IRAN = "wave8_khwarazmian_mongol_cambridge_history_iran_v5"

WAVE8_KHWARAZMIAN_MONGOL_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Bamian1221-1": _hold(
        "hced-Bamian1221-1",
        "mongol_invasion_massacre_scope_holds_1220_1221",
        "massacre_or_city_capture_scope_not_clean_tactical_battle",
        [_CAMBRIDGE_IRAN, _JUVAINI],
        (
            "HCED explicitly marks a battle followed by massacre while its raw "
            "participant list names places and peoples rather than a clean "
            "Khwarezmid defending force. The Mongol conquest is known, but this "
            "row's exact competitive scope is not rated."
        ),
    ),
    "hced-Gurganj1221-1": _hold(
        "hced-Gurganj1221-1",
        "mongol_invasion_massacre_scope_holds_1220_1221",
        "massacre_or_city_capture_scope_not_clean_tactical_battle",
        [_CAMBRIDGE_IRAN, _IRANICA_JALAL, _JUVAINI],
        (
            "The lengthy investment and destruction of Gurganj are attested, but "
            "HCED combines battle and massacre and does not isolate one tactical "
            "contest. That composite row remains unknown rather than becoming a draw."
        ),
    ),
    "hced-Hamadan1220-1": _hold(
        "hced-Hamadan1220-1",
        "mongol_invasion_massacre_scope_holds_1220_1221",
        "massacre_or_city_capture_scope_not_clean_tactical_battle",
        [_CAMBRIDGE_IRAN, _JUVAINI],
        (
            "HCED's battle-followed-by-massacre classification and broad pursuit "
            "participant strings do not define a single independently verified "
            "Hamadan engagement in 1220, so no result is emitted."
        ),
    ),
    "hced-Merv1221-1": _hold(
        "hced-Merv1221-1",
        "mongol_invasion_massacre_scope_holds_1220_1221",
        "massacre_or_city_capture_scope_not_clean_tactical_battle",
        [_CAMBRIDGE_IRAN, _JUVAINI],
        (
            "The sources attest Merv's conquest and catastrophic killing, but the "
            "HCED row merges battle and massacre and supplies no clean tactical "
            "boundary. The city-level catastrophe is not manufactured into a battle."
        ),
    ),
    "hced-Jand1218-1": _hold(
        "hced-Jand1218-1",
        "campaign_date_or_counterpart_holds_1205_1218",
        "source_year_precedes_reviewed_siege_chronology",
        [_ARMY, _JUVAINI],
        (
            "HCED fixes the action in 1218, while reviewed campaign chronology "
            "places the Mongol operation against Jand after the invasion began. "
            "The exact year cannot be corrected silently, so the row stays held."
        ),
    ),
    "hced-Andkhui1205-1": _hold(
        "hced-Andkhui1205-1",
        "campaign_date_or_counterpart_holds_1205_1218",
        "generic_afghanistan_is_not_a_reviewed_historical_counterpart",
        [_CAMBRIDGE_IRAN],
        (
            "The raw opponent 'Afghanistan' is a modern geographic shorthand, not "
            "the reviewed Ghurid/Qara Khitai/Karakhanid coalition or polity for the "
            "Andkhud fighting. The counterpart is therefore unresolved."
        ),
    ),
    "hced-Dabusiyya1032-1": _hold(
        "hced-Dabusiyya1032-1",
        "pre_empire_identity_holds_1017_1194",
        "row_predates_selected_khwarezmid_empire_interval",
        [_CAMBRIDGE_IRAN],
        (
            "The 1032 row predates the selected 1202-1235 Khwarezmid Empire "
            "identity by 170 years. No earlier Khwarazm identity is created or "
            "bridged in this lane."
        ),
    ),
    "hced-Shahr Rey1194-1": _hold(
        "hced-Shahr Rey1194-1",
        "pre_empire_identity_holds_1017_1194",
        "row_predates_selected_khwarezmid_empire_interval",
        [_CAMBRIDGE_IRAN],
        (
            "The 1194 Ray conflict belongs to an earlier Khwarazmshah interval "
            "than the existing 1202-1235 identity. The eight-year boundary gap is "
            "preserved instead of expanding the registry window."
        ),
    ),
    "hced-Hazarasp1017-1": _hold(
        "hced-Hazarasp1017-1",
        "pre_empire_identity_holds_1017_1194",
        "rebel_faction_and_massacre_not_selected_polity",
        [_CAMBRIDGE_IRAN],
        (
            "The raw loser is a Khwarezm rebel faction in a battle-followed-by-"
            "massacre row from 1017, not the later Khwarezmid Empire. Neither the "
            "faction nor the composite outcome is promoted."
        ),
    ),
    "hced-Jerusalem1244-1": _hold(
        "hced-Jerusalem1244-1",
        "post_empire_mercenary_hold_1244",
        "post_imperial_mercenary_force_not_selected_polity",
        [_CAMBRIDGE_IRAN, _IRANICA_JALAL],
        (
            "The Khwarazmian troops at Jerusalem were a displaced post-imperial "
            "mercenary formation, not the selected state identity and not the "
            "Mongol Empire. A separate force identity would require its own audit."
        ),
    ),
}


WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS = frozenset(
    WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS
)
WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS = frozenset(
    WAVE8_KHWARAZMIAN_MONGOL_HOLDS
)
WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS = frozenset(
    {
        *WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS,
        *WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS,
    }
)
WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
)
WAVE8_KHWARAZMIAN_MONGOL_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named engagement and modern "
            "country but do not independently verify HCED's exact coordinate; "
            "retain provenance and country while withholding the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS.items()
    )
}


# Outcome-less discovery rows are pinned as cross-source twins and may never
# become rating owners.  The HCED contracts above remain the sole owners.
WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Bokhara1220-1": "Q110970851",
    "hced-Indus1221-1": "Q3269760",
    "hced-Khojend1220-1": "Q136332981",
    "hced-Otrar1219-1": "Q111943842",
    "hced-Parwan Durrah1221-1": "Q3269746",
    "hced-Samarkand1220-1": "Q7510363",
}
WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q110970851": "e0cd860bbc3f8fcaddeb938be4377c3c345cda1e1cfc78edaf48a3e450d4fa44",
    "Q111943842": "9a7d9ebafaf8e58c138c75cade3d6137499db983000e919b2cd5182df86c7419",
    "Q136332981": "c95bf66013a750827c12204b64c5d009a3eb3c6cfb99840e975a1d5c74f2c49c",
    "Q3269746": "7b2080ac17d74451a8430b0c2b9546ec53b7b296d4eff4a5e4602b3d0bb9d92b",
    "Q3269760": "b5c19c846aa2b43fdfe3636acde9556699d721155aec84afdbca351800ba8165",
    "Q7510363": "b427498abf6d0be9d738bc84d319a4b95600497d84ed97760bec79e6b856f26a",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS,
        "discovery_row_hashes": WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS,
        "entities": WAVE8_KHWARAZMIAN_MONGOL_ENTITIES,
        "expected_raw_outcomes": WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES,
        "funnel": WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT,
        "holds": WAVE8_KHWARAZMIAN_MONGOL_HOLDS,
        "label_candidate_ids": WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS,
        "location_reasons": WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES,
        "sources": WAVE8_KHWARAZMIAN_MONGOL_SOURCES,
    }


def wave8_khwarazmian_mongol_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE = (
    "d13cb22fa3d10d0cd1e60228cf134925ef2b08c2fc51ea229d3e2212fad92cde"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_KHWARAZMIAN_MONGOL_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if any(
        not str(source["url"]).startswith("https://")
        or not source["source_family_id"]
        or not _is_sorted_unique(source["evidence_roles"])
        for source in WAVE8_KHWARAZMIAN_MONGOL_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source fixture drift")

    entity_ids = {
        str(entity["id"]) for entity in WAVE8_KHWARAZMIAN_MONGOL_ENTITIES
    }
    if entity_ids != {_KHWAREZMID_EMPIRE}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    entity = WAVE8_KHWARAZMIAN_MONGOL_ENTITIES[0]
    if (
        entity["aliases"]
        or entity["predecessors"]
        or (entity["start_year"], entity["end_year"]) != (1202, 1235)
        or normalize_label(entity["name"]) in _EXACT_LABELS
    ):
        raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity source order drift")

    if WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS & WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if (
        WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS
        != set(WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES)
        or WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS
        != set(WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES)
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    label_inventory = {
        candidate_id
        for candidate_ids in WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS.values()
        for candidate_id in candidate_ids
    }
    if label_inventory != WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} label inventory drift")
    if set(WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label inventory drift")
    if (
        WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS
        != WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
        or WAVE8_KHWARAZMIAN_MONGOL_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_KHWARAZMIAN_MONGOL_LOCATION_QUARANTINE_REASONS)
        != WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location quarantine drift")

    used_sources = set(map(str, entity["source_ids"])) & source_ids
    allowed_actors = {_KHWAREZMID_EMPIRE, _MONGOL_EMPIRE}
    for candidate_id, contract in WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome drift: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        if actors != allowed_actors:
            raise ValueError(f"{_LANE_NAME} actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or set(evidence) != set(outcomes)
            or not set(outcomes) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure drift: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        if any(
            "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} source outcome-role drift: {candidate_id}")
        event_roles = contract.get("event_evidence_roles", {})
        if set(event_roles) != set(outcomes) or any(
            not isinstance(role, str) or not role.strip()
            for role in event_roles.values()
        ):
            raise ValueError(f"{_LANE_NAME} event-specific evidence drift: {candidate_id}")
        low = int(contract["canonical_event"]["year_low"])
        high = int(contract["canonical_event"]["year_high"])
        if not (1206 <= low <= high <= 1235):
            raise ValueError(f"{_LANE_NAME} identity-window drift: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_KHWARAZMIAN_MONGOL_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or not hold["hold_category"]
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if set(WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS) != (
        WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} discovery twin owner drift")
    if set(WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_TWINS.values()) != set(
        WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery twin inventory drift")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        wave8_khwarazmian_mongol_audit_signature()
        != WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_khwarazmian_mongol_queue_contracts(
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
    if (
        exact_ids != WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS
        or len(exact) != len(exact_ids)
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}

    actual_labels: dict[str, list[str]] = {label: [] for label in _EXACT_LABELS}
    for candidate_id, row in by_id.items():
        matched = {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        } & _EXACT_LABELS
        if len(matched) != 1:
            raise ValueError(f"{_LANE_NAME} expected one audited label: {candidate_id}")
        actual_labels[next(iter(matched))].append(candidate_id)
    normalized_actual = {
        label: tuple(sorted(candidate_ids))
        for label, candidate_ids in actual_labels.items()
    }
    if normalized_actual != WAVE8_KHWARAZMIAN_MONGOL_LABEL_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label cohort changed")

    for candidate_id, expected_hash in WAVE8_KHWARAZMIAN_MONGOL_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        expected = WAVE8_KHWARAZMIAN_MONGOL_EXPECTED_RAW_OUTCOMES[candidate_id]
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} raw outcome changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
        ):
            raise ValueError(f"{_LANE_NAME} queue semantic guard changed: {candidate_id}")
    for candidate_id in WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS:
        if by_id[candidate_id].get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS,
        WAVE8_KHWARAZMIAN_MONGOL_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "exact_label_rows": len(exact),
        "exact_labels": len(_EXACT_LABELS),
    }


def validate_wave8_khwarazmian_mongol_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    matches = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if str(row.get("label")) in _EXACT_LABELS
    }
    if set(matches) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label inventory changed")
    for label, expected in WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT.items():
        row = matches[label]
        actual = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "label": str(row.get("label")),
            "rated_counterpart_entities": int(
                row.get("rated_counterpart_entities", -1)
            ),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "unresolved_side_attempts": int(
                row.get("unresolved_side_attempts", -1)
            ),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "events_touched": sum(
            int(row["events_touched"])
            for row in WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT.values()
        ),
        "exact_labels": len(_EXACT_LABELS),
        "unresolved_side_attempts": sum(
            int(row["unresolved_side_attempts"])
            for row in WAVE8_KHWARAZMIAN_MONGOL_FUNNEL_AUDIT.values()
        ),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_khwarazmian_mongol_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        participant_labels = {
            str(participant.get("label")) for participant in row.get("participants", [])
        }
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("winners") != []
            or participant_labels != {"Khwarazmian Empire", "Mongol Empire"}
        ):
            raise ValueError(f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}")
    return {
        "discovery_nonrating_twins": len(
            WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES
        ),
        "discovery_promotions": 0,
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


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Bokhara1220-1": {
        "Bokhara",
        "Bukhara",
        "Capture of Bukhara",
        "Siege and Capture of Bukhara",
        "Siege of Bukhara",
    },
    "hced-Indus1221-1": {"Battle of Indus", "Battle of the Indus", "Indus"},
    "hced-Khojend1220-1": {
        "Khojend",
        "Khujand",
        "Siege of Khojend",
        "Siege of Khujand",
    },
    "hced-Otrar1219-1": {
        "Otrar",
        "Otrar Catastrophe",
        "Siege of Otrar",
        "Utrar",
    },
    "hced-Parwan Durrah1221-1": {
        "Battle of Parwan",
        "Battle of Parwan Durrah",
        "Parwan",
        "Parwan Durrah",
    },
    "hced-Samarkand1220-1": {
        "Samarkand",
        "Samarqand",
        "Siege of Samarkand",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(
            WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS[candidate_id]["canonical_event"][
                "year_low"
            ]
        ),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_khwarazmian_mongol_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_khwarazmian_mongol_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS
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
        if event.get("hced_candidate_id")
        not in WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
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


def install_wave8_khwarazmian_mongol_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_KHWARAZMIAN_MONGOL_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_khwarazmian_mongol_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_KHWARAZMIAN_MONGOL_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_KHWARAZMIAN_MONGOL_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_khwarazmian_mongol_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_khwarazmian_mongol_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_khwarazmian_mongol_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS.values(),
                    *WAVE8_KHWARAZMIAN_MONGOL_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_khwarazmian_mongol_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_twins": len(
            WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_KHWARAZMIAN_MONGOL_HOLDS),
        "new_entities": len(WAVE8_KHWARAZMIAN_MONGOL_ENTITIES),
        "new_sources": len(WAVE8_KHWARAZMIAN_MONGOL_SOURCES),
        "newly_rated_events": len(WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_KHWARAZMIAN_MONGOL_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_KHWARAZMIAN_MONGOL_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_KHWARAZMIAN_MONGOL_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_khwarazmian_mongol_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_khwarazmian_mongol_counts(),
        "cohorts": wave8_khwarazmian_mongol_cohort_counts(),
        "final_audit_signature": WAVE8_KHWARAZMIAN_MONGOL_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(
            WAVE8_KHWARAZMIAN_MONGOL_CONTRACT_IDS
        ),
        "hold_candidate_ids": sorted(WAVE8_KHWARAZMIAN_MONGOL_HOLD_IDS),
        "discovery_nonrating_candidate_ids": sorted(
            WAVE8_KHWARAZMIAN_MONGOL_DISCOVERY_ROW_HASHES
        ),
    }


_validate_static()
