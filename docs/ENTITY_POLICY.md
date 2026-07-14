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
- **The label "France":** resolves through three approved windows — the
  Kingdom of France (987-1792), the First French Empire (1804-1815), and the
  French Fifth Republic (1958-present) — each a separate curated identity that
  starts at the baseline like every new polity. The years 1793-1803 and
  1816-1957 are deliberate gaps: the First and Second Republics, the Bourbon
  Restoration, the July Monarchy, the Second Empire, and the Third and Fourth
  Republics have no curated identities yet, so labels naming France in those
  years stay unresolved rather than being attached to a neighboring identity.

### HCED label policies (second reviewer pending)

The HCED label-resolution pass resolves a small set of bare side labels through
the authoritative policy table below. A policy label must fit fully inside
exactly one window or it fails, with no fallback to alias matching. Assigning a
bare label to these windows is an entity-boundary decision under the review
workflow's high-impact rule: every entry below requires a second reviewer, and
the release stays labelled provisional pending that sign-off.

| Label(s) | Approved windows | Deliberately absent | Decision rationale |
|---|---|---|---|
| `france` | 987-1792 Kingdom of France; 1804-1815 First French Empire; 1958-present French Fifth Republic | 1793-1803; 1816-1957 | No Cliopatria record carries the alias "france" (verified empty in the alias index), so this policy closes no leak; it formalizes the era-correct behavior for kingdom-of-France and First-Empire-era rows and adds the 1958-present window under one authoritative rule with explicit gaps. |
| `russia` | 1721-1917 Russian Empire; 1922-1991 Soviet Union | pre-1721 Tsardom; 1918-1921 | Mirrors the COW-365 policy above. Also closes a measured observation-tier hazard: a crosswalk mis-pairing had "Russia" observed against a Crimean Khanate candidate. |
| `spain` | 1479-1898 Spanish Empire | outside that window | Mirrors the Spanish Empire code windows and prevents a measured parallel identity: without it, "Spain" resolves to Cliopatria's "Kingdom of Spain" (1516-2024) candidate alongside the curated `spanish_empire` seed, giving one polity two rating identities. |
| `rome`, `romans` | 509 BCE-27 BCE Roman Republic; 27 BCE-394 CE Roman Empire | 395 CE onward | Follows the project's 395 Rome/Byzantium convention. The boundary year 27 BCE is ambiguous by full-interval containment and deliberately fails. |
| `byzantium`, `byzantines` | 395-1453 Byzantine Empire | before 395 | The other half of the 395 convention; no rating crosses the split. |
| `persia` | 550 BCE-330 BCE Achaemenid Empire; 224-651 Sasanian Empire; 1501-1736 Safavid Empire | Seleucid/Parthian era (329 BCE-223 CE, since the boundary years 330 BCE and 224 CE resolve to the adjacent windows); post-1736 Afsharid, Zand, and Qajar eras | Only the three curated Persian identities resolve; the interregna have no curated identities and stay staged. |
| `ottomans` | 1299-1922 Ottoman Empire | after 1922 | The collective label maps to the single continuous Ottoman identity within its own interval. |

Labels deliberately **not** given policy entries — for example `prussia` (no
curated Prussia seed identity exists; creating one is a seed decision, not a
promotion-rule decision), `netherlands`, `poland`, `denmark`, `scotland`,
`venice`, pre-1953 `egypt`, `afghanistan`, pre-1948 `israel`, `turkey`,
`england`, and pre-1949 `china` — stay staged mechanically until curated
identities exist.

### Faction and collective-peoples labels never resolve

Faction, party, and movement labels (for example royalists, parliamentarians,
taiping, kuomintang, mujahideen) and collective-peoples labels (for example
vikings, tatars, mongols, saxons, huns, goths, normans) are not time-bounded
polities, so they are held in a declared blocklist that is checked before any
alias matching. This ordering matters: several such labels collide with records
in the polity file (Cliopatria carries a "Kuomintang" party record and a
"Viking settlements" record), and without the front-gate they would resolve
through exact alias matches. Promoting any blocklisted label later requires an
explicit policy entry mapping it to a curated identity, as was done for
`romans`. The label "confederate states of america" is deliberately not
blocklisted: the CSA is a time-bounded belligerent polity, and the blocklist
holds labels naming factions or peoples, not secessionist states.

### Polity labels pending identity splits

Five genuine polity names — `sweden`, `georgia`, `champa`, `switzerland` (with
`swiss confederation`), and `tibet` — never resolve, under their own counter,
because their only time-valid Cliopatria identity is a multi-regime envelope:
full-interval containment is vacuous against a candidate spanning many
conventional regime boundaries, so resolving them would manufacture rating
continuity across exactly the resets the curated side of the ledger enforces.
Per-label rationale:

- **Sweden** ("Kingdom of Sweden", 980-2024): one identity spanning Viking-age
  chiefdoms, the Kalmar Union, the Swedish Empire, and the modern kingdom.
- **Georgia** (567-2024): medieval kingdom through modern republic.
- **Champa** (207-1652): a 1,445-year envelope over successive Cham polities.
- **Switzerland** ("Swiss Confederation", 1294-2024): crosses the 1798
  Helvetic reset.
- **Tibet** (1363-1952): Phagmodrupa through Ganden Phodrang regimes.

These labels await curated identity splits; they are not faction labels.

### Retained long-envelope identities (audit note)

Every accepted long-envelope (over 450-year) resolution was individually
reviewed and retained as a single continuous polity or institution, with its
accepted events confined within one era: the Papal States (755-1870), the
Principality of Wallachia (1314-1858), the Principality of Moldavia
(1363-1858), the Abbasid Caliphate (750-1259), and the Zhou-era states Qi,
Qin, and Chu. Norway required no quarantine: the two candidates carrying the
`norway` alias are era-distinct (866-1401 and 1814-2024), so each event
resolves to the candidate containing its own span and no single identity
bridges regimes.

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

### IWBD deny window: "Turkey", 1920-1923

IWBD promotion checks a declared deny window before consulting the resolver:
the label "Turkey" never resolves for events intersecting 1920-1923. In those
years the label denotes the Ankara (Grand National Assembly/Kemalist)
government — a distinct actor fighting in parallel with, and against the
treaty of, the Istanbul government — while the Ottoman Empire's 1299-1922
interval still covers the span, so without the window the resolver would
attach Kemalist-era battles such as Sakarya 1921 to `ottoman_empire`, crossing
a regime boundary exactly as this policy forbids. The window claims no
authority outside 1920-1923: post-1924 "Turkey" labels resolve to the Republic
of Turkey identity.

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
