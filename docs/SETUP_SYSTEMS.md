# Competitive setup systems v0.17 — static clean map and regional supply mesh

## Why v0.16 did not visibly change the country-selection map

The v0.16 ownership changes were applied from the bookmark effect. That is too
late for the scenario-selection map and some startup systems. WAEF now bakes
the final ownership directly into all generated state histories.

## Static final theatre

- WEF: 141 states.
- EEF: 141 states.
- OBS: 825 states.
- States 16, 28 and 29 are WEF.
- Norway, Greece, southern/island Italy and most of France are OBS.
- The eastern playable theatre ends at the Urals; Siberia, the Far East and
  the removed Central Asian extension are OBS.

## State-history whitelist

Every one of the 1107 state files is reconstructed from a minimal whitelist:
- state id and name;
- provinces;
- victory points;
- final owner/controller/core;
- normalized population;
- state category;
- the new minimal buildings block;
- designated capital resources only.

This deliberately removes all inherited:
- dynamic state modifiers;
- dated state effects;
- forts and stronghold networks;
- naval bases and dockyards;
- air bases;
- anti-air;
- refineries and silos;
- special/landmark buildings;
- extra building-slot effects;
- claims and historical state-side scripts;
- resource blocks outside the designated capitals.

## Construction baseline

- every state category: city (15 shared slots);
- infrastructure: 7 everywhere;
- WEF/EEF: exactly 1 civilian factory + 1 military factory per state;
- OBS: no civilian or military factories from WAEF state history;
- WEF/EEF population: 725,000 per state = 102,225,000 per player.

## Resources

Only Berlin (810) and Moscow (219) carry scenario resources:
- oil 10;
- rubber 10;
- tungsten 10;
- chromium 10;
- coal 10;
- bauxite 10;
- steel 10.

Iron and aluminium are absent, and every other state has no resource block.

## Supply and railways

- exactly one supply hub is generated for every WEF/EEF state;
- hub position is the state's first victory-point province, falling back to the
  first province only when the state has no VP;
- province adjacency is derived from World Ablaze's pinned provinces.bmp;
- every pair of adjacent playable states gets a direct level-3 railway route
  between their two regional supply hubs;
- the route is calculated through adjacent land provinces rather than by
  pretending the two capital provinces magically touch each other.

## Technology assimilation

All seven WA technology schools remain available. The original WA adoption
flags and technology grants are preserved, but the foreign_technologies idea
is removed at the end of adoption so its -10% Major Technologies research
penalty does not remain on WEF/EEF.
