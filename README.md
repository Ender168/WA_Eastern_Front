# WA Eastern Front

Competitive Germany vs Soviet Union scenario built as a thin submod for
**World Ablaze (9.6)**.

## Scenario baseline

- start date: **1 January 1941**;
- World Ablaze remains the ruleset and map source;
- Germany and the Soviet Union are the two intended player countries;
- the rest of the world is consolidated under a dedicated passive `OBS` tag;
- no World Ablaze map/state files are copied;
- GER and SOV use clean symmetric country-history baselines;
- normal focus-tree progression is disabled;
- both players begin on World Ablaze generic/minor technology access;
- World Ablaze national technology packages are selectable through adapted versions of its existing adoption decisions;
- both players start with 30 civilian factories and choose one military-industry layout:
  - **Forward Industry:** 60 MIL, concentrated closer to the front;
  - **Deep Industry:** 50 MIL, dispersed into the rear.

## Core implementation

- `common/bookmarks/waef_1941.txt`
- `common/scripted_effects/waef_map_setup.txt`
- `common/scripted_effects/waef_industry_setup.txt`
- `common/decisions/waef_industry.txt`
- `history/countries/GER - Germany.txt`
- `history/countries/SOV - Soviet union.txt`
- `history/countries/OBS - Observer.txt`

## World Ablaze compatibility overrides

Two World Ablaze files are intentionally copied and minimally patched:

- `common/technology_tags/00_technology.txt`
- `common/decisions/_unique_technologies_adoption.txt`

These files must be diffed against upstream World Ablaze after relevant WA updates.
The project otherwise avoids copying World Ablaze systems.

## Next systems

1. Starting armies, templates and equipment pools.
2. Fixed war-start rules and preparation period.
3. Manpower/resource normalization where required.
4. Long-war and defensive-depth mechanics.
5. Periodic strategic scoring.

See `docs/MAP_SETUP.md` and `docs/SETUP_SYSTEMS.md`.

## Dependency

World Ablaze Workshop ID: `2149567872`
