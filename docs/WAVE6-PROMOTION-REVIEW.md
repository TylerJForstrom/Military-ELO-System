# Wave 6 promotion review

Wave 6 is a candidate-fingerprinted, identity-bound promotion tranche. It is
not a claim of comprehensive historical coverage.

## Coupled artifact result

| Metric | Wave 5 | Wave 6 | Change |
|---|---:|---:|---:|
| Rated events | 4,406 | 4,605 | +199 |
| Rated entities | 235 | 288 | +53 |
| Release entity records | 236 | 289 | +53 |
| Registry identities | 1,598 | 1,648 | +50 |
| HCED events | 4,152 | 4,343 | +191 |
| IWBD events | 143 | 151 | +8 |
| Sources / families | 106 / 31 | 205 / 115 | +99 / +84 |

All 4,406 Wave 5 event IDs and complete event payloads are unchanged. The 199
additions are 55 pre-1500 HCED label events, 76 candidate-keyed HCED events
from 1500–1799, and 68 modern additions (60 HCED and 8 IWBD).

## Boundary corrections before publication

The modern proposal was reduced from 90 to 68 after an independent identity
audit. Twenty-two exact contracts remain fingerprinted holds:

- eight post-1882 Egyptian HCED rows;
- six transitional Spanish-government HCED rows;
- IWD parent 55 (the 1948 Arab–Israeli War coalition);
- six 1967 Egypt IWBD rows; and
- one 1967 Syria IWBD row.

Those rows may promote only after an atomic, sourced sequence of time-bounded
identities is reviewed. The build preserves the 1805–1882 Muhammad Ali dynasty
and the existing 1973-open Syria series and prevents modern overrides from
colliding with an existing identity. The First Balkan War contract reuses the
already-rated Montenegro identity.

Five Wave 5 registry-only source candidates are retained as explicit
superseded rows rather than silently removed. Every release identity has a
registry row with exact name, kind, interval, and region parity.

## Measured next-wave accelerators

The unresolved-label funnel is generated with:

```powershell
$env:PYTHONPATH='src'
python scripts/report_hced_funnel.py --review data/review --ledger-events data/release/events.json --output build/hced-unresolved-label-funnel.json --batch-size 50
```

On the locked corpus it measures 3,242 distinct events touched by remaining
no-unique label failures. The greedy top-50 label ceiling is 428 events before
historical review; it is not an approved promotion count.

The co-war report is generated with `scripts/report_war_constraints.py`. Its
strict time-valid, non-conflicting gate finds only 22 rows that become fully
unambiguous through current war-side constraints. Suggestions are read-only
and never enter the rating ledger automatically.

The previously proposed Confederate States shortcut is refuted by the live
resolver. The existing `clio_q81931_1861_f3bc20bd` identity is already bounded
to 1861–1865 and participates in 365 rated HCED events. Adding a second CSA
identity would add zero events and risk a parallel Elo series.

## Rebuild rule

Release, registry, dashboard, documentation counts, and test hashes are one
coupled artifact set. Any release-touching change must rebuild all of them from
the same locked queues and commit them together.
