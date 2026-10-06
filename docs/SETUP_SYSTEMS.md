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
- every pair of adjacent playable states gets an end-to-end level-3 railway
  route between their two regional supply hubs;
- routes are calculated through adjacent land provinces;
- shared trunks are deduplicated into unique railway segments, so multiple
  hub-to-hub routes can share the same physical track without duplicate edges.

## Technology assimilation

All seven WA technology schools remain available. The original WA national
technology flags and dated technology grants are preserved. WAEF does not add
WA's `foreign_technologies` idea at all, so its -10% Major Technologies
research-speed penalty never applies to WEF/EEF.


## v0.18 — Eastern edge cleanup and heavier starting industry

The detached EEF states 742, 732, 40 and 654 are removed from the playable
theatre. They are replaced by 1027, 407, 1015, 1014 and 406, producing a more
continuous eastern/rear boundary.

Final ownership after this pass:
- WEF: 141 states;
- EEF: 142 states;
- OBS: 824 states.

Playable-state industry is increased to:
- 2 civilian factories;
- 5 military factories.

The regional supply generator is rerun after ownership changes. Every newly
added EEF state receives its own supply hub and is included in the automatic
level-3 rail mesh between adjacent playable states.

Technology baseline is intentionally not bundled into this map/industry pass.
The planned implementation is a separate one-time 1940 baseline decision
unlocked only after a technology school is assimilated. That keeps national
tree selection and bulk tech granting independently testable.


## v0.19 — exact state symmetry, 1940 baseline and national Grand Strategy

State 583 is removed from EEF and assigned to OBS. The playable state count is
again exactly 141 WEF / 141 EEF / 825 OBS. Supply hubs and railways are
regenerated after the removal.

Each technology Assimilate now also assigns the matching World Ablaze Grand
Strategy doctrine:
- France: noria_tactics;
- Italy: rapid_decision;
- Japan: bushido;
- Germany: auftragstaktik;
- Soviet Union: deep_battle;
- Britain: british_professionalism;
- United States: overwhelming_firepower.

After Assimilate, a separate one-time zero-cost decision applies the 1940
technology baseline. The baseline is generated from the pinned World Ablaze
technology definitions rather than maintained by hand.

Generation rules:
- start_year <= 1940;
- shared Industry/Electronics/Support technologies;
- only the selected national air/armor/artillery/infantry/naval files;
- doctrine technologies excluded;
- dependencies and sub-technologies included recursively;
- DLC-gated alternatives preserve their DLC conditions.
