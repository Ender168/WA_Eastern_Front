# Competitive setup systems v0.13 — static country-tag ordering fix

## Root cause isolated

World Ablaze defines its civil-war/dynamic tag boundary in:

`common/country_tags/zz_dynamic_countries.txt`

with:

`dynamic_tags = yes`

Country tags loaded after that marker are treated as dynamic temporary tags.

The WAEF tags were previously declared in:

`common/country_tags/zz_waef_countries.txt`

Alphabetically, `zz_waef_countries.txt` loads after
`zz_dynamic_countries.txt`. Therefore WEF, EEF and OBS were being registered
as dynamic tags instead of normal static countries.

This explains the diagnostic sequence:
- WAEF common content with no WEF/EEF territory can reach the frontend;
- a pure World Ablaze 1941 bookmark launches successfully;
- giving even one real state (East Berlin, state 810) to WEF causes a crash
  when the country-selection frontend opens.

## Fix

The tag file is now:

`common/country_tags/01_waef_countries.txt`

so WEF/EEF/OBS are declared before World Ablaze's
`zz_dynamic_countries.txt` marker.

## Current diagnostic configuration

- Start date: 1941.1.1.12.
- Bookmark remains the working World Ablaze-style bookmark.
- GER remains the default bookmark country.
- State 810 (East Berlin) is owned/cored by WEF.
- All other states, country histories and OOBs remain World Ablaze.
- No EEF state ownership is active yet.

## Expected result

If the country-selection screen now remains stable, the static/dynamic tag
ordering was the frontend crash cause. The next step is to restore both WEF and
EEF as selectable scenario countries before scaling up territory ownership.
