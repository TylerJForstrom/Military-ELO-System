# Handoff: M4/M5 adversarial-review triage completed

Current implementation state (2026-07-14): the policy, pipeline, historical
adjudication, and test-gap work below is complete in the working tree. The
coordinated machine-local build contains 1,590 registry identities, 226 rated
entities, and 4,234 events: 40 seed, 1,769 crosswalk HCED, 2,243 label HCED,
54 IWD, 121 IWBD, and 7 UCDP. It reports 27,014 staged source records and
19,163 unresolved event-like candidates from a 23,390-candidate event queue.
The dashboard is the 1,000-simulation build and its embedded audit reports zero
warnings. All 241 tests pass. The rendered browser check confirmed the four
headline counters, the 1871-1918 German Empire registry boundary, working
registry filtering, and no console warnings or errors.

The original adversarial review ran to ~95% completion: five reviewers
produced 61 findings and 57 received adversarial verification before the run
was cut short. This document preserves that inventory below as the decision
record; it is no longer an open pickup list. The post-fix adversarial sweep
also found and excluded two additional granularity duplicates: the redundant
`Changsha1942II` assertion and the `Barcelona, Spain1705-1706` envelope.
The final ULTRA re-review restored the distinct 1999 Badme 2(a) battle that a
cross-year fuzzy match had suppressed, excluded the wrong-outcome IWBD Duppel
fallback exposed by the HCED exclusion, made suffix-path matching preserve
different ordinal/part branches, and narrowed the three seed interval
exemptions to their exact approved bounds. These corrections offset in the
headline totals.

## Where the findings live

- `.local-handoff/m4m5-review-findings-full.txt` — full findings with failure
  scenarios and complete verification reasoning (local-only, never commit).
- `.local-handoff/m4m5-review-findings-digest.txt` — one line per finding
  plus one line per verdict, numbered; verdict Vn corresponds roughly in
  order to finding n but match them by content, not index.
- Four findings never received verdicts (the run stopped mid-verify), and the
  historical-accuracy reviewer sampled only part of the ledger — assume the
  confirmed list below is a floor, not a ceiling.

Already fixed in the working tree (verified-confirmed doc/comment defects): the
stale France/Persia gap inventory in the `HCED_LABEL_POLICIES` header comment,
the Sweden example in the pending-split comment, the stale France-gap sentence
and the "twelve former faction labels" migration claim in METHODOLOGY, and the
README "thirty others" arithmetic.

## Original work list preserved verbatim

### A. Policy and pipeline defects (code + rebuild + doc/test sync)

1. **1871 boundary inconsistency:** `HCED_LABEL_POLICIES["prussia"]` ends at
   1871 while `IWD_COW_CODE_POLICIES["255"]` gives 1871 to `german_empire`,
   so the two pipelines assign the boundary year to opposite sides of the
   declared era split; relatedly, Franco-Prussian engagements fought after the
   18 January 1871 proclamation (St Quentin, Mont Valerian, Dijon, Pontarlier,
   Belfort 1871 rows) are credited to `kingdom_prussia`. Decide one
   convention (the year-precision data cannot split January 1871, so the
   defensible move is probably to make bare-1871 ambiguous everywhere, or to
   assign all of 1871 to `german_empire` in both tables) and pin it with
   boundary tests.
2. **Turkey deny window starts too late:** May–July 1919 Greco-Turkish rows
   carry "Turkey" side labels denoting the Kemalist movement; widen
   `IDENTITY_DENY_WINDOWS["turkey"]` to (1919, 1923) and re-measure.
3. **`fr_france_modern_1` code window (1870, 1940)** contradicts the declared
   bare-1870-undecidable convention that the label table enforces; align the
   code window (1871, 1940) or document why codes differ from labels.
4. **IWBD-vs-HCED dedup misses ordinal-suffix variants** ("Plevna 1" vs
   "Plevna (1st)"), measured at ~29 battles rated twice. Extend the
   normalized-name matcher to strip/canonicalize ordinal suffixes on both
   sides, re-measure, and keep excluded duplicates counted.
5. **Label-pass `duplicate_of_promoted_event` key is (name, best_year)**:
   distinct same-name same-year battles are dropped, and which row survives
   depends on source order. Add a disambiguator (location/participants) or
   stage collisions explicitly.
6. **Metadata policy text** in `release.py` still says "twelve former faction
   labels"; correct to the seven-migrated/five-never-blocklisted phrasing
   (the committed artifacts refresh at the next rebuild).
7. **Three curated seed events rate an identity outside its interval**
   (the known anomaly from the original handoff, now measured at exactly
   three); add participant entry dates or a documented seed-event exemption
   gate so the invariant is enforced rather than accidental.

### B. Historical outcome errors in the released ledger (confirmed by verification)

Each needs triage into: curated row exclusion (wrong actor/duplicate), policy
fix (where the error is the project's identity substitution), or a documented
source assertion left in place. Confirmed items:

- **Inverted or wrong winners:** Brusilov Offensive 1916 (critical — coded as
  a Central Powers victory); Coatit 1895; Dembeguina 1935; A Shau 1966;
  Dragasani 1821; Barcelona 1936; Kemmel 1918; Kaiserswerth 1702; Lvov 1675;
  Parwan Durrah 1840; Diamond Hill 1900; Mojkovac 1916; Brest 1513;
  St Augustine 1702; IWD parent "Germany-Denmark 1848" (First Schleswig War
  coded as a Prussian win).
- **Wrong belligerent through identity resolution:** Lepanto 1571 (Habsburg
  Monarchy was not a belligerent); Valmy/Verdun/Longwy 1792 (Habsburg coded
  where Prussia fought); Duppel 1849 (Austria not a belligerent); Kolberg
  1774 (no Russo-Prussian war existed; and Kolberg 1760 inverted); Bautzen/
  Rippach/Mockern 1813 (Austria was neutral until August); Montmirail/
  Brienne/Vauchamps 1814 (fought against Prussia/Russia, coded vs Austria);
  Messina 1718 (France vs Habsburg who were allies; Spain fought); Trebizond
  1916 (France/UK credited for an exclusively Russian campaign); Hanoi 1873
  (Qing coded; Nguyen Vietnam/Black Flags fought); Cadore 1508 and Hadad 1562
  (Habsburg branch confusion); Grol 1627 and Maastricht 1632 (Dutch Republic
  absent, England/France credited); Tutrakan 1916 (Ottomans credited for a
  Bulgarian assault); Andalsnes 1940 (France coded for a British-Norwegian
  operation).
- **Duplicates and granularity:** Rimnik 1789 = Martinesti 1789; Tournai
  1794 = Pont-a-Chin 1794; Chinese Civil War campaign envelopes (Liaoshen,
  Huaihai, Beijing-Tianjin) rated alongside their own component battles;
  Trentino 1917 date error.
- **Systematic:** dyadic HCED rows omit principal co-belligerents (Caporetto
  without Germany, Rossbach without France, and others) — a documented
  modeling limitation today; consider a curated co-belligerent table or a
  documented acceptance.

Findings that verification REFUTED (leave as documented source assertions):
Newbury/Gainsborough 1643, Bizani 1913/Jannina 1912, the 1916 Isonzo rows,
Nieman River 1920 (the IWBD row is not the Polish-Soviet battle), the
Basing House range-truncation claim, and the empire_brazil 23-event pin.

### C. Test gaps (confirmed)

- IWD/IWBD resolvers bypass the HCED front gates (blocklist, pending-split,
  label policies) by design — the shipped artifact depends on that; document
  the asymmetry in METHODOLOGY and pin it with a test so a refactor cannot
  silently change it.
- `IWBD_CURATED_EXCLUSIONS` has zero coverage: add a unit test for the
  counter and an artifact test that the five excluded ids never appear.
- UCDP negative cases: actor-policy label on the government slot, mixed
  government+actor side, actor label as secondary party.
- Cross-table target validation: extend the policy-target test to
  HCED_LABEL_POLICIES, IWD_COW/UCDP_GW/actor tables.
- Deny-window ∩ policy-table disjointness guard (the policy gate runs before
  the deny check inside the tiers).
- Exact era-boundary edge pins (1803/1804, 1866/1867, 1648/1661, 1792/1793).
- The UCDP actor-policy artifact test passes vacuously if no event uses the
  method; pin the two enumerated episodes (conflict 202 ep1, conflict 242
  ep2) directly.

## Machine-local rebuild record

This release was rebuilt with the 18-candidate Wikidata discovery queue on
this machine. The resulting totals are 27,014 staged source records, 23,390
event-like candidates, and 19,163 unresolved candidates. Future
release-touching work must again rebuild release + registry + dashboard
(`--simulations 1000`) together and re-sync every current count-bearing doc
and test pin to that machine's measured values. Do not combine counts from a
different discovery queue.

## Definition-of-done status

1. Complete: every category-A defect is fixed and tested.
2. Complete: every category-B item has an explicit exclusion, policy fix,
   retained-source-assertion disposition, or documented modeling limitation.
3. Complete: every category-C test gap is covered.
4. Complete: release, registry, and 1,000-simulation dashboard were rebuilt
   together; audit, browser verification, and count synchronization are clean.
5. Complete: the fresh historical-accuracy sweep checked exclusions, interval
   containment, cross-source duplicates, every residual exact same-name/year
   HCED collision, and the IWBD fallbacks exposed by HCED exclusions; it added
   the exclusions and Badme/dedup hardening noted above.
6. Pending user review: split the reviewed working tree into coherent
   conventional commits and push only after that review.
