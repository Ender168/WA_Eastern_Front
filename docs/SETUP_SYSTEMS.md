# Competitive setup systems v0.8

## Runtime bootstrap status

The current build is intentionally reduced to a minimal runtime baseline while
the 1941 scenario is validated in-game.

The WAEF-owned country histories for WEF/EEF contain only:

- capital;
- 5 research slots;
- 75% stability;
- 50% war support;
- 200 political power;
- neutrality at 100%;
- one neutral generic country leader;
- the `waef_player_country` flag.

Economic Fatigue, laws, starting technologies, stockpiles, convoys and scripted
industry reset effects remain temporarily disabled.

## Bookmark bootstrap

WAEF replaces `common/bookmarks`.

The only visible bookmark is `common/bookmarks/waef_1941.txt`:

- 1 January 1941 at 12:00;
- WEF as the default country;
- `default = yes`;
- WEF and EEF as the two displayed player countries;
- weather randomization plus the `waef_scenario_1941` global flag.

The latest log reached `frontend.cpp: Startup time` successfully on 1941, so
bookmark parsing and frontend bootstrap are no longer treated as the failing
layer.

## Country-history compatibility stubs

WAEF again replaces `history/countries`, but no longer leaves the original
World Ablaze tags without history entries.

For every World Ablaze country-history filename from the pinned upstream
baseline, WAEF ships a minimal compatibility stub using the same filename.
The stubs contain only neutral politics, 100% neutrality, stability and war
support. They deliberately contain no:

- capitals;
- OOB references;
- factions;
- characters;
- ideas;
- technologies;
- equipment variants;
- missions;
- dated historical effects.

WEF, EEF and OBS keep their own WAEF histories.

This isolates two requirements discovered during startup testing:

1. removing almost the entire country-history database breaks startup;
2. restoring the full historical database causes World Ablaze to execute
   five years of historical country setup over a map owned exclusively by
   WEF/EEF/OBS.

The compatibility-stub layer preserves the database shape without replaying the
historical scenario.

## Player countries

The scenario uses custom tags `WEF` and `EEF`.

Both currently use neutrality and have no advisors, generals, field marshals or
other recruited characters beyond temporary country leaders.

## Geography baseline

Both players own exactly **182 states**.

State-level balancing:

- 550,000 manpower per state;
- infrastructure 7;
- air base 5;
- existing naval bases 5;
- existing VPs 10.

All original state resources are removed.

WEF capital state 810 and EEF capital state 219 each receive 10 oil, rubber,
tungsten, chromium, coal, bauxite and iron. Steel and aluminium remain zero.

## State and unit history

WAEF replaces `history/states` and `history/units`.

The static map therefore remains WEF/EEF/OBS-only and historical World Ablaze
OOB files are not loaded.

Starting armies will be implemented separately after the minimal scenario loads
cleanly.

## Known upstream warnings

The recurring refinery entity, `mapobject_14`, river and assorted graphical
warnings are still treated as upstream/environmental warnings because they occur
across multiple diagnostic configurations and do not stop frontend startup.

The previous Belgium/Gotterdammerung `Unknown character BEL_*` warnings should
disappear in this build because the historical Belgium setup is no longer
executed.

## Focus tree

WEF, EEF and OBS use `waef_empty_focus_tree`.

## Technology selection

The intended design is for WEF and EEF to begin with generic/minor World Ablaze
technology access and later choose a German or Soviet national technology
package through an adapted version of World Ablaze's existing adoption system.

Starting technologies remain temporarily absent during runtime isolation.

## Industry setup

The intended design keeps the Forward Industry / Deep Industry setup choice.
The scripted reset and deployment effects remain disabled until startup is
stable.
