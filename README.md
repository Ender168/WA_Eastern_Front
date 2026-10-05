# WA Eastern Front

Competitive Germany vs Soviet Union scenario built as a thin submod for
**World Ablaze (9.6)**.

## Current concept

- scenario start: **1 January 1941**;
- World Ablaze remains the ruleset and map source;
- Germany and the Soviet Union are the two intended player countries;
- the rest of the world is neutralized under an observer/world-holder;
- no copied World Ablaze map files unless a future mechanic absolutely requires it.

## Map bootstrap

The first implementation is in:

- `common/bookmarks/waef_1941.txt`
- `common/scripted_effects/waef_map_setup.txt`
- `docs/MAP_SETUP.md`

The scenario keeps World Ablaze province/state geometry, terrain, resources,
railways, supply hubs, air regions and strategic regions. Ownership is reassigned
by script when the January 1941 bookmark starts.

## Planned systems

1. Validate the initial GER-SOV border and neutral world holder.
2. Replace the standard national setup with the competitive industry choices.
3. Start GER and SOV on the minor/generic World Ablaze technology tree.
4. Add decisions to adopt one of World Ablaze's existing national technology trees.
5. Remove or neutralize normal national focus-tree progression.
6. Add war-start rules and long-war mechanics.
7. Add periodic strategic scoring.

## Dependency

World Ablaze Workshop ID: `2149567872`
