"""Candidate-keyed audit of HCED's unresolved pre-1853 Montenegro rows.

HCED has ten rows whose exact side label is ``Montenegro``. Five later
Principality-era rows already rate through the legacy release, and Mojkovac is
already excluded because HCED reverses the documented defensive result. This
lane owns the four still-unresolved eighteenth-century rows.

Only Martinići and Krusi promote. Independent museum, archival, and scholarly
sources agree that Petar I's Montenegrin-Brda force defeated Kara Mahmud
Pasha's Scutari army in both 1796 actions. Podgoritza/Carev Laz (1712) and
Čevo (1768) remain staged: recent source criticism rejects the categorical
victories asserted by HCED, and the place-only rows cannot be aligned to a
unique victorious engagement without inventing an outcome.
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
    "WAVE8_MONTENEGRO_1796_CONTRACT_IDS",
    "WAVE8_MONTENEGRO_1796_CONTRACTS",
    "WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MONTENEGRO_1796_ENTITIES",
    "WAVE8_MONTENEGRO_1796_EXPECTED_EXACT_LABEL_IDS",
    "WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT",
    "WAVE8_MONTENEGRO_1796_HOLD_IDS",
    "WAVE8_MONTENEGRO_1796_HOLDS",
    "WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS",
    "WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MONTENEGRO_1796_RESERVED_IDS",
    "WAVE8_MONTENEGRO_1796_ROW_HASHES",
    "WAVE8_MONTENEGRO_1796_SOURCES",
    "install_wave8_montenegro_1796_entities",
    "install_wave8_montenegro_1796_sources",
    "promote_wave8_montenegro_1796_contracts",
    "validate_wave8_montenegro_1796_funnel",
    "validate_wave8_montenegro_1796_integration_dispositions",
    "validate_wave8_montenegro_1796_queue_contracts",
    "wave8_montenegro_1796_audit_signature",
    "wave8_montenegro_1796_cohort_counts",
    "wave8_montenegro_1796_counts",
    "wave8_montenegro_1796_location_quarantine_additions",
    "wave8_montenegro_1796_metadata",
)


_LANE_NAME = "Wave 8 exact pre-1853 Montenegro audit"
_MODULE_OWNER = "military_elo.promotion.wave8_montenegro_1796"
_EVENT_ID_PREFIX = "hced_wave8_montenegro_1796_"
_EXACT_LABEL = "montenegro"

_MONTENEGRIN_FORCE_ID = "petar_i_montenegro_brda_force_1796"
_SCUTARI_FORCE_ID = "kara_mahmud_scutari_campaign_army_1796"


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
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
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


WAVE8_MONTENEGRO_1796_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_montenegro_national_museum_history",
        "Historical Museum of Montenegro: Creation of the Modern State",
        (
            "https://narodnimuzej.me/wp-content/uploads/2020/09/"
            "Istorijski-muzej-ENG.pdf"
        ),
        "National Museum of Montenegro",
        "official_museum_historical_catalogue",
        "national_museum_montenegro_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_balcanica_1796",
        (
            "Political Developments and Unrests in Stara Raška (Old Rascia) "
            "and Old Herzegovina during Ottoman Rule"
        ),
        "https://doiserbia.nb.rs/img/doi/0350-7653/2015/0350-76531546079S.pdf",
        "Balcanica XLVI / Institute for Balkan Studies",
        "peer_reviewed_scholarly_article_with_archival_references",
        "scekic_lekovic_premovic_balcanica_2015",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_belgrade_law_1796",
        (
            "The Application of the General Montenegrin and Mountains Code "
            "and the Issue of the Intensity of Compulsion"
        ),
        "https://www.ceeol.com/search/article-detail?id=1059598",
        "University of Belgrade Faculty of Law",
        "peer_reviewed_legal_history_article",
        "jovicevic_montenegrin_code_1990",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_historical_lexicon_krusi",
        "Why the Battle of Krusi is central to Montenegro's history",
        (
            "https://www.portalanalitika.me/clanak/247625--dragulji-istorije-"
            "zasto-je-bitka-na-krusima-najznacajnija-u-istoriji-crne-gore"
        ),
        "Portal Analitika, citing the Historical Lexicon of Montenegro",
        "public_history_article_with_scholarly_lexicon_citations",
        "historical_lexicon_montenegro_krusi",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_petar_speeches_1796",
        "Speeches before the battles of Martinići and Krusi, 1796",
        "https://www.rastko.rs/rastko-cg/povijest/sveti_petar-1796e.html",
        "Project Rastko transcription of History of Montenegro (Zemun, 1850)",
        "translated_primary_text_transcription",
        "petar_i_battle_speeches_1796",
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_ucg_carev_laz_critique",
        "Battle of Carev Laz: Between Legend and Truth",
        (
            "https://www.ucg.ac.me/skladiste/blog_21704/objava_186808/fajlovi/"
            "Zapisi%202024-1-2%20web.pdf"
        ),
        "Historical Institute, University of Montenegro",
        "peer_reviewed_source_critical_history_article",
        "bajovic_carev_laz_2024",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_montenegro_vakanuvis_scepan",
        "The Era of Little Stepan in Montenegro (1767-1773)",
        "https://dergipark.org.tr/tr/pub/vakanuvis/article/1336135",
        "Vakanüvis International Journal of Historical Research",
        "peer_reviewed_ottoman_archival_history_article",
        "yuksel_scepan_mali_2024",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_MONTENEGRO_1796_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1796,
        "end_year": 1796,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No generic Montenegro, Scutari, Albania, Ottoman Empire, or "
            "modern-state alias resolves to this record. It inherits no Elo from "
            "a predecessor, successor, dynasty, tribe, or broader imperial actor."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_MONTENEGRO_1796_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _MONTENEGRIN_FORCE_ID,
        "Petar I's Montenegrin-Brda field force (1796)",
        "campaign_bounded_confederate_force",
        "Old Montenegro and Brda",
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_belgrade_law_1796",
            "wave8_montenegro_national_museum_history",
            "wave8_montenegro_petar_speeches_1796",
        ],
        (
            "Bounded to the Montenegrin and Brda tribes organized by Metropolitan "
            "Petar I for the two 1796 campaigns at Martinići and Krusi. The shared "
            "campaign identity does not back-project later state institutions."
        ),
    ),
    _entity(
        _SCUTARI_FORCE_ID,
        "Kara Mahmud Pasha's Scutari campaign army (1796)",
        "campaign_bounded_pashalik_army",
        "Scutari, Zeta valley, and Old Montenegro",
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_historical_lexicon_krusi",
            "wave8_montenegro_national_museum_history",
        ],
        (
            "Bounded to Kara Mahmud Pasha Bushatli's Scutari-led invasion armies "
            "opposed at Martinići and Krusi in 1796. It is not every Ottoman unit "
            "or every force of the Scutari pashalik in another year."
        ),
    ),
)


WAVE8_MONTENEGRO_1796_ROW_HASHES: dict[str, str] = {
    "hced-Cevo1768-1": "69eb2d4b6c218aba38b65b2b5f08289c2215fa92ccd5c719c4b6776020a6183b",
    "hced-Krusi1796-1": "87c3703195d0cedfb683d3c84fa3572d5e17134787497b3ebf3a264e983f419b",
    "hced-Martinici1796-1": "8ea09ffacc9e9876c5108b4fc60ef46aea33e8401e9e99f24834dbcb08a0fe77",
    "hced-Podgoritza1712-1": "9c854f0b522fd10d3150c078ef36415b7770006e8bc41c316654917ff4dd5980",
}

WAVE8_MONTENEGRO_1796_EXPECTED_EXACT_LABEL_IDS = frozenset(
    {
        "hced-Cevo1768-1",
        "hced-Fundina1876-1",
        "hced-Grahovo1858-1",
        "hced-Krusi1796-1",
        "hced-Martinici1796-1",
        "hced-Mojkovac1916-1",
        "hced-Ostrog1853-1",
        "hced-Podgoritza1712-1",
        "hced-Rijeka1862-1",
        "hced-Vucji Do1876-1",
    }
)

_ALREADY_PROMOTED_BASELINE_IDS = frozenset(
    {
        "hced-Fundina1876-1",
        "hced-Grahovo1858-1",
        "hced-Ostrog1853-1",
        "hced-Rijeka1862-1",
        "hced-Vucji Do1876-1",
    }
)
_EXISTING_CURATED_EXCLUSION_IDS = frozenset({"hced-Mojkovac1916-1"})

WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": ["clio_q236_1853_31d59baa"],
    "event_candidate_id_sha256": (
        "43d2d5fa715e71c6a7f6cfa5f676a09c029767633fd254b773a1215e826221a4"
    ),
    "events_touched": 4,
    "label": _EXACT_LABEL,
    "one_wrong_interval_candidates": 4,
    "sole_blocker_events": 3,
}


def _canonical(
    name: str,
    date_text: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1796:1796",
        "date_precision": "day",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1796,
        "year_high": 1796,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_MONTENEGRO_1796_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "montenegro_scutari_campaigns_1796",
        "side_1_entity_ids": [_MONTENEGRIN_FORCE_ID],
        "side_2_entity_ids": [_SCUTARI_FORCE_ID],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
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
        "actor_override": "candidate_keyed_campaign_bounded_opposing_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_MONTENEGRO_1796_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Martinici1796-1": _contract(
        "hced-Martinici1796-1",
        _canonical(
            "Battle of Martinići",
            "11 July 1796 Old Style / 22 July 1796 New Style",
            "single_battle_against_scutari_invasion_army",
        ),
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_belgrade_law_1796",
            "wave8_montenegro_historical_lexicon_krusi",
            "wave8_montenegro_national_museum_history",
            "wave8_montenegro_petar_speeches_1796",
        ],
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_belgrade_law_1796",
            "wave8_montenegro_historical_lexicon_krusi",
            "wave8_montenegro_national_museum_history",
        ],
        (
            "The official museum history and three independent scholarly families "
            "agree that Petar I's force defeated Kara Mahmud's first 1796 campaign "
            "at Martinići. The contract rates only that battle, not the later state-"
            "building consequence or the whole Montenegrin-Ottoman struggle."
        ),
        confidence=0.94,
    ),
    "hced-Krusi1796-1": _contract(
        "hced-Krusi1796-1",
        _canonical(
            "Battle of Krusi",
            "22 September 1796 Old Style / 3 October 1796 New Style",
            "single_battle_against_second_scutari_invasion_army",
        ),
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_belgrade_law_1796",
            "wave8_montenegro_historical_lexicon_krusi",
            "wave8_montenegro_national_museum_history",
            "wave8_montenegro_petar_speeches_1796",
        ],
        [
            "wave8_montenegro_balcanica_1796",
            "wave8_montenegro_belgrade_law_1796",
            "wave8_montenegro_historical_lexicon_krusi",
            "wave8_montenegro_national_museum_history",
        ],
        (
            "Independent scholarly and museum accounts agree that the second "
            "Scutari campaign was defeated at Krusi and Kara Mahmud Pasha was "
            "killed. Only the battlefield result is rated; no strategic termination "
            "of Ottoman-Montenegrin conflict is inferred."
        ),
        confidence=0.96,
    ),
}


WAVE8_MONTENEGRO_1796_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Podgoritza1712-1": {
        "raw_row_sha256": WAVE8_MONTENEGRO_1796_ROW_HASHES[
            "hced-Podgoritza1712-1"
        ],
        "cohort": "source_critical_holds",
        "disposition": "hold",
        "reason_code": "historically_contradictory_outcome_and_event_identity",
        "evidence_refs": [
            "wave8_montenegro_ucg_carev_laz_critique",
        ],
        "audit_note": (
            "HCED's place-only 'Podgoritza' row appears to encode the disputed "
            "1712 Carev Laz tradition as a categorical Montenegrin win. The 2024 "
            "University of Montenegro source-critical study finds that Venetian "
            "records do not support a great victory and that Ottoman forces reached "
            "Cetinje. Unknown or disputed is never converted into a win."
        ),
    },
    "hced-Cevo1768-1": {
        "raw_row_sha256": WAVE8_MONTENEGRO_1796_ROW_HASHES["hced-Cevo1768-1"],
        "cohort": "source_critical_holds",
        "disposition": "hold",
        "reason_code": "historically_contradictory_outcome_and_event_identity",
        "evidence_refs": [
            "wave8_montenegro_vakanuvis_scepan",
        ],
        "audit_note": (
            "HCED supplies only Čevo and the year. Ottoman-archival scholarship "
            "finds Šćepan Mali's army surrounded and defeated in the documented 5 "
            "September 1768 action, while broader campaign narratives contain "
            "several axes and phases. The row cannot be aligned to a unique "
            "Montenegrin victory without reversing or inventing an outcome."
        ),
    },
}

WAVE8_MONTENEGRO_1796_CONTRACT_IDS = frozenset(
    WAVE8_MONTENEGRO_1796_CONTRACTS
)
WAVE8_MONTENEGRO_1796_HOLD_IDS = frozenset(WAVE8_MONTENEGRO_1796_HOLDS)
WAVE8_MONTENEGRO_1796_RESERVED_IDS = frozenset(
    {*WAVE8_MONTENEGRO_1796_CONTRACT_IDS, *WAVE8_MONTENEGRO_1796_HOLD_IDS}
)

WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_MONTENEGRO_1796_CONTRACT_IDS
)
WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources identify the named battlefield and present-day "
            "country but do not independently verify HCED's exact coordinate; "
            "retain the Montenegro country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_MONTENEGRO_1796_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MONTENEGRO_1796_CONTRACTS,
        "entities": WAVE8_MONTENEGRO_1796_ENTITIES,
        "funnel": WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT,
        "holds": WAVE8_MONTENEGRO_1796_HOLDS,
        "location_reasons": WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_MONTENEGRO_1796_ROW_HASHES,
        "sources": WAVE8_MONTENEGRO_1796_SOURCES,
    }


def wave8_montenegro_1796_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE = (
    "2bf96ff247ffa0a3c8eb78ed4b0f27f48836714d5f771992b97ac73d003ddf0d"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_MONTENEGRO_1796_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_MONTENEGRO_1796_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_MONTENEGRO_1796_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if (
        WAVE8_MONTENEGRO_1796_CONTRACT_IDS
        & WAVE8_MONTENEGRO_1796_HOLD_IDS
    ):
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_MONTENEGRO_1796_RESERVED_IDS != set(
        WAVE8_MONTENEGRO_1796_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} reservation or row-hash drift")
    if WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_MONTENEGRO_1796_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point review incomplete")
    if WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_MONTENEGRO_1796_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_MONTENEGRO_1796_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")
    if (
        WAVE8_MONTENEGRO_1796_RESERVED_IDS
        | _ALREADY_PROMOTED_BASELINE_IDS
        | _EXISTING_CURATED_EXCLUSION_IDS
    ) != WAVE8_MONTENEGRO_1796_EXPECTED_EXACT_LABEL_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label disposition partition drift")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_MONTENEGRO_1796_ENTITIES:
        if entity["aliases"] or (
            entity["start_year"], entity["end_year"]
        ) != (1796, 1796):
            raise ValueError(f"{_LANE_NAME} entity escaped campaign boundary")
        entity_sources = list(map(str, entity["source_ids"]))
        if not entity_sources or not _is_sorted_unique(entity_sources):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(entity_sources) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity references unknown source")
        used_sources.update(entity_sources)

    for candidate_id, contract in WAVE8_MONTENEGRO_1796_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} contract disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} unexpected outcome override: {candidate_id}")
        for side_key in ("side_1_entity_ids", "side_2_entity_ids"):
            side = list(map(str, contract[side_key]))
            if not side or not set(side) <= set(entity_by_id):
                raise ValueError(f"{_LANE_NAME} unknown exact actor: {candidate_id}")
            used_entities.update(side)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence is not canonical: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_MONTENEGRO_1796_HOLDS.items():
        if hold["disposition"] != "hold" or not hold["reason_code"]:
            raise ValueError(f"{_LANE_NAME} hold disposition drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not evidence or not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} contains an unused entity fixture")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_montenegro_1796_audit_signature() != (
        WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_montenegro_1796_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_MONTENEGRO_1796_EXPECTED_EXACT_LABEL_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_MONTENEGRO_1796_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MONTENEGRO_1796_CONTRACTS,
        WAVE8_MONTENEGRO_1796_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "already_promoted_baseline_rows": len(_ALREADY_PROMOTED_BASELINE_IDS),
        "exact_label_rows": len(exact),
        "existing_curated_exclusion_rows": len(_EXISTING_CURATED_EXCLUSION_IDS),
    }


def validate_wave8_montenegro_1796_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    label = labels[0]
    checks = {
        "candidate_ids": list(map(str, label.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(label.get("event_candidate_id_sha256")),
        "events_touched": int(label.get("events_touched", -1)),
        "label": str(label.get("label")),
        "one_wrong_interval_candidates": int(
            label.get("failure_cases", {}).get("one_wrong_interval_candidate", -1)
        ),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
    }
    if checks != WAVE8_MONTENEGRO_1796_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "one_wrong_interval_candidates": checks["one_wrong_interval_candidates"],
        "sole_blocker_events": checks["sole_blocker_events"],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("name", "battle_name", "batname", "event_name"):
        value = normalize_label(row.get(key))
        if value:
            names.add(value)
    for value in row.get("aliases", []) or []:
        normalized = normalize_label(value)
        if normalized:
            names.add(normalized)
    return names


_RAW_EVENT_NAMES = {
    "hced-Martinici1796-1": {"Martinici", "Martinići", "Martinichi"},
    "hced-Krusi1796-1": {"Krusi", "Kruši", "Krusa", "Kruse"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1796, normalize_label(alias))
    for candidate_id, contract in WAVE8_MONTENEGRO_1796_CONTRACTS.items()
    for alias in {contract["canonical_event"]["name"], *_RAW_EVENT_NAMES[candidate_id]}
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_montenegro_1796_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_montenegro_1796_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_MONTENEGRO_1796_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_MONTENEGRO_1796_CONTRACT_IDS
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


def install_wave8_montenegro_1796_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MONTENEGRO_1796_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_montenegro_1796_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MONTENEGRO_1796_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_montenegro_1796_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_montenegro_1796_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MONTENEGRO_1796_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_montenegro_1796_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_MONTENEGRO_1796_CONTRACTS.values(),
                    *WAVE8_MONTENEGRO_1796_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_montenegro_1796_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_MONTENEGRO_1796_HOLDS),
        "new_entities": len(WAVE8_MONTENEGRO_1796_ENTITIES),
        "new_sources": len(WAVE8_MONTENEGRO_1796_SOURCES),
        "newly_rated_events": len(WAVE8_MONTENEGRO_1796_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MONTENEGRO_1796_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MONTENEGRO_1796_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_montenegro_1796_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_MONTENEGRO_1796_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MONTENEGRO_1796_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_montenegro_1796_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_montenegro_1796_counts(),
        "cohorts": wave8_montenegro_1796_cohort_counts(),
        "final_audit_signature": WAVE8_MONTENEGRO_1796_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_MONTENEGRO_1796_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_MONTENEGRO_1796_CONTRACT_IDS),
    }


_validate_static()
