"""Candidate-keyed Wave 8 audit for HCED's exact ``Thebes`` label.

The staged cohort contains six ancient-Greek rows from 447 to 335 BCE.  The
literal label does not identify one continuous polity or army.  Coronea's
victors were a Boeotian-exile coalition rather than Thebes; Delium and Leuctra
were fought by federal Boeotian armies; Tegyra by Pelopidas's small Theban
force; Mantinea by a broad Theban-led coalition; and the 335 BCE row by civic
defenders of a revolt against Alexander.  This lane therefore installs only
event-bounded field formations and never a timeless ``Thebes`` alias.

All six tactical outcomes are independently attested and are promoted.  The
raw Mantinea ``Draw`` is corrected to the source-attested Theban-led tactical
victory while preserving the sources' separate conclusion that the battle had
no decisive strategic payoff after Epaminondas fell.  Unknown is never treated
as a draw.  Holds and terminal exclusions are explicitly owned and empty.
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
    "WAVE8_THEBES_CONTRACT_IDS",
    "WAVE8_THEBES_CONTRACTS",
    "WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_THEBES_CROSS_LANE_DISPOSITIONS",
    "WAVE8_THEBES_ENTITIES",
    "WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_THEBES_EXCLUSION_IDS",
    "WAVE8_THEBES_EXCLUSIONS",
    "WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_THEBES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_THEBES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_THEBES_HOLD_IDS",
    "WAVE8_THEBES_HOLDS",
    "WAVE8_THEBES_INTEGRATION_DISPOSITIONS",
    "WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_THEBES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_THEBES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_THEBES_NONPROMOTIONS",
    "WAVE8_THEBES_OUTCOME_OVERRIDES",
    "WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_THEBES_RESERVED_IDS",
    "WAVE8_THEBES_SOURCES",
    "WAVE8_THEBES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_THEBES_TERMINAL_EXCLUSIONS",
    "install_wave8_thebes_entities",
    "install_wave8_thebes_sources",
    "promote_wave8_thebes_contracts",
    "validate_wave8_thebes_integration_dispositions",
    "validate_wave8_thebes_queue_contracts",
    "wave8_thebes_audit_signature",
    "wave8_thebes_cohort_counts",
    "wave8_thebes_counts",
    "wave8_thebes_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Thebes actor audit"
_EVENT_ID_PREFIX = "hced_wave8_thebes_"
_MODULE_OWNER = "military_elo.promotion.wave8_thebes"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
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


WAVE8_THEBES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_thebes_thucydides_coronea",
        "Thucydides, History of the Peloponnesian War 1.113: Coronea",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A"
            "1999.01.0200%3Abook%3D1%3Achapter%3D113"
        ),
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "thucydides_peloponnesian_war_crawley",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_dull_coronea",
        "Thucydides 1.113 and the Leadership of Orchomenus",
        "https://www.jstor.org/stable/267879",
        "Classical Philology / University of Chicago Press",
        "peer_reviewed_scholarly_article",
        "dull_coronea_orchomenus_1977",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_van_wijk_athens_boiotia",
        (
            "The Attic Neighbour? A Short Chronological Overview of "
            "Atheno-Boiotian Relations"
        ),
        (
            "https://www.cambridge.org/core/books/athens-and-boiotia/"
            "attic-neighbour/76EF4754B60E745DFA2DDD62C1FB7F19"
        ),
        "Cambridge University Press",
        "open_access_scholarly_monograph_chapter",
        "van_wijk_athens_and_boiotia_2024",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_thucydides_delium",
        "Thucydides, History of the Peloponnesian War 4.89-101: Delium",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A"
            "1999.01.0200%3Abook%3D4"
        ),
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "thucydides_peloponnesian_war_crawley",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_lucas_boeotian_army",
        "L'organisation militaire de la confédération béotienne (447-171 av. J.-C.)",
        "https://books.openedition.org/efa/15868",
        "École française d'Athènes",
        "open_access_scholarly_monograph",
        "lucas_boeotian_military_organization_2023",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_hammond_boeotia",
        "Political Developments in Boeotia",
        (
            "https://www.cambridge.org/core/journals/classical-quarterly/"
            "article/political-developments-in-boeotia/"
            "AC1562330D7EDE3100E3AB70C37AE757"
        ),
        "The Classical Quarterly / Cambridge University Press",
        "peer_reviewed_scholarly_article",
        "hammond_political_developments_boeotia_2000",
        outcome=False,
    ),
    _source(
        "wave8_thebes_plutarch_pelopidas",
        "Plutarch, Life of Pelopidas 16-23: Tegyra and Leuctra",
        "https://penelope.uchicago.edu/Thayer/e/roman/texts/plutarch/lives/pelopidas%2A.html",
        "University of Chicago LacusCurtius",
        "translated_primary_source",
        "plutarch_pelopidas_perrin",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_buckler_beck_tegyra",
        "The battle of Tegyra, 375 BC",
        (
            "https://www.cambridge.org/core/books/central-greece-and-the-politics-"
            "of-power-in-the-fourth-century-bc/battle-of-tegyra-375-bc/"
            "707C6396118CC26949753D47C7FF2A51"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "buckler_beck_central_greece_2008",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_xenophon_leuctra",
        "Xenophon, Hellenica 6.4: Leuctra",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A"
            "1999.01.0206%3Abook%3D6%3Achapter%3D4"
        ),
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "xenophon_hellenica_brownson",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_buckler_beck_leuctra",
        "Plutarch on Leuctra",
        (
            "https://www.cambridge.org/core/books/central-greece-and-the-politics-"
            "of-power-in-the-fourth-century-bc/plutarch-on-leuctra/"
            "62A8242B61E5E075DF9DB04E0092BAB8"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "buckler_beck_central_greece_2008",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_xenophon_mantinea",
        "Xenophon, Hellenica 7.5.18-27: Mantinea",
        "https://www.perseus.tufts.edu/hopper/text?doc=Xen.+Hell.+7.5&lang=original",
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "xenophon_hellenica_brownson",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_shipley_mantinea",
        "Warfare and Control",
        (
            "https://www.cambridge.org/core/books/early-hellenistic-peloponnese/"
            "warfare-and-control/7C1B225BBF6AD84FADF4320C3A38BE03"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "shipley_early_hellenistic_peloponnese_2018",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_diodorus_book17",
        "Diodorus Siculus, Library of History 17.8-14: Thebes",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A"
            "1999.01.0084%3Abook%3D17"
        ),
        "Perseus Digital Library, Tufts University",
        "translated_primary_source",
        "diodorus_library_oldfather",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_flower_panhellenism",
        "Alexander the Great and Panhellenism",
        "https://academic.oup.com/book/9564/chapter-abstract/156576753",
        "Oxford University Press",
        "scholarly_history_chapter",
        "flower_alexander_panhellenism_2000",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_thebes_bosworth_alexander",
        "Alexander III, 'the Great', of Macedon, 356-323 BCE",
        "https://academic.oup.com/edited-volume/61673/chapter-abstract/548059801",
        "Oxford Classical Dictionary / Oxford University Press",
        "scholarly_reference_entry",
        "bosworth_oxford_alexander_2015",
        outcome=True,
        crosscheck=True,
    ),
)


_CORONEA_EXILES_ID = (
    "orchomenian_boeotian_exiles_locrian_euboean_exiles_coronea_447_bce"
)
_CORONEA_ATHENIAN_ID = "tolmides_athenian_allied_force_coronea_447_bce"
_DELIUM_BOEOTIAN_ID = "boeotian_federal_field_army_delium_424_bce"
_DELIUM_ATHENIAN_ID = "hippocrates_athenian_field_army_delium_424_bce"
_TEGYRA_THEBAN_ID = "pelopidas_sacred_band_cavalry_tegyra_375_bce"
_TEGYRA_SPARTAN_ID = "spartan_orchomenus_garrison_force_tegyra_375_bce"
_LEUCTRA_BOEOTIAN_ID = "epaminondas_boeotian_field_army_leuctra_371_bce"
_LEUCTRA_LACEDAEMONIAN_ID = "cleombrotus_lacedaemonian_allied_army_leuctra_371_bce"
_MANTINEA_THEBAN_ID = "epaminondas_theban_allied_army_mantinea_362_bce"
_MANTINEA_OPPOSITION_ID = "spartan_athenian_mantinean_allied_army_362_bce"
_THEBES_ASSAULT_ID = "alexander_macedonian_greek_assault_force_thebes_335_bce"
_THEBES_DEFENDERS_ID = "theban_rebel_civic_defenders_335_bce"


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    actor_boundary: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            actor_boundary
            + " No rating is inherited from or passed to an earlier or later "
            "Theban, Boeotian, Athenian, Spartan, or Macedonian regime, any "
            "same-name Thebes elsewhere, or any modern state."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_THEBES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _CORONEA_EXILES_ID,
        (
            "Orchomenian Boeotian exiles, Locrians, and Euboean exiles at "
            "Coronea (447 BCE)"
        ),
        "field_coalition",
        -447,
        "Coronea and north-western Boeotia",
        (
            "Bounded to the Orchomenian-led Boeotian exiles, Locrian allies, "
            "Euboean exiles, and others of the same party who attacked Tolmides; "
            "it is not Thebes."
        ),
        [
            "wave8_thebes_dull_coronea",
            "wave8_thebes_thucydides_coronea",
            "wave8_thebes_van_wijk_athens_boiotia",
        ],
    ),
    _entity(
        _CORONEA_ATHENIAN_ID,
        "Tolmides's Athenian and allied expedition at Coronea (447 BCE)",
        "field_force",
        -447,
        "Chaeronea-Coronea, Boeotia",
        (
            "Bounded to the one-thousand-hoplite Athenian core, allied contingents, "
            "and Tolmides's return march from Chaeronea."
        ),
        [
            "wave8_thebes_dull_coronea",
            "wave8_thebes_thucydides_coronea",
            "wave8_thebes_van_wijk_athens_boiotia",
        ],
    ),
    _entity(
        _DELIUM_BOEOTIAN_ID,
        "Boeotian federal field army under Pagondas at Delium (424 BCE)",
        "federal_field_army",
        -424,
        "Delium and the Attic-Boeotian frontier",
        (
            "Bounded to the assembled Boeotian army: its Theban right wing and "
            "the Haliartian, Coronean, Copaean, Thespian, Tanagraean, "
            "Orchomenian, cavalry, and light-armed contingents."
        ),
        [
            "wave8_thebes_hammond_boeotia",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_thucydides_delium",
        ],
    ),
    _entity(
        _DELIUM_ATHENIAN_ID,
        "Athenian field army under Hippocrates at Delium (424 BCE)",
        "field_army",
        -424,
        "Delium and Oropia",
        (
            "Bounded to Hippocrates's withdrawing Athenian expedition and its "
            "field battle, not the city of Athens across other campaigns."
        ),
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_thucydides_delium",
        ],
    ),
    _entity(
        _TEGYRA_THEBAN_ID,
        "Pelopidas's Sacred Band and cavalry at Tegyra (375 BCE)",
        "field_force",
        -375,
        "Tegyra and Orchomenus, Boeotia",
        (
            "Bounded to Pelopidas's three hundred Theban infantry and small "
            "cavalry force returning from the attempted move on Orchomenus."
        ),
        [
            "wave8_thebes_buckler_beck_tegyra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
        ],
    ),
    _entity(
        _TEGYRA_SPARTAN_ID,
        "Spartan Orchomenus garrison detachments at Tegyra (375 BCE)",
        "garrison_field_force",
        -375,
        "Tegyra and Orchomenus, Boeotia",
        (
            "Bounded to the two Lacedaemonian garrison divisions encountered "
            "while returning from Locris, not the Spartan polity generally."
        ),
        [
            "wave8_thebes_buckler_beck_tegyra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
        ],
    ),
    _entity(
        _LEUCTRA_BOEOTIAN_ID,
        "Boeotian field army under Epaminondas at Leuctra (371 BCE)",
        "federal_field_army",
        -371,
        "Leuctra, Boeotia",
        (
            "Bounded to the Boeotian mobilization and its Theban-led assault "
            "formation at Leuctra, including but not flattened to the Sacred Band."
        ),
        [
            "wave8_thebes_buckler_beck_leuctra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
            "wave8_thebes_xenophon_leuctra",
        ],
    ),
    _entity(
        _LEUCTRA_LACEDAEMONIAN_ID,
        "Cleombrotus's Lacedaemonian and allied army at Leuctra (371 BCE)",
        "field_army",
        -371,
        "Leuctra, Boeotia",
        (
            "Bounded to King Cleombrotus's Lacedaemonian core and Peloponnesian "
            "allied contingents at Leuctra, not Sparta across other wars."
        ),
        [
            "wave8_thebes_buckler_beck_leuctra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
            "wave8_thebes_xenophon_leuctra",
        ],
    ),
    _entity(
        _MANTINEA_THEBAN_ID,
        "Epaminondas's Theban-led allied army at Mantinea (362 BCE)",
        "field_coalition",
        -362,
        "Mantinea and Tegea, Arcadia",
        (
            "Bounded to the Boeotian, Euboean, Thessalian, Argive, Messenian, "
            "Sicyonian, Tegean, Megalopolitan, and aligned Arcadian coalition."
        ),
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_shipley_mantinea",
            "wave8_thebes_van_wijk_athens_boiotia",
            "wave8_thebes_xenophon_mantinea",
        ],
    ),
    _entity(
        _MANTINEA_OPPOSITION_ID,
        "Spartan-Athenian-Mantinean allied army at Mantinea (362 BCE)",
        "field_coalition",
        -362,
        "Mantinea, Arcadia",
        (
            "Bounded to the Lacedaemonian, Athenian, Mantinean, Elean, Achaean, "
            "and anti-Theban Arcadian coalition in this battle."
        ),
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_shipley_mantinea",
            "wave8_thebes_van_wijk_athens_boiotia",
            "wave8_thebes_xenophon_mantinea",
        ],
    ),
    _entity(
        _THEBES_ASSAULT_ID,
        "Alexander's Macedonian and allied Greek assault force at Thebes (335 BCE)",
        "siege_and_assault_force",
        -335,
        "Thebes, Boeotia",
        (
            "Bounded to Alexander's battle-seasoned Macedonian army and the allied "
            "Greek contingents used against the Theban revolt."
        ),
        [
            "wave8_thebes_bosworth_alexander",
            "wave8_thebes_diodorus_book17",
            "wave8_thebes_flower_panhellenism",
        ],
    ),
    _entity(
        _THEBES_DEFENDERS_ID,
        "Theban rebel civic defenders at Thebes (335 BCE)",
        "civic_defense_force",
        -335,
        "Thebes, Boeotia",
        (
            "Bounded to the citizens and other defenders who resolved to fight "
            "Alexander during the 335 BCE revolt and city assault."
        ),
        [
            "wave8_thebes_bosworth_alexander",
            "wave8_thebes_diodorus_book17",
            "wave8_thebes_flower_panhellenism",
        ],
    ),
)


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


_ROW_HASHES = {
    "hced-Coronea-447-1": "00e955d94fad33140d093479ab6c3d3ef2ba8e20206a12b05f488e18f21e8ff9",
    "hced-Delium-424-1": "fad4a7d0e653c05f1fc43adcf953813336d440e80adadcb29b530c131d5e5cb3",
    "hced-Leuctra-371-1": "b68adb278e24a23a4cc5c75d4b1ecc45c22ea0804924283420e02e567d391094",
    "hced-Mantinea-362-1": "2b8a38d2546d047a8ffa34b9e2dab19f0fd3426a69dc5e3c63eddebca8df19db",
    "hced-Tegyra-375-1": "127755835753e6f0748fdd8afdb8d1dd48510ba8888e97313bf11353dc29142c",
    "hced-Thebes-335-1": "34e4310c1224bc71e22366cdc4f9ecd489ff0942419e947aec8addfbd23f88a1",
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_THEBES_SOURCES
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": False,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_THEBES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Coronea-447-1": _contract(
        "hced-Coronea-447-1",
        _canonical(
            "Battle of Coronea (447 BCE)",
            -447,
            "447 BCE (traditional chronology)",
        ),
        "first_peloponnesian_war_boeotia_447_bce",
        [_CORONEA_EXILES_ID],
        [_CORONEA_ATHENIAN_ID],
        [
            "wave8_thebes_dull_coronea",
            "wave8_thebes_thucydides_coronea",
            "wave8_thebes_van_wijk_athens_boiotia",
        ],
        [
            "wave8_thebes_dull_coronea",
            "wave8_thebes_thucydides_coronea",
            "wave8_thebes_van_wijk_athens_boiotia",
        ],
        (
            "Thucydides identifies the victors as exiles from Orchomenus, some "
            "Locrians, Euboean exiles, and others of the same party, not a Theban "
            "army. They "
            "defeated Tolmides's returning Athenian-allied force. The conventional "
            "447 BCE row is kept distinct from Agesilaus's Coronea battle in 394."
        ),
        "anti_imperial_revolt",
        confidence=0.91,
    ),
    "hced-Delium-424-1": _contract(
        "hced-Delium-424-1",
        _canonical("Battle of Delium", -424, "late 424 BCE"),
        "peloponnesian_war_boeotian_campaign_424_bce",
        [_DELIUM_BOEOTIAN_ID],
        [_DELIUM_ATHENIAN_ID],
        [
            "wave8_thebes_hammond_boeotia",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_thucydides_delium",
        ],
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_thucydides_delium",
        ],
        (
            "Thucydides enumerates a federal Boeotian army: the Thebans held the "
            "right, while multiple other Boeotian contingents occupied the centre "
            "and left. Pagondas's army broke and pursued Hippocrates's Athenians."
        ),
        "interstate_limited",
        confidence=0.98,
    ),
    "hced-Tegyra-375-1": _contract(
        "hced-Tegyra-375-1",
        _canonical("Battle of Tegyra", -375, "375 BCE"),
        "boeotian_spartan_war_375_371_bce",
        [_TEGYRA_THEBAN_ID],
        [_TEGYRA_SPARTAN_ID],
        [
            "wave8_thebes_buckler_beck_tegyra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
        ],
        [
            "wave8_thebes_buckler_beck_tegyra",
            "wave8_thebes_plutarch_pelopidas",
        ],
        (
            "Plutarch's bounded actor is Pelopidas's three hundred infantry and a "
            "few horsemen. They killed the two Spartan commanders, routed the two "
            "garrison divisions, erected a trophy, and withdrew without attempting "
            "to represent either side as a timeless polity."
        ),
        "interstate_limited",
        confidence=0.90,
    ),
    "hced-Leuctra-371-1": _contract(
        "hced-Leuctra-371-1",
        _canonical("Battle of Leuctra", -371, "371 BCE"),
        "boeotian_spartan_war_375_371_bce",
        [_LEUCTRA_BOEOTIAN_ID],
        [_LEUCTRA_LACEDAEMONIAN_ID],
        [
            "wave8_thebes_buckler_beck_leuctra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
            "wave8_thebes_xenophon_leuctra",
        ],
        [
            "wave8_thebes_buckler_beck_leuctra",
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_plutarch_pelopidas",
            "wave8_thebes_xenophon_leuctra",
        ],
        (
            "The sources attest the Boeotian field army's defeat of Cleombrotus's "
            "Lacedaemonian-allied army. The Theban-led assault wing is represented "
            "inside the federal formation rather than substituted for all Boeotia."
        ),
        "interstate_limited",
        confidence=0.98,
    ),
    "hced-Mantinea-362-1": _contract(
        "hced-Mantinea-362-1",
        _canonical(
            "Battle of Mantinea (362 BCE)",
            -362,
            "summer 362 BCE",
            date_precision="season",
        ),
        "theban_hegemony_mantinea_362_bce",
        [_MANTINEA_THEBAN_ID],
        [_MANTINEA_OPPOSITION_ID],
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_shipley_mantinea",
            "wave8_thebes_van_wijk_athens_boiotia",
            "wave8_thebes_xenophon_mantinea",
        ],
        [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_shipley_mantinea",
            "wave8_thebes_xenophon_mantinea",
        ],
        (
            "Xenophon says Epaminondas gained mastery at the point of attack and "
            "caused the opposing army to flee, but his mortal wound stopped the "
            "pursuit and left neither coalition strategically better off. Shipley "
            "likewise distinguishes the Theban defeat of Sparta and Athens from "
            "the battle's indecisive strategic aftermath. The raw Draw is therefore "
            "corrected only at tactical engagement granularity."
        ),
        "interstate_limited",
        confidence=0.93,
        source_outcome_override=True,
    ),
    "hced-Thebes-335-1": _contract(
        "hced-Thebes-335-1",
        _canonical(
            "Siege and destruction of Thebes",
            -335,
            "335 BCE",
            granularity="city_siege_and_assault",
        ),
        "theban_revolt_against_alexander_335_bce",
        [_THEBES_ASSAULT_ID],
        [_THEBES_DEFENDERS_ID],
        [
            "wave8_thebes_bosworth_alexander",
            "wave8_thebes_diodorus_book17",
            "wave8_thebes_flower_panhellenism",
        ],
        [
            "wave8_thebes_bosworth_alexander",
            "wave8_thebes_diodorus_book17",
            "wave8_thebes_flower_panhellenism",
        ],
        (
            "Diodorus and the Oxford studies attest Alexander's defeat of the "
            "revolting Theban defenders, followed by the city's destruction. The "
            "actors are the 335 BCE assault force and civic defenders, not generic "
            "Macedonia or any earlier, later, or Egyptian Thebes."
        ),
        "internal_rebellion",
        confidence=0.98,
    ),
}


# Every row has a source-attested tactical result.  These explicit inventories
# still reserve the nonpromotion semantics so future uncertainty cannot be
# silently encoded as a draw or dropped from lane ownership.
WAVE8_THEBES_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_THEBES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_THEBES_EXCLUSIONS = WAVE8_THEBES_TERMINAL_EXCLUSIONS
WAVE8_THEBES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_THEBES_HOLDS,
    **WAVE8_THEBES_TERMINAL_EXCLUSIONS,
}

WAVE8_THEBES_CONTRACT_IDS = frozenset(WAVE8_THEBES_CONTRACTS)
WAVE8_THEBES_HOLD_IDS = frozenset(WAVE8_THEBES_HOLDS)
WAVE8_THEBES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_THEBES_TERMINAL_EXCLUSIONS
)
WAVE8_THEBES_EXCLUSION_IDS = WAVE8_THEBES_TERMINAL_EXCLUSION_IDS
WAVE8_THEBES_RESERVED_IDS = frozenset(
    WAVE8_THEBES_CONTRACT_IDS
    | WAVE8_THEBES_HOLD_IDS
    | WAVE8_THEBES_TERMINAL_EXCLUSION_IDS
)
WAVE8_THEBES_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256 = (
    "7ddb38c5103454765606d88a2b08d700cb22ca56d36d10d952701837e60af75b"
)


WAVE8_THEBES_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Coronea-447-1": {
        "actions": ["withhold_point"],
        "raw_point": [22.9597293, 38.3593442],
        "retained_country": "Greece",
        "evidence_refs": [
            "wave8_thebes_dull_coronea",
            "wave8_thebes_van_wijk_athens_boiotia",
        ],
        "reason": (
            "HCED reuses this locality coordinate for the distinct 447 and 394 "
            "BCE Coronea rows; it is not an event-specific, source-audited "
            "battlefield point."
        ),
    },
    "hced-Delium-424-1": {
        "actions": ["withhold_point"],
        "raw_point": [23.6654365, 38.3327765],
        "retained_country": "Greece",
        "evidence_refs": [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_thucydides_delium",
        ],
        "reason": (
            "The staged locality point is not a source-audited coordinate for "
            "the field battle, which was separate from the fortified sanctuary "
            "and its subsequent siege."
        ),
    },
    "hced-Tegyra-375-1": {
        "actions": ["withhold_point"],
        "raw_point": [22.957728, 38.534199],
        "retained_country": "Greece",
        "evidence_refs": ["wave8_thebes_buckler_beck_tegyra"],
        "reason": (
            "The scholarly topographic discussion does not authenticate HCED's "
            "single locality point as the encounter site in Tegyra's pass."
        ),
    },
    "hced-Leuctra-371-1": {
        "actions": ["withhold_point"],
        "raw_point": [23.182943, 38.254175],
        "retained_country": "Greece",
        "evidence_refs": [
            "wave8_thebes_buckler_beck_leuctra",
            "wave8_thebes_lucas_boeotian_army",
        ],
        "reason": (
            "The Leuctra locality coordinate is not established by the reviewed "
            "battle studies as an exact point for the opposing formations."
        ),
    },
    "hced-Mantinea-362-1": {
        "actions": ["withhold_point"],
        "raw_point": [22.383333, 37.616667],
        "retained_country": "Greece",
        "evidence_refs": [
            "wave8_thebes_lucas_boeotian_army",
            "wave8_thebes_shipley_mantinea",
            "wave8_thebes_xenophon_mantinea",
        ],
        "reason": (
            "A generic Mantinean-plain point cannot stand for the footprint of "
            "two large coalition armies and is not source-audited as the clash point."
        ),
    },
    "hced-Thebes-335-1": {
        "actions": ["withhold_point"],
        "raw_point": [23.3204309, 38.322579],
        "retained_country": "Greece",
        "evidence_refs": [
            "wave8_thebes_diodorus_book17",
            "wave8_thebes_flower_panhellenism",
        ],
        "reason": (
            "A city-centre coordinate cannot represent the footprint of the "
            "siege, wall fighting, breach, and destruction of Thebes."
        ),
    },
}
WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_THEBES_LOCATION_QUARANTINE_REASONS
)
WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_THEBES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_THEBES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Mantinea-362-1": {
        "raw_winner_raw": "Draw",
        "raw_loser_raw": None,
        "raw_winner_loser_complete": False,
        "corrected_result_type": "win",
        "corrected_winner_side": 1,
        "corrected_winner_entity_ids": [_MANTINEA_THEBAN_ID],
        "corrected_loser_entity_ids": [_MANTINEA_OPPOSITION_ID],
        "override_kind": "raw_draw_placeholder_to_sourced_theban_led_tactical_victory",
        "outcome_reversal": False,
        "strategic_disposition": (
            "no_decisive_strategic_payoff_after_epaminondas_death_not_a_tactical_draw"
        ),
        "outcome_source_ids": WAVE8_THEBES_CONTRACTS["hced-Mantinea-362-1"][
            "outcome_source_ids"
        ],
        "outcome_source_family_ids": WAVE8_THEBES_CONTRACTS[
            "hced-Mantinea-362-1"
        ]["outcome_source_family_ids"],
    }
}


# The staged IWBD queue, other HCED lanes, and current release contain no
# probable twins under the candidate-keyed alias/year audit below.
WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_THEBES_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_THEBES_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted(set(map(normalize_label, aliases))),
        "years": [year, year],
    }


WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Coronea-447-1": _duplicate_audit(
        -447,
        "Battle of Coronea",
        "Battle of Coronea (447 BCE)",
        "Battle of Coronaea",
        "Battle of Koroneia",
        "Coronea",
        "Coronaea",
        "Koroneia",
    ),
    "hced-Delium-424-1": _duplicate_audit(
        -424,
        "Battle of Delium",
        "Battle of Delion",
        "Delium",
        "Delion",
    ),
    "hced-Tegyra-375-1": _duplicate_audit(
        -375,
        "Battle of Tegyra",
        "Battle of Tegyrae",
        "Tegyra",
        "Tegyrae",
    ),
    "hced-Leuctra-371-1": _duplicate_audit(
        -371,
        "Battle of Leuctra",
        "Battle of Leuktra",
        "Leuctra",
        "Leuktra",
    ),
    "hced-Mantinea-362-1": _duplicate_audit(
        -362,
        "Battle of Mantinea",
        "Battle of Mantinea (362 BCE)",
        "Battle of Mantineia",
        "Mantinea",
        "Mantineia",
        "Second Battle of Mantinea",
        "Second Battle of Mantineia",
    ),
    "hced-Thebes-335-1": _duplicate_audit(
        -335,
        "Battle of Thebes",
        "Destruction of Thebes",
        "Siege and destruction of Thebes",
        "Siege of Thebes",
        "Thebes",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_THEBES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_THEBES_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_THEBES_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256,
        "existing_release_duplicate_dispositions": (
            WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_THEBES_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_THEBES_HOLDS,
        "integration_dispositions": WAVE8_THEBES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_THEBES_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_THEBES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_THEBES_SOURCES,
        "terminal_exclusions": WAVE8_THEBES_TERMINAL_EXCLUSIONS,
    }


def wave8_thebes_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_THEBES_FINAL_AUDIT_SIGNATURE = (
    "b2e341390dccf5ebb9e4d16e3cdbddf3c1640163af361064fa231b599c54595a"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_THEBES_CONTRACTS),
        len(WAVE8_THEBES_HOLDS),
        len(WAVE8_THEBES_TERMINAL_EXCLUSIONS),
    ) != (6, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_THEBES_ENTITIES), len(WAVE8_THEBES_SOURCES)) != (12, 15):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_THEBES_RESERVED_IDS != WAVE8_THEBES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_THEBES_CONTRACT_IDS,
        WAVE8_THEBES_HOLD_IDS,
        WAVE8_THEBES_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_THEBES_EXCLUSIONS is not WAVE8_THEBES_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if set(WAVE8_THEBES_NONPROMOTIONS) != (
        WAVE8_THEBES_HOLD_IDS | WAVE8_THEBES_TERMINAL_EXCLUSION_IDS
    ):
        raise ValueError(f"{_LANE_NAME} nonpromotion inventory drifted")
    if (
        _sorted_newline_sha256(WAVE8_THEBES_EXPECTED_CANDIDATE_IDS)
        != WAVE8_THEBES_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} candidate-ID signature changed")
    if wave8_thebes_audit_signature() != WAVE8_THEBES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_THEBES_SOURCES}
    if len(source_by_id) != len(WAVE8_THEBES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_THEBES_SOURCES}) != 12:
        raise ValueError(f"{_LANE_NAME} source-family inventory changed")
    for source in WAVE8_THEBES_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_THEBES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_THEBES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "athens",
        "boeotia",
        "boeotian",
        "egyptian thebes",
        "macedonia",
        "sparta",
        "theban",
        "thebes",
    }
    for entity in WAVE8_THEBES_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if any(
            phrase not in note
            for phrase in (
                "no rating is inherited",
                "same-name thebes",
                "modern state",
            )
        ):
            raise ValueError(f"{_LANE_NAME} identity permits continuity bridging")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_THEBES_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] not in {"engagement", "city_siege_and_assault"}:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses a non-bounded identity")
        used_entities.update(set(side_1) | set(side_2))
        year = int(canonical["year_low"])
        for entity_id in set(side_1) | set(side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor policy drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    if override_ids != {"hced-Mantinea-362-1"}:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if set(WAVE8_THEBES_OUTCOME_OVERRIDES) != override_ids:
        raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")
    override = WAVE8_THEBES_OUTCOME_OVERRIDES["hced-Mantinea-362-1"]
    contract = WAVE8_THEBES_CONTRACTS["hced-Mantinea-362-1"]
    if (
        override["corrected_winner_side"] != contract["winner_side"]
        or override["corrected_winner_entity_ids"] != contract["side_1_entity_ids"]
        or override["corrected_loser_entity_ids"] != contract["side_2_entity_ids"]
        or override["outcome_source_ids"] != contract["outcome_source_ids"]
        or override["outcome_source_family_ids"]
        != contract["outcome_source_family_ids"]
        or override["outcome_reversal"] is not False
    ):
        raise ValueError(f"{_LANE_NAME} corrected outcome metadata drifted")

    used_sources.update(
        source_id
        for entity in WAVE8_THEBES_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_THEBES_HOLDS or WAVE8_THEBES_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited nonpromotion")
    if (
        WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_THEBES_CROSS_LANE_DISPOSITIONS
        or WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_THEBES_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate inventories changed")

    if WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS != WAVE8_THEBES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_THEBES_LOCATION_QUARANTINE_REASONS) != WAVE8_THEBES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for candidate_id, review in WAVE8_THEBES_LOCATION_QUARANTINE_REASONS.items():
        if review["actions"] != ["withhold_point"]:
            raise ValueError(f"{_LANE_NAME} location action drifted")
        if review["retained_country"] != "Greece" or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} country review drifted")
        refs = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        if candidate_id not in WAVE8_THEBES_CONTRACT_IDS:
            raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")

    if set(WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_THEBES_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        canonical = WAVE8_THEBES_CONTRACTS[candidate_id]["canonical_event"]
        if years != [int(canonical["year_low"]), int(canonical["year_high"])]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        if normalize_label(canonical["name"]) not in aliases:
            raise ValueError(f"{_LANE_NAME} canonical duplicate alias is missing")


def _is_exact_thebes_label(value: Any) -> bool:
    return normalize_label(value) == "thebes"


def validate_wave8_thebes_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all six exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_THEBES_CONTRACTS,
        WAVE8_THEBES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_thebes_label(row.get("side_1_raw"))
        or _is_exact_thebes_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_THEBES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Thebes inventory changed: {sorted(exact_label_ids)}"
        )
    return {
        "holds": len(WAVE8_THEBES_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_THEBES_TERMINAL_EXCLUSIONS),
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
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                return -year if value.startswith("-") else year
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_thebes_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue or release lane adds an unreviewed twin."""

    validate_wave8_thebes_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_THEBES_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_THEBES_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_THEBES_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_THEBES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT),
    }


def install_wave8_thebes_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_THEBES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_thebes_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_THEBES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_thebes_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_thebes_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_THEBES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_thebes_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_THEBES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_thebes_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_THEBES_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_THEBES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_THEBES_HOLDS),
        "integration_dispositions": len(WAVE8_THEBES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_THEBES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_THEBES_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_THEBES_ENTITIES),
        "new_sources": len(WAVE8_THEBES_SOURCES),
        "newly_rated_events": len(WAVE8_THEBES_CONTRACTS),
        "outcome_overrides": len(WAVE8_THEBES_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_THEBES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_THEBES_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_THEBES_TERMINAL_EXCLUSIONS),
    }


def wave8_thebes_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_THEBES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_THEBES_POINT_QUARANTINE_ADDITIONS,
    }
