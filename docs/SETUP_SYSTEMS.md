# Competitive setup systems v0.10 — two-state WAEF bootstrap

## Purpose

The full upstream-history control build launches successfully. This proves that
World Ablaze plus WAEF's remaining common content can reach and remain in the
frontend.

This diagnostic build restores the WAEF scenario in the smallest useful form.

## Bookmark

WAEF again replaces `common/bookmarks` and exposes only the 1 January 1941
bookmark with WEF as the default country and EEF as the second player country.

## State history

WAEF does **not** replace `history/states`.

Only two state files are overridden by matching World Ablaze paths:

- state 810 (East Berlin): owner/core changed from GER to WEF;
- state 219 (Moscow): owner/core changed from SOV to EEF.

Every other state is loaded unchanged from World Ablaze.

No manpower, building, resource or victory-point normalization is applied.
No OBS ownership is applied.

## Country and unit history

WAEF does not replace `history/countries` or `history/units`.

World Ablaze's normal country histories and OOB therefore remain active, while
the existing WEF/EEF/OBS history files are added alongside them.

## Diagnostic interpretation

If this build remains stable, custom WEF/EEF tags, the WAEF 1941 bookmark and
basic custom state ownership are valid. The crash in the full map build must
then come from scaling or from one of the transformations performed across the
1,107 generated state files.

If this build crashes, the failure is already reproducible with only two custom
state owners, greatly narrowing the remaining compatibility problem.
