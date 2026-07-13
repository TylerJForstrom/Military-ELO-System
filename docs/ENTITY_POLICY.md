# Historical entity and continuity policy

## Governing rule

The rating unit is a versioned historical polity or autonomous military actor, not a normalized country name. When standard historical works conventionally treat a polity or empire as new, it receives a new entity ID and starts at the 1500 prior with maximum uncertainty.

Predecessor and successor links never transfer rating points.

## Default decisions

A new entity is created when:

- historiography conventionally treats it as a new polity or empire;
- a state dissolves into successors;
- a merger creates a new sovereign polity;
- a secession creates a new actor;
- a conqueror-founded regime is conventionally treated as distinct;
- rival governments in a civil war field materially independent forces;
- a documented project override requires a split.

A new entity is not created solely for a monarch, dynasty, capital, translated name, ruling party or constitutional change unless historical convention treats the resulting actor as a new state or empire.

## Special cases

- **Secession:** the parent continues unless it dissolves; the secessionist starts new.
- **Personal union:** members remain separate unless military command, taxation and armed forces are genuinely integrated.
- **Vassals and clients:** rate separately when they field forces under materially autonomous command. The same troops cannot be credited twice.
- **Governments in exile:** continuity requires strong legal/historiographic support and forces still under that government.
- **Restoration:** reuse an ID only when scholarship conventionally treats it as restoration of the same polity; otherwise reset.
- **Civil-war victory:** the winning faction and resulting successor polity can be linked but are not automatically the same entity.
- **Changing sides:** use separate participation episodes, not two simultaneous coalition memberships.

## Source-label identity policies

Open datasets sometimes label a polity with a name that does not identify the
historical actor by itself. Those labels are resolved only through explicit,
time-bounded policies, never through loose name similarity:

- **COW code 365 ("Russia"):** resolves to the Russian Empire through 1917 and
  to the Soviet Union from 1922 through 1991. The 1918-1921 revolutionary years
  deliberately resolve to nothing, so wars against the early RSFSR stay staged
  rather than being attached to either neighboring identity. No rating crosses
  the 1917 or 1991 boundaries.
- **"France" in modern interstate sources:** resolves to the curated French
  Fifth Republic identity (1958-present), which starts at the baseline like
  every new polity. Earlier French kingdoms, empires, and republics are
  separate identities, and labels naming France between their intervals stay
  unresolved.

## Rome and Byzantium project convention

This project implements the requested rule that the Byzantine Empire does not inherit Rome's rating. The v1 registry uses 395 CE as a practical split convention and records an explicit reset. There is no uncontested scholarly “Byzantine start” date, so 330, 395, 476 and 610 should be available as sensitivity alternatives in a mature release.

The decision record must say that this is a project convention, cite boundary sources, and retain predecessor/successor metadata without transferring any points.

## Required identity record

The production registry should contain:

```text
entity_id
canonical_name
aliases
polity_type
existence_start_low / best / high
existence_end_low / best / high
predecessor_ids / successor_ids
continuity_decision
rating_reset
boundary_sources
boundary_confidence
project_override_reason
external identifiers (Seshat, Wikidata, COW, GW, UCDP)
reviewer / reviewed_at / version
```

Name matching and automated source crosswalks may propose an identity link, but only an approved decision can enter rated data.
