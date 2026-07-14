from __future__ import annotations

"""Curated identity, exclusion, and rejection policies for release promotion."""

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
    "ru_romanov_dyn_1": ((1721, 1917, "russian_empire"),),
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
    "pl_poland_lithuania_commonwealth": ((1569, 1795, "polish_lithuanian_commonwealth"),),
    "pl_poland_lithuania_k": ((1569, 1795, "polish_lithuanian_commonwealth"),),
    "pl_polish_rep_1": ((1918, 1939, "second_polish_republic"),),
    "rs_serbia_k": ((1882, 1918, "kingdom_serbia"),),
    "sv_sweden_k_modern": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k_1": ((1523, 2026, "kingdom_sweden"),),
    "sv_swedish_k_2": ((1523, 2026, "kingdom_sweden"),),
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
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
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
}


# Faction, party, movement, and collective-peoples labels are not time-bounded
# polities (the rating unit is a versioned polity or autonomous military actor,
# never a peoples name). The blocklist is checked before every alias tier so
# these labels cannot resolve even when a source record carries a colliding
# alias; promoting one later requires an explicit HCED_LABEL_POLICIES entry
# mapping it to a curated identity.
HCED_FACTION_LABELS: frozenset[str] = frozenset({
    # war-faction / party / movement labels (royalists, parliamentarians,
    # taiping, chinese communists, spanish republicans/nationalists, and
    # carlists migrated to curated actor policies in HCED_LABEL_POLICIES)
    "indian rebels",
    "chinese nationalists", "kuomintang", "guomindang",
    "communists", "nationalists",
    "republicans", "loyalists", "rebels", "insurgents", "jacobites",
    "huguenots", "catholics", "protestants", "covenanters", "confederates",
    "unionists", "boxers", "whites", "reds", "bolsheviks", "mujahideen",
    "cristinos", "mexican rebels", "irish rebels", "vendeen rebels",
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


# Declared identity deny windows, enforced in every label-resolution pipeline:
# within a window the label is never resolved, because it denotes an actor
# distinct from the identity the resolver would return. "Turkey" in 1919-1923
# denotes the nationalist/Kemalist movement and then the Ankara government,
# fighting in parallel with the Istanbul government; it must not attach to the
# ottoman_empire identity
# whose interval still covers those years.
IDENTITY_DENY_WINDOWS: dict[str, tuple[tuple[int, int], ...]] = {
    "turkey": ((1919, 1923),),
}


# Curated row exclusions (second reviewer pending), mirroring
# UCDP_CURATED_EXCLUSIONS: enumerated, documented, counted under a
# curated-exclusion rejection counter in the owning pipeline, never merged
# and never fuzzy-matched.
HCED_CURATED_EXCLUSIONS: dict[str, str] = {
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
    "hced-Lepanto1571-1": (
        "wrong belligerent: the Danubian Habsburg monarchy did not fight at Lepanto"
    ),
    "hced-Maastricht1632-1": (
        "wrong principal belligerent: the Dutch States Army, not England and France, took Maastricht"
    ),
    "hced-Martinesti1789-1": "duplicate of Rimnik/Rymnik 1789 under the battlefield place name",
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
}


IWBD_CURATED_EXCLUSIONS: dict[str, str] = {
    "iwbd-13-5-51": (
        "wrong outcome at Duppel/Dybbol on 1849-04-13: Denmark, not Prussia, "
        "won the action"
    ),
    "iwbd-55-19-188": "duplicate of HCED Liebenau 1866 (spelling variant 'Liebnau')",
    "iwbd-58-20-268": "duplicate of HCED Dijon 1871 (IWBD 'Dijon 3')",
    "iwbd-76-28-346": "duplicate of HCED Velestino (1st) 1897 (IWBD 'Velestino 1')",
    "iwbd-127-49-877": "duplicate of HCED Tembien (1st) 1936 (IWBD 'Tembien 1')",
    "iwbd-127-49-879": "duplicate of HCED Tembien (2nd) 1936 (IWBD 'Tembien 2')",
}


IWD_CURATED_PARENT_EXCLUSIONS: dict[str, str] = {
    "5": (
        "Germany-Denmark 1848 asserts a Prussian strategic victory, but Denmark won the "
        "First Schleswig War; the source assertion stays staged rather than being inverted"
    ),
    "10": (
        "Italian Unification 1859: belligerent was the Kingdom of Sardinia; the "
        "'Kingdom of Italy' [587,1946] envelope is not the 1859 actor (identity pending)"
    ),
    "42": (
        "Hungarian-Allies 1919: fought principally by the Hungarian Soviet Republic; "
        "the [1919,1943] Hungary interval bridges the 1919 regime resets (identity pending)"
    ),
}


# HCED rows excluded from the label pass by curated adjudication:
# cross-source duplicates of already-promoted IWBD battles under name
# variants exact-key dedup cannot catch, one measured crosswalk error, and
# rows whose "Viet Cong" side labels PAVN engagements.
HCED_LABEL_CURATED_EXCLUSIONS: dict[str, str] = {
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
    "hced-Brest1513-1": "inverted outcome: Howard's English attack on Brest failed",
    "hced-Brienne1814-1": (
        "wrong belligerent: the action was fought against Russian and Prussian forces, not Austria"
    ),
    "hced-Cadore1508-1": (
        "wrong Habsburg branch: Maximilian's Imperial-Tyrolean army is coded as Spain"
    ),
    "hced-Coatit1895-1": "inverted outcome: Baratieri's Italian force defeated Ras Mengesha",
    "hced-Dardanelles1654-1": "inverted outcome: the first 1654 Dardanelles battle was Ottoman",
    "hced-Dembeguina1935-1": (
        "inverted outcome: Ethiopian forces won the Dembeguina Pass action"
    ),
    "hced-Dong Xoai1965-1": (
        "inverted outcome: Viet Cong forces overran Dong Xoai and mauled the relief force"
    ),
    "hced-Dragasani1821-1": (
        "duplicate source row with the same inverted Dragasani outcome"
    ),
    "hced-Huaihai1948-1": (
        "campaign envelope duplicates separately rated Huaihai component battles"
    ),
    "hced-Kalat1839-1": (
        "wrong actor: the defender was the independent Khanate of Kalat, not the Kabul emirate"
    ),
    "hced-Kehl1797-1": "inverted outcome: the French garrison capitulated to Austria",
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
    "hced-Marstrand-1": (
        "inverted outcome: Danish-Norwegian forces captured Marstrand and Carlsten"
    ),
    "hced-Mewe1626-1": "inverted outcome: the Battle of Gniew/Mewe was a Swedish victory",
    "hced-Mockern (1st)1813-1": (
        "wrong belligerent: Austria was neutral during the April action"
    ),
    "hced-Mojkovac1916-1": "inverted outcome: Montenegro won the defensive action at Mojkovac",
    "hced-Montmirail1814-1": (
        "wrong belligerent: Russian and Prussian corps, not Austria, fought at Montmirail"
    ),
    "hced-Parwan Durrah1840-1": "inverted outcome: Dost Mohammad's Afghan force won the action",
    "hced-Poland1939-1": (
        "campaign envelope duplicates separately rated invasion-of-Poland components"
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
