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

# 76 additional OBS states transferred to WEF to equalize state counts at 182 vs 182.
# Metropolitan France, Benelux, Switzerland, Denmark, Italy, Norway and Greece.
WEST_EXPANSION_IDS = {
    1, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33,
    735, 785, 855, 1016,
    6, 34, 979, 985, 790,
    7, 35, 36,
    8,
    3, 151, 911, 912,
    37, 99, 1051, 957, 871,
    2, 856, 986, 163, 736, 160, 162, 157, 156, 158, 117, 114, 159, 164, 39,
    885, 161, 115, 1032,
    110, 142, 143, 144, 878, 1017, 1018, 1019, 1020, 1023,
    182, 184, 185, 47, 186, 187, 731,
}

# Resource policy: all static map resources are removed.
# WAEF applies the symmetric per-state resource package at runtime from
# common/on_actions/waef_scenario_on_actions.txt, after scenario control is known.

POLITICAL_LINE = re.compile(
    r"^[ \t]*(owner|controller|add_core_of|remove_core_of|add_claim_by|remove_claim_by)"
    r"\s*=\s*[A-Z0-9]{3}[^\r\n]*\r?\n?",
    re.MULTILINE,
)

def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    i = open_index
    while i < len(text):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "#":
                nl = text.find("\n", i)
                if nl == -1:
                    return len(text) - 1
                i = nl
                continue
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise RuntimeError(f"Unmatched brace at index {open_index}")

def remove_named_blocks(text: str, keyword: str) -> str:
    pattern = re.compile(rf"\b{re.escape(keyword)}\s*=\s*\{{")
    while True:
        match = pattern.search(text)
        if not match:
            return text
        open_index = text.find("{", match.start(), match.end())
        close_index = find_matching_brace(text, open_index)
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", close_index)
        if line_end == -1:
            line_end = close_index + 1
        else:
            line_end += 1
        text = text[:line_start] + text[line_end:]

def normalize_victory_points(text: str) -> str:
    pattern = re.compile(r"\bvictory_points\s*=\s*\{")
    pos = 0
    while True:
        match = pattern.search(text, pos)
        if not match:
            return text
        open_index = text.find("{", match.start(), match.end())
        close_index = find_matching_brace(text, open_index)
        body = text[open_index + 1:close_index]
        body = re.sub(r"(\b\d+\b)(\s+)(-?\d+)", lambda m: f"{m.group(1)}{m.group(2)}10", body)
        text = text[:open_index + 1] + body + text[close_index:]
        pos = open_index + 1 + len(body) + 1

def ensure_base_buildings(text: str) -> str:
    history_match = re.search(r"\bhistory\s*=\s*\{", text)
    if not history_match:
        raise RuntimeError("Missing history block")
    history_open = text.find("{", history_match.start(), history_match.end())
    history_close = find_matching_brace(text, history_open)

    region = text[history_open + 1:history_close]
    buildings_pattern = re.compile(r"\bbuildings\s*=\s*\{")
    selected = None
    for match in buildings_pattern.finditer(region):
        prefix = region[:match.start()]
        depth = prefix.count("{") - prefix.count("}")
        if depth == 0:
            selected = match
            break

    if selected is None:
        insertion = (
            "\n\t\tbuildings = {\n"
            "\t\t\tinfrastructure = 7\n"
            "\t\t\tair_base = 5\n"
            "\t\t}\n"
        )
        return text[:history_open + 1] + insertion + text[history_open + 1:]

    absolute_start = history_open + 1 + selected.start()
    block_open = text.find("{", absolute_start, history_open + 1 + selected.end())
    block_close = find_matching_brace(text, block_open)
    block = text[block_open + 1:block_close]

    if not re.search(r"(?m)^\s*infrastructure\s*=", block):
        block = "\n\t\t\tinfrastructure = 7" + block
    if not re.search(r"(?m)^\s*air_base\s*=", block):
        block = "\n\t\t\tair_base = 5" + block

    return text[:block_open + 1] + block + text[block_close:]

def normalize_state_values(text: str, state_id: int) -> str:
    # Civilian population.
    if re.search(r"(?m)^\s*manpower\s*=", text):
        text = re.sub(r"(?m)^\s*manpower\s*=\s*\d+[^\r\n]*", "\tmanpower = 550000", text, count=1)
    else:
        name_match = re.search(r"(?m)^\s*name\s*=.*$", text)
        insert_at = name_match.end() if name_match else 0
        text = text[:insert_at] + "\n\tmanpower = 550000" + text[insert_at:]

    # Remove every state resource block first.
    text = remove_named_blocks(text, "resources")

    # Ensure every state has base infrastructure and an air base.
    text = ensure_base_buildings(text)

    # Normalize all base and dated building levels.
    text = re.sub(r"(?m)(\binfrastructure\s*=\s*)\d+", r"\g<1>7", text)
    text = re.sub(r"(?m)(\bair_base\s*=\s*)\d+", r"\g<1>5", text)

    # Existing ports only. Landlocked states do not receive artificial ports.
    text = re.sub(r"(?m)(\bnaval_base\s*=\s*)\d+", r"\g<1>5", text)

    # Every existing VP is worth 10.
    text = normalize_victory_points(text)

    return text

def target_for(state_id: int, original_owner: str) -> str:
    # When regenerating from our already-static main map, preserve existing
    # scenario ownership and apply only explicit expansion overrides.
    if original_owner in {"WEF", "EEF", "OBS"}:
        if state_id in WEST_EXPANSION_IDS:
            return "WEF"
        return original_owner

    # Compatibility with the original World Ablaze source set.
    if state_id in EAST_OVERRIDES:
        return "EEF"
    if state_id in WEST_OVERRIDES:
        return "WEF"
    if state_id in WEST_EXPANSION_IDS:
        return "WEF"
    if original_owner in EAST_OWNERS:
        return "EEF"
    if original_owner in WEST_OWNERS:
        return "WEF"
    return "OBS"

def transform(text: str, path: Path):
    id_match = re.search(r"^\s*id\s*=\s*(\d+)", text, re.MULTILINE)
    if not id_match:
        raise RuntimeError(f"Missing state id: {path}")
    state_id = int(id_match.group(1))

    owner_match = re.search(r"^\s*owner\s*=\s*([A-Z0-9]{3})\s*$", text, re.MULTILINE)
    original_owner = owner_match.group(1) if owner_match else ""
    target = target_for(state_id, original_owner)

    text = POLITICAL_LINE.sub("", text)

    history = re.search(r"history\s*=\s*\{", text)
    if not history:
        raise RuntimeError(f"Missing history block: {path}")

    injection = (
        "history = {\n"
        f"\t\towner = {target}\n"
        f"\t\tcontroller = {target}\n"
        f"\t\tadd_core_of = {target}"
    )
    text = text[:history.start()] + injection + text[history.end():]

    text = normalize_state_values(text, state_id)
    return state_id, target, text

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_static_states.py SOURCE_STATES_DIR DEST_STATES_DIR")

    source = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    files = sorted(source.glob("*.txt"))

    if len(files) != 1107:
        raise RuntimeError(f"Expected 1107 World Ablaze states, found {len(files)}")

    if len(WEST_EXPANSION_IDS) != 76:
        raise RuntimeError(f"Expected 76 WEF expansion states, got {len(WEST_EXPANSION_IDS)}")

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
        (dest / src.name).write_text(result, encoding="utf-8", newline="\n")

    expected_ids = set(range(1, 1108))
    if ids != expected_ids:
        missing = sorted(expected_ids - ids)
        extra = sorted(ids - expected_ids)
        raise RuntimeError(f"Unexpected state IDs. Missing={missing}, extra={extra}")

    expected = {"WEF": 182, "EEF": 182, "OBS": 743}
    actual = {key: counts[key] for key in ("WEF", "EEF", "OBS")}
    if actual != expected:
        raise RuntimeError(f"Ownership counts changed: got {actual}, expected {expected}")

    print(f"Generated {len(files)} states: WEF={counts['WEF']} EEF={counts['EEF']} OBS={counts['OBS']}")
    print("Normalized manpower=550000, infrastructure=7, air_base=5, naval_base=5, VP=10")
    print("All map resources removed; states 810 and 219 receive 10 of all non-steel/non-aluminium resources")

if __name__ == "__main__":
    main()
