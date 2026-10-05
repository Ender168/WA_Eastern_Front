# Competitive setup systems v0.3

## Player countries

The scenario uses custom tags `WEF` and `EEF`.

Both receive the same country baseline:

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

Both currently use neutrality.

There are no rulers, advisors or recruited characters.

## Geography baseline

Both players now own exactly **182 states**.

State-level balancing:

- 550,000 manpower per state;
- infrastructure 7;
- air base 5;
- existing naval bases 5;
- existing VPs 10.

All original state resources are removed.

WEF capital state 810 and EEF capital state 219 each receive 10 oil, rubber,
tungsten, chromium, coal, bauxite and iron. Steel and aluminium remain zero.

## Country and unit history

The mod replaces `history/countries` and `history/units`.

Only WEF, EEF and OBS receive scenario country histories. Historical GER/SOV OOB,
production, faction, advisor and national-spirit setup is not inherited.

Starting armies will be implemented separately.

## Focus tree

WEF, EEF and OBS use `waef_empty_focus_tree`.

## Technology selection

WEF and EEF naturally use generic/minor World Ablaze technology access.

The scenario adapts World Ablaze's existing
`_unique_technologies_adoption.txt` so WEF and EEF can choose a national
technology package without a donor faction relationship.

World Ablaze's original package effects and date-based technology backfill are
retained.

## Industry setup

The separate industry-choice system still resets ordinary CIV/MIL/dockyard
levels on WEF/EEF territory at scenario start.

Both players receive 30 CIV and then choose:

### Forward Industry

60 MIL per player.

### Deep Industry

50 MIL per player.

These values remain provisional competitive balance constants.
