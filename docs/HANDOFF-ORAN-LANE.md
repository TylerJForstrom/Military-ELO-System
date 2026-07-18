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

## Resolution (2026-07-18)

The Egypt pin and validator were looking at different artifact stages. The
builder passed `wave8_egypt_forces_existing_events`, a 5,181-event mid-chain
duplicate-detection view that projected 56 audited Egypt events. Commit
1382087 minted the 57-event pin from the final 5,412-event release. The missing
audited event was the later Macedon lane's Andros event, whose participant is
`ptolemaic_egypt_305_bce`; neither Oran event carries an audited Egypt identity.

Both Egypt validators now run immediately after the final `all_events`
assembly and receive that complete ledger. The count, event-ID digest, event
projection digest, entity boundaries, and duplicate guards remain unchanged;
only the validated view was aligned with the stage from which the audit was
minted.

The Oran release is complete and verified:

- 5,414 events, 5,150 HCED bindings, and 782 reviewed candidate contracts;
- 4,794 points, 5,055 country assertions, and 5,104 provenance objects;
- exact `algeria` absent from both the current funnel and all entity aliases;
- dashboard rebuilt with 1,000 simulations and audit status 0 findings / 0
  warnings;
- 1,979 tests passed with 5 skips, including the 16-test Oran suite;
- both corpus-lock modes verified 38 raw files and all 11 generated queues;
- ingestion, coverage, dataset-gap, and funnel reports regenerated, with
  `git diff --check` clean.

Next work is `HANDOFF-EXACT-OUTCOME-LANES.md` Lane 2 (Cheyenne Dog Soldiers),
followed by Lane 3 (Libya Chad-war rows with Erdi-style reversal
dispositions).

Invariants: unknown is not a draw; no algeria alias ever; no window
changes; commit as Tyler Forstrom, conventional messages, no attribution
trailers; never stage .claude/, .local-handoff/, build/, data/raw/,
data/review/.
