# Competitive setup systems v0.14 — two-country frontend validation

## Confirmed root cause

WAEF country tags must be declared before World Ablaze's
`zz_dynamic_countries.txt` file, which starts with `dynamic_tags = yes`.

After renaming the WAEF tag file to `01_waef_countries.txt`, the frontend
successfully opens with state 810 owned by WEF.

## Current validation target

Restore the actual WAEF scenario-selection shell while keeping map ownership
minimal:

- start date: 1941.1.1.12;
- default/selectable countries: WEF and EEF only;
- WEF owns and cores state 810 (East Berlin);
- EEF owns and cores state 219 (Moscow);
- all other states remain native World Ablaze ownership;
- World Ablaze country histories and OOBs remain available;
- scenario flag `waef_scenario_1941` is restored;
- weather initialization remains enabled.

This validates that both custom countries can coexist as ordinary static tags,
own their capitals and appear together in the country-selection frontend.

## Next step after successful validation

Scale state ownership from the two-capital bootstrap to the intended
WEF / EEF / OBS map, preserving upstream World Ablaze state structure rather
than altering unrelated map data at the same time.
