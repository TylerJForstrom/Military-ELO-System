# Handoff: composite coalition-label splitting + next-identity tranche

Two coverage expansions are specified here, both ready to land through the wave
build's baseline-regeneration step. They are written as contracts rather than
applied directly because every event-adding change trips the coupled audit
(pinned tranche counts, location counts, quarantine SHAs, the frozen pre-1500
manifest, and the Wave 7 identity supersessions). That audit is regenerated as
part of a wave pass; hand-patching its ~8 pinned layers one error at a time is
the wrong tool. Both items below were verified against the current tree
(4,797-event build, 666 tests green) before being written down.

## Prerequisite finding: the "free policy" tier is exhausted

Every bare label that maps onto an already-curated identity now resolves. This
was confirmed by running the real `resolve_hced_side_label` over the whole
unresolved reservoir: `mexico -> mexican_republic`, `greece -> kingdom_greece`,
`israel -> clio_q801`, `netherlands -> dutch_republic`, `hungary`, `romania`,
`paraguay`, `brazil`, `iraq` all already resolve. The rows that still look
unresolved are blocked on the *opposing* side or fall outside the identity's
window, not on the label a policy would add. Do not add label policies for
already-resolving labels; measure resolution with the real resolver first.

The remaining ~3,300 outcome-aligned unpromoted rows break down as: ~2,821 need
a new identity or are correctly out-of-window; ~539 are blocked faction/peoples
labels (need new curated actors); ~348 are composite multi-entity side labels
(item 1 below); ~533 have codes/aliases on both sides but are held by a
stricter crosswalk unique-polity gate, dedup, or continuity (mostly correct
staging); ~55 are outcome-misaligned (correct staging).

## Item 1 — Composite coalition-label splitting (implemented + measured)

A comma/semicolon/ampersand-delimited side label ("Brazil, Argentina, Uruguay")
should resolve as a coalition when, and only when, every member independently
resolves to a distinct time-valid identity through the ordinary label resolver.
The participant builder already supports multi-entity sides (contribution
`1/len`, role `major_ally`), and the outcome-alignment check already compares
full normalized strings, so the winner "Brazil, Argentina, Uruguay" already
passes alignment. The only missing piece is splitting the raw label.

Measured yield on the current tree: **31 immediately-promotable post-1500
events** (War of the Spanish Succession, the Ogaden War with Ethiopia+Cuba vs
Somalia, the Scania War, Central American federation wars, the American
invasion of Grenada, etc.). Roughly 580 further composite rows flip
automatically as item 2's identities land (the War of the Triple Alliance is
the largest, once `argentina` exists). This is compounding infrastructure.

### Exact code

Add to `src/military_elo/promotion/common.py` (next to `_participants`):

```python
def _split_composite_label(raw: Any) -> list[str]:
    """Split a raw coalition side label into its members.

    Splits only on comma, semicolon, and ampersand -- never on " and ", which
    appears inside single polity names (Bosnia and Herzegovina, Trinidad and
    Tobago). An Oxford-comma "and" prefix ("A, B, and C") is stripped from a
    member. Returns ``[]`` when the label is not a delimited composite (fewer
    than two members), so a single polity name is never mistaken for a
    coalition.
    """
    members: list[str] = []
    for part in re.split(r"[;,&]", str(raw or "")):
        cleaned = part.strip()
        if cleaned.lower().startswith("and "):
            cleaned = cleaned[4:].strip()
        if cleaned:
            members.append(cleaned)
    return members if len(members) >= 2 else []
```

In `src/military_elo/promotion/hced.py`: import `_split_composite_label`, add a
module constant, and replace the uncoded-side failure branch inside
`promote_hced_label_rows` (the `else` after single-label resolution) with a
composite fallback:

```python
# Composite splitting applies only to the un-frozen post-1500 reservoir; the
# pre-1500 wave is an exact-manifest, exhaustively cited cohort.
_COMPOSITE_SPLIT_MIN_YEAR = 1500
```

```python
if entity_id:
    if polity:
        pending_polities[entity_id] = polity
    resolved.append(entity_id)
    side_tiers.append(str(tier))
    label_side_count += 1
    if tier == "crosswalk_observation":
        observation_hits.append((normalize_label(label), entity_id))
elif low_year < _COMPOSITE_SPLIT_MIN_YEAR:
    rejections[reason or "no_unique_time_valid_label_match"] += 1
    resolution_failed = True
else:
    members = _split_composite_label(label)
    member_ids: list[str] = []
    member_polities: dict[str, dict[str, Any]] = {}
    composite_ok = len(members) >= 2
    for member in members:
        member_id, member_polity, _reason, _tier = resolve_side_label(
            member, low_year, high_year
        )
        if not member_id:
            composite_ok = False
            break
        member_ids.append(member_id)
        if member_polity:
            member_polities[member_id] = member_polity
    if composite_ok and len(set(member_ids)) == len(member_ids):
        pending_polities.update(member_polities)
        resolved.extend(member_ids)
        side_tiers.append("label_composite")
        label_side_count += 1
    else:
        rejections[reason or "no_unique_time_valid_label_match"] += 1
        resolution_failed = True
```

The existing `set(side_a) & set(side_b)` guard still rejects an entity on both
coalitions. Members always resolve via the generic `resolve_side_label`, never
a candidate-keyed contract.

### Integration cascade this triggers (regenerate, do not hand-count)

Verified sequence of guards, in the order the build hits them:

1. **Pre-1500 frozen manifest** — the split correctly declines pre-1500 rows via
   `_COMPOSITE_SPLIT_MIN_YEAR`, so `annotate_and_validate_wave6_pre1500_events`
   stays green. Two correct ancient composites are deliberately deferred:
   `hced-Syracuse-414-1` (Syracuse+Sparta vs Athens, 414 BCE) and
   `hced-Cremaste-388-1` (Sparta+Persia+Syracuse vs Athens, 388 BCE). Fold them
   into the Wave 6 manifest with their own citations if wanted.
2. **`hced_location.HCED_WAVE5_CANDIDATE_BINDINGS`** `4_152 -> 4_183` (+31).
3. **`orchestrator.py` tranche check** label baseline `2_328 -> 2_359` (+31);
   crosswalk `1_824` unchanged.
4. **Location baselines** (all +31; every composite event carries point,
   country, and provenance): `HCED_WAVE5_POINT_ASSERTIONS 4_115 -> 4_146`,
   `HCED_WAVE5_COUNTRY_ASSERTIONS 4_072 -> 4_103`,
   `HCED_WAVE5_PROVENANCE_OBJECTS 4_119 -> 4_150`.
5. **Second-tier expected pins** in `hced_location.py` also move (+31 each):
   `HCED_EXPECTED_CANDIDATE_BINDINGS 4_535`, `HCED_EXPECTED_POINT_ASSERTIONS
   4_498`, `HCED_EXPECTED_COUNTRY_ASSERTIONS 4_455`,
   `HCED_EXPECTED_PROVENANCE_OBJECTS 4_502`.
6. **Wave 7 Global supersession guard** — the Boer War composite
   ("Transvaal, Orange Free State" vs UK) resolves `orange free state` to the
   superseded `clio_q218023_1856_cfb4e08e` envelope. The composite member
   resolver must apply the same identity supersession remap the wave post-pass
   applies (`WAVE7_GLOBAL_SUPERSESSIONS` and the pre-1500 registry
   supersessions), or that Boer row must be excluded until the remap is shared.
   This is the one correctness coupling, not just a count.
7. Downstream: registry/metadata coverage counts, the point/country quarantine
   event SHAs (recompute over the new event-id sets), the dashboard 1,000-sim
   rebuild, README/docs counts, and any `test_wave*` pins that assert exact
   totals.

### Tests to add

Unit tests for `_split_composite_label` (comma/semicolon/ampersand split,
Oxford-comma "and" strip, single name never split, "Bosnia and Herzegovina"
never split); a label-pass test that a fully-resolving post-1500 composite
promotes one coalition event with `side_identity_resolution` tier
`label_composite`; a test that a composite with one unresolved member stays
staged; and a test that a pre-1500 composite is declined.

## Item 2 — Next state-identity tranche (crisp boundaries only)

Add these curated state identities (each has a clear founding and dissolution,
unified command, and unblocks aligned rows once its label policy exists). Same
M4 template as the committed tranche: seed entity + Britannica source + label
policy window + code policy where a COW/GW code applies. Row counts are the
opponent-blocked aligned rows each unlocks today (they compound with item 1 for
the coalition rows).

- **Mahdist State (Sudan, 1881-1899)** — Mahdi's proclamation to Omdurman;
  labels `mahdists`, `mahdiyya`, `the mahdiyya`, `sudanese mahdists`,
  `sudanese islamists`. ~17 rows across the British Sudan wars. Cleanest.
- **Argentine Republic (1861-1930)** — Pavon/reunification to the 1930 coup;
  fills the gap between the curated `argentine_confederation` (1831-1861) and
  the Cliopatria modern interval (from 1930). Unblocks the War of the Triple
  Alliance coalition rows (with item 1) and the 1865+ `argentina` opponent.
- **Kingdom of Bulgaria (1878/1908-1946)** — Second Balkan War and both world
  wars; label `bulgaria`. Unblocks the 2nd Balkan War and WWI coalition rows.
- **Republic of Texas (1836-1846)** — independence to US annexation; labels
  `texas`, `texan rebels`. Unblocks the Texan war rows opposite `mexico`
  (which already resolves).
- **Syria (modern, 1946-)** — post-mandate republic; label `syria`. Unblocks
  the Israeli War of Independence and Yom Kippur rows opposite `israel` (which
  already resolves). Confirm the modern-Syria Cliopatria interval or add a
  curated identity; keep the 1958-1961 United Arab Republic era in mind.

Defer fuzzier indigenous-actor identities (Sioux, Xhosa, Apache, Maori,
Cheyenne) to a reviewed pass; their boundaries hit the project's
pause-rather-than-guess rule more often.

Item 2 lands through the same regeneration cascade as item 1 (it produces
events), so batch both into one wave rebuild and regenerate all pinned
baselines/hashes once.

## Verification target

After integration: full test suite green (add the item-1 unit tests and item-2
window-pin tests), audit clean, release + registry + 1,000-sim dashboard
rebuilt together, and every count re-synced across release metadata, registry,
results.json, README, and docs. Spot-check a sample of the new composite and
identity events for era-correct belligerents before committing.
