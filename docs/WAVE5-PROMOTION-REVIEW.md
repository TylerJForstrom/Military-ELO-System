# Wave 5 promotion review

## Scope and release result

Wave 5 is a conservative identity-bound promotion tranche, not a claim of
historical completeness. It expands Portugal and Tsardom-era HCED coverage and
adds exact reviewed IWD/IWBD contracts for transitional identities. Every
accepted event remains provisional pending claim-level historical review.

The frozen release/registry build measures:

| Metric | Wave 4 | Wave 5 | Change |
|---|---:|---:|---:|
| Rated events | 4,245 | 4,406 | +161 |
| Curated seed events | 40 | 40 | 0 |
| HCED events | 4,019 | 4,152 | +133 |
| HCED crosswalk / label | 1,769 / 2,250 | 1,824 / 2,328 | +55 / +78 |
| IWD parent wars | 56 | 64 | +8 |
| IWD components aggregated | 89 | 100 | +11 |
| IWBD battles | 123 | 143 | +20 |
| UCDP episodes | 7 | 7 | 0 |
| Registry identities | 1,591 | 1,598 | +7 |
| Release entity records | 228 | 236 | +8 |
| Entity IDs with rated evidence | 228 | 235 | +7 |
| Registered sources / families | 94 / 23 | 106 / 31 | +12 / +8 |
| Events with a direct outcome family | 4,205 | 4,366 | +161 |
| Staged source records | 27,014 | 27,014 | 0 |
| Event-like candidate denominator | 23,390 | 23,390 | 0 |
| Unresolved event-like candidates | 19,152 | 18,988 | -164 |
| Latest rated event year | 2021 | 2021 | 0 |

All 4,245 Wave 4 event IDs remain. The 161-event increase is 133 HCED
encounters plus 8 IWD parents and 20 IWBD battles. The event-like unresolved
counter uses pipeline candidate units, not release-event units, so its change
must not be forced to equal the event delta.

The release file contains 236 entity records but only 235 participant IDs with
rated evidence. The United Kingdom of Portugal, Brazil and the Algarves is a
curated boundary record with no promoted event and therefore has no rating.

## Portugal and Tsardom HCED tranche

The Wave 5 cohort contains 79 Portugal-linked events: 78 new events plus the
previously rated Estaires event, split 16 crosswalk-resolved and 63
label-resolved. It contains 58 Tsardom-linked events: 55 new events plus three
previously rated events, split 41 crosswalk-resolved and 17 label-resolved.
Together these cohorts account for the 133-event HCED increase.

Portugal uses separate, non-inheriting identities and conservative complete-year
source windows:

| Identity | Curated identity interval | Generic source-policy interval |
|---|---:|---:|
| Kingdom of Portugal | 1143-1814 | 1147-1814 |
| United Kingdom of Portugal, Brazil and the Algarves | 1815-1822 | 1816-1821 |
| Kingdom of Portugal (restored) | 1822-1910 | 1823-1909 |
| First Portuguese Republic | 1910-1926 | 1911-1925 |

Generic year-only rows in 1815, 1822, and 1910 fail closed because each year
contains a regime boundary. The independently dated Battle of Piraja on
8 November 1822 is the sole exact candidate contract through the 1822 gap; its
complete source fingerprint and exact entity IDs are pinned. The cross-boundary
Salvador 1822-23 campaign stays staged.

The Tsardom policy resolves 1547-1720 to the existing canonical Cliopatria ID
`clio_ru_moskva_rurik_dyn_1547_93deb0e2`. It does not create a parallel
`tsardom_russia` record. The Russian Empire begins a separate rating in 1721;
no Elo transfers across that boundary.

## Exact strategic contracts

Wave 5 adds exactly 28 strategic-tranche events through complete, fail-closed
contracts rather than generic aliases:

| Cohort | IWD | IWBD | Total |
|---|---:|---:|---:|
| Bourbon Restoration France / Spain, 1823 | 1 | 1 | 2 |
| Russian SFSR with first-republic Estonia or Poland | 2 | 0 | 2 |
| Turkish National Movement, 1919-1922 | 2 | 12 | 14 |
| Republic of China on Taiwan | 3 | 6 | 9 |
| Orleans / French Third Republic, 1870 | 0 | 1 | 1 |
| **Total** | **8** | **20** | **28** |

The IWD parent contracts are `1`, `39`, `41`, `43`, `44`, `57`, `60`, and
`91`. Each pins the complete parent/component inventory, source semantics,
party codes, and exact entity IDs.

The final IWBD candidate contracts are:

- Bourbon Restoration: `iwbd-1-1-2`;
- Orleans: `iwbd-58-20-257`;
- Greco-Turkish: `iwbd-115-43-802`, `iwbd-115-43-803`,
  `iwbd-115-43-804`, `iwbd-115-43-806`, `iwbd-115-43-807`,
  `iwbd-115-43-808`, `iwbd-115-43-809`, and `iwbd-115-43-819`;
- Franco-Turkish: `iwbd-116-44-820`, `iwbd-116-44-821`,
  `iwbd-116-44-823`, and `iwbd-116-44-824`; and
- China-Taiwan: `iwbd--9-91-1402`, `iwbd--9-91-1403`,
  `iwbd-153-57-1445`, `iwbd-153-57-1446`, `iwbd-153-57-1447`, and
  `iwbd-159-60-1460`.

The contract inventory and each named cohort are complete-or-fail. A missing
sibling, changed source fingerprint, or changed exact identity raises an error.
These bindings never become aliases. In particular, uncontracted bare
`Turkey` rows intersecting 1919-1923 remain denied even though exact reviewed
rows may bind the Turkish National Movement.

## Audit dispositions before publication

The first Wave 5 accuracy pass added four HCED exclusions: Dunamunde as a
duplicate of Riga, Lesnaya's reversed result, Napue's wrong-orientation Storkyro
duplicate, and Montijo's incorrectly coded English opponent. The independent
row-level audit then removed 19 more HCED rows and four IWBD rows from the
unpublished 4,429-event proposal. The published result is 4,406 events. These
23 proposal removals do not remove any Wave 4 event.

The 19 additional HCED dispositions are:

| Candidate | Reason it stays staged |
|---|---|
| `hced-Altona1714-1` | Phantom/misdated action and wrong actor. |
| `hced-Bronnitsa1614-1` | Reversed result; Sweden won. |
| `hced-Punitz1704-1` | Omits the principal Saxon opponent and substitutes Russia. |
| `hced-Salvador1638-1` | Reversed result; the Dutch assault failed. |
| `hced-Malacca1606-1` | Reversed result; the first VOC siege failed. |
| `hced-Beachy Head1707-1` | Portugal was not a belligerent. |
| `hced-Colonia do Sacrimento1735-1` | Reversed result; the Portuguese fortress held. |
| `hced-Reval1719-1` | Departure-port duplicate/mislabel of the Osel Island action. |
| `hced-Majadahonda1812-1` | Reversed result; French cavalry won. |
| `hced-Elba1811-1` | Misnamed El Bodon row with the result reversed. |
| `hced-Campo1811-1` | Duplicate/ambiguous Campo Maior assertion. |
| `hced-Azov1695-1696-1` | Conflates the opposite-result 1695 and 1696 campaigns. |
| `hced-Salvador1822-1823-1` | Crosses the modeled September 1822 Portuguese reset. |
| `hced-Aden1513-1` | Anachronistic Ottoman actor; Aden was Tahirid. |
| `hced-Wofla1542-1` | Drops the principal Adal army and retains Ottoman support alone. |
| `hced-Marbella1705-1` | Drops the principal French opponent and retains Spain alone. |
| `hced-Cadiz1810-1812-1` | Omits Spain, the principal defending polity. |
| `hced-Barrosa1811-1` | Omits the principal Spanish co-belligerent. |
| `hced-Riga1701-1` | Omits Saxony and rates Russian auxiliaries as the principal opponent. |

The four new IWBD exclusions are:

- `iwbd-108-40-788`: Riga 2 was fought against the Bermondt/West Russian
  Volunteer Army, not the Russian SFSR;
- `iwbd-115-43-810`: Akbas involved French guards, not Greece;
- `iwbd-115-43-811`: the 93-day Summer Offensive is an operational campaign
  umbrella, not one tactical battle; and
- `iwbd-115-43-812`: Gediz has the wrong result.

The final policy contains 62 HCED coded-pass exclusions and 10 IWBD curated
exclusions. Source rows remain immutable; exclusions are enumerated by exact ID
and emitted with reasons in release metadata.

## Coverage, provenance, and limits

The final 4,152 HCED events bind bijectively to source candidates. The
rating-neutral location layer publishes 4,115 strict Points, 4,072 exact
source-transcribed geographic-jurisdiction labels, and 4,119 closed provenance
objects. The frozen quarantine remains 37 Point candidates, 79 country-label
candidates, 33 overlapping candidates, and 83 unique affected events, plus one
source-blank country field. These are unreviewed source assertions, not verified
historical locations or sovereign-country truth.

The 106 sources span 31 provenance families. Exactly 4,366 events map to one
direct outcome family; the 40 curated seed events remain explicitly unmapped
until claim-level locators are reviewed. No event has multiple independently
established direct outcome families.

The source-role inventory is also measured rather than inferred: 60 sources
carry `identity_boundary_or_context_reference`, 37 carry
`curated_reference_pending_claim_level_outcome_locator`, four carry `outcome`,
two carry `identity_registry`, and one each carries `identity_crosswalk`,
`derived_project_continuity_convention`, and
`outcome_consistency_crosscheck`. A source can carry more than one role, so
these values are capability counts rather than a partition of 106.

This wave does not resolve the general partial-coalition limitation in dyadic
HCED rows, prove the correctness of every source assertion, or estimate global
historical completeness. Some defensible dyads inside larger coalitions remain
provisional until a curated co-belligerent table exists. The generic Portugal
window also begins in 1147 even though the identity begins in 1143; no current
cohort row falls in 1143-1146.

Any release-touching follow-up must rebuild `data/release/*`,
`data/catalog/registry.json`, and `web/data/results.json` together from the
explicit machine-local review queue, then synchronize documentation and tests
to that machine's measured values. Dashboard simulation hashes are deliberately
not pinned in this narrative review record.
