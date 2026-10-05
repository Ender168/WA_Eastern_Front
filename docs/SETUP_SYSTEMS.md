# Competitive setup systems v0.11 — pure World Ablaze 1941 date control

## Purpose

The normal World Ablaze 1936 frontend is stable, while the minimal WAEF build
with only two state ownership changes still exits after frontend startup.

This control isolates the bookmark date from every WAEF map/country change.

## Configuration

- `common/bookmarks` is still replaced so only one bookmark is exposed.
- The bookmark content is copied from World Ablaze's own
  `common/bookmarks/blitzkrieg.txt` at pinned commit
  `691c7085f3ec1333ac2a0742983da8a64011ca8b`.
- The only functional change to that upstream bookmark is:
  `1939.8.14.12 -> 1941.1.1.12`.
- Default country remains GER.
- All listed major/minor countries remain the upstream World Ablaze set.
- The normal World Ablaze weather effect is preserved.
- There are no WAEF state-history overrides.
- There is no `replace_path` for states, countries or units.
- World Ablaze provides all state ownership, country histories and OOBs.

WEF/EEF/OBS definitions remain installed but are not referenced by this
bookmark and own no states in this control.

## Diagnostic interpretation

If this build crashes in the frontend, a direct 1 January 1941 bookmark against
World Ablaze's historical database is sufficient to reproduce the failure.
The WAEF map and custom player tags are then exonerated.

If this build remains stable, the 1941 date itself is valid and the next test
will isolate WEF/EEF activation without changing map ownership.

## Intended final scenario

This is diagnostic only. The final scenario remains a symmetric WEF vs EEF
Eastern Front setup beginning on 1 January 1941.
