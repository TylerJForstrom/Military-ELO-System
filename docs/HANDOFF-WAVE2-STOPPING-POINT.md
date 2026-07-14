# Handoff: wave 2 audited stopping point

This is the pickup point after the 2026-07-14 wave-2 review. Start from the
tip of `codex/wave2-audited-stopping-point`, verify that the worktree is
clean, and read this file together with `docs/HANDOFF-REVIEW-TRIAGE.md`.

## Published scope

The stopping point adds an explicit, fail-closed outcome-source contract
without changing rating eligibility, event outcomes, participants, entities,
or Elo values.

- 4,194 of 4,234 rated events have one explicit direct outcome-source family:
  4,012 HCED, 54 IWD, 121 IWBD, and 7 UCDP.
- The 40 curated seed events remain explicitly unmapped until claim-level
  locators and human review exist.
- No rated event has two independent direct outcome-source families. The new
  99.055267% figure measures explicit provenance, not corroboration.
- Crosswalk, registry, dyad cross-check, publisher, URL, and consulted-manual
  links do not count as outcome evidence.
- Headline corpus values remain 226 rated entities, 4,234 rated events,
  89 sources, 1,590 registry entries, 27,014 staged records, 23,390
  event-like candidates, and 19,163 unresolved candidates.

The dashboard and release artifacts must contain the same paired
`outcome_source_ids` and `outcome_source_family_ids` values. A committed
artifact-parity test prevents a stale dashboard from silently rendering all
events as unmapped.

## Deliberately not published

### Proposed 19-event promotion tranche

No candidate in the proposed 19-event tranche was promoted. The provisional
arithmetic would have produced 4,253 events and 231 rated entities, but the
tranche failed the independent historical and governance gates.

Eleven candidates are plausible inputs for a later human-reviewed tranche,
subject to the project's provisional principal-dyad rule and exact identity
policies:

- Miletus 334 BCE, Issus 333 BCE, Sebastopolis 692, Khan Yunis 1516,
  Slaak 1631, Sas van Gent 1644, and The Saints 1782 from HCED;
- Abtao 1866 and Mishan 1929 from IWBD;
- Ecuadorian-Colombian War 1863 and Saudi-Yemeni War 1934 from IWD.

The other eight have specific blockers:

- Megalopolis has a material 331/330 BCE chronology dispute and incomplete
  coalition representation.
- Jaxartes does not justify treating broad `Scythia` as one rated polity.
- Antioch uses a principality identity that incorrectly continues to 1271
  after its destruction in 1268.
- Mons omits French Huguenot participation.
- Steenwijk omits the English contingent.
- Amjhera has a primary-source-based 1728/1729 chronology conflict.
- Abensberg omits sovereign Bavarian and Wurttemberg forces.
- The 1823 Franco-Spanish parent models France against undifferentiated Spain
  despite Spanish royalist co-belligerents; its proposed Bourbon policy also
  includes 1830 while claiming to stop before that transition.

All proposed curated identities, annual code windows, overlap absorptions,
and migrations still require authenticated independent human review. Do not
convert multiple model sessions into the required human approval.

### Seed-event research packets

The two 20-event research packets are review context, not canonical data.
The first-half audit found 0 store-ready claims; 35 of 45 evidence rows had
content verified, but all rows lacked the complete canonical locator. It also
confirmed all 7 declared conflicts and found 5 additional substantive and
1 provenance conflict. The second-half audit found 18 atomic candidates but
0 store-ready rows, 29 verified and 10 failed cited links, 13 confirmed and
1 incorrect declared conflict, and 2 missed conflicts.

Every imported assertion must first be atomized and supplied with a stable
source ID, edition/version, SHA-256 checksum, language, source family, and an
exact page, row, section, or URL anchor. Normalized outcome vectors, inferred
entity substitutions, confidence scores, proxy coordinates, and adjudication
decisions remain scratch work.

Machine-local audit artifacts, when present, are ignored under
`build/wave2/`. Their verified hashes are:

- `seed-research-audit-01-20.json`:
  `ee056ccf93517e565f21eae89eca7716e17874c99dd951b33bd6976a759e44c9`
- `seed-research-audit-21-40.json`:
  `662400b827b3407f39592ccf257650ce18b6a135fda34abd4b8ce6ec60b61661`

### Review-only evidence store

The evidence-store implementation is excluded from this stopping point. Its
arbitrary nested claim-value/precision payload made a vocabulary denylist
inherently fail-open: the audit could still encode review or model decisions
under equivalents such as `verificationStatus`, `curator`, `judgment`,
`machineLearningOutput`, `gptOutput`, `modelVersion`, and `aiAgent`.

Redesign this boundary around a dedicated seed-evidence claim schema with
closed, predicate-specific historical value types. Rendering and loading must
use the same allowlisted contract, and review/decision/model/ingestion
metadata must live outside the tracked evidence store. The loader must also
accept the expanded canonical seed-source pair
`source_family_id`/`evidence_roles` and require locator families to agree with
the referenced seed source. Do not import either research packet merely to
populate the store.

The stopped prototype is uncommitted machine-local scratch in the managed
worktree `C:\Users\tforstrom\.codex\worktrees\ca2c\ELO system`. Preserve it
only as a design reference; do not commit its current denylist implementation.

## Next implementation wave

The next release-neutral candidate is HCED's modern-country and coordinate
metadata for the 4,012 already-rated HCED events, but it needs a quarantine
pass before publication. All 4,012 raw pairs are finite and in range, yet the
audit found one strong likely latitude/longitude swap (`Focchies1649`), nine
coordinate pairs with contradictory country labels across 22 events, and 27
additional country-distribution outliers requiring review. Examples include
source coordinates that place Perimeter (2nd) near Winnipeg, Mitla Pass in
Mexico, Cape St Vincent in Canada, and Huon Peninsula in Tasmania. Decimal
digits are geocoder precision, not historical accuracy.

Do not publish the naive 4,012/4,234 (94.756731%) coverage figure as verified
truth. Preserve the field name `modern_location_country`, quarantine the
likely swap instead of correcting it, and quarantine all 22 contradictory
country assertions. The immediately defensible ceilings are 4,011
source-transcribed Points (94.733113%) before the remaining outlier review and
3,989 uncontested country assertions (94.213510%). Attach explicit HCED
source-record provenance, `unreviewed_source_assertion`, and
`coordinate_precision: unknown`; never relabel a country as `location_name`.
Parsing must reject blank, boolean, malformed, non-finite, out-of-range, and
`(0,0)` pairs, and GeoJSON Points must use longitude then latitude. The model,
schema, engine export, dashboard warning, coverage semantics, quarantine set,
and unchanged Elo projection all require tests before a release rebuild.

After that metadata-only tranche, return to the human-reviewed 11-candidate
subset and the historical-error inventory in
`docs/HANDOFF-REVIEW-TRIAGE.md`. Rebuild and measure; do not adopt the
provisional 4,253/231 arithmetic as a pin.

## Machine-local rebuild warning

Managed worktrees contain only `.gitkeep` under `data/review`. Any
release-touching command must explicitly use the original checkout's locked
raw/review inputs. On this machine the review path is
`C:\Users\tforstrom\Desktop\ELO system\data\review`.

For every release-touching change:

1. Verify the offline corpus lock (12 raw snapshots and 10 review queues).
2. Rebuild `data/release`, `data/catalog/registry.json`, and
   `web/data/results.json` together with `--simulations 1000`.
3. Require `build/audit.json` to be `[]`, run the full test suite, compare
   rating numerics, and verify the dashboard in a browser with no console
   errors.
4. Re-sync every current count and digest pin from that machine's measured
   outputs. Never combine counts from a different discovery queue.
5. Never stage `data/raw`, `data/review`, `.local-handoff`, `build` scratch,
   or machine-local reports.
