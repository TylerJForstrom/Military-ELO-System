# Wave 4 promotion review

Date: 2026-07-15

This is the current pickup record for the completed Wave 4 build.
`HANDOFF-REVIEW-TRIAGE.md` remains the historical review input; findings already
implemented or refuted there must not be applied a second time.

This record covers the approved event, outcome, participant, and identity decisions. Location publication remains a separate gate even when the underlying battle is approved. The completed location review withholds the source Points for Issus, Slaak, and Sas van Gent and the country/jurisdiction labels for Saints and Sas van Gent. Every surviving field remains an unreviewed source assertion, not a verified historical location or sovereignty determination.

## Implemented decisions

The following eleven source candidates were approved and encoded without broadening any generic resolver:

| Candidate | Decision |
| --- | --- |
| `hced-Miletus-334-1` | Macedonia defeated Persia in 334 BCE; exact label policy `macedonia` -> `macedonian_empire` for -336..-323. |
| `hced-Issus-333-1` | Macedonia defeated Persia in 333 BCE under the same exact policy. |
| `hced-Sebastopolis692-1` | Umayyad victory over Byzantium in 692; exact upstream spelling `ummayyad caliphate` -> `umayyad_caliphate` for 661..750. |
| `hced-Yaunis Khan1516-1` | Ottoman victory over the Mamluks in 1516; exact `mamluks` -> `mamluk_sultanate` for 1250..1517. The source remains year-only because reviewed secondary accounts disagree on a specific day. |
| `hced-Slaak1631-1` | Dutch Republic victory over Spain in 1631; exact `dutch rebels` -> `dutch_republic` for 1568..1795. |
| `hced-Sas van Gent1644-1` | Dutch Republic victory over Spain in 1644 under the same exact policy. |
| `hced-Saints1782-1` | British victory over France in 1782; exact upstream typo `untied kingdom` -> `united_kingdom` for 1707..current snapshot. |
| `iwbd-52-18-185` | Abtao, 7 February 1866: Spain versus the exact Chile-Peru coalition, inconclusive. Spain contributes 1.0 on its side; Chile and Peru contribute 0.5 each. |
| `iwbd-118-45-842` | Mishan, 17-18 November 1929: Soviet victory over China. It is concurrent with, but distinct from, `iwbd-118-45-840` Chalainor 2. |
| `iwd-23` | Ecuadorian-Colombian War, 1863: COW 100 resolves to `united_states_colombia` for 1863..1885. |
| `iwd-107` | Saudi-Yemeni War, 1934: COW 670 resolves to `kingdom_saudi_arabia` from 1932 through the current snapshot; COW 678 resolves to `mutawakkilite_kingdom_yemen` for 1918..1961. |

Abtao and Mishan are candidate-keyed exceptions with exact semantic fingerprints. Abtao also pins the resolver result for every reconstructed participant. Mishan pins the exact contained sibling set and both source rows. Any changed field, missing/extra sibling, duplicate reviewed row, or unexpected resolver identity raises a stale-policy error. Generic slash/comma/parenthesis labels and generic containment remain fail-closed.

The three new IWD identities have narrow canonical names and no generic `Colombia`, `Saudi Arabia`, or `Yemen` aliases. Existing same-name Cliopatria candidates for United States of Colombia and Kingdom of Saudi Arabia can be absorbed by the normal exact-name/overlap rule; the broad North Yemen envelope is not absorbed. The Mutawakkilite policy ends at 1961 so a year-only event cannot cross the 1962 coup/transition year.

## Reviewed candidates retained in staging

These eight near-misses are locked fail-closed and must not be promoted by alias fallback:

| Candidate | Reason |
| --- | --- |
| `hced-Megalopolis-331-1` | Chronology and the incomplete Macedonian coalition were not independently adjudicated. |
| `hced-Jaxartes-329-1` | The broad Scythia label does not identify the specific Saka force. |
| `hced-Antioch1268-1` | The Principality of Antioch interval ends at the 1268 destruction, not 1271; the boundary remains unadjudicated. |
| `hced-Mons1572-1` | The proposed source-side reconstruction omits the Huguenot co-belligerent. |
| `hced-Steenwijk1592-1` | The proposed source-side reconstruction omits the English co-belligerent. |
| `hced-Amjhera1728-1` | Conflicting chronology remains unresolved. |
| `hced-Abensberg1809-1` | The proposed two-polity rating omits principal Bavarian and other Confederation forces; this is an incomplete-coalition hold, not an asserted outcome correction. |
| IWD parent `1` | The proposed promotion requires a new Bourbon Restoration identity and review of the COW 220 continuity window. |

## Evidence anchors

- Miletus and Issus: [Perseus Miletus](https://www.perseus.tufts.edu/hopper/artifact?name=Miletus&object=Site), [Plutarch, Alexander 17.1](https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0243%3Achapter%3D17%3Asection%3D1), [Arrian I.19](https://en.wikisource.org/wiki/The_Anabasis_of_Alexander/Book_I/Chapter_XIX), and [Encyclopaedia Iranica, Alexander the Great](https://www.iranicaonline.org/articles/alexander-the-great-356-23-bc/).
- Sebastopolis: [Brandes, 2023, DOI 10.1515/9783111070315-003](https://doi.org/10.1515/9783111070315-003) and [Cecota, *Islam, the Arabs and Umayyad Rulers*](https://almuslih.org/wp-content/uploads/2024/11/Cecota-B-Islam-the-Arabs-and-Umayyad-Rulers-.pdf).
- Khan Yunis: [academic chapter DOI 10.31826/9781463229986-006](https://doi.org/10.31826/9781463229986-006). The evidence supports December 1516 but not a single uncontested day, so no day precision was added.
- Slaak and Sas van Gent: [Rijksmuseum, Battle of the Slaak](https://www.rijksmuseum.nl/nl/collectie/object/De-slag-op-het-Slaak-tussen-de-Nederlandse-en-Spaanse-vloten-in-de-nacht-van-12-op-13-september-1631--8766f960f603cea1bc6e5c86cbde0862) and [Rijksmuseum, siege and capture of Sas van Gent](https://www.rijksmuseum.nl/en/collection/object/Kaart-van-beleg-en-verovering-van-Sas-van-Gent%2C-1644--9a80f463bf976370c2a86b00405ee29f).
- Saints: [Royal Museums Greenwich, Battle of the Saints](https://www.rmg.co.uk/collections/objects/rmgc-object-12193).
- Abtao: [Chilean Navy, 7 February 1866](https://www.armada.cl/tradicion-e-historia/efemerides-navales/febrero/7-de-febrero-de-1866), which identifies the Spanish and Chilean-Peruvian forces and describes the action as having no victor or vanquished.
- Mishan: [IWBD codebook, section 5.17.9](https://www.ryangrauer.com/linked/belligerents_in_battle_codebook__v1.0.pdf) and the [U.S. Army CGSC study](https://cgsc.contentdm.oclc.org/digital/api/collection/p4013coll3/id/4298/download), which distinguishes the eastern Mishan operation from the western Manchouli/Dalainor operation.
- Colombia identity: [1863 constitution](https://www.archivogeneral.gov.co/sites/default/files/exposiciones_patrimonio/ConstitucionesColombia/1863/Texto1863.pdf) and [U.S. Department of State country history](https://history.state.gov/countries/colombia).
- Saudi and Yemen identities: [Saudi Ministry of Foreign Affairs history](https://mofa.gov.sa/en/ksa/Pages/history.aspx), [UK National Archives, Arabian Peninsula](https://www.nationalarchives.gov.uk/the-middle-east/arabian-peninsula/), and [Austrian Academy of Sciences, Mutawakkilite Kingdom 1918-1962](https://epub.oeaw.ac.at/0xc1aa5576_0x003ac93e.pdf).
- 1934 outcome: [UN Peacemaker, Treaty of Taif](https://peacemaker.un.org/en/node/9396) and [Sana'a Center analysis](https://sanaacenter.org/publications/policy-research/17828).

## Integrated build result

The release, registry, and dashboard were rebuilt together and the current-facing
documentation and test pins were synchronized to that same build. The measured
result is:

- 1,591 registry identities, 228 rated identities, and 4,245 rated events;
- 40 seed events, 1,769 crosswalk-resolved HCED events, 2,250 label-resolved
  HCED events, 56 IWD parent wars, 123 IWBD battles, and 7 UCDP termination
  episodes;
- 27,014 staged source records and an unchanged 23,390 event-like denominator,
  leaving 19,152 unresolved event-like candidates;
- 94 registered sources across 23 source families, with direct outcome mappings
  for 4,205 events: 4,019 HCED, 56 IWD, 123 IWBD, and 7 UCDP; and
- exact HCED bindings for all 4,019 rated HCED events, with 3,982 published
  Points, 3,939 published country/jurisdiction labels, and 3,986 provenance-bound
  events after quarantine.

The frozen location policy withholds 37 Point fields and 79 country/jurisdiction
fields; the manifests overlap on 33 events and affect 83 unique events. The
separate 49-row disputed/non-sovereign jurisdiction review retains 46 exact
source transcriptions and withholds 3. Its frozen contract digest is
`b209a0cc8d308d56d74012b53ea72bd29df34c4ac8a773b3602b38558c085b5e`.

## Rating impact relative to Wave 3

The ledger adds exactly 11 event IDs and removes none. Two existing IWD events
(Yom Kippur 1973 and the Gulf War 1991) change only by replacing the absorbed
Cliopatria Saudi candidate with the exact `kingdom_saudi_arabia` identity.

Chronological replay is expected to propagate small numerical changes beyond
the new rows: 1,283 common dashboard event records have a changed participant
delta, 110 common entity series change, and 69 pre-existing entities have a
changed final composite. The three largest final shifts are Republic of Ecuador
-1.773, Macedonian Empire of Alexander +1.613, and Achaemenid Empire -1.248.
These are intentional consequences of adding or migrating rateable evidence,
not location-only drift.

## Dashboard result

The dashboard was rebuilt with 1,000 deterministic sensitivity simulations. It
now provides an offline interactive battle map and an adjacent Top 5/8/12/20
standings list. The selected year is a hard information horizon across rating
series, rankings, search, pins, movers, events, evidence detail, and map markers:
an event remains unavailable until its end year, and map windows look backward
only. Map publication uses only the 3,982 non-quarantined HCED Points and keeps
the unreviewed-source/unknown-precision warning visible.

Future release-touching work must preserve the same atomic rebuild rule: rebuild
release + registry + dashboard together on one machine, then synchronize all
documentation and test count/digest pins to that machine's measured values.
