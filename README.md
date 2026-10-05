# WA Eastern Front

Competitive two-player Eastern Front scenario built on **World Ablaze (9.6)**.

## Scenario baseline

- start date: **1 January 1941**;
- World Ablaze remains the mechanical and geographical base;
- the playable countries are custom scenario tags:
  - `WEF` - Western Side;
  - `EEF` - Eastern Side;
- `OBS` owns the rest of the world;
- WEF and EEF have no ruler, advisors or inherited GER/SOV characters;
- historical World Ablaze country histories and OOBs are replaced;
- all 1107 World Ablaze states are statically assigned to WEF, EEF or OBS;
- normal focus-tree progression is disabled;
- both players begin with generic/minor World Ablaze technology access;
- World Ablaze national technology packages remain available through adapted adoption decisions;
- both players receive the same civilian industrial baseline and choose:
  - **Forward Industry:** 60 MIL closer to the front;
  - **Deep Industry:** 50 MIL in the rear.

## Static map

The complete generated state set lives in `history/states`.

Ownership totals:

- WEF: **106 states**
- EEF: **182 states**
- OBS: **819 states**
- Total: **1107 states**

The state generator is kept in `tools/generate_static_states.py` and is pinned
to World Ablaze commit `691c7085f3ec1333ac2a0742983da8a64011ca8b`.

See `docs/STATIC_MAP.md`.

## Replace paths

WAEF replaces:

- `common/bookmarks`;
- `history/states`;
- `history/countries`;
- `history/units`.

The original GER/SOV country-history overrides and the old scripted map-transfer
system have been removed.

## Technology

WEF and EEF are new minor-style tags, so no `technology_tags` override is
required. The only retained upstream compatibility copy is:

- `common/decisions/_unique_technologies_adoption.txt`

It preserves World Ablaze's existing technology packages and backfill effects,
while allowing WEF/EEF to use them without a donor faction relationship.

## Next systems

1. Runtime validation of the static 1941 scenario.
2. Starting armies, templates and equipment pools.
3. Fixed war-start rules and preparation period.
4. Manpower/resource balancing if testing shows it is required.
5. Strategic scoring and defensive-depth mechanics.

## Dependency

World Ablaze Workshop ID: `2149567872`
