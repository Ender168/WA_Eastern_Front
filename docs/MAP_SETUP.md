# Map setup v0.2

The project does **not** copy the World Ablaze map.

The custom January 1941 bookmark calls `waef_initialize_map`, which reassigns
ownership while keeping World Ablaze state definitions, province boundaries,
terrain, resources, railways, supply hubs, air regions and strategic regions intact.

## Initial sides

### Germany

States owned by the base World Ablaze setup as GER, AUS, CZE, HUN, YUG, BUL,
ROM or POL are assigned to Germany, subject to the eastern-border overrides.

### Soviet Union

States owned by SOV, LIT, LAT or EST are assigned to the Soviet Union.

Additional Soviet states:

- Eastern Poland: 96, 95, 1058, 97, 94, 93, 91, 89, 1059
- Vilnius / Druskininkai: 784, 1065
- Romanian concessions of 1940: 80, 78, 766

German override:

- 188 Memel

These Polish IDs follow World Ablaze's own Molotov-Ribbentrop implementation.

## Neutral world

A dedicated static country tag, `OBS`, is used as the world-holder.

At scenario initialization:

1. OBS is guaranteed to exist by giving it a core on Kanto (state 282) and
   releasing it before the world transfer.
2. Every state outside the GER and SOV blocs is transferred to OBS.
3. Every other country is annexed into OBS with `transfer_troops = no`.
4. OBS civilian factories, military factories and dockyards are set to zero.
5. OBS receives cores on its world-holder territory.

The observer is intentionally not a third active strategic participant.

## Player cores

All scenario-start GER and SOV territories become cores of the corresponding
player. This avoids occupation mechanics being inherited accidentally from the
countries consolidated into each side.

## Why ownership is scripted

Copying `history/states` would freeze the submod to one World Ablaze map
snapshot. Scripted ownership allows terrain, supply, resource and map changes
from later World Ablaze versions to flow through automatically.

Explicit state IDs remain maintenance-sensitive and must be rechecked if World
Ablaze changes state boundaries or numbering.

## Runtime validation still pending

- OBS release and world consolidation;
- initial border from Baltic to Black Sea;
- Memel, Vilnius, eastern Poland, Bessarabia and Bucovina;
- railways and supply hubs after ownership transfer;
- removal of unwanted diplomacy/factions after country consolidation;
- absence of unwanted observer AI behaviour.
