# Military History Elo

An auditable, uncertainty-aware system for exploring the military success of historical countries, empires and other autonomous actors.

The project is working as a research-grade foundation, not yet a claim to have completed “every battle ever.” It currently includes:

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
python scripts/build_dashboard.py --simulations 200
```

Start the local site:

```powershell
python scripts/serve_dashboard.py
```

Then open `http://127.0.0.1:8080`.

## Deploy on Netlify

The repository includes `netlify.toml`. Import the GitHub repository into
Netlify and the site will build with these settings automatically:

```text
Build command: python scripts/build_dashboard.py --simulations 1000
Publish directory: web
```

Every push to the selected production branch will rebuild the rating results
and deploy the standalone static dashboard. No database, server process, or
runtime API is required.

The seed history is deliberately labeled a curated demonstration. Do not publish its current ranking as a comprehensive historical conclusion. The downloaded and staged source corpus is much larger, but candidates only enter the rating after identity, outcome and provenance review.

## Data already staged

The live ingestion pipeline has immutable snapshots and review candidates from:

- Cliopatria v0.2.0: 1,633 global polity/relation identity candidates spanning 3400 BCE–2024;
- Historical Conflict Event Dataset (HCED): 8,881 encounter candidates;
- Interstate War Battle Dataset (IWBD): 1,708 battle candidates;
- UCDP/PRIO conflict-year v26.1: 2,816 candidates;
- UCDP dyadic v26.1: 3,518 candidates;
- UCDP actor v26.1: 1,987 identity candidates;
- UCDP termination data: 2,752 conflict and 3,432 dyad candidates;
- a tested Wikidata discovery page with 18 candidates.

These records remain in `data/review/` and are not silently treated as accurate Elo matches.

## Refresh the open source corpus

```powershell
python scripts/download_open_data.py core
python scripts/stage_open_data.py core
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
data/seed/              small adjudicated demonstration dataset
docs/                   methodology, identity rules, sources and review policy
src/military_elo/       model, audit, sensitivity and ingestion code
tests/                  mathematical and historical stress tests
web/                    interactive dashboard
```

## Accuracy principles

1. Automated scraping discovers evidence; it does not decide historical identity or victory.
2. A battle, campaign and war are different evidence layers and are not double-counted.
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
