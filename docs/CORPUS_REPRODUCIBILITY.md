# Corpus reproducibility

`data/corpus.lock.json` identifies the exact machine-local source blobs and
generated review queues used by this checkout without committing the source
files themselves. The lock is metadata only: it contains source URLs,
dataset/file versions, license-policy classes, retrieval timestamps and
methods, portable basenames, byte sizes, full SHA-256 digests, transformation
versions, and expected queue digests and record counts.

The lock never contains raw records, licensed content, credentials, request
headers, absolute paths, or operator identities. A license class records the
project's reviewed handling policy; it is not a new grant of rights. Recheck
the publisher's current terms before refreshing a source or redistributing a
derivative.

## What is locked

Each dataset entry identifies one or more immutable files. Each transformation
names its input roles and one replaceable `*-candidates.jsonl` output. The
current transformation set covers the core open-data stagers, the exact
bounded Wikidata discovery page, and the separate era-bucketed Wikidata
battle/siege discovery pull used by the machine-local build. The locked
queue names and record counts are tested against
`data/release/metadata.json` so an omitted or rewritten queue cannot silently
change the staged corpus arithmetic.

The legacy `wikidata` entry is a fixed 18-event audit set drawn from three
content-locked HTTPS source pages. Its version-2 transformer allowlists those
18 QIDs, sorts the resulting candidates, and fails closed if any audited item
is absent. This preserves the Wave 6 row contracts while making the queue
reproducible from source snapshots that are still present in the authorized
corpus cache. The additive `wikidata-battles` entry locks snapshots behind a
separate 18,954-candidate queue: 15,658 dated battle-tree items and 3,296
siege-only items, including 4,908 pre-1500 candidates. Both are restaged
offline through their own transformers; numeric `page-*` input roles define
deterministic snapshot order. Live Wikidata fetchers remain acquisition
tooling and do not update either lock implicitly.

## Obtain blobs on another machine

Clone the repository, then choose one of these acquisition paths for every
locked file:

1. For the datasets listed by `scripts/download_open_data.py --list`, run:

   ```powershell
   python scripts/download_open_data.py core
   ```

   The downloader accepts only a catalogued `open_core` entry whose locked
   retrieval method is `https`. It verifies the full digest and size before
   installing the lock's exact basename. If an upstream URL now returns
   different bytes, the command fails without installing or manifesting them.

2. Obtain the exact content-addressed blob from an authorized project archive
   or another authorized machine. Place it at
   `data/raw/<dataset-id>/<locked-filename>`. This is the required path for an
   `authorized_copy` entry and is also suitable when network access is
   unavailable. Do not commit the copied blob.

3. For both Wikidata contracts, use authorized copies of the exact locked
   blobs. A live query is only a proposed lock refresh because the service can
   change. If a fresh acquisition is needed, isolate its outputs under
   `build/` and use non-locked queue basenames, for example:

   ```powershell
   python scripts/ingest_wikidata.py `
     --raw-root build/acquisition/raw `
     --review build/acquisition/wikidata-live.jsonl `
     --page-size 50 --max-pages 1

   python scripts/ingest_wikidata_battles.py
   ```

   The provenance writer refuses an unlocked write to either locked Wikidata
   queue basename. Adopting new pages requires a reviewed lock and
   transformation update; live fetches never do that implicitly.

Verify the acquired bytes without downloading anything:

```powershell
python scripts/verify_corpus_lock.py --inputs-only
```

Missing files, extra path indirection, size drift, or SHA-256 drift fails
closed. The verifier can also point at an authorized cache:

```powershell
python scripts/verify_corpus_lock.py `
  --raw-root D:\authorized-corpus\raw `
  --inputs-only
```

The cache path is a runtime argument and is never written into the lock or
generated queues.

## Deterministic restaging

After all locked blobs verify, regenerate the complete locked queue set:

```powershell
python scripts/stage_open_data.py corpus
python scripts/verify_corpus_lock.py
```

`corpus` includes both Wikidata transformations; `core` retains the historical
core-stager selection and excludes both machine-local Wikidata pulls. Staging
resolves exact locked filenames and never chooses a file by modification time.
Candidate provenance uses logical
`data/raw/<dataset>/<filename>` references, so absolute cache roots cannot
change output bytes.

The staging CLI preflights every selected dependency, renders each queue into a
temporary directory, checks the locked record count, size, and digest, and
only then replaces the selected generated queues. To prove restaging without
touching the working review tree:

```powershell
python scripts/stage_open_data.py corpus --review-root build/restaged-review
python scripts/verify_corpus_lock.py --review-root build/restaged-review
```

No upstream service is contacted by staging or verification.

## Generated queues and human decisions

The two forms of review state are deliberately separate:

- `data/review/*-candidates.jsonl` files are replaceable generated artifacts.
  Do not edit them to record adjudication.
- `data/review/decisions/*.jsonl` files are append-only local human decisions,
  keyed by stable decision and candidate IDs. Restaging never traverses,
  deletes, or rewrites this directory.

Both areas remain ignored because review rows can contain source-derived or
private material. The append helper rejects decision writes outside the
`decisions/` namespace and duplicate decision IDs. `report_ingestion.py`
counts only candidate basenames, excludes nested decisions, verifies the full
locked queue set by default, and rejects unexpected top-level JSONL files.

## Acquisition tools outside the locked corpus

The legacy UCDP API ingester and permission-gated COW importer are not corpus
restagers. Keep their raw and review outputs under `build/` while evaluating a
new source, for example:

```powershell
python scripts/ingest_ucdp.py `
  --raw-root build/acquisition/ucdp-raw `
  --review build/acquisition/ucdp-api.jsonl

python scripts/import_cow.py authorized-input.csv `
  --review build/acquisition/cow-candidates.jsonl
```

Their output must not be copied into the locked top-level review queue set
without a separate licensing decision, transformation contract, fixture
tests, and lock update. These acquisition paths do not alter promotion rules
or release artifacts.

## Updating the lock

A corpus refresh is a reviewed change, not an in-place download:

1. Acquire proposed bytes under `build/` or another temporary location.
2. Confirm the exact dataset version, URL, license-policy class, retrieval
   method, timestamp, filename, byte size, and SHA-256.
3. Add or update named transformation inputs. Bump the transformation version
   whenever parsing or serialization behavior changes.
4. Restage into `build/`, inspect the queue diff, and record the new output
   count, size, and SHA-256 in the lock.
5. Run the focused tests, full suite, offline verifier, `git diff --check`, and
   `git status --short`.

Commit only the lock, code, tests, documentation, and permitted derived
reference artifacts. Never stage the source blobs, generated review queues,
local decisions, or temporary acquisition outputs. In particular, the Brecke
workbook remains ignored because it has no clear redistributable license; only
its parsed war-name sidecar is versioned.
