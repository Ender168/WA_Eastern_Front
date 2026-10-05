# Map setup v1.0

The scenario now uses a **static 1107-state ownership map**.

The previous runtime ownership-transfer system has been removed.

## Countries

- `WEF`: Western Side
- `EEF`: Eastern Side
- `OBS`: neutral world holder

GER and SOV are not player countries.

## Ownership

WEF receives states whose original World Ablaze owner was:

- GER
- AUS
- CZE
- HUN
- YUG
- BUL
- ROM
- POL

with the eastern-border overrides below.

EEF receives states whose original owner was:

- SOV
- LIT
- LAT
- EST

and additionally:

- Eastern Poland: 96, 95, 1058, 97, 94, 93, 91, 89, 1059
- Vilnius / Druskininkai: 784, 1065
- Romanian concessions: 80, 78, 766

Memel (188) is explicitly WEF.

Every remaining state is OBS.

Final totals:

- WEF: 106
- EEF: 182
- OBS: 819

## State-history cleanup

For every state, all previous political history entries are removed:

- owner/controller;
- core additions/removals;
- claims additions/removals.

Then exactly one scenario owner, controller and core is inserted.

This is important because dated World Ablaze history from 1938-1940 would
otherwise transfer territory back to historical tags when the game executes
history up to January 1941.

Non-political state content remains intact.

## Source and regeneration

The user-provided `states.rar` was used as the 1107-state reference set.

The repository generator is pinned to World Ablaze commit:

`691c7085f3ec1333ac2a0742983da8a64011ca8b`

The generated files are committed directly to `history/states`, so the game no
longer depends on runtime state-transfer effects.

See `docs/STATIC_MAP.md` for the generator details.
