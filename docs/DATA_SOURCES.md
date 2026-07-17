# Data sources and ingestion policy

Last verified: 2026-07-15.

This document records the datasets evaluated for the Military History Elo
system, what each source can establish, and what it cannot. The central rule is
that an extracted record is a candidate assertion, not an automatically rated
event. Entity identity, sides, participation roles, event scope, and outcomes
must be adjudicated before a record can move from `data/review` into the rated
dataset.

No known dataset contains every polity or military encounter in history.
Ancient, non-literate, non-European, defeated, small, and short-lived societies
are systematically under-recorded. Coverage and evidence confidence therefore
belong beside every rating.

## What counts as evidence of a win

The system separates three different questions:

- **Tactical:** who controlled the battlefield, achieved the immediate mission,
  preserved forces, or gained position in an engagement?
- **Operational:** who achieved the campaign objective, controlled the theater,
  sustained logistics, and retained initiative?
- **Strategic:** who achieved the political objective, changed territory,
  preserved sovereignty, obtained a durable settlement, and preserved usable
  military force?

A battle winner is not automatically the winner of its campaign or war. Deaths,
force size, duration, intensity, or the fact that an actor initiated an attack do
not by themselves identify a winner. A peace agreement, withdrawal, ceasefire,
government overthrow, unconditional capitulation, occupation, annexation, and
an actor merely falling below a fatality threshold are also different outcomes.

| Source | Contains a purported winner? | What it means | Direct rating input? |
|---|---|---|---|
| HCED | Usually | Encounter-level `Winner` and `Loser` labels | No. Treat as a tactical proposal pending entity, side, scope, and confidence review. |
| IWBD | Yes | Tactical victor under a strategic-objective standard; also attacker/defender and war-side role | Rated only as tactical engagements through the declared IWBD promotion rule; duplicates, campaign umbrellas, coalition labels, and unresolved identities stay staged. It does not establish the enclosing war's strategic outcome, and its war-level victor code is ignored. |
| IWD | Yes | Terminal component-war outcome from the initiator's perspective: victory, defeat, or draw | Rated only through parent-war coalition aggregation: at most one strategic update per parent conflict, with consistent sides, unanimous outcomes, and time-bounded identities; unresolved parents stay staged. |
| UCDP conflict/dyadic/GED/deaths | No | Actors, conflict type, intensity, events, and deaths | No. Intensity and fatalities are not victory labels. |
| UCDP Conflict Termination | Yes, for terminated episodes | Peace, ceasefire, government-side victory, non-state-side victory, low activity, or actor cessation | Rated only through the declared conflict-episode termination ruleset (victory codes 3/4, state primaries, time-bounded GW policies, cross-source dedup); all other rows stay staged. It is episode-level and may not describe every supporter or coalition participant, so secondary parties are recorded without outcomes. |
| Wikidata | Sometimes through `winner` (P1346) | A community-maintained sourced statement | No. Preserve statement references and qualifiers and verify against scholarly sources. |
| Cliopatria | No | Polity identity, time, relationships, and geography | Identity evidence only. |
| Pleiades / GeoNames | No | Place identity, aliases, and coordinates | Location evidence only. |
| COW war data | Yes | Participant-level coded war outcome and battle deaths | Permission-gated and still requires scope/participant review. |
| MIE | No general winner field | Directed military action, hostility, and fatality ranges | No. The codebook explicitly warns that an attacker may lose an attack. |
| ACLED | No | Political-violence event type, actors, location, and reported fatalities | No, and its terms make this project an unsuitable use without written authorization. |
| PA-X | No simple winner | Terms and provisions in peace agreements | Settlement evidence only and permission/reuse restricted. |
| DBpedia | Sometimes an extracted value | Automatically extracted Wikipedia assertions | Discovery only; lower priority than Wikidata. |
| Brecke Conflict Catalog | Not systematically | Participants, initiator where possible, dates, location, and fatalities | Gap discovery only; unfinished and no explicit reusable license. |

### Explicit source-family and outcome-role contract

Every released source now carries a stable `source_family_id` and explicit
`evidence_roles`. The family identifies a provenance and deduplication unit; it
does not by itself establish that two sources are independent or that either
supports a particular scored outcome. Mechanically promoted events identify
their exact direct subset in `outcome_source_ids` and repeat the corresponding
stable dependency families in `outcome_source_family_ids`. For legacy records
with neither event-level field, a generic `source_ids` link can count only when
the linked source explicitly includes `outcome` in `evidence_roles`; generic
roles are never unioned into an event that already has an explicit mapping.
Titles, URLs, publishers, source counts, and family labels are never used to
infer an outcome role.

The 1,413-source registry contains 831 sources carrying the direct outcome role
across 761 dependency families. Current event-level contracts select 721 of
those sources across 665 families. This maps 5,298 of 5,338 rated events:
5,074 HCED encounters, 64 IWD parent wars, 153 IWBD battles, and 7 UCDP
termination episodes. Of the mapped events, 4,959 cite one declared direct
outcome family and 339 cite between two and six. Family cardinality is an audit
fact, not automatic proof that the cited publications are independent.

The 40 curated seed events remain explicitly unmapped: their generic reference
URLs do not contain the claim-level outcome locator, edition/checksum context,
or citation-lineage review needed to say which source supports each scored
dimension. Future review may add paired event-level `outcome_source_ids` and
`outcome_source_family_ids`; the registry does not apply a blanket outcome role
to those manual references.

The negative roles are equally important. `hced_seshat_crosswalk` is an
identity crosswalk, both Cliopatria records are identity registries,
`ucdp_termination_dyad` is a same-family outcome consistency cross-check, and
curated/manual references remain pending claim-level locators. HCED's free-text
list of consulted sources is not a registered locator and adds no family.
Crosswalks, registry rows, dyad rows, components, mirrors, publisher pages, and
generic consulted references can supply provenance or checks without supplying
another outcome assertion.

## Open core sources

### Historical Conflict Event Dataset (HCED)

**Purpose:** the principal deep-history encounter inventory.

- Dataset record and DOI:
  <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6ZFC0V>
- Current data file:
  <https://dataverse.harvard.edu/api/access/datafile/13390255>
- HCED-to-Seshat crosswalk:
  <https://dataverse.harvard.edu/api/access/datafile/11018172?format=original>
- Dataverse metadata API, including current license:
  <https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/6ZFC0V>
- Peer-reviewed article:
  <https://doi.org/10.1177/00220027221119085>
- Current repository version: Dataverse 5.0, updated 2026-01-21. The
  principal file is labelled `HCED Data v3.csv`.
- Coverage: 8,881 encounters from 1468 BCE through 2003 CE.
- License: CC0 1.0.
- Publisher MD5 for the current CSV:
  `80f4e0631ed866a1ce4f59bc376783cb`.
- Workspace snapshot SHA-256:
  `92a22e49c20d02a1d7ecf3fbdbb5e3ca94b7327b7620ee79dd01909857805b79`.

Useful fields include `ID`, `Battle`, `Year`, modern `Country`, latitude,
longitude, `War`, `Participants`, `Winner`, `Loser`, `Participant 1`,
`Participant 2`, `Lehmann Zhukov Scale`, `Theatre`, `Massacre`, inferred
scale, and alternative sources consulted.

In this system HCED creates engagement candidates. Its winner and loser are
tactical proposals only. `Country` is retained, when publishable, as the exact
source-transcribed geographic-jurisdiction label
`modern_location_country`; it is neither a historical participant polity nor
normalized sovereign-country truth. HCED has no consistently usable
participant-level casualty field, so its scale must not be interpreted as a
casualty ratio or decisiveness score.

For the 5,074 rated HCED events, the release-to-candidate join is an
exact bijection: 1,887 crosswalk-resolved events, 2,423 label-resolved events,
and 764 candidate-keyed reviewed events: 76 from Wave 6, 192 from Wave 7, and
496 from Wave 8, with no missing, ambiguous, or colliding bindings.
Candidate-ID-only policy manifests withhold 340 Point fields and 94
country/jurisdiction fields, with 46 overlapping and 388 unique
quarantine-manifest events. One additional rated candidate has a source-blank
country. After fail-closed quarantine, 4,734 events carry an exact
source-transcribed Point, 4,979 carry the source's modern
country/geographic-jurisdiction string, and 5,028 carry at least one location
field plus closed provenance. Of 49 separately reviewed disputed or
non-sovereign jurisdiction rows, 46 are deliberately retained verbatim and 3
are already withheld under independent quarantine criteria. They are source
geography labels, not sovereignty determinations. Every published value remains
an `unreviewed_source_assertion` with `coordinate_precision: unknown`;
verified historical-location coverage is unavailable. Quarantined values are
withheld rather than corrected, swapped, normalized, inferred,
reverse-geocoded, or exposed through release provenance.
The frozen 49-row jurisdiction review contract has SHA-256
`b209a0cc8d308d56d74012b53ea72bd29df34c4ac8a773b3602b38558c085b5e`.

The HCED label pass also recognizes an explicitly delimited coalition on
post-1500 rows. It splits only commas, semicolons, and ampersands—never plain
`and`—and accepts the side only when every member independently resolves to a
distinct identity valid for the whole interval. The shared canonical
supersession remap runs before coalition assembly. The current release contains
21 such events dated 1658–1983, including four Boer-War composites whose
Orange Free State member is canonicalized to `orange_free_state_1854`; zero
pre-1500 rows enter through this path. The current exact HCED label-exclusion
inventory contains 71 candidate IDs; failed spot-checks stay staged rather
than being repaired implicitly by coalition splitting.

Wave 8 uses only candidate-keyed exact contracts: every queue-row hash, event,
date, side, time-bounded entity ID, and evidence set is pinned. The contracts
create no broad aliases and never let an umbrella ethnonym confer identity or
rating on a particular group. Four exact events use documented outcome
overrides with their direct sources named; massacre/noncompetitive assertions
and rows with unresolved exact actors, coalitions, or outcomes remain explicit
fingerprinted holds rather than inferred competitive results.

HCED's `mx_mexico_1` code resolves to `mexican_republic` for 1824-1863 and to
the reviewed modern Mexican series for 1868-2024 in the current Cliopatria
snapshot. A shared `mexico` deny window
covers 1864-1867, so coded, bare-label, and composite-member paths cannot use a
broad alias to bridge the Reform/Second Empire boundary. This continuity rule
does not override event review: the current global coded-pass policy inventory
contains 172 exact candidates, of which 164 reach the `curated_exclusion`
counter under current gate ordering; the label-pass inventory and counter both
contain 71.

#### Verified live HCED profile

The snapshot downloaded on 2026-07-13 was parsed locally:

- 17,762 physical data rows: 8,881 rows with an `ID` and 8,881 placeholder
  rows without one.
- 8,881 encounter records but only 8,878 unique `ID` values; three IDs are
  duplicated.
- 8,853 records have a nonblank winner and 8,606 have a nonblank loser.
- 4,883 have a directly coded Lehmann-Zhukov scale and 870 have an inferred
  scale value.
- 184 records contain a year range, such as `1825-1826`, rather than one
  integer year.
- The single-year values span `-1468` through `2003`.
- There are 11 raw theatre strings, including whitespace and spelling variants
  that normalize to a smaller set such as land, sea, air, and combinations.
- Participant strings are serialized lists and can contain locations, campaigns,
  demonyms, or other non-polity text.

The 2026-07 historical-adjudication pass therefore stages enumerated HCED
assertions with verified inverted outcomes, wrong principal belligerents,
date errors, or duplicate campaign/battle granularity. Raw HCED rows are never
edited; candidate IDs and reasons are counted in release metadata, with the
full disposition groups documented in `ENTITY_POLICY.md`. Diamond Hill 1900
and the six adversarially refuted project-defect claims remain provisional
source assertions rather than being silently "corrected." Dyadic rows that
omit co-belligerents remain a documented source-model limitation pending a
curated composition table. A post-fix same-name/year collision sweep also
staged `Changsha1942II` as a duplicate of the 1941-42 Third Battle of
Changsha and the `Barcelona, Spain1705-1706` envelope, which conflates the
separately represented 1705 capture with the distinct 1706 defense.
The chronology was cross-checked against the Republic of China Ministry of
National Defense's [Third Battle of Changsha history](https://www.mnd.gov.tw/en/informationservices/publication/69595)
and Barcelona City Council's [Montjuïc Castle historical guide](https://ajuntament.barcelona.cat/castelldemontjuic/sites/default/files/fitxers/biblioteca/cmj_guia_20oct14_eng.pdf),
which describes the 1705 Allied capture and the separate Bourbon siege in
April 1706.

The crosswalk contains 8,880 rows. A first-side Seshat code is present in 4,693
rows, a second-side code in 3,811, and both sides are mapped in only 2,122.
These mappings are useful seeds, not approved identities. The current
Cliopatria release can connect many Seshat IDs onward to Wikidata IDs.

The staging code correctly drops rows without an ID, parses year ranges into
low/best/high candidates, marks duplicate IDs, preserves raw strings, and sets
`do_not_rate_automatically`.

### Interstate War Battle Dataset (IWBD)

**Purpose:** high-quality validation of interstate battle dates, opposing sides,
and tactical outcomes.

- Dataset record and DOI:
  <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KLQFAP>
- Data:
  <https://dataverse.harvard.edu/api/access/datafile/4435240?format=original>
- Codebook:
  <https://dataverse.harvard.edu/api/access/datafile/4435241>
- Metadata API and license:
  <https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/KLQFAP>
- Peer-reviewed article:
  <https://doi.org/10.1177/0022343320913305>
- Version: 1.0.
- Coverage: 1,708 battles in 97 interstate wars, 1823-2003.
- License: CC0 1.0.
- Publisher MD5 for the data file:
  `3bdf22d6f8e58621abd6b3601806f642`.
- Workspace snapshot SHA-256:
  `fcf5747cf94b50de9b74c41da078444d05bc7992bf6949f0a71107407d52b534`.

Fields are `cowNum`, `iwdNum`, `warName`, `battleName`, `attacker`,
`defender`, start and end components/dates, `battleLength`, `victor`,
`victorWarLevel`, and `victorBattleLevel`.

The victor is coded by tactical control of the attacker's strategic objective:
the attacker wins by taking it, the defender wins by retaining it, and cases
without a clear result are inconclusive. This is strong tactical evidence. It
does not describe casualties, the magnitude of a result, political goals, or
the final settlement of the enclosing war.

In this system IWBD battles enter the provisional ledger only through a
declared promotion rule, as tactical engagements. Exact normalized battle
names use a ±1-year window against curated seed events, non-curated-excluded
HCED candidates (promoted or staged), and earlier accepted IWBD rows. In the
current release, 864 IWBD records are excluded as presumptive HCED
duplicates. Exact canonical name/year matches remain exclusions rather than
corroboration and do not require side agreement; no HCED record is modified.
Cross-source matching canonicalizes numeric, suffixed, and word ordinals. A
broader base-name match is allowed only when one recognized terminal
ordinal/part path is a strict extension of the other (for example `Plevna 1`
and `Plevna 1(a)`), and a promoted HCED event has the same resolved winning
and losing sides in the same calendar year. Different suffix branches,
adjacent-year battles, and arbitrary terminal numbers are not collapsed merely
because they share a possible base.
Within-IWBD matching always retains the exact canonical ordinal. A row
whose date span strictly contains a differently-named battle of the same war
is staged as a presumptive campaign umbrella (321 rows), so only battle-level
granularity enters; the rule deliberately over-includes some genuinely
distinct long engagements. The coded battle-level victor must match a named
side with an agreeing attacker/defender role — the coded `inconclusive` value
maps to a tactical stalemate, while a blank or mismatched victor is rejected —
and the war-level victor code is ignored entirely. Coalition or composite side
labels stay staged (139 rows), and both sides must resolve to unique
time-bounded identities outside declared deny windows (12 side-resolution
failures, including the declared "Turkey" 1919-1923 deny window). In the
current build 153 of 1,708 battles pass; every other row stays staged under a
named rejection counter.

Twenty of those accepted battles use Wave 5 candidate-keyed identity
contracts: Trocadero; Orleans 1870; 12 Greco-Turkish or Franco-Turkish
battles; and six China-Taiwan battles. Each contract pins the
candidate's complete fingerprint and exact entity ID on both sides, and the
named cohort is complete-or-fail. These bindings are not aliases and do not
widen a label resolver. In particular, the 12 exact Turkish National Movement
bindings are the only contracted path through the deny interval; every other
bare `Turkey` row intersecting 1919-1923 remains staged.

Wave 6 now contains nine independently fingerprinted IWBD contracts. The
reviewed post-UAR Syrian identity releases one exact 1967 row; six proposed
Six-Day War rows remain held at the unresolved Egyptian identity boundary and
cannot fall through to a generic resolver.

IWBD's `iwdNum` field is the IWD parent-war identifier (IWD's `largerwarid`
numbering), not an IWD component (`initwarid`) identifier. Promoted IWBD
battles use that join to share a war cluster with the corresponding IWD
strategic parent for correlated-evidence down-weighting. Joining `iwdNum`
through IWD component IDs would misfile battles: component 77 is a World War I
dyad, while parent war 77 is Iran-Iraq.

#### Verified live IWBD profile

- 1,708 rows.
- 1,145 attacker victories, 489 defender victories, and 74 inconclusive
  battles.
- 96 distinct `cowNum` values. `cowNum=-9` contains two separately named
  wars, producing the published total of 97 wars.
- 116 distinct `warName` strings because the world wars are divided into
  theater labels such as Eastern Front, Western Front, Pacific, and War at Sea.
- Campaigns and constituent battles may both appear. The event hierarchy and
  `parent_event_id` must prevent double-counting.

### Interstate War Data (IWD)

**Purpose:** participant and terminal-outcome evidence for interstate component
wars, kept separate from the IWBD battle inventory.

- Dataset record and DOI: <https://doi.org/10.7910/DVN/WGS1YX>
- Data: <https://dataverse.harvard.edu/api/access/datafile/5118363>
- Version used: 1.21, covering 1823-2003.
- License: CC0 1.0.
- Workspace snapshot SHA-256:
  `fd6cfbcbebed2d31cc0aa8eaa417ec4b9d1514f9d0261cb843c153c05ba231ec`.

The file has 627 annual rows describing 265 component records within 93
larger-war umbrellas. `annualoutcome` is coded from the initiator's perspective:
0 is ongoing, 1 initiator victory, 2 initiator defeat, and 3 draw. The staging
pipeline groups by `initwarid` and preserves one unambiguous terminal outcome
per component record instead of treating every annual row as a new war.

IWD provides a strategic result category, but its component records are not
independent wars. One parent conflict can appear as many dyads: rating those
rows separately would repeatedly reward or penalize the same coalition result.
The release therefore rates IWD only through parent-war coalition aggregation.
Each `largerwarid` group is reconstructed as two coalitions from its
initiator/target pairs and receives at most one strategic update, and only when
every check passes: the opposition graph is two-colorable and connected (an
entity coded on both sides quarantines the parent, because no explicit
time-bounded side-switch policy is defined), the component outcomes are
unanimous once oriented to the reconstructed sides, no curated seed war
overlaps (naming variants such as `WorldWarI` are canonicalized), and every
belligerent resolves to a unique time-bounded identity. COW-coded parties are
resolved by explicit era policies: code 365 maps to the Russian Empire through
1917 and the Soviet Union from 1922 (the 1918-1921 revolutionary years
deliberately stay unresolved), code 255 to the Kingdom of Prussia through 1870
and the German Empire from 1871, code 300 to the Austrian Empire through 1866
and Austria-Hungary from 1867, code 345 to the Kingdom of Serbia (1882-1918,
the interval COW labels "Yugoslavia"), code 100 to the United States of
Colombia for 1863-1885, code 670 to the Kingdom of Saudi Arabia from 1932
through the current snapshot, and code 678 to the Mutawakkilite Kingdom of
Yemen for 1918-1961. The crisp-boundary policies additionally split code 160
across the Argentine Confederation, post-Pavon republic, and modern republic;
code 355 across the Bulgarian principality and kingdom; and code 652 around
Syria's deliberate 1958-1961 UAR gap. Overlapping transition years remain
ambiguous and fail closed. Wave 5 adds complete parent-keyed contracts for eight
reviewed wars: Franco-Spanish 1823; the Estonian War; Poland-USSR;
Greco-Turkish and France-Turkey; and the three China-Taiwan parents of 1950,
1954-55, and 1958. Each contract pins the full component inventory, source
semantics, party codes, and exact target entity IDs. It is not a generic COW
fallback, and a missing component or changed fingerprint fails the build.
Four parent wars remain on the curated exclusion list: Germany-Denmark 1848
because the source asserts a Prussian victory although Denmark won the First
Schleswig War; Italian Unification 1859 because it was fought by the Kingdom
of Sardinia; and Hungarian-Allies 1919 because it was fought by the Hungarian
Soviet Republic. The War of the Triple Alliance also stays staged: its IWD
component dyads omit Uruguay from the Argentina-Brazil-Uruguay coalition, so
the parent cannot be promoted as a complete coalition merely because the new
Argentine identity now resolves.
Event confidence is reduced when some component rows could not contribute, and
all component rows are attached to the emitted event as provenance. In the
current build, 64 of 93 parent wars pass (100 of 265 component records); the
rest stay staged. IWD also cannot by itself establish that a defeat was
existential, regime-ending, or equivalent to surrender, so aggregated outcomes
are never coded above limited victory or defeat.

Because IWD supplies no per-participant contribution, role, or stakes data,
aggregated coalition events use declared uniform defaults: every member of a
multi-entity side receives an equal contribution share with the `major_ally`
role, both sides share one outcome vector, and every parent war is coded at
`major_war` scale with `major` stakes. This is a provisional mechanical
default, not a claim that (for example) every 1991 coalition member
contributed equally; the participation-review guidance below still applies
before any of these events can be treated as curated. Differentiated coalition
contribution is future curated work.

### Uppsala Conflict Data Program (UCDP)

**Purpose:** the principal modern source for conflicts, dyads, actors, violence
events, deaths, goals, and conflict termination.

- Download center: <https://ucdp.uu.se/downloads/>
- API documentation: <https://ucdp.uu.se/apidocs/>
- License for all current downloads: CC BY 4.0.
- Current annual version: 26.1.
- Static files can be downloaded without an API token. The API requires a token
  sent as `x-ucdp-access-token` and currently permits 5,000 requests per day.

#### Files used or recommended

| Dataset | Exact access URL | Coverage/use |
|---|---|---|
| UCDP/PRIO Armed Conflict v26.1 | <https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-261-csv.zip> | Conflict-year, 1946-2025; at least one side is a state government. |
| Dyadic v26.1 | <https://ucdp.uu.se/downloads/dyadic/ucdp-dyadic-261-csv.zip> | Opposing actor pair-year, 1946-2025. |
| Actor v26.1 | <https://ucdp.uu.se/downloads/actor/ucdp-actor-261-csv.zip> | Actor identifiers, full and alternate names, origins, alliances, splits, conflicts, and dyads. |
| GED v26.1 | <https://ucdp.uu.se/downloads/ged/ged261-csv.zip> | Georeferenced lethal events, 1989-2025. |
| Non-State v26.1 | <https://ucdp.uu.se/downloads/nsos/ucdp-nonstate-261-csv.zip> | Conflict-year where neither primary party is a state, 1989-2025. |
| One-Sided Violence v26.1 | <https://ucdp.uu.se/downloads/nsos/ucdp-onesided-261-csv.zip> | Intentional attacks on civilians by governments or organized groups, 1989-2025. |
| Battle-Related Deaths, dyadic | <https://ucdp.uu.se/downloads/brd/ucdp-brd-dyadic-261-csv.zip> | Dyad-year fatality estimates. |
| Battle-Related Deaths, conflict | <https://ucdp.uu.se/downloads/brd/ucdp-brd-conf-261-csv.zip> | Conflict-year fatality estimates. |
| Conflict Termination v4-2024, conflict | <https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv> | Conflict episodes and termination categories; aligned to UCDP 25.1, not 26.1. |
| Conflict Termination v4-2024, dyad | <https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Dyad.csv> | Dyad episodes, outcomes, ceasefire dates, and peace-agreement dates; aligned to 25.1. |
| Conflict Issues v23.2, dyad-year | <https://ucdp.uu.se/downloads/cid/ucdp_issues_dataset_dyadyear_232.csv> | Stated rebel goals and incompatibility issues, 1989-2017. |
| Conflict Issues v23.2, dyad-issue-year | <https://ucdp.uu.se/downloads/cid/ucdp_issues_dataset_dyadissueyear_232.csv> | One row per stated issue and dyad-year. |
| Peace Agreements v22.2 | <https://ucdp.uu.se/downloads/peace/ucdp-peace-agreements-222.xlsx> | Agreements between primary warring parties, 1975-2021; links updated in 2026. |

UCDP GED fields include event/conflict/dyad IDs, violence type, side IDs and
names, source counts and citations, coordinate/location precision, latitude,
longitude, country and region, event/date precision, start/end dates,
`deaths_a`, `deaths_b`, civilian and unknown deaths, and `low`, `best`, and
`high` estimates. The v26.1 API documentation currently reports 417,968 GED
events.

GED represents lethal organized-violence events, not necessarily named battles.
Its violence types are state-based, non-state, and one-sided. One-sided violence
must never be treated as a competitive match. GED has no winner field.

The annual conflict/dyadic files identify incompatibility, territory, conflict
type, intensity, secondary supporters, dates, and state/actor IDs. Intensity
means 25-999 battle-related deaths or at least 1,000 in a calendar year; it does
not establish victory.

The termination data supplies six strategic categories:

1. Peace agreement.
2. Ceasefire agreement.
3. Victory for Side A, the government side in internal conflict.
4. Victory for Side B, the non-state side in internal conflict.
5. Low activity below the UCDP threshold.
6. Actor ceases to exist or becomes a different actor.

These categories do not automatically determine outcomes for secondary
supporters. For example, an intervening state can withdraw before the primary
government or rebel side wins or loses. Participant entry/exit dates,
contribution, objectives, and settlement effects still require review.

In this system the termination data is the only UCDP data with a mechanical
promotion rule, and that rule is declared and narrow. Promotion operates at
the conflict-episode level only; the dyad-level termination file is never
promoted and serves solely as a consistency cross-check. Only terminal
episodes with victory outcome codes 3 or 4 can produce strategic events —
peace agreements, ceasefires, low-activity endings, and actor cessation stay
staged, because peace is not a loss and low activity is not an outcome. Every
primary party on both sides must resolve to a unique time-bounded identity for
the full episode span: state parties (a `Government of ...` party with a
Gleditsch-Ward code) through explicit, authoritative GW-code policy windows or
exact time-valid alias matching, and non-state primaries only through
conflict-scoped curated actor policies (`UCDP_ACTOR_PARTY_POLICIES`), whose
windows are the actor's attested existence bounds and whose keys are bound to
one conflict ID so a homonymous actor label in another conflict (for example
the "PLA" of conflict 347) never resolves; the government side must
independently resolve. The event's `war_type` follows the source's
`type_of_conflict` under an exhaustive declared mapping, and unmapped types
are rejected rather than coerced. An episode is rejected when it duplicates an
already-promoted strategic event by shared entities and overlapping years,
when a terminal dyad row of the same conflict contradicts it (an
opposite-orientation victory or a same-pair negotiated termination), when a
victory assertion elsewhere in the file with the same episode end date orients
a shared entity oppositely (this quarantines the Israel-Jordan front of the
mutually contradictory 1967 Six-Day complex; every other front must still
independently pass the identity and linked-evidence gates), or
when it carries a documented side-attribution dispute
recorded as a curated exclusion (the 1974 Paracel episode). Severity is capped
at limited, and secondary supporters are recorded as provenance without
outcomes. In the current build 7 of 2,752 conflict-level rows pass; the rest
stay staged under named rejection counters.

#### Verified live UCDP profile

The following counts come from the workspace snapshots retrieved on
2026-07-13, not estimates:

| Snapshot | Parsed rows | Unique units | Observed years |
|---|---:|---:|---:|
| UCDP/PRIO Conflict v26.1 | 2,816 | 303 conflicts | 1946-2025 |
| Dyadic v26.1 | 3,518 | 697 dyads across 303 conflicts | 1946-2025 |
| Actor v26.1 | 1,987 physical CSV rows | 1,928 nonblank actor records; 59 fully blank rows | Not an annual panel |
| Termination conflict v4-2024 | 2,752 | 303 conflicts; 507 terminal episode rows | 1946-2024 in the file |
| Termination dyad v4-2024 | 3,432 | 684 dyads; 923 terminal episode rows | Intended modern range through 2024 |

Termination conflict outcomes among the 507 terminal rows are: 60 peace
agreements, 67 ceasefires, 107 government-side victories, 44 non-state-side
victories, 209 low-activity endings, and 20 actor-cessation endings.

Termination dyad outcomes among 923 terminal rows are: 111 peace agreements,
101 ceasefires, 150 government-side victories, 73 non-state-side victories, 399
low-activity endings, 88 actor-cessation endings, and one terminal row with a
blank outcome.

Verified issues requiring quarantine or validation:

- The termination files correspond to UCDP 25.1, while the current conflict,
  dyadic, and actor files are 26.1. Join only through version-aware IDs and audit
  missing/new dyads.
- The dyadic termination snapshot contains an apparent corrupt source row for
  dyad `16562` (Central African Republic government-CPC): `year=8` and
  `d_ep_durcount=-2011`. The current v26.1 dyadic file shows that episode
  beginning in 2020. Do not silently repair it; quarantine it until confirmed
  against a corrected publisher release.
- The Actor archive has 59 completely blank physical rows. Filter them before
  producing review candidates.
- The download-center heading presents Battle-Related Deaths as a 1989-2025
  dataset while its current prose still says 1989-2023. Check the file and
  codebook for the needed years rather than relying on the heading.
- UCDP IDs changed in version 17.1. Use the official translation tables when
  connecting older UCDP releases.

### Cliopatria

**Purpose:** time-bounded identity and geometry for historical polities.

- Current release: v0.2.0, published 2026-05-16.
- Zenodo: <https://zenodo.org/records/20274630>
- Direct release archive:
  <https://zenodo.org/records/20274630/files/Seshat-Global-History-Databank/cliopatria-v0.2.0.zip?download=1>
- GitHub: <https://github.com/Seshat-Global-History-Databank/cliopatria>
- Peer-reviewed data description:
  <https://www.nature.com/articles/s41597-025-04516-9>
- Coverage: more than 1,800 political entities from 3400 BCE through 2024 CE.
- License: CC BY 4.0.
- Release MD5: `6d573d5a07dfcd5a2c6c9933d6401d48`.

The GeoJSON records provide entity name, polygon geometry in EPSG:4326, area,
`FromYear`, `ToYear`, Wikipedia reference, Seshat ID, membership/components,
and polity/relation type. Version 0.2.0 adds Wikidata IDs for all polities and
supra-polity relations such as selected unions, vassalages, and alliances.

Cliopatria seeds the internal `Entity` registry. A new internal entity receives
a new baseline rating even when it has a predecessor. `predecessors` and
`continuity_note` are descriptive relationships and never transfer rating.

Cliopatria is not exhaustive. With rare exceptions it omits polities smaller
than roughly 5,000 square kilometres or shorter than roughly 50 years. Temporal
sampling is irregular, ancient changes are sparse, and historical boundary
uncertainty is not numerically encoded. It reflects one reviewed interpretation,
not a final ruling on succession or identity.

### Wikidata

**Purpose:** open entity IDs, aliases, discovery, cross-source links, and source
references.

- Data access: <https://www.wikidata.org/wiki/Wikidata:Data_access>
- Licensing: <https://www.wikidata.org/wiki/Wikidata:Licensing>
- SPARQL endpoint: <https://query.wikidata.org/sparql>
- Entity dumps: <https://dumps.wikimedia.org/wikidatawiki/entities/>
- License: structured data in the main, property, lexeme, and entity-schema
  namespaces is CC0 1.0. Text in other namespaces is CC BY-SA.

Relevant properties include instance/subclass (`P31`, `P279`), part of (`P361`),
participant (`P710`), winner (`P1346`), conflict (`P607`), start/end/point in
time (`P580`, `P582`, `P585`), location (`P276`), and coordinates (`P625`).

Use QIDs as crosswalk identifiers, not as automatic polity boundaries or proof
of victory. Preserve statement rank, qualifiers, references, and retrieval date.
Missing `winner` is unknown, not a draw. The public query service is unsuitable
for extracting the entire graph; use paged, bounded queries or a versioned dump.

### Pleiades and GeoNames

These are location resolvers, not conflict-outcome datasets.

#### Pleiades

- Downloads: <https://pleiades.stoa.org/downloads>
- Current numbered release listed by the publisher: 4.1, 2025-05-28.
- Coverage: ancient places, names, locations, connections, time periods, and
  coordinates.
- Preferred comprehensive format: daily JSON; quarterly numbered releases are
  better for reproducible research.
- License: CC BY 3.0.

#### GeoNames

- Download and service terms: <https://www.geonames.org/export/>
- Daily worldwide dump: <https://download.geonames.org/export/dump/allCountries.zip>
- Fields include stable place ID, names and aliases, coordinates, feature code,
  administrative hierarchy, elevation, and population.
- License: the publisher describes it as CC-BY and permits commercial use.

Use Pleiades for ancient aliases and GeoNames for modern locations. Neither
identifies the polity that fought at a place or the winner of an event.

## Restricted, permission-gated, or secondary sources

These sources may be consulted for validation, but their raw data must not enter
the public distributable corpus under the current policy. See
[`LICENSING.md`](LICENSING.md).

### Correlates of War (COW)

- Terms: <https://correlatesofwar.org/data-sets/>
- War data: <https://correlatesofwar.org/data-sets/cow-war/>
- Militarized Interstate Disputes v5:
  <https://correlatesofwar.org/data-sets/MIDs/>
- State System Membership v2024:
  <https://correlatesofwar.org/data-sets/state-system-membership/>
- Territorial Change v6:
  <https://correlatesofwar.org/data-sets/territorial-change/>
- National Material Capabilities v6:
  <https://correlatesofwar.org/data-sets/national-material-capabilities/>

COW covers interstate, extra-state, non-state, and intrastate wars generally
from 1816-2007, with intrastate v5.1 through 2014; MIDs cover 1816-2014;
state membership extends through December 2024; territorial change covers
1816-2018; and material capabilities cover 1816-2016.

War records include participant outcomes and battle deaths and are valuable for
historical validation. Outcome categories remain coarse and do not by themselves
distinguish limited withdrawal from capitulation, occupation, regime collapse,
or dissolution. COW prohibits commercial use and third-party distribution
without written permission, so public use is permission-gated.

### Militarized Interstate Events (MIE)

- Download page and user agreement:
  <https://internationalconflict.ua.edu/data-download/>
- Codebook:
  <https://internationalconflict.ua.edu/wp-content/uploads/2023/07/MIEcodebook.pdf>
- Coverage: daily interstate events, 1816-2014.

Fields include confrontation/event IDs, COW state codes, dates, side, action,
hostility level, and minimum/maximum military fatalities for each state. Its
`war battle` events build on IWBD and add roughly 100 battles. It excludes
non-state actors and non-COW-system participants. The user agreement prohibits
commercial use and distribution other than replication, so ingestion is
permission-gated.

### ACLED

- API documentation: <https://acleddata.com/api-documentation/getting-started>
- Content usage terms: <https://acleddata.com/contentusage>
- Attribution policy: <https://acleddata.com/attributionpolicy>
- Country/time coverage: <https://acleddata.com/methodology/countrytime-period-coverage>

ACLED is a living, weekly modern political-violence dataset with country-specific
start dates. Fields include event/sub-event type, actors, location, sources,
reported fatalities, civilian targeting, date and geolocation precision. It has
no winner field and should not power Elo outcomes. Its current terms prohibit
creating a competing or functionally substitutive dataset/product and impose
strict reuse and attribution conditions. Exclude it unless ACLED provides
specific written authorization for this project.

### PA-X Peace Agreement Database

- Downloads: <https://www.peaceagreements.org/downloads/>
- Version 10 codebook:
  <https://www.peaceagreements.org/cms/documents/3956/PA_X_codebook_v10.pdf>
- Terms:
  <https://www.peaceagreements.org/cms/documents/8/Terms_of_Use_updated_added_local.pdf>
- Coverage: 2,257 agreements in more than 170 peace processes, 1990-2025.

PA-X codes more than 225 substantive provision categories and can clarify
territorial, institutional, military, and power-sharing settlement effects. It
does not provide a simple military winner. Its terms prohibit commercial use
and reusing a substantial portion to create a substantially similar database;
the content is otherwise CC BY-NC-SA 4.0. Use only for bounded manual research
or after receiving permission.

### DBpedia

- SPARQL access and limits: <https://www.dbpedia.org/resources/sparql/>
- Monthly Latest Core: <https://www.dbpedia.org/resources/latest-core/>
- License: <https://www.dbpedia.org/imprint/>

DBpedia automatically extracts Wikipedia infobox and article data. Releases
from 3.4 onward are dual-licensed CC BY-SA 3.0 and GFDL. The public endpoint
limits results to 10,000 rows and execution to 120 seconds and may return
partial data with HTTP 200 rather than an error. Wikidata is cleaner and CC0,
so DBpedia is excluded from the initial merged corpus and may be used only as a
separately attributed resolver after a license review.

### Brecke Conflict Catalog

- Project and downloads: <https://brecke.inta.gatech.edu/research/conflict/>
- Author's notes:
  <https://brecke.inta.gatech.edu/wp-content/uploads/sites/19/2018/09/Notes-about-Conflict-Catalog.pdf>

The catalog aims to record conflicts since 1400 with at least 32 fatalities and
has a European extension to 900. It includes participants, initiation where
possible, dates, locations, and military/total fatalities. The author calls it
unfinished, expects substantial growth, and warns that errors increase backward
in time and in poorly documented regions. No explicit data license is stated.
Do not redistribute or ingest it into the public corpus without permission.

### Broader Seshat data

Seshat warfare, social-complexity, and military-technology variables can provide
context, but the general Seshat terms are CC BY-NC-SA and may require API
credentials. They do not supply battle winners. Keep them separate from
Cliopatria, whose v0.2.0 release is expressly CC BY 4.0.

## Required ingestion order

1. **License allowlist:** record the exact URL, version, license, access date,
   and checksum before parsing. Permission-gated sources remain outside the
   public raw-data directory.
2. **Immutable snapshot:** download a versioned raw file and append its metadata
   to `data/raw/manifest.jsonl`; never overwrite an earlier snapshot.
3. **Polity registry:** seed time-bounded entities from Cliopatria and Wikidata,
   then apply the project's historiographic continuity rule. A successor starts
   at baseline even when linked to a predecessor.
4. **Candidate staging:** stage HCED, IWD, IWBD, and UCDP records into
   `data/review/*.jsonl` with raw labels, row location, source snapshot, and
   `do_not_rate_automatically=true`.
5. **Entity resolution:** resolve aliases to a polity that existed on the event
   date. Preserve unresolved, coalition, rebel, colonial, and dependency actors
   rather than forcing them into modern-country IDs.
6. **Hierarchy and deduplication:** distinguish engagement, campaign, conflict
   episode, and war; link nested records with `parent_event_id`; do not count a
   campaign and each constituent battle as independent full-value evidence.
7. **Outcome adjudication:** build tactical, operational, and strategic vectors
   separately. Use UCDP goals/termination/agreements and independent historical
   sources for strategic dimensions. Unknown remains unknown, not a draw.
8. **Participation review:** code principal, coalition lead, major/supporting
   ally, expeditionary force, or proxy sponsor and the actor's entry/exit dates
   and contribution. Do not assign an entire coalition's outcome equally to
   every participant.
9. **Confidence and audit:** retain conflicting assertions, date/location
   precision, casualty ranges, and confidence. A narrow, declared ruleset may
   admit qualifying source assertions to the provisional ledger; only
   claim-level reviewed events belong in a fully curated release.
10. **Restricted validation:** use COW, MIE, PA-X, ACLED, DBpedia, Brecke, or
    broader Seshat data only within the limits in `LICENSING.md` and never copy
    their raw records into a public release without the required permission.

## Current expanded provisional release

The current release publishes distinct coverage units separately:

- 2,345 time-bounded polity identities in the rated-and-unrated registry;
- 995 release entity records, of which 988 distinct IDs actually participate
  in rated events;
- 1,413 registered provenance sources across 1,158 source families; and
- 5,338 rating events: 40 manually curated events, 1,887 crosswalk-resolved,
  2,423 label-resolved, and 764 candidate-keyed HCED tactical encounters
  (76 Wave 6 + 192 Wave 7 + 496 Wave 8),
  64 coalition-aggregated IWD strategic parent wars, 153 IWBD tactical
  battles, and 7 UCDP conflict-termination strategic episodes.

The committed dashboard is the matching 1,000-simulation build and its audit
error array is empty. The current post-Wave-8 HCED planning funnel removes all
candidate IDs already published in the ledger before ranking and reports 2,293
touched deferred rows, 2,223 unresolved normalized labels, and 1,069
sole-blocker rows; the current top-ten greedy batch reaches 30 cumulative
events. Those are prioritization units, not extra rating events.

The seven-record entity/evidence difference is intentional. These inactive
release identities are retained as curated boundary records, reviewed
campaign-specific identities whose proposed rows remain held, or an explicit
superseded source envelope. None receives a rating or counts among the 988
participant IDs.

Relative to the Wave 4 artifact, Wave 5 adds 161 events and removes none of the
previously published event IDs: 133 HCED encounters, 8 IWD parents, and 20 IWBD
battles. The Wave 5 cohort contains 79 Portugal-linked events (78 new plus the
existing Estaires event) and 58 Tsardom-linked events (55 new plus three
existing). Its HCED resolution split is 16 crosswalk / 63 label for Portugal
and 41 crosswalk / 17 label for the Tsardom. A row-level audit kept 19 proposed
HCED rows and four proposed IWBD rows out of the release before publication;
they were never part of the Wave 4 ledger and therefore are not release
removals.

Relative to Wave 5, Wave 6 adds 199 events and changes none of the 4,406 prior
event payloads: 191 HCED encounters and 8 IWBD battles. The three chronological
lanes retain exact candidate fingerprints and explicit hold inventories. Two
candidate-keyed reviewed contracts raise the current Portugal-linked total to
81. Five registry-only Cliopatria proposals remain addressable as explicit
superseded rows, rather than disappearing when stronger curated identities
replace them.

Relative to Wave 6, Wave 7 adds 192 fingerprinted HCED encounters through five
audited promotion lanes. It also atomically migrates five already-rated Orange
Free State battles from a superseded source envelope to the reviewed identity;
those migrations do not add events. Forty-two reviewed proposals remain on
explicit holds. Seven root-lane outcomes and five western-lane source claims
replace HCED as the direct outcome source for 12 exact candidates without
creating a second rating event.

Relative to Wave 7, the final composite-and-identities rebuild adds 48 event
IDs and removes three after the deeper source-side audit, for 45 net events.
The ledger gains 40 label-resolved and four crosswalk-resolved HCED encounters
while the disputed Aros assertion leaves; four IWBD rows enter while the
Puebla and Jijiga duplicates leave, for two net IWBD events. The IWD total is
unchanged because the newly resolvable Triple Alliance parent remains excluded
as an incomplete coalition. Of the label additions, 21 use the new post-1500
delimiter-only composite path. The tranche curates the
Mahdist State, post-Pavon Argentine Republic, Bulgarian principality/kingdom,
Republic of Texas, and pre-/post-UAR Syrian republic windows. Argentina's
1861 and 1930 boundaries and Bulgaria's 1908 boundary fail closed at year
precision, Texas's generic label window ends in 1845, and Syria deliberately
has no generic or code resolution in 1958-1961.

Relative to that post-Wave 7 artifact, the initial Wave 8 batch added 46
candidate-keyed HCED events and removed none: 9 in the African-states lane, 15
in New Zealand, and 22 in North America. It added 26 alias-free
release/registry identities and 29
sources. Four promoted rows carry documented outcome overrides, while 16
massacre/noncompetitive or unresolved reviewed rows remain exact holds.

The earlier curated state and non-state actor identity tranches raised the totals
from the previous build (177 rated entities across 2,620 events): the new
seed identities and their code/label policy windows resolve rows that were
previously staged for lack of a defensible time-bounded identity, and the
registry consolidates 40 absorbed source-candidate rows into 48 curated
records (1,582 to 1,590 net). Wave 4 then added three narrow identities while
absorbing two exact-name Cliopatria envelopes, producing the Wave 4 total of
1,591. Wave 5 produced a 1,598-row registry after consolidating the
Tsardom of Russia onto its pre-existing canonical Cliopatria ID rather than
creating a second Tsardom record. Wave 6 produced a 1,648-row registry. Wave 7
added reviewed identities and explicit supersession records to produce 1,702
registry rows. The post-Wave 7 composite tranche consolidated reused source
identities and produced 1,701 rows. The initial Wave 8 batch added 26 exact,
alias-free identity records. Continued Wave 8 identity and candidate-keyed
review now produces the current measured 2,345-row registry; every release
identity still has an exact registry row.

The review queues contain 27,014 staged source records across Cliopatria, HCED,
IWD, IWBD, UCDP, and the small Wikidata discovery sample (the Wikidata queue
holds 18 candidates on this machine). That total includes
identity records and the source-derived evidence promoted into this
provisional release; it is not an unresolved-record count. Of 23,390 event-like
candidates, 18,056 remain outside the rating ledger because their layer,
identity, outcome, duplication, or continuity requirements are unresolved.
The registry and queue sizes document coverage work; neither is evidence that
the historical record is complete.

Outcome-family coverage uses a different denominator from corpus coverage.
Exactly 5,298 rated events have an explicit direct-outcome mapping; the
remaining 40 are the curated seed events and stay unknown pending claim-level
locator review. Of the mapped events, 4,959 cite one declared direct-outcome
family and 339 cite more than one.
