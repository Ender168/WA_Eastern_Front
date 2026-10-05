# Competitive setup systems v0.12 — WEF ownership isolation

## Confirmed controls

- Native World Ablaze history/frontend works.
- The World Ablaze bookmark copied unchanged except for a 1941.1.1.12 start date
  successfully launches a single-player game.
- Therefore the 1941 date itself is valid.

## Current diagnostic

Keep the working 1941 World Ablaze bookmark exactly as in v0.11:
- default country remains GER;
- normal World Ablaze country list remains;
- normal World Ablaze country and unit histories remain.

Change only one state:
- state 810 (East Berlin) owner/core GER -> WEF.

No EEF state is changed.
WEF is not selected by the bookmark.
No global state replacement is used.

## Interpretation

If this build launches, a state can safely be transferred to WEF and the next
test should activate WEF as the bookmark/default country.

If this build fails in the frontend, merely giving an existing state to the WEF
custom tag is sufficient to reproduce the failure, so the problem is in custom
country/state integration rather than the bookmark date.
