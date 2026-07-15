# Coverage and quality reporting frame

## Purpose

The coverage report measures what the supplied Military History Elo artifacts
actually contain. It does not estimate how much of all military history is
known, how accurate every source assertion is, or how many events truly
occurred.

This distinction is structural. A registry identity, a staged source record,
an event-like candidate, a curated seed record, a rule-promoted event, a rated
event, and a claim-level adjudication are different units. The report keeps
them separate and retains unknown or unclassified values instead of
redistributing them.

## Inputs

The required input is a release directory containing `events.json`,
`entities.json`, and `sources.json`. `metadata.json` is read when present.
Three additional artifacts are optional:

- a `data/review`-style directory of JSONL queues;
- a registry document such as `data/catalog/registry.json`; and
- a rating-results document such as `web/data/results.json`.

The reporter treats every input as read-only. Raw snapshots are deliberately
outside its input contract. A missing optional artifact makes only its
dependent metrics unavailable when the option is omitted. An explicitly
requested path that does not exist or is structurally invalid is an input
error, so a typo cannot silently produce a degraded report.

## Stage scorecard, not a monotone funnel

The report calls this section a stage scorecard because the stages do not form
one cardinality-preserving pipeline.

| Stage | Definition |
|---|---|
| Raw | Physical or logical rows before candidate staging. This is unavailable unless an allowed input declares it explicitly; staged rows are not used as a proxy. |
| Staged | All records in the review queues, including identity and event-like records. Immutable staged rows remain present after promotion. |
| Event-like | Staged rows other than the declared Cliopatria polity and UCDP actor identity queues. Supporting and cross-check rows can still be included, so these are not unique historical events. |
| Unresolved | The release builder's declared count of event-like candidate units remaining outside the ledger. Review `needs_review` flags are not reinterpreted because mechanically promoted rows retain that flag too. |
| Curated seed | Foundation records explicitly identified by the release as curated seed events. This is an observed category, not proof of formal claim-level adjudication. |
| Adjudicated | Events with explicit claim-level adjudication records. The current supported inputs do not contain those records, so this stage is reported as `not_available`. |
| Provisional rated | Source-derived events admitted by the declared mechanical promotion rules but still pending claim-level review. |
| Rated | Complete events in the rating ledger. A missing legacy event status is interpreted as `complete` only for rating scope, matching the model; raw status-field completeness is not imputed. |

IWD illustrates why the units matter. The report independently exposes (1)
component records whose usable evidence contributed to an aggregate, (2) all
component records attached to accepted rated parents for provenance, and (3)
rated parent-war events. Attached and aggregated component counts can differ,
and neither uses the parent-war event as its unit. The report never aliases or
subtracts these counters as if they were interchangeable.

A declared `source_queue_counts` field is authoritative by presence, including
an empty object or an all-zero mapping; the registry declaration wins by
presence over release metadata. An explicitly supplied empty review directory
is an observed zero-record corpus, while an omitted review input is unavailable.
Physical-versus-declared consistency is evaluated whenever both a review
directory and a declaration are present, including these known-zero cases.

## Event profile

Category counts apply to rated events only.

- **Layer** uses the strict mapping `engagement` to tactical, `campaign` to
  operational, and `war` to strategic. Other values remain `unknown`. An
  optional explicit `layer` field does not override this mapping; disagreements
  are reported separately with their event IDs. Tactical, operational,
  strategic, and unknown counts are always emitted, including zeroes.
- **Era** uses neutral numeric analysis periods, assigned once from the event's
  `end_year`: before 500 BCE (`end_year <= -501`); 500 BCE through 499 CE
  (`-500 <= end_year <= 499`); 500-1499; 1500-1799;
  1800-1945; and 1946 onward. These are reporting bins, not a universal
  historiographic periodization. Cross-boundary events are not duplicated.
- **Region** means an explicit event-location region. Participant polity
  regions are not substituted when event geography is absent.
- **Participant-entity region** is a separate, non-exclusive profile. An event
  is counted once for each distinct region represented by its participants, so
  those counts can exceed the event total and must not be read as event
  locations.
- **Domain, war type, and date precision** preserve the supplied categories;
  blanks and missing values appear as `unknown`.
- **Source family** means an explicitly mapped outcome-evidence family. If the
  mapping is absent, the category is unavailable rather than inferred.

## Field-completeness denominators

Completeness describes whether a structured field is present, not whether its
historical assertion is true.

| Field group | Reported checks |
|---|---|
| Dates | Integer start and end years, ordered interval, and explicit date precision, each over rated events. |
| Locations | Generic presence reports named or structured event location, valid coordinate presence, supported GeoJSON geometry containing at least one valid position, and explicit event-region presence. This presence-only aggregate is separate from the HCED status-aware metrics. Provenance-bound HCED coverage reports strict source Points, exact source-transcribed geographic-jurisdiction labels, any surviving HCED location, provenance-object presence, and closed-contract validity separately; it requires an exact candidate binding, linked `hced_dataset` source, and closed unreviewed provenance. Verified-location coverage is `not_available`, never inferred as zero. Generic GeoJSON is validated recursively, including nested geometry collections and closed polygon rings. Positions use longitude then latitude; latitude must be from -90 through 90 and longitude from -180 through 180. The stricter HCED source contract permits only a two-ordinate Point and rejects the source's `(0,0)` sentinel without globally outlawing valid GeoJSON there. Empty, malformed, unsupported, boolean, nonnumeric, non-finite, and wholly out-of-range geometry is absent. `geographic_scope` and entity region are not locations. |
| Participants | At least two participant objects, nonblank entity IDs and sides, and at least two distinct sides. |
| Roles | Explicit participant role presence and role-category counts. Model defaults are not inserted for this measurement. |
| Objectives | Explicit participant objective statements, separately from the layer-specific numerical objective-attainment dimension. An attainment score does not document the objective itself. |
| Hierarchy | Event-level parent-link presence unions `parent_event_id` with `parent_event_ids`; resolution counts distinct child-to-parent references from both fields, deduplicated within each child. Cluster-link presence and either-link presence remain event-based. A missing parent is not automatically an error for a top-level event. |
| Outcomes | Every expected layer-specific dimension, measured by participant and by individual dimension. Missing and null slots remain missing; a value of `0.5` is data, not an unknown marker. |

Every ratio carries `availability`, `numerator`, `denominator`, `value`, `unit`,
and `definition`. A zero denominator produces `not_applicable`; missing
evidence produces `not_available`, never a fabricated zero.

The current status-aware HCED numerators are 4,115 unreviewed source Points,
4,072 source-transcribed geographic-jurisdiction labels, and 4,119 events with
at least one provenance-bound HCED location, all over 4,406 rated events.
Verified-location coverage is `not_available`. The report separately publishes
the frozen policy counts rather than inferring policy from absence: 37 Point
fields withheld by quarantine, 79 country/jurisdiction fields withheld, 33
events in both quarantine manifests, and 83 unique quarantine-manifest events.
One additional event has a source-blank country field and is outside both
manifests. These values describe an audited publication policy; they must not
be reverse-engineered from absent release fields or relabelled as
verified-location accuracy. Retained disputed or non-sovereign labels describe
source geography and are not sovereign-country truth.

## Independent outcome-source families

Source IDs are provenance links, not evidence of independence. URLs on the
same host can represent different datasets, while different URLs can copy one
underlying work. Identity crosswalks also do not become outcome evidence merely
because they appear in an event's `source_ids`.

Likewise, `source_family_id` is first a provenance and deduplication unit. Its
presence does not prove independent corroboration. Independence for a specific
outcome still requires claim-level locators and citation-lineage review; a
family contributes to this report only through the explicit outcome-role
contract below.

For backward-compatible reporting, the reporter recognizes these explicit
inputs:

1. an event supplies `outcome_source_family_ids` or
   `outcome_source_families`;
2. an event supplies `outcome_source_ids` and those sources carry an explicit
   family identifier; or
3. an event's generic source link points to a source carrying both an explicit
   family identifier and an explicit outcome-evidence role.

The canonical current Event contract requires inputs 1 and 2 together, as
nonempty deduplicated arrays whose declared family set exactly matches the
families derived from the outcome-source subset. Inputs 1 or 2 by themselves
remain readable only for legacy coverage reports. When either event-level input
is present, it takes precedence and the reporter never unions generic source
roles into it.

Recognized family identifier fields are `source_family_id`, `source_family`,
`family_id`, and `family`. Recognized outcome-role declarations include
`supports_outcome`, `outcome_evidence`, and an `outcome` value in an explicit
role or claim-type field. Families are deduplicated within each event.

The report publishes two different ratios. Explicit-mapping coverage uses all
rated events as its denominator. Multiple-family coverage uses only explicitly
mapped events as its denominator. Unmapped events are counted separately and
are excluded from the family-count histogram; they are unknown, not observed
zero-family events.

The current release implements the first two contracts conservatively: each
mechanically promoted event carries an exact `outcome_source_ids` subset and a
matching stable `outcome_source_family_ids` array. Generic source-role fallback
is considered only when neither event-level field is present and is never
unioned into an explicit mapping. Exactly four sources advertise the direct
`outcome` capability: HCED data, IWD data, IWBD data, and the UCDP
conflict-level termination file. They map 4,366 of 4,406 rated events:
4,152 HCED, 64 IWD, 143 IWBD, and 7 UCDP. Every mapped event has exactly one
family, so multiple-independent-family coverage is 0 of 4,366 mapped events.

The other 40 rated events are the curated seed. They remain explicitly
unmapped, not observed zero-family events, because their generic URLs lack
claim-level outcome locators and citation-lineage review. The HCED-to-Seshat
crosswalk, Cliopatria registry records, UCDP termination dyad rows, HCED
consulted-source text, and curated/manual references have explicit non-outcome
roles. They never add an outcome family, even when they share a publisher,
family, or event link with a direct source.

## Registry and network coverage

Registry-to-rating coverage is the intersection of registry IDs with distinct
participant IDs in rated events, divided by all registry IDs. Registry status
labels are not the rating set: both curated and provisional identities can
have rating evidence. This ratio is observed model coverage only.

When results are supplied, component sizes are recomputed from explicit
`network_component` values on result entities. A component of size one defines
an isolated entity. Missing component values stay visible, and component IDs
are treated as arbitrary labels rather than ordered historical facts.

## Rejections and unresolved-queue aging

Rejection reasons come from the release's pipeline-specific counter maps.
HCED rows, IWD parent wars, IWBD battles, and UCDP termination rows use
different units, so the report does not publish one global rejection total.
Declared zero-valued counters are retained.

Queue aging requires both:

- an explicit row-level unresolved marker; and
- a schema-qualified queue-entry timestamp: `queued_at` or `staged_at`.

The general `needs_review` flag is insufficient because promoted records keep
it. Generic assertion `created_at` values, source retrieval timestamps,
snapshot identifiers, file modification times, and the wall clock are never
used. Ages are anchored to `--as-of` or the release metadata's deterministic
`as_of` date. If either disposition or queue time is missing, aging is
`not_available`, not zero.

## Historical completeness

True historical completeness needs a bounded historical-event universe or a
defensible probability sampling frame. The supplied registry, queues, and
ledger provide neither. The report therefore emits a structured
`historical_completeness` result with `status: not_estimated`, a null estimate,
an unknown denominator, and a reason.

No registry-to-rating ratio, promotion rate, source count, field-completeness
ratio, or network statistic is relabelled as a global historical-completeness
or accuracy score.

## Command-line use

Print both Markdown and deterministic JSON to standard output:

```powershell
python scripts/report_coverage.py
```

Print one machine-readable format:

```powershell
python scripts/report_coverage.py --format json
python scripts/report_coverage.py --format markdown
```

Use machine-local review inputs explicitly when they live in another
worktree:

```powershell
python scripts/report_coverage.py --review "C:\path\to\data\review" --format json
```

Write paired artifacts only to an ignored `build/` or temporary directory:

```powershell
python scripts/report_coverage.py --output-dir build/coverage
```

That command writes `coverage.json` and `coverage.md` as exact UTF-8 bytes with
LF line endings on every operating system. Output is deterministic: keys,
category labels, component labels, IDs, and file scans are sorted; no generation
timestamp, filesystem modification time, or absolute input path is embedded.

`--as-of` accepts exactly one full `YYYY-MM-DD` calendar-date string. Datetimes,
prefixes, suffixes, surrounding whitespace, empty values, and invalid dates are
input errors. Explicit `--review`, `--registry`, and `--results` paths must
exist; only omitted optional inputs degrade to unavailable metrics.

The library entry points are `build_coverage_report`,
`render_coverage_json`, `render_coverage_markdown`, and
`write_coverage_report` in `military_elo.coverage`.
