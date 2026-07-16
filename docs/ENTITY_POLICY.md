# Historical entity and continuity policy

## Governing rule

The rating unit is a versioned historical polity or autonomous military actor, not a normalized country name. When standard historical works conventionally treat a polity or empire as new, it receives a new entity ID and starts at the 1500 prior with maximum uncertainty.

Predecessor and successor links never transfer rating points.

## Default decisions

A new entity is created when:

- historiography conventionally treats it as a new polity or empire;
- a state dissolves into successors;
- a merger creates a new sovereign polity;
- a secession creates a new actor;
- a conqueror-founded regime is conventionally treated as distinct;
- rival governments in a civil war field materially independent forces;
- a documented project override requires a split.

A new entity is not created solely for a monarch, dynasty, capital, translated name, ruling party or constitutional change unless historical convention treats the resulting actor as a new state or empire.

## Special cases

- **Secession:** the parent continues unless it dissolves; the secessionist starts new.
- **Personal union:** members remain separate unless military command, taxation and armed forces are genuinely integrated.
- **Vassals and clients:** rate separately when they field forces under materially autonomous command. The same troops cannot be credited twice.
- **Governments in exile:** continuity requires strong legal/historiographic support and forces still under that government.
- **Restoration:** reuse an ID only when scholarship conventionally treats it as restoration of the same polity; otherwise reset.
- **Civil-war victory:** the winning faction and resulting successor polity can be linked but are not automatically the same entity.
- **Changing sides:** use separate participation episodes, not two simultaneous coalition memberships.

## Source-label identity policies

Open datasets sometimes label a polity with a name that does not identify the
historical actor by itself. Those labels are resolved only through explicit,
time-bounded policies, never through loose name similarity:

- **COW code 365 ("Russia"):** resolves to the Russian Empire through 1917 and
  to the Soviet Union from 1922 through 1991. The 1918-1921 revolutionary years
  deliberately resolve to nothing, so wars against the early RSFSR stay staged
  rather than being attached to either neighboring identity. No rating crosses
  the 1917 or 1991 boundaries.
- **COW code 255 ("Germany"/"Prussia"):** resolves to the Kingdom of Prussia
  through 1870 and the German Empire from 1871. Brandenburg-Prussia before the
  1701 coronation stays staged.
- **COW code 300 ("Austria-Hungary"):** resolves to the Austrian Empire
  through 1866 and Austria-Hungary from the 1867 Compromise. No rating crosses
  1867 or 1918.
- **COW code 345 ("Yugoslavia"):** resolves to the Kingdom of Serbia for
  1882-1918 — the interval COW files label "Yugoslavia" before the South Slav
  state existed. Interwar and later Yugoslavia have no curated identity and
  stay staged.
- **COW code 100 ("Colombia"):** resolves to the United States of Colombia for
  1863-1885 only. The broader `Colombia` label is deliberately not an alias,
  so neighboring regimes do not inherit this federal identity's rating.
- **COW code 670 ("Saudi Arabia"):** resolves to the Kingdom of Saudi Arabia
  from 1932 through the current 2026 source snapshot. Earlier Arabian polities
  stay staged rather than being folded into the kingdom.
- **COW code 678 ("Yemen Arab Republic"):** resolves to the Mutawakkilite
  Kingdom of Yemen for 1918-1961 only. The policy stops before the 1962 coup
  and does not bridge into the republican regime.
- **Seshat code `mx_mexico_1` and the bare label `mexico`:** resolve to the
  Mexican Republic for 1824-1863 and to the reviewed modern Mexican series
  from 1868. The years 1864-1867 are a global deny window shared by every
  label pipeline, preventing the French Intervention and Second Mexican Empire
  from being flattened into either republic.
- **The label "France":** resolves through six approved windows — the Kingdom
  of France (987-1792), the French First Republic (1793-1803), the First
  French Empire (1804-1815), the Second French Empire (1852-1870), the French
  Third Republic (1870-1940), and the French Fifth Republic (1958-present) —
  each a separate curated identity that starts at the baseline like every new
  polity. The years 1816-1851 (Bourbon Restoration, July Monarchy, Second
  Republic) and 1941-1957 (Vichy, Free France, Fourth Republic) are deliberate
  gaps with no curated identities, so labels naming France in those years stay
  unresolved rather than being attached to a neighboring identity. Events
  dated only "1870" fit inside both the Second Empire and Third Republic
  windows, are therefore ambiguous by full-interval containment, and
  deliberately fail.

### HCED label policies (second reviewer pending)

The HCED label-resolution pass resolves a small set of bare side labels through
the authoritative policy table below. A policy label must fit fully inside
exactly one window or it fails, with no fallback to alias matching. Assigning a
bare label to these windows is an entity-boundary decision under the review
workflow's high-impact rule: every entry below requires a second reviewer, and
the release stays labelled provisional pending that sign-off.

An explicit post-1500 comma, semicolon, or ampersand may describe a coalition
rather than one label. Such a side resolves only when every member independently
passes this same ordinary label resolver for the full interval and produces a
distinct identity; plain `and` is never a delimiter. Resolved members are then
canonicalized through the shared audited supersession inventory, so a source
envelope cannot re-enter the ledger through a composite spelling. The rule has
no pre-1500 path and therefore cannot modify the frozen ancient cohort.

State polity labels:

| Label(s) | Approved windows | Deliberately absent | Decision rationale |
|---|---|---|---|
| `france` | 987-1792 Kingdom of France; 1793-1803 French First Republic; 1804-1815 First French Empire; 1852-1870 Second French Empire; 1870-1940 French Third Republic; 1958-present French Fifth Republic | 1816-1851; 1941-1957; the bare year 1870 (ambiguous between two windows) | Six era-correct windows over the curated French identities, with explicit gaps for the Restoration/July Monarchy/Second Republic and Vichy/Fourth Republic eras. |
| `russia` | 1721-1917 Russian Empire; 1922-1991 Soviet Union | pre-1721 Tsardom; 1918-1921 | Mirrors the COW-365 policy above. Also closes a measured observation-tier hazard: a crosswalk mis-pairing had "Russia" observed against a Crimean Khanate candidate. |
| `spain` | 1479-1898 Spanish Empire | outside that window | Mirrors the Spanish Empire code windows and prevents a measured parallel identity: without it, "Spain" resolves to Cliopatria's "Kingdom of Spain" (1516-2024) candidate alongside the curated `spanish_empire` seed, giving one polity two rating identities. |
| `rome`, `romans` | 509 BCE-27 BCE Roman Republic; 27 BCE-394 CE Roman Empire | 395 CE onward | Follows the project's 395 Rome/Byzantium convention. The boundary year 27 BCE is ambiguous by full-interval containment and deliberately fails. |
| `byzantium`, `byzantines` | 395-1453 Byzantine Empire | before 395 | The other half of the 395 convention; no rating crosses the split. |
| `persia` | 550 BCE-330 BCE Achaemenid Empire; 224-651 Sasanian Empire; 1501-1736 Safavid Empire; 1737-1747 Afsharid Iran; 1794-1925 Qajar Iran | Seleucid/Parthian era; 652-1500; the Zand era (1748-1793); post-1925 Pahlavi Iran | The five curated Persian identities resolve era-correctly. The Afsharid window starts 1737 so 1736 events keep the committed Safavid attribution; the Zand interregnum stays staged. |
| `ottomans` | 1299-1922 Ottoman Empire | after 1922 | The collective label maps to the single continuous Ottoman identity within its own interval. |
| `austria`, `habsburg empire` | 1556-1803 Habsburg Monarchy; 1804-1866 Austrian Empire; 1867-1918 Austria-Hungary | 1526-1555; post-1918 | Until Charles V's abdication the label is ambiguous between the dynasty's Danubian and Spanish branches, so windows begin 1556 and 1526-1555 rows stay staged. The First Republic and later Austria stay staged. |
| `austria hungary` | 1804-1866 Austrian Empire; 1867-1918 Austria-Hungary | outside | Source rows sometimes apply the Dual-Monarchy name to pre-Compromise events; the split keeps each row era-correct. |
| `england` | 927-1648 and 1661-1706 Kingdom of England | 1649-1660 Interregnum; 1707 onward | The Commonwealth and Protectorate are conventionally a distinct republic (mirroring the French First Republic reset) and await a curated identity; the United Kingdom begins 1707 and inherits no rating. |
| `scotland` | 843-1706 Kingdom of Scotland | 1707 onward | Ends at the Acts of Union. |
| `prussia` | 1701-1870 Kingdom of Prussia; bare 1871 German Empire | pre-1701; post-1871 | Year-only sources cannot split the 18 January 1871 proclamation, so all bare-1871 records use the German Empire in agreement with COW code 255. Later labels that still say Prussia stay staged. |
| `poland` | 1569-1795 Polish-Lithuanian Commonwealth; 1918-1939 Second Polish Republic | medieval Poland; 1796-1917; post-1939 | The partitions era and the People's Republic have no curated identities. |
| `sweden` | 1523-present Kingdom of Sweden | pre-1523 | The modern kingdom from Gustav Vasa; medieval and Kalmar-era Sweden stays staged. This policy replaces the former pending-split quarantine of the bare label. |
| `denmark` | 1523-present Kingdom of Denmark | pre-1523 | Same Kalmar-dissolution boundary as Sweden; the Danish-Norwegian personal union is not a separate rating identity. |
| `venice` | 697-1797 Republic of Venice | after 1797 | A single continuous institution per the long-envelope audit convention, ending at Napoleon's abolition. |
| `korea` | 1392-1897 Joseon | 1897 onward | The Korean Empire, the colonial era, and the modern Korean states have no curated identities. |
| `afghanistan` | 1747-1822 Durrani Empire; 1823-1926 Emirate of Afghanistan | pre-1747; 1927 onward | The Hotak era and the post-1926 Kingdom and republics stay staged (the UCDP GW-700 policy covers the modern windows separately). |
| `marathas`, `maratha empire` | 1674-1818 Maratha Confederacy | post-1818 | Princely successor states (Gwalior, Indore, Baroda) stay staged. |
| `mysore` | 1572-1799 Kingdom of Mysore | post-1799 | The Hyder Ali/Tipu Sultan takeover is a dynastic change within one polity; the post-1799 princely state stays staged. |
| `punjab` | 1799-1849 Sikh Empire | outside | The pre-1799 misl confederacy stays staged. |
| `transvaal` | 1852-1902 South African Republic | outside | The 1877-1881 British annexation is treated as an interruption of the same polity, not a reset. |
| `mahdists`, `mahdiyya`, `the mahdiyya`, `sudanese mahdists`, `sudanese islamists` | 1881-1899 Mahdist State | outside | Muhammad Ahmad's proclamation through the successor regime's defeat; the existing rated Mahdist identity is retained rather than forking its Elo history. |
| `argentina` | 1831-1861 Argentine Confederation; 1861-1930 post-Pavon Argentine Republic; 1930-present modern Argentine Republic | outside; bare 1861 and 1930 | The adjacent windows overlap deliberately at Pavon and the coup, so year-only transition records resolve to neither identity. |
| `bulgaria` | 1878-1908 Principality of Bulgaria; 1908-1946 Kingdom of Bulgaria | outside; bare 1908 | The declaration-of-independence year is shared by both windows and therefore fails the unique-window rule at year precision. |
| `texas`, `texan rebels` | 1836-1845 Republic of Texas | outside | The entity extends through 1846, but the generic policy stops after the last complete pre-transfer year; pre-independence rebels and the annexation-transfer year stay staged. |
| `syria` | 1946-1957 Second Syrian Republic; 1962-present Syrian Arab Republic | 1958-1961 United Arab Republic | The union with Egypt is a distinct command identity and a deliberate gap; the post-UAR series restarts from the normal prior. |
| `muslim caliphate` | 632-660 Rashidun Caliphate; 661-750 Umayyad Caliphate | after 750 | Era-correct split at the Umayyad accession; the Abbasid era resolves through its own Cliopatria identity. |
| `macedonia` | 336-323 BCE Macedonian Empire | outside | Exact source-label policy for Alexander's reign; it does not turn the generic label into a resolver alias. |
| `ummayyad caliphate` | 661-750 Umayyad Caliphate | outside | Exact upstream misspelling, constrained to the same historical interval as the canonical identity. |
| `mamluks` | 1250-1517 Mamluk Sultanate | outside | Exact collective source label for the sultanate; later Mamluk forces do not inherit the identity. |
| `dutch rebels` | 1568-1795 Dutch Republic | outside | Exact source label for the Dutch Revolt and continuing republic, with no generic rebel fallback. |
| `untied kingdom` | 1707-2026 United Kingdom | outside | Exact upstream typo, bounded by the current source snapshot and never generalized into typo correction. |

Non-state actor labels (see the non-state actor policy below):

| Label(s) | Approved windows | Decision rationale |
|---|---|---|
| `royalists` | 1642-1651 Royalist Forces (Wars of the Three Kingdoms) | Migrated off the faction blocklist to a curated belligerent identity. |
| `parliamentarians` | 1642-1651 Parliamentarian Forces (Wars of the Three Kingdoms) | Same war, opposing curated belligerent. |
| `taiping` | 1851-1864 Taiping Heavenly Kingdom | Rebel proto-state with unified command and attested boundaries. |
| `chinese communists` | 1927-1949 Chinese Communist Forces | Nanchang uprising to the proclamation of the PRC; the PRC inherits no rating. |
| `carlists` | 1833-1840 Carlist Forces (First Carlist War) | Later Carlist risings are separate movements with no policy windows. |
| `greek rebels` | 1821-1829 Greek Revolutionary Forces | The revolutionary belligerent of the War of Independence; the 1832 Kingdom is a separate identity. |
| `mexican liberals` | 1857-1861 Mexican Liberal (Constitutionalist) Forces | War of the Reform belligerent. |
| `mexican conservatives` | 1857-1861 Mexican Conservative Forces | War of the Reform belligerent; French-Intervention-era collaboration is outside the identity. |
| `spanish republicans` | 1936-1939 Second Spanish Republic | Resolves to the incumbent state identity created under the actor tranche's carve-out. |
| `spanish nationalists` | 1936-1939 Spanish Nationalist Faction | Insurgent belligerent; its succession into Francoist Spain transfers no rating. |
| `viet cong` | 1960-1976 National Liberation Front of South Vietnam | Materially distinct fielded force from the PAVN; PAVN engagements mislabelled "Viet Cong" are curated exclusions, not absorbed. |
| `cuban rebels` | 1868-1878 Cuban Insurgent Army; 1895-1898 Cuban Liberation Army; 1955-1959 26th of July Movement | Three separate risings, three separate identities; namesake continuity is forbidden. |

Labels deliberately **not** given policy entries — for example `netherlands`
(resolves through the curated Dutch Republic's alias for 1568-1795 only),
`turkey` (deny-windowed 1919-1923 and otherwise resolved by era-valid alias
matching), `mexico` (deny-windowed 1864-1867 and otherwise resolved by the
time-valid code/alias policy), pre-1948 `israel`, and pre-1949 `china` — stay staged mechanically
until curated identities exist.

### Faction and collective-peoples labels never resolve

Faction, party, and movement labels (for example kuomintang, mujahideen,
vendeen rebels) and collective-peoples labels (for example vikings, tatars,
mongols, saxons, huns, goths, normans) are not time-bounded polities, so they
are held in a declared blocklist that is checked before any alias matching.
This ordering matters: several such labels collide with records in the polity
file (Cliopatria carries a "Kuomintang" party record and a "Viking
settlements" record), and without the front-gate they would resolve through
exact alias matches. Promoting a blocklisted label requires an explicit policy
entry mapping it to a curated identity, as was done for `romans` and — under
the non-state actor tranche — for seven labels migrated off the blocklist to
authoritative policy windows (`royalists`, `parliamentarians`, `taiping`,
`carlists`, `chinese communists`, `spanish nationalists`, `spanish
republicans`). Seven newly measured faction and collective labels took their
places (`cristinos`, `irish rebels`, `mexican rebels`, `russian whites`,
`white russians`, `seminole indians`, `vendeen rebels`), keeping the blocklist
at eighty entries; `vendeen rebels` stays blocked because resolving it is a
future-tranche decision, not because the label is undatable. The label
"confederate states of america" is deliberately not blocklisted: the CSA is a
time-bounded belligerent polity, and the blocklist holds labels naming
factions or peoples, not secessionist states.

### Polity labels pending identity splits

Four genuine polity names — `georgia`, `champa`, `switzerland` (with
`swiss confederation`), and `tibet` — never resolve, under their own counter,
because their only time-valid Cliopatria identity is a multi-regime envelope:
full-interval containment is vacuous against a candidate spanning many
conventional regime boundaries, so resolving them would manufacture rating
continuity across exactly the resets the curated side of the ledger enforces.
Per-label rationale:

- **Georgia** (567-2024): medieval kingdom through modern republic.
- **Champa** (207-1652): a 1,445-year envelope over successive Cham polities.
- **Switzerland** ("Swiss Confederation", 1294-2024): crosses the 1798
  Helvetic reset.
- **Tibet** (1363-1952): Phagmodrupa through Ganden Phodrang regimes.

These labels await curated identity splits; they are not faction labels.
`sweden` left this list when the curated Kingdom of Sweden identity (1523-
present) and its label policy were adopted: historiography treats the
post-Vasa kingdom as one continuing state, so the envelope objection no
longer applied.

### Retained long-envelope identities (audit note)

Every accepted long-envelope (over 450-year) resolution was individually
reviewed and retained as a single continuous polity or institution, with its
accepted events confined within one era: the Papal States (755-1870), the
Principality of Wallachia (1314-1858), the Principality of Moldavia
(1363-1858), the Abbasid Caliphate (750-1259), and the Zhou-era states Qi,
Qin, and Chu. Norway required no quarantine: the two candidates carrying the
`norway` alias are era-distinct (866-1401 and 1814-2024), so each event
resolves to the candidate containing its own span and no single identity
bridges regimes. Two long institutions entered the curated seed under the
same single-continuous-institution convention: the Republic of Venice
(697-1797) and Joseon (1392-1897), each retained deliberately rather than by
envelope accident.

### UCDP Gleditsch-Ward code policies

UCDP termination promotion resolves state parties through the approved
time-bounded `UCDP_GW_CODE_POLICIES` table. Like the COW-code policies, these
are authoritative: a coded party must fit fully inside exactly one window or
resolution fails outright, and the absent windows are deliberate.

- **GW 365 ("Russia"):** Russian Empire 1721-1917; Soviet Union 1922-1991.
  Deliberately absent: 1918-1921 (revolutionary era) and 1992 onward (the
  post-Soviet Russian Federation has no curated identity).
- **GW 816 ("Vietnam (North Vietnam)"):** North Vietnam 1945-1976.
  Deliberately absent: 1977 onward — the code is authoritative and never falls
  back to label matching, so post-unification episodes carrying GW 816 (for
  example China-Vietnam 1978-1981) fail outright and stay staged until a
  curated unified-Vietnam identity exists.
- **GW 817 ("South Vietnam"):** South Vietnam 1955-1975.
- **GW 700 ("Afghanistan"):** Taliban (Islamic Emirate) 1996-2001; Islamic
  Republic of Afghanistan 2004-2021. Deliberately absent: 1979-1995 and
  2002-2003 — Cliopatria's blanket "Afghanistan 1979-2024" polity bridges the
  DRA, the mujahideen government, the Islamic Emirate, the Islamic Republic,
  and the restored Emirate, and namesake continuity is forbidden, so the
  Soviet-invasion-era government stays unresolved.

### Curated exclusion: UCDP conflict 334, episode 1 (Paracel Islands, 1974)

UCDP codes the 1974 Battle of the Paracel Islands episode against the DRV
(GW 816, "Government of Vietnam (North Vietnam)"), but historical accounts
attribute the engagement to the Republic of Vietnam Navy (GW 817). Which
registry identity opposed China is ambiguous between two time-bounded
identities, and ambiguity always fails: the episode is held on a curated
exclusion list and stays staged for human adjudication, which may re-side the
record or confirm UCDP's coding. Promoting the source's coding while
footnoting the dispute would assign a rated defeat to a polity that likely did
not fight the battle.

### Identity deny windows: "Turkey", 1919-1923

Every label-resolution pipeline (HCED label pass, IWBD, IWD, UCDP) checks the
declared `IDENTITY_DENY_WINDOWS` table before consulting any resolver tier:
within a deny window the label never resolves, because it denotes an actor
distinct from the identity the resolver would return. The table was
originally IWBD-scoped and was renamed and lifted into the shared resolver so
one declaration covers every pipeline. Its single entry: the label "Turkey"
never resolves for events intersecting 1919-1923. From the May 1919 opening
of the Greco-Turkish fighting the label denotes the nationalist/Kemalist
movement and then the Ankara government — a distinct actor fighting in
parallel with, and against the treaty of, the Istanbul government — while
the Ottoman Empire's 1299-1922 interval still covers the
span, so without the window the resolver would attach Aydin 1919 and Sakarya
1921 to `ottoman_empire`, crossing a regime boundary exactly as this policy
forbids. The window claims no authority outside 1919-1923:
post-1924 "Turkey" labels resolve to the Republic of Turkey identity.

## Curated state identity tranche (second reviewer pending)

Thirty-four curated state identities were adopted in one reviewed tranche so
that bare labels and orphaned source codes resolve era-correctly instead of
staying staged or attaching to multi-regime Cliopatria envelopes. Every entry
starts at the baseline, inherits nothing, and is an entity-boundary decision
under the high-impact review rule: the tranche remains second-reviewer-pending
and the release stays labelled provisional.

| Identity | Window | Boundary rationale |
|---|---|---|
| French First Republic | 1792-1804 | Fall of the monarchy to the proclamation of the Empire; label windows use 1793-1803 so boundary years stay with the committed conventions. |
| Second French Empire | 1852-1870 | Proclamation to Sedan; the Second Republic (1848-1852) is a deliberate gap. |
| French Third Republic | 1870-1940 | 4 September 1870 to the vote of full powers to Petain; bare "1870" stays staged as ambiguous. |
| Habsburg Monarchy | 1526-1804 | Ferdinand I's Bohemian/Hungarian election to the proclamation of the Austrian Empire; label and code windows begin 1556 because the label is branch-ambiguous until Charles V's abdication, and 1526-1555 rows stay staged. |
| Austrian Empire | 1804-1867 | Proclamation to the Compromise. |
| Austria-Hungary | 1867-1918 | The Dual Monarchy to dissolution; successor republics inherit nothing. |
| Kingdom of Prussia | 1701-1871 | Coronation of Frederick I to the German Empire's proclamation. |
| Kingdom of England | 927-1707 | AEthelstan to the Acts of Union, with a deliberate 1649-1660 Interregnum gap in every window pending a curated Commonwealth identity. |
| Kingdom of Scotland | 843-1707 | Conventional MacAlpin founding (precision not implied) to the Acts of Union. |
| Kingdom of Sweden | 1523-present | Gustav Vasa's election; later constitutional changes are the same continuing kingdom by convention. |
| Kingdom of Denmark | 1523-present | Effective end of the Kalmar Union; the union with Norway is not a separate rating identity. |
| Polish-Lithuanian Commonwealth | 1569-1795 | Union of Lublin to the Third Partition. |
| Second Polish Republic | 1918-1939 | Independence to the German-Soviet invasion; the exile government and People's Republic inherit nothing. |
| Maratha Confederacy | 1674-1818 | Shivaji's coronation to the abolition of the Peshwa; supersedes the Cliopatria 1677-1845 envelope as the rating identity. |
| Kingdom of Mysore | 1572-1799 | Post-Vijayanagara consolidation to the fall of Seringapatam; the Hyder Ali/Tipu takeover is dynastic change, not a reset. |
| Sikh Empire | 1799-1849 | Ranjit Singh's Lahore to the British annexation. |
| Durrani Empire | 1747-1823 | Ahmad Shah's election to the fall of the Sadozais. |
| Emirate of Afghanistan | 1823-1926 | Barakzai rule through all three Anglo-Afghan wars; rival principalities of the fragmentation era are curated exclusions, not this identity. |
| Republic of Venice | 697-1797 | Traditional first doge (a convention) to Napoleon's abolition; a single continuous institution. |
| Afsharid Iran | 1736-1747 | Nader Shah's coronation to his assassination; the label window starts 1737 to keep 1736 events Safavid. |
| Qajar Iran | 1794-1925 | Agha Mohammad Khan's victory at Kerman to the Pahlavi accession; supersedes the Cliopatria "Qajar Dynasty" 1788-1923 interval. |
| Kingdom of Hungary | 1000-1526 | Stephen I to Mohacs and the kingdom's trisection. |
| Ethiopian Empire | 1855-1936 | Tewodros II's unification to the Italian occupation; earlier Solomonic eras and the 1941 restoration stay on other identities. |
| Egypt (Muhammad Ali dynasty) | 1805-1882 | Autonomous command under nominal Ottoman suzerainty, rated separately under the vassal rule, including against the Ottomans; ends at the British occupation. |
| South African Republic | 1852-1902 | Sand River Convention to Vereeniging; the 1877-1881 annexation is an interruption, not a reset. |
| Kingdom of Greece | 1832-1924 | Treaty of Constantinople to the Second Hellenic Republic. |
| Kingdom of Serbia | 1882-1918 | Proclamation to absorption into the South Slav kingdom; COW code 345 labels this interval "Yugoslavia". |
| Kingdom of Romania | 1881-1947 | Proclamation to the forced abdication of Michael I. |
| Joseon | 1392-1897 | The Yi kingdom to the proclamation of the Korean Empire; a single continuous institution. |
| Empire of Brazil | 1822-1889 | Independence to the republic; supersedes the identically-windowed Cliopatria interval as the rating identity. |
| Mexican Republic | 1824-1863 | The 1824 constitution to the French installation of the Second Empire; constitutional swings are one polity by convention. |
| Argentine Confederation | 1831-1861 | Federal Pact to Pavon and reunification. |
| Kingdom of Iraq | 1932-1958 | End of the British mandate to the 14 July revolution; no rating crosses 1958. |
| Republic of Lithuania | 1918-1940 | Independence to Soviet annexation; the Grand Duchy and the restored republic inherit nothing. |

Adopting the tranche changed exactly nineteen already-rated events by
enumerated identity supersession, with zero events removed: the 1822 Battle of
Khoi moved from the Cliopatria Qajar envelope to `qajar_iran`, and eighteen
Paraguayan-war events moved from the Cliopatria Brazil envelope to
`empire_brazil`. The registry absorbed forty source-candidate rows into the
forty-eight curated records (1,582 to 1,590 net). Two crosswalk-observation
pairings used by the label pass were individually reviewed and approved:
"north korea" observed against the DPRK candidate (ten resolved sides) and
"timurid empire" observed against the Timurid candidate (one resolved side).

### Wave 4 narrow state identity additions

Wave 4 adds three separately sourced identities needed by two IWD parent wars.
They start at the normal baseline, carry no predecessor rating, and intentionally
omit broad modern-country aliases:

| Identity | Window | Boundary rationale |
|---|---|---|
| United States of Colombia | 1863-1885 | The federal constitution through the 1886 constitutional replacement; no generic `Colombia` alias. |
| Kingdom of Saudi Arabia | 1932-present | Proclamation of the unified kingdom; the COW policy is additionally capped at the current 2026 source snapshot. |
| Mutawakkilite Kingdom of Yemen | 1918-1961 | Independence from Ottoman rule through the last full pre-coup year; no generic `Yemen` alias and no continuity into the republic. |

Two exact-name Cliopatria envelopes are absorbed by the normal overlap rule,
while the broader North Yemen envelopes remain separate. The three additions
therefore move the registry from the earlier tranche's 1,590 entries to 1,591
net in Wave 4, without widening a generic code or label resolver.

### Wave 5 era boundaries and reviewed identity contracts

Wave 5 adds explicit Portuguese regime boundaries and a canonical Tsardom of
Russia policy for the HCED tranche. All identities start from the normal prior;
no rating crosses a predecessor/successor boundary.

| Source label or code | Accepted complete-year windows | Rating identity |
|---|---|---|
| Portuguese kingdom/empire labels | 1147-1814 | Kingdom of Portugal (`kingdom_portugal`) |
| Portuguese kingdom/empire labels | 1816-1821 | United Kingdom of Portugal, Brazil and the Algarves (`united_kingdom_portugal_brazil_algarves`) |
| Portuguese kingdom/empire labels | 1823-1909 | Kingdom of Portugal (restored) (`kingdom_portugal_restored`) |
| Portuguese kingdom/empire labels | 1911-1925 | First Portuguese Republic (`portuguese_first_republic`) |
| Romanov/Russia labels | 1547-1720 | Tsardom of Russia (`clio_ru_moskva_rurik_dyn_1547_93deb0e2`) |
| Romanov/Russia labels | 1721-1917 | Russian Empire (`russian_empire`) |

The Portuguese identity records use the broader attested boundaries 1143-1814,
1815-1822, 1822-1910, and 1910-1926. The narrower source-policy windows leave
the year-only 1815, 1822, and 1910 transitions unresolved and avoid assigning
the First Republic's 1926 transition year. The independently dated 8 November
1822 Battle of Piraja is the sole exact candidate contract through the 1822
gap; a changed fingerprint fails closed. No event currently lands in the
1816-1821 union window, so that identity is a release record but has no rated
evidence. The Tsardom is curated onto the existing canonical Cliopatria ID;
there is deliberately no second `tsardom_russia` identity. Its rating ends
before the Russian Empire begins in 1721.

The strategic tranche uses complete, fail-closed source contracts rather than
broad country aliases. Eight IWD parents and 20 IWBD battles add exactly 28
events:

| Reviewed cohort | IWD | IWBD | Total |
|---|---:|---:|---:|
| Bourbon Restoration France / Spain, 1823 | 1 | 1 | 2 |
| Russian SFSR with first-republic Estonia or Poland | 2 | 0 | 2 |
| Turkish National Movement, 1919-1922 | 2 | 12 | 14 |
| Republic of China on Taiwan | 3 | 6 | 9 |
| Orleans / French Third Republic, 1870 | 0 | 1 | 1 |
| **Total** | **8** | **20** | **28** |

Each IWD contract pins a complete parent/component inventory and exact party
IDs. Each IWBD contract pins one complete candidate fingerprint and exact IDs
for both sides, and each named cohort is complete-or-fail. These bindings do
not become aliases. The Turkish National Movement contracts therefore do not
open the general `Turkey` resolver: all uncontracted Turkey records
intersecting 1919-1923 remain denied. The tranche adds separate identities for
Bourbon Restoration France, the Russian SFSR, the first Estonian republic,
and the Turkish National Movement; the Republic of China on Taiwan,
French Third Republic, Spain, Poland, Greece, and the other opposing identities
reuse their established canonical records.

After canonical consolidation, the reviewed Wave 7 identity splits, and the
crisp-boundary tranche, the pre-Wave 8 registry contained 1,701 identities.
Wave 8 adds 26 alias-free identity records, producing the current 1,727-row
registry. The release entity file contains 371 records, while 369 distinct IDs
actually participate in rated events. The unrated Portuguese union and
the superseded Free Orange State source envelope explain the two-record
difference; the Republic of Texas now participates through the reviewed Mexico
code-continuity path.

### Crisp state-identity tranche

The post-Wave 7 tranche reuses established IDs wherever a polity already has rated
evidence, rather than opening parallel Elo series. Its exact identity and
generic-policy boundaries are:

| Identity | Entity interval | Generic label/code behavior |
|---|---|---|
| Mahdist State | 1881-1899 | Mahdist labels resolve throughout 1881-1899. |
| Argentine Republic (post-Pavon) | 1861-1930 | `argentina` and COW/GW code 160 overlap the Confederation in 1861 and the modern republic in 1930, so both boundary years fail closed. |
| Principality / Kingdom of Bulgaria | 1878-1908 / 1908-1946 | `bulgaria` and COW/GW code 355 overlap at 1908, so a year-only 1908 record is ambiguous. |
| Republic of Texas | 1836-1846 | `texas` and `texan rebels` resolve only in complete years 1836-1845; 1846 stays staged. |
| Syrian republics | 1946-1957 / 1962-present | `syria`, Seshat's modern-Syria code, and COW/GW code 652 all preserve the 1958-1961 UAR gap; no rating crosses it. |

All five decisions use Britannica boundary references, start at the normal
prior, and transfer no rating across a predecessor, coup, monarchy, union, or
annexation boundary.

The Argentine windows do not authorize every newly resolvable row. Exact HCED
records remain excluded when they flatten Blanco/Colorado or Mexican faction
forces into a state, omit Brazil or Uruguay from the Triple Alliance, invert a
result, or duplicate a stronger event record. IWD parent 17 is also withheld:
its component dyads omit Uruguay, so they cannot support the complete
Argentina-Brazil-Uruguay coalition required by the parent-war rule.

### Wave 6 identity-bound contracts and holds

Wave 6 originally added 199 events through three candidate-keyed chronological lanes while
preserving every Wave 5 event payload. The modern lane initially proposed 90
events, but an independent boundary audit moved 22 exact contracts to
fingerprinted holds. The post-UAR Syrian identity now releases one exact 1967
IWBD contract, leaving 21 holds: 14 HCED rows involving post-1882 Egypt or
transitional Spanish governments, the 1948 IWD parent (still blocked by other
coalition identities), and six Egypt-linked 1967 IWBD rows. The build must not
widen `egypt_muhammad_ali` beyond 1882 or bridge Syria's 1958-1961 UAR gap. The First Balkan War row
reuses the already-rated, time-valid Montenegro identity instead of opening a
parallel series.

Five registry-only Cliopatria proposals for Genoa, Aragon, Castile, and the
Second Bulgarian Empire remain published with `identity_status: superseded`
and an exact `superseded_by` target. The two reused Bulgarian/Seljuk release
identities preserve their Cliopatria provenance and aliases. Supersession is
therefore explicit and reversible; no registry ID silently disappears.

### Wave 8 candidate-keyed identities and holds

Wave 8 admits 46 HCED rows through exact candidate contracts: 9 in the African-states lane, 15 in New Zealand, and 22 in North America. Each contract pins the complete queue row, event, time-bounded participants, and evidence set; the 26 added identities are alias-free, and no umbrella ethnonym passes identity or rating to a particular band, coalition, or successor. Four exact events use documented outcome overrides with their direct sources named. Sixteen massacre/noncompetitive or still-unresolved actor, coalition, and outcome records remain explicit fingerprinted holds rather than becoming inferred wins, losses, or draws.

## Non-state autonomous military actors (second reviewer pending)

The rating unit has always been a polity **or autonomous military actor**; this
policy makes the actor half operational. A non-state belligerent receives a
curated identity only when all of the following hold:

1. it fielded organized forces under materially unified, autonomous command in
   a conventional named conflict, rather than being an umbrella label over
   uncoordinated movements (labels for umbrella movements without unified
   command — for example `mujahideen` — stay blocked);
2. its start and end boundaries are conventionally attested events (a rising,
   a proclamation, a decisive defeat, a dissolution), not round-number guesses;
3. the identity never bridges separate risings that merely share a name —
   namesake continuity is forbidden, which is why the three Cuban insurgencies
   are three identities;
4. no rating transfers between the actor and any predecessor, successor state,
   or later movement, in either direction; and
5. the actor's label resolves only through an authoritative time-bounded
   policy window, never through alias matching.

Fourteen identities entered under this policy: the Royalist and
Parliamentarian forces of the Wars of the Three Kingdoms (1642-1651, with the
1650-1651 Scottish-raised army of Charles II and the 1649-1651 Commonwealth
tail kept inside the faction identities as declared contested-boundary
decisions), the Taiping Heavenly Kingdom (1851-1864), the Chinese Communist
Forces (1927-1949), the Greek Revolutionary Forces (1821-1832, including the
1821 Danubian campaign as a declared exception to the single-conflict
criterion), the Second Spanish Republic and Spanish Nationalist Faction
(1931/1936-1939), the Mexican Liberal and Conservative forces of the War of
the Reform (1857-1861), the National Liberation Front of South Vietnam
(1960-1976), the two nineteenth-century Cuban insurgent armies and the 26th of
July Movement, and the Carlist forces of the First Carlist War (1833-1840).

The Second Spanish Republic is a state, not a faction; it was created inside
the actor tranche under a declared incumbent-side carve-out (it reopens no
declared gap, it is the sole opposing side of a curated actor, and its
boundaries are conventionally attested). PAVN engagements that HCED labels
"Viet Cong" are held on the curated exclusion list rather than resolved to
either Vietnamese identity, so the two fielded forces stay distinct.

UCDP termination episodes may include a curated non-state actor as a primary
party only through conflict-scoped actor policies
(`UCDP_ACTOR_PARTY_POLICIES`): the key binds an actor label to one UCDP
conflict ID, and the window is the actor's attested existence bounds, so the
"PLA" of the Chinese Civil War (conflict 202) resolves to the Chinese
Communist Forces while the homonymous "PLA" of conflict 347 resolves to
nothing. The government side of such an episode must independently resolve.

## Curated row exclusions and historical adjudications

Known wrong-actor, wrong-outcome, variant-spelling, date-error, and duplicate
records are excluded by enumerated candidate ID with a documented reason,
counted under a curated-exclusion rejection counter in the owning pipeline,
and never merged, rewritten, or fuzzy-matched. The immutable source assertions
remain in `data/raw`; every exact ID and reason is emitted in release metadata.

- **HCED coded pass (172 policy entries; 164 current rejections):** exact
  candidate-ID exclusions cover wrong or omitted principal actors, reversed
  outcomes, duplicates, malformed campaign envelopes, unsafe umbrella
  identities, and records crossing declared identity resets. The foundational
  62 comprise 39 Wave 4 exclusions plus 23 Wave 5 Portugal, Tsardom, and
  boundary-cohort findings; later reviewed inventories extend that set. All 172
  entries are published in metadata, while 164 reach this rejection counter
  under the current mutually exclusive gate order.
- **HCED label pass (71):** exact candidate-ID exclusions cover the original
  PAVN/IWBD/crosswalk adjudications, historical-review exclusions, and later
  candidate-keyed review findings. The original 53 comprised eight early
  adjudications, 38 historical-review exclusions, and seven retained Wave 4
  candidates. All 71 reach the current label-pass counter.
- **IWBD (213):** exact exclusions include wrong outcomes, cross-source
  spelling-twin duplicates, campaign umbrellas, unresolved identity-boundary
  proposals, and rows reserved by later reviewed inventories. The foundational
  ten include Duppel/Dybbol 1849, five HCED spelling-twin duplicates, and the
  four Wave 5 Riga 2, Akbas, Summer Offensive, and Gediz findings.
- **IWD parents (19):** exact parent exclusions include wrong state actors,
  indefensible source outcomes, incomplete coalitions, and unresolved reviewed
  identity boundaries. The foundational three were Germany-Denmark 1848,
  Italian Unification 1859, and Hungarian-Allies 1919; parent 1 now promotes
  only through its exact reviewed Bourbon-Restoration contract.
- **UCDP (1):** the 1974 Paracel Islands episode, documented above.

Historical-review dispositions are explicit:

| Disposition | Records |
|---|---|
| Excluded: inverted or indefensible result | Brusilov Offensive; Coatit; Dembeguina; A Shau and Dong Xoai; Dragasani; Barcelona 1936; Kemmel; Kaiserswerth; Lvov; Parwan Durrah; Mojkovac; Brest 1513; St Augustine 1702; Kolberg 1760; and the lower-weight Rheims, Dardanelles 1654, Marstrand, Mewe, Arcis-sur-Aube, and Kehl assertions. |
| Excluded: wrong principal belligerent or Habsburg branch | Lepanto; Valmy, Verdun, and Longwy; Duppel; Kolberg 1774; Bautzen, Rippach, and First Mockern; Montmirail, Brienne, and Vauchamps; Messina; Trebizond; Hanoi; Cadore and Hadad; Grol and Maastricht; Tutrakan; Andalsnes; Kalat; Monte Grappa 1917/1918; Vittorio Veneto; Rosas 1645; and Isola del Giglio 1646. |
| Excluded: duplicate or incompatible granularity | Martinesti (Rimnik duplicate); Tournai (Pont-a-Chin duplicate); St Quentin 1914 (Guise duplicate); Changsha 1942II (duplicate of the 1941-42 Third Battle); Barcelona 1705-06 (envelope over the separately rated 1705 capture and the distinct 1706 defense); Nivelle Offensive (Aisne 1917 envelope); Ushant 1794 (First of June duplicate); and the Liaoshen, Huaihai, Beijing-Tianjin, Poland 1939, France 1940, Norway 1940, Sevastopol 1854-55, and Galicia 1914 campaign envelopes. |
| Excluded: date cannot support chronological rating | Trentino 1917, Kolin 1756, and Rocoux 1747. No replacement date is silently invented. |
| Wave 5 HCED proposal withheld before release | Dunamunde and Riga 1701; Lesnaya; Napue; Montijo; Altona; Bronnitsa; Punitz; Salvador 1638; Malacca 1606; Beachy Head 1707; Colonia do Sacramento 1735; Reval; Majadahonda; Elba/El Bodon; Campo Maior; Azov 1695-96; Salvador 1822-23; Aden 1513; Wofla; Marbella; Cadiz 1810-12; and Barrosa. The exact candidate IDs and reasons are emitted in metadata and summarized in the Wave 5 review record. |
| Retained in staging after Wave 4 review | Megalopolis 331 BCE and Jaxartes 329 BCE lack a fully adjudicated chronology or specific coalition identity; Antioch 1268 has an unresolved identity boundary; Mons 1572, Steenwijk 1592, and Abensberg 1809 omit principal co-belligerents; Amjhera 1728 has conflicting chronology. |
| Retained as provisional source assertions | Diamond Hill 1900 remains because HCED itself asserts a Boer success and all HCED outcomes are labelled provisional. Newbury/Gainsborough 1643, Bizani/Jannina, the two 1916 Isonzo rows, and Nieman River 1920 were adversarially refuted as project defects and remain unchanged. The Basing House range claim was also refuted: staging already preserves ranges. |
| Documented modeling limitation | Dyadic HCED rows can omit principal co-belligerents (for example Germany at Caporetto, France at Rossbach, the Polish-Lithuanian Commonwealth at Vienna, or the BEF at the Marne). Participants are not silently added without a curated composition source; these rows remain provisional pending a co-belligerent table. |

Three curated seed war envelopes intentionally begin before one participant's
formal identity entry year: American Revolutionary War/United States,
Napoleonic Wars/First French Empire, and Afghanistan War 2001-2021/Islamic
Republic of Afghanistan. They are enumerated exemptions checked by the build,
and each exemption pins the exact event and entity intervals so widening an
approved envelope also fails. Any fourth containment exception fails unless it
is explicitly documented.

## Rome and Byzantium project convention

This project implements the requested rule that the Byzantine Empire does not inherit Rome's rating. The v1 registry uses 395 CE as a practical split convention and records an explicit reset. There is no uncontested scholarly “Byzantine start” date, so 330, 395, 476 and 610 should be available as sensitivity alternatives in a mature release.

The decision record must say that this is a project convention, cite boundary sources, and retain predecessor/successor metadata without transferring any points.

## Required identity record

The production registry should contain:

```text
entity_id
canonical_name
aliases
polity_type
existence_start_low / best / high
existence_end_low / best / high
predecessor_ids / successor_ids
continuity_decision
rating_reset
boundary_sources
boundary_confidence
project_override_reason
external identifiers (Seshat, Wikidata, COW, GW, UCDP)
reviewer / reviewed_at / version
```

Name matching and automated source crosswalks may propose an identity link, but only an approved decision can enter rated data.
