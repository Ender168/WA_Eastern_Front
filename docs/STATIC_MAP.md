# Static map architecture

## Player countries

The scenario uses three custom tags:

- `WEF` - Western Side;
- `EEF` - Eastern Side;
- `OBS` - neutral world holder.

WEF and EEF deliberately do **not** use GER or SOV. They have no scripted ruler
and no recruited advisors/characters at this stage.

## State source

The user-provided `states.rar` contains the full 1107-state World Ablaze state
set. The generated static map preserves each state's geography, manpower,
buildings, infrastructure, resources, victory points and other non-political
content.

The generator is pinned to World Ablaze commit:

`691c7085f3ec1333ac2a0742983da8a64011ca8b`

The archive and the pinned WA state files match in sampled content; line endings
differ (CRLF vs LF).

## Ownership transformation

All existing state-history political ownership data is stripped:

- owner
- controller
- add_core_of / remove_core_of
- add_claim_by / remove_claim_by

This includes dated historical transfers, so 1938-1940 history cannot hand states
back to GER, SOV, POL, LIT, ROM, etc. when the 1941 bookmark is loaded.

Every state receives exactly one scenario owner, controller and core.

### WEF

Original owner in:

- GER
- AUS
- CZE
- HUN
- YUG
- BUL
- ROM
- POL

Memel (188) is explicitly WEF.

Eastern-border overrides below take priority.

### EEF

Original owner in:

- SOV
- LIT
- LAT
- EST

Additional EEF overrides:

- 96, 95, 1058, 97, 94, 93, 91, 89, 1059
- 784, 1065
- 80, 78, 766

### OBS

Every other state.

Expected final totals:

- WEF: 106 states
- EEF: 182 states
- OBS: 819 states
- Total: 1107 states

## Replace paths

The scenario replaces:

- `common/bookmarks`
- `history/states`
- `history/countries`
- `history/units`

This prevents World Ablaze country history and OOB files from recreating the
historical nations and armies behind the scenario map.
