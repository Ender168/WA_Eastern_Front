# WA Eastern Front

Competitive two-player Eastern Front scenario built on **World Ablaze (9.6)**.

## Scenario baseline

- start date: **1 January 1941**;
- World Ablaze remains the mechanical and geographical base;
- playable countries:
  - `WEF` - Western Side;
  - `EEF` - Eastern Side;
- `OBS` owns the rest of the world;
- WEF and EEF have no inherited GER/SOV rulers, advisors or OOBs;
- all 1107 states are statically assigned to WEF, EEF or OBS;
- normal focus-tree progression is disabled;
- both players can choose one World Ablaze national technology school;
- after the school choice, a separate one-time decision applies the 1940 technology baseline;
- both players can make one permanent ideology choice: democratic, fascist or communist;
- WEF and EEF have access to a shared generic tank MIO based on World Ablaze's own generic tank archetype;
- both sides start with a shared Great War air-doctrine baseline, 100 Army XP and 100 Air XP, plus optional startup doctrine mastery decisions and a temporary Land/Air doctrine cost waiver through 29 January 1941;
- after the 1940 baseline, a one-time force setup decision creates suppression, infantry and medium-tank templates, 300 fully trained infantry divisions, 30 fully trained tank divisions, 50 generals and 5 field marshals per player.

## Static map

Ownership totals:

- WEF: **141 states**
- EEF: **141 states**
- OBS: **825 states**
- Total: **1107 states**

The playable theatre is deliberately compact. Detached and remote states are
removed from WEF/EEF and replaced by geographically more useful rear/border
states while preserving exact state-count symmetry.

## State normalization

Every state has:

- infrastructure: **7**;
- state category: **city**.

Player states additionally have:

- manpower: **725,000**;
- **2 civilian factories**;
- **5 military factories**.

OBS states use **550,000** manpower and receive no WAEF civilian or military
factories.

Inherited forts, air bases, naval bases, dockyards, anti-air, refineries,
special buildings and state modifiers are removed by the clean-map generator.

## Resources

Only the player-capital states receive resources:

- WEF capital state 810;
- EEF capital state 219.

Each capital receives **10** of:

- oil;
- rubber;
- tungsten;
- chromium;
- coal;
- bauxite;
- steel.

Iron and aluminium are absent.

## Supply

- one generated supply hub per WEF/EEF state;
- hubs use the first VP province where possible;
- adjacent playable states are connected by generated level-3 railways;
- railway routing uses the pinned World Ablaze province bitmap;
- shared railway segments are deduplicated.

## Replace paths

WAEF replaces:

- `common/bookmarks`;
- `history/states`;
- `history/countries`;
- `history/units`.

## Technology

Seven World Ablaze technology schools are available:

- France;
- Italy;
- Japan;
- Germany;
- Soviet Union;
- Britain;
- United States.

Each school also assigns its matching World Ablaze Grand Strategy doctrine.
The 1940 baseline is generated from the pinned World Ablaze technology files
with a 1940 cutoff and dependency closure.

## Next systems

1. Starting armies, templates and equipment pools.
2. Fixed war-start rules and preparation period.
3. Industrial balancing.
4. Strategic scoring and defensive-depth mechanics.
5. Runtime balance testing of technology schools and MIO progression.

## Dependency

World Ablaze Workshop ID: `2149567872`
- v0.23 scenario economy baseline: symmetric per-state resources/refineries, 800 starting PP, constrained fuel storage, train/truck stockpiles, Regular spawned divisions and 100-week manpower accounting.
