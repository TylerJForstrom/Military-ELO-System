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
| `prussia` | 1701-1871 Kingdom of Prussia | pre-1701; post-1871 | Brandenburg-Prussia stays staged; imperial-era forces fight under the German Empire identity. |
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
| `muslim caliphate` | 632-660 Rashidun Caliphate; 661-750 Umayyad Caliphate | after 750 | Era-correct split at the Umayyad accession; the Abbasid era resolves through its own Cliopatria identity. |

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
`turkey` (deny-windowed 1920-1923 and otherwise resolved by era-valid alias
matching), pre-1948 `israel`, and pre-1949 `china` — stay staged mechanically
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

### Identity deny windows: "Turkey", 1920-1923

Every label-resolution pipeline (HCED label pass, IWBD, IWD, UCDP) checks the
declared `IDENTITY_DENY_WINDOWS` table before consulting any resolver tier:
within a deny window the label never resolves, because it denotes an actor
distinct from the identity the resolver would return. The table was
originally IWBD-scoped and was renamed and lifted into the shared resolver so
one declaration covers every pipeline. Its single entry: the label "Turkey"
never resolves for events intersecting 1920-1923. In those years the label
denotes the Ankara (Grand National Assembly/Kemalist) government — a distinct
actor fighting in parallel with, and against the treaty of, the Istanbul
government — while the Ottoman Empire's 1299-1922 interval still covers the
span, so without the window the resolver would attach Kemalist-era battles
such as Sakarya 1921 to `ottoman_empire`, crossing a regime boundary exactly
as this policy forbids. The window claims no authority outside 1920-1923:
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

## Curated row exclusions (second reviewer pending)

Known wrong-actor, variant-spelling, and cross-source-duplicate records are
excluded by enumerated candidate ID with a documented reason, counted under a
curated-exclusion rejection counter in the owning pipeline, and never merged
or fuzzy-matched:

- **HCED coded pass (10):** five variant-spelling duplicates (Pandjeh 1885,
  Gustalla 1734, Truillas 1793, Juthas 1808, Libertwolkwitz 1813), three
  Herat-principality rows whose defender was not the Kabul emirate (1837-38,
  1856, 1863), one wrong-belligerent row (Alcacer do Sol 1158, which England
  did not fight), and one branch-misattribution (St Quentin 1557, fought by
  Habsburg Spain after Charles V's abdication).
- **HCED label pass (8):** four PAVN engagements mislabelled "Viet Cong" (Ia
  Drang 1965, both Con Thien 1967 rows, Hue 1968), three duplicates of
  promoted IWBD battles (Binh Gia 1964, Long Tan 1966, Khe Sanh 1967), and one
  mis-crosswalked participant (Nam Dong 1964, "Australia" coded as the Republic
  of Korea).
- **IWBD (5):** cross-source spelling-twin duplicates of HCED battles
  (Tembien 1 and 2 1936, Liebenau 1866, Dijon 3 1871, Velestino 1 1897).
- **IWD parents (2):** Italian Unification 1859 (fought by the Kingdom of
  Sardinia, which has no curated identity yet — the "Kingdom of Italy"
  envelope is not the 1859 actor) and Hungarian-Allies 1919 (fought
  principally by the Hungarian Soviet Republic; the available Hungary interval
  bridges the 1919 regime resets).
- **UCDP (1):** the 1974 Paracel Islands episode, documented above.

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
