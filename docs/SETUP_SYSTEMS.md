# Competitive setup systems v0.1

## Country baseline

GER and SOV override their normal World Ablaze country-history files.

Both receive:

- 5 research slots;
- 75% stability;
- 50% war support;
- 200 political power;
- 100 convoys;
- Economic Fatigue at 0;
- Low Economic Mobilisation;
- Limited Exports;
- Limited Conscription;
- 300 trains;
- 2,000 motorized equipment;
- the same generic starting technology baseline.

Historical OOBs, production lines, starting factions and normal GER/SOV national
spirits are deliberately not imported.

A compact historical commander pool is retained separately for each side.

## Focus trees

GER, SOV and OBS are routed to `waef_empty_focus_tree`.

Scenario progression is intended to use decisions and scripted systems rather
than national focus trees.

## Technology selection

World Ablaze normally hard-codes GER and SOV into their own national technology
folders. WAEF needs them to start with generic/minor access.

Therefore:

### `common/technology_tags/00_technology.txt`

This is an upstream compatibility copy. GER/SOV original-tag checks are modified
so their inherent national-tree access is disabled only while
`waef_scenario_1941` is active.

Before adopting a package, the generic/minor folders remain available.

### `common/decisions/_unique_technologies_adoption.txt`

This is also an upstream compatibility copy.

WAEF gates the normal GER/SOV original-tag prohibition behind the scenario flag and allows either player to use
the existing World Ablaze national technology adoption decisions without needing
the donor country to remain an active faction partner.

The original World Ablaze `complete_effect` blocks are preserved, including
their date-based grants of previous technologies.

This deliberately avoids a custom Technology Points system.

## Industry normalization

At scenario initialization all ordinary CIV, MIL and dockyard levels on GER/SOV
territory are cleared. Map resources, infrastructure, railways, supply, refineries
and other World Ablaze strategic systems are preserved.

Each player then receives 30 CIV.

### Fixed civilian locations

GER:
810, 65, 55, 54, 52, 50, 57, 51, 4, 9

SOV:
219, 223, 252, 249, 239, 255, 257, 254, 253, 400

### Forward Industry

60 MIL per player, 6 factories in each of 10 states.

GER:
10, 92, 90, 88, 87, 86, 98, 85, 5, 798

SOV:
96, 95, 1058, 97, 94, 93, 91, 89, 1059, 206

### Deep Industry

50 MIL per player, 5 factories in each of 10 states.

GER:
55, 54, 52, 50, 801, 57, 51, 803, 152, 882

SOV:
219, 252, 249, 239, 255, 257, 400, 398, 403, 571

These numbers are balance constants, not intended as historical industrial counts.

## Maintenance note

After a World Ablaze update, compare upstream versions of:

- `common/technology_tags/00_technology.txt`
- `common/decisions/_unique_technologies_adoption.txt`

Do not blindly recopy map/state files.

## Runtime validation still pending

The implementation has been statically assembled but not launched in Hearts of
Iron IV yet. Parser/runtime assumptions that need checking include the dedicated
OBS release, empty focus tree selection, technology-folder switching and industry
decision execution.
