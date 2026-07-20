# Contract: exact-outcome lanes and deferred follow-ups from the funnel tranche

The funnel-ranked identity tranche (greedy batch ranks 1–20) landed fifteen
label policies and eleven curated identities, promoting 58 events. Three
labels from the researched batch and four row-level follow-ups were
deliberately deferred because they cannot ride the label tier: their adjudicated
outcomes reverse the HCED source coding, or they collide with frozen-lane
record precedence. Each needs the candidate-keyed exact-contract treatment
(wave8 lane pattern, one lane per cohort, fingerprinted rows, explicit
conflict dispositions).

## Lane 1: Regency of Algiers Oran cohort (label "algeria", 3 rows)

Bind per-candidate exact contracts only; never register an "algeria" alias and
never change any identity window. Target identity:
`dey_regency_of_algiers_1671_1830` (registered, rated).

- `hced-Oran1704-1708-1` — Siege of Oran, active phase November 1707 to April
  1708. Winner: side_1 (Regency of Algiers), high confidence. Pin the event
  year 1708 explicitly with rationale; do not inherit the midpointed
  year_best 1706.
- `hced-Oran1732-1` — Spanish reconquest of Oran, 1732. Winner: side_1
  (Spain), high confidence.
- `hced-Oran1780-1` — NOT SCORABLE. No dedicated scholarly account of a
  discrete 1780 engagement exists; the coding rests on fallible reference
  transcription. Hold or exclude with that rationale; do not promote.

## Lane 2: Cheyenne Dog Soldiers cohort (label "cheyenne", 3 rows) — COMPLETE

Register `cheyenne_dog_soldiers_band_1849_1869` (window 1849–1869) with
per-candidate binding only — no global "cheyenne" alias ever. Coordinate with
the frozen `wave8_algiers_cheyenne` module, which forbids generic cheyenne
entity naming and pins its own inventory; run its validators before and after.

- `hced-Beecher Island1868-1` — winner side_1 (United States), high.
- `hced-Beaver Creek1868-1` — winner side_1 (United States), high. Point
  quarantine required for date/location fields.
- `hced-Cedar Canyon1864-1` — NOT SCORABLE: noncompetitive attack on a peace
  village (mirror the Ash Creek 1864 terminal exclusion).

Landed as exact candidate contracts: Beecher Island and Beaver Creek are
high-confidence United States tactical wins; Cedar Canyon is terminally
excluded. The new identity remains alias-free and time-bounded to 1849–1869,
Beaver Creek's Point is withheld while its source country and provenance stay
visible, and the frozen `wave8_algiers_cheyenne` audit signature is unchanged.
The regenerated funnel contains no live exact `cheyenne` label.

## Lane 3: Libyan Arab Jamahiriya Chad-war cohort (label "libya", 3 rows) — COMPLETE

Route to existing `libyan_arab_jamahiriya` (1977–2011) for these candidate ids
only. Two of three adjudications REVERSE HCED winner_raw and therefore require
Erdi-style recorded conflict dispositions inside the contracts:

- `hced-Faya Largeau1983-1` — winner side_1 (Libya, joint Libyan–GUNT force),
  high; aligns with winner_raw. Check the wave8_chadian_rebels
  coalition-ownership rules before binding the GUNT side.
- `hced-Aozou1987-1` — winner side_2 (Libya), medium. Reverses winner_raw
  "Chad" (Clodfelter p. 557 covers only the 8 August capture); adjudicate the
  row as the full two-phase August 1987 engagement (Chadian capture 8 August,
  Libyan recapture 28 August). The row is year-only; do not claim date
  alignment with IWBD twins.
- `hced-Zouar1986-1987-1` — winner side_2 (Chad), medium. Reverses winner_raw
  "Libya"; the Chadian army definitively freed Zouar in January 1987 (IWBD
  twin iwbd-207-80-1651, winner Chad, end 1987-01-02).

Landed as three fingerprinted exact contracts. Faya-Largeau rates the joint
Libyan–GUNT tactical capture through a new alias-free, event-bounded 1983 GUNT
formation. Aozou and Zouar carry explicit reviewed source-conflict
dispositions and preserve their two independent outcome-source families;
their IWBD rows remain non-emitting, and Aozou explicitly makes no date-
alignment claim. The existing Jamahiriya and Chad windows and aliases are
unchanged, the frozen Chadian Rebels signature reproduces before and after
promotion, and the regenerated funnel contains no live exact `libya` label.

## Follow-up A: huang chao policy behind a Tang record-precedence contract — COMPLETE

`huang_chao_rebel_movement` (875–884) is registered but its label policy is
deliberately absent from `HCED_LABEL_POLICIES`. Enabling it makes the Tang
counterpart rows alias-install the raw Cliopatria record for
`clio_cn_tang_dyn_1_623_3e98c37b` BEFORE `install_wave8_goguryeo_entities`
installs the lane's curated enrichment of the same identity, and the equality
guard in `install_exact_entities` fails closed ("entity collision"). Options,
in preference order: (1) pre-seed the curated Tang record so the alias tier
takes the merge branch, then align the Goguryeo fixture's aliases with the
merged record and its lane pins; (2) an orchestrator-level curated-record
precedence rule. Either way the decision must be recorded as a contract; the
three source rows (Guangzhou 879 → Huang Chao; Liangtian 883 and the HCED
year-only Chenzhou 883 row → Tang, all high confidence) are already
adjudicated. No wider chronology is imported into the year-only source row.

Landed through the preferred first option: the exact curated, alias-free Tang
payload is pre-seeded before source-candidate materialization, and a fail-closed
precedence contract pins it byte-for-byte to the Goguryeo fixture. The
authoritative `huang chao` policy is limited to 875–884; it promotes exactly
Guangzhou, Liangtian, and Chenzhou with their source-aligned tactical outcomes,
opens no generic Tang or China alias, changes no identity window, and leaves no
live exact `huang chao` funnel label.

## Follow-up B: deferred rows from landed labels

- `hced-Sikasso1887-1888-1` (Siege of Sikasso, winner Kenedougou, high) stays
  staged until a curated `kenedougou` identity (Tieba Traoré's state,
  Wassoulou's enemy — never conflate) is registered and the "kenedougou" label
  resolves.
- `hced-Balapur1720-1` and `hced-Ratanpur1720-1` predate the Asaf Jahi window
  (1724–1948) by curated design; they need a Mughal-era follow-up contract,
  never a widened window.
- `hced-Kharda1795-1` resolves on the Hyderabad side but remains blocked by
  the composite co-label "marathas tukaji hulkar berar".

## Next tranche: greedy batch ranks 21–50

`build/hced-unresolved-label-funnel.json` (regenerate after any promotion)
ranks the remaining unresolved labels; the rank 21–50 window held ~76
additional events at the pre-tranche measurement. The landed tranche followed
this pipeline and it holds for the next one: verify each label's identity
mapping and window against sources, register seed identities (policy targets
that are lane- or crosswalk-installed must be added to
`LANE_OR_CROSSWALK_POLICY_TARGETS` in `tests/test_m4_state_identities.py`),
add windowed `HCED_LABEL_POLICIES` entries, add curated exclusions for any row
whose source coding is inverted, incomplete, or a doublet, then rebuild,
re-measure every count pin, and refresh the dashboard.
