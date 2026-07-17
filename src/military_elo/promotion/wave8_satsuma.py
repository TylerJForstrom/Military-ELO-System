"""Candidate-keyed Wave 8 audit for HCED's exact ``Satsuma`` label.

The locked snapshot contains seven exact-label rows.  ``Satsuma`` is not one
continuous military actor across them: the 1587 rows concern Shimazu and
Toyotomi campaign armies, the 1863 row concerns the Satsuma Domain's coastal
force, and the 1877 rows concern Saigo's extra-governmental rebel army after
the domains had been abolished.  This lane installs only time-bounded forces
and never transfers a rating among those identities or to modern Kagoshima.

Six source-supported engagements are promoted.  Kagoshima 1877 is terminally
excluded because its participant field names Shiroyama and the locked queue
contains a separate Shiroyama 1877 row for the same final engagement.  Emitting
both would double-rate one result.  Every promoted point is withheld because
the staged coordinate is a city/locality/river point rather than a
source-audited event footprint; the modern country value remains usable.
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
    "WAVE8_SATSUMA_CONTRACT_IDS",
    "WAVE8_SATSUMA_CONTRACTS",
    "WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_SATSUMA_ENTITIES",
    "WAVE8_SATSUMA_EXCLUSION_IDS",
    "WAVE8_SATSUMA_EXCLUSIONS",
    "WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_SATSUMA_HOLD_IDS",
    "WAVE8_SATSUMA_HOLDS",
    "WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS",
    "WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SATSUMA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SATSUMA_NONPROMOTIONS",
    "WAVE8_SATSUMA_OUTCOME_OVERRIDES",
    "WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SATSUMA_RESERVED_IDS",
    "WAVE8_SATSUMA_SOURCES",
    "WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SATSUMA_TERMINAL_EXCLUSIONS",
    "install_wave8_satsuma_entities",
    "install_wave8_satsuma_sources",
    "promote_wave8_satsuma_contracts",
    "validate_wave8_satsuma_integration_dispositions",
    "validate_wave8_satsuma_queue_contracts",
    "wave8_satsuma_audit_signature",
    "wave8_satsuma_cohort_counts",
    "wave8_satsuma_counts",
    "wave8_satsuma_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Satsuma actor audit"
_EVENT_ID_PREFIX = "hced_wave8_satsuma_"
_MODULE_OWNER = "military_elo.promotion.wave8_satsuma"
_SHIROYAMA_CANDIDATE_ID = "hced-Shiroyama1877-1"
_SHIROYAMA_RAW_ROW_SHA256 = (
    "8afa15c8db32ca76099ffdd8b8d03c180f5d7d361dac7824d84a6a5b92dfa4d3"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
    crosscheck: bool = True,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if outcome and crosscheck:
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


WAVE8_SATSUMA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_satsuma_iriki_documents",
        "The Documents of Iriki, no. 148: Hideyoshi's Demand of Hostages, 1592",
        "https://www.hi.u-tokyo.ac.jp/IRIKI/ETXT/eng_text148.html",
        "Historiographical Institute, University of Tokyo",
        "scholarly_translation_and_primary_document_apparatus",
        "tokyo_historiographical_institute_iriki_148",
    ),
    _source(
        "wave8_satsuma_kijo_takajo",
        "Second Battle of Takajo (Nejirozaka battlefield site)",
        (
            "https://www.town.kijo.lg.jp/sosikikarasagasu/"
            "kyouikuiinkai_kyouikuka/1_1/1/3299.html"
        ),
        "Kijo Town",
        "municipal_official_history",
        "kijo_official_second_takajo",
    ),
    _source(
        "wave8_satsuma_oita_otomo",
        "The later Otomo clan (Otomo-shi no sono go)",
        "https://www.city.oita.oita.jp/o205/documents/ootomosinosonogo.pdf",
        "Oita City",
        "municipal_official_history",
        "oita_city_otomo_history",
    ),
    _source(
        "wave8_satsuma_morton_sendai",
        "Japan: Its History and Culture",
        "https://books.google.com/books/about/Japan_Its_History_and_Culture.html?id=NC1bDncgKCQC",
        "McGraw-Hill Professional",
        "scholarly_historical_survey",
        "morton_olenik_japan_history_culture",
    ),
    _source(
        "wave8_satsuma_kagoshima_hideyoshi",
        "Hideyoshi's Kyushu expedition",
        "https://www.pref.kagoshima.jp/ab23/pr/gaiyou/rekishi/tyuusei/kyusyu.html",
        "Kagoshima Prefecture and Reimeikan",
        "prefectural_official_history",
        "kagoshima_reimeikan_hideyoshi_kyushu",
    ),
    _source(
        "wave8_satsuma_kagoshima_anglo",
        "Anglo-Satsuma War",
        "https://www.pref.kagoshima.jp/ab23/pr/gaiyou/rekishi/bakumatu/satuei.html",
        "Kagoshima Prefecture and Reimeikan",
        "prefectural_official_history",
        "kagoshima_reimeikan_anglo_satsuma",
    ),
    _source(
        "wave8_satsuma_cardiff_anglo",
        (
            "A 'New Diplomatic History' of Anglo-Japanese Relations: "
            "The Namamugi Incident and Anglo-Satsuma War"
        ),
        "https://orca.cardiff.ac.uk/id/eprint/169100/1/2024trullmphd.pdf",
        "Cardiff University",
        "doctoral_thesis",
        "trull_cardiff_anglo_japanese_relations",
    ),
    _source(
        "wave8_satsuma_jacar_domain",
        "Satsuma Domain",
        "https://www.jacar.archives.go.jp/das/term-en/00003293",
        "Japan Center for Asian Historical Records, National Archives of Japan",
        "national_archival_identity_reference",
        "jacar_satsuma_domain_term",
        outcome=False,
    ),
    _source(
        "wave8_satsuma_archives_domain_abolition",
        "Abolition of domains and establishment of prefectures",
        "https://www.archives.go.jp/ayumi/kobetsu/m04_1871_04.html",
        "National Archives of Japan",
        "national_archival_chronology",
        "national_archives_japan_haihan_chiken",
        outcome=False,
    ),
    _source(
        "wave8_satsuma_ndl_rebellion",
        "Satsuma Rebellion",
        "https://www.ndl.go.jp/modern/e/cha1/description11.html",
        "National Diet Library",
        "national_library_historical_reference",
        "ndl_satsuma_rebellion",
    ),
    _source(
        "wave8_satsuma_kumamoto_castle",
        "History of Kumamoto Castle",
        "https://castle.kumamoto-guide.jp/en/history/",
        "Kumamoto Castle official site",
        "municipal_official_site_history",
        "kumamoto_castle_official_history",
    ),
    _source(
        "wave8_satsuma_kumamoto_city",
        "Kumamoto City and the Satsuma Rebellion",
        "https://kumamoto-guide.jp/en/article/detail/366",
        "Kumamoto City Official Guide",
        "municipal_official_history",
        "kumamoto_city_satsuma_rebellion",
    ),
    _source(
        "wave8_satsuma_mlit_tabaruzaka",
        "Tabaruzaka Seinan Civil War Museum",
        "https://www.mlit.go.jp/tagengo-db/en/R2-02042.html",
        "Japan Tourism Agency, Ministry of Land, Infrastructure and Transport",
        "national_government_site_history",
        "japan_tourism_agency_tabaruzaka",
    ),
    _source(
        "wave8_satsuma_bunka_rebellion",
        "Satsuma Rebellion sites (Seinan Senso iseki)",
        "https://kunishitei.bunka.go.jp/heritage/detail/401/00003787",
        "Agency for Cultural Affairs, Government of Japan",
        "national_heritage_register_history",
        "agency_cultural_affairs_satsuma_rebellion_sites",
    ),
)


_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_SATSUMA_SOURCES}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


_SHIMAZU_1587_ID = "shimazu_kyushu_war_army_1586_1587"
_OTOMO_1587_ID = "otomo_bungo_army_1586_1587"
_TOYOTOMI_RELIEF_1587_ID = "toyotomi_shikoku_relief_contingent_1586_1587"
_TOYOTOMI_EXPEDITION_1587_ID = "toyotomi_kyushu_expedition_army_1587"
_SATSUMA_DOMAIN_1863_ID = "satsuma_domain_kagoshima_batteries_1863"
_SAIGO_REBELS_1877_ID = "saigo_satsuma_rebel_army_1877"
_UNITED_KINGDOM_ID = "united_kingdom"
_EMPIRE_JAPAN_ID = "empire_japan"


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_SATSUMA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _SHIMAZU_1587_ID,
        "Shimazu Kyushu campaign army (1586-1587)",
        "campaign_bounded_daimyo_army",
        1586,
        1587,
        "Kyushu, Japan",
        (
            "Bounded to the Shimazu campaign force in the Otomo-Toyotomi war. "
            "No rating is inherited by the 1863 Satsuma Domain force, the 1877 "
            "rebels, a clan or regional population generally, or modern Kagoshima."
        ),
        [
            "wave8_satsuma_iriki_documents",
            "wave8_satsuma_kagoshima_hideyoshi",
            "wave8_satsuma_kijo_takajo",
            "wave8_satsuma_oita_otomo",
        ],
    ),
    _entity(
        _OTOMO_1587_ID,
        "Otomo Bungo army in the Hetsugigawa campaign (1586-1587)",
        "campaign_bounded_daimyo_army",
        1586,
        1587,
        "Bungo Province, Kyushu, Japan",
        (
            "Bounded to the Otomo force opposing the Shimazu advance in Bungo. "
            "No rating is inherited by Bungo, Kyushu, an Otomo lineage generally, "
            "or any modern state or prefecture."
        ),
        ["wave8_satsuma_iriki_documents", "wave8_satsuma_oita_otomo"],
    ),
    _entity(
        _TOYOTOMI_RELIEF_1587_ID,
        "Toyotomi-Shikoku relief contingent at Hetsugigawa (1586-1587)",
        "campaign_bounded_relief_contingent",
        1586,
        1587,
        "Bungo Province, Kyushu, Japan",
        (
            "Bounded to the Shikoku commanders and troops sent to aid the Otomo "
            "at Hetsugigawa; Hideyoshi was not personally this battlefield actor. "
            "No rating is inherited by the later main expedition or modern Japan."
        ),
        ["wave8_satsuma_iriki_documents", "wave8_satsuma_oita_otomo"],
    ),
    _entity(
        _TOYOTOMI_EXPEDITION_1587_ID,
        "Toyotomi Kyushu expedition army (1587)",
        "campaign_bounded_expedition_army",
        1587,
        1587,
        "Kyushu, Japan",
        (
            "Bounded to the Toyotomi expedition and its operational columns in "
            "Kyushu during 1587. No rating is inherited by the Hetsugigawa relief "
            "contingent, Japan across eras, or the later Tokugawa polity."
        ),
        [
            "wave8_satsuma_iriki_documents",
            "wave8_satsuma_kagoshima_hideyoshi",
            "wave8_satsuma_kijo_takajo",
            "wave8_satsuma_morton_sendai",
        ],
    ),
    _entity(
        _SATSUMA_DOMAIN_1863_ID,
        "Satsuma Domain Kagoshima batteries and field force (1863)",
        "campaign_bounded_domain_force",
        1863,
        1863,
        "Kagoshima Bay, Satsuma Domain, Japan",
        (
            "Bounded to the domain batteries and troops engaged with the British "
            "squadron in 1863. No rating is inherited by the 1587 Shimazu army, "
            "the 1877 rebels, the abolished domain after 1871, or Kagoshima Prefecture."
        ),
        [
            "wave8_satsuma_archives_domain_abolition",
            "wave8_satsuma_jacar_domain",
            "wave8_satsuma_kagoshima_anglo",
        ],
    ),
    _entity(
        _SAIGO_REBELS_1877_ID,
        "Saigo-led Satsuma rebel army (1877)",
        "campaign_bounded_rebel_army",
        1877,
        1877,
        "Kyushu, Japan",
        (
            "Bounded to Saigo Takamori's private-school and former-samurai rebel "
            "army in 1877. The domains had been abolished in 1871; no rating is "
            "inherited from the Satsuma Domain, its population, or modern Kagoshima."
        ),
        [
            "wave8_satsuma_archives_domain_abolition",
            "wave8_satsuma_bunka_rebellion",
            "wave8_satsuma_kumamoto_city",
            "wave8_satsuma_ndl_rebellion",
        ],
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Kagoshima1863-1": (
        "6bee09eb88e940e057c9ec14aee79864cc0c4994d596fc87508c4e6cf4da236e"
    ),
    "hced-Kagoshima1877-1": (
        "e77f5c4f437e05c55403d16fdc81e38ef10d8dbee6f8d6d196863375e6a2216c"
    ),
    "hced-Kumamoto1877-1": (
        "59fc818753c71c76b8852fefacb0e0d46b4417790829d0bad0f0e327bbdd1b04"
    ),
    "hced-Sendaigawa1587-1": (
        "e24d408a3dbb99c45f9c476b53725ab501ec6168036319735c0d1193bce925d1"
    ),
    "hced-Tabaruzaka1877-1": (
        "83efe46bc348b667b504b51151fe7d99e9ef3672c60c87c76adb91c10bb9e5b2"
    ),
    "hced-Takashiro1587-1": (
        "a5a93f1cc2b70a99405c7f7bfe4b8b4364626bcd0b69d92dbd12e8de5c51f4f4"
    ),
    "hced-Toshimitsu1587-1": (
        "f36557443b419ea5c254eedc7c068fd6af35709f855a7213acd7eac235d0ad78"
    ),
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "name": name,
        "year": year,
        "year_low": year,
        "year_high": year,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:{year}:{year}",
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    event_boundary: str,
    war_type: str,
    confidence: float,
    result_type: str = "win",
    winner_side: int | None = 1,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    contract: dict[str, Any] = {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1))),
        "side_2_entity_ids": sorted(set(map(str, side_2))),
        "result_type": result_type,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "direct_provenance": {
            "reviewed_date": canonical_event["date_text"],
            "reviewed_sides": list(map(str, reviewed_sides)),
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }
    if result_type == "win":
        contract["winner_side"] = winner_side
    return contract


WAVE8_SATSUMA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Toshimitsu1587-1": _contract(
        "hced-Toshimitsu1587-1",
        _canonical("Battle of Hetsugigawa (Toshimitsu)", 1587, "20 January 1587"),
        "shimazu_toyotomi_kyushu_campaign_1586_1587",
        [_SHIMAZU_1587_ID],
        [_OTOMO_1587_ID, _TOYOTOMI_RELIEF_1587_ID],
        ["wave8_satsuma_iriki_documents", "wave8_satsuma_oita_otomo"],
        ["wave8_satsuma_iriki_documents", "wave8_satsuma_oita_otomo"],
        (
            "The Shimazu vanguard defeated the Otomo and Toyotomi-Shikoku relief "
            "coalition at Hetsugigawa. HCED's comma-separated losing side is kept "
            "as two bounded participants; Hideyoshi is not made a personal combatant."
        ),
        reviewed_sides=[
            "Shimazu Kyushu campaign army",
            "Otomo army and Toyotomi-Shikoku relief contingent",
        ],
        reviewed_outcome="Shimazu tactical victory",
        event_boundary="field battle at Hetsugigawa/Toshimitsu",
        war_type="civil_war",
        confidence=0.94,
    ),
    "hced-Takashiro1587-1": _contract(
        "hced-Takashiro1587-1",
        _canonical(
            "Second Battle of Takajo (Nejirozaka)",
            1587,
            "1587",
            date_precision="year",
        ),
        "shimazu_toyotomi_kyushu_campaign_1586_1587",
        [_TOYOTOMI_EXPEDITION_1587_ID],
        [_SHIMAZU_1587_ID],
        [
            "wave8_satsuma_iriki_documents",
            "wave8_satsuma_kagoshima_hideyoshi",
            "wave8_satsuma_kijo_takajo",
        ],
        ["wave8_satsuma_iriki_documents", "wave8_satsuma_kijo_takajo"],
        (
            "The Toyotomi besieging army repelled the Shimazu relief attack at "
            "Nejirozaka and forced its retreat. The raw 'Toyotomo Hideyoshi' label "
            "is resolved to the bounded expedition, not Hideyoshi personally."
        ),
        reviewed_sides=["Toyotomi Kyushu expedition", "Shimazu relief army"],
        reviewed_outcome="Toyotomi tactical victory and Shimazu retreat",
        event_boundary="second Takajo battle and Nejirozaka relief attack",
        war_type="civil_war",
        confidence=0.94,
    ),
    "hced-Sendaigawa1587-1": _contract(
        "hced-Sendaigawa1587-1",
        _canonical(
            "Battle near the Sendai River",
            1587,
            "1587",
            date_precision="year",
        ),
        "shimazu_toyotomi_kyushu_campaign_1586_1587",
        [_TOYOTOMI_EXPEDITION_1587_ID],
        [_SHIMAZU_1587_ID],
        [
            "wave8_satsuma_iriki_documents",
            "wave8_satsuma_kagoshima_hideyoshi",
            "wave8_satsuma_morton_sendai",
        ],
        [
            "wave8_satsuma_iriki_documents",
            "wave8_satsuma_kagoshima_hideyoshi",
            "wave8_satsuma_morton_sendai",
        ],
        (
            "The reviewed histories support a Toyotomi victory on the Sendai "
            "approach before Shimazu submission. Precision remains at year because "
            "the sources do not support a single exact day for HCED's label."
        ),
        reviewed_sides=["Toyotomi Kyushu expedition", "Shimazu campaign army"],
        reviewed_outcome="Toyotomi tactical victory on the Sendai approach",
        event_boundary="battle near the Sendai River, not the later surrender itself",
        war_type="civil_war",
        confidence=0.86,
    ),
    "hced-Kagoshima1863-1": _contract(
        "hced-Kagoshima1863-1",
        _canonical(
            "Bombardment of Kagoshima",
            1863,
            "15-17 August 1863",
            date_precision="day_range",
            granularity="naval_bombardment_and_shore_action",
        ),
        "anglo_satsuma_war_1863",
        [_UNITED_KINGDOM_ID],
        [_SATSUMA_DOMAIN_1863_ID],
        [
            "wave8_satsuma_cardiff_anglo",
            "wave8_satsuma_jacar_domain",
            "wave8_satsuma_kagoshima_anglo",
        ],
        ["wave8_satsuma_cardiff_anglo", "wave8_satsuma_kagoshima_anglo"],
        (
            "Both reviewed source families characterize the immediate fighting as "
            "even or inconclusive. This preserves HCED's explicit Draw without "
            "inventing a tactical winner from later diplomatic consequences."
        ),
        reviewed_sides=[
            "British naval squadron",
            "Satsuma Domain Kagoshima batteries and field force",
        ],
        reviewed_outcome="inconclusive immediate engagement (draw)",
        event_boundary="British bombardment, Satsuma shore fire, and immediate action",
        war_type="interstate_limited",
        confidence=0.91,
        result_type="draw",
        winner_side=None,
    ),
    "hced-Kumamoto1877-1": _contract(
        "hced-Kumamoto1877-1",
        _canonical(
            "Siege of Kumamoto Castle",
            1877,
            "19 February-12 April 1877",
            date_precision="day_range",
            granularity="siege",
        ),
        "satsuma_rebellion_1877",
        [_EMPIRE_JAPAN_ID],
        [_SAIGO_REBELS_1877_ID],
        [
            "wave8_satsuma_kumamoto_castle",
            "wave8_satsuma_kumamoto_city",
            "wave8_satsuma_ndl_rebellion",
        ],
        ["wave8_satsuma_kumamoto_castle", "wave8_satsuma_kumamoto_city"],
        (
            "The imperial garrison held Kumamoto Castle through the rebel siege, "
            "which ended after relief. The opponent is Saigo's 1877 rebel army, "
            "not the Satsuma Domain abolished six years earlier."
        ),
        reviewed_sides=["Imperial Japanese garrison", "Saigo-led rebel army"],
        reviewed_outcome="imperial defensive victory; castle not captured",
        event_boundary="siege of Kumamoto Castle",
        war_type="civil_war",
        confidence=0.97,
    ),
    "hced-Tabaruzaka1877-1": _contract(
        "hced-Tabaruzaka1877-1",
        _canonical(
            "Battle of Tabaruzaka",
            1877,
            "March 1877",
            date_precision="month",
        ),
        "satsuma_rebellion_1877",
        [_EMPIRE_JAPAN_ID],
        [_SAIGO_REBELS_1877_ID],
        [
            "wave8_satsuma_bunka_rebellion",
            "wave8_satsuma_kumamoto_city",
            "wave8_satsuma_mlit_tabaruzaka",
        ],
        [
            "wave8_satsuma_bunka_rebellion",
            "wave8_satsuma_kumamoto_city",
            "wave8_satsuma_mlit_tabaruzaka",
        ],
        (
            "Government forces broke the rebel position at Tabaruzaka. The date is "
            "kept at month precision because official references differ by one day "
            "on the opening boundary; HCED's misspelled 'Tabaruzak' remains an alias."
        ),
        reviewed_sides=["Imperial Japanese army", "Saigo-led rebel army"],
        reviewed_outcome="imperial tactical victory and rebel retreat",
        event_boundary="multi-day battle across the Tabaruzaka position",
        war_type="civil_war",
        confidence=0.97,
    ),
}


WAVE8_SATSUMA_HOLDS: dict[str, dict[str, Any]] = {}


WAVE8_SATSUMA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Kagoshima1877-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Kagoshima1877-1"],
        "canonical_event": _canonical(
            "Battle of Shiroyama",
            1877,
            "24 September 1877",
            date_precision="day",
        ),
        "cohort": "satsuma_rebellion_1877",
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": "same_event_duplicate_and_place_conflation",
        "reviewed_outcome": (
            "Imperial victory over the surviving Saigo-led rebel force at Shiroyama"
        ),
        "reviewed_actor_description": [
            "Empire of Japan assault force",
            "surviving Saigo-led Satsuma rebel force",
        ],
        "reviewed_granularity": "duplicate_final_engagement_assertion",
        "hold_reason": (
            "The Kagoshima row's participant field explicitly names Shiroyama, and "
            "the same locked snapshot contains hced-Shiroyama1877-1 for the final "
            "24 September engagement. No independent Kagoshima battle is identified. "
            "Emitting both would double-rate one imperial victory, so this exact-label "
            "row is terminally excluded and the Shiroyama row remains cross-lane."
        ),
        "evidence_refs": sorted(
            ["wave8_satsuma_bunka_rebellion", "wave8_satsuma_ndl_rebellion"]
        ),
        "full_row_audited": True,
        "duplicate_of_hced_candidate_id": _SHIROYAMA_CANDIDATE_ID,
        "duplicate_raw_row_sha256": _SHIROYAMA_RAW_ROW_SHA256,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_duplicate_exclusion",
        },
    }
}


WAVE8_SATSUMA_EXCLUSIONS = WAVE8_SATSUMA_TERMINAL_EXCLUSIONS
WAVE8_SATSUMA_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SATSUMA_HOLDS,
    **WAVE8_SATSUMA_TERMINAL_EXCLUSIONS,
}

WAVE8_SATSUMA_CONTRACT_IDS = frozenset(WAVE8_SATSUMA_CONTRACTS)
WAVE8_SATSUMA_HOLD_IDS = frozenset(WAVE8_SATSUMA_HOLDS)
WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_SATSUMA_TERMINAL_EXCLUSIONS
)
WAVE8_SATSUMA_EXCLUSION_IDS = WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS
WAVE8_SATSUMA_RESERVED_IDS = (
    WAVE8_SATSUMA_CONTRACT_IDS
    | WAVE8_SATSUMA_HOLD_IDS
    | WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS
)
WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Kagoshima1877-1": {
        "source_dataset": "hced",
        "related_hced_candidate_id": _SHIROYAMA_CANDIDATE_ID,
        "disposition": "terminally_exclude_duplicate_from_exact_label_lane",
        "relationship": "same_final_engagement_same_year_same_outcome",
        "raw_row_sha256": _ROW_HASHES["hced-Kagoshima1877-1"],
        "related_raw_row_sha256": _SHIROYAMA_RAW_ROW_SHA256,
        "evidence_refs": sorted(
            ["wave8_satsuma_bunka_rebellion", "wave8_satsuma_ndl_rebellion"]
        ),
        "reason": (
            "The Kagoshima row names Shiroyama in its participants and has no "
            "separate engagement boundary; retain only the separately staged "
            "Shiroyama assertion for its own actor-label review."
        ),
    }
}


# Shiroyama is fingerprinted to pin the duplicate boundary.  It is not a
# reservation, contract, entity dependency, or promotion in this exact-label lane.
WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _SHIROYAMA_CANDIDATE_ID: {
        "source_dataset": "hced",
        "disposition": "cross_lane_candidate_pending_actor_review",
        "owner_module": None,
        "raw_row_sha256": _SHIROYAMA_RAW_ROW_SHA256,
        "related_excluded_candidate_id": "hced-Kagoshima1877-1",
        "relationship": "canonical_same_event_candidate_for_terminal_duplicate",
        "reason": (
            "The row uses the distinct exact actor label 'Saiga Takamori' and is "
            "outside this lane. It is fingerprinted but neither claimed nor rated "
            "here; a separate actor-label review must correct that spelling and "
            "adjudicate the Shiroyama contract."
        ),
    }
}


WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
    **WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}
WAVE8_SATSUMA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


# Every promoted point is a generic city, locality, castle, or river lookup and
# is too precise for the reviewed event footprint.  Modern country remains Japan.
WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS = frozenset(WAVE8_SATSUMA_CONTRACT_IDS)
WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SATSUMA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Toshimitsu1587-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The locality coordinate is not a source-audited Hetsugigawa battlefield "
            "footprint and would imply unsupported point precision."
        ),
    },
    "hced-Takashiro1587-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Takashiro locality/castle lookup is not a source-audited point for "
            "the Nejirozaka battle position."
        ),
    },
    "hced-Sendaigawa1587-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A single generic Sendai River lookup cannot represent the reviewed "
            "approach engagement and is not source-audited to its battlefield."
        ),
    },
    "hced-Kagoshima1863-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Kagoshima city point cannot represent the bay, British squadron, "
            "shore batteries, and dispersed bombardment footprint."
        ),
    },
    "hced-Kumamoto1877-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged value is a city centroid rather than a source-audited castle "
            "or siege footprint."
        ),
    },
    "hced-Tabaruzaka1877-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The multi-day battlefield spans hillsides and a valley; one staged "
            "point would overstate the reviewed event's location precision."
        ),
    },
}


WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Toshimitsu1587-1": {
        "aliases": sorted(
            {
                "battle of hetsugigawa",
                "battle of hetsugigawa toshimitsu",
                "battle of toshimitsu",
                "hetsugigawa",
                "toshimitsu",
            }
        ),
        "years": [1587, 1587],
    },
    "hced-Takashiro1587-1": {
        "aliases": sorted(
            {
                "battle of nejirozaka",
                "nejirozaka",
                "second battle of takajo nejirozaka",
                "second battle of takajo",
                "takajo",
                "takashiro",
            }
        ),
        "years": [1587, 1587],
    },
    "hced-Sendaigawa1587-1": {
        "aliases": sorted(
            {
                "battle near the sendai river",
                "battle of sendaigawa",
                "sendai river",
                "sendaigawa",
            }
        ),
        "years": [1587, 1587],
    },
    "hced-Kagoshima1863-1": {
        "aliases": sorted(
            {
                "anglo satsuma war",
                "bombardment of kagoshima",
                "british satsuma war",
                "kagoshima",
            }
        ),
        "years": [1863, 1863],
    },
    "hced-Kagoshima1877-1": {
        "aliases": sorted(
            {"battle of shiroyama", "kagoshima", "shiroyama"}
        ),
        "years": [1877, 1877],
    },
    "hced-Kumamoto1877-1": {
        "aliases": sorted(
            {"kumamoto", "kumamoto castle", "siege of kumamoto castle"}
        ),
        "years": [1877, 1877],
    },
    "hced-Tabaruzaka1877-1": {
        "aliases": sorted(
            {"battle of tabaruzaka", "tabaruzak", "tabaruzaka"}
        ),
        "years": [1877, 1877],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SATSUMA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_SATSUMA_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS),
        "hced_duplicate_dispositions": WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS,
        "holds": WAVE8_SATSUMA_HOLDS,
        "integration_dispositions": WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_SATSUMA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS),
        "sources": WAVE8_SATSUMA_SOURCES,
        "terminal_exclusions": WAVE8_SATSUMA_TERMINAL_EXCLUSIONS,
    }


def wave8_satsuma_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


# Patched to the measured payload after all fixtures and dispositions are final.
WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE = (
    "719ebd1ac11732998e2a2b2490b055518e3da616596fa2c859d366825fa92076"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SATSUMA_CONTRACTS),
        len(WAVE8_SATSUMA_HOLDS),
        len(WAVE8_SATSUMA_TERMINAL_EXCLUSIONS),
        len(WAVE8_SATSUMA_ENTITIES),
        len(WAVE8_SATSUMA_SOURCES),
    ) != (6, 0, 1, 6, 14):
        raise ValueError(f"{_LANE_NAME} fixture or disposition inventory changed")
    if WAVE8_SATSUMA_RESERVED_IDS != WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if WAVE8_SATSUMA_EXCLUSIONS is not WAVE8_SATSUMA_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if set(WAVE8_SATSUMA_NONPROMOTIONS) != (
        WAVE8_SATSUMA_HOLD_IDS | WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS
    ):
        raise ValueError(f"{_LANE_NAME} nonpromotion inventory drifted")
    dispositions = (
        WAVE8_SATSUMA_CONTRACT_IDS,
        WAVE8_SATSUMA_HOLD_IDS,
        WAVE8_SATSUMA_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_satsuma_audit_signature() != WAVE8_SATSUMA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_SATSUMA_SOURCES}
    if len(source_by_id) != len(WAVE8_SATSUMA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_SATSUMA_SOURCES}) != len(
        WAVE8_SATSUMA_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_SATSUMA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if source["accessed"] != "2026-07-16":
            raise ValueError(f"{_LANE_NAME} source access date drifted")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SATSUMA_ENTITIES}
    if len(entity_by_id) != len(WAVE8_SATSUMA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_SATSUMA_ENTITIES:
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity window is inverted")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in {"satsuma", "shimazu"}:
            raise ValueError(f"{_LANE_NAME} installed a generic actor identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    known_windows: dict[str, tuple[int, int | None]] = {
        entity_id: (int(entity["start_year"]), int(entity["end_year"]))
        for entity_id, entity in entity_by_id.items()
    }
    known_windows[_UNITED_KINGDOM_ID] = (1707, None)
    known_windows[_EMPIRE_JAPAN_ID] = (1868, 1947)
    expected_results = {
        "hced-Toshimitsu1587-1": ("win", 1),
        "hced-Takashiro1587-1": ("win", 1),
        "hced-Sendaigawa1587-1": ("win", 1),
        "hced-Kagoshima1863-1": ("draw", None),
        "hced-Kumamoto1877-1": ("win", 1),
        "hced-Tabaruzaka1877-1": ("win", 1),
    }
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_SATSUMA_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        low, high = int(canonical["year_low"]), int(canonical["year_high"])
        expected_key = f"{_slug(str(canonical['name']))}:{low}:{high}"
        if (
            low != high
            or int(canonical["year"]) != low
            or canonical["canonical_key"] != expected_key
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        for entity_id in set(side_1) | set(side_2):
            if entity_id not in known_windows:
                raise ValueError(f"{_LANE_NAME} uses an unknown actor identity")
            start, end = known_windows[entity_id]
            if start > low or (end is not None and end < high):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))
        actual_result = (contract["result_type"], contract.get("winner_side"))
        if actual_result != expected_results[candidate_id]:
            raise ValueError(f"{_LANE_NAME} outcome disposition drifted")
        if (
            contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} global outcome policy drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        direct = contract["direct_provenance"]
        if set(direct) != {
            "event_boundary",
            "reviewed_date",
            "reviewed_outcome",
            "reviewed_sides",
        } or not all(direct.values()):
            raise ValueError(f"{_LANE_NAME} direct provenance drifted")
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
            raise ValueError(f"{_LANE_NAME} outcome provenance is not independent")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    if WAVE8_SATSUMA_HOLDS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited hold")

    exclusion = WAVE8_SATSUMA_TERMINAL_EXCLUSIONS["hced-Kagoshima1877-1"]
    forbidden = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    if (
        exclusion["raw_row_sha256"] != _ROW_HASHES["hced-Kagoshima1877-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["full_row_audited"] is not True
        or exclusion["duplicate_of_hced_candidate_id"] != _SHIROYAMA_CANDIDATE_ID
        or exclusion["duplicate_raw_row_sha256"] != _SHIROYAMA_RAW_ROW_SHA256
        or forbidden & set(exclusion)
    ):
        raise ValueError(f"{_LANE_NAME} terminal duplicate exclusion drifted")
    exclusion_evidence = set(map(str, exclusion["evidence_refs"]))
    if not exclusion_evidence <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} exclusion evidence drifted")
    used_sources.update(exclusion_evidence)

    duplicate = WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS.get(
        "hced-Kagoshima1877-1"
    )
    if (
        duplicate is None
        or duplicate["raw_row_sha256"] != _ROW_HASHES["hced-Kagoshima1877-1"]
        or duplicate["related_hced_candidate_id"] != _SHIROYAMA_CANDIDATE_ID
        or duplicate["related_raw_row_sha256"] != _SHIROYAMA_RAW_ROW_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} HCED duplicate disposition drifted")
    used_sources.update(map(str, duplicate["evidence_refs"]))

    cross_lane = WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS
    if set(cross_lane) != {_SHIROYAMA_CANDIDATE_ID}:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory drifted")
    shiroyama = cross_lane[_SHIROYAMA_CANDIDATE_ID]
    if (
        shiroyama["raw_row_sha256"] != _SHIROYAMA_RAW_ROW_SHA256
        or shiroyama["related_excluded_candidate_id"] != "hced-Kagoshima1877-1"
        or shiroyama["disposition"] != "cross_lane_candidate_pending_actor_review"
        or shiroyama["owner_module"] is not None
    ):
        raise ValueError(f"{_LANE_NAME} Shiroyama boundary drifted")
    if (
        WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_SATSUMA_OUTCOME_OVERRIDES
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS != cross_lane:
        raise ValueError(f"{_LANE_NAME} integration disposition union drifted")

    used_sources.update(
        source_id
        for entity in WAVE8_SATSUMA_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS != WAVE8_SATSUMA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location review inventory changed")
    for review in WAVE8_SATSUMA_LOCATION_QUARANTINE_REASONS.values():
        if review["actions"] != ["withhold_point"] or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} location review drifted")

    if set(WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if (
            not aliases
            or not _is_sorted_unique(aliases)
            or any(alias != normalize_label(alias) for alias in aliases)
            or years != [years[0], years[0]]
        ):
            raise ValueError(f"{_LANE_NAME} duplicate negative audit drifted")
        disposition = WAVE8_SATSUMA_CONTRACTS.get(candidate_id) or (
            WAVE8_SATSUMA_NONPROMOTIONS.get(candidate_id)
        )
        canonical = disposition["canonical_event"]
        if normalize_label(canonical["name"]) not in aliases:
            raise ValueError(f"{_LANE_NAME} canonical duplicate alias is missing")


def _is_exact_satsuma_label(value: Any) -> bool:
    return normalize_label(value) == "satsuma"


def validate_wave8_satsuma_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all seven exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SATSUMA_CONTRACTS,
        WAVE8_SATSUMA_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_satsuma_label(row.get("side_1_raw"))
        or _is_exact_satsuma_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Satsuma inventory changed: {sorted(exact_label_ids)}"
        )
    return {
        "holds": len(WAVE8_SATSUMA_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_SATSUMA_TERMINAL_EXCLUSIONS),
    }


def _row_year_range(row: Mapping[str, Any]) -> tuple[int, int] | None:
    low = row.get("year_low")
    high = row.get("year_high")
    try:
        if low is not None and high is not None:
            return int(low), int(high)
    except (TypeError, ValueError):
        pass
    for field in ("year", "year_best"):
        value = row.get(field)
        try:
            if value is not None:
                year = int(value)
                return year, year
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                year = -year if value.startswith("-") else year
                return year, year
    return None


def _normalized_event_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases", [])
    if isinstance(aliases, (list, tuple)):
        names.update(normalize_label(alias) for alias in aliases)
    return {name for name in names if name}


def _find_unreviewed_overlap(
    rows: Iterable[Mapping[str, Any]],
    *,
    skip_ids: frozenset[str] = frozenset(),
) -> tuple[str, str] | None:
    for row in rows:
        row_id = str(
            row.get("candidate_id") or row.get("id") or row.get("source_row") or "unknown"
        )
        if row_id in skip_ids:
            continue
        years = _row_year_range(row)
        if years is None:
            continue
        names = _normalized_event_names(row)
        for candidate_id, audit in WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT.items():
            audit_years = tuple(map(int, audit["years"]))
            aliases = set(map(str, audit["aliases"]))
            if (
                years[0] <= audit_years[1]
                and years[1] >= audit_years[0]
                and names & aliases
            ):
                return row_id, candidate_id
    return None


def validate_wave8_satsuma_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin Shiroyama and fail closed on future HCED, IWBD, or release twins."""

    validate_wave8_satsuma_queue_contracts(hced_rows)
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    shiroyama_rows = indexed.get(_SHIROYAMA_CANDIDATE_ID, [])
    if len(shiroyama_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one cross-lane Shiroyama row, "
            f"found {len(shiroyama_rows)}"
        )
    if canonical_hced_row_sha256(shiroyama_rows[0]) != _SHIROYAMA_RAW_ROW_SHA256:
        raise ValueError(f"{_LANE_NAME} cross-lane Shiroyama fingerprint changed")

    hced_overlap = _find_unreviewed_overlap(
        hced_rows,
        skip_ids=frozenset(
            {*WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS, _SHIROYAMA_CANDIDATE_ID}
        ),
    )
    if hced_overlap:
        raise ValueError(
            f"{_LANE_NAME} found unreviewed cross-lane HCED twin "
            f"{hced_overlap[0]} for {hced_overlap[1]}"
        )
    iwbd_overlap = _find_unreviewed_overlap(iwbd_rows)
    if iwbd_overlap:
        raise ValueError(
            f"{_LANE_NAME} found plausible IWBD overlap "
            f"{iwbd_overlap[0]} for {iwbd_overlap[1]}"
        )
    existing_list = list(existing_events)
    release_skip = frozenset(
        str(event.get("id"))
        for event in existing_list
        if event.get("hced_candidate_id") in WAVE8_SATSUMA_CONTRACT_IDS
    )
    release_overlap = _find_unreviewed_overlap(existing_list, skip_ids=release_skip)
    if release_overlap:
        raise ValueError(
            f"{_LANE_NAME} found existing-release duplicate "
            f"{release_overlap[0]} for {release_overlap[1]}"
        )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT),
    }


def install_wave8_satsuma_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SATSUMA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_satsuma_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SATSUMA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_satsuma_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit only the six signed promotion contracts, with local quarantine."""

    validate_wave8_satsuma_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SATSUMA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_satsuma_cohort_counts() -> dict[str, int]:
    """Return counts for all seven reviewed rows, including the exclusion."""

    _validate_static()
    return dict(
        sorted(
            Counter(
                str(disposition["cohort"])
                for disposition in (
                    *WAVE8_SATSUMA_CONTRACTS.values(),
                    *WAVE8_SATSUMA_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_satsuma_counts() -> dict[str, int]:
    """Return stable lane metadata for release orchestration and audits."""

    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_SATSUMA_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_SATSUMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_SATSUMA_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_SATSUMA_HOLDS),
        "integration_dispositions": len(WAVE8_SATSUMA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_SATSUMA_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_SATSUMA_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_SATSUMA_ENTITIES),
        "new_sources": len(WAVE8_SATSUMA_SOURCES),
        "newly_rated_events": len(WAVE8_SATSUMA_CONTRACTS),
        "outcome_overrides": len(WAVE8_SATSUMA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_SATSUMA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SATSUMA_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_SATSUMA_TERMINAL_EXCLUSIONS),
    }


def wave8_satsuma_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return a copy-safe declaration of the lane-local location withholding."""

    _validate_static()
    return {
        "country": WAVE8_SATSUMA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SATSUMA_POINT_QUARANTINE_ADDITIONS,
    }
