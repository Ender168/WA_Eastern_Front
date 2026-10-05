#!/usr/bin/env python3
"""Generate minimal WAEF compatibility country histories.

Usage:
    python tools/generate_country_history_stubs.py <world_ablaze_history_countries_dir>

The script mirrors every upstream .txt filename into history/countries while
preserving WEF/EEF/OBS, whose histories are authored by WAEF.
"""

from pathlib import Path
import sys

STUB = """# WAEF compatibility stub.
# Historical World Ablaze country setup is intentionally suppressed.

set_stability = 1
set_war_support = 0

set_politics = {
    ruling_party = neutrality
    last_election = "1936.1.1"
    election_frequency = 48
    elections_allowed = no
}

set_popularities = {
    neutrality = 100
}
"""

PROTECTED = {"WEF", "EEF", "OBS"}

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_country_history_stubs.py <WA history/countries dir>")

    source = Path(sys.argv[1])
    target = Path(__file__).resolve().parents[1] / "history" / "countries"

    if not source.is_dir():
        raise SystemExit(f"not a directory: {source}")

    written = 0
    for src in sorted(source.glob("*.txt")):
        tag = src.name.split(" ", 1)[0]
        if tag in PROTECTED:
            continue
        (target / src.name).write_text(STUB, encoding="utf-8", newline="\n")
        written += 1

    print(f"generated {written} compatibility stubs")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
