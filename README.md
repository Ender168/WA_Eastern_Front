# WA Eastern Front

Competitive two-player Eastern Front scenario built on **World Ablaze (9.6)**.

## Scenario baseline

- start date: **1 January 1941**;
- World Ablaze remains the mechanical and geographical base;
- playable countries:
  - `WEF` - Western Side;
  - `EEF` - Eastern Side;
- `OBS` owns the rest of the world;
- WEF and EEF have no ruler, advisors or inherited GER/SOV characters;
- historical World Ablaze country histories and OOBs are replaced;
- all 1107 states are statically assigned to WEF, EEF or OBS;
- WEF and EEF now have the same number of states;
- normal focus-tree progression is disabled;
- both players begin with generic/minor World Ablaze technology access;
- World Ablaze national technology packages remain available through adapted adoption decisions.

## Static map

Ownership totals:

- WEF: **182 states**
- EEF: **182 states**
- OBS: **743 states**
- Total: **1107 states**

WEF was expanded by 76 former OBS states using geographically coherent European
blocks: metropolitan France, Benelux, Switzerland, Denmark, Italy, Norway and Greece.

## State normalization

Every state has:

- manpower: **550,000**;
- infrastructure: **7**;
- air base: **5**;
- every existing naval base: **5**;
- every existing victory point: **10**.

All state resource blocks are removed.

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
- iron.

Steel and aluminium remain at **0**.

## Replace paths

WAEF replaces:

- `common/bookmarks`;
- `history/states`;
- `history/countries`;
- `history/units`.

## Technology

WEF and EEF are new minor-style tags, so no `technology_tags` override is
required. The retained compatibility copy is:

- `common/decisions/_unique_technologies_adoption.txt`

It preserves World Ablaze's existing technology packages and backfill effects,
while allowing WEF/EEF to use them without a donor faction relationship.

## Next systems

1. Runtime validation of the normalized 1941 map.
2. Starting armies, templates and equipment pools.
3. Fixed war-start rules and preparation period.
4. Industrial balancing.
5. Strategic scoring and defensive-depth mechanics.

## Dependency

World Ablaze Workshop ID: `2149567872`
