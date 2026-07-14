# Evidence model contract

This workstream stores historical assertions and review decisions without
changing source promotion, event eligibility, rating calculations, or published
results. Evidence records use explicit stable IDs and deterministic JSON forms.
Existing entity and event documents remain valid because every evidence field
added to those records is optional.

## Claims and evidence

A claim is one assertion: a subject, predicate, value, precision description,
and provenance. Competing or contradictory assertions remain separate claims;
they are not overwritten or collapsed into a source-count vote.

Claim `status` describes only the assertion row's lifecycle:

- `active` means the assertion remains under consideration.
- `withdrawn` means its submitter withdrew the assertion.
- `superseded` means another assertion row replaces it.

Acceptance, rejection, dispute, and insufficient-evidence outcomes belong only
to adjudications. A claim may optionally identify a claim group. When any member
marks that group exclusive, the group cannot resolve with multiple accepted
members.

Source locators retain exact edition and page, row, or URL anchors, along with a
checksum, language, source ID, and source family. Creator and citation metadata
may retain historian, archivist, or other source authorship when it is not
available through the source registry. An evidence link states whether one
locator supports, contradicts, or contextualizes one claim.

`source_family` is an explicit provenance/deduplication label. It is never
inferred from a generic `source` field, and the number of families or locators
does not determine a claim's review outcome.

## Append-only adjudication

Each adjudication is an immutable decision with a stable ID, claim ID, reviewer,
rationale, and codebook version. Corrections append a new decision whose
`supersedes` field names earlier decisions; prior rows remain in history.
Unsuperseded leaves are the effective decisions. Parallel leaves are preserved
so reviewer disagreement remains visible.

High-impact acceptance requires accepted primary and secondary leaves from two
distinct, non-blank reviewer identifiers. A superseded acceptance cannot satisfy
that gate. These resolution rules are derived audit views, not mutations of the
claim rows.

An accepted claim is still evidence only. Acceptance does not make the claim,
event, participant, or entity rating-eligible. A separate future promotion
workflow must make any such integration explicit.

## Canonical events and dates

Canonical event identity may include aliases, parent and child links, geometry,
and bounded participation episodes. Episodes record side, role, entry and exit,
contribution, objectives, and supporting claim IDs without replacing legacy
participants.

Uncertain dates carry low, best, and high values. Signed years follow the BCE/CE
convention with no year zero. Month and day validation uses the proleptic
Gregorian calendar as a machine-readable storage convention; it does not claim
that a historical source used that calendar contemporaneously. Date intervals
and participation bounds are audited as evidence data only. The rating engine
does not interpret them in this workstream.

## Sampling and review packets

Gold-set samples use an explicit seed and may stratify by era, region, layer,
domain, and source family. Their population manifest and digest bind the seed to
the exact stable IDs and strata that were sampled.

Review packets expose selected event context, claims, exact evidence, and
unresolved disagreements while excluding Elo, rating, rank, leaderboard, and
other model effects. Prior adjudications are omitted by default for independent
review. If an operator explicitly includes them, append/supersession order is
preserved and the packet reports that it is no longer blinded to prior
decisions; it remains free of leaderboard effects.
