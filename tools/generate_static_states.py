#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys
from collections import Counter

WEST_OWNERS = {"GER", "AUS", "CZE", "HUN", "YUG", "BUL", "ROM", "POL"}
EAST_OWNERS = {"SOV", "LIT", "LAT", "EST"}

EAST_OVERRIDES = {96, 95, 1058, 97, 94, 93, 91, 89, 1059, 784, 1065, 80, 78, 766}
WEST_OVERRIDES = {188}

POLITICAL_LINE = re.compile(
    r"^[ \\t]*(owner|controller|add_core_of|remove_core_of|add_claim_by|remove_claim_by)"
    r"\\s*=\\s*[A-Z0-9]{3}[^\\r\\n]*\\r?\\n?",
    re.MULTILINE,
)

def target_for(state_id: int, original_owner: str) -> str:
    if state_id in EAST_OVERRIDES:
        return "EEF"
    if state_id in WEST_OVERRIDES:
        return "WEF"
    if original_owner in EAST_OWNERS:
        return "EEF"
    if original_owner in WEST_OWNERS:
        return "WEF"
    return "OBS"

def transform(text: str, path: Path):
    id_match = re.search(r"^\\s*id\\s*=\\s*(\\d+)", text, re.MULTILINE)
    if not id_match:
        raise RuntimeError(f"Missing state id: {path}")
    state_id = int(id_match.group(1))

    owner_match = re.search(r"^\\s*owner\\s*=\\s*([A-Z0-9]{3})\\s*$", text, re.MULTILINE)
    original_owner = owner_match.group(1) if owner_match else ""
    target = target_for(state_id, original_owner)

    text = POLITICAL_LINE.sub("", text)

    history = re.search(r"history\\s*=\\s*\\{", text)
    if not history:
        raise RuntimeError(f"Missing history block: {path}")

    injection = (
        "history = {\\n"
        f"\\t\\towner = {target}\\n"
        f"\\t\\tcontroller = {target}\\n"
        f"\\t\\tadd_core_of = {target}"
    )
    text = text[:history.start()] + injection + text[history.end():]
    return state_id, target, text

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_static_states.py SOURCE_STATES_DIR DEST_STATES_DIR")

    source = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    files = sorted(source.glob("*.txt"))

    if len(files) != 1107:
        raise RuntimeError(f"Expected 1107 World Ablaze states, found {len(files)}")

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    counts = Counter()
    ids = set()

    for src in files:
        text = src.read_text(encoding="utf-8-sig")
        state_id, target, result = transform(text, src)
        if state_id in ids:
            raise RuntimeError(f"Duplicate state id {state_id}")
        ids.add(state_id)
        counts[target] += 1
        (dest / src.name).write_text(result, encoding="utf-8", newline="\\n")

    if ids != set(range(1, 1108)):
        missing = sorted(set(range(1, 1108)) - ids)
        extra = sorted(ids - set(range(1, 1108)))
        raise RuntimeError(f"Unexpected state IDs. Missing={missing}, extra={extra}")

    expected = {"WEF": 106, "EEF": 182, "OBS": 819}
    if dict(counts) != expected:
        raise RuntimeError(f"Ownership counts changed: got {dict(counts)}, expected {expected}")

    print(f"Generated {len(files)} states: WEF={counts['WEF']} EEF={counts['EEF']} OBS={counts['OBS']}")

if __name__ == "__main__":
    main()
