# Competitive setup systems v0.9 — upstream history control

## Purpose of this build

This is a diagnostic control build, not the intended final scenario.

The previous WAEF 1941 build with minimal country-history compatibility stubs
still completed history execution and reached `frontend.cpp: Startup time`
before the application exited.

The country stubs also removed the previous Belgium unknown-character errors.
That makes the custom country-history layer an unlikely direct cause.

## Control configuration

For this test WAEF no longer uses any `replace_path` directives.

The local generated state-history files are removed so World Ablaze provides its
native `history/states`.

The 309 World Ablaze country-history compatibility stubs are removed so World
Ablaze provides its native `history/countries`.

World Ablaze `history/units` is also restored.

World Ablaze's normal bookmarks are restored. The WAEF 1941 bookmark is
removed from this control build so the frontend uses only the known-good
World Ablaze bookmark set.

The WEF, EEF and OBS country definitions and their three WAEF-authored history
files remain present. They are not the default countries in the restored World
Ablaze 1936 frontend.

## Diagnostic interpretation

If this build reaches the normal World Ablaze frontend without crashing, the
failure is inside WAEF's history replacement architecture, with the custom
state-history layer the strongest remaining suspect.

If this build still crashes, the history replacement layer is not sufficient to
explain the failure. The next isolation pass should remove WAEF additions under
`common/*` in groups, especially country tags/country definitions, characters,
decisions, scripted effects and focus-tree additions.

## Intended final architecture

The intended scenario remains:

- one WAEF 1941 competitive bookmark;
- WEF and EEF as player countries;
- OBS for the rest of the world;
- a symmetric custom state map;
- no historical World Ablaze OOB;
- later restoration of WAEF technology, industry, Economic Fatigue and OOB
  systems after startup stability is proven.

This control build exists only to locate the crash boundary.
