# Map setup v1.1

The scenario uses a **static 1107-state ownership map**.

## Countries

- `WEF`: Western Side
- `EEF`: Eastern Side
- `OBS`: neutral world holder

GER and SOV are not player countries.

## Ownership

EEF keeps its established 182-state eastern bloc.

WEF has been expanded from 106 to 182 states by transferring exactly 76 former
OBS states. The added territory is grouped geographically rather than selected
at random:

- metropolitan France;
- Benelux;
- Switzerland;
- Denmark;
- Italy;
- Norway;
- Greece.

Final totals:

- WEF: **182**
- EEF: **182**
- OBS: **743**

## Border overrides retained

EEF:

- Eastern Poland: 96, 95, 1058, 97, 94, 93, 91, 89, 1059
- Vilnius / Druskininkai: 784, 1065
- Romanian concessions: 80, 78, 766

WEF:

- Memel: 188

## State-history cleanup

All previous owner/controller/core/claim history is removed, including dated
historical transfers.

Every state receives exactly one owner, controller and core.

## Normalized map values

Every state:

- manpower: 550000;
- infrastructure: 7;
- air base: 5.

Every existing:

- naval base: level 5;
- victory point: value 10.

All map resources are removed except the resource packages in player-capital
states 810 and 219. Each capital gets 10 oil, rubber, tungsten, chromium, coal,
bauxite and iron. Steel and aluminium stay at zero.
