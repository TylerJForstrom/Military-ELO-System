# Military History Elo methodology

## What the score means

This project measures documented military success relative to the opponents and circumstances an actor actually faced. It does **not** estimate who would win a hypothetical fight between a modern state and an ancient empire. Technology, disconnected opponent networks, missing evidence, and changing definitions make that claim undefendable.

The system publishes four values rather than hiding everything in one number:

1. **Tactical rating** — battles, sieges, raids and other engagements.
2. **Operational rating** — campaigns and major operations.
3. **Strategic rating** — participant-specific outcomes of completed wars.
4. **Historical success index** — a declared editorial summary of peak, sustained and cumulative opponent-adjusted success within a connected opponent network.

Each layer starts at 1500 with high uncertainty. A successor or newly recognized polity always starts from that prior; predecessor ratings are descriptive history, never inherited points.

## Event hierarchy and double-counting

```text
war
└── campaign / operation
    └── engagement / battle / siege / raid
```

- Engagements update only the tactical layer.
- Campaigns update only the operational layer.
- Completed-war outcomes update only the strategic layer.
- A battle can be nested within a campaign and war, but it is never inserted twice into the same rating stream.
- One-sided violence against civilians is not a competitive match and is never scored as a victory.
- Ongoing, disputed and excluded records are visible to the review process but are not rated as completed outcomes.

## Outcomes are vectors, not a win/loss switch

Tactical events use:

- battlefield control;
- mission objective;
- force preservation;
- positional gain.

Operational events use:

- campaign objective;
- theater control;
- force preservation;
- tempo and initiative;
- logistics and sustainment.

Strategic events use:

- battlefield outcome;
- documented political-objective attainment;
- territorial outcome;
- sovereignty/regime survival;
- settlement durability;
- force preservation.

Every value is coded from 0 to 1 from that participant's perspective. The strategic weights change by war type. An intervention or insurgency emphasizes political objectives; a conquest emphasizes territory and sovereignty; a world war gives more weight to state/regime survival.

Uncertain evidence is pulled toward 0.5 rather than converted to a confident win, loss or draw:

```text
adjusted utility = 0.5 + (coded utility - 0.5) × evidence confidence
```

An unknown outcome remains unknown and is not rated until reviewed.

## Result classes

The displayed result class is separate from its numerical utility and importance.

| Actual score | Default class |
|---:|---|
| 0.00–0.05 | Existential defeat |
| 0.05–0.20 | Major strategic defeat |
| 0.20–0.40 | Limited defeat |
| 0.40–0.47 | Negotiated disadvantage |
| 0.47–0.53 | Stalemate or inconclusive |
| 0.53–0.60 | Negotiated advantage |
| 0.60–0.80 | Limited victory |
| 0.80–0.95 | Major strategic victory |
| 0.95–1.00 | Existential/terminal victory |

Curators may apply a more precise class when the historical termination is known, such as withdrawal, capitulation, imposed settlement, low activity, annexation, or actor ceasing to exist.

## Why Vietnam and Germany in 1945 are different

The U.S. in Vietnam can receive a major strategic defeat because its principal political objective failed and it withdrew. Its battlefield performance, homeland sovereignty and regime survival are separately coded, and its participant-relative stakes and national scale are below an existential total war.

South Vietnam can simultaneously receive an existential defeat because the state ceased to exist. North Vietnam can receive a decisive strategic victory because its principal objective was achieved. Germany in 1945 receives a much larger terminal-defeat treatment because the event involved capitulation, occupation, regime destruction, loss of core territory and total-war national stakes.

Thus participants in the same war need not receive mirror-image labels, and two entities both called “losers” need not receive remotely equal consequences.

## Expected result and context

For a pair of opposing participants:

```text
expected = 1 / (1 + 10 ^ (-(rating difference + context adjustment) / 400))

actual = 0.5 + 0.5 × (participant utility - opponent utility)
```

Context can include only sourced values:

- force-size ratio, capped so disputed ancient estimates cannot dominate;
- home/away advantage;
- coalition contribution and role.

A favorite with a large force should gain less for an expected victory, while an underdog should gain more for an upset. Missing context is left missing; it is not imputed as a hidden fact.

## Scale, stakes and participant importance

Event-wide scale is classified as skirmish, battle, campaign, theater, major war or total war. Event-wide stakes are low, limited, major or existential. Each participant can additionally have 0–1 values for its own stakes and national share committed or affected. Geographic/system scope is also 0–1.

Participant importance is:

```text
M = clip(0.25, 3.00,
         0.25 + 1.25 × participant stakes
              + 0.90 × national scale
              + 0.60 × geographic scope)
```

The rating update uses only a bounded square-root-like information adjustment, so one giant war cannot erase an entire prior history. Cumulative achievement uses the full participant importance. Raw deaths are not used as a cross-era importance scale; ancient and modern casualty estimates are not commensurable.

## Coalition handling

Coalition credit is based on a participant's documented contribution and role. Default role multipliers distinguish coalition leads, major allies, supporting allies, expeditionary contingents and proxy sponsors.

Pair weights are normalized within each opposing side, so adding a list of tiny or duplicate allies cannot manufacture extra rating points. Pairwise updates conserve total rating points. Participant-specific utilities, stakes and contribution still produce different consequences for allies on the same side.

## K factor

The layer base is multiplied by bounded factors for event scale, stakes, decisiveness, evidence confidence and duration:

```text
K_event = clip(4, 96,
  K_layer × scale × stakes × decisiveness × confidence × duration)
```

Current bases are 28 tactical, 34 operational and 42 strategic. They are model parameters, not historical facts, and must be calibrated on chronological holdouts as the adjudicated dataset grows.

## Uncertainty and inactivity

Every new entity begins with rating uncertainty 350. Evidence reduces uncertainty; elapsed inactive time increases it without changing the mean rating. Peace is not recorded as a loss, and the absence of records is not treated as victory or deterrence.

Routine builds can run seeded Monte Carlo sensitivity simulations. Low-confidence outcome dimensions are perturbed more than high-confidence ones, and plausible model weights are sampled. The output includes median, 10th–90th percentile, median rank and probability of a top-ten finish. A production release should use at least 1,000 simulations and source-family/bootstrap and entity-boundary alternatives.

An entity is “established” only after at least five effective events, three completed wars and composite uncertainty no greater than 200. Other rankings are marked provisional.

## Disconnected networks and cross-era comparison

If two entities have no path through shared opponents, their raw Elo difference is not identified by the data. The engine assigns a network component and publishes a warning. The historical-success index uses percentiles within each connected network rather than pretending that an ancient isolated rating and a modern global rating share a directly observed scale.

The index is:

```text
40% peak percentile
+ 35% sustained percentile
+ 25% cumulative achievement percentile
```

For provisional actors, that raw index is shrunk toward 50 using effective event count, completed-war count and opponent-network size. This prevents a polity with one surviving victory record from appearing as a certain all-time leader. Both the raw percentile index and the coverage-adjusted headline remain available in the generated data.

Peak, sustained and achievement remain separately visible. No single index is presented as objective truth.

## Bias controls

The project must publish coverage by century, region, war type, domain and source quality. Known risks include survivor/victor bias, Eurocentric and modern over-documentation, famous wars being split into more records, non-state actors being omitted, and copied web pages masquerading as independent sources.

Controls include immutable raw snapshots, claim-level provenance, source-family deduplication, explicit missingness, review queues, blind adjudication samples, alternative entity boundaries, region/source-language checks and leave-one-dataset-out sensitivity runs. Automated extraction proposes records; it never approves identity, objectives or strategic outcomes.

## Validation

The automated suite checks rating conservation, successor resets, coalition behavior, confidence shrinkage, force advantage, and terminal-versus-limited defeat magnitude. Planned calibration checks include same-period order sensitivity, duplicate ingestion, chronological Brier/log loss, calibration by era/type, source-family bootstrap and comparison against Glicko/dynamic Bradley–Terry variants.
