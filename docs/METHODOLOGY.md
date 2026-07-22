# Military History Elo methodology

## What the score means

This project measures documented military success relative to the opponents and circumstances an actor actually faced. It does **not** estimate who would win a hypothetical fight between a modern state and an ancient empire. Technology, disconnected opponent networks, missing evidence, and changing definitions make that claim undefendable.

The system publishes four values rather than hiding everything in one number:

1. **Tactical rating** — battles, sieges, raids and other engagements.
2. **Operational rating** — campaigns and major operations.
3. **Strategic rating** — participant-specific outcomes of completed wars.
4. **Historical success index** — a declared editorial summary of peak, sustained and cumulative opponent-adjusted success within a connected opponent network.

Each layer starts at 1500 with high uncertainty. A successor or newly recognized polity always starts from that prior; predecessor ratings are descriptive history, never inherited points.

## Coverage and evidence tiers

The polity registry and rating ledger are separate products. The current expanded provisional release catalogues 2,539 time-bounded polity identities. Its entity file contains 1,200 release records, while 1,193 distinct entity IDs actually participate in accepted rating evidence. Its 5,585 events consist of 40 manually curated events, 1,887 crosswalk-resolved, 2,525 label-resolved, and 906 candidate-keyed HCED outcomes — 76 from Wave 6, 192 from Wave 7, and 638 from Wave 8 — plus 66 coalition-aggregated IWD strategic parent wars, 153 IWBD tactical battles, and 8 UCDP conflict-termination strategic episodes. The 1,737 registered sources span 1,444 provenance families. The review queues hold 45,968 staged source records, of which 42,344 are event-like candidates; 36,758 of those remain outside the rating ledger. The additive 18,954-candidate Wikidata battle/siege queue is discovery data only and changes none of those 5,585 rated events. An unrated registry entry or release entity record has no Elo result; it is not assigned a baseline score, loss, draw, or implied lack of military success.

Location coverage is status-aware. Every rated HCED event is bound to exactly
one stable source candidate ID, but a location field is published only when it
survives the frozen candidate-ID quarantine. The release contains 4,850 strict
GeoJSON Points, 5,218 exact `modern_location_country` transcriptions, and 5,267
provenance-bound events with at least one of those fields. Each provenance
object is closed to `source_id: hced_dataset`, the exact source record ID,
`assertion_status: unreviewed_source_assertion`, and
`coordinate_precision: unknown`. The Point and label quarantines contain 468
and 99 candidates respectively, overlap on 51 events, and affect 516 unique
events; one additional candidate has a source-blank country field. Values are
withheld, not corrected. The retained country field is a source-transcribed
geographic-jurisdiction label; none is normalized into sovereign-country
truth. Verified-location coverage is unavailable, not zero.

Source-derived events enter only through declared mechanical promotion rules and remain provisional. HCED promotion requires nonduplicate records, an outcome aligned to both crosswalk sides, and a unique polity identity valid for the entire event date range. IWD component rows are never promoted individually, because they can repeat one larger war across many dyads. Instead, each IWD parent conflict is reconstructed as two coalitions from its component initiator/target pairs and rated at most once, and only when the reconstruction is defensible: sides must be consistent (an entity coded on both sides quarantines the parent, since no explicit time-bounded side-switch policy exists), component outcomes must be unanimous once oriented to the reconstructed sides (draws and mixed dyad results are never forced into one binary umbrella outcome), no curated seed war may overlap (naming variants are canonicalized so `WorldWarI` matches `First World War`), and every belligerent must resolve to a unique time-bounded identity. Aggregated confidence is reduced when component rows could not contribute, component rows are attached to the event as provenance, and existential or regime-ending severity is never inferred from IWD's outcome codes. Because IWD supplies no per-participant contribution or stakes data, these events use declared uniform defaults — equal contribution shares within each coalition side, the `major_ally` role for every coalition member, one shared outcome vector per side, and `major_war` scale with `major` stakes for every parent — rather than invented differentiation.

Candidate-specific corrections are permitted only through a complete row
fingerprint plus an explicit reviewed binding. The current mainland Southeast
Asia tranche uses that mechanism to distinguish Filipe de Brito's Syriam
regime from Portugal and to preserve the attested 1568–1569 Ayutthaya span.
Generic aliases are not added, transition years remain closed, and conflicting
Bangkok 1688 evidence stays unrated rather than being converted to a draw or
silently inverted.

HCED rows lacking Seshat coding on one or both sides are retried in a second,
declared label-resolution pass. The coded pass, IWD aggregation, and label pass
remain strictly ordered. HCED label policies, the faction blocklist, and the
pending-split set are authoritative front gates; exact alias tiers require one
identity valid across the full event interval. Deny windows apply everywhere:
`Turkey` never resolves for an event intersecting 1919-1923. Curated
wrong-actor, wrong-outcome, date-error, and duplicate assertions are counted
and staged, never rewritten. Label-pass source observations require name
coherence, and accepted label rows never feed observations back into the
resolver. Same-name same-year label rows use their preserved source-record ID
as a disambiguator, so distinct engagements such as both Breslau actions of
1757 do not depend on source order. Label-resolved events retain their lower
identity confidence and per-side resolution provenance.

For post-1500 HCED rows only, an otherwise unresolved side can be interpreted
as a coalition when the source label contains an explicit comma, semicolon, or
ampersand. Plain `and` is never split because it occurs inside polity names.
Every delimited member must independently pass the ordinary label resolver for
the full event interval, every resulting identity must be distinct, and the
normal guard still rejects an identity appearing on both sides. Before the
coalition is built, the same shared pre-1500 and Wave 7 supersession inventory
used by the release post-pass remaps obsolete source identities to their one
time-valid canonical target. This admits 21 current events from 1658–1983,
including four Boer-War composites canonicalized to
`orange_free_state_1854`, while admitting no pre-1500 event and leaving the
frozen ancient cohort unchanged.

The Mexican Seshat-code policy is likewise interval-specific: it resolves to
the Mexican Republic for 1824–1863 and to the reviewed modern series from 1868,
while a shared `mexico` deny window forces every label pipeline to fail closed
for 1864–1867. Resolution is only an identity gate, not automatic acceptance.
Newly resolvable Argentine and Triple Alliance rows remain exact curated
exclusions when the source omits a principal coalition member, assigns the
wrong state actor, inverts the result, or duplicates a stronger event record;
the IWD Triple Alliance parent is withheld because its component graph omits
Uruguay.

IWD and IWBD deliberately call the lower alias tiers directly. They enforce
deny windows but bypass the HCED-only label policies, faction blocklist,
pending-split set, and observation-coherence guard. This preserves their
established promotion contract but can resolve a broad Cliopatria envelope
where HCED would stage the same bare label (for example `Spain` in 1909). The
asymmetry is regression-tested and must not change incidentally in a refactor.

Wave 5 adds a still narrower exception mechanism for reviewed transitional
records. Eight IWD parents are bound by complete parent/component fingerprints,
and 20 IWBD battles are bound by exact candidate fingerprints and exact entity
IDs. The complete cohort must be present and unchanged; a missing sibling,
source drift, or identity drift makes the build fail. These contracts cover the
Bourbon Restoration, the Russian SFSR with the first Estonian republic and
Poland, the Turkish National Movement, the Republic of China on Taiwan, and
one 1870 Orleans battle. They do not become aliases or generic country windows.
In particular, an exact reviewed Turkish contract may name the Turkish
National Movement while uncontracted `Turkey` records intersecting 1919-1923
remain denied.

The initial Wave 8 bundle extended that fail-closed mechanism to 46 HCED rows through candidate-keyed exact contracts. Every contract pins the complete queue-row hash, canonical event, dates, sides, time-bounded entity IDs, and evidence set; none creates a generic alias or lets an umbrella ethnonym confer identity or rating on a local band, coalition, or successor. Four exact contracts use documented outcome overrides with named direct sources. Sixteen additional reviewed rows remain explicit fingerprinted holds because they are massacres or other noncompetitive records, or because the exact actor, coalition, or outcome is unresolved; they are never converted into draws or inferred victories. Continued Wave 8 review uses the same exact, alias-free contract pattern.

IWBD battle rows enter only as tactical engagements. Exact normalized names
are compared with curated seed events, non-curated-excluded HCED candidates,
and prior accepted IWBD rows within one year. Cross-source names canonicalize
ordinal spellings (`1`, `1st`, `first`). A broader base-name match requires one
recognized terminal ordinal/part path to be a strict extension of the other,
and the promoted HCED event must have the same resolved outcome sides in the
same calendar year. This closes the measured 29-pair gap without conflating
adjacent years or different suffix branches; arbitrary terminal numbers are
not stripped.
Within-IWBD keys retain the exact canonical ordinal so numbered battles remain
distinct. Campaign umbrellas,
malformed IDs, mismatched victors, coalition/composite labels, unresolved
identities, and `Turkey` rows intersecting 1919-1923 stay staged. The
war-level victor is ignored, day precision is preserved, and tactical severity
is capped at limited.

UCDP conflict-termination records are promoted only at the conflict-episode level; the dyad-level file is a consistency cross-check, never a promotion unit, because dyad rows are the component layer of one conflict episode and promoting them would enter one episode several times. Only terminal episodes with victory outcome codes 3 or 4 produce events: peace agreements, ceasefires, low-activity endings, and actor cessation all stay staged under named counters, because peace is not a loss, low activity is not an outcome, and actor cessation is ambiguous. Every primary party on both sides must resolve to a unique time-bounded identity for the full episode span: state parties through explicit Gleditsch–Ward code policies — authoritative tables with deliberately absent windows, exactly like the COW-code policies, so for example "Government of Afghanistan" resolves to nothing in 1979 rather than bridging four regimes — or exact time-valid alias matching, and non-state primaries only through conflict-scoped curated actor policies whose windows are the actor's attested existence bounds and whose keys bind to one conflict ID, so a homonymous actor label in a different conflict never resolves; the government side must independently resolve. The event's war type follows the source's `type_of_conflict` under an exhaustive declared mapping, and unmapped types are rejected rather than coerced. An otherwise-promotable episode is still rejected when it duplicates an already-promoted strategic event by shared entities and overlapping years; when a terminal dyad row of the same conflict contradicts it, either through an opposite-orientation victory or a same-pair negotiated termination (mixed evidence is quarantined, never forced into one binary umbrella outcome); when a victory assertion elsewhere in the file with the same episode end date orients a shared entity oppositely — this linked-episode rule quarantines the Israel–Jordan front of the 1967 Six-Day complex, whose fronts are mutually contradictory in the source and whose other fronts must independently pass the identity and linked-evidence gates; or when it carries a documented side-attribution dispute recorded as a curated exclusion. An accepted episode whose sibling episode deduplicated against a ledger war event inherits that event's cluster identifier, so episodes of one conflict share one diminishing evidence-weight schedule even across sources. Severity is capped at limited, existential or regime-ending consequences are never inferred from termination codes, and secondary supporters are recorded as provenance only — attaching a win/loss vector to a supporter whose individual result the source does not assert would invent an outcome.

These filters make the build reproducible; they do not substitute for claim-level human adjudication or make the release comprehensive.

## Event hierarchy and double-counting

```text
war
└── campaign / operation
    └── engagement / battle / siege / raid
```

- Engagements update only the tactical layer.
- Campaigns update only the operational layer.
- Completed-war outcomes update only the strategic layer.
- A battle can be nested within a campaign and war, but it is never inserted twice into the same rating stream. Enumerated campaign envelopes that duplicated rated components (including Liaoshen, Huaihai, Beijing-Tianjin, Poland 1939, France 1940, Norway 1940, Sevastopol 1854-55, and Galicia 1914) are counted curated exclusions.
- Events sharing a war cluster and rating layer each receive evidence weight `n^-0.5`, where `n` is that cluster's event count. The same factor scales Elo movement, uncertainty reduction, effective evidence, and cumulative achievement so a richly documented war cannot manufacture hundreds of independent observations.
- When exact dates are unavailable, same-year records use a stable `(end year, start year, event id)` order; source-file row order is never treated as chronology.
- One-sided violence against civilians is not a competitive match and is never scored as a victory.
- Ongoing, disputed and excluded records are visible to the review process but are not rated as completed outcomes.

## Outcomes are vectors, not a win/loss switch

Tactical events use:

- battlefield control;
- mission objective;
- force preservation;
- positional gain.

Operational events use:

- campaign objective;
- theater control;
- force preservation;
- tempo and initiative;
- logistics and sustainment.

Strategic events use:

- battlefield outcome;
- documented political-objective attainment;
- territorial outcome;
- sovereignty/regime survival;
- settlement durability;
- force preservation.

Every value is coded from 0 to 1 from that participant's perspective. The strategic weights change by war type. An intervention or insurgency emphasizes political objectives; a conquest emphasizes territory and sovereignty; a world war gives more weight to state/regime survival.

Uncertain evidence is pulled toward 0.5 rather than converted to a confident win, loss or draw:

```text
adjusted utility = 0.5 + (coded utility - 0.5) × evidence confidence
```

An unknown outcome remains unknown and is not rated until reviewed.

## Result classes

The displayed result class is separate from its numerical utility and importance.

| Actual score | Default class |
|---:|---|
| 0.00–0.05 | Existential defeat |
| 0.05–0.20 | Major strategic defeat |
| 0.20–0.40 | Limited defeat |
| 0.40–0.47 | Negotiated disadvantage |
| 0.47–0.53 | Stalemate or inconclusive |
| 0.53–0.60 | Negotiated advantage |
| 0.60–0.80 | Limited victory |
| 0.80–0.95 | Major strategic victory |
| 0.95–1.00 | Existential/terminal victory |

Curators may apply a more precise class when the historical termination is known, such as withdrawal, capitulation, imposed settlement, low activity, annexation, or actor ceasing to exist.

## Why Vietnam and Germany in 1945 are different

The U.S. in Vietnam can receive a major strategic defeat because its principal political objective failed and it withdrew. Its battlefield performance, homeland sovereignty and regime survival are separately coded, and its participant-relative stakes and national scale are below an existential total war.

South Vietnam can simultaneously receive an existential defeat because the state ceased to exist. North Vietnam can receive a decisive strategic victory because its principal objective was achieved. Germany in 1945 receives a much larger terminal-defeat treatment because the event involved capitulation, occupation, regime destruction, loss of core territory and total-war national stakes.

Thus participants in the same war need not receive mirror-image labels, and two entities both called “losers” need not receive remotely equal consequences.

## Expected result and context

For a pair of opposing participants:

```text
expected = 1 / (1 + 10 ^ (-(rating difference + context adjustment) / 400))

actual = 0.5 + 0.5 × (participant utility - opponent utility)
```

Context can include only sourced values:

- force-size ratio, capped so disputed ancient estimates cannot dominate;
- home/away advantage;
- coalition contribution and role.

A favorite with a large force should gain less for an expected victory, while an underdog should gain more for an upset. Missing context is left missing; it is not imputed as a hidden fact.

## Scale, stakes and participant importance

Event-wide scale is classified as skirmish, battle, campaign, theater, major war or total war. Event-wide stakes are low, limited, major or existential. Each participant can additionally have 0–1 values for its own stakes and national share committed or affected. Geographic/system scope is also 0–1.

Participant importance is:

```text
M = clip(0.25, 3.00,
         0.25 + 1.25 × participant stakes
              + 0.90 × national scale
              + 0.60 × geographic scope)
```

The rating update uses only a bounded square-root-like information adjustment, so one giant war cannot erase an entire prior history. Cumulative achievement uses the full participant importance. Raw deaths are not used as a cross-era importance scale; ancient and modern casualty estimates are not commensurable.

## Coalition handling

Coalition credit is based on a participant's documented contribution and role. Default role multipliers distinguish coalition leads, major allies, supporting allies, expeditionary contingents and proxy sponsors.

Pair weights are normalized within each opposing side, so adding a list of tiny or duplicate allies cannot manufacture extra rating points. Pairwise updates conserve total rating points. Participant-specific utilities, stakes and contribution still produce different consequences for allies on the same side.

## K factor

The layer base is multiplied by bounded factors for event scale, stakes, decisiveness, evidence confidence and duration:

```text
K_event = clip(16, 384,
  K_layer × scale × stakes × decisiveness × confidence × duration)
```

Current bases are 112 tactical, 136 operational and 168 strategic — a
uniform 4x rescale of the v0.2.0 bases (28/34/42, clip 4–96) adopted in
model v0.3.0 so rating movements are legible at dashboard scale. The
rescale is proportional across layers and bounds: win expectations, rank
ordering, and the multiplier stacks are unchanged, only point magnitudes
grow. The bases are model parameters, not historical facts, and must be
calibrated on chronological holdouts as the adjudicated dataset grows.

## Uncertainty and inactivity

Every new entity begins with rating uncertainty 350. Evidence reduces uncertainty; elapsed inactive time increases it without changing the mean rating. Peace is not recorded as a loss, and the absence of records is not treated as victory or deterrence.

Routine builds can run seeded Monte Carlo sensitivity simulations. Low-confidence outcome dimensions are perturbed more than high-confidence ones, and plausible model weights are sampled. The output includes median, 10th–90th percentile, median rank and probability of a top-ten finish. A production release should use at least 1,000 simulations and source-family/bootstrap and entity-boundary alternatives.

An entity reaches the model's coverage threshold only after at least five effective events, three effective completed-war observations and composite uncertainty no greater than 200. This is a statistical sufficiency label, not a claim that its identity or every underlying historical judgment has been fully established. Other rankings are marked low coverage or provisional.

## Disconnected networks and cross-era comparison

If two entities have no path through shared opponents, their raw Elo difference is not identified by the data. The engine assigns a network component and publishes a warning. The historical-success index uses percentiles within each connected network rather than pretending that an ancient isolated rating and a modern global rating share a directly observed scale.

The index is:

```text
40% peak percentile
+ 35% sustained percentile
+ 25% cumulative achievement percentile
```

For provisional actors, that raw index is shrunk toward 50 using effective event count, effective completed-war evidence, opponent-network size, and the fraction of maximum uncertainty that the evidence has actually resolved. This prevents a polity with one surviving victory record—or hundreds of correlated records from one famous war—from appearing as a certain all-time leader. Both the raw percentile index and the coverage-adjusted headline remain available in the generated data.

Peak, sustained and achievement remain separately visible. No single index is presented as objective truth.

## Bias controls

The project must publish coverage by century, region, war type, domain and source quality. Known risks include survivor/victor bias, Eurocentric and modern over-documentation, famous wars being split into more records, non-state actors being omitted, and copied web pages masquerading as independent sources.

Controls include immutable raw snapshots, claim-level provenance, source-family deduplication, explicit missingness, review queues, blind adjudication samples, alternative entity boundaries, region/source-language checks and leave-one-dataset-out sensitivity runs. Automated extraction proposes records. A narrow, declared ruleset may promote source assertions into the provisional ledger, but this status is never represented as human approval of identity, objectives, or strategic interpretation.

## Validation

The automated suite checks rating conservation, successor resets, coalition behavior, confidence shrinkage, force advantage, and terminal-versus-limited defeat magnitude. Planned calibration checks include same-period order sensitivity, duplicate ingestion, chronological Brier/log loss, calibration by era/type, source-family bootstrap and comparison against Glicko/dynamic Bradley–Terry variants.
