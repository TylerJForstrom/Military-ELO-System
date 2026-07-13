# Military History Elo

An auditable, uncertainty-aware system for exploring the military success of historical countries, empires and other autonomous actors.

The project is a reproducible research foundation, not a claim to contain “every battle ever.” The current expanded provisional release contains 1,582 catalogued, time-bounded polity identities, of which 109 have rateable evidence across 1,461 events. It currently includes:

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

The dashboard deliberately separates the polity registry from the rating ledger. The 1,582-entry registry includes unrated source candidates; absence from the ledger is not a defeat. The 1,461-event ledger combines 40 manually curated seed events, 1,377 strictly filtered HCED tactical encounters, and 44 coalition-aggregated IWD strategic parent wars. Source-derived entries remain visibly provisional and must not be published as a comprehensive historical conclusion.

## Data already staged

The live ingestion pipeline has immutable snapshots and review candidates from:

- Cliopatria v0.2.0: 1,637 time-bounded identity candidates spanning 3400 BCE–2024, consolidated with the curated identities into the 1,582-entry registry;
- Historical Conflict Event Dataset (HCED): 8,881 encounter candidates;
- Interstate War Data (IWD) v1.21: 265 component-war candidates derived once per war rather than once per annual row;
- Interstate War Battle Dataset (IWBD): 1,708 battle candidates;
- UCDP/PRIO conflict-year v26.1: 2,816 candidates;
- UCDP dyadic v26.1: 3,518 candidates;
- UCDP actor v26.1: 1,987 identity candidates;
- UCDP termination data: 2,752 conflict and 3,432 dyad candidates;
- a tested Wikidata discovery page with 18 candidates.

These records remain in `data/review/` and are not silently treated as accurate Elo matches.

Promotion into the provisional ledger is conservative and reproducible. HCED records require nonduplicate IDs, aligned winner/loser labels, both Seshat-coded sides, and unique time-valid polity resolution. IWD component rows never enter individually because they can repeat one umbrella war across many dyads; each parent conflict is rated at most once, as a coalition event aggregated from its component dyads, and only when the reconstructed sides are consistent, the component outcomes are unanimous, no curated seed war overlaps, and every belligerent resolves to a unique time-bounded identity. Of 93 IWD parent wars, 44 currently pass those checks (72 of 265 component records); the rest stay staged. IWBD and UCDP also remain staged evidence because battle winners, conflict intensity, and deaths do not by themselves establish participant-specific strategic success.

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
