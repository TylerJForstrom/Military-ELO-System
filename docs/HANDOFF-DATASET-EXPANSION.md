# Contract: dataset expansion for coverage discovery (Wikidata battles + Brecke)

> Completion note (2026-07-18): the legacy 18-event queue remains semantically
> unchanged, but its missing original one-page blob was replaced by three
> surviving content-locked HTTPS pages from the same acquisition day. The
> version-2 legacy transformer explicitly allowlists the audited QIDs and fails
> closed on an incomplete set. The separate 18,954-event battle queue was
> refreshed from the same declared era-bucket queries; its count and
> non-rating contract are unchanged.

Goal: stage two new open sources so the funnel and a new gap report can show
where the corpus is thinnest and re-rank promotion priority — especially
pre-1500 and non-Western theatres. This is discovery/enrichment work: neither
source contributes outcomes, so nothing here rates events directly.

## Verified findings that shape the design (do not re-litigate)

- **Wikidata (CC0, ingest approved).** The battle tree (P31/P279* under
  Q178561) holds ~19,910 items (15,659 dated) plus ~3,490 siege-only items
  under Q188055 (3,298 dated); ~3,618 dated pre-1500, 1,598 of those with two
  or more distinct P710 participants. **Wikidata does not encode battle
  outcomes at scale: ~60 events in the whole graph carry a winner** (P1346 on
  the battle tree: 2; winner-role qualifier pq:P3831=Q18560095: 55). Treat as
  discovery + enrichment (coordinates, QID join spine to Cliopatria polity
  IDs, part-of hierarchy), never as an outcome source.
  docs/DATA_SOURCES.md's Wikidata section overstates P1346 and needs that
  correction.
- **Brecke Conflict Catalog (courtesy-posted, no license).** 3,708 war-level
  conflicts 1400-2000 (18 columns) plus a 1,147-row pre-1400 European
  extension; no winner column of any kind. Live URLs (verified 2026-07-17):
  https://brecke.inta.gatech.edu/wp-content/uploads/sites/19/2018/09/Conflict-Catalog-18-vars.xlsx
  (308,092 bytes; sheet name is literally 'Conflict Catalog 18 vars.xls';
  header row 1, data rows 2-3709; -9 means missing) and
  .../Notes-about-Conflict-Catalog.pdf. **Never commit the file content**;
  snapshot into gitignored data/raw/brecke-conflict-catalog/ per machine. Use
  only as a war-name registry and coverage cross-check.
- **Dincecco-Onorato: rejected for ingestion.** The public Springer ESM
  replication files contain a city-century regression panel — zero battle
  rows; the 1,091-event list exists only in copyrighted print or by author
  request (dincecco@umich.edu, m.onorato@imtlucca.it). Documented here so
  nobody chases it again.

## Already implemented (committed with this contract)

- `src/military_elo/ingest/wikidata.py`: `BATTLE_QUERY_TEMPLATE` (era-bucketed
  hydration query, tested at ~554 rows/bucket in <70 s: one row per event via
  GROUP_CONCAT, P279* closure, P625 coordinates, P17 countries, winner-role
  qualifiers, deterministic buckets instead of the old unordered
  LIMIT/OFFSET), `BATTLE_ERA_BUCKETS` (12 ranges sized from the measured
  century histogram), the siege series with `MINUS` against the battle tree,
  `fetch_wikidata_battles`, and `parse_wikidata_battle_rows` (candidate shape
  with latitude/longitude, classes, countries, QID~label pairs;
  `do_not_rate_automatically: true` on every row).
- `scripts/ingest_wikidata_battles.py`: acquisition driver. Writes snapshots
  under build/acquisition/wikidata-battles/ (~24 requests, 2 s pauses,
  ~20-25 MB total).

## Remaining steps

1. Run `python scripts/ingest_wikidata_battles.py` to completion. Validation:
   bucket row counts should sum near the measured totals (battle-tree dated
   ~15,659, siege-only dated ~3,298, plus daily drift); zero duplicate
   candidate_ids; spot-check ~20 pre-1500 candidates against their Wikidata
   pages.
2. **Additive lock mint — do not touch the existing `wikidata` dataset or its
   18-candidate queue.** `validate_wave6_queue_contracts` SHA-pins exact rows
   of data/review/wikidata-candidates.jsonl; the broadened pull must be a NEW
   dataset id `wikidata-battles` with its own raw files, transformation
   (`wikidata-battles-review`, page-NNNN roles), and output queue
   `data/review/wikidata-battle-candidates.jsonl`. Copy the acquisition
   snapshots into data/raw/wikidata-battles/, author the corpus.lock.json
   entries (files with sha256/size, transformation inputs, output hash after
   first staging), mirroring the existing wikidata records.
3. Add `stage_wikidata_battles` to src/military_elo/ingest/stage_open_data.py
   (reuse `parse_wikidata_battle_rows`), register it in
   scripts/stage_open_data.py STAGERS + TRANSFORMATION_IDS_BY_DATASET, stage,
   and verify the locked round trip reproduces the queue byte-for-byte.
4. Register Brecke in the lock only if a non-open license classification is
   added cleanly; otherwise leave it un-locked and document the URL + sha256
   in the gap report. Parse with openpyxl (read_only, data_only); strip the
   trailing date suffix regex `,\s*\d{4}(-\d{2,4})?$` from Name; emit a
   war-registry sidecar data/reference/brecke-wars.jsonl (NOT a candidate
   queue).
5. New script `scripts/report_dataset_gaps.py` producing
   build/dataset-gaps.json + a committed docs/DATASET_GAPS.md: (a) dedup the
   new Wikidata candidates against data/review/hced-candidates.jsonl on
   normalized name + year ±1 + coordinate proximity <25 km, writing
   `hced_match_candidates` per row; (b) bucket the genuinely-new candidates
   by century and region (P17 countries); (c) join Brecke wars against HCED
   war_names and enumerate wars with zero matching battles by region; (d) end
   with a revised promotion-priority ranking comparing these gaps against the
   current funnel (build/hced-unresolved-label-funnel.json). Expectation from
   the scouting: ~1,500-2,000 genuinely new pre-1500 engagement candidates,
   heaviest in Japanese, Chinese, Islamic-world, and Indian theatres.
6. Sync pins: tests/test_corpus_lock.py (raw file and queue counts grow),
   plus any suite that inventories data/review/*. Update
   docs/DATA_SOURCES.md (new dataset sections; Wikidata winner-scarcity
   correction). Keep every new candidate out of the rating ledger — this
   contract adds staged discovery data and analysis only.

Invariants: accuracy over counts; unknown is not a draw; automated
extractions are never approved rating data; commit as Tyler Forstrom with
conventional messages and no attribution trailers; never stage
.local-handoff/; never commit data/raw contents.
