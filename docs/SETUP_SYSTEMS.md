# Competitive setup systems v0.16 — compact land-war core

## Confirmed foundation

The static-tag ordering fix is confirmed in game. WEF and EEF both launch as
ordinary countries at 1941.1.1.12, so the diagnostic phase is closed.

## Finalized map pass

The 182/182 bootstrap map is compacted at scenario initialization.

- WEF: 141 playable states.
- EEF: 141 playable states.
- OBS: 825 states.
- Norway, Greece, southern/island Italy and most of France are removed from WEF.
- WEF keeps a compact north-eastern French belt, Benelux, Switzerland,
  northern/central Italy and the continental Danish connection.
- States 16, 28 and 29 fill the previous OBS holes in that retained western belt.
- Siberia, the Far East and the Central Asian extension beyond the intended
  Ural theatre are transferred from EEF to OBS.

## Map normalization

At scenario start:
- every state category is set to `city` (15 shared building slots);
- the two inherited +2 Belgian slot bonuses are neutralized;
- infrastructure is level 7;
- all civilian/military factories are cleared globally;
- every WEF/EEF state receives exactly 1 CIV and 1 MIL;
- all dockyards are removed;
- all land forts, coastal forts and stronghold networks are removed;
- every inherited supply node is removed;
- every WEF/EEF state receives one supply node at its first VP (the WA regional
  capital/main city convention), with a fallback node for states without a VP;
- the entire inherited railway graph is normalized to level 3.

## Population

All static states start at 550,000 population. Each final WEF/EEF state receives
+175,000 at scenario initialization.

141 × 725,000 = 102,225,000 civilian population per player.

## Resources

The existing capital-resource convention is retained. Berlin and Moscow each
hold 10 oil, rubber, tungsten, chromium, coal, bauxite and steel.
Iron and aluminium remain at zero.

## Runtime cleanup

The mod now replaces:
- `history/countries`;
- `history/units`;
- `common/decisions`;
- `common/decisions/categories`.

Only WEF/EEF/OBS country histories are active and inherited WA OOB files are
disabled. Historical WA decision clutter is removed.

## Technology assimilation

WEF and EEF both have 10 research slots and immediately see seven mutually
exclusive zero-cost choices:

- French;
- Italian;
- Japanese;
- German;
- Soviet;
- British;
- United States.

Each decision preserves the original World Ablaze adoption complete-effect.
After one is selected, `waef_technology_assimilated` permanently hides and
locks the other six choices.
