# Competitive setup systems v0.2

## Player countries

The scenario uses custom tags `WEF` and `EEF`.

Both receive the same baseline:

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

Both currently use neutrality for symmetry.

There are **no rulers, advisors or recruited characters** at this stage.

## Country and unit history

The mod replaces `history/countries` and `history/units`.

Only WEF, EEF and OBS receive scenario country histories. Historical GER/SOV OOB,
production, faction, advisor and national-spirit setup is therefore not inherited.

Starting armies will be implemented separately.

## Focus tree

WEF, EEF and OBS use `waef_empty_focus_tree`.

## Technology selection

Because WEF and EEF are new tags, World Ablaze naturally treats them as
generic/minor technology countries. The old custom `technology_tags` override
has been deleted.

The scenario still adapts World Ablaze's existing
`_unique_technologies_adoption.txt` so WEF and EEF can choose a national
technology package without needing the donor country to exist as their faction
partner.

World Ablaze's original package effects and date-based technology backfill are
retained.

## Industry normalization

At scenario start ordinary CIV, MIL and dockyards on WEF/EEF territory are reset.
Resources, infrastructure, railways, supply, refineries and other World Ablaze
state systems are preserved.

Both players receive 30 CIV.

### Forward Industry

60 MIL per player.

WEF states:
10, 92, 90, 88, 87, 86, 98, 85, 5, 798

EEF states:
96, 95, 1058, 97, 94, 93, 91, 89, 1059, 206

### Deep Industry

50 MIL per player.

WEF states:
55, 54, 52, 50, 801, 57, 51, 803, 152, 882

EEF states:
219, 252, 249, 239, 255, 257, 400, 398, 403, 571

These are competitive balance constants rather than historical factory totals.

## Observer

OBS owns 819 states.

At bookmark start its ordinary CIV, MIL and dockyards are cleared so it remains a
map holder rather than a third economy.
