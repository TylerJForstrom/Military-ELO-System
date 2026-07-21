from __future__ import annotations

"""Curated identity, exclusion, and rejection policies for release promotion."""

from typing import Any

# Shared era-window sequences for the Habsburg and English identity chains.
# Habsburg windows start 1556: until Charles V's abdications the dynasty's
# Danubian and Spanish-Imperial branches shared the "Habsburg" label in the
# sources, so 1526-1555 rows stay staged. England windows gap 1649-1660: the
# Commonwealth and Protectorate are conventionally a distinct republic, so
# Interregnum rows stay staged pending a curated Commonwealth identity.
_HABSBURG_WINDOWS: tuple[tuple[int, int, str], ...] = (
    (1556, 1803, "habsburg_monarchy"),
    (1804, 1866, "austrian_empire"),
    (1867, 1918, "austria_hungary"),
)


_ENGLAND_WINDOWS: tuple[tuple[int, int, str], ...] = (
    (927, 1648, "kingdom_england"),
    (1661, 1706, "kingdom_england"),
)


# The 16 December 1815 elevation of Brazil created a new pluricontinental
# sovereign polity; its September 1822 dissolution therefore resets the
# restored Portuguese kingdom instead of carrying the earlier kingdom's rating
# through the union. Year-only 1815, 1822, and 1910 rows stay unresolved because
# each transition occurred within the year. Exact candidate contracts may bind
# an independently dated action on the correct side of a boundary.
_PORTUGAL_WINDOWS: tuple[tuple[int, int, str], ...] = (
    (1147, 1814, "kingdom_portugal"),
    (1816, 1821, "united_kingdom_portugal_brazil_algarves"),
    (1823, 1909, "kingdom_portugal_restored"),
    (1911, 1925, "portuguese_first_republic"),
)


SEED_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "ir_achaemenid_emp": ((-550, -330, "achaemenid_empire"),),
    "ir_archaemenid_emp": ((-550, -330, "achaemenid_empire"),),
    "tn_carthage_emp": ((-650, -146, "carthage"),),
    "it_roman_rep_1": ((-509, -27, "roman_republic"),),
    "it_roman_rep_2": ((-509, -27, "roman_republic"),),
    "it_roman_rep_3": ((-509, -27, "roman_republic"),),
    "it_roman_principate": ((-27, 286, "roman_empire"),),
    "it_roman_dominate": ((287, 394, "roman_empire"),),
    "tr_roman_dominate": ((287, 394, "roman_empire"),),
    "tr_east_roman_emp": ((395, 625, "byzantine_empire"),),
    "tr_byzantine_emp_1": ((395, 1453, "byzantine_empire"),),
    "tr_byzantine_emp_2": ((395, 1453, "byzantine_empire"),),
    "tr_byzantine_emp_3": ((395, 1453, "byzantine_empire"),),
    "ir_sassanian_emp_1": ((224, 651, "sasanian_empire"),),
    "ir_sassanian_emp_2": ((224, 651, "sasanian_empire"),),
    "sy_umayyad_cal": ((661, 750, "umayyad_caliphate"),),
    "fr_carolingian_emp_1": ((481, 843, "frankish_kingdom"),),
    "fr_carolingian_emp_2": ((481, 843, "frankish_kingdom"),),
    "gr_macedonian_emp": ((-336, -323, "macedonian_empire"),),
    "mn_mongol_emp": ((1206, 1294, "mongol_empire"),),
    "eg_mamluk_sultanate_1": ((1250, 1517, "mamluk_sultanate"),),
    "eg_mamluk_sultanate_3": ((1250, 1517, "mamluk_sultanate"),),
    "tr_ottoman_emp_1": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_2": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_3": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_4": ((1299, 1922, "ottoman_empire"),),
    "ir_safavid_emp": ((1501, 1736, "safavid_empire"),),
    "in_mughal_emp": ((1526, 1857, "mughal_empire"),),
    "es_spanish_emp_1": ((1479, 1898, "spanish_empire"),),
    "es_spanish_emp_2": ((1479, 1898, "spanish_empire"),),
    "es_spanish_emp_3": ((1479, 1898, "spanish_empire"),),
    "fr_valois_k_1": ((987, 1792, "kingdom_france"),),
    "fr_valois_k_2": ((987, 1792, "kingdom_france"),),
    "fr_bourbon_k_1": ((987, 1792, "kingdom_france"),),
    "fr_bourbon_k_2": (
        (987, 1792, "kingdom_france"),
        (1793, 1803, "french_first_republic"),
        (1804, 1815, "first_french_empire"),
    ),
    "gb_british_emp_1": (*_ENGLAND_WINDOWS, (1707, 2026, "united_kingdom")),
    "gb_british_emp_2": ((1707, 2026, "united_kingdom"),),
    # Cliopatria's first Romanov-series code also covers the preceding
    # Tsardom.  Split it at Peter I's 1721 imperial proclamation so the two
    # conventionally distinct polities never share a rating.
    "ru_romanov_dyn_1": (
        (1547, 1720, "clio_ru_moskva_rurik_dyn_1547_93deb0e2"),
        (1721, 1917, "russian_empire"),
    ),
    "ru_romanov_dyn_2": ((1721, 1917, "russian_empire"),),
    "de_german_reich_2": ((1871, 1918, "german_empire"),),
    "de_third_reich": ((1933, 1945, "nazi_germany"),),
    "jp_japanese_emp": ((1868, 1947, "empire_japan"),),
    "ru_soviet_union": ((1922, 1991, "soviet_union"),),
    "us_antebellum": ((1776, 2026, "united_states"),),
    "us_united_states_of_america_reconstruction": ((1776, 2026, "united_states"),),
    "us_united_states_contemporary": ((1776, 2026, "united_states"),),
    "us_united_states_of_america_contemporary": ((1776, 2026, "united_states"),),
    "vt_vietnam_democratic_rep": ((1945, 1976, "north_vietnam"),),
    "vt_vietnam_rep": ((1955, 1975, "south_vietnam"),),
    "cn_chinese_peoples_rep": ((1949, 2026, "peoples_republic_china"),),
    # ---- M4 curated state identities (second reviewer pending) ----
    # Codes with no Cliopatria owner or never-unique owners, plus two
    # enumerated identity supersessions (br_brazil_emp, ir_qajar_dyn).
    # fr_france_napoleonic ends 1869: 1870 is undecidable between the Second
    # Empire and the Third Republic at year precision and stays staged.
    "af_afghanistan_emirate": ((1823, 1926, "emirate_afghanistan"),),
    "af_durrani_emp": ((1747, 1822, "durrani_empire"),),
    # The Seshat code spans the Confederation, post-Pavon republic, and modern
    # series.  Overlapping transition years deliberately fail closed.
    "ar_argentina_rep_1": (
        (1831, 1861, "argentine_confederation"),
        (1861, 1930, "argentine_republic_1861"),
        (1930, 2026, "clio_q414_1930_5e281b3e"),
    ),
    "at_habsburg_1": _HABSBURG_WINDOWS,
    "at_habsburg_2": _HABSBURG_WINDOWS,
    "au_austro_hungarian_emp": ((1867, 1918, "austria_hungary"),),
    "au_habsburg_1": _HABSBURG_WINDOWS,
    "au_habsburg_2": _HABSBURG_WINDOWS,
    "au_habsburg_3": _HABSBURG_WINDOWS,
    "br_brazil_emp": ((1822, 1889, "empire_brazil"),),
    "dk_danish_emp_modern": ((1523, 2026, "kingdom_denmark"),),
    "dk_danish_k_modern": ((1523, 2026, "kingdom_denmark"),),
    "eg_egypt_modern_1": ((1805, 1882, "egypt_muhammad_ali"),),
    "et_ethiopian_k": ((1855, 1936, "ethiopian_empire"),),
    "fr_france_modern_1": ((1871, 1940, "french_third_republic"),),
    "fr_france_napoleonic": ((1852, 1869, "second_french_empire"),),
    "gb_england_plantagenet": _ENGLAND_WINDOWS,
    "gb_england_tudor_and_early_stuart": _ENGLAND_WINDOWS,
    "gb_scotland_k": ((843, 1706, "kingdom_scotland"),),
    "hu_arpad_dyn": ((1000, 1526, "kingdom_hungary"),),
    "hu_hungary_k": ((1000, 1526, "kingdom_hungary"),),
    "hu_later_dyn": ((1000, 1526, "kingdom_hungary"),),
    "in_maratha_emp": ((1674, 1818, "maratha_confederacy"),),
    "in_mysore_k": ((1572, 1799, "kingdom_mysore"),),
    "ir_qajar_dyn": ((1794, 1925, "qajar_iran"),),
    "it_venetian_rep_3": ((697, 1797, "republic_venice"),),
    "it_venetian_rep_4": ((697, 1797, "republic_venice"),),
    "kr_joseon": ((1392, 1897, "joseon"),),
    # HCED's Texas-revolution rows code the opposing republic with this
    # Seshat identifier.  Bind only the already-curated Mexican Republic
    # interval; the First and Second Empires remain outside the window.
    "mx_mexico_1": (
        (1824, 1863, "mexican_republic"),
        (1868, 2024, "clio_mx_mexico_1_1868_ffbcfbae"),
    ),
    "pl_poland_lithuania_commonwealth": ((1569, 1795, "polish_lithuanian_commonwealth"),),
    "pl_poland_lithuania_k": ((1569, 1795, "polish_lithuanian_commonwealth"),),
    "pl_polish_rep_1": ((1918, 1939, "second_polish_republic"),),
    "rs_serbia_k": ((1882, 1918, "kingdom_serbia"),),
    # Syria's union with Egypt is a distinct command identity. The two
    # republic series therefore remain separate and 1958-1961 is absent.
    "sy_syria_modern": (
        (1946, 1957, "clio_sy_syria_modern_1946_86597c89"),
        (1962, 2026, "clio_q41137_1973_b05dea50"),
    ),
    "sv_sweden_k_modern": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k_1": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k_2": ((1523, 2026, "kingdom_sweden"),),
    "pt_portuguese_emp_1": _PORTUGAL_WINDOWS,
    "pt_portuguese_emp_2": _PORTUGAL_WINDOWS,
}


# Explicit, time-bounded identity policy for IWD/COW country codes whose source
# label does not name the historical polity directly. COW code 365 labels both
# the Russian Empire and the Soviet Union as "Russia"; the 1918-1921
# revolutionary era is deliberately absent so wars from that period stay staged
# instead of being attached to either neighboring identity.
IWD_COW_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "365": (
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
    # COW 255 pre-1871 is Prussia (both Schleswig wars were fought under
    # Prussian command); COW 300's "Austria-Hungary" label predates the Dual
    # Monarchy for 1804-1866 records; COW 345's "Yugoslavia" label denotes
    # the Kingdom of Serbia for 1882-1918 records. Deliberate absences: 255
    # post-1918, 300 pre-1804, 345 outside 1882-1918.
    "255": ((1701, 1870, "kingdom_prussia"), (1871, 1918, "german_empire")),
    "300": ((1804, 1866, "austrian_empire"), (1867, 1918, "austria_hungary")),
    "345": ((1882, 1918, "kingdom_serbia"),),
    # Curated Wave 4 identities. The 2026 endpoint is the policy-table
    # representation of an open/current seed identity (whose end_year is null).
    "100": ((1863, 1885, "united_states_colombia"),),
    "670": ((1932, 2026, "kingdom_saudi_arabia"),),
    "678": ((1918, 1961, "mutawakkilite_kingdom_yemen"),),
    # Crisp-state tranche. Transition years intentionally overlap adjacent
    # identities and therefore resolve to no unique target.
    "160": (
        (1831, 1861, "argentine_confederation"),
        (1861, 1930, "argentine_republic_1861"),
        (1930, 2026, "clio_q414_1930_5e281b3e"),
    ),
    "355": (
        (1878, 1908, "principality_bulgaria"),
        (1908, 1946, "kingdom_bulgaria"),
    ),
    "652": (
        (1946, 1957, "clio_sy_syria_modern_1946_86597c89"),
        (1962, 2026, "clio_q41137_1973_b05dea50"),
    ),
}


def _iwd_component_contract(
    source_component_id: str,
    parent_war_name: str,
    name: str,
    start_year: int,
    end_year: int,
    initiators: tuple[tuple[str, str], ...],
    targets: tuple[tuple[str, str], ...],
    terminal_outcome_code: str,
    terminal_outcome: str,
    source_rows: tuple[str, ...],
    *,
    allies: tuple[tuple[str, str], ...] = (),
    adversaries: tuple[tuple[str, str], ...] = (),
    joiner_decision: bool = False,
) -> dict[str, Any]:
    return {
        "source_component_id": source_component_id,
        "parent_war_name": parent_war_name,
        "name": name,
        "start_year": str(start_year),
        "end_year": str(end_year),
        "initiators": initiators,
        "targets": targets,
        "allies": allies,
        "adversaries": adversaries,
        "terminal_outcome_code": terminal_outcome_code,
        "terminal_outcome": terminal_outcome,
        "joiner_decision": str(joiner_decision).lower(),
        "source_rows": source_rows,
    }


# Parent-keyed contracts for rows whose source labels cross disputed or
# transitional identity boundaries. They do not create a generic COW fallback:
# once one reviewed parent is present, its complete component set, source
# semantics, party codes, and exact target IDs must all remain unchanged.
IWD_REVIEWED_PARENT_CONTRACTS: dict[str, dict[str, Any]] = {
    "1": {
        "components": {
            "iwd-1": _iwd_component_contract(
                "1", "Franco-Spanish1823", "Franco-Spanish1823", 1823, 1823,
                (("220", "France"),), (("230", "Spain"),),
                "1", "initiator_victory", ("2",),
            ),
        },
        "party_bindings": {
            "220": "bourbon_restoration_france",
            "230": "spanish_empire",
        },
    },
    "10": {
        "components": {
            "iwd-17": _iwd_component_contract(
                "17", "ItalianUnification1859", "ItalianUnification_France_1859",
                1859, 1859, (("220", "France"),), (("300", "Austria-Hungary"),),
                "1", "initiator_victory", ("32",),
                allies=(("325", "Italy"),),
                joiner_decision=True,
            ),
            "iwd-18": _iwd_component_contract(
                "18", "ItalianUnification1859", "ItalianUnification_Austria_1859",
                1859, 1859, (("300", "Austria-Hungary"),), (("325", "Italy"),),
                "2", "initiator_defeat", ("33",),
                adversaries=(("220", "France"),),
            ),
        },
        "party_bindings": {
            "220": "second_french_empire",
            "300": "austrian_empire",
            "325": "kingdom_sardinia_piedmont",
        },
    },
    "39": {
        "components": {
            "iwd-88": _iwd_component_contract(
                "88", "EstonianWar1918-1920", "EstonianWar_Russia_1918-1920",
                1918, 1920, (("365", "Russia"),), (("366", "Estonia"),),
                "2", "initiator_defeat", ("173", "174", "175"),
                adversaries=(
                    ("375", "Finland"),
                    ("220", "France"),
                    ("200", "United Kingdom"),
                ),
            ),
            "iwd-89": _iwd_component_contract(
                "89", "EstonianWar1918-1920", "EstonianWar_Finland_1918-1920",
                1918, 1920, (("375", "Finland"),), (("365", "Russia"),),
                "1", "initiator_victory", ("176", "177", "178"),
                allies=(
                    ("366", "Estonia"),
                    ("220", "France"),
                    ("200", "United Kingdom"),
                ),
                joiner_decision=True,
            ),
            "iwd-90": _iwd_component_contract(
                "90", "EstonianWar1918-1920", "EstonianWar_UK_1918-1920",
                1918, 1920, (("200", "United Kingdom"),), (("365", "Russia"),),
                "1", "initiator_victory", ("179", "180", "181"),
                allies=(
                    ("366", "Estonia"),
                    ("375", "Finland"),
                    ("220", "France"),
                ),
                joiner_decision=True,
            ),
            "iwd-91": _iwd_component_contract(
                "91", "EstonianWar1918-1920", "EstonianWar_France_1918-1920",
                1918, 1920, (("220", "France"),), (("365", "Russia"),),
                "1", "initiator_victory", ("182", "183", "184"),
                allies=(
                    ("366", "Estonia"),
                    ("375", "Finland"),
                    ("200", "United Kingdom"),
                ),
                joiner_decision=True,
            ),
        },
        "party_bindings": {
            "365": "russian_sfsr",
            "366": "first_republic_estonia",
            "375": "clio_su_finland_rep_1918_31f8394b",
            "220": "french_third_republic",
            "200": "united_kingdom",
        },
    },
    "41": {
        "components": {
            "iwd-99": _iwd_component_contract(
                "99", "Poland-USSR", "Poland-USSR", 1920, 1920,
                (("290", "Poland"),), (("365", "Russia"),),
                "1", "initiator_victory", ("195",),
            ),
        },
        "party_bindings": {
            "290": "second_polish_republic",
            "365": "russian_sfsr",
        },
    },
    "43": {
        "components": {
            "iwd-102": _iwd_component_contract(
                "102", "Greco-Turkish1919-1922", "Greco-Turkish1919-1922",
                1919, 1922, (("350", "Greece"),), (("640", "Turkey"),),
                "2", "initiator_defeat", ("198", "199", "200", "201"),
            ),
        },
        "party_bindings": {
            "350": "kingdom_greece",
            "640": "turkish_national_movement",
        },
    },
    "44": {
        "components": {
            "iwd-103": _iwd_component_contract(
                "103", "France-Turkey 1919-21", "France-Turkey 1919-21",
                1919, 1921, (("220", "France"),), (("640", "Turkey"),),
                "3", "draw", ("202", "203", "204"),
            ),
        },
        "party_bindings": {
            "220": "french_third_republic",
            "640": "turkish_national_movement",
        },
    },
    "57": {
        "components": {
            "iwd-181": _iwd_component_contract(
                "181", "OffShoreIslands_1954-55", "OffShoreIslands_1954-55",
                1954, 1955, (("710", "China"),), (("713", "Taiwan"),),
                "1", "initiator_victory", ("466", "467"),
            ),
        },
        "party_bindings": {
            "710": "peoples_republic_china",
            "713": "clio_cn_chinese_rep_1912_970b7032",
        },
    },
    "60": {
        "components": {
            "iwd-186": _iwd_component_contract(
                "186", "TaiwanStraits_1958", "TaiwanStraits_1958", 1958, 1958,
                (("710", "China"),), (("713", "Taiwan"),),
                "3", "draw", ("472",),
            ),
        },
        "party_bindings": {
            "710": "peoples_republic_china",
            "713": "clio_cn_chinese_rep_1912_970b7032",
        },
    },
    "91": {
        "components": {
            "iwd-258": _iwd_component_contract(
                "258", "China-Taiwan_1950", "China-Taiwan_1950", 1950, 1950,
                (("710", "China"),), (("713", "Taiwan"),),
                "1", "initiator_victory", ("400",),
            ),
        },
        "party_bindings": {
            "710": "peoples_republic_china",
            "713": "clio_cn_chinese_rep_1912_970b7032",
        },
    },
}


# Explicit, time-bounded identity policies for bare HCED side labels that lack
# Seshat coding. A policy label is authoritative: outside its windows the side
# stays staged instead of falling through to alias matching. Deliberate gaps
# (France 1816-1851 and 1941-1957, Russia pre-1721 and 1918-1921, Persia
# -329..223, 652-1500, 1748-1793, and post-1925) keep events from eras without
# a curated identity staged rather than attached to a neighboring regime.
HCED_LABEL_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    # The "france" 1870 boundary year is contained by BOTH the Second Empire
    # and Third Republic windows, so 1870 rows are ambiguous by containment
    # and deliberately stay staged (the war's battles split at 4 September).
    "france": (
        (987, 1792, "kingdom_france"),
        (1793, 1803, "french_first_republic"),
        (1804, 1815, "first_french_empire"),
        (1852, 1870, "second_french_empire"),
        (1870, 1940, "french_third_republic"),
        (1958, 2026, "french_fifth_republic"),
    ),
    "russia": (
        (1547, 1720, "clio_ru_moskva_rurik_dyn_1547_93deb0e2"),
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
    "portugal": _PORTUGAL_WINDOWS,
    "spain": ((1479, 1898, "spanish_empire"),),
    "rome": ((-509, -27, "roman_republic"), (-27, 394, "roman_empire")),
    "romans": ((-509, -27, "roman_republic"), (-27, 394, "roman_empire")),
    "byzantium": ((395, 1453, "byzantine_empire"),),
    "byzantines": ((395, 1453, "byzantine_empire"),),
    # Persia gaps: 1748-1793 (Zand era and pre-Kerman Qajar) is deliberate.
    "persia": (
        (-550, -330, "achaemenid_empire"),
        (224, 651, "sasanian_empire"),
        (1501, 1736, "safavid_empire"),
        (1737, 1747, "afsharid_iran"),
        (1794, 1925, "qajar_iran"),
    ),
    "ottomans": ((1299, 1922, "ottoman_empire"),),
    # Exact source spellings, including two upstream misspellings. These are
    # policy keys only and are deliberately not broad seed aliases.
    "macedonia": ((-336, -323, "macedonian_empire"),),
    "ummayyad caliphate": ((661, 750, "umayyad_caliphate"),),
    "mamluks": ((1250, 1517, "mamluk_sultanate"),),
    "dutch rebels": ((1568, 1795, "dutch_republic"),),
    "untied kingdom": ((1707, 2026, "united_kingdom"),),
    # ---- M4 curated state identities (second reviewer pending) ----
    "afghanistan": ((1747, 1822, "durrani_empire"), (1823, 1926, "emirate_afghanistan")),
    "austria": _HABSBURG_WINDOWS,
    # HCED uses "Austria-Hungary" anachronistically for pre-1867 events; the
    # 1804-1866 window maps them to the era-correct Austrian Empire.
    "austria hungary": ((1804, 1866, "austrian_empire"), (1867, 1918, "austria_hungary")),
    "denmark": ((1523, 2026, "kingdom_denmark"),),
    "england": _ENGLAND_WINDOWS,
    "habsburg empire": _HABSBURG_WINDOWS,
    "korea": ((1392, 1897, "joseon"),),
    "maratha empire": ((1674, 1818, "maratha_confederacy"),),
    "marathas": ((1674, 1818, "maratha_confederacy"),),
    "muslim caliphate": ((632, 660, "rashidun_caliphate"), (661, 750, "umayyad_caliphate")),
    "mysore": ((1572, 1799, "kingdom_mysore"),),
    "poland": (
        (1569, 1795, "polish_lithuanian_commonwealth"),
        (1918, 1939, "second_polish_republic"),
    ),
    # Year-only sources cannot split the 18 January 1871 imperial
    # proclamation. Use one reproducible convention in every pipeline:
    # bare 1871 records enter the German Empire identity.
    "prussia": ((1701, 1870, "kingdom_prussia"), (1871, 1871, "german_empire")),
    # A label policy only, deliberately not a seed alias: in HCED's 1799-1849
    # rows the bare region name denotes the Lahore state.
    "punjab": ((1799, 1849, "sikh_empire"),),
    "scotland": ((843, 1706, "kingdom_scotland"),),
    "sweden": ((1523, 2026, "kingdom_sweden"),),
    "transvaal": ((1852, 1902, "south_african_republic"),),
    "venice": ((697, 1797, "republic_venice"),),
    # ---- Post-M4 crisp state-identity tranche ----
    # The Argentina and Bulgaria transition years intentionally overlap two
    # policy windows, preserving the pause-at-year-precision rule.
    "argentina": (
        (1831, 1861, "argentine_confederation"),
        (1861, 1930, "argentine_republic_1861"),
        (1930, 2026, "clio_q414_1930_5e281b3e"),
    ),
    "bulgaria": (
        (1878, 1908, "principality_bulgaria"),
        (1908, 1946, "kingdom_bulgaria"),
    ),
    "mahdists": ((1881, 1899, "mahdist_ansar_forces"),),
    "mahdiyya": ((1881, 1899, "mahdist_ansar_forces"),),
    "the mahdiyya": ((1881, 1899, "mahdist_ansar_forces"),),
    "sudanese mahdists": ((1881, 1899, "mahdist_ansar_forces"),),
    "sudanese islamists": ((1881, 1899, "mahdist_ansar_forces"),),
    "texas": ((1836, 1845, "clio_q170588_1836_8e422d86"),),
    "texan rebels": ((1836, 1845, "clio_q170588_1836_8e422d86"),),
    "syria": (
        (1946, 1957, "clio_sy_syria_modern_1946_86597c89"),
        (1962, 2026, "clio_q41137_1973_b05dea50"),
    ),
    # ---- M5 curated non-state actors (second reviewer pending) ----
    "royalists": ((1642, 1651, "english_royalists"),),
    "parliamentarians": ((1642, 1651, "english_parliamentarians"),),
    "taiping": ((1851, 1864, "taiping_heavenly_kingdom"),),
    "chinese communists": ((1927, 1949, "chinese_communist_forces"),),
    "greek rebels": ((1821, 1829, "greek_revolutionaries_1821"),),
    "spanish republicans": ((1936, 1939, "second_spanish_republic"),),
    "spanish nationalists": ((1936, 1939, "spanish_nationalist_faction"),),
    "mexican liberals": ((1857, 1861, "mexican_liberal_forces"),),
    "mexican conservatives": ((1857, 1861, "mexican_conservative_forces"),),
    "viet cong": ((1960, 1976, "viet_cong"),),
    "cuban rebels": (
        (1868, 1878, "cuban_insurgent_army_1868"),
        (1895, 1898, "cuban_liberation_army_1895"),
        (1955, 1959, "cuban_26_july_movement"),
    ),
    "carlists": ((1833, 1840, "carlist_army_first_war"),),
    # ---- Funnel-ranked identity tranche (greedy batch ranks 1-20) ----
    # Windows are the scorability source: rows outside a window stage as
    # label_outside_policy_window rather than resolving. Deliberate gaps:
    # "hyderabad" starts 1724 (the Asaf Jahi identity begins with the
    # post-Shakar Kheda settlement; the 1720 Balapur/Ratanpur rows await a
    # Mughal-era follow-up contract), "new zealand" covers only the 1907-1947
    # Dominion (post-1948 rows stage until a successor identity is curated,
    # the France/Russia/Persia gap pattern), and "mombassa" has no coverage
    # 1590-1630 or after 1638 (no continuity between the sultanate and the
    # 1631 revolt).
    "norman sicily": ((1139, 1194, "clio_it_sicily_k_1_1139_c1640de5"),),
    "hungarian revolutionaries": ((1848, 1849, "hungarian_honved_army_1848"),),
    "judean rebels": ((66, 73, "great_jewish_revolt_judean_forces_66_73"),),
    "hyderabad": ((1724, 1948, "hyderabad_asaf_jahi_state_1724"),),
    "irish rebels": ((1798, 1803, "united_irishmen"),),
    "palestinian arabs": ((1947, 1949, "palestinian_arab_forces_1947_1949"),),
    "mandingos": ((1878, 1898, "wassoulou_empire_samori_ture"),),
    "ottawa indians": ((1763, 1763, "pontiac_detroit_coalition_1763"),),
    "new zealand": ((1907, 1947, "dominion_new_zealand"),),
    "hauhau": ((1864, 1866, "pai_marire_forces_1864"),),
    "inca": ((1780, 1783, "tupac_amaru_rebellion_forces"),),
    "flemish rebels": ((1379, 1385, "ghent_rebel_regime_1379_1385"),),
    # The exact curated Tang payload is pre-seeded before label resolution and
    # is byte-identical to the Wave 8 Goguryeo fixture. This gives the curated
    # record precedence over the raw Cliopatria candidate without changing its
    # identity window or opening a generic China/Tang alias.
    "huang chao": ((875, 884, "huang_chao_rebel_movement"),),
    "cayuse indians": ((1848, 1848, "cayuse_war_allied_fighting_bands_1848"),),
    "mombassa": (
        (1500, 1589, "sultanate_of_mombasa"),
        (1631, 1638, "mombasa_revolt_yusuf_ibn_al_hasan"),
    ),
    # ---- Audited state-polity tranche (2026-07-20) ----
    # These intentionally narrow windows are outcome-audit boundaries, not
    # claims that the polity existed only in the listed year. Adjacent rows
    # with the same raw label remain staged where HCED names a commander,
    # compresses a mixed campaign, omits a principal ally, or has a chronology
    # conflict. The identity records retain the independently reviewed polity
    # intervals while this table controls which bare labels may score.
    "wurtemburg": ((1866, 1866, "kingdom_wurttemberg_1806_1918"),),
    "hanover": (
        (1794, 1794, "electorate_hanover_1708_1814"),
        (1866, 1866, "kingdom_hanover_1814_1866"),
    ),
    "hesse": ((1866, 1866, "grand_duchy_hesse_1806_1918"),),
    "hormuz": ((1515, 1515, "kingdom_hormuz_1500_1622"),),
    "java": ((1628, 1629, "mataram_sultanate_1588_1755"),),
    "macassar": ((1660, 1660, "sultanate_gowa_1512_1669"),),
    "palmyra": ((272, 272, "palmyrene_empire_270_273"),),
    "suri empire": ((1540, 1540, "sur_empire_1540_1555"),),
    "corinth": (
        (-435, -435, "corinthian_polis_480_338_bce"),
        (-425, -425, "corinthian_polis_480_338_bce"),
    ),
    "corcyra": ((-435, -435, "classical_corcyra_480_433_bce"),),
    # ---- Audited Ming-Manchu transition tranche (2026-07-20) ----
    # These source spellings are admitted only for the independently reviewed
    # four-row singular-Manchu/Zheng inventory.  The existing candidate-keyed
    # Wave 8 Manchus lane continues to own every plural-Manchus row and its
    # identities. Earlier rows remain outside the policy: several pre-1368
    # records call Zhu Yuanzhang's forces "Ming", while the frozen pre-1500
    # cohort may be reopened only by fingerprinted contracts.
    "ming": (
        (1659, 1659, "zheng_chenggong_loyalist_forces_1646_1660"),
        (1661, 1683, "kingdom_tungning_1661_1683"),
    ),
    "ming china": (
        (1619, 1619, "clio_cn_ming_dyn_1375_80721637"),
        (1661, 1662, "kingdom_tungning_1661_1683"),
    ),
    "manchu": (
        (1619, 1619, "nurhaci_hong_taiji_jin_state_1616_1636"),
        (1659, 1659, "clio_cn_qing_dyn_1_1645_8a50480c"),
        (1683, 1683, "clio_cn_qing_dyn_1_1645_8a50480c"),
    ),
}


# Faction, party, movement, and collective-peoples labels are not time-bounded
# polities (the rating unit is a versioned polity or autonomous military actor,
# never a peoples name). The blocklist is checked before every alias tier so
# these labels cannot resolve even when a source record carries a colliding
# alias; promoting one later requires an explicit HCED_LABEL_POLICIES entry
# mapping it to a curated identity.
HCED_FACTION_LABELS: frozenset[str] = frozenset({
    # war-faction / party / movement labels (royalists, parliamentarians,
    # taiping, chinese communists, spanish republicans/nationalists, carlists,
    # and irish rebels migrated to curated actor policies in
    # HCED_LABEL_POLICIES)
    "indian rebels",
    "chinese nationalists", "kuomintang", "guomindang",
    "communists", "nationalists",
    "republicans", "loyalists", "rebels", "insurgents", "jacobites",
    "huguenots", "catholics", "protestants", "covenanters", "confederates",
    "unionists", "boxers", "whites", "reds", "bolsheviks", "mujahideen",
    "cristinos", "mexican rebels", "vendeen rebels",
    "russian whites", "white russians", "seminole indians",
    # collective-peoples labels with no unique time-bounded polity referent
    "vikings", "norsemen", "danes", "tatars", "crusaders", "moors",
    "berbers", "cossacks", "palestinians", "barbary pirates", "pirates",
    "saxons", "huns", "white huns", "mongols", "ostrogoths", "visigoths",
    "goths", "vandals", "franks", "avars", "magyars", "gauls", "celts",
    "slavs", "picts", "normans", "bulgars", "pechenegs", "cumans", "khazars",
    "alans", "lombards", "angles", "jutes", "britons", "scythians",
    "sarmatians", "xiongnu", "arabs", "turks", "germans", "greeks",
    "zulus", "sikhs", "maori", "comanche", "sioux", "cherokee",
    "apache", "seminole",
})


# Genuine polity names whose only time-valid Cliopatria identity is a
# multi-regime envelope (for example one Swiss identity spanning 1294-2024,
# across the 1798 Helvetic reset): full-interval containment is vacuous
# against such a span, so resolving the label would manufacture rating
# continuity across regime boundaries. These stay staged under their own
# counter until curated identity splits exist.
HCED_PENDING_SPLIT_LABELS: frozenset[str] = frozenset({
    "georgia",
    "champa",
    "switzerland",
    "swiss confederation",
    "tibet",
})


# Coalition and composite battle-side labels are not rating units: coalition
# sides need curated per-participant composition, and slash/comma/parenthesis
# composites are ambiguous between alias and coalition — ambiguity always
# stays staged.
IWBD_COALITION_SIDE_LABELS: frozenset[str] = frozenset({
    "allies",
    "allied powers",
    "axis",
    "central powers",
    "balkan league",
    "coalition",
    "nato",
    "arab states",
})


# Candidate-keyed exceptions to IWBD's otherwise fail-closed composite-side
# and containment gates. Each exception carries an exact semantic fingerprint;
# iwbd.py raises on source or resolver drift instead of silently broadening it.
# The Abtao side reconstruction is uniquely reviewed: Spain opposed the exact
# Chile-Peru coalition and the result is inconclusive. No generic slash parsing
# is enabled by this policy.
IWBD_REVIEWED_PARTICIPANT_COMPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-52-18-185": {
        "fingerprint": {
            "source_row": "185",
            "name": "Abtao",
            "war_name": "Naval War",
            "start_date": "1866-02-07",
            "end_date": "1866-02-07",
            "duration_days": "1",
            "attacker_raw": "Spain",
            "defender_raw": "Chile/Peru",
            "winner_raw": "Inconclusive",
            "battle_level_victor_role": "Inconclusive",
        },
        "attacker": (("Spain", "spanish_empire"),),
        "defender": (
            ("Chile", "clio_ch_chile_rep_1_1812_3b31ba25"),
            ("Peru", "clio_q419_1822_a6e12c5b"),
        ),
    },
}


# Mishan (17-18 November 1929) overlaps Chalainor 2 on the first day but the
# reviewed operations are concurrent and geographically distinct. The target
# may bypass containment only while the exact sibling set and both source
# fingerprints remain unchanged.
IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS: dict[str, dict[str, Any]] = {
    "iwbd-118-45-842": {
        "fingerprint": {
            "source_row": "842",
            "name": "Mishan",
            "war_name": "Manchurian",
            "start_date": "1929-11-17",
            "end_date": "1929-11-18",
            "duration_days": "2",
            "attacker_raw": "USSR",
            "defender_raw": "China",
            "winner_raw": "USSR",
            "battle_level_victor_role": "Attacker",
        },
        "contained_candidates": {
            "iwbd-118-45-840": {
                "source_row": "840",
                "name": "Chalainor 2",
                "war_name": "Manchurian",
                "start_date": "1929-11-17",
                "end_date": "1929-11-17",
                "duration_days": "1",
                "attacker_raw": "USSR",
                "defender_raw": "China",
                "winner_raw": "USSR",
                "battle_level_victor_role": "Attacker",
            },
        },
    },
}


# Candidate-keyed HCED crosswalk exception for an action independently dated
# to the post-independence side of an otherwise fail-closed year boundary. The
# complete semantic fingerprint prevents this binding from applying to a
# changed source row, and the code override never becomes a generic code or
# label window.
HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS: dict[str, dict[str, Any]] = {
    "hced-Piraja1822-1": {
        "fingerprint": {
            "source_row": "12561",
            "source_record_id": "Piraja1822",
            "name": "Piraja",
            "year_low": "1822",
            "year_best": "1822",
            "year_high": "1822",
            "side_1_raw": "Brazilian Rebels",
            "side_2_raw": "Portugal",
            "winner_raw": "Brazilian Rebels",
            "loser_raw": "Portugal",
            "seshat_side_1_candidates": ("br_brazil_emp",),
            "seshat_side_2_candidates": ("pt_portuguese_emp_2",),
            "war_names": ("Brazilian War of Independence",),
        },
        "code_bindings": {
            "pt_portuguese_emp_2": "kingdom_portugal_restored",
        },
        "review": {
            "event_date": "1822-11-08",
            "source_urls": (
                "https://al.ba.gov.br/historia-do-legislativo/batalha-piraja",
                "https://www.gov.br/mast/pt-br/assuntos/noticias/2022/julho/as-independencias-do-brasil",
            ),
        },
    },
    "hced-Fort Zeelandia1661-1662-1": {
        "fingerprint": {
            "source_row": "5777",
            "source_record_id": "Fort Zeelandia1661-1662",
            "name": "Fort Zeelandia",
            "year_low": "1661",
            "year_best": "1662",
            "year_high": "1662",
            "side_1_raw": "Ming China",
            "side_2_raw": "Netherlands",
            "winner_raw": "Ming China",
            "loser_raw": "Netherlands",
            "seshat_side_1_candidates": ("cn_qing_dyn_1",),
            "seshat_side_2_candidates": (),
            "war_names": ("Chinese Conquest of Taiwan",),
        },
        "code_bindings": {
            "cn_qing_dyn_1": "kingdom_tungning_1661_1683",
        },
        "review": {
            "event_date": "1661-1662",
            "source_urls": (
                "https://china.usc.edu/node/20504",
                "https://ws.moi.gov.tw/Download.ashx?icon=..pdf&n=QVRfMjAwOTAzMjYxMTMzNDcucGRm&u=LzAwMS9VcGxvYWQvT2xkRmlsZV9OTFNDL3VwbG9hZGZpbGUvQVRfMjAwOTAzMjYxMTMzNDcucGRm",
            ),
        },
    },
}


def _iwbd_identity_contract(
    source_row: str,
    name: str,
    war_name: str,
    start_date: str,
    end_date: str,
    duration_days: str,
    attacker_raw: str,
    defender_raw: str,
    winner_raw: str,
    battle_level_victor_role: str,
    attacker_id: str,
    defender_id: str,
) -> dict[str, Any]:
    return {
        "fingerprint": {
            "source_row": source_row,
            "name": name,
            "war_name": war_name,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "attacker_raw": attacker_raw,
            "defender_raw": defender_raw,
            "winner_raw": winner_raw,
            "battle_level_victor_role": battle_level_victor_role,
        },
        "attacker": ((attacker_raw, attacker_id),),
        "defender": ((defender_raw, defender_id),),
    }


# Candidate-keyed identity contracts for labels that are ambiguous outside the
# reviewed battle itself. These records never become aliases or generic label
# windows. Both sides are exact-ID bound so an identity or source drift raises
# instead of silently selecting a neighboring regime.
IWBD_REVIEWED_IDENTITY_BINDINGS: dict[str, dict[str, Any]] = {
    "iwbd-1-1-2": _iwbd_identity_contract(
        "2", "Trocadero", "Franco-Spanish", "1823-08-31", "1823-08-31", "1",
        "France", "Spain", "France", "Attacker",
        "bourbon_restoration_france", "spanish_empire",
    ),
    "iwbd-58-20-257": _iwbd_identity_contract(
        "257", "Orleans", "Franco-Prussian", "1870-12-04", "1870-12-05", "2",
        "Prussia", "France", "Prussia", "Attacker",
        "kingdom_prussia", "french_third_republic",
    ),
    "iwbd-115-43-802": _iwbd_identity_contract(
        "802", "Smyrna 1", "Second Greco-Turkish", "1919-05-15", "1919-05-15", "1",
        "Greece", "Turkey", "Greece", "Attacker",
        "kingdom_greece", "turkish_national_movement",
    ),
    "iwbd-115-43-803": _iwbd_identity_contract(
        "803", "Urla", "Second Greco-Turkish", "1919-05-16", "1919-05-17", "2",
        "Greece", "Turkey", "Greece", "Attacker",
        "kingdom_greece", "turkish_national_movement",
    ),
    "iwbd-115-43-804": _iwbd_identity_contract(
        "804", "Malgac", "Second Greco-Turkish", "1919-06-15", "1919-06-16", "2",
        "Turkey", "Greece", "Turkey", "Attacker",
        "turkish_national_movement", "kingdom_greece",
    ),
    "iwbd-115-43-806": _iwbd_identity_contract(
        "806", "Erbeyli", "Second Greco-Turkish", "1919-06-20", "1919-06-21", "2",
        "Turkey", "Greece", "Inconclusive", "Inconclusive",
        "turkish_national_movement", "kingdom_greece",
    ),
    "iwbd-115-43-807": _iwbd_identity_contract(
        "807", "Erikli", "Second Greco-Turkish", "1919-06-21", "1919-06-22", "2",
        "Turkey", "Greece", "Turkey", "Attacker",
        "turkish_national_movement", "kingdom_greece",
    ),
    "iwbd-115-43-808": _iwbd_identity_contract(
        "808", "Tellidede", "Second Greco-Turkish", "1919-06-25", "1919-06-26", "2",
        "Greece", "Turkey", "Greece", "Attacker",
        "kingdom_greece", "turkish_national_movement",
    ),
    "iwbd-115-43-809": _iwbd_identity_contract(
        "809", "Aydin", "Second Greco-Turkish", "1919-06-27", "1919-07-04", "8",
        "Greece", "Turkey", "Greece", "Attacker",
        "kingdom_greece", "turkish_national_movement",
    ),
    "iwbd-115-43-819": _iwbd_identity_contract(
        "819", "Smyrna 2", "Second Greco-Turkish", "1922-09-09", "1922-09-11", "3",
        "Turkey", "Greece", "Turkey", "Attacker",
        "turkish_national_movement", "kingdom_greece",
    ),
    "iwbd-116-44-820": _iwbd_identity_contract(
        "820", "Marash", "Franco-Turkish", "1920-01-21", "1920-02-13", "24",
        "Turkey", "France", "Turkey", "Attacker",
        "turkish_national_movement", "french_third_republic",
    ),
    "iwbd-116-44-821": _iwbd_identity_contract(
        "821", "Urfa", "Franco-Turkish", "1920-02-09", "1920-04-11", "63",
        "Turkey", "France", "Turkey", "Attacker",
        "turkish_national_movement", "french_third_republic",
    ),
    "iwbd-116-44-823": _iwbd_identity_contract(
        "823", "Karbogazi", "Franco-Turkish", "1920-05-27", "1920-05-28", "2",
        "Turkey", "France", "Turkey", "Attacker",
        "turkish_national_movement", "french_third_republic",
    ),
    "iwbd-116-44-824": _iwbd_identity_contract(
        "824", "Kanli Gecit", "Franco-Turkish", "1920-11-01", "1920-11-09", "9",
        "Turkey", "France", "Turkey", "Attacker",
        "turkish_national_movement", "french_third_republic",
    ),
    "iwbd--9-91-1402": _iwbd_identity_contract(
        "1402", "Hainan", "China-Taiwan Islands", "1950-03-05", "1950-04-22", "49",
        "China", "Taiwan", "China", "Attacker",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
    "iwbd--9-91-1403": _iwbd_identity_contract(
        "1403", "Wanshan", "China-Taiwan Islands", "1950-05-25", "1950-06-27", "34",
        "China", "Taiwan", "China", "Attacker",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
    "iwbd-153-57-1445": _iwbd_identity_contract(
        "1445", "September Third", "Off-shore Islands", "1954-09-03", "1954-09-03", "1",
        "China", "Taiwan", "Inconclusive", "Inconclusive",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
    "iwbd-153-57-1446": _iwbd_identity_contract(
        "1446", "Yijiangshan Islands", "Off-shore Islands", "1955-01-18", "1955-01-20", "3",
        "China", "Taiwan", "China", "Attacker",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
    "iwbd-153-57-1447": _iwbd_identity_contract(
        "1447", "Dachen Archipelago", "Off-shore Islands", "1955-01-19", "1955-02-26", "39",
        "China", "Taiwan", "China", "Attacker",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
    "iwbd-159-60-1460": _iwbd_identity_contract(
        "1460", "Kinmen", "Taiwan Straits", "1958-08-23", "1958-10-06", "45",
        "China", "Taiwan", "Inconclusive", "Inconclusive",
        "peoples_republic_china", "clio_cn_chinese_rep_1912_970b7032",
    ),
}


IWBD_REVIEWED_IDENTITY_COHORTS: dict[str, tuple[str, ...]] = {
    "bourbon_restoration_1823": ("iwbd-1-1-2",),
    "orleans_third_republic": ("iwbd-58-20-257",),
    "turkish_national_movement_greco_turkish": (
        "iwbd-115-43-802", "iwbd-115-43-803", "iwbd-115-43-804",
        "iwbd-115-43-806", "iwbd-115-43-807", "iwbd-115-43-808",
        "iwbd-115-43-809", "iwbd-115-43-819",
    ),
    "turkish_national_movement_franco_turkish": (
        "iwbd-116-44-820", "iwbd-116-44-821",
        "iwbd-116-44-823", "iwbd-116-44-824",
    ),
    "roc_taiwan_1950": ("iwbd--9-91-1402", "iwbd--9-91-1403"),
    "roc_taiwan_1954_1955": (
        "iwbd-153-57-1445", "iwbd-153-57-1446", "iwbd-153-57-1447",
    ),
    "roc_taiwan_1958": ("iwbd-159-60-1460",),
}


# Declared identity deny windows, enforced in every label-resolution pipeline:
# within a window the label is never resolved, because it denotes an actor
# distinct from the identity the resolver would return. The Latvia envelope
# bridges separate regimes; "Turkey" in 1919-1923 denotes the nationalist/
# Kemalist movement and then the Ankara government, fighting in parallel with
# the Istanbul government, and must not attach to the Ottoman identity.
IDENTITY_DENY_WINDOWS: dict[str, tuple[tuple[int, int], ...]] = {
    # Cliopatria's Latvia envelope bridges the first republic, Soviet
    # occupation, and restored republic. Until those identities are split,
    # generic Latvia labels before the 1991 restoration stay fail-closed.
    "latvia": ((1918, 1991),),
    # Generic "Mexico" is ambiguous during the French intervention between
    # Juarez's republican government and the Second Mexican Empire.  Until
    # those concurrent actors have reviewed identities, every label pipeline
    # must fail closed instead of accepting a broad Cliopatria alias.
    "mexico": ((1864, 1867),),
    "turkey": ((1919, 1923),),
}


# Curated row exclusions (second reviewer pending), mirroring
# UCDP_CURATED_EXCLUSIONS: enumerated, documented, counted under a
# curated-exclusion rejection counter in the owning pipeline, never merged
# and never fuzzy-matched.
HCED_CURATED_EXCLUSIONS: dict[str, str] = {
    "hced-Dunamunde1701-1": (
        "variant duplicate of hced-Riga1701-1 for the 1701 Crossing of the "
        "Duna/Battle of Riga; both stay staged because the crosswalk omits "
        "the principal Saxon opponent"
    ),
    "hced-Lesnaya1708-1": (
        "source outcome is reversed: Lesnaya was a Russian victory over the "
        "Swedish column, not a Swedish victory"
    ),
    "hced-Napue1714-1": (
        "duplicate wrong-orientation record for the Russian victory at "
        "Storkyro/Isokyro; hced-Storkyro1714-1 is the retained source row"
    ),
    "hced-Montijo1644-1": (
        "wrong opposing actor: the Restoration War battle was Portugal versus "
        "Spain, while the source row incorrectly codes England"
    ),
    "hced-Altona1714-1": (
        "phantom/misdated action with the wrong actor: the documented Altona "
        "action was Sweden burning Danish Altona in January 1713, not a "
        "Russian victory over Sweden in 1714"
    ),
    "hced-Bronnitsa1614-1": (
        "source outcome is reversed: Swedish forces under De la Gardie drove "
        "the Russian forces from Bronnitsy in July 1614"
    ),
    "hced-Punitz1704-1": (
        "wrong opposing actor after composite-side collapse: the opposing army "
        "at Punitz was Saxon under Schulenburg, not Russian"
    ),
    "hced-Salvador1638-1": (
        "source outcome is reversed: the Dutch assault on Portuguese Salvador "
        "failed and the besiegers withdrew"
    ),
    "hced-Malacca1606-1": (
        "source outcome is reversed: the first VOC siege of Portuguese Malacca "
        "failed after a Portuguese relief force arrived"
    ),
    "hced-Beachy Head1707-1": (
        "wrong opposing actor: the Action of 2 May 1707 was fought by a French "
        "squadron against a British convoy and escorts; Portugal did not fight"
    ),
    "hced-Colonia do Sacrimento1735-1": (
        "source outcome is reversed: the Portuguese fortress withstood the "
        "Spanish siege of 1735-1737"
    ),
    "hced-Reval1719-1": (
        "departure-port duplicate/mislabel of hced-Osel Island1719-1: the "
        "Russian squadron sailed from Reval for the single Osel naval action"
    ),
    "hced-Majadahonda1812-1": (
        "source outcome is reversed: French cavalry defeated the Anglo-"
        "Portuguese cavalry at Majadahonda"
    ),
    "hced-Elba1811-1": (
        "misnamed El Bodon action with a reversed outcome: French forces won "
        "and the Anglo-Portuguese force withdrew"
    ),
    "hced-Campo1811-1": (
        "duplicate/ambiguous Campo Maior record: it shares the retained siege "
        "row's exact coordinates and French-victory assertion, while the "
        "separate 25 March combat was an Anglo-Portuguese victory"
    ),
    "hced-Azov1695-1696-1": (
        "conflates opposite-result campaigns: the source dates the event only "
        "to 1695, when the Russian siege failed, while the 1696 campaign won"
    ),
    "hced-Salvador1822-1823-1": (
        "cross-boundary campaign envelope: the Salvador campaign began before "
        "Brazilian independence on 7 September 1822 and continued to July "
        "1823, so one year-level Portuguese identity cannot represent it"
    ),
    "hced-Aden1513-1": (
        "anachronistic principal actor: Aden was Tahirid in 1513; Ottoman "
        "conquest did not occur until 1538"
    ),
    "hced-Wofla1542-1": (
        "incomplete principal side: the Adal Sultanate fielded the army at "
        "Wofla, but the crosswalk retains Ottoman support alone"
    ),
    "hced-Marbella1705-1": (
        "incomplete principal side: the opposing squadron was principally "
        "French, but the crosswalk retains Spain alone"
    ),
    "hced-Cadiz1810-1812-1": (
        "incomplete principal side and campaign envelope: Spanish defenders "
        "are omitted from the two-year siege of Cadiz"
    ),
    "hced-Barrosa1811-1": (
        "incomplete principal side: the Spanish army is omitted from the "
        "Allied force at Barrosa"
    ),
    "hced-Riga1701-1": (
        "incomplete principal side at the Crossing of the Duna: the principal "
        "opponent was Saxony, but the crosswalk retains Russian auxiliaries alone"
    ),
    "hced-Pandjeh1885-1": "duplicate of Penjdeh 1885 under a variant spelling",
    "hced-Gustalla1734-1": "duplicate of Guastalla 1734 under a variant spelling",
    "hced-Truillas1793-1": "duplicate of Trouillas 1793 under a variant spelling",
    "hced-Juthas1808-1": "duplicate of Jutas 1808 under a variant spelling",
    "hced-Libertwolkwitz1813-1": "duplicate of Liebertwolkwitz 1813 under a variant spelling",
    "hced-Herat1837-1838-1": (
        "defender was the independent Sadozai principality of Herat, not the Kabul emirate"
    ),
    "hced-Herat1856-1": (
        "defender was the independent principality of Herat; Kabul was aligned "
        "with Britain against Persia"
    ),
    "hced-Herat1863-1": (
        "Dost Mohammad's siege of Sultan Ahmad Khan's Herat; Persia fielded no army"
    ),
    "hced-Alcacer do Sol1158-1": (
        "Afonso I of Portugal's conquest; England was not a belligerent in 1158"
    ),
    "hced-St Quentin1557-1": (
        "fought by Habsburg Spain after Charles V's abdication; the Danubian "
        "monarchy was not a belligerent"
    ),
    # Historical-adjudication tranche. The immutable HCED source assertions
    # remain in data/raw; these rows stay staged because the asserted outcome,
    # actor, date, or granularity is not defensible for rating.
    "hced-Andalsnes1940-1": (
        "wrong belligerent: Andalsnes was a British-Norwegian operation, not French"
    ),
    "hced-Aros1886-1": (
        "disputed friendly-fire outcome: Mexican and US accounts of the Crawford "
        "affair conflict, so an unqualified Mexican tactical victory is unsupported"
    ),
    "hced-Brusilov Offensive1916-1": (
        "inverted outcome: the Brusilov Offensive was a Russian victory over the Central Powers"
    ),
    "hced-Changsha1942II-1": (
        "duplicate of Changsha 1941-1942: both rows cite the same Third Battle of "
        "Changsha account and assert the same Chinese victory over Japan"
    ),
    "hced-Duppel1849-1": (
        "wrong belligerent and outcome: Austria did not fight at Dybbol; Denmark won the action"
    ),
    "hced-France1940-1": (
        "campaign envelope duplicates separately rated Fall of France component engagements"
    ),
    "hced-Galicia1914-1": (
        "campaign envelope duplicates separately rated Galicia component engagements"
    ),
    "hced-Grol1627-1": (
        "wrong principal belligerent: the Dutch States Army, not England and France, took Grol"
    ),
    "hced-Hadad1562-1": (
        "inverted outcome and branch confusion: Habsburg forces defeated Ottoman-vassal Transylvania"
    ),
    "hced-Hanoi1873-1": (
        "wrong belligerent: Nguyen Vietnam and the Black Flags fought France, not Qing state forces"
    ),
    "hced-Isola del Giglio1646-1": (
        "Habsburg branch confusion: the defending fleet belonged to Habsburg Spain"
    ),
    "hced-Kaiserswerth1702-1": (
        "inverted outcome: the French garrison capitulated to the Allied besiegers"
    ),
    "hced-Kemmel1918-1": "inverted outcome: German forces captured Mont Kemmel",
    "hced-Laredo1842-1": (
        "unsupported opposing force: the Somervell expedition captured and sacked "
        "Laredo without an identified Mexican field force"
    ),
    "hced-Lepanto1571-1": (
        "wrong belligerent: the Danubian Habsburg monarchy did not fight at Lepanto"
    ),
    "hced-Maastricht1632-1": (
        "wrong principal belligerent: the Dutch States Army, not England and France, took Maastricht"
    ),
    "hced-Martinesti1789-1": "duplicate of Rimnik/Rymnik 1789 under the battlefield place name",
    "hced-Mill Creek1839-1": (
        "wrong opponent identity: Cordova's Mexican and Indigenous insurgent band "
        "was not the Mexican Republic; a bounded actor identity is still pending"
    ),
    "hced-Messina1718-1": (
        "wrong opposing sides: Spain captured Messina while France and Austria were allies"
    ),
    "hced-Monte Grappa1917-1": (
        "wrong principal belligerent: the 1917 defense was an Italian operation"
    ),
    "hced-Monte Grappa1918-1": (
        "wrong principal belligerent: Italy is omitted from its own Monte Grappa battle"
    ),
    "hced-Nivelle Offensive1917-1": (
        "campaign envelope duplicates the separately rated Aisne 1917 offensive"
    ),
    "hced-Norway1940-1": (
        "campaign envelope duplicates separately rated Norwegian Campaign engagements"
    ),
    "hced-Rheims1359-1360-1": (
        "inverted siege assertion: Edward III abandoned the siege without taking Rheims"
    ),
    "hced-Rocoux1747-1": "date error: Rocoux was fought in 1746",
    "hced-Rosas1645-1": (
        "Habsburg branch confusion: the defense belonged to Habsburg Spain"
    ),
    "hced-San Antonio, Texas (2nd)1842-1": (
        "wrong outcome: Mexican forces occupied San Antonio after the defenders "
        "surrendered; the later Texan resistance is represented separately"
    ),
    "hced-SanAntonio, Texas1842-1": (
        "unsupported engagement: the first 1842 seizure was an unopposed occupation "
        "after the Texan evacuation, not a bilateral draw"
    ),
    "hced-Sevastopol1854-1855-1": (
        "campaign envelope duplicates separately rated Crimean War siege components"
    ),
    "hced-St Augustine1702-1": (
        "inverted outcome: the English siege failed and the attackers withdrew"
    ),
    "hced-St Quentin1914-1": "duplicate of the Battle of Guise/Saint-Quentin 1914",
    "hced-Trebizond1916-1": (
        "wrong belligerents: the campaign was exclusively Russian, not French or British"
    ),
    "hced-Trentino1917-1": (
        "date/granularity ambiguity: likely duplicates the 1916 Asiago offensive or 1917 Ortigara"
    ),
    "hced-Vittorio Veneto1918-1": (
        "wrong principal belligerent: Italy is omitted from the Vittorio Veneto victory"
    ),
    # Identity-tranche source-side audit: these rows become technically
    # resolvable once the Argentina/Mexico code windows exist, but their raw
    # belligerent reconstruction is incomplete, wrong, or duplicated.
    "hced-Boqueron, Nhembucu1866-1": (
        "incomplete coalition: Brazil is omitted from the coded side"
    ),
    "hced-Corrientes (2nd)1865-1": (
        "incomplete coalition: Brazil is omitted from the coded side"
    ),
    "hced-Curupaity1866-1": (
        "incomplete coalition: Brazil and Uruguay are omitted from the coded side"
    ),
    "hced-Curuzu1866-1": (
        "wrong belligerent: Curuzu was a Brazilian land-and-naval operation, "
        "while the source-side coding adds Argentina"
    ),
    "hced-Estero Bellaco1866-1": (
        "incomplete belligerents: the reconstruction omits Uruguay from the Allied force"
    ),
    "hced-Fluvial1866-1": "incomplete coalition: Brazil is omitted from the coded side",
    "hced-India Muerta1845-1": (
        "wrong identity flattening: the Blanco-Argentine force against Rivera's "
        "Colorados is not a simple Argentina-versus-Uruguay state battle"
    ),
    "hced-Ita Ybate1868-1": "incomplete coalition: Uruguay is omitted from the coded side",
    "hced-Riachuelo1865-1": (
        "wrong belligerent: Riachuelo was fought by the Brazilian and Paraguayan fleets"
    ),
    "hced-Tuyuti1866-1": "incomplete coalition: Uruguay is omitted from the coded side",
    "hced-Uruguayana1865-1": "incomplete coalition: Uruguay is omitted from the coded side",
    "hced-Yatay1865-1": (
        "incomplete coalition: Brazilian and Uruguayan belligerents are omitted"
    ),
    "hced-Ytororo1868-1": (
        "wrong and incomplete belligerents: Ytororo was principally Brazil versus Paraguay"
    ),
    "hced-Atlixco1847-1": (
        "inverted outcome and swapped identity coding: United States forces won at Atlixco"
    ),
    "hced-Molino del Rey1847-1": (
        "inverted outcome: United States forces captured the Molino del Rey position"
    ),
    "hced-Toluca1860-1": (
        "wrong actor identity: the opposing force was the Mexican Conservative faction, "
        "not a generic Mexican Republic state side"
    ),
    "hced-San Carlos, Falklands1982-1": (
        "duplicate of the day-precision IWBD San Carlos record iwbd-202-78-1636"
    ),
    "hced-Stanley1982-1": (
        "overlapping operation envelope: the Battle for Stanley aggregates high-ground "
        "engagements already rated separately, including Longdon and Tumbledown"
    ),
    "hced-Thorntons Ambush1846-1": (
        "duplicate of the day-precision IWBD Thornton's Ambush record iwbd-7-3-10"
    ),
}


IWBD_CURATED_EXCLUSIONS: dict[str, str] = {
    "iwbd-13-5-51": (
        "wrong outcome at Duppel/Dybbol on 1849-04-13: Denmark, not Prussia, "
        "won the action"
    ),
    "iwbd-55-19-188": "duplicate of HCED Liebenau 1866 (spelling variant 'Liebnau')",
    "iwbd-58-20-268": "duplicate of HCED Dijon 1871 (IWBD 'Dijon 3')",
    "iwbd-76-28-346": "duplicate of HCED Velestino (1st) 1897 (IWBD 'Velestino 1')",
    "iwbd-108-40-788": (
        "wrong principal belligerent at Riga 2 in October 1919: Latvian forces "
        "fought the Bermondt/West Russian Volunteer Army, not the Russian SFSR"
    ),
    "iwbd-115-43-810": (
        "wrong opposing belligerent at Akbas on 1920-01-26/27: Turkish National "
        "Forces raided a French-guarded ammunition store, not Greek forces"
    ),
    "iwbd-115-43-811": (
        "unsafe event granularity: the 93-day Summer Offensive is an operational "
        "campaign umbrella, not one independently rateable tactical battle"
    ),
    "iwbd-115-43-812": (
        "wrong outcome at Gediz in October-November 1920: Turkish National "
        "Forces were defeated, not tactically inconclusive"
    ),
    "iwbd-127-49-877": "duplicate of HCED Tembien (1st) 1936 (IWBD 'Tembien 1')",
    "iwbd-127-49-879": "duplicate of HCED Tembien (2nd) 1936 (IWBD 'Tembien 2')",
    "iwbd-187-73-1600": (
        "duplicate of HCED Jijiga 1978; retain the HCED record because its "
        "coalition reconstruction includes Cuba"
    ),
    "iwbd-202-78-1640": (
        "overlapping operation envelope: Stanley aggregates the final high-ground "
        "engagements already rated separately, including Longdon and Tumbledown"
    ),
}


IWD_CURATED_PARENT_EXCLUSIONS: dict[str, str] = {
    "5": (
        "Germany-Denmark 1848 asserts a Prussian strategic victory, but Denmark won the "
        "First Schleswig War; the source assertion stays staged rather than being inverted"
    ),
    "42": (
        "Hungarian-Allies 1919: fought principally by the Hungarian Soviet Republic; "
        "the [1919,1943] Hungary interval bridges the 1919 regime resets (identity pending)"
    ),
    "17": (
        "War of the Triple Alliance aggregation is incomplete: the available IWD "
        "component dyads omit Uruguay from the Argentina-Brazil-Uruguay coalition"
    ),
}


# HCED rows excluded from the label pass by curated adjudication:
# cross-source duplicates of already-promoted IWBD battles under name
# variants exact-key dedup cannot catch, one measured crosswalk error, and
# rows whose "Viet Cong" side labels PAVN engagements.
HCED_LABEL_CURATED_EXCLUSIONS: dict[str, str] = {
    "hced-Sarhu1619-1": (
        "campaign umbrella overlaps the separately represented Niumaozhai and "
        "Siyanggiayan actions; rating all three would repeat the same Sarhu campaign result"
    ),
    "hced-Penghu1683-1": (
        "inverted outcome: Shi Lang's Qing fleet defeated the Zheng/Tungning fleet "
        "at Penghu, not the reverse asserted by the source row"
    ),
    "hced-Megalopolis-331-1": (
        "chronology and the incomplete Macedonian coalition were not independently adjudicated"
    ),
    "hced-Jaxartes-329-1": (
        "the broad Scythia label does not identify the specific Saka force"
    ),
    "hced-Antioch1268-1": (
        "the Principality of Antioch interval ends at its 1268 destruction, not 1271; "
        "the boundary remains unadjudicated"
    ),
    "hced-Mons1572-1": "source-side reconstruction omits the Huguenot co-belligerent",
    "hced-Steenwijk1592-1": "source-side reconstruction omits the English co-belligerent",
    "hced-Amjhera1728-1": "conflicting source chronology remains unresolved",
    "hced-Abensberg1809-1": (
        "incomplete coalition reconstruction: the proposed two-polity rating omits "
        "principal Bavarian and other Confederation forces"
    ),
    "hced-Binh Gia1964-1": "duplicate of iwbd_iwbd_163_62_1468/1469 (Binh Gia a/b, 1964)",
    "hced-Khe Sanh1967-1": "duplicate of iwbd_iwbd_163_62_1489 (Khe Sanh 1, 1967)",
    "hced-Long Tan, Vietnam1966-1": "duplicate of iwbd_iwbd_163_62_1485 (Long Tan, 1966)",
    "hced-Nam Dong1964-1": (
        "mis-crosswalked participant: 'Australia' coded ko_korean_rep (no ROK "
        "forces at Nam Dong)"
    ),
    "hced-Ia Drang1965-1": (
        "side-misattributed: PAVN regulars coded as 'Viet Cong'; north_vietnam "
        "is separately rated"
    ),
    "hced-Con Thien (1st)1967-1": "side-misattributed: PAVN engagement coded as 'Viet Cong'",
    "hced-Con Thien (2nd)1967-1": "side-misattributed: PAVN engagement coded as 'Viet Cong'",
    "hced-Hue1968-1": "side-misattributed: predominantly PAVN engagement coded as 'Viet Cong'",
    "hced-1stDragasani1821-1": (
        "inverted outcome: Ottoman forces destroyed the Sacred Band at Dragasani"
    ),
    "hced-A Shau1966-1": (
        "inverted outcome and actor error: PAVN overran the camp but is coded as defeated Viet Cong"
    ),
    "hced-Arcis-sur-Aube1814-1": (
        "inverted outcome: Napoleon withdrew before Schwarzenberg's Allied army"
    ),
    "hced-Atbara1898-1": (
        "incomplete coalition: Kitchener's Anglo-Egyptian army included British, "
        "Egyptian, and Sudanese formations, while the source-side resolution rates only Britain"
    ),
    "hced-Barcelona, Spain1936-1": (
        "inverted outcome: Republican and anarchist forces defeated the July uprising"
    ),
    "hced-Barcelona, Spain1705-1706-1": (
        "incompatible envelope: combines the distinct 1705 capture and 1706 defense "
        "while the 1705 siege is already rated separately"
    ),
    "hced-Bautzen1813-1": (
        "wrong belligerent: Austria was neutral; the defeated Allies were Prussian and Russian"
    ),
    "hced-Beijing-Tianjin1948-1": (
        "campaign envelope duplicates separately rated Tianjin and related component battles"
    ),
    "hced-Bloody Run1763-1": (
        "inverted outcome: HCED codes the United Kingdom as winner but Pontiac's "
        "coalition defeated Dalyell's sortie from Fort Detroit"
    ),
    "hced-Brest1513-1": "inverted outcome: Howard's English attack on Brest failed",
    "hced-Brienne1814-1": (
        "wrong belligerent: the action was fought against Russian and Prussian forces, not Austria"
    ),
    "hced-Cadore1508-1": (
        "wrong Habsburg branch: Maximilian's Imperial-Tyrolean army is coded as Spain"
    ),
    "hced-Chalchuapa1885-1": (
        "wrong belligerent: the battle was fought by El Salvador against the "
        "Guatemalan invasion; Honduras did not fight at Chalchuapa"
    ),
    "hced-Coatit1895-1": "inverted outcome: Baratieri's Italian force defeated Ras Mengesha",
    "hced-Dardanelles1654-1": "inverted outcome: the first 1654 Dardanelles battle was Ottoman",
    "hced-Dakhila1898-1": (
        "incomplete coalition: the raw winner is United Kingdom and Sudan, but "
        "the British crosswalk short-circuits the composite and drops the Sudanese force"
    ),
    "hced-Dembeguina1935-1": (
        "inverted outcome: Ethiopian forces won the Dembeguina Pass action"
    ),
    "hced-Dong Xoai1965-1": (
        "inverted outcome: Viet Cong forces overran Dong Xoai and mauled the relief force"
    ),
    "hced-Dragasani1821-1": (
        "duplicate source row with the same inverted Dragasani outcome"
    ),
    "hced-El Obeid1883-1": (
        "duplicate of the Kashgal/Kashgil-Sheikan engagement and wrong resolved "
        "loser: Hicks commanded an Egyptian-Khedival army, not a Britain-only force"
    ),
    "hced-Fuengirola1810-1": (
        "incomplete coalition: the source loser label is British and Spanish, but "
        "the Spanish crosswalk short-circuits that composite and omits Britain"
    ),
    "hced-Gedaref1898-1": (
        "wrong resolved belligerent: the field force was Egyptian-Sudanese under "
        "British officers, while the release would rate Britain alone"
    ),
    "hced-Handoub1888-1": (
        "incomplete coalition: the raw winner includes Sudanese forces, but the "
        "British crosswalk short-circuits the composite and drops them"
    ),
    "hced-Huaihai1948-1": (
        "campaign envelope duplicates separately rated Huaihai component battles"
    ),
    "hced-Kalat1839-1": (
        "wrong actor: the defender was the independent Khanate of Kalat, not the Kabul emirate"
    ),
    "hced-Kashgal1883-1": (
        "duplicate of the El Obeid/Kashgil-Sheikan engagement and wrong resolved "
        "loser: Hicks commanded an Egyptian-Khedival army, not a Britain-only force"
    ),
    "hced-Khania1692-1": (
        "incomplete coalition: the Christian expedition also included Maltese and "
        "Florentine forces omitted by the source-side reconstruction"
    ),
    "hced-Kehl1797-1": "inverted outcome: the French garrison capitulated to Austria",
    "hced-Koge Bay1677-1": (
        "wrong belligerent: the supporting Dutch fleet never reached the battle, "
        "which was fought by the Danish-Norwegian and Swedish fleets"
    ),
    "hced-Kolin1756-1": "date error: Kolin was fought in 1757",
    "hced-Kolberg1760-1": "inverted outcome: the Russian siege of Kolberg failed in 1760",
    "hced-Kolberg1774-1": (
        "phantom engagement: no Russo-Prussian battle or war occurred at Kolberg in 1774"
    ),
    "hced-Liaoshen1948-1": (
        "campaign envelope duplicates separately rated Liaoshen component battles"
    ),
    "hced-Longwy1792-1": "wrong belligerent: the siege was conducted by Prussian forces",
    "hced-Lvov1675-1": "inverted outcome: Sobieski defeated the Ottoman-Crimean force",
    "hced-Malaga1704-1": (
        "incomplete coalition: the source omits Spain from the Franco-Spanish fleet"
    ),
    "hced-Marstrand-1": (
        "inverted outcome: Danish-Norwegian forces captured Marstrand and Carlsten"
    ),
    "hced-Mewe1626-1": "inverted outcome: the Battle of Gniew/Mewe was a Swedish victory",
    "hced-Mockern (1st)1813-1": (
        "wrong belligerent: Austria was neutral during the April action"
    ),
    "hced-Mirandola1511-1": (
        "incomplete coalition reconstruction: the siege involved additional Urbino, "
        "Spanish, Mirandolan, and Ferrarese belligerents"
    ),
    "hced-Mojkovac1916-1": "inverted outcome: Montenegro won the defensive action at Mojkovac",
    "hced-Monastir1912-1": (
        "wrong belligerent: Serbian forces fought the Ottoman army at Monastir; "
        "Bulgaria did not participate in the battle"
    ),
    "hced-Montmirail1814-1": (
        "wrong belligerent: Russian and Prussian corps, not Austria, fought at Montmirail"
    ),
    "hced-Nieuport1600-1": (
        "inverted outcome: Maurice's Dutch-led army defeated the Spanish field army"
    ),
    "hced-Omdurman1898-1": (
        "incomplete coalition: the Anglo-Egyptian army included British, Egyptian, "
        "and Sudanese formations, while the release would rate only Britain"
    ),
    "hced-Paniani1782-1": (
        "wrong belligerent: the opposing field force was Mysorean, including "
        "Lally's corps; the Maratha Confederacy did not fight at Paniani"
    ),
    "hced-Parwan Durrah1840-1": "inverted outcome: Dost Mohammad's Afghan force won the action",
    "hced-Piave1809-1": (
        "wrong belligerent identity: the Italian force at Piave belonged to the "
        "Napoleonic Kingdom of Italy (1805-1814), while the ordinary Italy alias "
        "resolves to an over-wide Cliopatria Italian Republic envelope"
    ),
    "hced-Poland1939-1": (
        "campaign envelope duplicates separately rated invasion-of-Poland components"
    ),
    "hced-Raszyn1809-1": (
        "wrong belligerent: the defending coalition was Polish-Saxon, not French; "
        "the source also omits Saxony"
    ),
    "hced-Rippach1813-1": "wrong belligerent: Austria was neutral during the May action",
    "hced-Tournai1794-1": "duplicate of Pont-a-Chin 1794, the same 22 May engagement",
    "hced-Tutrakan1916-1": (
        "wrong victor: Bulgarian forces led the assault; Ottoman troops were absent"
    ),
    "hced-Ushant1794-1": "duplicate of the Glorious First of June 1794",
    "hced-Valmy1792-1": "wrong principal opponent: the field army was Prussian",
    "hced-Vauchamps1814-1": (
        "wrong belligerent: the defeated force was Russian-Prussian, not Austrian"
    ),
    "hced-Verdun1792-1": "wrong belligerent: the siege was conducted by Prussian forces",
    # ---- Funnel-ranked identity tranche (greedy batch ranks 1-20) ----
    "hced-Keniera1882-1": (
        "inverted outcome: HCED codes the French side as winner but Keniera "
        "fell to Samori Ture on 21 February 1882 before the relief column "
        "arrived"
    ),
    "hced-Romani1916-1": (
        "incomplete coalition: the British 52nd (Lowland) Division of the EEF "
        "was a principal combatant omitted from the source's 'Australia, New "
        "Zealand' side"
    ),
    "hced-Strymon1185-1": (
        "duplicate of hced-Demetritsa1185-1: both rows encode the 7 November "
        "1185 destruction of the Norman field army on the Strymon"
    ),
    # ---- Audited state-polity tranche companion holds (2026-07-20) ----
    "hced-Altenkirchen (1st)1796-1": (
        "wrong actor: Duke Ferdinand of Wurttemberg commanded a Habsburg "
        "Austrian wing; Wurtemburg is a commander's title, not the belligerent polity"
    ),
    "hced-Pirna1813-1": (
        "wrong actor: Duke Eugene of Wurttemberg commanded a Russian-Allied "
        "formation; the Kingdom of Wurttemberg was not the defeated polity"
    ),
    "hced-Ypres1793-1": (
        "chronology and actor mismatch: the attested French siege of Ypres was "
        "in 1794 against a mixed Habsburg-Hessian garrison, not a France-Hesse dyad in 1793"
    ),
    "hced-Hormuz1507-1508-1": (
        "mixed-result campaign envelope: the 1507 Portuguese naval victory and "
        "tribute settlement were followed by Albuquerque's forced withdrawal in 1508"
    ),
    "hced-Mount Haemus981-1": (
        "unverified event: the cited gazetteer identifies the Haemus range but "
        "does not attest a discrete 981 Bulgarian victory at this location"
    ),
    "hced-Macassar1667-1668-1": (
        "incomplete coalition and campaign envelope: Bone and Soppeng were "
        "principal Dutch allies and the conquest continued through 1669"
    ),
    "hced-Surajgarh1530-1": (
        "chronology and identity mismatch: the battle is generally dated 1534, "
        "before the Sur Empire was established by the 1540 victory at Kanauj"
    ),
}


# Seed events are curated strategic envelopes. These three intentionally begin
# before a participant identity's formal entry year; every other seed-event
# participant must be fully contained by its identity interval.
SEED_EVENT_INTERVAL_EXEMPTIONS: dict[tuple[str, str], dict[str, Any]] = {
    ("american_revolutionary_war", "united_states"): {
        "event_interval": (1775, 1783),
        "entity_interval": (1776, None),
        "reason": (
            "the curated war envelope begins in 1775; the United States identity begins in 1776"
        ),
    },
    ("napoleonic_wars", "first_french_empire"): {
        "event_interval": (1803, 1815),
        "entity_interval": (1804, 1815),
        "reason": (
            "the curated coalition-war envelope begins in 1803; the Empire identity begins in 1804"
        ),
    },
    ("afghanistan_war_2001_2021", "islamic_republic_afghanistan"): {
        "event_interval": (2001, 2021),
        "entity_interval": (2004, 2021),
        "reason": (
            "the curated war envelope includes the 2001-2003 transition before the 2004 republic"
        ),
    },
}


# Conflict-scoped identity policies for curated non-state UCDP primary
# parties. Keyed (conflict_id, normalized side name) because UCDP org names
# collide across conflicts: the "PLA" of conflict 202 is the Chinese People's
# Liberation Army; the "PLA" of conflict 347 is the People's Liberation Army
# of Manipur, which must never resolve here. A policy party carries no GW
# code; its identity comes only from these windows (authoritative, no tier
# fallback), and the episode interval must fit fully inside one window.
# Windows are the actor identity's attested existence bounds with cited
# boundary sources - never the episode's activity span.
UCDP_ACTOR_PARTY_POLICIES: dict[tuple[str, str], tuple[tuple[int, int, str], ...]] = {
    ("202", "pla"): ((1927, 1949, "chinese_communist_forces"),),
    ("242", "m 26 7"): ((1955, 1959, "cuban_26_july_movement"),),
}


# Exhaustive declared mapping of UCDP type_of_conflict (values 1-4).
# An unmapped value is a NAMED rejection, never a silent fallback.
UCDP_WAR_TYPES: dict[str, str] = {
    "1": "colonial_anti_colonial",
    "2": "interstate_limited",
    "3": "civil_war",
    "4": "insurgency_intervention",
}


# Every declared rejection counter per promotion path, including gates that
# measure zero on the current snapshot: a zero gate is a declared guard, and
# the published artifact must distinguish "declared and measured zero" from
# "not implemented".
HCED_LABEL_REJECTION_COUNTERS: tuple[str, ...] = (
    "curated_row_exclusion",
    "label_outcome_not_aligned",
    "outside_continuity_policy",
    "no_unique_time_valid_polity",
    "blank_side_label",
    "faction_label_not_a_polity",
    "label_pending_identity_split",
    "label_outside_policy_window",
    "no_unique_time_valid_label_match",
    "same_or_empty_opposing_side",
    "duplicate_of_curated_seed",
    "duplicate_of_promoted_event",
)


IWBD_REJECTION_COUNTERS: tuple[str, ...] = (
    "curated_exclusion",
    "missing_battle_name",
    "missing_or_invalid_date",
    "missing_belligerent_label",
    "duplicate_within_iwbd",
    "duplicate_of_curated_seed",
    "duplicate_of_hced_battle",
    "malformed_candidate_id",
    "contains_constituent_iwbd_rows",
    "outcome_not_aligned_to_battle_sides",
    "coalition_or_composite_side",
    "unresolved_time_bounded_belligerent",
    "same_or_empty_opposing_side",
)


UCDP_REJECTION_COUNTERS: tuple[str, ...] = (
    "malformed_source_row",
    "not_terminal_episode",
    "outcome_peace_agreement",
    "outcome_ceasefire",
    "outcome_low_activity",
    "outcome_actor_ceased",
    "outcome_missing_or_unknown",
    "missing_or_invalid_episode_years",
    "nonstate_primary_party",
    "unresolved_time_bounded_party",
    "same_or_empty_opposing_side",
    "documented_side_attribution_dispute",
    "duplicate_of_promoted_strategic_event",
    "dyad_conflict_outcome_contradiction",
    "contradictory_linked_episode_outcomes",
    "unmapped_type_of_conflict",
)


# Explicit, time-bounded identity policies for UCDP Gleditsch-Ward codes whose
# label does not name the historical polity directly. A policy code is
# authoritative: outside its windows the party stays unresolved instead of
# falling back to name matching. Deliberate gaps: GW 365 omits 1918-1921 and
# 1992+ (revolutionary era and the post-Soviet federation have no curated
# identity); GW 816 omits post-unification years; GW 700 omits 1979-1995 and
# 2002-2003 because the DRA and the transitional administrations have no
# curated identity — Cliopatria's blanket "Afghanistan 1979-2024" polity would
# bridge four regimes, which namesake continuity rules forbid.
UCDP_GW_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "365": (
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
    "816": ((1945, 1976, "north_vietnam"),),
    "817": ((1955, 1975, "south_vietnam"),),
    "700": (
        (1996, 2001, "taliban"),
        (2004, 2021, "islamic_republic_afghanistan"),
    ),
    "160": (
        (1831, 1861, "argentine_confederation"),
        (1861, 1930, "argentine_republic_1861"),
        (1930, 2026, "clio_q414_1930_5e281b3e"),
    ),
    "355": (
        (1878, 1908, "principality_bulgaria"),
        (1908, 1946, "kingdom_bulgaria"),
    ),
    "652": (
        (1946, 1957, "clio_sy_syria_modern_1946_86597c89"),
        (1962, 2026, "clio_q41137_1973_b05dea50"),
    ),
    "751": ((1724, 1948, "hyderabad_asaf_jahi_state_1724"),),
}


# Curated exclusions for UCDP termination episodes with a documented
# side-attribution dispute: promoting the source's coding would assign a rated
# outcome to a polity that may not have fought. Ambiguity between time-bounded
# identities always stays staged for human review.
UCDP_CURATED_EXCLUSIONS: dict[tuple[str, str], str] = {
    ("334", "1"): (
        "side_attribution_dispute: UCDP codes the 1974 episode (Battle of the "
        "Paracel Islands) against the DRV (gwno 816, 'Government of Vietnam "
        "(North Vietnam)'), but historical accounts attribute the engagement "
        "to the Republic of Vietnam Navy (GW 817). Which registry identity "
        "opposed China is ambiguous between two time-bounded identities; "
        "ambiguity always fails. Staged for human review."
    ),
}


def _cow_policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    policies = IWD_COW_CODE_POLICIES.get(code)
    if not policies:
        return None
    matches = [
        entity_id
        for start_year, end_year, entity_id in policies
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def _label_policy_seed_id(label: str, low_year: int, high_year: int) -> str | None:
    matches = [
        entity_id
        for start_year, end_year, entity_id in HCED_LABEL_POLICIES.get(label, ())
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def _policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    policies = SEED_CODE_POLICIES.get(code)
    if not policies:
        return None
    matches = [
        entity_id
        for start_year, end_year, entity_id in policies
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def _gw_policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    matches = [
        entity_id
        for start_year, end_year, entity_id in UCDP_GW_CODE_POLICIES.get(code, ())
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None
