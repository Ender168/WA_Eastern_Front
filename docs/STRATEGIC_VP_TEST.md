# Strategic VP map test

Branch: `test/strategic-state-mapicon` (retained for the next visual experiment).

All 40 strategic cities from `tools/waef_strategic_cities.json` have 10 VP.
Every other existing VP location, including OBS territory, has 1 VP.
Provinces without a VP entry do not receive a new entry. City positions,
state categories and the supply network are preserved. All categories now have
20 base building slots.
The map generator applies the same rule on regeneration and checks that
every objective has a VP entry in its expected state.

The previous Warsaw scripted GUI marker and its localisation are removed.
This build tests the game's normal VP markers and labels. Their visual
difference at 10 versus 1 VP still needs to be checked in HOI4.
Native VP values also affect gameplay; no surrender modifiers are changed.
The existing strategic capture and collapse missions are preserved.

## Install and check

Replace the previous local mod contents with this branch's ZIP contents,
so deleted GUI files do not survive. Enable World Ablaze (9.6) and only one
copy of WA Eastern Front. Start a new 1941 game.

Compare Warsaw or another non-capital objective with nearby ordinary cities
at the same zoom. Check their VP tooltips (10 versus 1), then run several
days and save/reload. Report visibility separately from successful loading.
