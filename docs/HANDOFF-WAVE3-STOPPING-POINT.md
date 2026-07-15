# Handoff: wave 3 audited HCED location metadata

This is the pickup point after the audited HCED location-metadata tranche.
Start from the tip of `codex/wave3-audited-evidence-location`, verify that the
worktree is clean, and read this file with `docs/HANDOFF-REVIEW-TRIAGE.md`.

## Published scope

This tranche adds source-transcribed HCED location metadata to the 4,012
already-rated HCED events. It changes no event eligibility, outcome,
participant, entity, ordering, rating update, simulation, leaderboard, or Elo
value. No new event or entity becomes ranked.

The release-to-candidate join is an exact 4,012-to-4,012 bijection: 1,769
crosswalk-resolved HCED events and 2,243 label-resolved HCED events, with zero
missing, ambiguous, or colliding bindings.

After fail-closed quarantine:

- 3,978 of 4,234 rated events carry a source-transcribed GeoJSON Point
  (`93.953708%`);
- 3,934 carry a source-transcribed modern country/geographic-jurisdiction
  label (`92.914502%`); and
- 3,980 carry at least one location field and the closed HCED provenance
  object (`94.000945%`).

These are field-presence counts, not verified-location coverage. Verified
historical location coverage remains unavailable. Every published value is an
`unreviewed_source_assertion`; coordinate precision and accuracy are unknown.
Quarantined values are omitted, never corrected, swapped, normalized,
reverse-geocoded, rounded, or inferred.

The closed provenance object contains exactly:

- `source_id: hced_dataset`;
- the exact HCED `source_record_id`;
- `assertion_status: unreviewed_source_assertion`; and
- `coordinate_precision: unknown`.

`modern_location_country` is never repurposed as `location_name`, and Points
always use `[longitude, latitude]`.

## Quarantine manifests

The policy withholds 34 Point fields and 77 country/jurisdiction fields across
79 unique events; 32 events occur in both manifests. One additional event has a
source-blank country field, which remains absent rather than becoming an
inferred value.

- Point candidate-ID manifest, sorted-newline SHA-256:
  `0f41aba5dda824cabdca7da7f0d6c156489e3a16397ad70187b23bccd013fdb2`
- Country candidate-ID manifest, sorted-newline SHA-256:
  `ea6e8ac15e6e8426a574471cb4e30dc050eb8bef3f11589a44a4487d24f5dd6d`
- Combined candidate/field/reason policy digest:
  `3cde3666cdb5ced040306cc25cba153b9f73fe49f04703ac864e889a1399dc7d`

The authoritative HCED review queue SHA-256 remains
`7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf`.

## Country/jurisdiction semantic boundary

A separate 47-row disputed or non-sovereign jurisdiction review produced no
additional quarantine in this wave. Two rows were already withheld for
independent reasons and 45 remain published. Those retained strings are exact
HCED geographic-jurisdiction labels, not assertions of sovereign-country
status. The 47-row manifest SHA-256 is
`634de385cc61446df6427ae8a63a83defbaf96efd1fc0276111a9d1fc68992df`.

Do not describe the 3,934-field numerator as sovereign-country coverage. A
future strict sovereign-country policy would be a separate reviewed decision.

## Evidence-store blocker

No claim-bearing research-packet evidence store was added or populated. The
existing claim/adjudication infrastructure is not authorization to import
those packets.

Safe population remains blocked because the packet sources are not available
as immutable artifacts bound to an authenticated source-version registry. A
future loader must recompute artifact and extraction bytes, require an exact
typed page/span/cell locator, bind content-derived identifiers, and compare
against an expected manifest digest supplied outside the store. Until those
prerequisites exist, no research-packet claim rows should be committed.

## Rating-neutral versus score-changing work

This wave intentionally uses exact rating equality as a safety oracle. Location
metadata can improve event description, search, geographic quality review, and
future stratified coverage analysis, but it cannot legitimately change who won,
who participated, whether an event is rateable, or how its Elo update is
computed.

The next score-changing wave is outcome and participant adjudication: resolve
the confirmed historical-error inventory, human-review eligible staged events,
deduplicate overlapping source records, promote only defensible candidates,
then rebuild ratings with an event-attributed before/after report. Return first
to the two policy-boundary defects, the IWBD-HCED deduplication gap, the
label-pass duplicate-key collision, the confirmed ledger outcome/identity
errors, and the test gaps in `docs/HANDOFF-REVIEW-TRIAGE.md`. Do not alter the
six refuted findings.

## Headline invariants

The coupled rebuild must preserve:

- 226 rated entities;
- 4,234 rated events: 40 seed, 1,769 crosswalk HCED, 2,243 label HCED,
  54 IWD, 121 IWBD, and 7 UCDP;
- 89 release sources;
- 1,590 registry identities;
- 27,014 staged records;
- 23,390 event-like candidates;
- 19,163 unresolved candidates;
- 4,194 events with one explicit outcome-source family and zero events with
  independently established multiple-family outcome support; and
- the 1,000-simulation dashboard.

Any deviation is a blocker rather than a new documentation pin unless the
change is independently explained and reviewed.

## Verification record

The final coupled release must record all of these gates before this handoff is
published:

- corpus lock: 12 raw snapshots and 10 review queues verified;
- release audit: `[]`;
- full test suite: final measured pass/skip counts;
- dashboard: 1,000 simulations and release parity clean;
- rating projection: exact equality with the Wave 2 baseline after removing
  only the new HCED binding/location/provenance fields and allowed coverage
  metadata;
- deterministic rebuild: byte-identical generated artifacts from identical
  inputs; and
- browser: real data loaded, the visible HCED warning appeared, representative
  quarantine values stayed withheld, interactions worked, and the console was
  clean.

## Machine-local rebuild warning

Managed worktrees do not contain the authoritative review corpus. On this
machine, release-touching commands must explicitly use:

`C:\Users\tforstrom\Desktop\ELO system\data\raw`

and

`C:\Users\tforstrom\Desktop\ELO system\data\review`.

Verify the 12-raw/10-review lock, then rebuild `data/release`,
`data/catalog/registry.json`, and `web/data/results.json` together, with the
dashboard explicitly using `--simulations 1000`. Re-run the audit, full suite,
numeric oracle, coverage report, deterministic build comparison, and browser
check, then synchronize every current count and digest pin from that one
measured build. Never stage `data/raw`, `data/review`, `.local-handoff`, `build`,
or machine-local reports.
