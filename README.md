# Military History Elo

An auditable, uncertainty-aware system for exploring the military success of historical countries, empires and other autonomous actors.

The project is a reproducible research foundation, not a claim to contain “every battle ever.” The current expanded provisional release contains 2,409 catalogued, time-bounded polity identities, of which 1,063 actually participate in rated evidence across 5,487 events. It currently includes:

- separate tactical, operational and strategic ratings;
- participant-specific outcome vectors, so limited withdrawals and terminal defeats are not equivalent;
- event scale, national stakes, war type, domain, force context and coalition contribution;
- explicit predecessor/successor links with **no inherited rating**;
- an explicit Rome-to-Byzantium reset convention;
- uncertainty growth, confidence shrinkage and Monte Carlo sensitivity bands;
- disconnected-opponent-network warnings;
- immutable, licensed raw-source snapshots and a human-review queue;
- a hard-horizon interactive timeline, same-year Top X standings, audited battle
  map, leaderboard, risers/fallers and sourced event inspector.

## Open the dashboard

Build the data:

```powershell
python scripts/build_dashboard.py --data data/release --registry data/catalog/registry.json --simulations 200
```

Start the local site:

```powershell
python scripts/serve_dashboard.py
```

Then open `http://127.0.0.1:8080`.

## Deploy on Netlify

The repository includes `netlify.toml`. Import the GitHub repository into
Netlify and every push to the production branch publishes the `web/`
directory as-is. The committed `web/data/results.json` is the reviewed
1,000-simulation artifact, so the live site always matches the audited build;
deploys do not rerun the model. No database, server process, or runtime API
is required.

To update the site, rebuild the artifact locally and commit it:

```powershell
python scripts/build_dashboard.py --data data/release --registry data/catalog/registry.json --simulations 1000
```

The test suite cross-checks the committed artifact against the release and
registry so a stale or partial rebuild fails before it ships.

The dashboard deliberately separates the polity registry from the rating ledger. The 2,409-entry registry includes unrated and explicitly superseded source candidates; absence from the ledger is not a defeat. The release entity file has 1,070 records, of which 1,063 distinct entity IDs actually participate in rated events. The 5,487-event ledger combines 40 manually curated seed events, 1,887 crosswalk-resolved, 2,500 label-resolved, and 833 candidate-keyed HCED tactical encounters: 76 from Wave 6, 192 from Wave 7, and 565 from Wave 8. It also contains 66 coalition-aggregated IWD strategic parent wars, 153 IWBD tactical battles, and 8 UCDP conflict-termination strategic episodes. Source-derived entries remain visibly provisional and must not be published as a comprehensive historical conclusion.

The 5,220 already-rated HCED events also carry an audited, rating-neutral
location tranche where the source assertion survives fail-closed quarantine:
4,819 exact GeoJSON Points, 5,125 source-transcribed geographic-jurisdiction
labels in `modern_location_country`, and 5,174 closed `location_provenance`
objects. These are modern, unreviewed HCED source assertions with unknown
coordinate precision, not verified historical locations or sovereign-country
truth. Candidate-ID manifests withhold 401 Point fields and 94 jurisdiction
fields; 46 events overlap and 449 unique events have at least one quarantined
field. Quarantined values are omitted, never corrected. None may be normalized
into sovereign-country truth. This metadata-only tranche adds no rated event
and leaves every participant, outcome, rating, leaderboard value, and
sensitivity result unchanged. Outcome validation and promotion are separate,
score-changing workflows.

The 1,546-source registry spans 1,277 provenance families and also makes the
outcome-provenance contract explicit. Of the 5,487 rated events, 5,447 map
through explicit event outcome metadata to at least one direct outcome family:
5,220 HCED-derived events, 66 IWD parent wars, 153 IWBD battles, and 8 UCDP
conflict-termination episodes. Of those mapped events, 5,036 cite one direct
outcome family and 408 cite more than one. The 40 curated seed events remain
explicitly unknown until claim-level outcome locators and human review identify
which linked sources support the scored assertions. A `source_family_id` is a
provenance and deduplication label, while `evidence_roles` declares source
capabilities; neither is proof of independence by itself. URLs, publishers,
identity crosswalks, polity registries, UCDP dyad checks, and generic consulted
references do not become outcome evidence merely because an event links to
them.

## Data staged and referenced

The live ingestion pipeline has immutable snapshots and review candidates from:

- Cliopatria v0.2.0: 1,637 time-bounded identity candidates spanning 3400 BCE–2024, consolidated with curated and explicitly superseded identities into the 2,409-entry registry;
- Historical Conflict Event Dataset (HCED): 8,881 encounter candidates;
- Interstate War Data (IWD) v1.21: 265 component-war candidates derived once per war rather than once per annual row;
- Interstate War Battle Dataset (IWBD): 1,708 battle candidates;
- UCDP/PRIO conflict-year v26.1: 2,816 candidates;
- UCDP dyadic v26.1: 3,518 candidates;
- UCDP actor v26.1: 1,987 identity candidates;
- UCDP termination data: 2,752 conflict and 3,432 dyad candidates;
- a legacy bounded Wikidata discovery page with 18 candidates, plus an additive
  battle-tree and siege-only discovery queue with 18,954 candidates; and
- a 3,708-record Brecke war-name reference sidecar, derived from a
  machine-local, ignored workbook with no clear redistributable license.

The review queues now contain 45,968 staged source records. Of 42,344
event-like candidates, 36,856 remain outside the rating ledger. The additive
Wikidata queue contributes discovery metadata only: automated extraction is
never approved rating data, and Wikidata's roughly 60 winner assertions across
the whole graph are far too sparse to supply outcomes. These records remain in
`data/review/` and are not silently treated as accurate Elo matches.

Promotion into the provisional ledger is conservative and reproducible. HCED records require nonduplicate IDs, aligned winner/loser labels, both Seshat-coded sides, and unique time-valid polity resolution; rows lacking Seshat coding are retried in a second, declared label-resolution pass in which a side promotes only through an explicit time-bounded label policy or an exact, uniquely matching, time-valid alias, and the resulting events carry visibly lower identity confidence. For post-1500 rows only, that pass may split a side on an explicit comma, semicolon, or ampersand; every member must independently resolve through the ordinary label resolver to a distinct full-interval-valid identity. Plain `and` is never a delimiter. Superseded member IDs are canonicalized through the shared audited supersession inventory before the coalition is accepted, and the frozen pre-1500 cohort is never reopened by this rule. IWD component rows never enter individually because they can repeat one umbrella war across many dyads; each parent conflict is rated at most once, as a coalition event aggregated from its component dyads, and only when the reconstructed sides are consistent, the component outcomes are unanimous, no curated seed war overlaps, and every belligerent resolves to a unique time-bounded identity. Of 93 IWD parent wars, 66 currently pass those checks; the rest stay staged. IWBD battles enter only as tactical engagements, and only when they duplicate no seed event, non-curated-excluded HCED candidate, or earlier accepted IWBD row by exact normalized name and year; a same-year ordinal/base-name match additionally requires one recognized suffix path to extend the other with agreeing oriented outcomes. They must not be campaign umbrellas over sibling battles, must carry a victor matching a named side, and must resolve both sides to unique time-bounded identities; their war-level victor codes are ignored. UCDP termination records promote only as conflict-level terminal victory episodes (codes 3/4) between state parties with unique time-bounded identities, after cross-source deduplication and dyad- and linked-episode consistency checks; peace agreements, ceasefires, and low activity are never scored as outcomes, and secondary supporters receive no outcome. Battle winners, conflict intensity, and deaths still do not by themselves establish participant-specific strategic success, and every promoted event remains visibly provisional pending claim-level review. The post-Wave 7 crisp-boundary identity tranche adds Mahdist State (Sudan, 1881–1899), the post-Pavon Argentine Republic, the Principality/Kingdom of Bulgaria split, the Republic of Texas, and pre- and post-UAR Syrian republic windows. Boundary years overlap where year-only evidence is ambiguous; Texas labels stop at 1845, Syria deliberately resolves to nothing in 1958–1961, and no successor inherits a predecessor rating. Mexico resolves to the reviewed 1824–1863 republic and the 1868–2024 series in the current Cliopatria snapshot, while 1864–1867 remains a global deny gap; newly resolvable Argentina rows still fail when their source coalition or outcome is incomplete. The current post-Wave-8 planning funnel excludes every candidate ID already published in the ledger and reports 2,150 touched deferred rows, 2,174 unresolved normalized labels, and 966 sole-blocker rows; it and the co-war report rank future work only and never change the ledger.

## Refresh the open source corpus

```powershell
python scripts/download_open_data.py core
python scripts/verify_corpus_lock.py --inputs-only
python scripts/stage_open_data.py corpus
python scripts/verify_corpus_lock.py
python scripts/build_release.py
python scripts/build_dashboard.py --data data/release --registry data/catalog/registry.json --simulations 1000
```

Both the legacy bounded Wikidata blob and the additive era-bucketed battle
snapshots must be obtained by their locked checksums before staging `corpus`;
see [corpus reproducibility](docs/CORPUS_REPRODUCIBILITY.md). Live Wikidata
discovery is acquisition-only and defaults to ignored `build/acquisition/`
paths:

```powershell
python scripts/ingest_wikidata.py --max-pages 10
python scripts/ingest_wikidata_battles.py
```

UCDP's API now requires a free access token in the `x-ucdp-access-token` header. Versioned CSV downloads work without it. If a token is obtained, set `UCDP_API_TOKEN` and run `scripts/ingest_ucdp.py`; its live acquisition also defaults to `build/acquisition/` and does not alter the locked review queues.

Correlates of War import is supported for a locally supplied CSV, but COW's redistribution/commercial terms require permission before it becomes a public-product dependency. `python scripts/import_cow.py PATH_TO_AUTHORIZED_CSV` defaults to `build/acquisition/cow/`, outside the locked review queues.

## Project map

```text
config/                 versioned model parameters
data/raw/               immutable source snapshots + SHA-256 manifest
data/review/            extracted, unapproved candidates
data/seed/              manually adjudicated foundation dataset
data/release/           reproducible provisional rating ledger
data/catalog/           full rated and unrated polity registry
docs/                   methodology, identity rules, sources and review policy
src/military_elo/       model, audit, sensitivity and ingestion code
tests/                  mathematical and historical stress tests
web/                    interactive dashboard
```

## Accuracy principles

1. Automated scraping discovers evidence; it does not decide historical identity or victory.
2. A battle, campaign and war are different evidence layers; correlated records in one war cluster receive diminishing evidence weight.
3. Every participant gets its own objectives, consequences, stakes and termination.
4. Unknown is not a draw, peace is not a loss, and civilian killing is not a competitive win.
5. Sparse, ancient and disconnected records get wider uncertainty and visible coverage warnings.
6. Every ranking can be traced to events, dimensions, parameters and cited sources.

Read [the methodology](docs/METHODOLOGY.md), [entity policy](docs/ENTITY_POLICY.md), [review workflow](docs/REVIEW_WORKFLOW.md), [data-source guide](docs/DATA_SOURCES.md), [Wave 6 promotion review](docs/WAVE6-PROMOTION-REVIEW.md), and [unresolved-label funnel guide](docs/HCED-UNRESOLVED-FUNNEL.md).

## Test

The core has no runtime dependencies outside Python's standard library:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```
