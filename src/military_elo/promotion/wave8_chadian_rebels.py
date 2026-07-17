"""Isolated Wave 8 audit for the exact HCED label ``Chadian Rebels``.

Six HCED rows use the exact normalized label.  Two mechanically adjacent
spellings (``Northern Chadian Rebels`` and the compound ``Libya, North
Chadian Rebels``) are also reserved so that another lane cannot split the
same audit by spelling alone.  Ati (1978) and the two N'Djamena rows
(1979/1980) have independently corroborated, event-bounded outcomes.  The
remaining five rows are holds: their year/place labels collapse distinct
captures, recaptures, campaign phases, or contradictory source outcomes.

No hold is converted to a draw and no generic Chadian rebel, FROLINAT, FAN,
FAP, GUNT, government, French, or Libyan actor is installed.  Every emitted
identity is bounded to one reviewed event and one year.  The 1980 N'Djamena
row is an operational urban campaign; the lane does not misstate it as one
point engagement or inherit its result from the wider civil war.
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
    "WAVE8_CHADIAN_REBELS_ADJACENT_CANDIDATE_IDS",
    "WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES",
    "WAVE8_CHADIAN_REBELS_CONTRACT_IDS",
    "WAVE8_CHADIAN_REBELS_CONTRACTS",
    "WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES",
    "WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS",
    "WAVE8_CHADIAN_REBELS_ENTITIES",
    "WAVE8_CHADIAN_REBELS_EXACT_CANDIDATE_IDS",
    "WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES",
    "WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256",
    "WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS",
    "WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256",
    "WAVE8_CHADIAN_REBELS_HOLD_IDS",
    "WAVE8_CHADIAN_REBELS_HOLDS",
    "WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256",
    "WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CHADIAN_REBELS_NONPROMOTIONS",
    "WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CHADIAN_REBELS_RESERVED_IDS",
    "WAVE8_CHADIAN_REBELS_ROW_HASHES",
    "WAVE8_CHADIAN_REBELS_SOURCES",
    "WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS",
    "WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS",
    "WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256",
    "install_wave8_chadian_rebels_entities",
    "install_wave8_chadian_rebels_sources",
    "promote_wave8_chadian_rebels_contracts",
    "validate_wave8_chadian_rebels_funnel",
    "validate_wave8_chadian_rebels_integration_dispositions",
    "validate_wave8_chadian_rebels_queue_contracts",
    "wave8_chadian_rebels_audit_signature",
    "wave8_chadian_rebels_cohort_counts",
    "wave8_chadian_rebels_counts",
    "wave8_chadian_rebels_location_quarantine_additions",
    "wave8_chadian_rebels_metadata",
)


_LANE_NAME = "Wave 8 Chadian Rebels exact-force audit"
_MODULE_OWNER = "military_elo.promotion.wave8_chadian_rebels"
_EVENT_ID_PREFIX = "hced_wave8_chadian_rebels_"
_EXACT_LABEL = "chadian rebels"
_ADJACENT_LABELS = frozenset(
    {"northern chadian rebels", "libya north chadian rebels"}
)


WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256: dict[str, str] = {
    "ucdp-conflict-26.1-candidates.jsonl": (
        "cbc28e8d06b5fdd83b688ca0be45695e2d2d3bcc59b486d8f92522593ba619ee"
    ),
    "ucdp-dyadic-26.1-candidates.jsonl": (
        "c6e6f7deda305d38e78c987713817410ba3c4045904e22e86e12389fb4a622e4"
    ),
    "ucdp-termination-conflict-candidates.jsonl": (
        "4ce351ab0b0654b341ca8aba42ba82bd5a1955e7c6900351d0f179aae02a3219"
    ),
    "ucdp-termination-dyad-candidates.jsonl": (
        "49c8bead50aa966ee0c70ac023eca9dd81060668db180c1dcfd116c0e827218d"
    ),
}


WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES: dict[str, str] = {
    "hced-Abeche1983-1": (
        "e3ecd5634a90987869d0f9ce3d21731df253fd220a1394581d7841fe6f210571"
    ),
    "hced-Iriba1990-1": (
        "af0728d6ffb3c6f5335376b35b4240d75518026dcce9850ebb5f95435ba049d5"
    ),
    "hced-N'Djamena1979-1": (
        "489bd18eea1d4def1b1e643b0443512f636957e96325cb772bd3435961f27c7b"
    ),
    "hced-N'Djamena1980-1": (
        "a4b9d658f647966744f30b7613d7b0a81ada4c8e0a849accf44452346549c144"
    ),
    "hced-Ouaddai1990-1": (
        "91b38d39daf899d796e3755588e3cc5aeb48d81446ade00dbccfe87ef6b5aea2"
    ),
    "hced-Oum Chalouba1983-1": (
        "6a98fae074dbde33041b3e3700c8a6d8c46261cf49bbddfe9be88e813b29e19e"
    ),
}
WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES: dict[str, str] = {
    "hced-Ati1978-1": (
        "c14cee9a87331ad06e3e6cf0b8a1f57fb5d89ad1432ce744b311fc52d473f0ee"
    ),
    "hced-Erdi1986-1": (
        "8612f9894707bbc15b9ff34da595e1fa1cff2cebd869d6d258b33a62cf1ee3d0"
    ),
}
WAVE8_CHADIAN_REBELS_ROW_HASHES: dict[str, str] = {
    **WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES,
    **WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES,
}
WAVE8_CHADIAN_REBELS_EXACT_CANDIDATE_IDS = frozenset(
    WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES
)
WAVE8_CHADIAN_REBELS_ADJACENT_CANDIDATE_IDS = frozenset(
    WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES
)
WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_CHADIAN_REBELS_ROW_HASHES
)
WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256 = (
    "6f817d799a692180c95daef7d5d043f50a515f80c7706f0eac0f8fced735459d"
)


WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS: dict[str, dict[str, Any]] = {
    "chadian rebels": {
        "label": "chadian rebels",
        "event_candidate_id_sha256": (
            "862b50fc9666c7c233f39c0e4359b9944843656e711c3f361853794860fac209"
        ),
        "events_touched": 6,
        "unresolved_side_attempts": 6,
        "sole_blocker_events": 3,
        "candidate_ids": [],
        "time_valid_candidate_ids": [],
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 6,
        },
        "centuries": {"CE_20": 6},
        "components_touched": 0,
        "components_bridged": 0,
        "rated_counterpart_entities": 0,
    },
    "northern chadian rebels": {
        "label": "northern chadian rebels",
        "event_candidate_id_sha256": (
            "afdd073b02c0367b00beeb7a152a5cb4081dfd83c045b92276077c57862590c7"
        ),
        "events_touched": 1,
        "unresolved_side_attempts": 1,
        "sole_blocker_events": 0,
        "candidate_ids": [],
        "time_valid_candidate_ids": [],
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 1,
        },
        "centuries": {"CE_20": 1},
        "components_touched": 0,
        "components_bridged": 0,
        "rated_counterpart_entities": 0,
    },
    "libya north chadian rebels": {
        "label": "libya north chadian rebels",
        "event_candidate_id_sha256": (
            "6f92b07c0583bd44423442117efc4d45c148c5e5d4ec05fe8a6d1ab80d0af1c5"
        ),
        "events_touched": 1,
        "unresolved_side_attempts": 1,
        "sole_blocker_events": 1,
        "candidate_ids": [],
        "time_valid_candidate_ids": [],
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 1,
        },
        "centuries": {"CE_20": 1},
        "components_touched": 0,
        "components_bridged": 0,
        "rated_counterpart_entities": 0,
    },
}


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


WAVE8_CHADIAN_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_chadian_rebels_loc_country_study",
        "Chad: A Country Study",
        "https://tile.loc.gov/storage-services/master/frd/frdcstdy/ch/chadcountrystudy00coll/chadcountrystudy00coll.pdf",
        "Library of Congress, Federal Research Division",
        "federal_country_study",
        "loc_chad_country_study_1990",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_powell_cambridge",
        "France's Wars in Chad: Military Intervention and Decolonization in Africa",
        "https://www.cambridge.org/core/books/frances-wars-in-chad/6B7D8F9C8A81E0A83028C24EA0CF8D28",
        "Cambridge University Press",
        "archival_scholarly_monograph",
        "powell_frances_wars_chad_2020",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_french_defense_tacaud",
        "Opération Tacaud",
        "https://www.cheminsdememoire.gouv.fr/sites/default/files/2019-06/op%C3%A9ration%20Tacaud.pdf",
        "French Ministry of the Armed Forces / ECPAD",
        "official_military_archive_history",
        "french_defense_tacaud_ecpad",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_air_university",
        "Prolonged Wars: A Post-Nuclear Challenge",
        "https://www.airuniversity.af.edu/Portals/10/AUPress/Books/B_0059_MAGYAR_PROLONGED_WARS.pdf",
        "Air University Press",
        "scholarly_defense_studies_volume",
        "air_university_prolonged_wars_chad",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_au_mays",
        "Frustrations of Regional Peacekeeping: The OAU in Chad, 1977-1982",
        "https://au.int/sites/default/files/documents/39217-doc-171._frustrations_of_regional_peacekeeping.the_oau_in_chad_1977-1982.pdf",
        "African Union",
        "scholarly_regional_organization_history",
        "mays_oau_chad_1977_1982",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_frus_1980",
        "Foreign Relations of the United States, 1977-1980, Volume XVII, Part 3, document 53",
        "https://history.state.gov/historicaldocuments/frus1977-80v17p3/d53",
        "U.S. Department of State, Office of the Historian",
        "declassified_diplomatic_record",
        "frus_1977_1980_chad_document_53",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_hrw_en_habre",
        "Enabling a Dictator: The United States and Chad's Hissène Habré 1982-1990",
        "https://www.hrw.org/report/2016/06/28/enabling-dictator/united-states-and-chads-hissene-habre-1982-1990",
        "Human Rights Watch",
        "archival_human_rights_history",
        "hrw_enabling_habre_2016",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_csm_abeche_1983",
        "Rebels retreat before Chad government forces",
        "https://www.csmonitor.com/1983/0726/072645.html",
        "The Christian Science Monitor",
        "contemporaneous_independent_reporting",
        "csm_chad_abeche_1983",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_washpost_oum_1983",
        "Chad Rebels Mount Major Drive in North",
        "https://www.washingtonpost.com/archive/politics/1983/09/03/chad-rebels-mount-major-drive-in-north/fbbccece-fd42-456e-a32f-49ef300ea17f/",
        "The Washington Post",
        "contemporaneous_independent_reporting",
        "washington_post_oum_chalouba_1983",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_un_sc_1983",
        "Security Council Official Records, Thirty-eighth Year, Supplement for July-September 1983",
        "https://digitallibrary.un.org/record/100573/files/S_SUPP_1983_3--%5EOR_SC_1983_III%5E-EN.pdf",
        "United Nations",
        "official_contemporaneous_record",
        "un_security_council_1983_q3_chad",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_un_wako_1991",
        "Report on extrajudicial, summary or arbitrary executions, E/CN.4/1991/36",
        "https://digitallibrary.un.org/record/107512",
        "United Nations Commission on Human Rights",
        "un_special_rapporteur_report",
        "un_wako_chad_1991",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_hrw_fr_habre",
        "Allié de la France, condamné par l'Afrique: Les relations entre la France et le régime de Hissène Habré",
        "https://www.hrw.org/fr/report/2016/06/28/allie-de-la-france-condamne-par-lafrique/les-relations-entre-la-france-et-le",
        "Human Rights Watch",
        "archival_human_rights_history",
        "hrw_france_habre_2016",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_ina_1990",
        "Tchad: rapport de forces entre Déby et Habré",
        "https://www.ina.fr/ina-eclaire-actu/video/cab90045503/tchad-rapport-de-forces-entre-deby-et-habre",
        "Institut national de l'audiovisuel",
        "contemporaneous_broadcast_archive",
        "ina_chad_deby_habre_1990",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_un_yearbook_1986",
        "Yearbook of the United Nations 1986",
        "https://digitallibrary.un.org/record/147661/files/284532-EN.pdf",
        "United Nations",
        "official_yearbook",
        "un_yearbook_1986_chad",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_iwbd_dataset",
        "International Wars and Battles Dataset",
        "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
        "Harvard Dataverse",
        "research_dataset",
        "iwbd_dataverse_release",
        crosscheck=True,
    ),
    _source(
        "wave8_chadian_rebels_ucdp_v26_1",
        "UCDP Conflict, Dyadic, and Conflict Termination datasets, version 26.1/4.2024.002",
        "https://ucdp.uu.se/downloads/",
        "Uppsala Conflict Data Program",
        "research_dataset_documentation",
        "ucdp_release_26_1_and_termination_4_2024_002",
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_CHADIAN_REBELS_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


def _entity(
    entity_id: str,
    name: str,
    year: int,
    kind: str,
    boundary_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Central Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or passed to generic Chadian Rebels, "
            "FROLINAT, FAN, FAP, GUNT, MPS, the government or state of Chad, "
            "France, Libya, another event formation, or the strategic civil-war "
            "outcome."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_ATI_FRENCH = "french_operation_tacaud_ati_force_1978"
_ATI_FAT = "malloum_fat_ati_defense_force_1978"
_ATI_FAP = "fap_frolinat_ati_assault_force_1978"
_NDJ79_FAN = "fan_habre_ndjamena_force_february_1979"
_NDJ79_FAP = "fap_goukouni_ndjamena_entry_force_february_1979"
_NDJ79_FAT = "malloum_fat_ndjamena_force_february_1979"
_NDJ80_GUNT = "gunt_fap_ndjamena_campaign_force_1980"
_NDJ80_LIBYA = "libyan_ndjamena_intervention_force_1980"
_NDJ80_FAN = "fan_habre_ndjamena_campaign_force_1980"


WAVE8_CHADIAN_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ATI_FRENCH,
        "French Operation Tacaud force at Ati (1978)",
        1978,
        "event_bounded_intervention_force",
        "Only the French detachment and air support participating in the Ati action are rated.",
        [
            "wave8_chadian_rebels_french_defense_tacaud",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
    ),
    _entity(
        _ATI_FAT,
        "Malloum FAT defense and relief force at Ati (1978)",
        1978,
        "event_bounded_government_force",
        "Only the Forces Armées Tchadiennes formation defending and relieving Ati is rated.",
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
    ),
    _entity(
        _ATI_FAP,
        "FAP/FROLINAT assault force at Ati (1978)",
        1978,
        "event_bounded_rebel_force",
        "Only the Forces Armées Populaires/FROLINAT force contesting Ati is rated.",
        [
            "wave8_chadian_rebels_french_defense_tacaud",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
    ),
    _entity(
        _NDJ79_FAN,
        "Habré FAN force in N'Djamena (12-22 February 1979)",
        1979,
        "event_bounded_rebel_force",
        "Only Hissène Habré's Forces Armées du Nord in the February capital fighting are rated.",
        [
            "wave8_chadian_rebels_au_mays",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
    ),
    _entity(
        _NDJ79_FAP,
        "Goukouni FAP entry force in N'Djamena (February 1979)",
        1979,
        "event_bounded_rebel_force",
        "Only Goukouni Oueddei's FAP force entering the capital during the takeover sequence is rated.",
        [
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
    ),
    _entity(
        _NDJ79_FAT,
        "Malloum FAT force in N'Djamena (February 1979)",
        1979,
        "event_bounded_government_force",
        "Only President Félix Malloum's Forces Armées Tchadiennes in the February capital fighting are rated.",
        [
            "wave8_chadian_rebels_au_mays",
            "wave8_chadian_rebels_loc_country_study",
        ],
    ),
    _entity(
        _NDJ80_GUNT,
        "Goukouni GUNT/FAP N'Djamena campaign force (1980)",
        1980,
        "event_bounded_government_coalition_force",
        "Only Goukouni Oueddei's GUNT/FAP coalition in the March-December capital campaign is rated.",
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_hrw_en_habre",
            "wave8_chadian_rebels_loc_country_study",
        ],
    ),
    _entity(
        _NDJ80_LIBYA,
        "Libyan intervention force in the N'Djamena campaign (1980)",
        1980,
        "event_bounded_intervention_force",
        "Only the Libyan formation intervening in the closing phase of the 1980 capital campaign is rated.",
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_frus_1980",
            "wave8_chadian_rebels_loc_country_study",
        ],
    ),
    _entity(
        _NDJ80_FAN,
        "Habré FAN N'Djamena campaign force (1980)",
        1980,
        "event_bounded_rebel_force",
        "Only Hissène Habré's FAN formation in the March-December capital campaign is rated.",
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_hrw_en_habre",
            "wave8_chadian_rebels_loc_country_study",
        ],
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
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
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    event_type: str,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_CHADIAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "event_type": event_type,
        "war_type": "intrastate_with_foreign_intervention",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_CHADIAN_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Ati1978-1": _contract(
        "hced-Ati1978-1",
        _canonical(
            "Battle of Ati",
            1978,
            "18-20 May 1978 (source-day variance)",
            date_precision="day_range_source_variance",
            granularity="three_day_battle_and_rebel_evacuation",
        ),
        "ati_battle_1978",
        [_ATI_FRENCH, _ATI_FAT],
        [_ATI_FAP],
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_french_defense_tacaud",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_french_defense_tacaud",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
        (
            "Official French operational history, the federal country study, and "
            "independent scholarly histories agree that the Franco-Chadian force "
            "broke the FAP/FROLINAT attack and entered Ati after the rebels "
            "evacuated. The contract ends at Ati and does not absorb Djedaa or the "
            "wider Tacaud campaign."
        ),
        event_type="engagement",
        confidence=0.93,
    ),
    "hced-N'Djamena1979-1": _contract(
        "hced-N'Djamena1979-1",
        _canonical(
            "First Battle of N'Djamena",
            1979,
            "12-22 February 1979",
            date_precision="day_range",
            granularity="urban_battle_and_regime_displacement_sequence",
        ),
        "ndjamena_first_battle_1979",
        [_NDJ79_FAN, _NDJ79_FAP],
        [_NDJ79_FAT],
        [
            "wave8_chadian_rebels_au_mays",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
            "wave8_chadian_rebels_ucdp_v26_1",
        ],
        [
            "wave8_chadian_rebels_au_mays",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
        (
            "The reviewed histories bound the result to FAN's 12 February attack, "
            "Malloum's retirement and FAT's displacement south, and FAP's entry by "
            "22 February. It is not a timeless northern-rebel victory and does not "
            "inherit the subsequent Kano/Lagos settlement or later civil war."
        ),
        event_type="engagement",
        confidence=0.91,
    ),
    "hced-N'Djamena1980-1": _contract(
        "hced-N'Djamena1980-1",
        _canonical(
            "Second Battle of N'Djamena",
            1980,
            "22 March-16 December 1980 (closing-day variance)",
            date_precision="day_range_source_variance",
            granularity="nine_month_urban_campaign",
        ),
        "ndjamena_second_battle_1980",
        [_NDJ80_GUNT, _NDJ80_LIBYA],
        [_NDJ80_FAN],
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_frus_1980",
            "wave8_chadian_rebels_hrw_en_habre",
            "wave8_chadian_rebels_loc_country_study",
        ],
        [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_hrw_en_habre",
            "wave8_chadian_rebels_loc_country_study",
        ],
        (
            "Independent histories and contemporaneous diplomatic evidence show a "
            "March-December urban campaign: GUNT/FAP, decisively reinforced by the "
            "Libyan intervention, drove Habré's FAN from the capital. This is an "
            "operational campaign result, not one engagement or the result of the "
            "civil war, which continued."
        ),
        event_type="campaign",
        confidence=0.94,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    historical_review: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_CHADIAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "hold",
        "terminal_exclusion": False,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": str(canonical_event["granularity"]),
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
        "historical_review": dict(historical_review),
    }


WAVE8_CHADIAN_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Abeche1983-1": _hold(
        "hced-Abeche1983-1",
        _canonical(
            "Abéché capture-recapture sequence",
            1983,
            "July 1983",
            date_precision="month",
            granularity="same_month_capture_and_recapture_sequence",
        ),
        "abeche_actions_1983",
        "year_place_row_collapses_opposite_results",
        (
            "Rebels occupied Abéché on 10 July and Habré's force recaptured it in "
            "the ensuing counteroffensive. The year/place HCED row does not identify "
            "which phase its asserted government win represents. Selecting the "
            "recapture would silently discard the preceding capture, so the whole "
            "row remains unknown; it is never converted into a draw."
        ),
        [
            "wave8_chadian_rebels_csm_abeche_1983",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_ucdp_v26_1",
        ],
        {
            "rebel_success": "Abéché occupied on 10 July",
            "government_success": "Abéché recaptured during the July counteroffensive",
            "row_resolution": "cannot select one phase from a year-only row",
        },
    ),
    "hced-Erdi1986-1": _hold(
        "hced-Erdi1986-1",
        _canonical(
            "Erdi action",
            1986,
            "5 October 1986 in IWBD; HCED supplies year only",
            date_precision="cross_source_day_vs_year",
            granularity="single_day_cross_source_result_conflict",
        ),
        "erdi_cross_source_conflict_1986",
        "opposite_hced_iwbd_results_without_independent_adjudication",
        (
            "HCED makes Libya and 'North Chadian Rebels' the winner, while the exact "
            "IWBD Erdi twin makes Chad the winner on 5 October 1986. UCDP and the UN "
            "records are strategic/annual and do not independently adjudicate this "
            "named action. Neither source outcome is promoted or reversed; the result "
            "is unknown and never a draw."
        ),
        [
            "wave8_chadian_rebels_iwbd_dataset",
            "wave8_chadian_rebels_ucdp_v26_1",
            "wave8_chadian_rebels_un_yearbook_1986",
        ],
        {
            "hced_winner": "Libya, North Chadian Rebels",
            "iwbd_winner": "Chad",
            "iwbd_date": "1986-10-05",
            "independent_tactical_adjudication": "not found",
        },
    ),
    "hced-Iriba1990-1": _hold(
        "hced-Iriba1990-1",
        _canonical(
            "Iriba actions",
            1990,
            "March-April and November 1990",
            date_precision="separated_periods_within_year",
            granularity="multiple_attacks_and_government_recaptures",
        ),
        "iriba_actions_1990",
        "year_place_row_collapses_multiple_actions",
        (
            "The record contains more than one Iriba action: government forces "
            "recaptured the town around 6 April after rebels held it, and Habré again "
            "regained Iriba during the November MPS offensive. A year-only government "
            "win cannot be assigned to one bounded formation or engagement without "
            "invention. The outcome is held unknown and is never a draw."
        ),
        [
            "wave8_chadian_rebels_hrw_fr_habre",
            "wave8_chadian_rebels_ina_1990",
            "wave8_chadian_rebels_un_wako_1991",
            "wave8_chadian_rebels_ucdp_v26_1",
        ],
        {
            "april_boundary": "government recapture around 6 April",
            "november_boundary": "Habré regained Iriba during the MPS offensive",
            "row_resolution": "multiple plausible government successes",
        },
    ),
    "hced-Ouaddai1990-1": _hold(
        "hced-Ouaddai1990-1",
        _canonical(
            "Ouaddaï phase of the MPS offensive",
            1990,
            "1990",
            date_precision="year",
            granularity="regional_campaign_umbrella_not_named_engagement",
        ),
        "ouaddai_mps_offensive_1990",
        "regional_campaign_not_bounded_engagement",
        (
            "Ouaddaï is a region and the available evidence describes Déby's broad "
            "MPS eastern offensive culminating in Habré's overthrow, not one named "
            "Ouaddaï engagement with a bounded tactical result. UCDP's 3 December "
            "MPS termination is strategic and cannot supply an engagement winner. "
            "The row remains unknown and is never a draw."
        ),
        [
            "wave8_chadian_rebels_hrw_fr_habre",
            "wave8_chadian_rebels_ina_1990",
            "wave8_chadian_rebels_ucdp_v26_1",
        ],
        {
            "geographic_scope": "Ouaddaï region",
            "attested_scope": "MPS eastern offensive and regime collapse",
            "named_engagement": "not independently identified",
        },
    ),
    "hced-Oum Chalouba1983-1": _hold(
        "hced-Oum Chalouba1983-1",
        _canonical(
            "Oum Chalouba actions",
            1983,
            "July-September 1983",
            date_precision="multi_month_sequence",
            granularity="capture_recapture_and_contested_attack_claims",
        ),
        "oum_chalouba_actions_1983",
        "multiple_actions_and_contested_contemporaneous_claims",
        (
            "Oum Chalouba changed hands or was attacked repeatedly during the 1983 "
            "northern campaign. Contemporaneous government and rebel claims conflict, "
            "and the UN record references a government battle to retake the place "
            "without resolving every later claim. The HCED year/place win cannot be "
            "assigned to one action; it remains unknown and is never a draw."
        ),
        [
            "wave8_chadian_rebels_csm_abeche_1983",
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_un_sc_1983",
            "wave8_chadian_rebels_washpost_oum_1983",
        ],
        {
            "reviewed_scope": "July-September capture, recapture, and attack sequence",
            "claim_quality": "contemporaneous claims were conflicting",
            "single_bounded_winner": "not independently established",
        },
    ),
}

WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_CHADIAN_REBELS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_CHADIAN_REBELS_HOLDS,
    **WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS,
}
WAVE8_CHADIAN_REBELS_CONTRACT_IDS = frozenset(WAVE8_CHADIAN_REBELS_CONTRACTS)
WAVE8_CHADIAN_REBELS_HOLD_IDS = frozenset(WAVE8_CHADIAN_REBELS_HOLDS)
WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS
)
WAVE8_CHADIAN_REBELS_RESERVED_IDS = frozenset(
    WAVE8_CHADIAN_REBELS_CONTRACT_IDS
    | WAVE8_CHADIAN_REBELS_HOLD_IDS
    | WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Ati1978-1": {
        "actions": ["withhold_point"],
        "raw_point": [18.3385977, 13.2166179],
        "retained_country": "Chad",
        "evidence_refs": [
            "wave8_chadian_rebels_french_defense_tacaud",
            "wave8_chadian_rebels_loc_country_study",
        ],
        "reason": (
            "The staged modern locality centroid does not authenticate the Batha "
            "crossing, approaches, positions, or full battle footprint."
        ),
    },
    "hced-N'Djamena1979-1": {
        "actions": ["withhold_point"],
        "raw_point": [15.0557415, 12.1348457],
        "retained_country": "Chad",
        "evidence_refs": [
            "wave8_chadian_rebels_loc_country_study",
            "wave8_chadian_rebels_powell_cambridge",
        ],
        "reason": (
            "A city centroid is not an authenticated geometry for the distributed "
            "street fighting, withdrawals, and force entry sequence."
        ),
    },
    "hced-N'Djamena1980-1": {
        "actions": ["withhold_point"],
        "raw_point": [15.0557415, 12.1348457],
        "retained_country": "Chad",
        "evidence_refs": [
            "wave8_chadian_rebels_air_university",
            "wave8_chadian_rebels_hrw_en_habre",
            "wave8_chadian_rebels_loc_country_study",
        ],
        "reason": (
            "A city centroid cannot represent a nine-month urban campaign and its "
            "changing fronts, intervention routes, and withdrawal corridor."
        ),
    },
}
WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS
)
WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Ati1978-1": {
        "raw_row_sha256": WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES[
            "hced-Ati1978-1"
        ],
        "normalized_side_label": "northern chadian rebels",
        "disposition": "promoted_by_exact_lane_for_spelling_ownership",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The directional adjective is a mechanically adjacent spelling of the "
            "same unresolved rebel-label problem; the bounded Ati contract owns it."
        ),
    },
    "hced-Erdi1986-1": {
        "raw_row_sha256": WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES[
            "hced-Erdi1986-1"
        ],
        "normalized_side_label": "libya north chadian rebels",
        "disposition": "held_by_exact_lane_for_spelling_ownership",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The compound wraps the mechanically adjacent 'North Chadian Rebels' "
            "spelling; ownership is reserved while its opposite-result IWBD twin is held."
        ),
    },
}


def _event_id(candidate_id: str) -> str:
    return f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"


WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "iwbd-207-80-1650": {
        "raw_row_sha256": (
            "a79d968ec33b6ff5353c3027af833a0ce6948a445565f120367f1c6c1ed68564"
        ),
        "owner_hced_candidate_id": "hced-Erdi1986-1",
        "expected_name": "Erdi",
        "expected_start_date": "1986-10-05",
        "expected_end_date": "1986-10-05",
        "expected_attacker_raw": "Libya",
        "expected_defender_raw": "Chad",
        "expected_winner_raw": "Chad",
        "disposition": "opposite_result_cross_source_twin_held",
        "evidence_refs": ["wave8_chadian_rebels_iwbd_dataset"],
        "reason": (
            "IWBD's Chad win directly contradicts HCED's Libya/North Chadian Rebels "
            "win; neither is used without independent tactical adjudication."
        ),
    }
}


_UCDP_HASHES: dict[str, str] = {
    "ucdp-conflict-26.1-288-1978-1064": "33aa6f76a62da52ca9a4097eb16efc25d15ac2b8d45f875c399266f86e5cf6fa",
    "ucdp-conflict-26.1-288-1979-1065": "07a652fd97767328b5f77b6d40d8c50ab4fc649d508ad96ad2ea99080c05f27e",
    "ucdp-conflict-26.1-288-1980-1066": "8e1c72942948a28cf7006c6ce5867ab3747e4f7105c29c6854498f441964f751",
    "ucdp-conflict-26.1-288-1983-1069": "75c9045e2b90d9f34a9b048d58aab0fa9dc2d408fff0ed4190e8e8b0505540c7",
    "ucdp-conflict-26.1-288-1986-1071": "8863c9430211c6aeb1670a3bca4ffd11a39f2653db1332fe1ca71e7bbc318a8c",
    "ucdp-conflict-26.1-288-1990-1074": "dbcc51cfaba6c01de8a4f8db47b47c50830cfe663da3d4ba100c3f02bbb3c2d6",
    "ucdp-dyadic-26.1-601-1979-1232": "3b84ed4ef5c3bfbfde8795aae240951c1901fb66a0caad320335319a77bafc8d",
    "ucdp-dyadic-26.1-601-1980-1233": "0a1c19943b71e668d09c5b885a0a3da2733b1e6ddabecc1124ee3fd8942ffce5",
    "ucdp-dyadic-26.1-602-1978-1237": "28553729532b608755b7dd0bc3c2cc064349c27b58f0c1a4279929a49fad600d",
    "ucdp-dyadic-26.1-602-1979-1238": "031f8d8cd5492d56d35dc2624c3b4f06df6d849be89d426c5f7f544730859541",
    "ucdp-dyadic-26.1-604-1983-1240": "b558a59c5ceedcdde99e1bac38b7c65e9ef074bbda01d78ab9d046b975171f73",
    "ucdp-dyadic-26.1-604-1986-1242": "a20aa738b4914a1042c5a240db6b1da4a925b8f53dd1e53efb91b7a0f040b484",
    "ucdp-dyadic-26.1-606-1990-1245": "3e9fc6bd6c0609f06ac4f3aed19619986b96ae9f2564709f9bdc42ea59ef6fa6",
    "ucdp-dyadic-26.1-609-1990-1248": "e9894c22f0892ae52ed13710a9417b122907fd465885ef460ccbcedebd377c6c",
    "ucdp-termination-conflict-288-1051": "ac778702689ff9c316731fee1559f8498bf4e3ad261e1cb9343a28a2fd4e44c0",
    "ucdp-termination-conflict-288-1052": "6fc70046107ff31564f83914db5f84f1df2014b26240bbbc598594e94e4e8afe",
    "ucdp-termination-conflict-288-1053": "3d2afab0ea5d954e06dd283db1241e341564e8fd27a2a068aad3b754b9ae11dd",
    "ucdp-termination-conflict-288-1056": "be559baa5bfcf3875f5d6f8640da5b02c74fb709cd7925ef0216f65ce86736a5",
    "ucdp-termination-conflict-288-1058": "b475f0ca251e5ffde96fdf1cd5fcd6e5d95b6c751cb465939f3e8e199c11fe76",
    "ucdp-termination-conflict-288-1061": "51e9bf5522c829331458f5322c535f844b1b2a41c0c6505e48778939a2be59fc",
    "ucdp-termination-dyad-288-1221": "ca1e07c151487a516ce94cf76adab985857b85c976a007ca23d6be4fbf3da904",
    "ucdp-termination-dyad-288-1222": "c8527949d17d1a3a9bfabd690efb18e486d50e864bf36fbee577c8a21d52a78b",
    "ucdp-termination-dyad-288-1226": "cb6d3b19fefdd0b7c01964ada3eb9aaf2cee88c6d7649356d0ee362be8204cc0",
    "ucdp-termination-dyad-288-1227": "0b4038a641476fd09cc3410d9b4a74c57ac24446e2605ecc37ad5d0ebeb4a540",
    "ucdp-termination-dyad-288-1229": "e224daf38665ab7ca28590f075b9168f9ac9e7e1dee9886e628fa01e353b2240",
    "ucdp-termination-dyad-288-1231": "e35f796959a9aa37eb29ed4cfbc2429be1a73e111b370b3494ecff0b570472fe",
    "ucdp-termination-dyad-288-1234": "211d77da4d1e6f932df13f471fed1790a0ed3500d007dfac8892863b3c13c5e9",
    "ucdp-termination-dyad-288-1237": "2ef4449951cdc5b218b9d0dc1fdc87f2d5ed3606230a92f2ecbb457ff0f191a6",
}


def _ucdp_scope(candidate_id: str) -> str:
    if candidate_id.startswith("ucdp-conflict-"):
        return "annual_conflict_record"
    if candidate_id.startswith("ucdp-dyadic-"):
        return "annual_dyad_record"
    if candidate_id.startswith("ucdp-termination-conflict-"):
        return "strategic_conflict_episode"
    return "strategic_dyad_episode_or_termination"


WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "raw_row_sha256": raw_hash,
        "conflict_id": "288",
        "scope": _ucdp_scope(candidate_id),
        "disposition": "related_strategic_record_not_named_tactical_duplicate",
        "evidence_refs": ["wave8_chadian_rebels_ucdp_v26_1"],
        "boundary_note": (
            "Conflict 288's annual/episode record identifies actors, intensity, or "
            "strategic termination; it does not independently encode the named "
            "HCED engagement outcome."
        ),
    }
    for candidate_id, raw_hash in sorted(_UCDP_HASHES.items())
}


WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES: dict[
    str, dict[str, Any]
] = {
    "iwbd_iwbd_207_80_1652_fada": {
        "expected_name": "Fada",
        "expected_year": 1987,
        "expected_end_year": 1987,
        "expected_entity_ids": ["libyan_arab_jamahiriya", "republic_chad"],
        "disposition": "distinct_1987_engagement",
    },
    "iwbd_iwbd_207_80_1653_ouadi_doum": {
        "expected_name": "Ouadi Doum",
        "expected_year": 1987,
        "expected_end_year": 1987,
        "expected_entity_ids": ["libyan_arab_jamahiriya", "republic_chad"],
        "disposition": "distinct_1987_engagement",
    },
    "iwbd_iwbd_207_80_1655_maaten_as_sarra": {
        "expected_name": "Maaten-as-Sarra",
        "expected_year": 1987,
        "expected_end_year": 1987,
        "expected_entity_ids": ["libyan_arab_jamahiriya", "republic_chad"],
        "disposition": "distinct_1987_engagement",
    },
}


def _hced_owner_disposition(candidate_id: str) -> dict[str, Any]:
    item = WAVE8_CHADIAN_REBELS_CONTRACTS.get(candidate_id)
    disposition = "promotion"
    if item is None:
        item = WAVE8_CHADIAN_REBELS_NONPROMOTIONS[candidate_id]
        disposition = str(item["disposition"])
    return {
        "raw_row_sha256": str(item["raw_row_sha256"]),
        "disposition": disposition,
        "owner_module": _MODULE_OWNER,
    }


WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    **{
        f"hced_owner:{candidate_id}": _hced_owner_disposition(candidate_id)
        for candidate_id in sorted(WAVE8_CHADIAN_REBELS_RESERVED_IDS)
    },
    **{
        f"iwbd_twin:{candidate_id}": dict(disposition)
        for candidate_id, disposition in sorted(
            WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        f"ucdp_boundary:{candidate_id}": dict(disposition)
        for candidate_id, disposition in sorted(
            WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS.items()
        )
    },
    **{
        f"current_release:{event_id}": dict(disposition)
        for event_id, disposition in sorted(
            WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES.items()
        )
    },
}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)))),
        "years": (year,),
    }


_DUPLICATE_AUDITS: dict[str, dict[str, Any]] = {
    "hced-Abeche1983-1": _duplicate_audit(
        1983, "Abeche", "Abéché", "Battle of Abéché"
    ),
    "hced-Ati1978-1": _duplicate_audit(1978, "Ati", "Battle of Ati"),
    "hced-Erdi1986-1": _duplicate_audit(1986, "Erdi", "Battle of Erdi"),
    "hced-Iriba1990-1": _duplicate_audit(1990, "Iriba", "Battle of Iriba"),
    "hced-N'Djamena1979-1": _duplicate_audit(
        1979, "N'Djamena", "First Battle of N'Djamena", "Battle of N'Djamena (1979)"
    ),
    "hced-N'Djamena1980-1": _duplicate_audit(
        1980, "N'Djamena", "Second Battle of N'Djamena", "Battle of N'Djamena (1980)"
    ),
    "hced-Ouaddai1990-1": _duplicate_audit(
        1990, "Ouaddai", "Ouaddaï", "Ouaddaï offensive"
    ),
    "hced-Oum Chalouba1983-1": _duplicate_audit(
        1983, "Oum Chalouba", "Um Chalouba", "Battle of Oum Chalouba"
    ),
}
WAVE8_CHADIAN_REBELS_DUPLICATE_AUDITS = _DUPLICATE_AUDITS


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _canonical_object_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS,
        "adjacent_row_hashes": WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES,
        "contracts": WAVE8_CHADIAN_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "current_release_boundaries": WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES,
        "duplicate_audits": _DUPLICATE_AUDITS,
        "entities": WAVE8_CHADIAN_REBELS_ENTITIES,
        "exact_row_hashes": WAVE8_CHADIAN_REBELS_EXACT_ROW_HASHES,
        "expected_candidate_id_sha256": WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256,
        "expected_candidate_ids": sorted(WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS),
        "funnel_audits": WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS,
        "hced_queue_sha256": WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256,
        "holds": WAVE8_CHADIAN_REBELS_HOLDS,
        "integration_dispositions": WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256,
        "location_quarantine_reasons": WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_CHADIAN_REBELS_SOURCES,
        "terminal_exclusions": WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS,
        "ucdp_overlap_dispositions": WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS,
        "ucdp_queue_sha256": WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256,
    }


def wave8_chadian_rebels_audit_signature() -> str:
    """Return the deterministic digest of all fixtures and audit boundaries."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE = (
    "313a118182a7c39fe4ab950c7f627afcc3b597ab8ef2a1d63c1d64e251cad9bc"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_CHADIAN_REBELS_CONTRACTS),
        len(WAVE8_CHADIAN_REBELS_HOLDS),
        len(WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS),
    ) != (3, 5, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_CHADIAN_REBELS_ENTITIES), len(WAVE8_CHADIAN_REBELS_SOURCES)) != (
        9,
        16,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_CHADIAN_REBELS_RESERVED_IDS != WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} HCED ownership is incomplete")
    if set(WAVE8_CHADIAN_REBELS_ADJACENT_HCED_DISPOSITIONS) != set(
        WAVE8_CHADIAN_REBELS_ADJACENT_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} adjacent spelling ownership changed")
    if _sorted_newline_sha256(WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} candidate digest changed")
    hashes = (
        WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256,
        WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256,
        WAVE8_CHADIAN_REBELS_EXPECTED_CANDIDATE_ID_SHA256,
        *WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256.values(),
        *WAVE8_CHADIAN_REBELS_ROW_HASHES.values(),
        *_UCDP_HASHES.values(),
    )
    if any(len(value) != 64 for value in hashes):
        raise ValueError(f"{_LANE_NAME} hash inventory changed")
    if (
        wave8_chadian_rebels_audit_signature()
        != WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = dict(_SOURCE_BY_ID)
    if len(source_by_id) != len(WAVE8_CHADIAN_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in source_by_id.values()}) != len(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in source_by_id.values():
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_CHADIAN_REBELS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_CHADIAN_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in entity_by_id.values():
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event-year bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = normalize_label(entity["continuity_note"])
        for phrase in (
            "no rating is inherited",
            "generic chadian rebels",
            "government or state of chad",
            "strategic civil war outcome",
        ):
            if normalize_label(phrase) not in note:
                raise ValueError(f"{_LANE_NAME} identity firewall changed")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity evidence changed")
        used_sources.update(refs)

    expected_types = {
        "hced-Ati1978-1": "engagement",
        "hced-N'Djamena1979-1": "engagement",
        "hced-N'Djamena1980-1": "campaign",
    }
    for candidate_id, contract in WAVE8_CHADIAN_REBELS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_CHADIAN_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash changed")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{canonical['year_low']}:{canonical['year_high']}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event changed")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            not _is_sorted_unique(side_1)
            or not _is_sorted_unique(side_2)
            or not side_1
            or not side_2
            or set(side_1) & set(side_2)
            or not (set(side_1) | set(side_2)) <= set(entity_by_id)
        ):
            raise ValueError(f"{_LANE_NAME} actor contract changed")
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id[entity_id]
            if int(entity["start_year"]) != int(canonical["year_low"]):
                raise ValueError(f"{_LANE_NAME} entity event window changed")
        used_entities.update(side_1)
        used_entities.update(side_2)
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["event_type"] != expected_types[candidate_id]
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= set(source_by_id)
            or len(outcomes) < 3
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or any(
                "outcome" not in source_by_id[source_id]["evidence_roles"]
                for source_id in outcomes
            )
        ):
            raise ValueError(f"{_LANE_NAME} outcome evidence changed")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} corroboration families changed")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} event identities are not exactly consumed")

    forbidden_nonpromotion = {
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
    }
    for candidate_id, item in WAVE8_CHADIAN_REBELS_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_CHADIAN_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold row hash changed")
        if forbidden_nonpromotion & set(item):
            raise ValueError(f"{_LANE_NAME} hold became rateable")
        if (
            item["disposition"] != "hold"
            or item["terminal_exclusion"] is not False
            or item["reviewed_outcome"] != "unknown"
            or item["unknown_is_never_draw"] is not True
            or "never" not in str(item["hold_reason"]).casefold()
            or "draw" not in str(item["hold_reason"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} unknown/draw policy changed")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence changed")
        used_sources.update(refs)

    if WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS != WAVE8_CHADIAN_REBELS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    for candidate_id, item in WAVE8_CHADIAN_REBELS_LOCATION_QUARANTINE_REASONS.items():
        if item["actions"] != ["withhold_point"] or item["retained_country"] != "Chad":
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(refs)

    if set(WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS) != set(_UCDP_HASHES):
        raise ValueError(f"{_LANE_NAME} UCDP inventory changed")
    for item in WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS.values():
        used_sources.update(map(str, item["evidence_refs"]))
    for item in WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.values():
        used_sources.update(map(str, item["evidence_refs"]))
    if used_sources != set(source_by_id):
        raise ValueError(
            f"{_LANE_NAME} sources are not exactly consumed: "
            f"{sorted(set(source_by_id) - used_sources)}"
        )
    if WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES or WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} declared-empty inventory changed")
    if len(WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS) != 40:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")


_EXPECTED_RAW_FIELDS: dict[str, dict[str, Any]] = {
    "hced-Abeche1983-1": {
        "name": "Abeche", "side_1_raw": "Chad", "side_2_raw": "Chadian Rebels",
        "winner_raw": "Chad", "loser_raw": "Chadian Rebels", "source_row": 23,
    },
    "hced-Ati1978-1": {
        "name": "Ati", "side_1_raw": "France, Chadian Government",
        "side_2_raw": "Northern Chadian Rebels",
        "winner_raw": "France, Chadian Government",
        "loser_raw": "Northern Chadian Rebels", "source_row": 1271,
    },
    "hced-Erdi1986-1": {
        "name": "Erdi", "side_1_raw": "Libya, North Chadian Rebels",
        "side_2_raw": "Chad", "winner_raw": "Libya, North Chadian Rebels",
        "loser_raw": "Chad", "source_row": 5285,
    },
    "hced-Iriba1990-1": {
        "name": "Iriba", "side_1_raw": "Chadian Government",
        "side_2_raw": "Chadian Rebels", "winner_raw": "Chadian Government",
        "loser_raw": "Chadian Rebels", "source_row": 7435,
    },
    "hced-N'Djamena1979-1": {
        "name": "N'Djamena", "side_1_raw": "Chadian Rebels",
        "side_2_raw": "Chadian Government", "winner_raw": "Chadian Rebels",
        "loser_raw": "Chadian Government", "source_row": 11285,
    },
    "hced-N'Djamena1980-1": {
        "name": "N'Djamena", "side_1_raw": "Chadian Government, Libya",
        "side_2_raw": "Chadian Rebels", "winner_raw": "Chadian Government, Libya",
        "loser_raw": "Chadian Rebels", "source_row": 11287,
    },
    "hced-Ouaddai1990-1": {
        "name": "Ouaddai", "side_1_raw": "Chadian Rebels", "side_2_raw": "Chad",
        "winner_raw": "Chadian Rebels", "loser_raw": "Chad", "source_row": 11979,
    },
    "hced-Oum Chalouba1983-1": {
        "name": "Oum Chalouba", "side_1_raw": "Chad",
        "side_2_raw": "Chadian Rebels", "winner_raw": "Chad",
        "loser_raw": "Chadian Rebels", "source_row": 11989,
    },
}


def _rows_by_id(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return result


def validate_wave8_chadian_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all six exact rows and only the two reserved adjacent spellings."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CHADIAN_REBELS_CONTRACTS,
        WAVE8_CHADIAN_REBELS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    }
    adjacent_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _ADJACENT_LABELS
        or normalize_label(row.get("side_2_raw")) in _ADJACENT_LABELS
    }
    if exact_ids != WAVE8_CHADIAN_REBELS_EXACT_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}")
    if adjacent_ids != WAVE8_CHADIAN_REBELS_ADJACENT_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} adjacent-label inventory changed: {sorted(adjacent_ids)}")
    for candidate_id, expected in _EXPECTED_RAW_FIELDS.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing owned row {candidate_id}")
        row = rows[0]
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} raw semantics changed for {candidate_id}")
        year = int(candidate_id[-6:-2])
        if (
            row.get("year_low") != year
            or row.get("year_high") != year
            or row.get("year_best") != year
            or row.get("winner_loser_complete") is not True
        ):
            raise ValueError(f"{_LANE_NAME} date/outcome completeness changed")
    return {
        "adjacent_hced_rows": len(adjacent_ids),
        "exact_hced_rows": len(exact_ids),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_chadian_rebels_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the exact and mechanically adjacent unresolved funnel records."""

    records = {
        str(record.get("label")): record for record in funnel.get("labels", [])
    }
    for label, expected in WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS.items():
        record = records.get(label)
        if record is None:
            raise ValueError(f"{_LANE_NAME} missing funnel label {label}")
        for field, value in expected.items():
            if record.get(field) != value:
                raise ValueError(f"{_LANE_NAME} funnel field changed: {label}.{field}")
    return {
        "funnel_labels": len(WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS),
        "rows_touched": sum(
            int(item["events_touched"])
            for item in WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS.values()
        ),
        "sole_blocker_rows": sum(
            int(item["sole_blocker_events"])
            for item in WAVE8_CHADIAN_REBELS_FUNNEL_AUDITS.values()
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value not in (None, ""):
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    aliases = row.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    values = [row.get("name"), *(aliases if isinstance(aliases, list) else [])]
    return {normalize_label(value) for value in values if normalize_label(value)}


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), str(alias))
        for audit in _DUPLICATE_AUDITS.values()
        for year in audit["years"]
        for alias in audit["aliases"]
    }


def _participant_ids(event: Mapping[str, Any]) -> set[str]:
    participants = event.get("participants", [])
    if not isinstance(participants, list):
        return set()
    return {
        str(participant.get("entity_id"))
        for participant in participants
        if isinstance(participant, Mapping) and participant.get("entity_id")
    }


def validate_wave8_chadian_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    ucdp_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on HCED/IWBD/UCDP/release twins and partial release state."""

    validate_wave8_chadian_rebels_queue_contracts(hced_rows)
    pairs = _audited_name_year_pairs()

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_CHADIAN_REBELS_RESERVED_IDS
        and any((_row_year(row), name) in pairs for name in _row_names(row))
    )
    if hced_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed HCED twin(s): {hced_twins}")

    iwbd_index = _rows_by_id(iwbd_rows)
    for candidate_id, disposition in WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items():
        rows = iwbd_index.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing IWBD twin {candidate_id}")
        row = rows[0]
        if _canonical_object_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {candidate_id}")
        expected = {
            "name": disposition["expected_name"],
            "start_date": disposition["expected_start_date"],
            "end_date": disposition["expected_end_date"],
            "attacker_raw": disposition["expected_attacker_raw"],
            "defender_raw": disposition["expected_defender_raw"],
            "winner_raw": disposition["expected_winner_raw"],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} IWBD twin semantics changed: {candidate_id}")
    declared_iwbd = set(WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS)
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in declared_iwbd
        and any((_row_year(row), name) in pairs for name in _row_names(row))
    )
    if iwbd_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed IWBD twin(s): {iwbd_twins}")

    supplied_ucdp = list(ucdp_rows)
    if supplied_ucdp:
        ucdp_index = _rows_by_id(supplied_ucdp)
        for candidate_id, disposition in WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS.items():
            rows = ucdp_index.get(candidate_id, [])
            if len(rows) != 1:
                raise ValueError(f"{_LANE_NAME} missing UCDP boundary {candidate_id}")
            if _canonical_object_sha256(rows[0]) != disposition["raw_row_sha256"]:
                raise ValueError(f"{_LANE_NAME} UCDP fingerprint changed: {candidate_id}")

    existing = list(existing_events)
    released_holds = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_CHADIAN_REBELS_NONPROMOTIONS
    )
    if released_holds:
        raise ValueError(f"{_LANE_NAME} nonpromotion entered release: {released_holds}")

    lane_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_CHADIAN_REBELS_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    lane_candidates = [str(event.get("hced_candidate_id")) for event in lane_events]
    if (
        set(lane_candidates)
        not in (set(), set(WAVE8_CHADIAN_REBELS_CONTRACT_IDS))
        or len(lane_candidates) not in (0, len(WAVE8_CHADIAN_REBELS_CONTRACT_IDS))
        or len(lane_candidates) != len(set(lane_candidates))
    ):
        raise ValueError(f"{_LANE_NAME} release candidate overlap is partial or duplicated")
    for event in lane_events:
        candidate_id = str(event.get("hced_candidate_id"))
        if candidate_id not in WAVE8_CHADIAN_REBELS_CONTRACTS:
            raise ValueError(f"{_LANE_NAME} release event has a foreign candidate")
        contract = WAVE8_CHADIAN_REBELS_CONTRACTS[candidate_id]
        if event.get("id") != _event_id(candidate_id):
            raise ValueError(f"{_LANE_NAME} release event has a foreign owner")
        expected_entities = set(contract["side_1_entity_ids"]) | set(
            contract["side_2_entity_ids"]
        )
        if _participant_ids(event) != expected_entities:
            raise ValueError(f"{_LANE_NAME} released actor boundary changed")
        if event.get("event_type") != contract["event_type"]:
            raise ValueError(f"{_LANE_NAME} released granularity changed")

    if existing:
        by_event_id = {str(event.get("id")): event for event in existing}
        for event_id, boundary in WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES.items():
            event = by_event_id.get(event_id)
            if event is None:
                raise ValueError(f"{_LANE_NAME} current-release boundary disappeared: {event_id}")
            if (
                event.get("name") != boundary["expected_name"]
                or _row_year(event) != boundary["expected_year"]
                or int(event.get("end_year", event.get("year"))) != boundary["expected_end_year"]
                or _participant_ids(event) != set(boundary["expected_entity_ids"])
            ):
                raise ValueError(f"{_LANE_NAME} current-release boundary changed: {event_id}")

    boundary_event_ids = set(WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES)
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if str(event.get("id")) not in boundary_event_ids
        and event.get("hced_candidate_id") not in WAVE8_CHADIAN_REBELS_CONTRACT_IDS
        and any((_row_year(event), name) in pairs for name in _row_names(event))
    )
    if release_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed current-release twin(s): {release_twins}")
    released_ucdp = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("ucdp_candidate_id") in WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS
        or event.get("source_candidate_id") in WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS
    )
    if released_ucdp:
        raise ValueError(f"{_LANE_NAME} audited UCDP boundary entered release: {released_ucdp}")

    return {
        "current_release_boundaries": len(WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES),
        "hced_probable_twins": 0,
        "integration_dispositions": len(WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_candidates),
        "ucdp_overlap_dispositions": (
            len(WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS) if supplied_ucdp else 0
        ),
    }


def install_wave8_chadian_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities, WAVE8_CHADIAN_REBELS_ENTITIES, lane_name=_LANE_NAME
    )


def install_wave8_chadian_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id, WAVE8_CHADIAN_REBELS_SOURCES, lane_name=_LANE_NAME
    )


_OPERATIONAL_WIN = {
    "campaign_objective": 0.86,
    "theater_control": 0.82,
    "force_preservation": 0.72,
    "tempo_initiative": 0.84,
    "logistics_sustainment": 0.78,
}
_OPERATIONAL_LOSS = {key: round(1.0 - value, 2) for key, value in _OPERATIONAL_WIN.items()}


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_CHADIAN_REBELS_CONTRACTS[candidate_id]
        if candidate_id in WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)
        event["event_type"] = str(contract["event_type"])
        if event["event_type"] == "campaign":
            event["summary"] = (
                "Candidate-keyed Wave 8 operational urban-campaign assertion. The "
                "nine-month boundary, event-specific formations, and independent "
                "outcome evidence are pinned; no individual engagement or whole-war "
                "result is inferred. "
                + str(contract["audit_note"])
            )
            for participant in event["participants"]:
                if participant["side"] == "side_a":
                    participant["outcome"] = dict(_OPERATIONAL_WIN)
                    participant["termination"] = "campaign_victory"
                    participant["result_class"] = "major_operational_victory"
                else:
                    participant["outcome"] = dict(_OPERATIONAL_LOSS)
                    participant["termination"] = "campaign_defeat"
                    participant["result_class"] = "major_operational_defeat"
                participant["note"] = (
                    f"Candidate-keyed {_LANE_NAME} campaign contract; no generic "
                    "actor continuity or strategic civil-war outcome is inferred."
                )


def promote_wave8_chadian_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit exactly three bounded outcomes and no generic rebel identity."""

    validate_wave8_chadian_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CHADIAN_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    return events


def wave8_chadian_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_CHADIAN_REBELS_CONTRACTS.values(),
                    *WAVE8_CHADIAN_REBELS_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_chadian_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_rows": len(WAVE8_CHADIAN_REBELS_ADJACENT_CANDIDATE_IDS),
        "country_quarantine_additions": len(WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS),
        "current_release_boundaries": len(WAVE8_CHADIAN_REBELS_CURRENT_RELEASE_BOUNDARIES),
        "exact_hced_rows": len(WAVE8_CHADIAN_REBELS_EXACT_CANDIDATE_IDS),
        "holds": len(WAVE8_CHADIAN_REBELS_HOLDS),
        "integration_dispositions": len(WAVE8_CHADIAN_REBELS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_CHADIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS),
        "new_entities": len(WAVE8_CHADIAN_REBELS_ENTITIES),
        "new_sources": len(WAVE8_CHADIAN_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_CHADIAN_REBELS_CONTRACTS),
        "outcome_overrides": len(WAVE8_CHADIAN_REBELS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_CHADIAN_REBELS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CHADIAN_REBELS_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_CHADIAN_REBELS_TERMINAL_EXCLUSIONS),
        "ucdp_overlap_dispositions": len(WAVE8_CHADIAN_REBELS_UCDP_OVERLAP_DISPOSITIONS),
    }


def wave8_chadian_rebels_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_CHADIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_CHADIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_chadian_rebels_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_with_adjacent_spelling_ownership",
        "counts": wave8_chadian_rebels_counts(),
        "cohorts": wave8_chadian_rebels_cohort_counts(),
        "final_audit_signature": WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE,
        "module_owner": _MODULE_OWNER,
        "queue_sha256": {
            "hced": WAVE8_CHADIAN_REBELS_HCED_QUEUE_SHA256,
            "iwbd": WAVE8_CHADIAN_REBELS_IWBD_QUEUE_SHA256,
            "ucdp": dict(WAVE8_CHADIAN_REBELS_UCDP_QUEUE_SHA256),
        },
    }


_validate_static()
