# Pinning discipline

Rules distilled from the failure classes that have actually cost repair
sessions. Every lane author and every pin refresh must follow them.

## 1. Never pin a moving artifact from a fixed test

build/hced-unresolved-label-funnel.json and every "current release"
projection are LIVE views: correct behavior removes rows the ledger
publishes and labels that policies resolve. A test that asserts its
cohort still appears there is stale the moment any later lane lands.

- Historical pre-promotion state belongs in an inline historical
  projection or a WAVE8_*_FUNNEL_AUDIT constant inside the lane, asserted
  exactly (same counts, digests, failure shapes).
- The live artifact gets exactly one kind of assertion: the completed
  cohort is ABSENT (bohemia pattern, with a clear message).
- Promoter, tamper, and duplicate-audit tests run against a
  pre-integration view (the lane's promoted candidate ids and event-id
  prefix filtered out) so each mutation reaches the guard it names.
  Current-release integration is asserted in its own all-or-none test.

## 2. A current-state pin names its artifact stage

When a lane pins "the current release" (count + digests), the pin must
record WHICH view it hashes - the final published events.json, or a
specific mid-build stage - and its validator must be fed exactly that
view. The staged Oran lane stalled because a 57-event audit minted from
the published ledger was validated against a different in-build event
list. When refreshing such a pin, mint it from the same call site that
will verify it.

## 3. Pin refreshes travel with their seals, atomically

Audited constants are covered by final audit signatures that fail closed
at import. Any refresh must land the new values and the re-minted
signature in the same edit session; between the two, every module that
imports the promotion package is broken for every other worker. Compute
the new signature with the module-level validation call temporarily
suspended, restore it immediately, and update source and test pins in
one commit.

## 4. Resolve pin conflicts by finding the generator, not by vote

When a pinned value disagrees with a measurement, locate the code that
WRITES the value (the registry generator, the coverage builder) before
choosing sides. The reviewed-contract pin was once "reconciled" to the
marker census (777) when the generator counts contract emissions (780);
the error surfaced only at the next regeneration. Generated artifacts
are never hand-patched to agree with a pin - regenerate them.

## 5. Builds run their documented parameters

The dashboard contract is 1,000 simulations; the build script's default
is lower. Any rebuild that feeds a commit passes --simulations 1000
explicitly and re-checks meta.simulations, audit errors, and audit
warnings in the output before the artifact is staged.

## 6. Count every cascade site before committing a promotion

A promotion moves, at minimum: the hced_location constants, the
orchestrator tranche literals, the registry coverage block, the seven
registry-snapshot lane suites, the shared suites (m4, wave4 families,
coverage, funnel, label resolution, location artifacts including the
oracle digests), both funnel artifacts, and the count-bearing docs.
Grep for the old values after the rebuild; a leftover literal is a
future red suite. The full suite plus verify_corpus_lock (both modes),
report_ingestion, report_coverage, and the ledger SHA check are the
gate - never push on a subset run.

## 7. Windows tooling hazards

PowerShell 5.1 corrupts this repository in three specific ways: commit
messages containing quotes must go through git commit -F file; stderr
redirects write UTF-16 files; Set-Content -Encoding UTF8 prepends a BOM
to Python files. Edit files with proper tooling, and keep JSON
re-serialization away from committed artifacts (string-surgery preserves
formatting; a load-dump cycle rewrites every line ending).
