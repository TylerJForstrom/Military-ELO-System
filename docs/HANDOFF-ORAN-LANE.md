# Contract: finish the Wave 8 Oran exact-outcome lane

Lane 1 of docs/HANDOFF-EXACT-OUTCOME-LANES.md is nine-tenths built and
committed. src/military_elo/promotion/wave8_oran.py is complete and sealed
(final audit signature f7efdc3b...), and its validators are smoke-verified
against the live queue, the live pre-promotion funnel, and the current
release: queue = 2 promotion contracts + 1 hold + 1 existing-release
disposition across the 4 bare-Algeria rows; the promoter emits exactly
hced_wave8_oran_hced_oran1704_1708_1 (year pinned 1708 via
source_date_override with direct date sources, winner Regency) and
hced_wave8_oran_hced_oran1732_1 (winner Spain), geometry and country
retained, zero probable twins. Oran 1780 is held
(insufficient_outcome_documentation - unknown is not a draw). Tindouf 1963
is pinned as already resolved to the modern republic. The orchestrator is
fully wired (import block, reserved-id union, queue validation, entity and
source installs, promote chain spliced between the Achea and Kievan Rus
lanes, four event splices, integration validation, contract-id union,
ledger arithmetic, two registry coverage counts, accepted-events metadata,
and the full metadata audit block).

## The one open issue

`python scripts/build_release.py` currently fails closed in
wave8_egypt_forces.validate_wave8_egypt_forces_identity_boundaries ->
_validate_current_release_event_inventory ("Egypt-related release event
count drifted"). The Egypt audit pin was refreshed to the CURRENT release
(57 events, commit 1382087); the failure fires during the NEW build.
Diagnose which event view the validator receives at that call site: the
Oran events contain no audited Egypt entity, so the count should still be
57 - suspect the validator runs against a mid-build event list whose
composition differs from the final release (for example before later
splices), in which case the correct fix is to compare against the same
projection stage the audit was minted from, or to re-mint the Egypt audit
from the exact view the builder passes. Do not weaken the guard; make the
pinned audit and the validated view refer to the same artifact stage.

## Remaining steps after the build passes

1. Verify the new release: 5,414 events (+2), bindings 5,150, reviewed
   contracts 782, points/countries/provenance each +2, ledger otherwise
   unchanged; regenerate both funnel artifacts (the algeria label must
   disappear).
2. Rebuild the dashboard with --simulations 1000; audit must stay 0/0.
3. Write tests/test_wave8_oran.py on the achea/bohemia template
   (integrated-aware funnel branch: historical WAVE8_ORAN_FUNNEL_AUDIT
   projection + live-absence assertion, pre-integration promoter views,
   tamper tests reaching the named guards, all-or-none release check).
4. Cascade pins: hced_location constants (bindings 5_148->5_150,
   candidate_keyed reviewed contracts 780->782, points 4_792->4_794,
   countries 5_053->5_055, provenance 5_102->5_104), the exact-marker
   census in test_hced_location_artifacts (777->779 and the corrections
   formula), the seven registry-snapshot lane suites, shared suites
   (m4, wave4 families, coverage, funnel, label_resolution), oracle
   digests, and count-bearing docs.
5. Full suite green, verify_corpus_lock both modes, report_ingestion,
   report_coverage, git diff --check, then commit and push.

Then continue HANDOFF-EXACT-OUTCOME-LANES.md Lane 2 (Cheyenne Dog
Soldiers) and Lane 3 (Libya Chad-war rows with Erdi-style reversal
dispositions).

Invariants: unknown is not a draw; no algeria alias ever; no window
changes; commit as Tyler Forstrom, conventional messages, no attribution
trailers; never stage .claude/, .local-handoff/, build/, data/raw/,
data/review/.
