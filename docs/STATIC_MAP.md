# Static map architecture

## Player countries

The scenario uses three custom tags:

- `WEF` - Western Side;
- `EEF` - Eastern Side;
- `OBS` - neutral world holder.

WEF and EEF do not use GER or SOV and currently have no scripted ruler,
advisors or recruited characters.

## State source

The map contains the complete 1107-state World Ablaze state set.

The initial static state set was derived from the user-provided `states.rar`
and World Ablaze commit:

`691c7085f3ec1333ac2a0742983da8a64011ca8b`

Further balance passes regenerate from the committed static map in `main`, so
ownership and map normalization do not depend on live upstream World Ablaze data.

## Ownership transformation

All historical political ownership data is stripped:

- owner;
- controller;
- add_core_of / remove_core_of;
- add_claim_by / remove_claim_by.

Each state receives exactly one scenario owner, controller and core.

### Base WEF

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

### EEF

Original owner in:

- SOV
- LIT
- LAT
- EST

Additional EEF overrides:

- 96, 95, 1058, 97, 94, 93, 91, 89, 1059;
- 784, 1065;
- 80, 78, 766.

### WEF expansion

76 former OBS states are reassigned to WEF to equalize the number of states.

The expansion covers:

- metropolitan France;
- Belgium;
- Netherlands;
- Luxembourg;
- Switzerland;
- Denmark;
- Italy;
- Norway;
- Greece.

### Final totals

- WEF: **182 states**
- EEF: **182 states**
- OBS: **743 states**
- Total: **1107 states**

## State normalization

Every state is normalized to:

- manpower = **550000**;
- infrastructure = **7**;
- air_base = **5**;
- every existing naval_base = **5**;
- every existing VP value = **10**.

Ports are not created in landlocked states. Existing ports are normalized.

States without an existing VP do not receive an artificial new VP; every
existing VP is set to 10.

## Resources

Every original `resources = { ... }` block is removed.

WEF capital state 810 and EEF capital state 219 each receive:

- oil = 10
- rubber = 10
- tungsten = 10
- chromium = 10
- coal = 10
- bauxite = 10
- iron = 10

Steel and aluminium are intentionally absent and therefore remain at 0.

OBS receives no state resources.

## Replace paths

The scenario replaces:

- `common/bookmarks`;
- `history/states`;
- `history/countries`;
- `history/units`.
