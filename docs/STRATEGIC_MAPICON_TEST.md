# Strategic state mapicon: first in-game test

Branch: `test/strategic-state-mapicon`.
Baseline: `a6ddd79b4ae18417f8c7a1053f6719989e86a386`.

This build adds one passive scripted GUI marker anchored to Warsaw's state
(10), using `context_type = state_mapicon`. It reuses World Ablaze's
`GFX_victory_points` sprite and displays a gold OBJECTIVE: WARSAW label.
The engine chooses the state anchor; exact placement over province 3544
is not promised. Both WEF and EEF should see the same marker.

There are no new textures, entities, history effects, map highlights or GUI
click effects. VP values, surrender rules and the 40-city victory system
are unchanged. Tooltips, colour changes and a visibility toggle are deferred
until this basic marker has been tested in the game.

## Install

Download this branch's ZIP and use its contents in your existing local mod
installation. Replace the previous mod contents rather than overlaying an
older experimental build, so removed marker files cannot remain active.
Keep World Ablaze (9.6) enabled. Enable only one WA Eastern Front copy.
The mod name and descriptor are unchanged in this test branch.

## In-game checks

1. Start a new 1941 scenario as WEF. Close the decisions and state panels.
2. Find Warsaw. Look for the enlarged VP symbol and gold OBJECTIVE: WARSAW
   label above the state anchor. No decision needs to be activated.
3. Zoom in/out and pan. Check whether the marker follows the map and whether
   the label remains readable at a useful campaign zoom level.
4. Click the terrain under the label and check that normal map input works.
5. Let three days pass, save, return to the menu and load that save.
6. Repeat the visibility check as EEF. Record any differences between sides.

Please report separately: whether loading succeeds, whether the marker is
visible, its position/zoom behaviour, and whether saving/loading succeeds.
A screenshot of Warsaw is useful even when the game launches normally.
If it crashes, keep the new error.log and the latest crash folder, especially
exception.txt and meta.yml where present.

Static validation cannot establish rendering, hit testing or runtime safety.
The marker must pass these checks before expanding to all 39 objective states.
