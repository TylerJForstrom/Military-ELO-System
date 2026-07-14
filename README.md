# Military History Elo

An auditable, uncertainty-aware system for exploring the military success of historical countries, empires and other autonomous actors.

The project is a reproducible research foundation, not a claim to contain “every battle ever.” The current expanded provisional release contains 1,590 catalogued, time-bounded polity identities, of which 226 have rateable evidence across 4,234 events. It currently includes:

- separate tactical, operational and strategic ratings;
- participant-specific outcome vectors, so limited withdrawals and terminal defeats are not equivalent;
- event scale, national stakes, war type, domain, force context and coalition contribution;
- explicit predecessor/successor links with **no inherited rating**;
- an explicit Rome-to-Byzantium reset convention;
- uncertainty growth, confidence shrinkage and Monte Carlo sensitivity bands;
- disconnected-opponent-network warnings;
- immutable, licensed raw-source snapshots and a human-review queue;
- an interactive timeline, leaderboard, risers/fallers and sourced event inspector.

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

The dashboard deliberately separates the polity registry from the rating ledger. The 1,590-entry registry includes unrated source candidates; absence from the ledger is not a defeat. The 4,234-event ledger combines 40 manually curated seed events, 1,769 crosswalk-resolved and 2,243 label-resolved HCED tactical encounters, 54 coalition-aggregated IWD strategic parent wars, 121 IWBD tactical battles, and 7 UCDP conflict-termination strategic episodes. Source-derived entries remain visibly provisional and must not be published as a comprehensive historical conclusion.

## Data already staged

The live ingestion pipeline has immutable snapshots and review candidates from:

- Cliopatria v0.2.0: 1,637 time-bounded identity candidates spanning 3400 BCE–2024, consolidated with the curated identities into the 1,590-entry registry;
- Historical Conflict Event Dataset (HCED): 8,881 encounter candidates;
- Interstate War Data (IWD) v1.21: 265 component-war candidates derived once per war rather than once per annual row;
- Interstate War Battle Dataset (IWBD): 1,708 battle candidates;
- UCDP/PRIO conflict-year v26.1: 2,816 candidates;
- UCDP dyadic v26.1: 3,518 candidates;
- UCDP actor v26.1: 1,987 identity candidates;
- UCDP termination data: 2,752 conflict and 3,432 dyad candidates;
- a tested Wikidata discovery page, currently holding 18 candidates on this machine.

These records remain in `data/review/` and are not silently treated as accurate Elo matches.

Promotion into the provisional ledger is conservative and reproducible. HCED records require nonduplicate IDs, aligned winner/loser labels, both Seshat-coded sides, and unique time-valid polity resolution; rows lacking Seshat coding are retried in a second, declared label-resolution pass in which a side promotes only through an explicit time-bounded label policy or an exact, uniquely matching, time-valid alias, and the resulting events carry visibly lower identity confidence. IWD component rows never enter individually because they can repeat one umbrella war across many dyads; each parent conflict is rated at most once, as a coalition event aggregated from its component dyads, and only when the reconstructed sides are consistent, the component outcomes are unanimous, no curated seed war overlaps, and every belligerent resolves to a unique time-bounded identity. Of 93 IWD parent wars, 54 currently pass those checks (87 of 265 component records); the rest stay staged. IWBD battles enter only as tactical engagements, and only when they duplicate no seed event, non-curated-excluded HCED candidate, or earlier accepted IWBD row by exact normalized name and year; a same-year ordinal/base-name match additionally requires one recognized suffix path to extend the other with agreeing oriented outcomes. They must not be campaign umbrellas over sibling battles, must carry a victor matching a named side, and must resolve both sides to unique time-bounded identities; their war-level victor codes are ignored. UCDP termination records promote only as conflict-level terminal victory episodes (codes 3/4) between state parties with unique time-bounded identities, after cross-source deduplication and dyad- and linked-episode consistency checks; peace agreements, ceasefires, and low activity are never scored as outcomes, and secondary supporters receive no outcome. Battle winners, conflict intensity, and deaths still do not by themselves establish participant-specific strategic success, and every promoted event remains visibly provisional pending claim-level review. A curated tranche of time-bounded state identities (Habsburg Monarchy through Austria-Hungary, Kingdom of Prussia, the French republics and Second Empire, Qajar Iran, Joseon, and twenty-five others) and a declared set of non-state actor identities (civil-war factions, revolutionary movements, and insurgent armies with materially autonomous command) resolve previously blocked labels and codes era-correctly, with deliberate gaps where no single defensible identity exists; every identity decision is documented in the entity policy and remains second-reviewer-pending.

## Refresh the open source corpus

```powershell
python scripts/download_open_data.py core
python scripts/stage_open_data.py core
python scripts/build_release.py
python scripts/build_dashboard.py --data data/release --registry data/catalog/registry.json --simulations 200
```

Wikidata discovery is paged and resumable:

```powershell
python scripts/ingest_wikidata.py --max-pages 10
```

UCDP's API now requires a free access token in the `x-ucdp-access-token` header. Versioned CSV downloads work without it. If a token is obtained, set `UCDP_API_TOKEN` and run `scripts/ingest_ucdp.py`.

Correlates of War import is supported for a locally supplied CSV, but COW's redistribution/commercial terms require permission before it becomes a public-product dependency.

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

Read [the methodology](docs/METHODOLOGY.md), [entity policy](docs/ENTITY_POLICY.md), [review workflow](docs/REVIEW_WORKFLOW.md), and [data-source guide](docs/DATA_SOURCES.md).

## Test

The core has no runtime dependencies outside Python's standard library:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```
