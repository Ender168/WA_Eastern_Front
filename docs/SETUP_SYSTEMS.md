# Competitive setup systems v0.7

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

WAEF once again replaces `common/bookmarks`, but unlike the earlier failing
configuration it now keeps World Ablaze country histories loaded for compatibility.

The only visible bookmark is `common/bookmarks/waef_1941.txt`:

- 1 January 1941 at 12:00;
- WEF as the default country;
- `default = yes`;
- WEF and EEF as the two displayed player countries;
- weather randomization plus the `waef_scenario_1941` global flag.

This combines the two successful diagnostic findings:

1. replacing the entire World Ablaze country-history database with only
   WEF/EEF/OBS prevents stable frontend startup;
2. leaving the World Ablaze 1936 bookmark active points the frontend at GER and
   other historical countries which own no states on the WAEF static map.

The current test therefore preserves upstream country histories but exposes only
the WAEF 1941 scenario.

## Country-history compatibility layer

WAEF does **not** replace `history/countries`.

World Ablaze country histories load alongside the WAEF-owned WEF/EEF/OBS
histories. Historical countries may therefore retain politics, characters,
ideas and other compatibility data while owning no states.

This remains a temporary compatibility layer. Once startup is stable, it can be
reduced to the minimum upstream country-history data required by World Ablaze
scripts and hardcoded frontend/runtime references.

Historical armies remain suppressed because WAEF still replaces
`history/units`.

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

## Known compatibility warning

With Gotterdammerung active, World Ablaze's Belgium country history currently
attempts to recruit several old pre-Gotterdammerung characters that its own
character definitions disable when the DLC is present. These produce
`Unknown character BEL_*` errors during history execution.

The engine survives these errors and reaches frontend startup afterwards, so they
are not treated as the current CTD cause. They will be cleaned up later if they
remain relevant to the final compatibility layer.

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
