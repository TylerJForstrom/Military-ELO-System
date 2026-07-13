# Licensing and redistribution policy

Last verified: 2026-07-13.

This is the project's operational data-use policy, not legal advice. Source
terms can change. Recheck the publisher's current license before every new
release or automated refresh, and obtain legal review before commercial
distribution.

The public corpus is built only from data that can be redistributed and adapted
under CC0 or attribution-only terms. A source being free to download does not
mean that it may be republished, combined into this database, used commercially,
or used to create a competing product.

## Release classes

| Class | Meaning | Current sources |
|---|---|---|
| Open core | Raw facts may be staged and derived records may be released while satisfying the stated attribution terms | HCED, HCED-Seshat crosswalk, IWD, IWBD, UCDP, Cliopatria, Wikidata structured data, Pleiades, GeoNames |
| Separate/secondary | Do not merge into the public corpus without a compatibility review; link or query separately if needed | DBpedia |
| Permission-gated | Do not download into a distributable corpus, commit raw records, or base a public product on the data without written authorization | COW, MIE, ACLED, PA-X, Brecke Conflict Catalog, broader Seshat data |

The allowlist applies to the exact release and URL recorded in
`data/raw/manifest.jsonl`. It does not automatically apply to another product
from the same organization.

## Open-core obligations

### CC0 1.0

Current sources:

- Historical Conflict Event Dataset and its Seshat crosswalk:
  <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6ZFC0V>
- Interstate War Battle Dataset:
  <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KLQFAP>
- Interstate War Data v1.21:
  <https://doi.org/10.7910/DVN/WGS1YX>
- Wikidata structured data:
  <https://www.wikidata.org/wiki/Wikidata:Licensing>

CC0 permits copying, modification, redistribution, and commercial use without
a legal attribution condition. This project nevertheless requires scholarly
attribution and provenance for auditability:

- Retain source title, publisher/author, DOI or canonical URL, version/file ID,
  access date, source row/record ID, and snapshot checksum.
- Cite the associated academic publication where the publisher requests it.
- Do not imply that the source authors endorse this rating model or its output.
- Do not reproduce copyrighted article prose, images, maps, or long source
  narratives merely because the dataset facts are CC0.

Recommended citations:

- Miller, Charles, and K. S. Bakar. "Conflict Events Worldwide Since 1468BC:
  Introducing the Historical Conflict Event Dataset." *Journal of Conflict
  Resolution* (2023). <https://doi.org/10.1177/00220027221119085>
- Min, Eric. "Interstate War Battle Dataset (1823-2003)." *Journal of Peace
  Research* 58(2), 294-303. <https://doi.org/10.1177/0022343320913305>
- For Wikidata, link the relevant QID and the Wikidata license/data-access page;
  preserve statement references and qualifiers where available.

Only Wikidata's structured main/property/lexeme/entity-schema data is CC0.
Text in other Wikidata namespaces is CC BY-SA, and Wikimedia Commons media has
file-specific licenses. The open-core approval does not cover that text or media.

### CC BY 4.0

Current sources:

- All current UCDP datasets listed at <https://ucdp.uu.se/downloads/>.
- Cliopatria v0.2.0 at <https://zenodo.org/records/20274630>.

CC BY 4.0 permits copying, adaptation, redistribution, and commercial use when
the release provides appropriate credit, a link to the license, and an
indication of modifications. For every derived record or release:

- Name the source and creators/publisher.
- Link the exact dataset release and <https://creativecommons.org/licenses/by/4.0/>.
- State the version and access date.
- State that the project normalized names, linked entities, classified scope,
  or otherwise modified the source data.
- Retain any supplied copyright/license notices and do not imply endorsement.
- Include the citations requested on the source's download page.

UCDP explicitly permits use and redistribution of its current datasets under
CC BY 4.0 provided the relevant publications listed with each dataset are
cited. A suitable dataset-level attribution is:

> Source data: Uppsala Conflict Data Program (UCDP), dataset name and version,
> accessed YYYY-MM-DD, <https://ucdp.uu.se/downloads/>, licensed CC BY 4.0.
> Historical Military Elo normalized actor identities and independently coded
> rating outcomes; those changes are not UCDP's analysis.

Use the current publication citation given beside the particular UCDP dataset.
For v26.1 core data, the download center requests citation of Shawn Davies,
Therese Pettersson, and Magnus Oberg, "Organized violence 1989-2025, and
violent political protests," *Journal of Peace Research* (2026),
<https://doi.org/10.1093/jopres/xjag046>, plus the dataset-specific foundational
paper where listed.

A suitable Cliopatria attribution is:

> Source polity geometry and identifiers: Bennett et al., Cliopatria v0.2.0,
> <https://doi.org/10.5281/zenodo.20274630>, CC BY 4.0. Historical Military Elo
> modified entity boundaries/continuity decisions for rating purposes.

Also cite the peer-reviewed data description:
<https://www.nature.com/articles/s41597-025-04516-9>.

### CC BY 3.0

Pleiades publishes its dataset under CC BY 3.0:
<https://pleiades.stoa.org/downloads>.

When Pleiades data is used, credit Pleiades and its contributors, link the
specific numbered release or canonical place URI, link
<https://creativecommons.org/licenses/by/3.0/>, and indicate modifications.
Do not assume that third-party media or linked resources on a place page share
the dataset license.

### GeoNames CC-BY terms

GeoNames states that its data is under a Creative Commons attribution license,
requires credit to GeoNames, and permits commercial use:
<https://www.geonames.org/export/>.

The source page does not identify a license version in its short terms. Use the
publisher's wording rather than inventing a version. Include "GeoNames" with a
link to <https://www.geonames.org/> in data documentation and any map or export
substantially using its records. Record the daily dump retrieval date because
the database changes continuously.

## Permission-gated and excluded sources

### Correlates of War (COW)

Terms: <https://correlatesofwar.org/data-sets/>.

COW states that:

- data may not be used for commercial activity;
- users must cite each dataset as directed;
- users may not distribute the dataset to a third party without written
  permission from the COW director and data host; and
- users must ask permission for dissemination, posting, or other uses not
  covered by those restrictions.

Policy: do not commit COW raw files, transform COW records into the public event
corpus, or publish a rating product materially based on COW until written
permission covers the intended redistribution and commercial/noncommercial
deployment. A local importer may be used only by a user who obtained the data
and accepts COW's terms; its output remains restricted.

### International Conflict Data Project / MIE

User agreement: <https://internationalconflict.ua.edu/data-download/>.

The agreement prohibits commercial use and sharing/distribution in any form
other than for replication, and requires citation of the release paper.

Policy: MIE, MIC, MIP, MICend, TDD, MICnames, PDMID, and WarDec records must
not be included in the public raw or derived corpus without written permission.
They may be used as a private research cross-check only when the user has
accepted the agreement.

### ACLED

- Content usage terms: <https://acleddata.com/contentusage>
- Attribution policy: <https://acleddata.com/attributionpolicy>
- API access: <https://acleddata.com/api-documentation/getting-started>
- EULA: <https://acleddata.com/eula>

ACLED requires an account and authenticated API access. Its current content
terms prohibit creating or supporting a dataset, product, or platform that
competes with or creates a functional substitute for ACLED content, and impose
additional restrictions on services, redistribution, and AI/ML use. Attribution
alone does not grant permission.

Policy: ACLED is excluded from downloads, model inputs, training data, public
event records, and rating calculations. It may be added only after ACLED gives
written authorization specifically covering this project's ingestion,
transformation, display, redistribution, and intended commercial status.

### PA-X

- Terms: <https://www.peaceagreements.org/cms/documents/8/Terms_of_Use_updated_added_local.pdf>
- Downloads: <https://www.peaceagreements.org/downloads/>

PA-X permits research, teaching, peace-mediation, and similar uses but prohibits
commercial use, charging a fee, and copying or reusing the entire database or a
substantial part to create an identical or substantially similar subset
database. Except for third-party material, its database content is CC
BY-NC-SA 4.0.

Policy: PA-X may be consulted manually for bounded settlement research with
proper citation. Do not bulk-ingest or redistribute it, and do not copy its
agreement texts or copyrighted translations into this project. Obtain written
permission before systematic integration or any commercial deployment.

### DBpedia

License: <https://www.dbpedia.org/imprint/>.

DBpedia releases from 3.4 onward are dual-licensed under CC BY-SA 3.0 and the
GNU Free Documentation License. Its share-alike and attribution requirements
are materially different from the open core.

Policy: do not copy DBpedia dumps or extracted triples into the main public
corpus until a documented license-compatibility review chooses a license path
for the combined database. If used as a separate resolver, retain active DBpedia
URIs and the attribution DBpedia requests. Prefer CC0 Wikidata structured data.

### Brecke Conflict Catalog

Project page: <https://brecke.inta.gatech.edu/research/conflict/>.

No explicit reusable data license was found on the project or download page.
Availability of an XLSX file is not permission to redistribute it.

Policy: do not commit, bulk-ingest, or redistribute the catalog. It may identify
possible gaps for manual follow-up using independently licensed sources. Obtain
written permission from the author before any systematic use.

### Broader Seshat data

General terms: <https://seshat-db.com/terms/current/>.

Public Seshat data is generally offered under CC BY-NC-SA terms and some API
access may require credentials. This is separate from the expressly CC BY 4.0
Cliopatria release.

Policy: only the identified Cliopatria v0.2.0 release is in the open core.
Broader Seshat warfare, technology, or social-complexity data remains
permission-gated for this project unless a specific file has independently
verified compatible terms.

## Attribution and provenance requirements

Every raw snapshot and approved record must retain:

- stable internal source ID;
- source title and publisher/creator;
- canonical landing-page URL and exact download/API URL;
- dataset version or Dataverse/Zenodo file ID;
- license identifier and license URL;
- retrieval timestamp;
- SHA-256 checksum;
- original source record ID and, when practical, row/member location;
- transformations performed by this project;
- citations requested by the publisher; and
- human reviewer and review status for any outcome or identity adjudication.

The existing `data/raw/manifest.jsonl` provides snapshot-level provenance. The
rated dataset's `sources.json` and exported UI/API records must provide
human-readable attribution and links. A checksum proves which bytes were used;
it does not replace an attribution or license notice.

## Redistribution checklist

Before publishing a dataset, application build, visualization, or API:

1. Confirm that every contributing source is on the open-core allowlist for the
   exact version used.
2. Confirm that no COW, MIE, ACLED, PA-X, DBpedia, Brecke, or broader Seshat
   record was copied into the release without the documented permission or
   compatibility review.
3. Include source/version/access-date attribution and links in the release notes
   and data documentation.
4. Link the CC BY license and clearly describe name normalization, entity
   resolution, deduplication, outcome adjudication, and rating transformations.
5. Include citations on or adjacent to visualizations when a source requests it.
6. Preserve source URLs and per-record provenance in machine-readable exports.
7. Do not copy long narrative descriptions, articles, agreement texts, images,
   or maps unless their separate copyright license permits it.
8. Do not present inferred outcomes or rating results as findings endorsed by
   the source publisher.
9. Recheck terms whenever a new source version is downloaded; do not assume
   that an earlier license still applies.
10. Stop release and request review when a license is absent, contradictory,
    noncommercial, share-alike, account-specific, or otherwise unclear.
