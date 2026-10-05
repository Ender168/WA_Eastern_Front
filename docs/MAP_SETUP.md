# Map setup v0.1

The project does **not** copy the World Ablaze map.

Instead, the custom January 1941 bookmark calls `waef_initialize_map`, which
reassigns ownership while keeping all World Ablaze state definitions, province
boundaries, terrain, resources, railways, supply hubs, air regions and strategic
regions intact.

## Initial sides

### Germany

States owned at the base World Ablaze start by:

- GER
- AUS
- CZE
- HUN
- YUG
- BUL
- ROM
- POL

are marked for Germany, subject to the eastern-border overrides below.

### Soviet Union

States owned at the base World Ablaze start by:

- SOV
- LIT
- LAT
- EST

are marked for the Soviet Union.

Additional Soviet states:

- Eastern Poland: 96, 95, 1058, 97, 94, 93, 91, 89, 1059
- Vilnius / Druskininkai: 784, 1065
- Romanian concessions of 1940: 80, 78, 766

### German override

- 188 Memel is reassigned to Germany.

## Neutral world

All states not marked for Germany or the Soviet Union are transferred to SWE.

SWE is only a temporary observer/world-holder solution inherited from the old
1v1 concept. It can be replaced by a dedicated observer tag later if World
Ablaze systems make Sweden's normal country content undesirable.

## Why ownership is scripted

Copying `history/states` would make the submod brittle against World Ablaze
map updates. Scripted ownership lets the project inherit future World Ablaze map
changes automatically, except where World Ablaze changes one of the explicitly
referenced border state IDs.

## Next validation

1. Launch only World Ablaze + WA Eastern Front.
2. Select the January 1941 bookmark.
3. Confirm only GER and SOV are intended playable sides.
4. Inspect the GER-SOV border from the Baltic to the Black Sea.
5. Check that railways, supply hubs and resources remain intact.
6. Check Memel, Vilnius, eastern Poland, Bessarabia and Bucovina manually.
7. Check whether landless former countries or SWE's normal World Ablaze content
   produce unwanted events/effects.
