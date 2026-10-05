# Competitive setup systems v0.15 — full static map retest

## Confirmed working baseline

The WAEF tags now load before World Ablaze's `dynamic_tags = yes` boundary.

Confirmed in-game:
- the WAEF country-selection screen opens;
- WEF and EEF are both selectable;
- WEF can own East Berlin (810);
- EEF can own Moscow (219);
- singleplayer launches successfully at 1941.1.1.12.

## Full-map retest

Restore the previously generated complete scenario state map from the last
known 182 / 182 / 743 static-map revision, but keep the corrected static-tag
ordering and the now-working WEF/EEF bookmark.

Ownership:
- WEF: 182 states;
- EEF: 182 states;
- OBS: 743 states.

This deliberately reuses the previous state-map snapshot rather than
regenerating it, so the test isolates the effect of the country-tag fix.

## What remains intentionally unchanged

- start date remains 1941.1.1.12;
- WEF and EEF remain the only bookmark countries;
- World Ablaze country histories and OOBs are still active for this validation;
- World Ablaze decision content is still active, so unrelated decisions may
  appear during this stage.

## Success criterion

If the country-selection screen and game start remain stable with all 1107
states assigned to WEF / EEF / OBS, the former full-map CTD was caused by the
late dynamic-tag registration rather than the state-map architecture.

After that, the next cleanup layer is to remove irrelevant historical
country/OOB/decision runtime content and then restore only WAEF systems.
