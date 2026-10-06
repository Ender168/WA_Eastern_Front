# Competitive setup systems v0.23 — static clean map and regional supply mesh

## Why v0.16 did not visibly change the country-selection map

The v0.16 ownership changes were applied from the bookmark effect. That is too
late for the scenario-selection map and some startup systems. WAEF now bakes
the final ownership directly into all generated state histories.

## Static final theatre

- WEF: 141 states.
- EEF: 141 states.
- OBS: 825 states.
- States 16, 28 and 29 are WEF.
- Norway, Greece, southern/island Italy and most of France are OBS.
- The eastern playable theatre ends at the Urals; Siberia, the Far East and
  the removed Central Asian extension are OBS.

## State-history whitelist

Every one of the 1107 state files is reconstructed from a minimal whitelist:
- state id and name;
- provinces;
- victory points;
- final owner/controller/core;
- normalized population;
- state category;
- the new minimal buildings block;
- designated capital resources only.

This deliberately removes all inherited:
- dynamic state modifiers;
- dated state effects;
- forts and stronghold networks;
- naval bases and dockyards;
- air bases;
- anti-air;
- refineries and silos;
- special/landmark buildings;
- extra building-slot effects;
- claims and historical state-side scripts;
- resource blocks outside the designated capitals.

## Construction baseline

- every state category: city (15 shared slots);
- infrastructure: 7 everywhere;
- WEF/EEF: exactly 2 civilian factories + 5 military factories per state;
- OBS: no civilian or military factories from WAEF state history;
- WEF/EEF population: 725,000 per state = 102,225,000 per player.

## Resources

Only Berlin (810) and Moscow (219) carry scenario resources:
- oil 10;
- rubber 10;
- tungsten 10;
- chromium 10;
- coal 10;
- bauxite 10;
- steel 10.

Iron and aluminium are absent, and every other state has no resource block.

## Supply and railways

- exactly one supply hub is generated for every WEF/EEF state;
- hub position is the state's first victory-point province, falling back to the
  first province only when the state has no VP;
- province adjacency is derived from World Ablaze's pinned provinces.bmp;
- every pair of adjacent playable states gets an end-to-end level-3 railway
  route between their two regional supply hubs;
- routes are calculated through adjacent land provinces;
- shared trunks are deduplicated into unique railway segments, so multiple
  hub-to-hub routes can share the same physical track without duplicate edges.

## Technology assimilation

All seven WA technology schools remain available. The original WA national
technology flags and dated technology grants are preserved. WAEF does not add
WA's `foreign_technologies` idea at all, so its -10% Major Technologies
research-speed penalty never applies to WEF/EEF.


## v0.18 — Eastern edge cleanup and heavier starting industry

The detached EEF states 742, 732, 40 and 654 are removed from the playable
theatre. They are replaced by 1027, 407, 1015, 1014 and 406, producing a more
continuous eastern/rear boundary.

Final ownership after this pass:
- WEF: 141 states;
- EEF: 142 states;
- OBS: 824 states.

Playable-state industry is increased to:
- 2 civilian factories;
- 5 military factories.

The regional supply generator is rerun after ownership changes. Every newly
added EEF state receives its own supply hub and is included in the automatic
level-3 rail mesh between adjacent playable states.

Technology baseline is intentionally not bundled into this map/industry pass.
The planned implementation is a separate one-time 1940 baseline decision
unlocked only after a technology school is assimilated. That keeps national
tree selection and bulk tech granting independently testable.


## v0.19 — exact state symmetry, 1940 baseline and national Grand Strategy

State 583 is removed from EEF and assigned to OBS. The playable state count is
again exactly 141 WEF / 141 EEF / 825 OBS. Supply hubs and railways are
regenerated after the removal.

Each technology Assimilate now also assigns the matching World Ablaze Grand
Strategy doctrine:
- France: noria_tactics;
- Italy: rapid_decision;
- Japan: bushido;
- Germany: auftragstaktik;
- Soviet Union: deep_battle;
- Britain: british_professionalism;
- United States: overwhelming_firepower.

After Assimilate, a separate one-time zero-cost decision applies the 1940
technology baseline. The baseline is generated from the pinned World Ablaze
technology definitions rather than maintained by hand.

Generation rules:
- start_year <= 1940;
- shared Industry/Electronics/Support technologies;
- only the selected national air/armor/artillery/infantry/naval files;
- doctrine technologies excluded;
- dependencies and sub-technologies included recursively only within the 1940 cutoff;
- DLC-gated alternatives inherit their DLC conditions through the whole technology chain;
- standard_industry is the neutral common industry philosophy;
- concentrated_industry and dispersed_industry are not granted.


## v0.20 — eastern cleanup, ideology choice and tank MIO fallback

Five detached/remote EEF states are removed from the playable theatre:

- 655 North Sakhalin;
- 657 Birobidzhan;
- 854 North Kamchatka;
- 953 Chukotka;
- 963 Pärnu.

They are replaced by:

- 146 Viipurin Karjala;
- 419 Tibriz;
- 420 Gilan;
- 1044 Raja Karjala;
- 1045 Terijoki.

The exchange is exactly five-for-five, so ownership remains 141 WEF / 141 EEF /
825 OBS. The clean-map generator rebuilds every state history, every playable
supply hub and the complete deduplicated level-3 railway mesh after the change.

WEF and EEF also receive a one-time political setup category. Each player may
choose exactly one of democracy, fascism or communism. The selected ideology is
set to 100% popularity, becomes the ruling party, elections remain disabled for
scenario stability, and all three choices disappear after the selection.

World Ablaze already contains a complete `generic_tank_organization` archetype,
but deliberately marks the archetype itself as unavailable. WAEF now exposes
one scenario-specific tank MIO for WEF and EEF by including that existing WA
archetype instead of cloning a national German/Soviet organization.


## v0.21 — post-1940 force package

After `waef_apply_1940_technology_baseline` is completed, each player receives
one additional zero-cost, one-time decision: `waef_create_starting_forces`.

The decision creates templates in this order:

1. `WAEF Suppression`
   - 25 cavalry battalions, filling the full 5x5 regiment grid;
   - military police as the only divisional support company;
   - priority 0 and created first so it is the first occupation-garrison
     candidate for the otherwise template-empty WEF/EEF tags.

2. `WAEF Infantry Division`
   - 9 heavy infantry battalions in three 3-battalion regiments;
   - 3 artillery brigades;
   - 3 anti-tank brigades;
   - each heavy-infantry regiment receives regimental artillery and
     regimental anti-tank;
   - non-motorized engineer, logistics, maintenance, field hospital, signal,
     recon, artillery, anti-air and military-police support.

3. `WAEF Medium Tank Division`
   - medium armor regiments sized 4 / 3 / 3, for 10 medium-tank battalions;
   - 4 mechanized battalions;
   - the mechanized regiment receives motorized regimental artillery and
     motorized regimental anti-tank;
   - motorized engineer, logistics, maintenance, field hospital, signal,
     recon, artillery, anti-air and military-police support.

The decision then creates, for the country taking it:

- 300 infantry divisions;
- 30 medium tank divisions;
- all with start experience factor 0.45 (World Ablaze Regular), full equipment and full manpower;
- WEF deployment prioritized to Berlin province 6521 in state 810;
- EEF deployment prioritized to Moscow province 6380 in state 219;
- 50 generic corps commanders at skill 1 with all four land skills at 1;
- 5 generic field marshals at skill 1 with all four land skills at 1.

The decision is gated by `waef_1940_technology_baseline_applied` and is removed
permanently after setting `waef_starting_forces_created`.

HOI4 exposes no country effect for directly assigning a specific division
template as the occupation-garrison template. WAEF therefore creates the
Suppression template first and gives it the lowest template priority. This
part requires an in-game validation pass; the template itself is deterministic,
while the occupation UI's automatic initial selection is engine-controlled.


## v0.22 — doctrine setup

Both WEF and EEF start with 100 Army Experience and 100 Air Experience.

### Air baseline

Air doctrine is deliberately symmetrical at scenario start:

- grand doctrine: `air_operations`;
- Great War fighter: `dogfighting`, 200 Mastery;
- Great War strike: `target_acquisition`, 200 Mastery;
- Great War naval aviation: `search_patterns`, 200 Mastery;
- Great War bomber: `bomber_formations`, 200 Mastery.

This completes the common Great War air layer and leaves the first meaningful
air-doctrine choice to Tier 1.

### Optional land mastery decisions

The `waef_land_doctrine_setup` category is an optional startup accelerator.
The player must first select a subdoctrine in the relevant track.

- Great War / Tier 0: Artillery, Armour and Infantry each receive 200 Mastery.
- Tier 1 decisions appear after all three Great War grants are taken and give
  200 Mastery to Artillery, Armour and Infantry.
- Tier 2 decisions appear after all three Tier 1 grants are taken and give
  100 Mastery to Artillery, Armour and Infantry.
- Operations tracks are intentionally excluded. Despite their internal
  `tier_1_operations` / `tier_2_operations` names, World Ablaze gates them
  behind completed Tier 3 Armour or Infantry tracks.

### Optional air mastery decisions

The `waef_air_doctrine_setup` category grants 200 Mastery to the selected
Tier 1 Fighter, Strike, Naval Aviation and Bomber tracks. Great War air tracks
are not represented here because they are already selected and mastered in
country history.

### Doctrine cost window

At scenario start both players receive `waef_initial_doctrine_window`:

- Land Doctrine cost: -100%;
- Air Doctrine cost: -100%;
- Naval Doctrine cost: +1000%.

On 30 January 1941 the country-specific daily on-action swaps this idea to
`waef_naval_doctrine_lock`, removing the Land/Air discounts while preserving
the +1000% Naval Doctrine cost modifier.

## v0.23 - scenario economy baseline

### Starting country package

Both WEF and EEF now start with:

- 800 political power;
- 7,000 regular trains (`train_equipment_1`);
- the permanent `waef_reduced_fuel_capacity` spirit, reducing national fuel
  storage capacity by 75%.

When `waef_create_starting_forces` is taken, each side additionally receives:

- 1,000 armored trains (`train_equipment_4`);
- 1,000 trucks (`motorized_equipment_1`);
- `waef_manpower_accounting` for exactly 700 days / 100 weeks.

The manpower spirit removes 57,400 manpower per week. Over its full lifetime
this repays 5,740,000 manpower to the scenario's bookkeeping. A triggered event
explains the intentionally artificial mechanism to the player.

### Symmetric state package

At scenario startup every state controlled by WEF or EEF receives the same
resource package:

- oil 2;
- bauxite 11;
- rubber 3;
- tungsten 2;
- chromium 3;
- coal 35;
- iron 25.

The old capital-only resource placeholder was removed from Berlin and Moscow
and from the static-state generator, so these values are final rather than
additive on top of the former 10-resource test block.

Each controlled player state is also set to:

- 1 fuel silo;
- 15 hydro steel refineries;
- 5 hydro aluminium refineries.

No extra shared building slots are granted. The setup therefore does not
quietly create additional factory construction capacity as a side effect.

### Naval restriction

Both `waef_initial_doctrine_window` and its post-30-January replacement
`waef_naval_doctrine_lock` now apply:

- Naval Doctrine cost: +1000%;
- Dockyard construction speed: -1000%.

The initial version still temporarily gives the existing -100% Land and Air
Doctrine costs through 29 January 1941.
