# Data review and adjudication workflow

## Four data zones

1. `data/raw/` contains immutable downloaded snapshots plus SHA-256, URL, version, retrieval time and license in `manifest.jsonl`.
2. `data/review/` contains machine-extracted candidates. Every candidate is explicitly marked `do_not_rate_automatically`.
3. `data/seed/` contains the manually adjudicated foundation. `data/release/` combines that foundation with strictly filtered, source-derived provisional evidence.
4. `data/catalog/registry.json` contains the wider time-bounded polity registry, including entries with no rating evidence.

Raw facts are never overwritten. Corrections produce a new curated version and preserve the prior decision history.

The current release catalogues 2,361 polity identities and contains 1,013 release entity records, of which 1,006 actually participate across 5,354 rated events. Its 1,450 registered sources span 1,188 provenance families. It reports all 27,014 staged source records separately. The staged total includes identity records and promoted evidence; of 23,390 event-like candidates, 18,040 remain outside the rating ledger. These are different denominators and must never be collapsed into a claim that every catalogued or released polity has been rated.

## Provisional source promotion

The release builder applies a narrow, reproducible filter before any source-derived record can affect a rating:

- HCED encounters must have a valid date, a nonduplicate source ID, both opposing Seshat-coded sides, winner/loser labels aligned to those sides, and one unique time-valid polity for every code. Rows lacking Seshat coding on one or both sides are retried in a second, declared label-resolution pass: a side promotes only through an explicit time-bounded label policy or an exact-normalized, uniquely matching, full-interval-valid alias, with faction and collective-peoples labels blocklisted and multi-regime-envelope labels quarantined pending curated splits. A post-1500 side with an explicit comma, semicolon, or ampersand may resolve as a coalition only when every delimited member independently resolves to a distinct full-interval-valid identity; plain `and` is never split. The shared canonical supersession remap is applied before coalition assembly, and the rule is unavailable to the frozen pre-1500 cohort. Label-resolved events carry a declared lower confidence tier than crosswalk-resolved events — one identity-confidence step per label-resolved side — and an `identity_resolution` provenance marker.
- The initial Wave 8 bundle promoted 46 HCED rows through candidate-keyed exact contracts: 9 in the African-states lane, 15 in New Zealand, and 22 in North America. Continued Wave 8 review uses the same fail-closed contract pattern. Each contract pins the queue-row fingerprint, event key, dates, sides, time-bounded entity IDs, and evidence set. It creates no generic alias and permits no umbrella ethnonym inheritance. Source-backed outcome overrides are explicit; massacre/noncompetitive records and rows with unresolved actors, coalitions, or outcomes remain fingerprinted holds.
- IWD component dyads are rated only through parent-war coalition aggregation: each parent conflict receives at most one strategic update, and only when the reconstructed sides are consistent, the component outcomes are unanimous, no curated seed war overlaps, and every belligerent resolves to a unique time-bounded identity. An entity coded on both sides, a mixed dyad outcome, or an unresolved party quarantines the whole parent. This prevents a single umbrella conflict from generating many strategic updates.
- IWBD battles are promoted only as tactical engagements through a declared ruleset: not a duplicate of any curated seed event, any non-curated-excluded HCED candidate, or an earlier accepted IWBD row (exact normalized names use a year ±1 window; a base-name match requires one recognized ordinal/part suffix path to extend the other in the same year with an agreeing oriented outcome); not a campaign umbrella whose date span contains a differently-named same-war battle; a coded victor matching a named side with an agreeing role; and both sides single polities resolving to unique time-bounded identities outside declared deny windows. The war-level victor code is ignored and severity is capped at limited.
- UCDP conflict-termination episodes are promoted only through a declared ruleset: conflict-level terminal episodes with victory codes 3/4, state primary parties resolving through explicit time-bounded GW-code policies or exact alias matching, no duplicate of an already-promoted strategic event, no contradicting terminal dyad row, no oppositely-oriented same-end-date linked episode, and no documented side-attribution dispute. Secondary supporters are recorded without outcomes, and dyad rows are never promoted.
- Identity resolution in every pipeline runs through curated, time-bounded decisions: seed identities and their code/label policy windows (including the state and non-state actor tranches documented in the entity policy), declared identity deny windows, and enumerated curated row exclusions for known wrong-actor, variant-spelling, and cross-source-duplicate records — counted under named rejection reasons, never merged or fuzzy-matched. Every identity-tranche decision is an entity-boundary decision under the high-impact rule below and remains second-reviewer-pending.
- Mexico's coded and bare-label continuity is bounded to 1824-1863 and
  1868-2024 in the current Cliopatria snapshot; a shared 1864-1867 deny window
  applies to every label pipeline. Passing that identity gate never overrides
  the exact curated-exclusion inventory: incomplete Argentine/Triple Alliance
  coalitions, wrong actors, inverted outcomes, and duplicates remain staged,
  including IWD parent 17 with Uruguay missing from its component graph.
- Participant-specific review remains pending on every provisional event from every source. Battle victory, intensity, or fatalities alone are never promoted into strategic success.

Promoted HCED records are labelled provisional even when they pass the schema audit. The filter demonstrates that the source assertion is internally usable; it is not the same as the claim-level human review below.

## Required review for an event

- Confirm that it is an engagement, campaign or war and link its parent/cluster.
- Resolve every participant to a time-bounded entity.
- Confirm actual opposing interaction rather than assuming every coalition member fought every opposing member.
- Record entry/exit dates, role and contribution.
- Record ex-ante or contemporaneously documented objectives; do not reward retrospective goal narrowing.
- Code every applicable outcome dimension and its uncertainty.
- Record war type, domain, scale, stakes and participant-relative importance.
- Record termination and material consequences.
- Attach independent source families and explain disagreements.
- Exclude one-sided violence, duplicates and unresolved/ongoing outcomes from competitive ratings.

## Confidence tiers

| Tier | Default confidence | Meaning |
|---|---:|---|
| A | 1.00 | Multiple independent high-quality scholarly/primary source families |
| B | 0.80 | Strong academic dataset or source with modest disagreement |
| C | 0.55 | Reputable synthesis or substantial ambiguity |
| D | 0.30 | Single, indirect, partisan or weakly supported account |

Copied pages drawing from the same work count as one source family.

## High-impact decisions

Entity boundaries, existential outcomes, major objective coding and the events producing the largest modeled changes require a second reviewer. A validation sample should be independently coded and inter-rater agreement reported. Reviewers should not see the current leaderboard while adjudicating contested outcomes.

## Reproducible release

A release records the raw manifest, foundation and release checksums, promotion rules and rejection counts, model configuration, audit output, code version and Monte Carlo seed/count. It publishes registry size, rateable-entity count, event count, staged-record and unresolved-event-candidate counts, coverage warnings and sensitivity results alongside rankings.
