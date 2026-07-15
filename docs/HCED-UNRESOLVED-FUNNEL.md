# HCED unresolved-label funnel

The funnel is a release-neutral planning report for the HCED label pass. It
uses the same seed identities, Cliopatria candidates, crosswalk observations,
deny windows, Wave 6 contracts, reservations, and curated exclusions as the
release builder. It does not edit identities and does not write the release,
registry, or dashboard.

Run it after the machine-local review queues have been restored:

```powershell
$env:PYTHONPATH = "src"
python scripts/report_hced_funnel.py `
  --review data/review `
  --ledger-events data/release/events.json `
  --output build/hced-unresolved-label-funnel.json `
  --batch-size 50
```

The JSON has no timestamp or machine-specific path. Its five input SHA-256
values make two reports comparable. A second run over byte-identical inputs is
byte-identical.

## Counts and failure cases

`events_touched` is the number of distinct HCED candidate rows containing the
normalized label as a `no_unique_time_valid_label_match` failure.
`sole_blocker_events` is stricter: the row has exactly one unresolved side
occurrence, that occurrence is the label, the other side resolves, and no
known outcome, duplicate, curated, code, or policy gate prevents it from
entering the planning universe. These are identity-stage upper bounds, not
automatic promotion approvals.

The failure split is counted in unresolved side attempts:

- `zero_time_valid_candidates`: no effective exact-label identity covers the
  full event interval (and the label does not have exactly one known identity
  whose interval is wrong).
- `one_wrong_interval_candidate`: exactly one exact-label identity is known,
  but it does not cover the full event interval.
- `multiple_time_valid_candidates`: more than one identity covers the full
  interval, so choosing one would be ambiguous.
- `policy_denied_window`: a declared deny window blocks the interval.
- `resolver_guard_or_tier_conflict`: the diagnostic sees one interval-valid
  identity but the live tiered resolver still refuses it. This is deliberately
  explicit and must be investigated rather than auto-fixed.

Century counts use `year_best`. Negative years are BCE, positive years are CE,
and the century number is `floor((abs(year)-1)/100)+1`. A literal zero is kept
in `YEAR_0` rather than silently assigned to either era.

## Network score

The rated ledger is converted to an undirected entity graph: all participants
in one rated event are connected. For one label's sole-blocker rows, the
report collects the existing connected components containing the resolved
counterpart entities. If that set contains `k` components,
`components_bridged` is `max(0, k-1)`. Attaching a new identity to one existing
component is therefore zero bridges; joining two previously disconnected
components is one bridge.

The greedy batch is recomputed after every selection. Its lexicographic
objective is:

1. most newly identity-unblocked rows;
2. most current planning-graph component joins;
3. most total events touched;
4. normalized label, ascending, as the deterministic final tie-break.

Rows with two different unresolved labels become available only after the
other label has been selected, so marginal yield can rise during the batch.
Use batches of 20-50, review and implement the accepted identities, rebuild,
then rerun the funnel instead of carrying old headline counts forward.

## Downstream interface

`row_label_data` is the deterministic row-level interface for later war-graph
or evidence scoring. Every row includes its candidate ID, event name and year
interval, raw war names and sides, blocker labels with failure cases, resolved
counterpart entity IDs, other blockers, and `greedy_eligible` status. It does
not perform war-level propagation.

Code can recompute marginal yield from this serialized field without running
the release builder:

```python
from military_elo.promotion.hced_funnel import recompute_hced_marginal_yield

next_batch = recompute_hced_marginal_yield(
    report["row_label_data"],
    ledger_events,
    batch_size=20,
    preselected_labels=already_reviewed_labels,
)
```

The assumption behind selection remains optimistic: a label may require
multiple non-overlapping identities, coalition adjudication, or a policy hold.
The funnel prioritizes review; it never authorizes a timeless alias.
