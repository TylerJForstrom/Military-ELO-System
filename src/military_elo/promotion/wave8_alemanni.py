"""Combined exact-label Wave 8 lane for ``Alemanni`` and ``Alemmani``.

The current HCED snapshot contains five rows under each spelling.  They span
separate third-, fourth-, and fifth-century campaigns, so this lane installs
only event- or campaign-bounded formations.  The three engagements in
Aurelian's 270--271 Italian campaign share campaign-bounded actors; no other
row shares a rating identity and no generic ethnic or Roman bridge is opened.

Eight rows have source-attested tactical outcomes.  ``Rheims356`` is an army
assembly point in Ammianus, not an attested battle, and ``Zulpich496`` fuses
Gregory of Tours' unlocated victory of Clovis with his separate report that
Sigibert had once been wounded near Zulpich.  Those two assertions are
terminally excluded: an unknown outcome is never converted into a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_ALEMANNI_CONTRACT_IDS",
    "WAVE8_ALEMANNI_CONTRACTS",
    "WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS",
    "WAVE8_ALEMANNI_ENTITIES",
    "WAVE8_ALEMANNI_EXCLUSION_IDS",
    "WAVE8_ALEMANNI_EXCLUSIONS",
    "WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE",
    "WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ALEMANNI_HOLD_IDS",
    "WAVE8_ALEMANNI_HOLDS",
    "WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS",
    "WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_ALEMANNI_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ALEMANNI_NONPROMOTIONS",
    "WAVE8_ALEMANNI_OUTCOME_OVERRIDES",
    "WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ALEMANNI_RESERVED_IDS",
    "WAVE8_ALEMANNI_ROW_HASHES",
    "WAVE8_ALEMANNI_SOURCES",
    "WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS",
    "WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS",
    "install_wave8_alemanni_entities",
    "install_wave8_alemanni_sources",
    "promote_wave8_alemanni_contracts",
    "validate_wave8_alemanni_integration_dispositions",
    "validate_wave8_alemanni_queue_contracts",
    "wave8_alemanni_audit_signature",
    "wave8_alemanni_cohort_counts",
    "wave8_alemanni_counts",
    "wave8_alemanni_location_quarantine_additions",
    "wave8_alemanni_spelling_counts",
)


_LANE_NAME = "Wave 8 exact Alemanni/Alemmani formation audit"
_MODULE_OWNER = "wave8_alemanni"
_EVENT_ID_PREFIX = "hced_wave8_alemanni_"
_EXACT_LABELS = frozenset({"alemanni", "alemmani"})

_BENACUS_ROMANS_ID = "claudius_ii_roman_field_army_lake_benacus_268"
_BENACUS_ALAMANNI_ID = "alamannic_invasion_force_lake_benacus_268"
_AURELIAN_ROMANS_ID = "aurelian_roman_field_army_italy_271"
_AURELIAN_INVADERS_ID = "alamannic_iuthungian_invasion_force_italy_270_271"
_SENS_ROMANS_ID = "julian_roman_garrison_sens_356"
_SENS_ALAMANNI_ID = "alamannic_besieging_host_sens_356"
_CHALONS_ROMANS_ID = "jovinus_roman_field_army_chalons_366"
_CHALONS_ALAMANNI_ID = "alamannic_third_raiding_division_chalons_366"
_SOLICINIUM_ROMANS_ID = "valentinian_sebastianus_roman_army_solicinium_368"
_SOLICINIUM_ALAMANNI_ID = "alamannic_mountain_force_solicinium_368"
_CAMPI_ROMANS_ID = "burco_roman_detachment_campi_cannini_457"
_CAMPI_ALAMANNI_ID = "alamannic_raiding_band_campi_cannini_457"


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
    granularity: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    if granularity:
        roles.append("curated_reference_pending_claim_level_outcome_locator")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_ALEMANNI_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_alemanni_epitome_caesaribus_34_35",
        "Epitome de Caesaribus, chapters 34-35",
        "https://la.wikisource.org/wiki/Epitome_de_Caesaribus",
        "Wikisource transcription of the Latin primary text",
        "primary_source_transcription",
        "epitome_de_caesaribus_34_35",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_ric_online_history",
        "Roman Imperial Coinage Online: historical introduction, AD 268-276",
        "https://ric.mom.fr/en/info/hist",
        "CNRS HiSoMA and Maison de l'Orient et de la Mediterranee",
        "scholarly_numismatic_reference",
        "ric_online_268_276_history",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_bleckmann_lake_garda",
        "Epitome de Caesaribus, Landolfus Sagax und 300 000 Alamannen",
        (
            "https://journals.ub.uni-heidelberg.de/index.php/gfa/"
            "article/download/76988/70848"
        ),
        "Goettinger Forum fuer Altertumswissenschaft 2 (1999), 139-149",
        "peer_reviewed_source_critical_article",
        "bleckmann_alamanni_lake_garda_1999",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_historia_augusta_aurelian",
        "Historia Augusta, Life of Aurelian, chapters 18-21",
        (
            "https://penelope.uchicago.edu/thayer/e/roman/texts/"
            "historia_augusta/aurelian/2%2A.html"
        ),
        "LacusCurtius; Loeb Classical Library translation and notes",
        "translated_primary_source",
        "historia_augusta_aurelian_loeb",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_watson_aurelian",
        "Aurelian and the Third Century",
        (
            "https://www.routledge.com/Aurelian-and-the-Third-Century/"
            "Watson/p/book/9780415301879"
        ),
        "Routledge; Alaric Watson",
        "scholarly_monograph",
        "watson_aurelian_third_century",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_drinkwater_alamanni_rome",
        "The Alamanni and Rome 213-496: Caracalla to Clovis",
        "https://doi.org/10.1093/acprof:oso/9780199295685.001.0001",
        "Oxford University Press; John F. Drinkwater",
        "scholarly_monograph",
        "drinkwater_alamanni_and_rome_2007",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_ammianus_book_16",
        "Ammianus Marcellinus, Roman History, Book 16",
        "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ammian/16%2A.html",
        "LacusCurtius; Loeb Classical Library translation",
        "translated_primary_source",
        "ammianus_roman_history_loeb",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_ammianus_book_27",
        "Ammianus Marcellinus, Roman History, Book 27",
        "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ammian/27%2A.html",
        "LacusCurtius; Loeb Classical Library translation",
        "translated_primary_source",
        "ammianus_roman_history_loeb",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_sidonius_poem_5",
        "Sidonius Apollinaris, Complete Poems, Poem 5, lines 373-383",
        (
            "https://urn.ub.unibe.ch/urn%3Ach%3Aslsp%3A9781800348592%3Aihv%3Apdf"
        ),
        "Liverpool University Press, Translated Texts for Historians 76",
        "critical_translated_primary_source",
        "sidonius_complete_poems_green_2022",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_hummer_ethnogenesis",
        (
            "The fluidity of barbarian identity: the ethnogenesis of Alemanni "
            "and Suebi, AD 200-500"
        ),
        "https://www.ffzg.unizg.hr/arheo/ska/tekstovi/alemanni_suebi.pdf",
        "Early Medieval Europe 7.1 (1998); Hans J. Hummer",
        "peer_reviewed_historical_article",
        "hummer_alemanni_suebi_1998",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_campi_canini_location",
        (
            "Alle origini dei Grigioni: fatti d'arme combattuti sui Campi Canini, "
            "presso Bellinzona, nei secoli IV-VI d.C."
        ),
        "https://oaj.fupress.net/index.php/prometheus/article/view/513/513",
        "Prometheus, Firenze University Press",
        "peer_reviewed_historical_article",
        "campi_canini_bellinzona_prometheus",
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_alemanni_gregory_tours_book_2",
        "Gregory of Tours, History of the Franks, Book 2, chapters 30 and 37",
        "https://sourcebooks.web.fordham.edu/source/gregory-clovisconv.asp",
        "Fordham University Internet Medieval Sourcebook",
        "translated_primary_source",
        "gregory_tours_book_2_dalton_translation",
        crosscheck=True,
        granularity=True,
    ),
)


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


_NO_INHERITANCE = (
    "No rating is inherited by a timeless Alamannic, Alemanni, Alemmani, Roman, "
    "Frankish, or modern-state identity, or by another campaign formation."
)


WAVE8_ALEMANNI_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _BENACUS_ROMANS_ID,
        "Claudius II's Roman field army near Lake Benacus (268)",
        "event_bounded_field_command",
        268,
        268,
        "Northern Italy near Lake Benacus",
        "The field army credited with the Lake Benacus victory. " + _NO_INHERITANCE,
        [
            "wave8_alemanni_bleckmann_lake_garda",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_ric_online_history",
        ],
    ),
    _entity(
        _BENACUS_ALAMANNI_ID,
        "Alamannic invasion force near Lake Benacus (268)",
        "event_bounded_invasion_force",
        268,
        268,
        "Northern Italy near Lake Benacus",
        (
            "The Alamannic force defeated near Lake Benacus in the 268 invasion. "
            + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_bleckmann_lake_garda",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_epitome_caesaribus_34_35",
        ],
    ),
    _entity(
        _AURELIAN_ROMANS_ID,
        "Aurelian's Roman field army in the Italian campaign (271)",
        "campaign_bounded_field_command",
        271,
        271,
        "Northern and central Italy",
        (
            "Aurelian's field army across the linked Placentia, Metaurus-Fanum "
            "Fortunae, and Ticinensian engagements. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_ric_online_history",
            "wave8_alemanni_watson_aurelian",
        ],
    ),
    _entity(
        _AURELIAN_INVADERS_ID,
        "Alamannic-Juthungian invasion force in Italy (270-271)",
        "campaign_bounded_coalition",
        270,
        271,
        "Northern and central Italy",
        (
            "The invasion coalition opposed by Aurelian from Placentia through "
            "Fanum Fortunae and the Ticinensian Fields. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_ric_online_history",
            "wave8_alemanni_watson_aurelian",
        ],
    ),
    _entity(
        _SENS_ROMANS_ID,
        "Julian's Roman garrison at Sens (356)",
        "event_bounded_garrison",
        356,
        356,
        "Sens in Roman Gaul",
        (
            "Julian and the available Roman defenders who held Sens during the "
            "month-long siege. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _SENS_ALAMANNI_ID,
        "Alamannic besieging host at Sens (356)",
        "event_bounded_besieging_force",
        356,
        356,
        "Sens in Roman Gaul",
        (
            "The host that invested Sens and withdrew after failing to take it. "
            + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _CHALONS_ROMANS_ID,
        "Jovinus's Roman field army near Chalons-sur-Marne (366)",
        "event_bounded_field_command",
        366,
        366,
        "Near Chalons-sur-Marne in Roman Gaul",
        (
            "Jovinus's army in Ammianus' third and decisive engagement of the 366 "
            "campaign. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _CHALONS_ALAMANNI_ID,
        "Third Alamannic raiding division near Chalons-sur-Marne (366)",
        "event_bounded_raiding_force",
        366,
        366,
        "Near Chalons-sur-Marne in Roman Gaul",
        (
            "The third separated Alamannic division found and defeated near "
            "Chalons-sur-Marne. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _SOLICINIUM_ROMANS_ID,
        "Valentinian-Sebastianus Roman army at Solicinium (368)",
        "event_bounded_joint_command",
        368,
        368,
        "Alamannic territory at the unidentified Mount Solicinium",
        (
            "The coordinated Roman force described by Ammianus in the assault at "
            "Solicinium. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _SOLICINIUM_ALAMANNI_ID,
        "Alamannic mountain force at Solicinium (368)",
        "event_bounded_defending_force",
        368,
        368,
        "Alamannic territory at the unidentified Mount Solicinium",
        (
            "The Alamannic force holding the mountain position before its rout. "
            + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
    ),
    _entity(
        _CAMPI_ROMANS_ID,
        "Burco's Roman detachment at Campi Cannini (457)",
        "event_bounded_detachment",
        457,
        457,
        "Campi Canini route near Bellinzona",
        (
            "The small detachment sent by Majorian under Burco against the returning "
            "raiders. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_campi_canini_location",
            "wave8_alemanni_hummer_ethnogenesis",
            "wave8_alemanni_sidonius_poem_5",
        ],
    ),
    _entity(
        _CAMPI_ALAMANNI_ID,
        "Alamannic raiding band at Campi Cannini (457)",
        "event_bounded_raiding_force",
        457,
        457,
        "Campi Canini route near Bellinzona",
        (
            "The roughly nine-hundred-person raiding band in Sidonius, not a "
            "timeless ethnic army. " + _NO_INHERITANCE
        ),
        [
            "wave8_alemanni_campi_canini_location",
            "wave8_alemanni_hummer_ethnogenesis",
            "wave8_alemanni_sidonius_poem_5",
        ],
    ),
)


WAVE8_ALEMANNI_ROW_HASHES: dict[str, str] = {
    "hced-Campi Cannini457-1": (
        "ca15c209c43db023e5e53c469f1ee7eba476e7de273f6999f3266f8e13e46df2"
    ),
    "hced-Chalons366-1": (
        "ba5e083f0017e27dcb5bfb76925fb4933d8cce06637e758a4c4ad25409aa85d0"
    ),
    "hced-Fano271-1": (
        "24c9d60d88608fb0b468ab11b91274e6f18fdc9754abf30911da0c9de82cb545"
    ),
    "hced-Lake Benacus268-1": (
        "10d0872e45e2d72993c98cf9a644eed82a5f4d8c74e9a6f998df3d70c438ba7d"
    ),
    "hced-Pavia271-1": (
        "774e86f4b3f2c2a03c120b89e116446fc02e1066a308153e5428ec83d2184245"
    ),
    "hced-Placentia271-1": (
        "f2d992db81770b6f4e85243b1bfdce968d610805993373b2f8b3dc75c7baa54f"
    ),
    "hced-Rheims356-1": (
        "e07194549d39eb9b7aeb017c7b3f3dc2369abdf83d946ec11c123e4962527d51"
    ),
    "hced-Sens356-1": (
        "03d0bdad5a7f1445456ea4104e4385aecd59002f94b6116c4072b6f7f14d75e4"
    ),
    "hced-Solicinium368-1": (
        "a330cd2e8c81218bbadf60fd1f73a61140241f6ae4592e42ce8e114cd6d21da6"
    ),
    "hced-Zulpich496-1": (
        "6c143ed6bdf3a8e1ec3c12b595a764af57485558908363f86672759427da369f"
    ),
}


WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE: dict[str, str] = {
    "hced-Campi Cannini457-1": "Alemmani",
    "hced-Chalons366-1": "Alemmani",
    "hced-Fano271-1": "Alemanni",
    "hced-Lake Benacus268-1": "Alemmani",
    "hced-Pavia271-1": "Alemanni",
    "hced-Placentia271-1": "Alemmani",
    "hced-Rheims356-1": "Alemmani",
    "hced-Sens356-1": "Alemanni",
    "hced-Solicinium368-1": "Alemanni",
    "hced-Zulpich496-1": "Alemanni",
}


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_ALEMANNI_SOURCES
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
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
    winner_ids: Iterable[str],
    loser_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    historical_review: Mapping[str, Any],
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ALEMANNI_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, winner_ids))),
        "side_2_entity_ids": sorted(set(map(str, loser_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
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
        "historical_review": dict(historical_review),
    }


WAVE8_ALEMANNI_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Lake Benacus268-1": _contract(
        "hced-Lake Benacus268-1",
        _canonical("Battle near Lake Benacus", 268, "268 CE"),
        "claudius_alamannic_campaign_268",
        [_BENACUS_ROMANS_ID],
        [_BENACUS_ALAMANNI_ID],
        [
            "wave8_alemanni_bleckmann_lake_garda",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_ric_online_history",
        ],
        [
            "wave8_alemanni_bleckmann_lake_garda",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_ric_online_history",
        ],
        (
            "The Epitome places Claudius's defeat of the Alamanni near Lake "
            "Benacus; modern numismatic history and source criticism support the "
            "victory in 268 while acknowledging the broader 268/269 chronology."
        ),
        {
            "dating_boundary": "HCED's exact 268 row is retained; no adjacent event is merged",
            "opposing_formation": "event-bounded Alamannic invasion force",
            "outcome": "roman_victory",
        },
        confidence=0.87,
    ),
    "hced-Placentia271-1": _contract(
        "hced-Placentia271-1",
        _canonical("Battle of Placentia", 271, "271 CE"),
        "aurelian_italian_campaign_271",
        [_AURELIAN_INVADERS_ID],
        [_AURELIAN_ROMANS_ID],
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_ric_online_history",
            "wave8_alemanni_watson_aurelian",
        ],
        [
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_ric_online_history",
            "wave8_alemanni_watson_aurelian",
        ],
        (
            "Historia Augusta explicitly reports Aurelian's severe defeat in an "
            "ambush near Placentia; modern studies identify the invaders as an "
            "Alamannic-Juthungian campaign force."
        ),
        {
            "mechanism": "ambush in wooded terrain",
            "outcome": "alamannic_iuthungian_victory",
            "roman_commander": "Aurelian",
        },
        confidence=0.93,
    ),
    "hced-Fano271-1": _contract(
        "hced-Fano271-1",
        _canonical("Battle at Fanum Fortunae and the Metaurus", 271, "271 CE"),
        "aurelian_italian_campaign_271",
        [_AURELIAN_ROMANS_ID],
        [_AURELIAN_INVADERS_ID],
        [
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_watson_aurelian",
        ],
        [
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_watson_aurelian",
        ],
        (
            "The primary summaries and modern campaign study distinguish the "
            "Roman recovery at Fanum Fortunae by the Metaurus from both the earlier "
            "Placentia defeat and the later Ticinensian victory."
        ),
        {
            "boundary": "distinct middle engagement of the 271 Italian campaign",
            "outcome": "roman_victory",
            "raw_name_resolution": "Fano is Fanum Fortunae by the Metaurus",
        },
        confidence=0.91,
    ),
    "hced-Pavia271-1": _contract(
        "hced-Pavia271-1",
        _canonical("Battle on the Ticinensian Fields", 271, "271 CE"),
        "aurelian_italian_campaign_271",
        [_AURELIAN_ROMANS_ID],
        [_AURELIAN_INVADERS_ID],
        [
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_watson_aurelian",
        ],
        [
            "wave8_alemanni_epitome_caesaribus_34_35",
            "wave8_alemanni_historia_augusta_aurelian",
            "wave8_alemanni_watson_aurelian",
        ],
        (
            "The Ticinensian-fields victory is the final engagement of the same "
            "bounded invasion campaign; 'Pavia' is retained only as the HCED alias, "
            "not as a precise battlefield coordinate."
        ),
        {
            "boundary": "distinct final engagement of the 271 Italian campaign",
            "outcome": "roman_victory",
            "raw_name_resolution": "Pavia represents the Ticinensian Fields",
        },
        confidence=0.91,
    ),
    "hced-Sens356-1": _contract(
        "hced-Sens356-1",
        _canonical("Siege of Sens", 356, "356 CE", granularity="siege"),
        "julian_gaul_campaign_356",
        [_SENS_ROMANS_ID],
        [_SENS_ALAMANNI_ID],
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        (
            "Ammianus reports that the Alamannic host besieged Julian at Sens for "
            "a month and then withdrew without taking the city.  The rated result "
            "is the defenders' completed siege objective, not a field battle."
        ),
        {
            "granularity": "siege",
            "mechanism": "besiegers withdrew after a month without taking Sens",
            "outcome": "roman_defensive_victory",
        },
        confidence=0.96,
    ),
    "hced-Chalons366-1": _contract(
        "hced-Chalons366-1",
        _canonical("Battle near Chalons-sur-Marne", 366, "366 CE"),
        "jovinus_alamannic_campaign_366",
        [_CHALONS_ROMANS_ID],
        [_CHALONS_ALAMANNI_ID],
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        (
            "Ammianus explicitly locates Jovinus's third engagement near "
            "Chalons-sur-Marne and reports a decisive Roman victory over the third "
            "separated Alamannic raiding division."
        ),
        {
            "campaign_sequence": "third engagement against separated raiding divisions",
            "outcome": "roman_victory",
            "roman_commander": "Jovinus",
        },
        confidence=0.97,
    ),
    "hced-Solicinium368-1": _contract(
        "hced-Solicinium368-1",
        _canonical("Battle of Solicinium", 368, "368 CE"),
        "valentinian_alamannic_campaign_368",
        [_SOLICINIUM_ROMANS_ID],
        [_SOLICINIUM_ALAMANNI_ID],
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        [
            "wave8_alemanni_ammianus_book_27",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        (
            "Ammianus describes the coordinated Roman assault on the Alamannic "
            "mountain position and the defenders' rout.  The formation is bounded "
            "to that engagement because Mount Solicinium's location is disputed."
        ),
        {
            "location_boundary": "Mount Solicinium is not securely identified",
            "outcome": "roman_victory",
            "roman_commands": ["Sebastianus", "Valentinian I"],
        },
        confidence=0.95,
    ),
    "hced-Campi Cannini457-1": _contract(
        "hced-Campi Cannini457-1",
        _canonical("Battle of Campi Cannini", 457, "457 CE"),
        "majorian_northern_italy_457",
        [_CAMPI_ROMANS_ID],
        [_CAMPI_ALAMANNI_ID],
        [
            "wave8_alemanni_campi_canini_location",
            "wave8_alemanni_hummer_ethnogenesis",
            "wave8_alemanni_sidonius_poem_5",
        ],
        [
            "wave8_alemanni_hummer_ethnogenesis",
            "wave8_alemanni_sidonius_poem_5",
        ],
        (
            "Sidonius reports Majorian sending a small detachment under Burco that "
            "defeated the returning raiding band; Hummer treats the episode as a "
            "457 victory while warning against turning the band into an ethnic army."
        ),
        {
            "opposing_scale": "raiding band described as about nine hundred",
            "outcome": "roman_detachment_victory",
            "roman_commander": "Burco, acting for Majorian",
        },
        confidence=0.91,
    ),
}


WAVE8_ALEMANNI_HOLDS: dict[str, dict[str, Any]] = {}


def _terminal_exclusion(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    historical_review: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_ALEMANNI_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": canonical_event["granularity"],
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
        "historical_review": dict(historical_review),
    }


WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Rheims356-1": _terminal_exclusion(
        "hced-Rheims356-1",
        _canonical(
            "Roman army assembly at Rheims in Julian's campaign",
            356,
            "356 CE",
            granularity="campaign_assembly_not_battle",
        ),
        "julian_gaul_campaign_356",
        "named_place_is_an_assembly_point_not_an_attested_engagement",
        (
            "Ammianus identifies Rheims as the place where the army assembled and "
            "received provisions before marching onward; his narrated battle is "
            "at Brumath, not Rheims.  The exact HCED battle has no source-attested "
            "result, cannot produce an Elo event, and unknown is never made a draw."
        ),
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
        ],
        {
            "attested_action": "army assembly and provisioning",
            "excluded_inference": "a Roman victory at Rheims",
            "nearby_battle_boundary": "the later engagement is at Brumath, not Rheims",
        },
    ),
    "hced-Zulpich496-1": _terminal_exclusion(
        "hced-Zulpich496-1",
        _canonical(
            "Conflated Clovis victory and Sigibert battle near Zulpich",
            496,
            "traditionally 496 CE",
            granularity="source_conflation",
        ),
        "clovis_alamannic_war_source_conflation",
        "date_place_and_victor_are_combined_from_separate_source_passages",
        (
            "Gregory of Tours reports Clovis defeating the Alamanni without naming "
            "Zulpich or an exact year, then separately says Sigibert had once been "
            "wounded in a battle with Alamanni near Zulpich.  Assigning Clovis's "
            "victory to HCED's exact Zulpich 496 row would fuse those passages.  It "
            "cannot produce an Elo event, and unknown is never made a draw."
        ),
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanni_gregory_tours_book_2",
        ],
        {
            "clovis_passage": "victory attested without Zulpich or an exact year",
            "sigibert_passage": "separate past battle near Zulpich",
            "repair_risk": "would merge different actors and source episodes",
        },
    ),
}


WAVE8_ALEMANNI_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ALEMANNI_HOLDS,
    **WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS,
}
WAVE8_ALEMANNI_EXCLUSIONS = WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS

WAVE8_ALEMANNI_CONTRACT_IDS = frozenset(WAVE8_ALEMANNI_CONTRACTS)
WAVE8_ALEMANNI_HOLD_IDS = frozenset(WAVE8_ALEMANNI_HOLDS)
WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS
)
WAVE8_ALEMANNI_EXCLUSION_IDS = WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS
WAVE8_ALEMANNI_RESERVED_IDS = frozenset(
    WAVE8_ALEMANNI_CONTRACT_IDS
    | WAVE8_ALEMANNI_HOLD_IDS
    | WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS
)
WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_ALEMANNI_ROW_HASHES)


WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Campi Cannini457-1": {
        "actions": ["withhold_country", "withhold_point"],
        "reason": (
            "The HCED point and Italy label are not supported by the Campi Canini "
            "location literature, which places the route near Bellinzona in modern "
            "Switzerland without fixing an exact battlefield coordinate."
        ),
    },
    "hced-Chalons366-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Ammianus says the battle was near Chalons-sur-Marne but does not "
            "support HCED's exact modern coordinate."
        ),
    },
    "hced-Fano271-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Fanum Fortunae and the Metaurus define the episode, not HCED's modern "
            "Fano centroid as an audited battlefield point."
        ),
    },
    "hced-Lake Benacus268-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The sources locate the battle near Lake Benacus but do not attest the "
            "specific point staged in HCED."
        ),
    },
    "hced-Pavia271-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The source tradition identifies the Ticinensian Fields, not the modern "
            "Pavia centroid as a precise battlefield coordinate."
        ),
    },
    "hced-Placentia271-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Historia Augusta says the ambush was near Placentia in wooded terrain; "
            "the exact HCED coordinate is not source-audited."
        ),
    },
    "hced-Sens356-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The event is a siege of Sens; the modern city centroid is not an "
            "audited point for the ancient defenses."
        ),
    },
    "hced-Solicinium368-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Mount Solicinium remains unidentified, so the staged Schwetzingen-area "
            "coordinate cannot be promoted."
        ),
    },
}
WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, item in WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS.items()
    if "withhold_point" in item["actions"]
)
WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, item in WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS.items()
    if "withhold_country" in item["actions"]
)
WAVE8_ALEMANNI_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_ALEMANNI_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _aliases(*values: str) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Campi Cannini457-1": {
        "aliases": _aliases(
            "battle of campi canini",
            "battle of campi cannini",
            "campi cani",
            "campi canini",
            "campi cannini",
            "canine fields",
        ),
        "years": (457, 457),
    },
    "hced-Chalons366-1": {
        "aliases": _aliases(
            "battle near chalons",
            "battle near chalons-sur-marne",
            "chalons",
            "chalons-sur-marne",
            "chalons sur marne",
            "châlons",
        ),
        "years": (366, 366),
    },
    "hced-Fano271-1": {
        "aliases": _aliases(
            "battle at fanum fortunae and the metaurus",
            "battle of fano",
            "fano",
            "fanum fortunae",
            "metaurus",
        ),
        "years": (271, 271),
    },
    "hced-Lake Benacus268-1": {
        "aliases": _aliases(
            "battle near lake benacus",
            "benacus",
            "lacus benacus",
            "lake benacus",
            "lake garda",
        ),
        "years": (268, 269),
    },
    "hced-Pavia271-1": {
        "aliases": _aliases(
            "battle of pavia",
            "battle of ticinum",
            "battle on the ticinensian fields",
            "pavia",
            "ticinum",
            "ticinensian fields",
        ),
        "years": (271, 271),
    },
    "hced-Placentia271-1": {
        "aliases": _aliases(
            "battle of placentia",
            "piacenza",
            "placentia",
        ),
        "years": (271, 271),
    },
    "hced-Rheims356-1": {
        "aliases": _aliases("durocortorum", "reims", "rheims"),
        "years": (356, 356),
    },
    "hced-Sens356-1": {
        "aliases": _aliases(
            "battle of sens",
            "senonae",
            "senones",
            "sens",
            "siege of sens",
        ),
        "years": (356, 356),
    },
    "hced-Solicinium368-1": {
        "aliases": _aliases(
            "battle of solicinium",
            "solicinio",
            "solicinium",
        ),
        "years": (368, 368),
    },
    "hced-Zulpich496-1": {
        "aliases": _aliases(
            "battle of tolbiac",
            "battle of zulpich",
            "tolbiac",
            "tolbiacum",
            "zulpich",
            "zülpich",
        ),
        "years": (496, 506),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ALEMANNI_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_ALEMANNI_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS),
        "expected_spelling_by_candidate": (
            WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE
        ),
        "holds": WAVE8_ALEMANNI_HOLDS,
        "integration_dispositions": WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_ALEMANNI_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_ALEMANNI_ROW_HASHES,
        "sources": WAVE8_ALEMANNI_SOURCES,
        "terminal_exclusions": WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS,
    }


def wave8_alemanni_audit_signature() -> str:
    """Return the SHA-256 pin over the complete combined-lane adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE = (
    "73268ff3b80dad527d43172a5774ea1a386bf4e90ca919e91ce87d98d22848ad"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


_EXPECTED_ACTOR_PAIRS = {
    "hced-Campi Cannini457-1": (_CAMPI_ROMANS_ID, _CAMPI_ALAMANNI_ID),
    "hced-Chalons366-1": (_CHALONS_ROMANS_ID, _CHALONS_ALAMANNI_ID),
    "hced-Fano271-1": (_AURELIAN_ROMANS_ID, _AURELIAN_INVADERS_ID),
    "hced-Lake Benacus268-1": (_BENACUS_ROMANS_ID, _BENACUS_ALAMANNI_ID),
    "hced-Pavia271-1": (_AURELIAN_ROMANS_ID, _AURELIAN_INVADERS_ID),
    "hced-Placentia271-1": (_AURELIAN_INVADERS_ID, _AURELIAN_ROMANS_ID),
    "hced-Sens356-1": (_SENS_ROMANS_ID, _SENS_ALAMANNI_ID),
    "hced-Solicinium368-1": (
        _SOLICINIUM_ROMANS_ID,
        _SOLICINIUM_ALAMANNI_ID,
    ),
}


def _validate_static() -> None:
    if (
        len(WAVE8_ALEMANNI_CONTRACTS),
        len(WAVE8_ALEMANNI_HOLDS),
        len(WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS),
    ) != (8, 0, 2):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_ALEMANNI_ENTITIES), len(WAVE8_ALEMANNI_SOURCES)) != (12, 12):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_ALEMANNI_RESERVED_IDS != WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE) != set(
        WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} spelling inventory is incomplete")
    if Counter(WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE.values()) != {
        "Alemanni": 5,
        "Alemmani": 5,
    }:
        raise ValueError(f"{_LANE_NAME} spelling cohort changed")
    dispositions = (
        WAVE8_ALEMANNI_CONTRACT_IDS,
        WAVE8_ALEMANNI_HOLD_IDS,
        WAVE8_ALEMANNI_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[left] & dispositions[right]
        for left in range(3)
        for right in range(left + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_alemanni_audit_signature() != WAVE8_ALEMANNI_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_ALEMANNI_SOURCES}
    if len(source_by_id) != len(WAVE8_ALEMANNI_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    families = [str(source["source_family_id"]) for source in WAVE8_ALEMANNI_SOURCES]
    if any(not family for family in families) or len(set(families)) != 11:
        raise ValueError(f"{_LANE_NAME} bibliographic source families drifted")
    for source in WAVE8_ALEMANNI_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_ALEMANNI_ENTITIES}
    if len(entity_by_id) != len(WAVE8_ALEMANNI_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "alamanni",
        "alemanni",
        "alemmani",
        "franks",
        "rome",
        "roman empire",
    }
    for entity in WAVE8_ALEMANNI_ENTITIES:
        start = int(entity["start_year"])
        end = int(entity["end_year"])
        if start > end or end - start > 1:
            raise ValueError(f"{_LANE_NAME} identity is not event/campaign bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern-state" not in note:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_ALEMANNI_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_ALEMANNI_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        expected_granularity = "siege" if candidate_id == "hced-Sens356-1" else "engagement"
        if canonical["granularity"] != expected_granularity:
            raise ValueError(f"{_LANE_NAME} promoted granularity drifted")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        expected_pair = _EXPECTED_ACTOR_PAIRS[candidate_id]
        if side_1 != [expected_pair[0]] or side_2 != [expected_pair[1]]:
            raise ValueError(f"{_LANE_NAME} formation boundary drifted")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded identity")
        used_entities.update(side_1)
        used_entities.update(side_2)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor policy drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        outcome_families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            not outcomes
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if outcome_families != expected_families or len(outcome_families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    aurelian_candidates = {
        "hced-Fano271-1",
        "hced-Pavia271-1",
        "hced-Placentia271-1",
    }
    for candidate_id, pair in _EXPECTED_ACTOR_PAIRS.items():
        pair_set = set(pair)
        if candidate_id not in aurelian_candidates and pair_set & {
            _AURELIAN_ROMANS_ID,
            _AURELIAN_INVADERS_ID,
        }:
            raise ValueError(f"{_LANE_NAME} leaked the 271 campaign bridge")

    forbidden_nonpromotion_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, item in WAVE8_ALEMANNI_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_ALEMANNI_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if forbidden_nonpromotion_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a rateable result")
        if (
            item["disposition"] != "terminal_exclusion"
            or item["terminal_exclusion"] is not True
            or item["reviewed_outcome"] != "unknown"
            or item["unknown_is_never_draw"] is not True
            or "never made a draw" not in str(item["hold_reason"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} terminal policy drifted")
        if item["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} nonpromotion ownership drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_ALEMANNI_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS != WAVE8_ALEMANNI_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} promoted-only point quarantine changed")
    if WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Campi Cannini457-1"
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine inventory changed")
    if set(WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS) != set(
        WAVE8_ALEMANNI_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for item in WAVE8_ALEMANNI_LOCATION_QUARANTINE_REASONS.values():
        if not _is_sorted_unique(item["actions"]):
            raise ValueError(f"{_LANE_NAME} location actions are not canonical")
        if not set(item["actions"]) <= {"withhold_country", "withhold_point"}:
            raise ValueError(f"{_LANE_NAME} location action is unsupported")

    if (
        WAVE8_ALEMANNI_OUTCOME_OVERRIDES
        or WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS
        or WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT) != set(
        WAVE8_ALEMANNI_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(item["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases drifted")
        low, high = map(int, item["years"])
        if low > high:
            raise ValueError(f"{_LANE_NAME} duplicate year range drifted")


def _is_exact_lane_label(value: Any) -> bool:
    return normalize_label(value) in _EXACT_LABELS


def validate_wave8_alemanni_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all ten exact spelling rows and immutable row fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ALEMANNI_CONTRACTS,
        WAVE8_ALEMANNI_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_rows = [
        row
        for row in hced_rows
        if _is_exact_lane_label(row.get("side_1_raw"))
        or _is_exact_lane_label(row.get("side_2_raw"))
    ]
    exact_label_ids = {str(row.get("candidate_id")) for row in exact_rows}
    if exact_label_ids != WAVE8_ALEMANNI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Alemanni/Alemmani inventory changed: "
            f"{sorted(exact_label_ids)}"
        )

    observed_spellings: Counter[str] = Counter()
    for row in exact_rows:
        candidate_id = str(row.get("candidate_id"))
        hits = [
            value
            for value in (row.get("side_1_raw"), row.get("side_2_raw"))
            if _is_exact_lane_label(value)
        ]
        expected = WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE[candidate_id]
        if len(hits) != 1 or hits[0] != expected:
            raise ValueError(
                f"{_LANE_NAME} exact spelling drift for {candidate_id}: {hits}"
            )
        observed_spellings[str(hits[0])] += 1
    if observed_spellings != {"Alemanni": 5, "Alemmani": 5}:
        raise ValueError(f"{_LANE_NAME} spelling cohort changed: {observed_spellings}")

    return {
        "exact_alemanni_rows": observed_spellings["Alemanni"],
        "exact_alemmani_rows": observed_spellings["Alemmani"],
        "holds": len(WAVE8_ALEMANNI_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases", [])
    if isinstance(aliases, (list, tuple, set)):
        names.update(normalize_label(alias) for alias in aliases)
    return {name for name in names if name}


_DUPLICATE_MATCH_KEYS = {
    (year, normalize_label(alias))
    for item in WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(item["years"][0]), int(item["years"][1]) + 1)
    for alias in item["aliases"]
}


def _probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row))


def validate_wave8_alemanni_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue, lane, or release adds a probable twin."""

    validate_wave8_alemanni_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ALEMANNI_RESERVED_IDS
        and _probable_twin(row)
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")

    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _probable_twin(row)
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")

    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_ALEMANNI_CONTRACT_IDS
        and _probable_twin(event)
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )

    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT),
    }


def install_wave8_alemanni_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ALEMANNI_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_alemanni_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ALEMANNI_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_alemanni_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_alemanni_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ALEMANNI_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_alemanni_cohort_counts() -> dict[str, int]:
    """Return cohort counts across promotions and terminal ownership."""

    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_ALEMANNI_CONTRACTS.values(),
                    *WAVE8_ALEMANNI_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_alemanni_spelling_counts() -> dict[str, int]:
    """Return the pinned exact-label split in the current HCED snapshot."""

    _validate_static()
    return dict(
        sorted(Counter(WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE.values()).items())
    )


def wave8_alemanni_counts() -> dict[str, int]:
    _validate_static()
    spelling = Counter(WAVE8_ALEMANNI_EXPECTED_SPELLING_BY_CANDIDATE.values())
    return {
        "country_quarantine_additions": len(
            WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_ALEMANNI_CROSS_LANE_DISPOSITIONS),
        "exact_alemanni_rows": spelling["Alemanni"],
        "exact_alemmani_rows": spelling["Alemmani"],
        "existing_release_duplicate_dispositions": len(
            WAVE8_ALEMANNI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_ALEMANNI_HOLDS),
        "integration_dispositions": len(WAVE8_ALEMANNI_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_ALEMANNI_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_ALEMANNI_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_ALEMANNI_ENTITIES),
        "new_sources": len(WAVE8_ALEMANNI_SOURCES),
        "newly_rated_events": len(WAVE8_ALEMANNI_CONTRACTS),
        "outcome_overrides": len(WAVE8_ALEMANNI_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ALEMANNI_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ALEMANNI_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_ALEMANNI_TERMINAL_EXCLUSIONS),
    }


def wave8_alemanni_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable, promoted-only location quarantine additions."""

    _validate_static()
    return {
        "country": WAVE8_ALEMANNI_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_ALEMANNI_POINT_QUARANTINE_ADDITIONS,
    }
