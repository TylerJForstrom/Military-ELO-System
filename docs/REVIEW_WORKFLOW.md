# Data review and adjudication workflow

## Four data zones

1. `data/raw/` contains immutable downloaded snapshots plus SHA-256, URL, version, retrieval time and license in `manifest.jsonl`.
2. `data/review/` contains machine-extracted candidates. Every candidate is explicitly marked `do_not_rate_automatically`.
3. `data/seed/` contains the manually adjudicated foundation. `data/release/` combines that foundation with strictly filtered, source-derived provisional evidence.
4. `data/catalog/registry.json` contains the wider time-bounded polity registry, including entries with no rating evidence.

Raw facts are never overwritten. Corrections produce a new curated version and preserve the prior decision history.

The current release catalogues 1,582 polity identities, rates 109 entities across 1,461 events, and reports all 27,014 staged source records separately. The staged total includes identity records and promoted evidence; 21,941 event-like candidates remain outside the rating ledger. These are different denominators and must never be collapsed into a claim that every catalogued polity has been rated.

## Provisional source promotion

The release builder applies a narrow, reproducible filter before any source-derived record can affect a rating:

- HCED encounters must have a valid date, a nonduplicate source ID, both opposing Seshat-coded sides, winner/loser labels aligned to those sides, and one unique time-valid polity for every code.
- IWD component dyads are rated only through parent-war coalition aggregation: each parent conflict receives at most one strategic update, and only when the reconstructed sides are consistent, the component outcomes are unanimous, no curated seed war overlaps, and every belligerent resolves to a unique time-bounded identity. An entity coded on both sides, a mixed dyad outcome, or an unresolved party quarantines the whole parent. This prevents a single umbrella conflict from generating many strategic updates.
- IWBD and UCDP records remain candidates until their layer, identity, and participant-specific outcomes can be established. Battle victory, intensity, or fatalities alone are not promoted into strategic success.

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
