# Handoff: Wave 7 audited stopping point

## Pickup

Pull `main`, read this file, and treat the committed release, registry, and
dashboard as one coupled artifact. Wave 7 is deliberately frozen here: every
coherent lane is integrated, the remaining expansion work was stopped before
partial cohorts could leak into the release, and the full regression gate is
green.

The earlier adversarial-review decision record remains in
`docs/HANDOFF-REVIEW-TRIAGE.md`. Its full reasoning is also preserved on this
machine in `.local-handoff/m4m5-review-findings-full.txt`, which is intentionally
gitignored.

## Measured result

Relative to the Wave 6 baseline, the coupled artifact changes as follows:

| Measure | Wave 6 | Wave 7 | Change |
|---|---:|---:|---:|
| Rated events | 4,605 | 4,797 | +192 |
| Rated HCED-derived events | 4,343 | 4,535 | +192 |
| Rated participant identities | 288 | 340 | +52 |
| Release entity records | 289 | 342 | +53 |
| Registry identities | 1,648 | 1,702 | +54 |
| Registered sources | 205 | 284 | +79 |
| Source families | 115 | 176 | +61 |
| Events with an explicit outcome family | 4,565 | 4,757 | +192 |
| Unresolved event-like candidates | 18,789 | 18,597 | -192 |
| Published GeoJSON points | 4,306 | 4,498 | +192 |
| Published modern-location labels | 4,263 | 4,455 | +192 |
| Location-provenance objects | 4,310 | 4,502 | +192 |

The 4,797-event ledger is 40 curated seeds, 1,884 crosswalk HCED, 2,383
label-lineage HCED, 76 Wave 6 candidate-keyed HCED, 192 Wave 7 candidate-keyed
HCED, 64 IWD parent wars, 151 IWBD battles, and 7 UCDP termination episodes.
The dashboard contains 342 entity records and was built with 1,000 simulations.

## Integrated Wave 7 lanes

| Lane | Promotions | Holds | New identities | New sources |
|---|---:|---:|---:|---:|
| Root | 62 | 4 | 9 | 20 |
| Central and East | 33 | 9 | 15 | 13 |
| Central and East, pass 2 | 31 | 11 | 7 | 16 |
| Global and South | 37 | 5 | 8 | 13 |
| Western Europe | 29 | 13 | 14 | 17 |
| **Total** | **192** | **42** | **53** | **79** |

Every promotion and hold is candidate-keyed and fingerprinted. Candidate-keyed
identities are installed only after the generic HCED label pass, so their names
cannot silently widen fallback resolution. All Wave 7 events join the global
HCED deduplication and location-provenance paths before the IWBD stream is
constructed.

Five already-rated Orange Free State events are atomically migrated from the
superseded `clio_q218023_1856_cfb4e08e` envelope to
`orange_free_state_1854`. This is a five-member, all-or-nothing identity
migration, not five new events. The source and final complete-event hashes are
pinned, and the migration is pure and idempotent.

## Historical corrections and deliberate holds

Seven root-lane candidates use reviewed historical outcome sources instead of
the raw HCED outcome assertion: Concord, Onitsha, Burnt Corn, Emuckfaw,
Enotachopco, Buda, and Pákozd. The western lane also pins reviewed claims for
Twt, Bamburgh, Caister, Lose-Coat Field/Lincolnshire 1470, and Bosworth. These
12 events remain HCED-derived candidates but use the reviewed direct-outcome
family in coverage accounting.

The five Orange migrations retain their stable `hced_label_*` event IDs and
label-pass lineage while recording `wave7_candidate_keyed_migration` as the
final identity-resolution method. The other 2,378 label-lineage events retain
the ordinary `label` marker.

The Kadesh proposal remains held; no source-supported winner was invented.
Forty-two additional Wave 7 proposals remain in explicit fingerprinted hold
inventories. Do not convert those holds into promotions merely to increase the
headline count.

Reviewed IWBD companion rows such as Rome/Palestrina/Velletri remain the one
rated representation while their HCED companions stay excluded. Likewise, the
12 bare-`Turkey` IWBD rows in 1919-1923 are permitted only by their exact,
complete candidate cohorts mapping the source assertion to the Turkish
National Movement; uncontracted Turkey labels in the deny window still fail
closed and never attach to the Ottoman Empire.

## Validation record

- `python -m unittest discover -s tests -q` with `PYTHONPATH=src`: 666 tests
  passed; 5 intentionally skipped.
- Ruff formatting and lint: all 26 Python files changed by Wave 7 pass.
- A fresh release/registry build reproduced every committed JSON artifact
  byte-for-byte.
- Dashboard: 4,797 events, 342 entities, 1,000 simulations, and an empty
  `build/audit.json` issue list.
- Coverage: 4,757 provisional source-derived rating events, 40 curated seeds
  without claim-level outcome-family mappings, and 18,597 unresolved event-like
  candidates.

The deterministic committed artifact hashes are:

| Artifact | SHA-256 |
|---|---|
| `data/release/entities.json` | `e8e3a39ed0868b9887f614502f278a8f673059138b8d528f4067968ce8e7acf6` |
| `data/release/events.json` | `f621155055817715ae74f8d525edc211b884da6eea1b98d7ed1241c4bdc41ead` |
| `data/release/metadata.json` | `658083463f602015fc0e32fab68fe52fbe1e1cb85430c6b9d46b8473141994cf` |
| `data/release/sources.json` | `b478031d6e60b60fa653673415af26c7775171257c83dfcdfa03bcbabc7af376` |
| `data/catalog/registry.json` | `b38dba83154647eabfc9653a00825cd8faeec3f90628e5182c366a57d5946685` |

## Machine-local rebuild warning

This machine has an 18-candidate Wikidata discovery queue. Its measured totals
are 27,014 staged source records and 23,390 event-like candidates. Any future
release-touching change must rebuild release, registry, dashboard, and coverage
together on the same machine, use exactly 1,000 dashboard simulations, and
re-sync every current documentation and test count/hash pin to the newly
measured values. Never combine registry or queue totals from a different local
discovery snapshot.

The minimum verification sequence is:

```powershell
$env:PYTHONPATH = "src"
python scripts/build_release.py
python scripts/build_dashboard.py --simulations 1000
python scripts/report_coverage.py --output-dir build/coverage
python -m unittest discover -s tests -q
```

## Next expansion cohorts

Two follow-on batches were identified but intentionally stopped before any
partial implementation was accepted:

- Native North America: Sioux (17 proposals), Apache Indians (10), and Apaches
  (5).
- Colonial and anti-colonial: Xhosa (13), Hauhau Maori (7), Maoris (6),
  Dahomey (5), Matabeleland (4), and Nama tribe (4).

Start them from the current unresolved funnel on `main`. Re-audit each exact
candidate, keep complete promotion and hold inventories, and do not re-promote
any Wave 6 or Wave 7 candidate ID. Separate worktrees are worthwhile only for
disjoint candidate cohorts; integration, release generation, dashboard
generation, and final count reconciliation must remain serialized in one
worktree.

## Remaining limits

This is still a provisional research ledger, not complete history. There are
18,597 unresolved event-like candidates, 40 curated seed events without
claim-level direct-outcome mappings, and no event with two independently
established outcome families. The next useful work is audited coverage growth
and stronger outcome provenance, not inflating confidence or treating unknowns
as draws.
