"""Candidate-keyed exact outcomes for HCED's ``Holy Roman Empire`` label.

The source label is too broad to rate as an actor.  This lane therefore opens
no label, alias, or continuity window for the Holy Roman Empire.  It promotes
only eighteen independently reviewed engagements and gives each side an
alias-free formation bounded to the source event's exact year interval.

The other five exact-label rows remain nonrating: Milan 1161 is an unknown
hold because its decisive result belongs to 1162, Rakersberg 1416 is a
terminal exclusion, and Ulm 1376, Reutlingen 1377, and Zatec 1421 already have
canonical owners.  Ten adjacent rows and every discovery inventory are pinned
as coverage-only.  Winnerless discovery data remain unknown, never draws.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
)


__all__ = (
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS",
    "WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS",
    "install_wave8_holy_roman_empire_exact_entities",
    "install_wave8_holy_roman_empire_exact_sources",
    "promote_wave8_holy_roman_empire_exact_contracts",
    "validate_wave8_holy_roman_empire_exact_cross_dataset_inventories",
    "validate_wave8_holy_roman_empire_exact_current_artifact_state",
    "validate_wave8_holy_roman_empire_exact_integration_dispositions",
    "validate_wave8_holy_roman_empire_exact_queue_contracts",
    "wave8_holy_roman_empire_exact_audit_signature",
    "wave8_holy_roman_empire_exact_cohort_counts",
    "wave8_holy_roman_empire_exact_counts",
    "wave8_holy_roman_empire_exact_metadata",
)


_LANE_NAME = "Wave 8 exact Holy Roman Empire actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_holy_roman_empire_exact"
_EVENT_ID_PREFIX = "hced_wave8_hre_exact_"
_EXACT_LABEL = "holy roman empire"
_FORBIDDEN_OUTCOME_FAMILIES = frozenset(
    {"brecke", "hced", "wikidata", "wikidata_battles"}
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return _sha256_json(dict(row))


def _string_values(value: Any) -> Iterable[str]:
    """Yield exact string values from nested event provenance structures."""

    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _string_values(nested)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for nested in value:
            yield from _string_values(nested)


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES: dict[str, str] = {
    "hced-Alte Veste1632-1": "efd685e09b1543ad2c8ab1968d00eaecdadabf7c09c606dd019c477e93f2f60b",
    "hced-Boulay1635-1": "95c06d9fa88a8bc125b57f5bdd975155bdad1a993adb2e524b8941e0f54bbb68",
    "hced-Brandeis1639-1": "7dbfbe9dc3dbd088a87940059f9a3db01972cc7bb10fefdca61dcd57dc44b755",
    "hced-Breisach1638-1": "d644583e4937a9fc61e314535e48dcd4c3d0100389aeee70fb4f78908f6559fa",
    "hced-Breitenfeld1631-1": "bbf4353333909a8cd7334752bed7ba3afc0943e47627545057ff5d04ddca0b60",
    "hced-Breitenfeld1642-1": "3a0cf9398f4b02d744fc7f08300c0d9b60aef3afe809562a9b3abd885ff9300d",
    "hced-Brema1638-1": "84057e978507cd6a257dc7f556e67055b50738da9afb03f802ca7e4ebbb57a52",
    "hced-Cortenuova1237-1": "fed53c6f98fa2f7d70856b9516c019aca4bac93e7acae81c04733fc9b0a41e15",
    "hced-Harkany1687-1": "7a664230133bf230f8912c39f9f1aa6e9fe4684d8874febb35d33d47f5a8fad0",
    "hced-Milan1158-1": "00071526b86082cd1cb427912b8fd143d5e0547045055597b31a0e8df46c6ef0",
    "hced-Milan1161-1": "7279b443d88c0c9bfb2e7e67bbde40ab70259e1872d5428c96a95cd297762f66",
    "hced-Mirischlau1600-1": "a7509c1ea9d8947268e5811b0cc527f2c72a191445fcae1d06b8b29650f46159",
    "hced-Neubrandenburg1631-1": "3b379d00ad487c9a97870f02b7e69c9a7e5dc42b9857d61bb205767eb6692ef2",
    "hced-Parma1247-1248-1": "2b61beff1a2615b4c744cce90cd361448b0ab6a9814cf0801cdd8de760bc2cbd",
    "hced-Rakersberg1416-1": "b970193f83eec6aab8fcb9cb1e2afa3520120b4b979c360c0cc07ce0457e6051",
    "hced-Reutlingen1377-1": "72dc18e36339f54002521a36f34fe795395b562285f439ba7a11584cbbc7a127",
    "hced-Rome1167-1": "973a3f40a49a159f9e271b8dd44e250d3b5760004b0093c6b63ba50144b046fc",
    "hced-Tortona1155-1": "54d4b3073c23e3130ceb3a3a2fa58bb55ae05ff428b74c4dd7a569076e837748",
    "hced-Ulm1376-1": "db337ec870aaed28d9899c17ef2cc52bc159846e31c1dbe7f3922badfe9455cc",
    "hced-Unstrut1075-1": "1cfa9cb51e39ba5c20c8c248451779885ec524cf3cf38e23878a1130e113605b",
    "hced-Welfesholze1115-1": "669f4cef6c40b33592ffa25a6495d9747e327b0d1db132b6e9cefb0dcad6c463",
    "hced-Wittenweier1638-1": "f110b6b88be1f87f7a45b1024feca902b63ee6409d60959991101554cbb53b2c",
    "hced-Zatec1421-1": "1e99ddf6f96f2cf434b6f5d75c05590fad0f85f017e1de9c5261c23cb88114e3",
}

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES: dict[str, str] = {
    "hced-Alte Veste1632-1": "3d84223f0361ca2543f4a9e381cd99390ecb2f66eda6d08a3bd594b69e09840d",
    "hced-Boulay1635-1": "9b1351036631ba9f457f4aa128ff310244995fa339bfe86c58fa2a08d7aa6597",
    "hced-Brandeis1639-1": "61c49e604e4c63812faf10db462cca9a3bbbd4d0fd2dd882e33ca490f7899d88",
    "hced-Breisach1638-1": "afa6d0eb0b529017f6fa7a31e6a2e143db480d605a3803e0a2d1e8c90613eeb4",
    "hced-Breitenfeld1631-1": "ccdd4b35b10d763020bc9f953e6e5fad178e237ad189fedfbc9a3b4bdd945ac1",
    "hced-Breitenfeld1642-1": "832ca5f2b2b09b54a51a0533f3ed0b79dd1b51738572bb9eccedb1c6764189fc",
    "hced-Brema1638-1": "ad7a64519a559623db8adeb4735e311542d9339822941af07242dbc1f3fdb0ba",
    "hced-Cortenuova1237-1": "2c96412d3b23649ae671b65b3e88fef6e3a150a25c6ee4e80cafdc437f762ab9",
    "hced-Harkany1687-1": "7744fc23f6056a8c7c17b5d895f45411945a9b1a40c6058ec9ebeade37515b93",
    "hced-Milan1158-1": "e1b33f2c2b8cbf20c92dc99a426f04bc433078e777063f1acfb062b1d3241eb9",
    "hced-Milan1161-1": "459c8ad31c627434481fa480ee35bb8f652f208a89b71dd8f4b5a9f49934b611",
    "hced-Mirischlau1600-1": "604d63b9f7140ebec48d3289e435ac3241c8f5ae51d791ff90cc58d3b9aebde3",
    "hced-Neubrandenburg1631-1": "1e296a47886e6b162ac007b8e82be3771ef88efc8ae2dff2b0dfe36602731140",
    "hced-Parma1247-1248-1": "544673fc8c87e299048e2915879a549675db3249477289d54901e725c9424c10",
    "hced-Rakersberg1416-1": "7e53d9f72ba0cfb42f81cdceff978ed2df8ce83e1e1ff4dfc9a7eb3fff7b1be2",
    "hced-Reutlingen1377-1": "7766e8b75a436ae9b349a585fd322423fbbed716edcc9f401319a44ecc5bfb21",
    "hced-Rome1167-1": "8ded1bc0199e7d3f75c55e24fdb8d7274e9a1006d0d2728a034ef690142a3ef2",
    "hced-Tortona1155-1": "ec09a45f6fbdb2150026fee574a390d66fe112b8b2f2c19ebbe6a359a9d76918",
    "hced-Ulm1376-1": "f46fd9b3d5e3f19d31ffe9e59f465b1810cd3257db08d4f3ca822a2f5f76b261",
    "hced-Unstrut1075-1": "103e4c0d6634beb8380660bb9b9c64f442cc63aeff10e4bc7a95ade472a8ee1b",
    "hced-Welfesholze1115-1": "2c332d936078d3d15ab3664f6dad9b6ae03cb27c9aa7bbdb6dd53608abd8ddf4",
    "hced-Wittenweier1638-1": "976fc416e82951776c1ea277c3532a0d431845d059a7454ed30fd5c0e0da7084",
    "hced-Zatec1421-1": "36b13edb95f46ea894a8a654aa16e626af287dcc93161ae196876364ba4eea21",
}

_EXACT_ID_DIGEST = "7ce03b4fbb33bc7ea1525ef6d8b2256cc0d9a5e2834b103d39c02e8cc92708fc"
_EXACT_CANONICAL_MAP_DIGEST = "4aa15e61a3bba1d5bb5cb3770b15b099c1514eb9b724ef81f7d47d30cb9f1b9a"
_EXACT_FULL_MAP_DIGEST = "835318489aaebd917d2a6395878061b5c516fae51b1d3b2ab1c71b36f16a45f1"


_ADJACENT_ROW_HASHES: dict[str, str] = {
    "hced-Alessandria1174-1": "7383435e6cd5941fffc19a272f0d9bb9ac4633a7a785bca9002508b2ae674cc3",
    "hced-Damascus1148-1": "9f711959fad105754c0cb6bdaa72b590e74171428571d640fbfb666210256f71",
    "hced-Fossalta1248-1": "d7425ee0440574ede40a56ab7afaf843854a2ca3cd72b0d8c8c2b18d0c6d138d",
    "hced-Liegnitz1241-1": "a83b38bef36e20bf0c36d38882030a67e46c7b6fdde554f79cdd7e4916c3663e",
    "hced-Lutter am Barenberg1626-1": "4188976a0e8bf691696ee8ba093027ca23106fbb60d2bd28fe6f95d7916aaa18",
    "hced-Nordlingen1634-1": "0506c3f043eb892ae438f4228aee8b2b8ae81ea1c4aa99be0fbd0a5f996b9df7",
    "hced-Oland (1st)1564-1": "11784bacaddf92fc34ba9b65c18df8d7d6140dfa714c1873c1c921e77b4375fa",
    "hced-Oland (2nd)1564-1": "95fa458807329bc03bf1a1bc44bb79b0b661d3d8df0fa3ea9ea0890684506d7b",
    "hced-Padua1509-1": "ba33d6b6b5e90507faac9fbf5e1df1fedf1e4b9ee2ddc2e60223625176a3528d",
    "hced-Vlaardingen1018-1": "90336a00f75950e24ad6cf69ed226fdca076a2c05bd027773d9711534d81a87c",
}

_ADJACENT_FULL_ROW_HASHES: dict[str, str] = {
    "hced-Alessandria1174-1": "f64af027d5a183962032ee71104d5f1f9f7f65a8d7247443a9b63b99a3b8ddce",
    "hced-Damascus1148-1": "db7aa750653cb96e1ba17d0bd4c73f3d8035a82c42116ab988ea5a0a6b23c975",
    "hced-Fossalta1248-1": "116f52e905165a514d52479cce37a1968a972cf384dd8c6509f2693e609d591e",
    "hced-Liegnitz1241-1": "f50650d993a1690cc97380fa128b9c63b29bdc303de757bec13963d02c430248",
    "hced-Lutter am Barenberg1626-1": "cee21ee3fa78c5b5c4c9fe1c2ea6086105d0e5e971e9fc98e263a8753b80bdf9",
    "hced-Nordlingen1634-1": "cc6e87444a7d7f3185179bb91953bfdfe1397be5b2630755121910f8b8d30320",
    "hced-Oland (1st)1564-1": "a65477547b1e2714c433881ea79249df5d25dd70ba1f27b276426e0afb7fca9c",
    "hced-Oland (2nd)1564-1": "78089fa8ebdd6dae7d50b038c0a6023bb485c5e8eb4e31630358b93b78d16b7d",
    "hced-Padua1509-1": "5e4a19f81bde70fb62895903db6e4a24b7e16ffb4cef6c4eee92eccd1c48e2ea",
    "hced-Vlaardingen1018-1": "0d1b06b4f4187aae4982519c2bf3eb0c544abdd8366132c6aeed85cdca57654d",
}

_ADJACENT_REASONS: dict[str, str] = {
    "hced-Alessandria1174-1": "defensive_success_resolves_in_1175_outside_locked_row",
    "hced-Damascus1148-1": "composite_crusader_and_defender_formations_require_separate_lane",
    "hced-Fossalta1248-1": "reviewed_battle_is_1249_not_locked_1248",
    "hced-Liegnitz1241-1": "composite_mongol_and_silesian_coalitions_require_separate_lane",
    "hced-Lutter am Barenberg1626-1": "composite_danish_and_imperial_coalitions_require_separate_lane",
    "hced-Nordlingen1634-1": "composite_spanish_imperial_and_swedish_allied_formations_require_separate_lane",
    "hced-Oland (1st)1564-1": "distinct_lubeck_danish_swedish_naval_action_requires_separate_lane",
    "hced-Oland (2nd)1564-1": "distinct_lubeck_danish_swedish_naval_action_requires_separate_lane",
    "hced-Padua1509-1": "raw_winner_reversed_and_requires_explicit_outcome_override_lane",
    "hced-Vlaardingen1018-1": "composite_imperial_and_frisian_formations_require_separate_lane",
}

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "canonical_row_sha256": _ADJACENT_ROW_HASHES[candidate_id],
        "disposition": "coverage_only_separate_exact_actor_lane",
        "full_row_sha256": _ADJACENT_FULL_ROW_HASHES[candidate_id],
        "reason_code": _ADJACENT_REASONS[candidate_id],
    }
    for candidate_id in sorted(_ADJACENT_ROW_HASHES)
}

_ADJACENT_ID_DIGEST = "e01a64f5f8f47dc7acce3b844ae210c71dca18f664b1727a83ee006941540788"
_ADJACENT_CANONICAL_MAP_DIGEST = "16d2e9596f9cc634f9720f3bc1626403391740339e3ab9990e0b45f5dffe45ff"
_ADJACENT_FULL_MAP_DIGEST = "9a7e54d3be6d07161fc561c4708e4b823205ca36bd87fc52dfd8ce00c05128b0"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    }


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_hre_exact_austrian_state_archives_generals",
        "Die kaiserlichen Generale 1618-1655",
        "https://www.oesta.gv.at/dam/jcr%3A3cb11fb4-f0f1-4589-85f9-2d4a16d29365/Antonio%20Schmidt-Brentano%20-%20Die%20kaiserlichen%20Generale%202022.pdf",
        "Austrian State Archives",
        "official_archival_reference",
        "austrian_state_archives_generals",
    ),
    _source(
        "wave8_hre_exact_basler_wittenweier",
        "Historical study of the Battle of Wittenweier",
        "https://www.e-periodica.ch/digbib/view?pid=bzg-002%3A1912%3A11%3A%3A362",
        "Basler Zeitschrift für Geschichte und Altertumskunde",
        "scholarly_historical_journal",
        "basler_zeitschrift_wittenweier",
    ),
    _source(
        "wave8_hre_exact_cambridge_modern_history",
        "The Thirty Years' War",
        "https://mateo.uni-mannheim.de/camenaref/cmh/cmh413.html",
        "Cambridge Modern History / University of Mannheim",
        "scholarly_historical_reference",
        "cambridge_modern_history_thirty_years",
    ),
    _source(
        "wave8_hre_exact_caracol_breme",
        "Study of the 1638 Lombard campaign and Breme",
        "https://www.edizionicaracol.it/wordpress/wp-content/uploads/2020/10/Studi-e-Ricerche-n.-7-low-1.pdf",
        "Edizioni Caracol",
        "scholarly_historical_study",
        "caracol_breme_study",
    ),
    _source(
        "wave8_hre_exact_czech_library_brandeis",
        "Research response on the 1639 battle near Lobkovice",
        "https://www.ptejteseknihovny.cz/dotazy/bitva-u-lobkovic",
        "National Library of the Czech Republic",
        "national_library_research_reference",
        "czech_national_library_reference",
    ),
    _source(
        "wave8_hre_exact_deutsche_biographie_hoyer",
        "Hoyer von Mansfeld",
        "https://www.deutsche-biographie.de/gnd137124988.html?language=en",
        "Deutsche Biographie",
        "national_scholarly_biography",
        "deutsche_biographie_hoyer",
    ),
    _source(
        "wave8_hre_exact_eb1911",
        "Encyclopaedia Britannica 1911 military chronology",
        "https://en.wikisource.org/wiki/Page%3AEB1911_-_Volume_26.djvu/895",
        "Encyclopaedia Britannica",
        "historical_reference_encyclopedia",
        "britannica_1911_warfare",
    ),
    _source(
        "wave8_hre_exact_freed_barbarossa",
        "Frederick Barbarossa",
        "https://academic.oup.com/yale-scholarship-online/book/33328/chapter-abstract/286036920",
        "Yale University Press / Oxford Academic",
        "scholarly_historical_monograph",
        "freed_barbarossa_yale",
    ),
    _source(
        "wave8_hre_exact_geschichtsquellen_gesta",
        "Gesta Friderici I. imperatoris in Lombardia",
        "https://geschichtsquellen.de/werk/1993",
        "Geschichtsquellen des deutschen Mittelalters",
        "scholarly_primary_source_registry",
        "geschichtsquellen_gesta_friderici",
    ),
    _source(
        "wave8_hre_exact_glasgow_schuerger",
        "The archaeology of the Battle of the Alte Veste",
        "https://theses.gla.ac.uk/6508/1/2015schuergerphd.pdf",
        "University of Glasgow",
        "doctoral_thesis",
        "glasgow_schuerger_2015",
    ),
    _source(
        "wave8_hre_exact_grillo_parma",
        "The siege of Parma and the destruction of Vittoria",
        "https://air.unimi.it/handle/2434/1008588",
        "University of Milan institutional repository",
        "scholarly_historical_study",
        "grillo_parma_2023",
    ),
    _source(
        "wave8_hre_exact_hadtortenelmi_harsany",
        "Study of the 1687 Battle of Harsány",
        "https://epa.oszk.hu/00000/00018/00287/pdf/EPA00018_hadtortenelmi_2020_04.pdf",
        "Hadtörténelmi Közlemények",
        "scholarly_military_history_journal",
        "hadtortenelmi_harsany_study",
    ),
    _source(
        "wave8_hre_exact_kreis_saarlouis",
        "Historical chronology of the Saarlouis district",
        "https://www.kreis-saarlouis.de/Geschichte.htm",
        "Landkreis Saarlouis",
        "official_regional_history",
        "kreis_saarlouis_local_history",
    ),
    _source(
        "wave8_hre_exact_lvr_rainald",
        "Rainald von Dassel",
        "https://rheinische-geschichte.lvr.de/Persoenlichkeiten/rainald-von-dassel/DE-2086/lido/57c95b4df1c8a3.86417112",
        "Portal Rheinische Geschichte / LVR",
        "scholarly_regional_biography",
        "lvr_rainald_dassel",
    ),
    _source(
        "wave8_hre_exact_lwl_german_civil",
        "Chronology of the German civil wars",
        "https://www.lwl.org/westfaelische-geschichte/portal/Internet/finde/langDatensatz.php?urlID=29&url_tabelle=tab_websegmente",
        "LWL Westfälische Geschichte",
        "scholarly_regional_chronology",
        "lwl_german_civil_wars",
    ),
    _source(
        "wave8_hre_exact_miraslau_study",
        "Historical study of the Battle of Mirăslău",
        "https://dergipark.org.tr/en/download/article-file/4254068",
        "DergiPark scholarly repository",
        "scholarly_historical_article",
        "miraslau_scholarly_article",
    ),
    _source(
        "wave8_hre_exact_neubrandenburg_city",
        "Neubrandenburg in the Thirty Years' War",
        "https://www.neubrandenburg.de/index.php?FID=2751.779.1&ModID=7&object=tx%7C2751.779.1",
        "City of Neubrandenburg",
        "official_municipal_history",
        "neubrandenburg_city_history",
    ),
    _source(
        "wave8_hre_exact_pecs_harsany",
        "Research context for the Battle of Harsány memorial",
        "https://art.pte.hu/hu/hirek/palyazatok/harsany-hegyi-csata-emlekhelyenek-tovabbepitese-palyazat",
        "University of Pécs",
        "university_historical_research_context",
        "pecs_harsany_research",
    ),
    _source(
        "wave8_hre_exact_rct_breisach",
        "View of the siege of Breisach, 1638",
        "https://militarymaps.rct.uk/thirty-years-war-1618-48/view-of-the-siege-of-breisach-1638-breisach-am-rhein-vieux-brisach-baden-wurttemburg-germany",
        "Royal Collection Trust",
        "curated_historical_map_catalogue",
        "royal_collection_breisach_1638",
    ),
    _source(
        "wave8_hre_exact_rct_breme",
        "View of Breme, 1638",
        "https://militarymaps.rct.uk/franco-spanish-war-1635-59/view-of-breme-1638-breme-lombardy-italy-45deg0739n-08deg3732e",
        "Royal Collection Trust",
        "curated_historical_map_catalogue",
        "royal_collection_breme_1638",
    ),
    _source(
        "wave8_hre_exact_ricchiuti_monte_porzio",
        "Study of the Battle of Monte Porzio",
        "https://iris.uniroma1.it/handle/11573/1742945",
        "Sapienza University of Rome",
        "scholarly_historical_study",
        "ricchiuti_monte_porzio_2025",
    ),
    _source(
        "wave8_hre_exact_robinson_henry_iv",
        "Henry IV and Saxony, 1065-1075",
        "https://www.cambridge.org/core/books/abs/henry-iv-of-germany-10561106/henry-iv-and-saxony-10651075/5E8FAD17B81FD7EECACFF70D1B1B6B39",
        "Cambridge University Press",
        "scholarly_historical_monograph",
        "robinson_henry_iv",
    ),
    _source(
        "wave8_hre_exact_rostock_mecklenburg",
        "Historical volume on Mecklenburg and Neubrandenburg",
        "https://rosdok.uni-rostock.de/do/pdfdownload/recordIdentifier/rosdok_ppn178054197X/rosdok_ppn178054197X.pdf",
        "University Library Rostock",
        "digitized_scholarly_history",
        "rostock_mecklenburg_history",
    ),
    _source(
        "wave8_hre_exact_showalter",
        "The Encyclopedia of Warfare",
        "https://archive.org/details/isbn_9781435151260",
        "Facts On File / Internet Archive catalogue",
        "scholarly_military_history_reference",
        "showalter_encyclopedia_warfare",
    ),
    _source(
        "wave8_hre_exact_treccani_barbarossa",
        "Federico I detto il Barbarossa",
        "https://www.treccani.it/enciclopedia/federico-i-detto-in-italia-il-barbarossa-imperatore_%28Enciclopedia-Italiana%29/",
        "Treccani",
        "national_scholarly_encyclopedia",
        "treccani_barbarossa",
    ),
    _source(
        "wave8_hre_exact_treccani_cortenuova",
        "Battaglia di Cortenuova",
        "https://www.treccani.it/enciclopedia/battaglia-di-cortenuova_%28Federiciana%29/",
        "Treccani Federiciana",
        "national_scholarly_encyclopedia",
        "treccani_federiciana_cortenuova",
    ),
)

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "wave8_great_northern_exact_landers_field_forge",
        "title": "The Field and the Forge: Population, Production, and Power in the Pre-Industrial West",
        "url": "https://academic.oup.com/book/1842",
        "publisher": "Oxford University Press",
        "license": "Citation and link only",
        "source_type": "scholarly_military_history_monograph",
        "accessed": "2026-07-21",
        "source_family_id": "landers_field_forge",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    },
)

_NEW_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES
}
_REUSED_SOURCE_BY_ID = {
    str(source["id"]): source
    for source in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES
}
_ALL_SOURCE_BY_ID = {**_NEW_SOURCE_BY_ID, **_REUSED_SOURCE_BY_ID}


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Unstrut1075-1": (
        "wave8_hre_exact_lwl_german_civil",
        "wave8_hre_exact_robinson_henry_iv",
    ),
    "hced-Welfesholze1115-1": (
        "wave8_hre_exact_deutsche_biographie_hoyer",
        "wave8_hre_exact_lwl_german_civil",
    ),
    "hced-Tortona1155-1": (
        "wave8_hre_exact_freed_barbarossa",
        "wave8_hre_exact_geschichtsquellen_gesta",
        "wave8_hre_exact_treccani_barbarossa",
    ),
    "hced-Milan1158-1": (
        "wave8_hre_exact_freed_barbarossa",
        "wave8_hre_exact_treccani_barbarossa",
    ),
    "hced-Rome1167-1": (
        "wave8_hre_exact_lvr_rainald",
        "wave8_hre_exact_ricchiuti_monte_porzio",
    ),
    "hced-Cortenuova1237-1": (
        "wave8_hre_exact_showalter",
        "wave8_hre_exact_treccani_cortenuova",
    ),
    "hced-Parma1247-1248-1": (
        "wave8_hre_exact_grillo_parma",
        "wave8_hre_exact_showalter",
    ),
    "hced-Mirischlau1600-1": (
        "wave8_hre_exact_miraslau_study",
        "wave8_hre_exact_showalter",
    ),
    "hced-Breitenfeld1631-1": (
        "wave8_great_northern_exact_landers_field_forge",
        "wave8_hre_exact_eb1911",
    ),
    "hced-Neubrandenburg1631-1": (
        "wave8_hre_exact_neubrandenburg_city",
        "wave8_hre_exact_rostock_mecklenburg",
    ),
    "hced-Alte Veste1632-1": (
        "wave8_hre_exact_eb1911",
        "wave8_hre_exact_glasgow_schuerger",
        "wave8_hre_exact_showalter",
    ),
    "hced-Boulay1635-1": (
        "wave8_hre_exact_cambridge_modern_history",
        "wave8_hre_exact_kreis_saarlouis",
    ),
    "hced-Breisach1638-1": (
        "wave8_hre_exact_cambridge_modern_history",
        "wave8_hre_exact_rct_breisach",
        "wave8_hre_exact_showalter",
    ),
    "hced-Brema1638-1": (
        "wave8_hre_exact_caracol_breme",
        "wave8_hre_exact_rct_breme",
    ),
    "hced-Wittenweier1638-1": (
        "wave8_great_northern_exact_landers_field_forge",
        "wave8_hre_exact_basler_wittenweier",
        "wave8_hre_exact_cambridge_modern_history",
    ),
    "hced-Brandeis1639-1": (
        "wave8_hre_exact_austrian_state_archives_generals",
        "wave8_hre_exact_cambridge_modern_history",
        "wave8_hre_exact_czech_library_brandeis",
    ),
    "hced-Breitenfeld1642-1": (
        "wave8_great_northern_exact_landers_field_forge",
        "wave8_hre_exact_cambridge_modern_history",
    ),
    "hced-Harkany1687-1": (
        "wave8_great_northern_exact_landers_field_forge",
        "wave8_hre_exact_hadtortenelmi_harsany",
        "wave8_hre_exact_pecs_harsany",
    ),
}


def _canonical(
    name: str,
    low: int,
    high: int,
    date_text: str,
    start_date: str,
    end_date: str,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "start_date": start_date,
        "year_high": high,
        "year_low": low,
    }


_EVENT_SPECS: dict[str, dict[str, Any]] = {
    "hced-Unstrut1075-1": {
        "canonical": _canonical(
            "Battle of Langensalza (Unstrut)", 1075, 1075,
            "9 June 1075", "1075-06-09", "1075-06-09",
            "source_stated_day", "single_pitched_battle_at_langensalza",
        ),
        "side_ids": (
            "henry_iv_royal_episcopal_field_army_langensalza_1075",
            "saxon_rebel_field_host_langensalza_1075",
        ),
        "side_names": (
            "Henry IV's royal-episcopal field army at Langensalza (1075)",
            "Saxon rebel field host at Langensalza (1075)",
        ),
        "region": "Thuringia and Saxony",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "civil_war",
        "cohort": "german_civil_wars",
        "scale_level": 2,
        "cluster_id": "hced_war_german_civil_wars",
        "audit_note": "The royal-episcopal field army defeated the Saxon rebel host in the bounded Battle of Langensalza; no empire-wide continuity is inferred.",
    },
    "hced-Welfesholze1115-1": {
        "canonical": _canonical(
            "Battle of Welfesholz", 1115, 1115,
            "11 February contemporary / 18 February proleptic Gregorian 1115",
            "1115-02-11", "1115-02-18", "source_stated_dual_calendar_day",
            "single_pitched_battle_at_welfesholz",
        ),
        "side_ids": (
            "lothair_saxon_rhenish_thuringian_rebel_coalition_welfesholz_1115",
            "hoyer_mansfeld_henry_v_imperial_field_army_welfesholz_1115",
        ),
        "side_names": (
            "Lothair's Saxon-Rhenish-Thuringian rebel coalition at Welfesholz (1115)",
            "Hoyer of Mansfeld's Henry V-aligned field army at Welfesholz (1115)",
        ),
        "region": "Saxony and Thuringia",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "civil_war",
        "cohort": "german_civil_wars",
        "scale_level": 2,
        "cluster_id": "hced_war_german_civil_wars",
        "audit_note": "The event-bounded rebel coalition defeated Hoyer's Henry V-aligned army; neither side is treated as a timeless polity.",
    },
    "hced-Tortona1155-1": {
        "canonical": _canonical(
            "Siege of Tortona (1155)", 1155, 1155,
            "13 February-18 April 1155", "1155-02-13", "1155-04-18",
            "source_bounded_day_range", "single_siege_capitulation_and_destruction_of_tortona",
        ),
        "side_ids": (
            "frederick_barbarossa_pavian_montferrat_malaspina_siege_host_tortona_1155",
            "tortona_communal_garrison_milanese_relief_force_1155",
        ),
        "side_names": (
            "Frederick Barbarossa's Pavian-Montferrat-Malaspina siege host at Tortona (1155)",
            "Tortona communal garrison and Milanese relief force (1155)",
        ),
        "region": "Lombardy and Piedmont",
        "kind": "event_bounded_siege_force",
        "confidence": 0.97,
        "war_type": "interstate_limited",
        "cohort": "barbarossa_italian_expeditions",
        "scale_level": 2,
        "cluster_id": "hced_war_frederick_s_1st_expedition_to_italy",
        "audit_note": "The contract covers the armed investment, resistance, capitulation, and destruction of Tortona, not a generic HRE victory.",
    },
    "hced-Milan1158-1": {
        "canonical": _canonical(
            "Siege of Milan (1158)", 1158, 1158,
            "6 August-7 September 1158", "1158-08-06", "1158-09-07",
            "source_bounded_day_range", "single_siege_and_capitulation_of_milan_in_1158",
        ),
        "side_ids": (
            "frederick_barbarossa_pavian_cremonese_lodigian_siege_host_milan_1158",
            "milan_communal_defenders_1158",
        ),
        "side_names": (
            "Frederick Barbarossa's Pavian-Cremonese-Lodigian siege host at Milan (1158)",
            "Milan communal defenders (1158)",
        ),
        "region": "Lombardy",
        "kind": "event_bounded_siege_force",
        "confidence": 0.96,
        "war_type": "interstate_limited",
        "cohort": "barbarossa_italian_expeditions",
        "scale_level": 2,
        "cluster_id": "hced_war_frederick_s_expedition_to_italy",
        "audit_note": "This owns only the 1158 armed siege and capitulation, not Milan's later 1162 surrender and destruction.",
    },
    "hced-Rome1167-1": {
        "canonical": _canonical(
            "Battle of Monte Porzio (Tusculum)", 1167, 1167,
            "29 May contemporary / 5 June proleptic Gregorian 1167",
            "1167-05-29", "1167-06-05", "source_stated_dual_calendar_day",
            "single_pitched_siege_relief_battle_at_monte_porzio",
        ),
        "side_ids": (
            "christian_mainz_rainald_dassel_tusculan_relief_force_monte_porzio_1167",
            "commune_of_rome_field_army_monte_porzio_1167",
        ),
        "side_names": (
            "Christian of Mainz-Rainald of Dassel Tusculan relief force at Monte Porzio (1167)",
            "Commune of Rome field army at Monte Porzio (1167)",
        ),
        "region": "Latium and Rome",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "barbarossa_italian_expeditions",
        "scale_level": 2,
        "cluster_id": "hced_war_wars_of_the_lombard_league",
        "audit_note": "The raw Papal States loser is corrected to the Roman communal field army while the source's side-1 outcome remains unchanged.",
    },
    "hced-Cortenuova1237-1": {
        "canonical": _canonical(
            "Battle of Cortenuova", 1237, 1237,
            "27 November contemporary / 4 December proleptic Gregorian 1237",
            "1237-11-27", "1237-12-04", "source_stated_dual_calendar_day",
            "single_pitched_battle_at_cortenuova",
        ),
        "side_ids": (
            "frederick_ii_imperial_sicilian_campaign_army_cortenuova_1237",
            "pietro_tiepolo_lombard_league_field_army_cortenuova_1237",
        ),
        "side_names": (
            "Frederick II's imperial-Sicilian campaign army at Cortenuova (1237)",
            "Pietro Tiepolo's Lombard League field army at Cortenuova (1237)",
        ),
        "region": "Lombardy",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "frederick_ii_lombard_conflicts",
        "scale_level": 2,
        "cluster_id": "hced_war_imperial_papal_wars",
        "audit_note": "A discrete field battle is rated; no Lombard-war or imperial continuity is created.",
    },
    "hced-Parma1247-1248-1": {
        "canonical": _canonical(
            "Siege of Parma and Vittoria (1247-1248)", 1247, 1248,
            "July 1247-18 February 1248", "1247-07-01", "1248-02-18",
            "source_bounded_month_to_day_range", "single_siege_ending_in_the_vittoria_sortie",
        ),
        "side_ids": (
            "parma_guelph_communal_sortie_force_vittoria_1247_1248",
            "frederick_ii_imperial_siege_host_parma_1247_1248",
        ),
        "side_names": (
            "Parma Guelph communal sortie force at Vittoria (1247-1248)",
            "Frederick II's imperial siege host at Parma (1247-1248)",
        ),
        "region": "Parma and Lombardy",
        "kind": "event_bounded_siege_force",
        "confidence": 0.97,
        "war_type": "interstate_limited",
        "cohort": "frederick_ii_lombard_conflicts",
        "scale_level": 2,
        "cluster_id": "hced_war_imperial_papal_war",
        "audit_note": "The decisive armed sortie and destruction of Vittoria ended the bounded siege; no campaign-wide result is inferred.",
    },
    "hced-Mirischlau1600-1": {
        "canonical": _canonical(
            "Battle of Mirăslău", 1600, 1600,
            "18 September 1600", "1600-09-18", "1600-09-18",
            "source_stated_day", "single_pitched_battle_at_miraslau",
        ),
        "side_ids": (
            "basta_transylvanian_noble_coalition_miraslau_1600",
            "michael_wallachian_szekely_field_army_miraslau_1600",
        ),
        "side_names": (
            "Basta's Transylvanian noble coalition at Mirăslău (1600)",
            "Michael's Wallachian-Székely field army at Mirăslău (1600)",
        ),
        "region": "Transylvania",
        "kind": "event_bounded_field_force",
        "confidence": 0.97,
        "war_type": "interstate_limited",
        "cohort": "miraslau_1600",
        "scale_level": 3,
        "cluster_id": "hced_war_balkan_national_wars",
        "audit_note": "Basta's Transylvanian-Habsburg-aligned coalition is used instead of a generic empire actor.",
    },
    "hced-Breitenfeld1631-1": {
        "canonical": _canonical(
            "First Battle of Breitenfeld", 1631, 1631,
            "7 September Julian / 17 September Gregorian 1631",
            "1631-09-07", "1631-09-17", "source_stated_dual_calendar_day",
            "single_pitched_battle_first_breitenfeld",
        ),
        "side_ids": (
            "gustavus_adolphus_swedish_saxon_coalition_breitenfeld_1631",
            "tilly_imperial_catholic_league_army_breitenfeld_1631",
        ),
        "side_names": (
            "Gustavus Adolphus's Swedish-Saxon coalition at Breitenfeld (1631)",
            "Tilly's Imperial-Catholic League army at Breitenfeld (1631)",
        ),
        "region": "Saxony",
        "kind": "event_bounded_field_force",
        "confidence": 0.99,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 3,
        "cluster_id": "hced_war_swedish_war",
        "audit_note": "The event-specific Swedish-Saxon and Imperial-League formations own only the first Breitenfeld battle.",
    },
    "hced-Neubrandenburg1631-1": {
        "canonical": _canonical(
            "Siege of Neubrandenburg", 1631, 1631,
            "4-9 March Julian / 14-19 March Gregorian 1631",
            "1631-03-04", "1631-03-19", "source_bounded_dual_calendar_range",
            "single_siege_and_storm_of_neubrandenburg",
        ),
        "side_ids": (
            "tilly_catholic_league_imperial_assault_force_neubrandenburg_1631",
            "kniphausen_swedish_neubrandenburg_garrison_1631",
        ),
        "side_names": (
            "Tilly's Catholic League-Imperial assault force at Neubrandenburg (1631)",
            "Kniphausen's Swedish Neubrandenburg garrison (1631)",
        ),
        "region": "Mecklenburg",
        "kind": "event_bounded_siege_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "The bounded siege, storm, and capture are rated; the subsequent massacre is not treated as another outcome.",
    },
    "hced-Alte Veste1632-1": {
        "canonical": _canonical(
            "Battle of the Alte Veste", 1632, 1632,
            "24 August Julian / 3 September Gregorian through 4 September 1632",
            "1632-08-24", "1632-09-04", "source_bounded_dual_calendar_range",
            "single_battle_and_failed_assaults_at_alte_veste",
        ),
        "side_ids": (
            "wallenstein_imperial_catholic_league_camp_force_alte_veste_1632",
            "gustavus_adolphus_swedish_allied_assault_force_alte_veste_1632",
        ),
        "side_names": (
            "Wallenstein's Imperial-Catholic League camp force at the Alte Veste (1632)",
            "Gustavus Adolphus's Swedish-allied assault force at the Alte Veste (1632)",
        ),
        "region": "Franconia",
        "kind": "event_bounded_field_force",
        "confidence": 0.94,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 3,
        "cluster_id": "hced_war_swedish_war",
        "audit_note": "Failed large-scale assaults and Swedish withdrawal support a bounded defensive victory, not a strategic campaign result.",
    },
    "hced-Boulay1635-1": {
        "canonical": _canonical(
            "Wallerfangen-Boulay rear-guard action", 1635, 1635,
            "26-29 September 1635", "1635-09-26", "1635-09-29",
            "source_bounded_day_range", "single_multiday_rearguard_action_ending_at_boulay",
        ),
        "side_ids": (
            "turenne_fabert_french_weimarian_rearguard_boulay_1635",
            "gallas_imperial_pursuit_vanguard_boulay_1635",
        ),
        "side_names": (
            "Turenne-Fabert French-Weimarian rear guard at Boulay (1635)",
            "Gallas's Imperial pursuit vanguard at Boulay (1635)",
        ),
        "region": "Lorraine and the Saar corridor",
        "kind": "event_bounded_field_force",
        "confidence": 0.88,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "Armed rear-guard fighting stopped the pursuit and enabled withdrawal to Metz; no campaign-level French victory is claimed.",
    },
    "hced-Breisach1638-1": {
        "canonical": _canonical(
            "Siege of Breisach (1638)", 1638, 1638,
            "18 August-17 December 1638", "1638-08-18", "1638-12-17",
            "source_bounded_day_range", "single_formal_siege_blockade_and_capitulation_of_breisach",
        ),
        "side_ids": (
            "bernard_weimarian_french_siege_force_breisach_1638",
            "reinach_imperial_breisach_garrison_1638",
        ),
        "side_names": (
            "Bernard's Weimarian-French siege force at Breisach (1638)",
            "Reinach's Imperial Breisach garrison (1638)",
        ),
        "region": "Upper Rhine",
        "kind": "event_bounded_siege_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "This owns the formal siege, blockade, and capitulation only and excludes separately rated relief battles, including Wittenweier.",
    },
    "hced-Brema1638-1": {
        "canonical": _canonical(
            "Siege of Breme (1638)", 1638, 1638,
            "12/13-26 March 1638", "1638-03-12", "1638-03-26",
            "source_bounded_day_range", "single_siege_and_capture_of_breme",
        ),
        "side_ids": (
            "leganes_aragon_spanish_army_of_lombardy_breme_1638",
            "mongallar_crequy_french_breme_garrison_relief_force_1638",
        ),
        "side_names": (
            "Leganés-Aragón Spanish Army of Lombardy at Breme (1638)",
            "Mongallar-Créquy French Breme garrison and relief force (1638)",
        ),
        "region": "Lombardy",
        "kind": "event_bounded_siege_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "The raw HRE winner is corrected to Leganés's Spanish Army of Lombardy without reversing the source outcome.",
    },
    "hced-Wittenweier1638-1": {
        "canonical": _canonical(
            "Battle of Wittenweier", 1638, 1638,
            "30 July Julian / 9 August Gregorian 1638",
            "1638-07-30", "1638-08-09", "source_stated_dual_calendar_day",
            "single_pitched_relief_battle_at_wittenweier",
        ),
        "side_ids": (
            "bernard_weimarian_french_field_army_wittenweier_1638",
            "goetz_savelli_imperial_bavarian_relief_army_wittenweier_1638",
        ),
        "side_names": (
            "Bernard's Weimarian-French field army at Wittenweier (1638)",
            "Götz-Savelli Imperial-Bavarian relief army at Wittenweier (1638)",
        ),
        "region": "Upper Rhine",
        "kind": "event_bounded_field_force",
        "confidence": 0.97,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "The pitched relief battle remains separate from the surrounding Breisach siege and owns no siege outcome.",
    },
    "hced-Brandeis1639-1": {
        "canonical": _canonical(
            "Battle of Brandeis (1639)", 1639, 1639,
            "29 May 1639", "1639-05-29", "1639-05-29",
            "source_stated_day", "single_field_engagement_near_lobkovice_brandeis",
        ),
        "side_ids": (
            "baner_swedish_field_force_brandeis_1639",
            "hofkirch_imperial_bohemian_field_force_brandeis_1639",
        ),
        "side_names": (
            "Banér's Swedish field force at Brandeis (1639)",
            "Hofkirch's Imperial-Bohemian field force at Brandeis (1639)",
        ),
        "region": "Bohemia",
        "kind": "event_bounded_field_force",
        "confidence": 0.96,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 2,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "The event-specific Imperial-Bohemian force was routed and its commanders captured; no broad HRE actor is created.",
    },
    "hced-Breitenfeld1642-1": {
        "canonical": _canonical(
            "Second Battle of Breitenfeld", 1642, 1642,
            "23 October Julian / 2 November Gregorian 1642",
            "1642-10-23", "1642-11-02", "source_stated_dual_calendar_day",
            "single_pitched_battle_second_breitenfeld",
        ),
        "side_ids": (
            "torstensson_swedish_field_army_breitenfeld_1642",
            "leopold_william_piccolomini_imperial_field_army_breitenfeld_1642",
        ),
        "side_names": (
            "Torstensson's Swedish field army at Breitenfeld (1642)",
            "Leopold William-Piccolomini Imperial field army at Breitenfeld (1642)",
        ),
        "region": "Saxony",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "thirty_years_war",
        "scale_level": 3,
        "cluster_id": "hced_war_thirty_years_war",
        "audit_note": "The second Breitenfeld battle is distinct from 1631 and uses only its event-bounded formations.",
    },
    "hced-Harkany1687-1": {
        "canonical": _canonical(
            "Battle of Harsány (Second Mohács)", 1687, 1687,
            "12 August 1687", "1687-08-12", "1687-08-12",
            "source_stated_day", "single_pitched_battle_at_harsany_second_mohacs",
        ),
        "side_ids": (
            "lorraine_bavarian_habsburg_allied_army_harsany_1687",
            "sari_suleyman_ottoman_field_army_harsany_1687",
        ),
        "side_names": (
            "Lorraine-Bavarian-Habsburg allied army at Harsány (1687)",
            "Sarı Süleyman's Ottoman field army at Harsány (1687)",
        ),
        "region": "Southern Hungary",
        "kind": "event_bounded_field_force",
        "confidence": 0.98,
        "war_type": "interstate_limited",
        "cohort": "great_turkish_war",
        "scale_level": 3,
        "cluster_id": "hced_war_later_turkish_habsburg_wars",
        "audit_note": "The victorious actor is the event-specific Christian allied army rather than a generic imperial polity.",
    },
}


def _entity(
    entity_id: str,
    name: str,
    low: int,
    high: int,
    region: str,
    kind: str,
    source_ids: Iterable[str],
    event_name: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": low,
        "end_year": high,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"Bounded only to {event_name} and its reviewed source interval. "
            "No Holy Roman Empire identity, alias, label rule, predecessor, "
            "successor, or cross-event rating continuity is created."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES: tuple[dict[str, Any], ...] = tuple(
    _entity(
        entity_id,
        spec["side_names"][index],
        int(spec["canonical"]["year_low"]),
        int(spec["canonical"]["year_high"]),
        str(spec["region"]),
        str(spec["kind"]),
        _EVENT_SOURCE_IDS[candidate_id],
        str(spec["canonical"]["name"]),
    )
    for candidate_id, spec in sorted(
        _EVENT_SPECS.items(),
        key=lambda item: (int(item[1]["canonical"]["year_low"]), item[0]),
    )
    for index, entity_id in enumerate(spec["side_ids"])
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES
}


def _contract(candidate_id: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    source_ids = sorted(_EVENT_SOURCE_IDS[candidate_id])
    family_ids = sorted(
        {
            str(_ALL_SOURCE_BY_ID[source_id]["source_family_id"])
            for source_id in source_ids
        }
    )
    return {
        "raw_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES[candidate_id],
        "raw_full_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES[candidate_id],
        "canonical_event": dict(spec["canonical"]),
        "cohort": str(spec["cohort"]),
        "side_1_entity_ids": [str(spec["side_ids"][0])],
        "side_2_entity_ids": [str(spec["side_ids"][1])],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": str(spec["war_type"]),
        "confidence": float(spec["confidence"]),
        "evidence_refs": source_ids,
        "outcome_source_ids": source_ids,
        "outcome_source_family_ids": family_ids,
        "event_evidence_roles": {
            source_id: [
                "actor_identity_boundary",
                "exact_date_or_date_range",
                "tactical_outcome",
            ]
            for source_id in source_ids
        },
        "date_source_ids": source_ids,
        "source_date_refinement": True,
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_event_bounded_opposing_forces",
        "expected_scale_level": int(spec["scale_level"]),
        "expected_cluster_id": str(spec["cluster_id"]),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": str(spec["audit_note"]),
    }


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS: dict[str, dict[str, Any]] = {
    candidate_id: _contract(candidate_id, spec)
    for candidate_id, spec in sorted(_EVENT_SPECS.items())
}
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS = frozenset(
    WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS
)

# Wave 6 correctly quarantined these source rows when its only available choice
# was to flatten the generic "Holy Roman Empire" label into one polity.  This
# lane supersedes that historical disposition only because every row now has a
# separately sourced, event-bounded formation pair.  The orchestrator verifies
# this set against Wave 6's complete unsafe-imperial-collapse inventory.
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS = frozenset(
    {
        "hced-Alte Veste1632-1",
        "hced-Boulay1635-1",
        "hced-Brandeis1639-1",
        "hced-Breisach1638-1",
        "hced-Breitenfeld1631-1",
        "hced-Breitenfeld1642-1",
        "hced-Brema1638-1",
        "hced-Harkany1687-1",
        "hced-Mirischlau1600-1",
        "hced-Neubrandenburg1631-1",
        "hced-Wittenweier1638-1",
    }
)


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Milan1161-1": {
        "raw_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES["hced-Milan1161-1"],
        "raw_full_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES["hced-Milan1161-1"],
        "disposition": "hold_unknown_never_draw",
        "outcome_disposition": "unknown_never_draw",
        "reason_code": "decisive_surrender_and_destruction_are_in_1162_outside_locked_1161_row",
        "unknown_is_never_draw": True,
        "evidence_urls": [
            "https://www.cambridge.org/core/books/conflict-and-violence-in-medieval-italy-5681154/5B05918EC0B043BD2D7E23B62A1D2F60/listing",
            "https://publires.unicatt.it/en/publications/federico-barbarossa-e-la-distruzione-di-milano-nella-storiografia-9/",
        ],
    }
}

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Rakersberg1416-1": {
        "raw_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES["hced-Rakersberg1416-1"],
        "raw_full_row_sha256": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES["hced-Rakersberg1416-1"],
        "disposition": "terminal_exclusion",
        "reason_code": "late_legendary_event_usually_dated_1418_not_source_locked_1416",
        "evidence_urls": [
            "https://www.historischerverein-stmk.at/wp-content/uploads/Z_Jg18_Hans-PIRCHEGGER-Die-ersten-T%C3%BCrkeneinf%C3%A4lle-1396-1415-1418-1.pdf"
        ],
    }
}

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES: dict[
    str, dict[str, Any]
] = {
    "hced-Reutlingen1377-1": {
        "disposition": "existing_owner_duplicate",
        "owner_event_id": "hced_wave8_swabian_hre_hced_reutlingen1377_1",
        "owner_event_full_sha256": "52383f983253ce5ae5a057f330e269b549f814c3039f3b2b1fe5419fe265fa91",
    },
    "hced-Ulm1376-1": {
        "disposition": "existing_owner_duplicate",
        "owner_event_id": "hced_wave8_swabian_hre_hced_ulm1376_1",
        "owner_event_full_sha256": "f4ea269adbc239ba1f3c39e7435a48f67469a57464e548c8c92f012a55b8180f",
    },
    "hced-Zatec1421-1": {
        "disposition": "existing_owner_duplicate",
        "owner_event_id": "hced_wave8_hussites_hced_zatec1421_1",
        "owner_event_full_sha256": "54c41abd25b31f17c61942654e809a473d6bccde799a850d2465ffc70a729829",
    },
}
_EXISTING_OWNER_MAP_DIGEST = "f8a2cc60cc4b18acae54d3395d8c9aa8219e35b9b5375c6b1f7f5c45b47d7f24"

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS = frozenset(
    set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS)
    | set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS)
    | set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS)
    | set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES)
)


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
)
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Boulay1635-1", "hced-Brema1638-1"}
)
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS,
}

_DEFINITE_POINT_MISMATCHES = frozenset(
    {
        "hced-Alte Veste1632-1",
        "hced-Boulay1635-1",
        "hced-Brema1638-1",
        "hced-Harkany1687-1",
        "hced-Rome1167-1",
        "hced-Unstrut1075-1",
    }
)
_UNVERIFIED_BATTLEFIELD_POINTS = frozenset(
    {"hced-Breitenfeld1631-1", "hced-Breitenfeld1642-1"}
)
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": (
            ["withhold_country", "withhold_point"]
            if candidate_id
            in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS
            else ["withhold_point"]
        ),
        "point_reason_code": (
            "reviewed_battle_location_mismatch"
            if candidate_id in _DEFINITE_POINT_MISMATCHES
            else (
                "candidate_keyed_point_not_independently_verified"
                if candidate_id in _UNVERIFIED_BATTLEFIELD_POINTS
                else "settlement_centroid_not_reviewed_combat_footprint"
            )
        ),
        "country_reason_code": (
            "reviewed_modern_jurisdiction_mismatch"
            if candidate_id
            in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS
            else None
        ),
        "evidence_refs": sorted(_EVENT_SOURCE_IDS[candidate_id]),
    }
    for candidate_id in sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS)
}


_WIKIDATA_BATTLE_HASHES: dict[str, str] = {
    "Q10671413": "aab130708d4e857a69c95f4ec696aa1ce65a88765f2aea64dac7802d09831f54",
    "Q108942993": "96dcddb1b14bdc76455b0f8eb94dab224103c5db08487667d98e193b445c7bc1",
    "Q110473264": "11279f4c4a83699204e31b1a6cc456d9a18dd741d6f2a86136dad06328882f3e",
    "Q1138687": "8062369594a79c44fa4db8280d278a6ef9ec400fbeedff9c42788781896bd334",
    "Q1169274": "fa0fae5ae8d86352278c3ebcc1ee1da7a34d1c1ad6442332bb6cb55b17b3ecf8",
    "Q12041939": "ec680306162a82025ceda561ce799d56d90b1092cd7e790a4b6814d328e9e56e",
    "Q1283205": "a70bd70f364ffed9d5ec32dce1306f1873eb7ac29e19ff6570dba5b79263d94c",
    "Q131742771": "b03b750b7b171635f4ca3909e5517ba1e94cf7c41ab56afa3d7c8e2eb4f6d882",
    "Q136753967": "2eb9bac5113cf1449b8596b4a19f234ae94839181b4110282c23dc76c5340e0f",
    "Q1565234": "162dbd43d855db62c2f4cade84673a15e35c28fa4e478196066b81d38a9e4636",
    "Q15727825": "e49446227302080318e40050ca8dc294b8e62ec6aaa7e038c2e809a7f5e17221",
    "Q159512": "1aa558aaef5b29d05d96a84ea2547dfd296ea928b7f14555c321c067ebfdf2a2",
    "Q1754785": "2d1c2c1b47fef7114b21b6bb29251dc93601f2164c89f61f0377a32ee1c5fcac",
    "Q2002331": "f11b5d0c3f74a9290cc8d03b117308ec3e8e38f80c45a6caf89ba49070680e70",
    "Q205379": "119b3ddc603f396fa5e41b5665c1bfee596be2ac249b42c72202ff06ab0cc62b",
    "Q2119849": "76d0746b73bb8b46ac3cc1125a194cf60fbdf246f2a4c830aa1732bf93d25218",
    "Q2226033": "9f9250adea25ffcfaa54aa2fe1899eb445daac73f3f561fe22242f05f4e5b7f5",
    "Q2284174": "7af45b7f557f469f3afe588eea9d0bc3a6ab700a8cb8ae5ce7b012bd3f1773d4",
    "Q312212": "0351b27f2d63cd5433281c06d444d06280e20068b793bc6d162fc6abed2e08b7",
    "Q316604": "befe21834487cf498f4592ca9702ee45b4dfd08f9f17601c99b23480fd821e8d",
    "Q331565": "4098883ecf72848a86ff0bb01b4fb2b687051ad6bd475c23474e37c618d5c497",
    "Q3625431": "93a3c787e88b4eec401f6013d2605148b07763a900fba19af82913ce9eefd523",
    "Q382967": "afc66fc3607c59664ad44958ccb7949e77e0a0dbc59b8153962979083b5f8fa4",
    "Q521285": "8daabb9c87fbef1690e16904e1123a794906055f0772c53c30f3a6313fcb1ddb",
    "Q55633165": "820bb9fc8cc51258dd6d8232b3a37312298e1aeb8d13042cc71b788eecd30074",
    "Q629302": "f3c8e159ccaf2d75208d7a75886d87ba6c364b5b05151a3d738daaf724df01b8",
    "Q690470": "f85a1002c340790a715cb5575c400f88f2cb932562b01226caf4e3e7936e461e",
    "Q722205": "672a298d994ae08169cb6ecd638b156b2dcb21232d8108cb1b9e20ba756f10be",
    "Q77095548": "e2bd882386ecac03b382097624bd56dbcd871ff00e3970414712dadfa32219b8",
}

_WIKIDATA_GENERIC_HASHES: dict[str, str] = {
    "Q1419229": "549e6a9c3d4af8e5aea09bdee896e9b242027f49550c4cb007329454712b99fd",
    "Q1429256": "b8e0b1d69c3a6f2be5ebcfb768a2943f678be0ba460e85151f6c56ec8a992d0d",
    "Q207318": "63f3282541b8532803b30b7daf60aa8a02e78597d5cde434324c6315f7a0d35b",
}

_BRECKE_HASHES: dict[str, str] = {
    "brecke-0101": "70efb04f0c1fa29e3adc7a23f1e1b8ef35b04a2bf99c1089bb13399b25f5304a",
    "brecke-0132": "217cc2b7a3b2af05f3e2e9e3c379336fbf90284fe7e16b6d54c36480b336e2e4",
    "brecke-0605": "e85194e8d4d9af5e8c7fd144ec1791eb5f178b4aca73d267683be5a146cbcafc",
    "brecke-0976": "c6b2da6b2cab156354655678f8a95189366c1c1d7c81492284969b3dead7bc81",
    "brecke-1168": "be1f4791b998b316a5e837dba9fb0c8d64ceb4f03f4a44d8bcda3145bbd848c4",
    "brecke-1184": "9ceeaf90effda35846f33fd1c09e6c4dc24d242c5c87c911659c7f56775ea6b1",
    "brecke-1202": "37b71fd613b30dc2c5e01194fe81e6a9a7ae50c87d9c9d4c907b4f9c142168db",
    "brecke-1328": "c19c2d64f679bd351694e9fce38cb29807988eef99276fd3e99290db470bff07",
    "brecke-1345": "01da0278d02d424ccb300cf4317b99491eeb1b79293a0c15125842576679127a",
    "brecke-1376": "843a74a3010f6d69f82f291179b238ae381b079d2b8f67d3f875a23a7921ae7e",
    "brecke-1385": "25835c0a5b83e25433e61accdc952ca61820953fe0ac32dca90d09fcefaac177",
    "brecke-1412": "bce5bf2c217b781478587e4e2dd5da1e1e7a6d508705747d2fa6590fc4abbc83",
    "brecke-1413": "aa84dd0a31c21fc2562afc663e66d2a11fe8be7b1da6bd359c9b764272705686",
    "brecke-1414": "588d24997a0b8c0d62f8d4d9917c0291433107ebb0552be639e02a00b003cdaf",
    "brecke-1665": "2fafe3953c5ca712742643bf32d3d90586317a1ae6c14bff72da57721937af20",
}

WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES: dict[
    str, dict[str, str]
] = {
    "brecke": _BRECKE_HASHES,
    "iwd": {},
    "iwbd": {},
    "ucdp_actor": {},
    "ucdp_conflict": {},
    "ucdp_dyadic": {},
    "ucdp_termination_conflict": {},
    "ucdp_termination_dyad": {},
    "wikidata_battle": _WIKIDATA_BATTLE_HASHES,
    "wikidata_generic": _WIKIDATA_GENERIC_HASHES,
}

_EMPTY_INVENTORY_DIGEST = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS: dict[
    str, dict[str, Any]
] = {
    "wikidata_battle": {
        "relative_path": "data/review/wikidata-battle-candidates.jsonl",
        "rows": 18954,
        "sha256": "5f67b193c58fe06947f965283c534d53a43d8ad8644a15995af39c6d6f55f22b",
        "id_field": "candidate_id",
        "inventory_id_digest": "aebd19d9c29b73fe2f70565a5570771f53d128d9e16e89ad7b80a4418541f71c",
        "inventory_map_digest": "c42227c8a7d05920ac3aa78015d460521ccb7d5678ae510fae55fedfd004f20f",
        "disposition": "winnerless_discovery_only_unknown_never_draw",
    },
    "wikidata_generic": {
        "relative_path": "data/review/wikidata-candidates.jsonl",
        "rows": 18,
        "sha256": "9a57ed9dbf4e2c59ea6185c699f00bbea6d07f5c90d5356ce501da449e8d0dd4",
        "id_field": "candidate_id",
        "inventory_id_digest": "0358bb15e47826c6c39a396cc0297acc7712c96c07eecd90b61f9fbb7fedbdcc",
        "inventory_map_digest": "5773dc135b8a01ebefd856a7ec16f77c10779303d36100975bddb2877fe54e2c",
        "disposition": "winnerless_discovery_only_unknown_never_draw",
    },
    "brecke": {
        "relative_path": "data/reference/brecke-wars.jsonl",
        "rows": 3708,
        "sha256": "1868097be6c9015715b4dd210d5168e3a961bf8870f6081396fabae319c269dc",
        "id_field": "brecke_id",
        "inventory_id_digest": "983ba64a07bcfe02bbf324f64b6edc58548e9e115f72676a9413da094af932e5",
        "inventory_map_digest": "9d63120f094617810438893b8bff94a58c7e5e9b1cf037401d78f239e744d564",
        "disposition": "broad_war_coverage_only_no_outcome",
    },
    "iwd": {
        "relative_path": "data/review/iwd-1.21-candidates.jsonl", "rows": 265,
        "sha256": "0867947dadfb29e93a4697efa308fcf1acd78f90c90f8d860d344ac12dd883fd",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1823_2003",
    },
    "iwbd": {
        "relative_path": "data/review/iwbd-candidates.jsonl", "rows": 1708,
        "sha256": "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1823_2003",
    },
    "ucdp_conflict": {
        "relative_path": "data/review/ucdp-conflict-26.1-candidates.jsonl", "rows": 2816,
        "sha256": "cbc28e8d06b5fdd83b688ca0be45695e2d2d3bcc59b486d8f92522593ba619ee",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1946_2025",
    },
    "ucdp_dyadic": {
        "relative_path": "data/review/ucdp-dyadic-26.1-candidates.jsonl", "rows": 3518,
        "sha256": "c6e6f7deda305d38e78c987713817410ba3c4045904e22e86e12389fb4a622e4",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1946_2025",
    },
    "ucdp_termination_conflict": {
        "relative_path": "data/review/ucdp-termination-conflict-candidates.jsonl", "rows": 2752,
        "sha256": "4ce351ab0b0654b341ca8aba42ba82bd5a1955e7c6900351d0f179aae02a3219",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1946_2024",
    },
    "ucdp_termination_dyad": {
        "relative_path": "data/review/ucdp-termination-dyad-candidates.jsonl", "rows": 3432,
        "sha256": "49c8bead50aa966ee0c70ac023eca9dd81060668db180c1dcfd116c0e827218d",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "empty_temporal_inventory_1946_2024",
    },
    "ucdp_actor": {
        "relative_path": "data/review/ucdp-actor-26.1-candidates.jsonl", "rows": 1987,
        "sha256": "3cc79938ebac46e1edd99d6116e50610b5753875c023b69128343be816c94788",
        "id_field": "candidate_id", "inventory_id_digest": _EMPTY_INVENTORY_DIGEST,
        "inventory_map_digest": _EMPTY_INVENTORY_DIGEST, "disposition": "actor_only_no_event_outcome_inventory",
    },
}


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS,
        "contracts": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS,
        "discovery_inventories": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES,
        "discovery_snapshot_locks": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS,
        "entities": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES,
        "existing_owner_duplicates": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES,
        "full_row_hashes": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES,
        "holds": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS,
        "location_reasons": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_REASONS,
        "reused_sources": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES,
        "row_hashes": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES,
        "sources": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES,
        "terminal_exclusions": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS,
        "wave6_superseded_exclusion_ids": sorted(
            WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
        ),
    }


def wave8_holy_roman_empire_exact_audit_signature() -> str:
    return _sha256_json(_signature_payload())


WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FINAL_AUDIT_SIGNATURE = (
    "740c954b41184a9a774bb70a69e3d74fc361631ae5731f9ddf39428ffd16155a"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    partitions = (
        set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS),
        set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
        set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS),
        set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES),
    )
    if [len(part) for part in partitions] != [18, 1, 1, 3]:
        raise ValueError(f"{_LANE_NAME} disposition count drift")
    for index, left in enumerate(partitions):
        for right in partitions[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} disposition overlap")
    if (
        set().union(*partitions) != set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES)
        or set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES)
        != set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES)
        or WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS != set().union(*partitions)
    ):
        raise ValueError(f"{_LANE_NAME} exact inventory drift")
    if (
        len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS) != 11
        or not WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
        <= WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} Wave 6 supersession inventory drift")
    if (
        _sha256_json(sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES))
        != _EXACT_ID_DIGEST
        or _sha256_json(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES)
        != _EXACT_CANONICAL_MAP_DIGEST
        or _sha256_json(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES)
        != _EXACT_FULL_MAP_DIGEST
    ):
        raise ValueError(f"{_LANE_NAME} exact digest drift")
    if (
        set(_ADJACENT_ROW_HASHES) != set(_ADJACENT_FULL_ROW_HASHES)
        or set(_ADJACENT_ROW_HASHES) & WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS
        or _sha256_json(sorted(_ADJACENT_ROW_HASHES)) != _ADJACENT_ID_DIGEST
        or _sha256_json(_ADJACENT_ROW_HASHES) != _ADJACENT_CANONICAL_MAP_DIGEST
        or _sha256_json(_ADJACENT_FULL_ROW_HASHES) != _ADJACENT_FULL_MAP_DIGEST
    ):
        raise ValueError(f"{_LANE_NAME} adjacent inventory drift")

    if len(_NEW_SOURCE_BY_ID) != 26 or len(_REUSED_SOURCE_BY_ID) != 1:
        raise ValueError(f"{_LANE_NAME} source count drift")
    if set(_NEW_SOURCE_BY_ID) & set(_REUSED_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} new/reused source overlap")
    for source_id, source in _ALL_SOURCE_BY_ID.items():
        if (
            not source.get("source_family_id")
            or "outcome" not in source.get("evidence_roles", [])
            or not _is_sorted_unique(source.get("evidence_roles", []))
        ):
            raise ValueError(f"{_LANE_NAME} invalid outcome source: {source_id}")

    if len(_ENTITY_BY_ID) != 36 or len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES) != 36:
        raise ValueError(f"{_LANE_NAME} event formation count drift")
    consumed_entities: set[str] = set()
    consumed_sources: set[str] = set()
    for candidate_id, contract in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["source_date_override"]
            or contract["outcome_reversal"]
            or contract["actor_override"]
            != "candidate_keyed_event_bounded_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} outcome contract drift: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if len(sides[0]) != 1 or len(sides[1]) != 1 or set(sides[0]) & set(sides[1]):
            raise ValueError(f"{_LANE_NAME} actor side drift: {candidate_id}")
        canonical = contract["canonical_event"]
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        if (
            canonical["canonical_key"]
            != f"{_slug(str(canonical['name']))}:{low}:{high}"
            or not canonical["start_date"]
            or not canonical["end_date"]
            or not canonical["date_text"]
            or contract["war_type"]
            not in {"civil_war", "interstate_limited"}
        ):
            raise ValueError(f"{_LANE_NAME} canonical boundary drift: {candidate_id}")
        for entity_id in (*sides[0], *sides[1]):
            entity = _ENTITY_BY_ID.get(entity_id)
            if entity is None:
                raise ValueError(f"{_LANE_NAME} missing formation: {entity_id}")
            if (
                entity["aliases"]
                or entity["predecessors"]
                or (int(entity["start_year"]), int(entity["end_year"]))
                != (low, high)
                or normalize_label(entity["id"]) == _EXACT_LABEL
                or normalize_label(entity["name"]) == _EXACT_LABEL
            ):
                raise ValueError(f"{_LANE_NAME} formation continuity drift: {entity_id}")
            consumed_entities.add(entity_id)
        source_ids = list(map(str, contract["outcome_source_ids"]))
        family_ids = list(map(str, contract["outcome_source_family_ids"]))
        if (
            source_ids != sorted(set(source_ids))
            or family_ids != sorted(set(family_ids))
            or len(family_ids) < 2
            or set(family_ids) & _FORBIDDEN_OUTCOME_FAMILIES
            or set(source_ids) != set(contract["evidence_refs"])
            or set(source_ids) != set(contract["date_source_ids"])
            or set(source_ids) != set(contract["event_evidence_roles"])
        ):
            raise ValueError(f"{_LANE_NAME} evidence independence drift: {candidate_id}")
        expected_families = sorted(
            {
                str(_ALL_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in source_ids
            }
        )
        if family_ids != expected_families:
            raise ValueError(f"{_LANE_NAME} source family closure drift: {candidate_id}")
        consumed_sources.update(source_ids)
    if consumed_entities != set(_ENTITY_BY_ID):
        raise ValueError(f"{_LANE_NAME} unused or missing formation")
    if consumed_sources != set(_ALL_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} unused or missing source")

    if (
        WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS
        != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
        or WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS
        != {"hced-Boulay1635-1", "hced-Brema1638-1"}
        or set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_LOCATION_QUARANTINE_REASONS)
        != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location quarantine drift")

    for dataset, inventory in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.items():
        lock = WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS[dataset]
        map_digest = (
            _sha256_json(inventory) if inventory else _EMPTY_INVENTORY_DIGEST
        )
        if (
            _sha256_json(sorted(inventory)) != lock["inventory_id_digest"]
            or map_digest != lock["inventory_map_digest"]
        ):
            raise ValueError(f"{_LANE_NAME} discovery inventory digest drift: {dataset}")
    if set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS) != set(
        WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES
    ):
        raise ValueError(f"{_LANE_NAME} discovery dataset inventory drift")
    if wave8_holy_roman_empire_exact_audit_signature() != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_holy_roman_empire_exact_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in exact:
        exact_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    if set(exact_by_id) != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    for candidate_id in sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS):
        rows = exact_by_id[candidate_id]
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} duplicate exact row: {candidate_id}")
        row = rows[0]
        if (
            canonical_hced_row_sha256(row)
            != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ROW_HASHES[candidate_id]
            or _full_row_sha256(row)
            != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FULL_ROW_HASHES[candidate_id]
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
        ):
            raise ValueError(f"{_LANE_NAME} exact row drift: {candidate_id}")

    all_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        all_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, disposition in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS.items():
        rows = all_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} adjacent row missing or duplicated: {candidate_id}")
        row = rows[0]
        if (
            canonical_hced_row_sha256(row) != disposition["canonical_row_sha256"]
            or _full_row_sha256(row) != disposition["full_row_sha256"]
        ):
            raise ValueError(f"{_LANE_NAME} adjacent row drift: {candidate_id}")
    return {
        "adjacent_coverage_only_rows": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS),
        "exact_label_rows": len(exact),
        "existing_owner_duplicates": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES),
        "holds": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
        "promotion_contracts": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS),
        "reviewed_hced_rows": len(exact) + len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS),
        "terminal_exclusions": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_holy_roman_empire_exact_cross_dataset_inventories(
    rows_by_dataset: Mapping[str, list[dict[str, Any]]],
    snapshot_sha256_by_dataset: Mapping[str, str],
    release_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    if set(rows_by_dataset) != set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS):
        raise ValueError(f"{_LANE_NAME} discovery dataset keys changed")
    if set(snapshot_sha256_by_dataset) != set(rows_by_dataset):
        raise ValueError(f"{_LANE_NAME} discovery snapshot hash keys changed")
    inventory_rows = 0
    unknown_rows = 0
    broad_war_rows = 0
    for dataset, lock in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_SNAPSHOT_LOCKS.items():
        rows = rows_by_dataset[dataset]
        if len(rows) != int(lock["rows"]):
            raise ValueError(f"{_LANE_NAME} {dataset} row count changed")
        if snapshot_sha256_by_dataset[dataset] != lock["sha256"]:
            raise ValueError(f"{_LANE_NAME} {dataset} snapshot hash changed")
        id_field = str(lock["id_field"])
        indexed: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            indexed.setdefault(str(row.get(id_field)), []).append(row)
        inventory = WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES[dataset]
        for candidate_id, expected_hash in inventory.items():
            matches = indexed.get(candidate_id, [])
            if len(matches) != 1 or _full_row_sha256(matches[0]) != expected_hash:
                raise ValueError(f"{_LANE_NAME} {dataset} inventory drift: {candidate_id}")
            row = matches[0]
            if dataset.startswith("wikidata"):
                if row.get("do_not_rate_automatically") is not True or row.get("winners") != []:
                    raise ValueError(f"{_LANE_NAME} winnerless discovery guard drift: {candidate_id}")
                unknown_rows += 1
            elif dataset == "brecke":
                if row.get("outcome_available") is not False or row.get("rating_use") != "coverage_cross_check_only":
                    raise ValueError(f"{_LANE_NAME} Brecke nonrating guard drift: {candidate_id}")
                broad_war_rows += 1
        inventory_rows += len(inventory)
    discovery_ids = frozenset().union(
        *(
            frozenset(inventory)
            for inventory in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.values()
        )
    )
    leaked_events = []
    for event in release_events:
        matched = sorted(discovery_ids & set(_string_values(event)))
        if matched:
            leaked_events.append(
                {
                    "event_id": str(event.get("id")),
                    "discovery_candidate_ids": matched,
                }
            )
    if leaked_events:
        raise ValueError(
            f"{_LANE_NAME} discovery-only row entered the rating ledger: "
            f"{leaked_events}"
        )
    return {
        "broad_war_coverage_only_rows": broad_war_rows,
        "cross_dataset_inventory_rows": inventory_rows,
        "discovery_promotions": len(leaked_events),
        "empty_dataset_inventories": sum(
            not inventory
            for inventory in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.values()
        ),
        "unknown_never_draw_rows": unknown_rows,
    }


def _validate_existing_owners(
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    events = list(existing_events)
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        candidate_id = event.get("hced_candidate_id")
        if candidate_id in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES:
            by_candidate.setdefault(str(candidate_id), []).append(event)
    owner_hashes: dict[str, str] = {}
    for candidate_id, disposition in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES.items():
        owned = by_candidate.get(candidate_id, [])
        if len(owned) != 1:
            raise ValueError(f"{_LANE_NAME} existing owner missing or duplicated: {candidate_id}")
        event = owned[0]
        event_hash = _full_row_sha256(event)
        if (
            event.get("id") != disposition["owner_event_id"]
            or event_hash != disposition["owner_event_full_sha256"]
            or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
        ):
            raise ValueError(f"{_LANE_NAME} existing owner drift: {candidate_id}")
        owner_hashes[candidate_id] = event_hash
    if _sha256_json(owner_hashes) != _EXISTING_OWNER_MAP_DIGEST:
        raise ValueError(f"{_LANE_NAME} existing owner map digest drift")
    return {"existing_owner_duplicates": len(owner_hashes)}


def validate_wave8_holy_roman_empire_exact_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    queue_counts = validate_wave8_holy_roman_empire_exact_queue_contracts(hced_rows)
    events = list(existing_events)
    owner_counts = _validate_existing_owners(events)
    forbidden_nonrating_ids = (
        set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS)
        | set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS)
        | set(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS)
    )
    leaked = sorted(
        str(event.get("id"))
        for event in events
        if event.get("hced_candidate_id") in forbidden_nonrating_ids
    )
    if leaked:
        raise ValueError(f"{_LANE_NAME} nonrating disposition emitted: {leaked}")
    return {
        **queue_counts,
        **owner_counts,
        "nonrating_lane_emissions": 0,
    }


def install_wave8_holy_roman_empire_exact_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_holy_roman_empire_exact_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    for source_id, expected in _REUSED_SOURCE_BY_ID.items():
        if sources_by_id.get(source_id) != expected:
            raise ValueError(f"{_LANE_NAME} reused source missing or changed: {source_id}")
    install_exact_sources(
        sources_by_id,
        WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_holy_roman_empire_exact_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    existing = list(existing_events)
    validate_wave8_holy_roman_empire_exact_integration_dispositions(
        hced_rows, existing
    )
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing,
        WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    if {str(event["hced_candidate_id"]) for event in events} != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} emitted candidate inventory drift")
    return events


def validate_wave8_holy_roman_empire_exact_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    _validate_static()
    events = list(release_events)
    _validate_existing_owners(events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_by_id = {
        str(entity.get("id")): entity
        for entity in release_entities
        if str(entity.get("id")) in _ENTITY_BY_ID
    }
    all_sources = {str(source.get("id")): source for source in release_sources}
    source_by_id = {
        source_id: all_sources[source_id]
        for source_id in _NEW_SOURCE_BY_ID
        if source_id in all_sources
    }
    for source_id, expected in _REUSED_SOURCE_BY_ID.items():
        if all_sources.get(source_id) != expected:
            raise ValueError(f"{_LANE_NAME} reused source artifact drift: {source_id}")
    complete_counts = (18, 36, 26)
    actual_counts = (len(owned), len(entity_by_id), len(source_by_id))
    if actual_counts not in {(0, 0, 0), complete_counts}:
        raise ValueError(f"{_LANE_NAME} current artifacts are partial: {actual_counts}")
    if actual_counts == (0, 0, 0):
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_new_sources": 0,
            "promoted_events": 0,
            "reused_sources": 1,
        }
    if entity_by_id != _ENTITY_BY_ID or source_by_id != _NEW_SOURCE_BY_ID:
        raise ValueError(f"{_LANE_NAME} current entity/source artifact drift")
    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS or len(owned) != len(by_candidate):
        raise ValueError(f"{_LANE_NAME} current event inventory drift")
    for candidate_id, contract in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("event_type") != "engagement"
            or event.get("war_type") != contract["war_type"]
            or event.get("cluster_id") != contract["expected_cluster_id"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids") != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0)) != float(contract["confidence"])
        ):
            raise ValueError(f"{_LANE_NAME} current event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            side_1,
            side_2,
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(f"{_LANE_NAME} participant drift: {candidate_id}")
        if "geometry" in event:
            raise ValueError(f"{_LANE_NAME} quarantined point leaked: {candidate_id}")
        if candidate_id in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
            if "modern_location_country" in event or "location_provenance" in event:
                raise ValueError(f"{_LANE_NAME} quarantined country leaked: {candidate_id}")
        elif "modern_location_country" not in event or "location_provenance" not in event:
            raise ValueError(f"{_LANE_NAME} retained country drift: {candidate_id}")
    return {
        "artifact_state": "integrated",
        "installed_entities": 36,
        "installed_new_sources": 26,
        "promoted_events": 18,
        "reused_sources": 1,
    }


def wave8_holy_roman_empire_exact_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS.values()
            ).items()
        )
    )


def wave8_holy_roman_empire_exact_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_coverage_only_rows": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS),
        "country_quarantine_additions": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_COUNTRY_QUARANTINE_ADDITIONS),
        "cross_dataset_inventory_rows": sum(map(len, WAVE8_HOLY_ROMAN_EMPIRE_EXACT_DISCOVERY_INVENTORIES.values())),
        "existing_owner_duplicates": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES),
        "holds": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
        "new_entities": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ENTITIES),
        "new_sources": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_SOURCES),
        "newly_rated_events": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_POINT_QUARANTINE_ADDITIONS),
        "reviewed_exact_hced_rows": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS),
        "reviewed_hced_rows": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_RESERVED_IDS) + len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_ADJACENT_HCED_DISPOSITIONS),
        "reused_sources": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_REUSED_SOURCES),
        "terminal_exclusions": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS),
        "unknown_holds": len(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
        "wave6_superseded_exclusions": len(
            WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
        ),
    }


def wave8_holy_roman_empire_exact_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_holy_roman_empire_exact_counts(),
        "cohorts": wave8_holy_roman_empire_exact_cohort_counts(),
        "existing_owner_duplicates": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_HOLY_ROMAN_EMPIRE_EXACT_EXISTING_OWNER_DUPLICATES.items()
            )
        ],
        "final_audit_signature": WAVE8_HOLY_ROMAN_EMPIRE_EXACT_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_HOLDS),
        "promoted_candidate_ids": sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_CONTRACT_IDS),
        "terminal_exclusion_candidate_ids": sorted(WAVE8_HOLY_ROMAN_EMPIRE_EXACT_TERMINAL_EXCLUSIONS),
        "wave6_superseded_exclusion_candidate_ids": sorted(
            WAVE8_HOLY_ROMAN_EMPIRE_EXACT_WAVE6_SUPERSEDED_EXCLUSION_IDS
        ),
    }


_validate_static()
