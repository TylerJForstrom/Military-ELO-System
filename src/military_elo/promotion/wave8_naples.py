"""Exact Wave 8 audit for HCED rows whose raw opponent is "Naples"."""

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


_LANE_NAME = "Wave 8 Naples"

# This pins the entire researched disposition: source fixtures, finite identities,
# promotion contracts, terminal exclusions, and the complete reserved inventory.
WAVE8_NAPLES_FINAL_AUDIT_SIGNATURE = (
    "32384473e6694eb55711559f0e2315689ed6dfdcd682ecc0ad750ef458070abe"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    family: str,
    *,
    source_type: str = "official_or_academic_reference",
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
        "source_family_id": family,
        "evidence_roles": sorted(roles),
    }


WAVE8_NAPLES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_naples_berat_balkans_journal",
        "The Battle of Berat (1281) and the Angevin-Byzantine conflict",
        "https://journals.uni-vt.bg/balkans/eng/vol2/iss1/art8",
        "The Balkans, St. Cyril and St. Methodius University of Veliko Tarnovo",
        "balkans_journal_berat_1281",
        source_type="academic_journal",
        outcome=True,
    ),
    _source(
        "wave8_naples_berat_byzantina_symmeikta",
        "The Byzantine-Angevin struggle and the siege of Berat",
        "https://ejournals.epublishing.ekt.gr/index.php/bz/article/viewFile/3928/3720.pdf",
        "Byzantina Symmeikta, National Hellenic Research Foundation",
        "byzantina_symmeikta_berat",
        source_type="academic_journal",
        outcome=True,
    ),
    _source(
        "wave8_naples_taranto_rah_gonzalo",
        "Gonzalo Fernández de Córdoba",
        "https://historia-hispanica.rah.es/biografias/15450-gonzalo-fernandez-de-cordoba",
        "Real Academia de la Historia",
        "real_academia_historia_taranto",
        outcome=True,
    ),
    _source(
        "wave8_naples_taranto_treccani_ferdinand",
        "Aragona, Ferdinando d', duca di Calabria, principe di Taranto",
        (
            "https://www.treccani.it/enciclopedia/aragona-ferdinando-d-duca-di-"
            "calabria-principe-di-taranto/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_taranto_1501_1502",
        outcome=True,
    ),
    _source(
        "wave8_naples_civita_castellana_army_journal",
        "Rivista Militare Italiana, 1909, volume III",
        (
            "https://www.esercito.difesa.it/comunicazione/editoria/Rivista-Militare/"
            "archivio/Documents/1909/1909-tomo3-testo-low.pdf"
        ),
        "Italian Army Historical Office",
        "italian_army_civita_castellana",
        source_type="official_military_history",
        outcome=True,
    ),
    _source(
        "wave8_naples_1799_cambridge",
        "Enlightenment and Revolution: Naples 1799",
        (
            "https://www.cambridge.org/core/journals/transactions-of-the-royal-"
            "historical-society/article/abs/enlightenment-and-revolution-naples-"
            "1799/ED746A78587428361E11ACF242BA4ABA"
        ),
        "Cambridge University Press / Royal Historical Society",
        "cambridge_naples_1799",
        source_type="academic_journal",
        outcome=True,
    ),
    _source(
        "wave8_naples_1799_treccani_republic",
        "Repubblica napoletana",
        (
            "https://www.treccani.it/enciclopedia/repubblica-napoletana_"
            "%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_neapolitan_republic_1799",
        outcome=True,
    ),
    _source(
        "wave8_naples_regime_boundaries_treccani",
        "Napoli",
        "https://www.treccani.it/enciclopedia/napoli/",
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_naples_regime_boundaries",
    ),
    _source(
        "wave8_naples_gaeta_treccani",
        "Gaeta",
        "https://www.treccani.it/enciclopedia/gaeta_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_gaeta_1806",
        outcome=True,
    ),
    _source(
        "wave8_naples_gaeta_founders_online",
        "William Pinkney to James Madison, 30 July 1806",
        "https://founders.archives.gov/documents/Madison/02-12-02-0267",
        "U.S. National Archives, Founders Online",
        "founders_online_gaeta_1806",
        source_type="edited_primary_source",
        outcome=True,
    ),
    _source(
        "wave8_naples_two_sicilies_treccani",
        "Due Sicilie, Regno delle",
        (
            "https://www.treccani.it/enciclopedia/due-sicilie-regno-delle_"
            "%28Dizionario-di-Storia%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_two_sicilies",
    ),
    _source(
        "wave8_naples_sicilian_revolution_oxford",
        "Under the Volcano: The Sicilian Revolution of 1848-49",
        "https://academic.oup.com/book/33068/chapter-abstract/281727604",
        "Oxford University Press",
        "oxford_sicilian_revolution_1848_1849",
        source_type="academic_monograph",
    ),
    _source(
        "wave8_naples_catania_treccani",
        "Catania",
        "https://www.treccani.it/enciclopedia/catania_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_catania_1849",
        outcome=True,
    ),
    _source(
        "wave8_naples_calatafimi_treccani",
        "Calatafimi",
        (
            "https://www.treccani.it/enciclopedia/calatafimi_"
            "%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_calatafimi_1860",
        outcome=True,
    ),
    _source(
        "wave8_naples_risorgimento_treccani",
        "Risorgimento",
        (
            "https://www.treccani.it/enciclopedia/risorgimento_"
            "%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_risorgimento_1860",
        outcome=True,
    ),
    _source(
        "wave8_naples_milazzo_treccani",
        "Milazzo",
        "https://www.treccani.it/enciclopedia/milazzo_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_milazzo_1860",
        outcome=True,
    ),
    _source(
        "wave8_naples_volturno_italian_army",
        "La battaglia del Volturno",
        (
            "https://www.esercito.difesa.it/en/history/historic-office-of-the-"
            "general-staff-of-the-army/military-publishing/catalogo/risorgimento-e-"
            "prima-guerra-mondiale/la-battaglia-del-volturno/76375.html"
        ),
        "Italian Army Historical Office",
        "italian_army_volturno_1860",
        source_type="official_military_history",
        outcome=True,
    ),
    _source(
        "wave8_naples_volturno_vive_museum",
        "Bourbon prisoners on the Volturno line",
        (
            "https://vive.cultura.gov.it/en/central-museum-risorgimento/what-see/"
            "bourbon-prisoners-volturno-line-michele-tedesco"
        ),
        "VIVE - Central Museum of the Risorgimento",
        "vive_museum_volturno_1860",
        source_type="official_museum_reference",
        outcome=True,
    ),
    _source(
        "wave8_naples_harbottle_scan",
        "Dictionary of Battles from the Earliest Date to the Present Time",
        "https://archive.org/details/dictionaryofbatt00harb/page/n7/mode/2up",
        "Internet Archive scan of Thomas Benfield Harbottle",
        "harbottle_dictionary_scan",
        source_type="digitized_reference_scan",
        crosscheck=True,
    ),
    _source(
        "wave8_naples_murat_treccani",
        "Murat, Gioacchino Napoleone, re di Napoli",
        (
            "https://www.treccani.it/enciclopedia/gioacchino-napoleone-murat-re-"
            "di-napoli_%28Dizionario-Biografico%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "treccani_murat_naples_1815",
    ),
    _source(
        "wave8_naples_1815_italian_army",
        "La campagna austro-napoletana del 1815",
        (
            "https://www.esercito.difesa.it/comunicazione/editoria/Rassegna-Esercito/"
            "Tutti-i-numeri/2015/Documents/rassei-1-15.pdf"
        ),
        "Italian Army Historical Office",
        "italian_army_naples_war_1815",
        source_type="official_military_history",
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    continuity_note: str,
    source_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": "Southern Europe and the central Mediterranean",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(source_ids),
    }


WAVE8_NAPLES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "byzantine_berat_relief_army_1281",
        "Byzantine Relief Army at Berat (1281)",
        "campaign_army",
        1281,
        1281,
        (
            "Battle-bounded Byzantine relief force that defeated Hugh of Sully's "
            "Angevin army. No rating is inherited from the Byzantine Empire, a "
            "predecessor, a successor, or another Byzantine field army."
        ),
        [
            "wave8_naples_berat_balkans_journal",
            "wave8_naples_berat_byzantina_symmeikta",
        ],
    ),
    _entity(
        "angevin_sicily_berat_army_1281",
        "Angevin Kingdom of Sicily Army at Berat (1281)",
        "campaign_army",
        1281,
        1281,
        (
            "Hugh of Sully's army serving Charles I's Angevin Kingdom of Sicily; "
            "the raw label 'Naples' is anachronistic for this event. No rating is "
            "inherited by a later Kingdom of Naples, a Sicilian regime, or another "
            "Angevin force."
        ),
        [
            "wave8_naples_berat_balkans_journal",
            "wave8_naples_berat_byzantina_symmeikta",
        ],
    ),
    _entity(
        "spanish_taranto_besieging_force_1501_1502",
        "Spanish Besieging Force at Taranto (1501-1502)",
        "campaign_army",
        1501,
        1502,
        (
            "Gonzalo Fernández de Córdoba's Spanish force in the exact Taranto "
            "siege. No rating is inherited from a timeless Spain identity, the "
            "Spanish Empire, or another Italian Wars army."
        ),
        ["wave8_naples_taranto_rah_gonzalo"],
    ),
    _entity(
        "aragonese_neapolitan_taranto_garrison_1501_1502",
        "Aragonese Neapolitan Garrison of Taranto (1501-1502)",
        "royal_garrison",
        1501,
        1502,
        (
            "The dynastic Neapolitan holdout commanded by Ferdinand, duke of "
            "Calabria and prince of Taranto, after Federico's defeat. No rating is "
            "inherited by later Spanish, Bourbon, republican, or Napoleonic Naples."
        ),
        ["wave8_naples_taranto_treccani_ferdinand"],
    ),
    _entity(
        "macdonald_french_division_civita_castellana_1798",
        "Macdonald's French Division at Civita Castellana (1798)",
        "campaign_army",
        1798,
        1798,
        (
            "The French Republican field force under Jacques Macdonald in the "
            "1798 Roman campaign. No rating is inherited from generic France, the "
            "First French Empire, or another French army."
        ),
        ["wave8_naples_civita_castellana_army_journal"],
    ),
    _entity(
        "bourbon_naples_field_army_1798",
        "Bourbon Kingdom of Naples Field Army (1798)",
        "state_armed_forces",
        1798,
        1798,
        (
            "Karl Mack's field army of Ferdinand IV's Bourbon Kingdom of Naples "
            "during the 1798 invasion of the Roman Republic. No rating is inherited "
            "by the 1799 Parthenopean Republic, a restored Bourbon force, Joseph "
            "Bonaparte's kingdom, Murat's kingdom, or the Two Sicilies."
        ),
        [
            "wave8_naples_civita_castellana_army_journal",
            "wave8_naples_regime_boundaries_treccani",
        ],
    ),
    _entity(
        "championnet_french_army_naples_1799",
        "Championnet's French Army at Naples (1799)",
        "campaign_army",
        1799,
        1799,
        (
            "Jean-Étienne Championnet's French Republican army in the January "
            "1799 capture of Naples. No rating is inherited from generic France, "
            "Macdonald's 1798 division, or a Napoleonic imperial army."
        ),
        [
            "wave8_naples_1799_cambridge",
            "wave8_naples_1799_treccani_republic",
        ],
    ),
    _entity(
        "parthenopean_republican_forces_1799",
        "Parthenopean Republican Forces at Naples (1799)",
        "revolutionary_forces",
        1799,
        1799,
        (
            "The Neapolitan patriots who held Castel Sant'Elmo and proclaimed the "
            "Parthenopean Republic during the French entry. No rating is inherited "
            "from Bourbon Naples, the restored Bourbon kingdom, either Napoleonic "
            "kingdom, or the Kingdom of the Two Sicilies."
        ),
        [
            "wave8_naples_1799_cambridge",
            "wave8_naples_1799_treccani_republic",
        ],
    ),
    _entity(
        "neapolitan_royalist_lazzari_1799",
        "Neapolitan Royalist Lazzari Defenders (1799)",
        "urban_militia",
        1799,
        1799,
        (
            "The armed popular royalist defenders who resisted after the Bourbon "
            "court and royal command abandoned Naples. No rating is inherited from "
            "Mack's 1798 army, a Bourbon state, or any later Neapolitan army."
        ),
        [
            "wave8_naples_1799_cambridge",
            "wave8_naples_1799_treccani_republic",
        ],
    ),
    _entity(
        "massena_french_gaeta_corps_1806",
        "Masséna's French Siege Corps at Gaeta (1806)",
        "siege_force",
        1806,
        1806,
        (
            "André Masséna's French imperial besieging force at Gaeta. No rating is "
            "inherited from the First French Republic, Joseph Bonaparte's newly "
            "installed kingdom, Murat's later kingdom, or another French corps."
        ),
        [
            "wave8_naples_gaeta_founders_online",
            "wave8_naples_gaeta_treccani",
        ],
    ),
    _entity(
        "restored_bourbon_gaeta_garrison_1806",
        "Restored Bourbon Neapolitan Garrison of Gaeta (1806)",
        "royal_garrison",
        1806,
        1806,
        (
            "The Gaeta garrison loyal to the displaced restored-Bourbon court and "
            "commanded by the prince of Hesse-Philippsthal. It is not the army of "
            "Joseph Bonaparte's Napoleonic Kingdom of Naples. No rating is inherited "
            "from the 1798 army or by any later Bourbon or Murat force."
        ),
        [
            "wave8_naples_gaeta_founders_online",
            "wave8_naples_gaeta_treccani",
            "wave8_naples_regime_boundaries_treccani",
        ],
    ),
    _entity(
        "sicilian_revolutionary_state_forces_1848_1849",
        "Sicilian Revolutionary State Forces (1848-1849)",
        "revolutionary_forces",
        1848,
        1849,
        (
            "Armed forces of the independent Sicilian revolutionary government in "
            "the 1848-49 revolution. No rating is inherited from a generic Sicilian "
            "rebel label, the 1799 republic, or Garibaldi's 1860 campaign army."
        ),
        [
            "wave8_naples_catania_treccani",
            "wave8_naples_sicilian_revolution_oxford",
        ],
    ),
    _entity(
        "two_sicilies_royal_army_sicily_1848_1849",
        "Two Sicilies Royal Army in Sicily (1848-1849)",
        "state_armed_forces",
        1848,
        1849,
        (
            "Carlo Filangieri's royal army of the Kingdom of the Two Sicilies in "
            "the 1848-49 reconquest of Sicily. No rating is inherited from a Kingdom "
            "of Naples army, another Bourbon restoration force, or the distinct "
            "1860 royal army."
        ),
        [
            "wave8_naples_catania_treccani",
            "wave8_naples_sicilian_revolution_oxford",
            "wave8_naples_two_sicilies_treccani",
        ],
    ),
    _entity(
        "garibaldian_southern_army_1860",
        "Garibaldian Southern Army (1860 campaign)",
        "revolutionary_campaign_army",
        1860,
        1860,
        (
            "Garibaldi's continuously commanded campaign force: the Thousand, "
            "Sicilian picciotti, and later volunteers. It excludes the regular "
            "Piedmontese or Sardinian army. No rating is inherited from earlier "
            "Italian nationalists, Sicilian revolutionaries, or the Kingdom of Italy."
        ),
        [
            "wave8_naples_calatafimi_treccani",
            "wave8_naples_milazzo_treccani",
            "wave8_naples_risorgimento_treccani",
            "wave8_naples_volturno_italian_army",
            "wave8_naples_volturno_vive_museum",
        ],
    ),
    _entity(
        "two_sicilies_royal_army_1860",
        "Two Sicilies Royal Army (1860 campaign)",
        "state_armed_forces",
        1860,
        1860,
        (
            "The Bourbon royal army of Francis II in the 1860 campaign against "
            "Garibaldi. No rating is inherited from earlier Kingdom of Naples forces, "
            "the 1848-49 Sicilian army, a later loyalist remnant, or the Kingdom of "
            "Italy."
        ),
        [
            "wave8_naples_calatafimi_treccani",
            "wave8_naples_milazzo_treccani",
            "wave8_naples_risorgimento_treccani",
            "wave8_naples_two_sicilies_treccani",
            "wave8_naples_volturno_italian_army",
            "wave8_naples_volturno_vive_museum",
        ],
    ),
    _entity(
        "bianchi_austrian_army_naples_war_1815",
        "Bianchi's Austrian Army in the Neapolitan War (1815)",
        "campaign_army",
        1815,
        1815,
        (
            "The Austrian campaign army opposed to Murat in 1815, retained only to "
            "fingerprint the terminal Ferrara conflation. No rating is inherited "
            "from the Austrian Empire or another Austrian force."
        ),
        ["wave8_naples_1815_italian_army"],
    ),
    _entity(
        "murat_neapolitan_army_1815",
        "Murat's Neapolitan Army (1815 campaign)",
        "state_armed_forces",
        1815,
        1815,
        (
            "The army of Joachim Murat's Napoleonic Kingdom of Naples in 1815, "
            "retained only to fingerprint the terminal Ferrara conflation. No rating "
            "is inherited from Bourbon Naples, Joseph Bonaparte's kingdom, a restored "
            "Bourbon army, or the Kingdom of the Two Sicilies."
        ),
        [
            "wave8_naples_1815_italian_army",
            "wave8_naples_murat_treccani",
        ],
    ),
)


def _canonical(name: str, year_low: int, year_high: int | None = None) -> dict[str, Any]:
    high = year_low if year_high is None else year_high
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{high}",
        "date_precision": "year" if year_low == high else "year_range",
        "granularity": "engagement",
        "name": name,
        "year_low": year_low,
        "year_high": high,
    }


_ROW_HASHES = {
    "hced-Berat1281-1": (
        "a62a401f40d5832c9c9edbae4a5e1a2042eb18497ffb9dc9b8a80be79ebd43ba"
    ),
    "hced-Calatafimi1860-1": "50a43fc2019dc7d85788e73791eace40d5e0c11b9c719ce087220ea16b22ebf2",
    "hced-Catania1849-1": "4085dde19b91723f90afbc3bed4ba124bedb84c63e1d95efdf214ca8f878d5fa",
    "hced-Civita Castelana1798-1": "829c9aca63eabea09f54d59ec3ccb6dc41a5576dc32fad74fa0a9f149832be8d",
    "hced-Ferrara1815-1": "1ed88f90c4500968d51f4f413c8cb0cd4f86b45ff1d6faba67932d8522045852",
    "hced-Gaeta1806-1": "521b529ca6cbb1934b5d296124432eacc30c6231de4558098821753ff46fab8b",
    "hced-Messina1860-1": "17b06507788b9f65f77b8ee4ad1bbdf781d6acea21b4bed76f5ced77685b53f2",
    "hced-Milazzo1860-1": "d13e6570790e766e7d136b30a6ba1aa6d1a4ecf70667dbd15598640951cd758a",
    "hced-Naples1799-1": "4fecab3832a1ac198d46420c664c5f5185ec9a72ea5d89cafe90ecc93fb79a8b",
    "hced-Palermo1848-1": "87538c13a7a0af72601584f22fc6f7f24e23d942d4b99b502b40a0d5540fc0ae",
    "hced-Palermo1860-1": "3de60e22c4a892ffb0b2896a68d8ec02fb71b1f850f366ecf52925d5e9a08eb4",
    "hced-Taranto1501-1502-1": "b0b2eb575ba4e9050f56aad5b4ba9385eea2a9acfdf7f82489ee1299074092dd",
    "hced-Volturno1860-1": "d98be3fd81c75821b850617476c0212bd4489734955f7ce4f1be417d03ca7079",
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float = 0.88,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(evidence_refs),
        "outcome_source_ids": sorted(outcome_source_ids),
        "outcome_source_family_ids": sorted(outcome_source_family_ids),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_NAPLES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Berat1281-1": _contract(
        "hced-Berat1281-1",
        _canonical("Battle of Berat", 1281),
        "angevin_byzantine_war",
        ["byzantine_berat_relief_army_1281"],
        ["angevin_sicily_berat_army_1281"],
        [
            "wave8_naples_berat_balkans_journal",
            "wave8_naples_berat_byzantina_symmeikta",
        ],
        [
            "wave8_naples_berat_balkans_journal",
            "wave8_naples_berat_byzantina_symmeikta",
        ],
        ["balkans_journal_berat_1281", "byzantina_symmeikta_berat"],
        (
            "Academic accounts place the defeat in 1281 and identify Hugh of "
            "Sully's attackers as Charles I's Angevin Kingdom of Sicily, not a "
            "timeless Neapolitan army. The raw winner orientation is retained."
        ),
        "interstate",
        confidence=0.91,
    ),
    "hced-Taranto1501-1502-1": _contract(
        "hced-Taranto1501-1502-1",
        _canonical("Siege of Taranto", 1501, 1502),
        "italian_war_naples_1501_1502",
        ["spanish_taranto_besieging_force_1501_1502"],
        ["aragonese_neapolitan_taranto_garrison_1501_1502"],
        [
            "wave8_naples_taranto_rah_gonzalo",
            "wave8_naples_taranto_treccani_ferdinand",
        ],
        [
            "wave8_naples_taranto_rah_gonzalo",
            "wave8_naples_taranto_treccani_ferdinand",
        ],
        ["real_academia_historia_taranto", "treccani_taranto_1501_1502"],
        (
            "The siege ran from September 1501 to the garrison's March 1502 "
            "surrender. The defender is Ferdinand of Calabria's Aragonese "
            "Neapolitan dynastic holdout, and the raw Spanish victory is retained."
        ),
        "interstate",
        confidence=0.91,
    ),
    "hced-Civita Castelana1798-1": _contract(
        "hced-Civita Castelana1798-1",
        _canonical("Battle of Civita Castellana", 1798),
        "bourbon_naples_french_invasion_1798_1799",
        ["macdonald_french_division_civita_castellana_1798"],
        ["bourbon_naples_field_army_1798"],
        ["wave8_naples_civita_castellana_army_journal"],
        ["wave8_naples_civita_castellana_army_journal"],
        ["italian_army_civita_castellana"],
        (
            "The canonical spelling is Civita Castellana. Macdonald's French "
            "Republican division defeated Mack's Bourbon Kingdom of Naples field "
            "army; no British or Austrian force is added from noisy participant text."
        ),
        "interstate",
        confidence=0.90,
    ),
    "hced-Naples1799-1": _contract(
        "hced-Naples1799-1",
        _canonical("Capture of Naples", 1799),
        "bourbon_naples_french_invasion_1798_1799",
        [
            "championnet_french_army_naples_1799",
            "parthenopean_republican_forces_1799",
        ],
        ["neapolitan_royalist_lazzari_1799"],
        [
            "wave8_naples_1799_cambridge",
            "wave8_naples_1799_treccani_republic",
        ],
        [
            "wave8_naples_1799_cambridge",
            "wave8_naples_1799_treccani_republic",
        ],
        ["cambridge_naples_1799", "treccani_neapolitan_republic_1799"],
        (
            "French troops forced entry after Parthenopean patriots had seized "
            "Castel Sant'Elmo and proclaimed the republic; armed royalist lazzari "
            "resisted after the Bourbon court and command left. The raw French-side "
            "victory is retained without assigning the defeated side to a timeless "
            "Naples state identity."
        ),
        "revolutionary_conflict",
        confidence=0.88,
    ),
    "hced-Gaeta1806-1": _contract(
        "hced-Gaeta1806-1",
        _canonical("Siege of Gaeta", 1806),
        "restored_bourbon_naples_1806",
        ["massena_french_gaeta_corps_1806"],
        ["restored_bourbon_gaeta_garrison_1806"],
        [
            "wave8_naples_gaeta_founders_online",
            "wave8_naples_gaeta_treccani",
        ],
        [
            "wave8_naples_gaeta_founders_online",
            "wave8_naples_gaeta_treccani",
        ],
        ["founders_online_gaeta_1806", "treccani_gaeta_1806"],
        (
            "Masséna's French corps compelled the loyalist Gaeta garrison to "
            "capitulate in July 1806. The defender remained loyal to the displaced "
            "restored Bourbon monarchy and is not Joseph Bonaparte's new Napoleonic "
            "Kingdom of Naples."
        ),
        "interstate",
        confidence=0.92,
    ),
    "hced-Catania1849-1": _contract(
        "hced-Catania1849-1",
        _canonical("Battle of Catania", 1849),
        "sicilian_revolution_1848_1849",
        ["two_sicilies_royal_army_sicily_1848_1849"],
        ["sicilian_revolutionary_state_forces_1848_1849"],
        [
            "wave8_naples_catania_treccani",
            "wave8_naples_sicilian_revolution_oxford",
            "wave8_naples_two_sicilies_treccani",
        ],
        ["wave8_naples_catania_treccani"],
        ["treccani_catania_1849"],
        (
            "Filangieri's Two Sicilies royal army took Catania by force in April "
            "1849 from the revolutionary Sicilian state. This is distinct from both "
            "Bourbon Kingdom of Naples armies and the 1860 campaign army."
        ),
        "civil_war",
        confidence=0.90,
    ),
    "hced-Calatafimi1860-1": _contract(
        "hced-Calatafimi1860-1",
        _canonical("Battle of Calatafimi", 1860),
        "garibaldian_campaign_1860",
        ["garibaldian_southern_army_1860"],
        ["two_sicilies_royal_army_1860"],
        [
            "wave8_naples_calatafimi_treccani",
            "wave8_naples_risorgimento_treccani",
        ],
        ["wave8_naples_calatafimi_treccani"],
        ["treccani_calatafimi_1860"],
        (
            "Garibaldi's Thousand and Sicilian picciotti defeated Landi's Bourbon "
            "troops on 15 May. Both sides are confined to the 1860 campaign and the "
            "raw winner orientation is retained."
        ),
        "state_formation_conflict",
        confidence=0.93,
    ),
    "hced-Palermo1860-1": _contract(
        "hced-Palermo1860-1",
        _canonical("Battle of Palermo", 1860),
        "garibaldian_campaign_1860",
        ["garibaldian_southern_army_1860"],
        ["two_sicilies_royal_army_1860"],
        ["wave8_naples_risorgimento_treccani"],
        ["wave8_naples_risorgimento_treccani"],
        ["treccani_risorgimento_1860"],
        (
            "Treccani's campaign account identifies Garibaldi's force, street "
            "fighting, royal bombardment, and the Bourbon evacuation in May 1860. "
            "This is the one defensible Palermo row; the conflicted 1848 identifier "
            "is terminally excluded as its misdated duplicate."
        ),
        "state_formation_conflict",
        confidence=0.91,
    ),
    "hced-Milazzo1860-1": _contract(
        "hced-Milazzo1860-1",
        _canonical("Battle of Milazzo", 1860),
        "garibaldian_campaign_1860",
        ["garibaldian_southern_army_1860"],
        ["two_sicilies_royal_army_1860"],
        [
            "wave8_naples_milazzo_treccani",
            "wave8_naples_risorgimento_treccani",
        ],
        ["wave8_naples_milazzo_treccani"],
        ["treccani_milazzo_1860"],
        (
            "Garibaldi and Medici's campaign force defeated Bosco's Bourbon force "
            "on 20 July. The exact campaign armies replace the raw generic Italian "
            "Nationalists and Naples labels."
        ),
        "state_formation_conflict",
        confidence=0.93,
    ),
    "hced-Volturno1860-1": _contract(
        "hced-Volturno1860-1",
        _canonical("Battle of the Volturno", 1860),
        "garibaldian_campaign_1860",
        ["garibaldian_southern_army_1860"],
        ["two_sicilies_royal_army_1860"],
        [
            "wave8_naples_volturno_italian_army",
            "wave8_naples_volturno_vive_museum",
        ],
        [
            "wave8_naples_volturno_italian_army",
            "wave8_naples_volturno_vive_museum",
        ],
        ["italian_army_volturno_1860", "vive_museum_volturno_1860"],
        (
            "Official military and museum accounts identify Garibaldi's men against "
            "Francis II's Bourbon army and a Garibaldian victory. The raw coalition "
            "label is corrected by excluding Piedmontese regulars; outcome orientation "
            "does not reverse."
        ),
        "state_formation_conflict",
        confidence=0.94,
    ),
}


WAVE8_NAPLES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Ferrara1815-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Ferrara1815-1"],
        "canonical_event": _canonical("Ferrara source-record conflation", 1815),
        "disposition": "terminal_exclusion",
        "hold_category": "source_conflation_and_duplicate_campaign_actions",
        "side_1_entity_ids": ["bianchi_austrian_army_naples_war_1815"],
        "side_2_entity_ids": ["murat_neapolitan_army_1815"],
        "duplicate_of_candidate_ids": [
            "hced-Casaglia1815-1",
            "hced-Occhiobello, 1815-1",
        ],
        "hold_reason": (
            "Harbottle's Ferrara entry says Murat attempted to force the Po and was "
            "repulsed by Bianchi, but its 12 April date and narrative conflate the "
            "already represented Occhiobello crossing attempt with Casaglia and the "
            "lifting of the siege of Ferrara. Emitting a third result would duplicate "
            "the same campaign actions."
        ),
        "evidence_refs": sorted(
            [
                "wave8_naples_1815_italian_army",
                "wave8_naples_harbottle_scan",
                "wave8_naples_murat_treccani",
            ]
        ),
    },
    "hced-Messina1860-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Messina1860-1"],
        "canonical_event": _canonical("Occupation of Messina", 1860),
        "disposition": "terminal_exclusion",
        "hold_category": "noncompetitive_negotiated_occupation",
        "side_1_entity_ids": ["garibaldian_southern_army_1860"],
        "side_2_entity_ids": ["two_sicilies_royal_army_1860"],
        "hold_reason": (
            "Medici occupied the city under a pact that left roughly 4,000 Bourbon "
            "troops inactive in the forts. The reviewed source supports negotiated "
            "occupation and control, not an opposing-force tactical result suitable "
            "for Elo."
        ),
        "evidence_refs": ["wave8_naples_risorgimento_treccani"],
    },
    "hced-Palermo1848-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Palermo1848-1"],
        "canonical_event": _canonical("Palermo source-record conflation", 1849),
        "disposition": "terminal_exclusion",
        "hold_category": "irreconcilable_year_conflict_and_duplicate",
        "side_1_entity_ids": ["sicilian_revolutionary_state_forces_1848_1849"],
        "side_2_entity_ids": ["two_sicilies_royal_army_sicily_1848_1849"],
        "source_described_side_1_entity_ids": ["garibaldian_southern_army_1860"],
        "source_described_side_2_entity_ids": ["two_sicilies_royal_army_1860"],
        "raw_identifier_year": 1848,
        "queue_year": 1849,
        "source_described_year": 1860,
        "duplicate_of_candidate_ids": ["hced-Palermo1860-1"],
        "hold_reason": (
            "The source-record identifier says 1848, the locked queue fields say "
            "1849, and the cited Harbottle entry describes Garibaldi's Thousand, "
            "Sicilian picciotti, and Lanza on 26-27 May—Palermo 1860. The row cannot "
            "be repaired without inventing which event was intended and duplicates "
            "the exact promoted Palermo 1860 row."
        ),
        "evidence_refs": sorted(
            [
                "wave8_naples_harbottle_scan",
                "wave8_naples_risorgimento_treccani",
                "wave8_naples_sicilian_revolution_oxford",
            ]
        ),
    },
}

# The shared exact-wave API calls every nonpromotion a hold. These three are
# terminal exclusions, not provisional research holds, and this alias preserves
# that API while keeping the stronger disposition explicit.
WAVE8_NAPLES_HOLDS = WAVE8_NAPLES_TERMINAL_EXCLUSIONS

WAVE8_NAPLES_CONTRACT_IDS = frozenset(WAVE8_NAPLES_CONTRACTS)
WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_NAPLES_TERMINAL_EXCLUSIONS
)
WAVE8_NAPLES_HOLD_IDS = WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS
WAVE8_NAPLES_RESERVED_IDS = (
    WAVE8_NAPLES_CONTRACT_IDS | WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS
)
WAVE8_NAPLES_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_naples_audit_signature() -> str:
    payload = {
        "contracts": WAVE8_NAPLES_CONTRACTS,
        "entities": WAVE8_NAPLES_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_NAPLES_EXPECTED_CANDIDATE_IDS),
        "sources": WAVE8_NAPLES_SOURCES,
        "terminal_exclusions": WAVE8_NAPLES_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_NAPLES_CONTRACTS), len(WAVE8_NAPLES_TERMINAL_EXCLUSIONS)) != (
        10,
        3,
    ):
        raise ValueError("Wave 8 Naples disposition inventory changed")
    if WAVE8_NAPLES_RESERVED_IDS != WAVE8_NAPLES_EXPECTED_CANDIDATE_IDS:
        raise ValueError("Wave 8 Naples reservations are incomplete")
    if WAVE8_NAPLES_CONTRACT_IDS & WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS:
        raise ValueError("Wave 8 Naples promotions and terminal exclusions overlap")
    if wave8_naples_audit_signature() != WAVE8_NAPLES_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Naples final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_NAPLES_SOURCES}
    if len(source_by_id) != len(WAVE8_NAPLES_SOURCES):
        raise ValueError("Wave 8 Naples source IDs are not unique")
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_NAPLES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_NAPLES_ENTITIES):
        raise ValueError("Wave 8 Naples entity IDs are not unique")

    forbidden_names = {"naples", "neapolitan army", "kingdom of naples"}
    for entity in WAVE8_NAPLES_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError("Wave 8 Naples identities must be alias-free")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError("Wave 8 Naples identity has an invalid finite window")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError("Wave 8 Naples opened a timeless generic identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 Naples identity permits rating inheritance")
        if list(entity["source_ids"]) != sorted(set(map(str, entity["source_ids"]))):
            raise ValueError("Wave 8 Naples entity sources must be deterministic")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError("Wave 8 Naples identity names an unknown source")

    for candidate_id, contract in WAVE8_NAPLES_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError("Wave 8 Naples promotion hash table drifted")
        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError("Wave 8 Naples promotion outcome orientation changed")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError("Wave 8 Naples contains an unsanctioned outcome reversal")
        if contract["actor_override"] is not True:
            raise ValueError("Wave 8 Naples actor correction is not explicit")
        evidence = list(map(str, contract["evidence_refs"]))
        outcome_sources = list(map(str, contract["outcome_source_ids"]))
        if evidence != sorted(set(evidence)) or outcome_sources != sorted(
            set(outcome_sources)
        ):
            raise ValueError("Wave 8 Naples provenance IDs must be deterministic")
        if not outcome_sources or not set(outcome_sources) <= set(evidence):
            raise ValueError("Wave 8 Naples lacks direct outcome provenance")
        if not set(evidence) <= set(source_by_id):
            raise ValueError("Wave 8 Naples promotion names an unknown source")
        for source_id in outcome_sources:
            if "outcome" not in source_by_id[source_id]["evidence_roles"]:
                raise ValueError("Wave 8 Naples outcome source lacks the outcome role")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcome_sources}
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError("Wave 8 Naples outcome source families drifted")

        canonical = contract["canonical_event"]
        low, high = int(canonical["year_low"]), int(canonical["year_high"])
        side_ids = [
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        ]
        if len(side_ids) != len(set(side_ids)):
            raise ValueError("Wave 8 Naples promotion sides overlap")
        for entity_id in side_ids:
            entity = entity_by_id.get(entity_id)
            if entity is None:
                raise ValueError("Wave 8 Naples promotion uses a non-lane identity")
            if int(entity["start_year"]) > low or int(entity["end_year"]) < high:
                raise ValueError("Wave 8 Naples promotion exceeds an identity window")

    for candidate_id, exclusion in WAVE8_NAPLES_TERMINAL_EXCLUSIONS.items():
        if exclusion["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError("Wave 8 Naples terminal hash table drifted")
        if exclusion["disposition"] != "terminal_exclusion":
            raise ValueError("Wave 8 Naples nonpromotion is not terminal")
        evidence = list(map(str, exclusion["evidence_refs"]))
        if evidence != sorted(set(evidence)) or not set(evidence) <= set(source_by_id):
            raise ValueError("Wave 8 Naples terminal provenance drifted")
        canonical = exclusion["canonical_event"]
        low, high = int(canonical["year_low"]), int(canonical["year_high"])
        for key in ("side_1_entity_ids", "side_2_entity_ids"):
            for entity_id in map(str, exclusion[key]):
                entity = entity_by_id.get(entity_id)
                if entity is None:
                    raise ValueError("Wave 8 Naples terminal row uses an unknown identity")
                if int(entity["start_year"]) > low or int(entity["end_year"]) < high:
                    raise ValueError("Wave 8 Naples terminal row exceeds an identity window")

    palermo = WAVE8_NAPLES_TERMINAL_EXCLUSIONS["hced-Palermo1848-1"]
    if (
        palermo["raw_identifier_year"],
        palermo["queue_year"],
        palermo["source_described_year"],
    ) != (1848, 1849, 1860):
        raise ValueError("Wave 8 Naples Palermo year conflict changed")
    for key in (
        "source_described_side_1_entity_ids",
        "source_described_side_2_entity_ids",
    ):
        for entity_id in map(str, palermo[key]):
            entity = entity_by_id.get(entity_id)
            if entity is None or not (
                int(entity["start_year"]) <= 1860 <= int(entity["end_year"])
            ):
                raise ValueError("Wave 8 Naples Palermo source-described side drifted")

    for candidate_id in (
        "hced-Calatafimi1860-1",
        "hced-Palermo1860-1",
        "hced-Milazzo1860-1",
        "hced-Volturno1860-1",
    ):
        side_ids = {
            *WAVE8_NAPLES_CONTRACTS[candidate_id]["side_1_entity_ids"],
            *WAVE8_NAPLES_CONTRACTS[candidate_id]["side_2_entity_ids"],
        }
        if any("piedmont" in item or "sardinia" in item for item in side_ids):
            raise ValueError("Wave 8 Naples incorrectly credits Piedmont in 1860")


def validate_wave8_naples_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_NAPLES_CONTRACTS,
        WAVE8_NAPLES_TERMINAL_EXCLUSIONS,
        lane_name=_LANE_NAME,
    )


def install_wave8_naples_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_NAPLES_SOURCES,
        lane_name=_LANE_NAME,
    )


def install_wave8_naples_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_NAPLES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_naples_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_naples_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_NAPLES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_naples_",
    )


def wave8_naples_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_NAPLES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_naples_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_NAPLES_TERMINAL_EXCLUSIONS),
        "newly_rated_events": len(WAVE8_NAPLES_CONTRACTS),
        "promotion_contracts": len(WAVE8_NAPLES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_NAPLES_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_NAPLES_TERMINAL_EXCLUSIONS),
    }
