# Competitive setup systems v0.6

## Runtime bootstrap status

The current build is intentionally reduced to a minimal runtime baseline while
the 1941 scenario is validated in-game.

The only WAEF-owned country-history setup for WEF/EEF is:

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

## Bookmark bootstrap

World Ablaze keeps its own default bookmarks. WAEF adds a separate
`common/bookmarks/waef_1941.txt` bookmark:

- 1 January 1941 at 12:00;
- WEF as the scenario default country;
- WEF and EEF as the two displayed player countries;
- weather randomization plus the `waef_scenario_1941` global flag;
- no `default = yes` marker.

The latest diagnostic run confirmed that all three bookmark files parse
successfully, including `waef_1941.txt`.

## Country-history compatibility diagnostic

WAEF temporarily does **not** replace `history/countries`.

World Ablaze country histories are allowed to load alongside the WAEF-owned
WEF/EEF/OBS histories. This is an isolation step prompted by a frontend crash
after the 1936 history had already executed successfully.

The purpose is to test whether globally replacing `history/countries` with
only WEF/EEF/OBS leaves the World Ablaze frontend and hardcoded country references
without required country setup.

This is not the intended final architecture. Historical GER/SOV/ENG/etc. setup
may therefore exist as zero-territory compatibility data during this test.
Their armies remain suppressed because WAEF still replaces `history/units`.

If the frontend reaches the menu with this build, country-history replacement is
confirmed as the failing layer and we can replace it later with a controlled
compatibility set rather than deleting the entire upstream database.

## Player countries

The scenario uses custom tags `WEF` and `EEF`.

Both currently use neutrality and have no advisors, generals, field marshals or
other recruited characters beyond the temporary country leaders.

The two temporary rulers are WAEF-owned characters using World Ablaze's generic
European civilian portraits:

- WEF: `portrait_europe_generic_4.dds`;
- EEF: `portrait_europe_generic_5.dds`.

They use `despotism`, have no traits and contain no original-tag or national
conditions.

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

WAEF still replaces `history/states` and `history/units`.

The static map therefore remains WEF/EEF/OBS-only, and no historical World Ablaze
OOB is inherited.

Starting armies will be implemented separately after the minimal scenario loads
cleanly.

## Focus tree

WEF, EEF and OBS use `waef_empty_focus_tree`.

## Technology selection

The intended design is for WEF and EEF to begin with generic/minor World Ablaze
technology access and later choose a national technology package through an
adapted version of World Ablaze's existing adoption system.

Starting technologies are temporarily absent from WAEF country history during
runtime isolation.

## Industry setup

The intended design keeps the Forward Industry / Deep Industry setup choice.
The scripted reset and deployment effects are temporarily not executed from the
bookmark while startup stability is being isolated.
