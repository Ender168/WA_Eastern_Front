# Competitive setup systems v0.4

## Runtime bootstrap status

The current build is intentionally reduced to a minimal runtime baseline while
the 1941 scenario is validated in-game.

The only active country-history setup for WEF/EEF is:

- capital;
- 5 research slots;
- 75% stability;
- 50% war support;
- 200 political power;
- neutrality at 100%;
- one neutral generic country leader;
- the `waef_player_country` flag.

Economic Fatigue, laws, starting technologies, stockpiles, convoys and scripted
industry reset effects are temporarily disabled. They are design requirements,
not active runtime features in this bootstrap build.

## Bookmark

WAEF replaces `common/bookmarks` and exposes a single bookmark:

- 1 January 1941 at 12:00;
- WEF as the default country;
- `default = yes`, matching World Ablaze's primary Gathering Storm bookmark;
- WEF and EEF as the two displayed player countries;
- weather randomization plus the `waef_scenario_1941` global flag.

The explicit default marker is required while WAEF replaces all upstream
bookmarks, otherwise there is no remaining default bookmark definition.

## Player countries

The scenario uses custom tags `WEF` and `EEF`.

Both currently use neutrality and have no advisors, generals, field marshals or
other recruited characters beyond the temporary country leaders.

The two temporary rulers are WAEF-owned characters using World Ablaze's generic
European civilian portraits:

- WEF: `portrait_europe_generic_4.dds`;
- EEF: `portrait_europe_generic_5.dds`.

They use `despotism`, have no traits and contain no original-tag or national
conditions. This avoids inheriting any GER/SOV/minor-country character logic.

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

## Country and unit history

The mod replaces `history/countries` and `history/units`.

Only WEF, EEF and OBS receive scenario country histories. Historical GER/SOV OOB,
production, faction, advisor and national-spirit setup is not inherited.

Starting armies will be implemented separately after the minimal scenario loads
cleanly.

## Focus tree

WEF, EEF and OBS use `waef_empty_focus_tree`.

## Technology selection

The intended design is for WEF and EEF to begin with generic/minor World Ablaze
technology access and later choose a national technology package through an
adapted version of World Ablaze's existing adoption system.

Starting technologies are temporarily absent from country history during runtime
isolation.

## Industry setup

The intended design keeps the Forward Industry / Deep Industry setup choice.
The scripted reset and deployment effects are temporarily not executed from the
bookmark while startup stability is being isolated.
