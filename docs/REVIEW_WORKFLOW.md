# Data review and adjudication workflow

## Three data zones

1. `data/raw/` contains immutable downloaded snapshots plus SHA-256, URL, version, retrieval time and license in `manifest.jsonl`.
2. `data/review/` contains machine-extracted candidates. Every candidate is explicitly marked `do_not_rate_automatically`.
3. `data/seed/` (and later `data/curated/`) contains approved, sourced entities and events accepted by the audit.

Raw facts are never overwritten. Corrections produce a new curated version and preserve the prior decision history.

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

A release records the raw manifest, curated-data checksum, model configuration, audit output, code version and Monte Carlo seed/count. It publishes coverage and sensitivity results alongside rankings.
