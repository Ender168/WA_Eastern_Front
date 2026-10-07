# WA Eastern Front

Competitive two-player Eastern Front scenario built on **World Ablaze (9.6)**.

## Scenario baseline

- start date: **1 January 1941**;
- World Ablaze remains the mechanical and geographical base;
- playable countries:
  - `WEF` - Western Side;
  - `EEF` - Eastern Side;
- `OBS` owns the rest of the world;
- WEF and EEF have no inherited GER/SOV rulers, advisors or OOBs;
- all 1107 states are statically assigned to WEF, EEF or OBS;
- OBS is a passive map holder excluded from the scenario economy and Expert AI initialization;
- normal focus-tree progression is disabled;
- both players can choose one World Ablaze national technology school;
- after the school choice, a separate one-time decision applies the 1940 technology baseline;
- both players can make one permanent ideology choice: democratic, fascist or communist;
- WEF and EEF have access to a shared generic tank MIO based on World Ablaze's own generic tank archetype;
- both sides start with a shared Great War air-doctrine baseline, 100 Army XP and 100 Air XP, plus optional startup doctrine mastery decisions and a temporary Land/Air doctrine cost waiver through 29 January 1941;
- after the 1940 baseline, a one-time force setup decision creates suppression, infantry and medium-tank templates, 300 regular infantry divisions, 30 regular tank divisions, 50 distinctly named generals and 5 field marshals per player.

## Static map

Ownership totals:

- WEF: **141 states**
- EEF: **141 states**
- OBS: **825 states**
- Total: **1107 states**

The playable theatre is deliberately compact. Detached and remote states are
removed from WEF/EEF and replaced by geographically more useful rear/border
states while preserving exact state-count symmetry.

## State normalization

Every state has:

- infrastructure: **7**;
- state category: **city**.

Player states additionally have:

- manpower: **725,000**;
- **2 civilian factories**;
- **5 military factories**.

OBS states use **550,000** manpower and receive no WAEF civilian or military
factories.

Inherited forts, air bases, naval bases, dockyards, anti-air, refineries,
special buildings and state modifiers are removed by the clean-map generator.

## Resources

Only the player-capital states receive resources:

- WEF capital state 810;
- EEF capital state 219.

Each capital receives **10** of:

- oil;
- rubber;
- tungsten;
- chromium;
- coal;
- bauxite;
- steel.

Iron and aluminium are absent.

## Supply

- one generated supply hub per WEF/EEF state;
- hubs use the first VP province where possible;
- adjacent playable states are connected by generated level-3 railways;
- railway routing uses the pinned World Ablaze province bitmap and impassable adjacency overrides;
- two level-1 supply ports in Murmanskaya and Yuzhny connect the retained EEF island;
- both starting-force packages include 50 logistics convoys;
- shared railway segments are deduplicated.

## Replace paths

WAEF replaces:

- `common/bookmarks`;
- `history/states`;
- `history/countries`;
- `history/units`.

## Technology

Seven World Ablaze technology schools are available:

- France;
- Italy;
- Japan;
- Germany;
- Soviet Union;
- Britain;
- United States.

Each school also assigns its matching World Ablaze Grand Strategy doctrine.
The 1940 baseline is generated from the pinned World Ablaze technology files
with a 1940 cutoff and dependency closure.

## Next systems

1. Starting armies, templates and equipment pools.
2. Fixed war-start rules and preparation period.
3. Industrial balancing.
4. Strategic scoring and defensive-depth mechanics.
5. Runtime balance testing of technology schools and MIO progression.

## Dependency

World Ablaze Workshop ID: `2149567872`

## Crash-safety and regeneration

Daily fuel synchronization chooses the economic-law branch before testing the
current spirit. Repeated calls preserve the intended combined -75% capacity
modifier instead of falling through to the full penalty under civilian economy.

Dormant historical decision/category definitions retain IDs referenced by WA
while preventing these decisions from appearing or executing in this scenario.
Pinned WA safety overlays exclude OBS from economic/Expert AI startup and
periodic handlers and guard factory-ratio divisions against zero denominators.

Regenerate from a checkout of WA commit
`691c7085f3ec1333ac2a0742983da8a64011ca8b`:

```bash
python tools/generate_1940_tech_baseline.py --wa-root /path/to/world-ablaze
python tools/generate_wa_compatibility.py /path/to/world-ablaze
python tools/regenerate_clean_scenario.py
python -m unittest discover -s tests -v
```

The French MB.134 and LN.402 upgrade grants are excluded because they require
national equipment-variant history absent from WEF/EEF. The exclusions apply
through recursive dependency/subtechnology traversal. DLC conditions propagate
through both technology links and subtechnologies.

The starting-force decision activates 700 days of manpower accounting:
57,400 available manpower is removed per week (5,740,000 over 100 weeks).
The semiannual mobilization schedule adds 0.5 percentage points of conscription
on each March 1 and September 1 starting in 1941, reaching +5% on
September 1, 1945. The first wave triggers the waef.2 explanation event.
The offensive-momentum (+10% division attack) spirit is defined but not yet
activated; war-preparation decisions remain for a later implementation stage.
No additional prewar ban on declarations of war is imposed by this scenario.
