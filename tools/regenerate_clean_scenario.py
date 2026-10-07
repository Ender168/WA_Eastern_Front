#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
import urllib.request
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATES_DIR = ROOT / "history" / "states"
MAP_DIR = ROOT / "map"

WA_COMMIT = "691c7085f3ec1333ac2a0742983da8a64011ca8b"
DEFINITION_URL = f"https://raw.githubusercontent.com/World-Ablaze/world-ablaze-beta/{WA_COMMIT}/map/definition.csv"
PROVINCES_URL = f"https://raw.githubusercontent.com/World-Ablaze/world-ablaze-beta/{WA_COMMIT}/map/provinces.bmp"
ADJACENCIES_URL = f"https://raw.githubusercontent.com/World-Ablaze/world-ablaze-beta/{WA_COMMIT}/map/adjacencies.csv"

# Retain the island theatre without leaving Yuzhny cut off from capital supply.
SUPPLY_PORTS = {213: 3134, 1028: 11047}

WEF_REMOVE = {
    1, 14, 15, 19, 20, 21, 22, 23, 24, 25, 26, 30, 31, 32, 33,
    37, 47, 110, 114, 115, 117, 142, 143, 144, 156, 164, 182, 184,
    185, 186, 187, 731, 735, 878, 957, 986, 1016, 1017, 1018, 1019,
    1020, 1023, 1032, 1051,
}
EEF_REMOVE = {
    40, 402, 403, 404, 405, 408, 409, 516, 560, 561, 562, 563,
    564, 565, 566, 567, 568, 569, 570, 571, 574, 575, 576, 577,
    578, 579, 580, 583, 584, 585, 586, 587, 588, 589, 590, 637,
    644, 654, 655, 657, 732, 742, 854, 953, 962, 1074,
}
WEF_ADD = {16, 28, 29}
EEF_ADD = {146, 406, 407, 419, 420, 963, 1014, 1015, 1027, 1044, 1045}

PLAYER_POPULATION_PER_STATE = 725_000
OBS_POPULATION_PER_STATE = 550_000

# Physical map barriers from the pinned WA map. These are geography, not
# gameplay modifiers, so the clean-state rebuild must preserve them.
IMPASSABLE_IDS = {
    101, 273, 495, 514, 515, 516, 552, 644, 674, 678, 756, 767, 775,
    782, 786, 788, 792, 793, 794, 795, 902, 947, 1001, 1003, 1048,
}

PLAYER_RESOURCE_PACKAGE = {
    "oil": 2,
    "bauxite": 11,
    "rubber": 3,
    "tungsten": 2,
    "chromium": 3,
    "coal": 35,
    "iron": 25,
}

PLAYER_BUILDING_PACKAGE = {
    "fuel_silo": 1,
    "hydro_steel_refinery": 15,
    "hydro_aluminium_refinery": 5,
}


def download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dst)


def parse_state(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    mid = re.search(r"(?m)^\s*id\s*=\s*(\d+)", text)
    mname = re.search(r'(?m)^\s*name\s*=\s*("[^"]+"|[^\r\n#]+)', text)
    mowner = re.search(r"(?m)^\s*owner\s*=\s*([A-Z0-9]{3})", text)
    if not (mid and mname and mowner):
        raise RuntimeError(f"Could not parse id/name/owner from {path}")

    vps = [(int(a), int(b)) for a, b in re.findall(
        r"victory_points\s*=\s*\{\s*(\d+)\s+(-?\d+)\s*\}", text, flags=re.S
    )]

    pblock = re.search(r"provinces\s*=\s*\{([^{}]*)\}", text, flags=re.S)
    if not pblock:
        raise RuntimeError(f"No provinces block in {path}")
    provinces = [int(x) for x in re.findall(r"\b\d+\b", pblock.group(1))]
    if not provinces:
        raise RuntimeError(f"No provinces in {path}")

    sid = int(mid.group(1))
    owner = mowner.group(1)
    if sid in WEF_REMOVE and owner == "WEF":
        owner = "OBS"
    if sid in EEF_REMOVE and owner == "EEF":
        owner = "OBS"
    if sid in WEF_ADD:
        owner = "WEF"
    if sid in EEF_ADD:
        owner = "EEF"

    return {
        "id": sid,
        "name": mname.group(1).strip(),
        "owner": owner,
        "vps": vps,
        "provinces": provinces,
        "path": path,
    }


def render_state(s: dict) -> str:
    sid = s["id"]
    owner = s["owner"]
    player = owner in {"WEF", "EEF"}
    population = PLAYER_POPULATION_PER_STATE if player else OBS_POPULATION_PER_STATE

    lines = [
        "state = {",
        f"\tid = {sid}",
        f"\tname = {s['name']}",
        f"\tmanpower = {population}",
    ]
    if sid in IMPASSABLE_IDS:
        lines.append("\timpassable = yes")
    lines.append("\tstate_category = city")

    resources = PLAYER_RESOURCE_PACKAGE if player else None
    if resources:
        lines.append("")
        lines.append("\tresources = {")
        for key, value in resources.items():
            lines.append(f"\t\t{key} = {value}")
        lines.append("\t}")

    lines += [
        "",
        "\thistory = {",
        f"\t\towner = {owner}",
        f"\t\tcontroller = {owner}",
        f"\t\tadd_core_of = {owner}",
    ]

    for prov, value in s["vps"]:
        lines += [
            "\t\tvictory_points = {",
            f"\t\t\t{prov} {value}",
            "\t\t}",
        ]

    lines += [
        "\t\tbuildings = {",
        "\t\t\tinfrastructure = 7",
    ]
    if player:
        lines += [
            "\t\t\tindustrial_complex = 2",
            "\t\t\tarms_factory = 5",
        ]
        lines += [f"\t\t\t{key} = {value}" for key, value in PLAYER_BUILDING_PACKAGE.items()]
    if sid in SUPPLY_PORTS:
        lines += [f"\t\t\t{SUPPLY_PORTS[sid]} = {{", "\t\t\t\tnaval_base = 1", "\t\t\t}"]
    lines += [
        "\t\t}",
        "\t}",
        "",
        "\tprovinces = {",
    ]
    for prov in s["provinces"]:
        lines.append(f"\t\t{prov}")
    lines += [
        "\t}",
        "}",
        "",
    ]
    return "\n".join(lines)


def choose_hub(s: dict) -> int:
    if s["vps"]:
        return s["vps"][0][0]
    return s["provinces"][0]


def read_definition(path: Path):
    color_to_pid: dict[int, int] = {}
    land: set[int] = set()
    max_pid = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 5:
                continue
            try:
                pid, r, g, b = map(int, row[:4])
            except ValueError:
                continue
            code = (r << 16) | (g << 8) | b
            color_to_pid[code] = pid
            max_pid = max(max_pid, pid)
            if row[4].strip().lower() == "land":
                land.add(pid)
    return color_to_pid, land, max_pid


def province_edges_from_bitmap(bmp: Path, color_to_pid: dict[int, int], active_provinces: set[int], max_pid: int):
    img = Image.open(bmp).convert("RGB")
    rgb = np.asarray(img, dtype=np.uint32)
    packed = (rgb[:, :, 0] << 16) | (rgb[:, :, 1] << 8) | rgb[:, :, 2]

    lut = np.zeros(1 << 24, dtype=np.int32)
    for color, pid in color_to_pid.items():
        lut[color] = pid
    ids = lut[packed]

    active = np.zeros(max_pid + 1, dtype=np.bool_)
    for pid in active_provinces:
        if 0 <= pid <= max_pid:
            active[pid] = True

    edges: set[tuple[int, int]] = set()

    def consume(a: np.ndarray, b: np.ndarray) -> None:
        mask = (a != b) & (a > 0) & (b > 0)
        if not np.any(mask):
            return
        av = a[mask]
        bv = b[mask]
        mask_active = active[av] & active[bv]
        if not np.any(mask_active):
            return
        av = av[mask_active].astype(np.int64)
        bv = bv[mask_active].astype(np.int64)
        lo = np.minimum(av, bv)
        hi = np.maximum(av, bv)
        codes = np.unique((lo << 32) | hi)
        for code in codes.tolist():
            edges.add((int(code >> 32), int(code & 0xFFFFFFFF)))

    consume(ids[:, :-1], ids[:, 1:])
    consume(ids[:-1, :], ids[1:, :])
    return edges


def build_graph(edges: set[tuple[int, int]]):
    graph: dict[int, set[int]] = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def bfs_path(graph: dict[int, set[int]], start: int, goal: int, allowed: set[int]) -> list[int] | None:
    if start == goal:
        return [start]
    q = deque([start])
    prev: dict[int, int | None] = {start: None}
    while q:
        cur = q.popleft()
        for nxt in sorted(graph.get(cur, ())):
            if nxt not in allowed or nxt in prev:
                continue
            prev[nxt] = cur
            if nxt == goal:
                out = [goal]
                while out[-1] != start:
                    out.append(prev[out[-1]])
                out.reverse()
                return out
            q.append(nxt)
    return None


def generate_supply_and_railways(states: list[dict]) -> None:
    active_states = [s for s in states if s["owner"] in {"WEF", "EEF"}]
    hub = {s["id"]: choose_hub(s) for s in active_states}
    all_state_provinces = {s["id"]: set(s["provinces"]) for s in active_states}

    cache = ROOT / ".waef_cache"
    definition = cache / "definition.csv"
    provinces_bmp = cache / "provinces.bmp"
    adjacencies = cache / "adjacencies.csv"
    download(DEFINITION_URL, definition)
    download(PROVINCES_URL, provinces_bmp)
    download(ADJACENCIES_URL, adjacencies)

    color_to_pid, land, max_pid = read_definition(definition)

    # WA state files can include lake/sea province IDs. They stay in the state
    # history, but railway topology must only use actual land provinces.
    state_provinces = {
        sid: {p for p in provinces if p in land}
        for sid, provinces in all_state_provinces.items()
    }
    for sid, provinces in state_provinces.items():
        if not provinces:
            raise RuntimeError(f"Playable state {sid} has no land provinces")
        if hub[sid] not in provinces:
            hub[sid] = min(provinces)

    province_to_state = {
        prov: sid
        for sid, provinces in state_provinces.items()
        for prov in provinces
    }
    active_provinces = set(province_to_state)

    edges = province_edges_from_bitmap(provinces_bmp, color_to_pid, active_provinces, max_pid)
    # Pixel contact is not sufficient: WA closes mountain passes explicitly.
    blocked = set()
    with adjacencies.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) > 2 and row[2].strip() == "impassable":
                a, b = int(row[0]), int(row[1])
                blocked.add((min(a, b), max(a, b)))
    edges -= blocked
    graph = build_graph(edges)

    state_edges: set[tuple[int, int]] = set()
    for pa, pb in edges:
        sa = province_to_state.get(pa)
        sb = province_to_state.get(pb)
        if sa is None or sb is None or sa == sb:
            continue
        state_edges.add((min(sa, sb), max(sa, sb)))

    MAP_DIR.mkdir(parents=True, exist_ok=True)
    supply_lines = [f"1 {hub[sid]}" for sid in sorted(hub)]
    (MAP_DIR / "supply_nodes.txt").write_text("\n".join(supply_lines) + "\n", encoding="utf-8")

    all_playable = set(active_provinces)
    rail_edges: set[tuple[int, int]] = set()
    missing: list[tuple[int, int]] = []
    routed_state_pairs = 0
    for sa, sb in sorted(state_edges):
        allowed = state_provinces[sa] | state_provinces[sb]
        path = bfs_path(graph, hub[sa], hub[sb], allowed)
        if path is None:
            path = bfs_path(graph, hub[sa], hub[sb], all_playable)
        if path is None or len(path) < 2:
            missing.append((sa, sb))
            continue
        routed_state_pairs += 1
        for a, b in zip(path, path[1:]):
            rail_edges.add((min(a, b), max(a, b)))

    if missing:
        raise RuntimeError("Could not route railways for adjacent state pairs: " + ", ".join(f"{a}-{b}" for a, b in missing[:30]))

    # Serialize the union graph as unique two-province segments. This avoids
    # duplicated railway edges when several hub-to-hub routes share a trunk.
    rail_lines = [f"3 2 {a} {b}" for a, b in sorted(rail_edges)]
    (MAP_DIR / "railways.txt").write_text("\n".join(rail_lines) + "\n", encoding="utf-8")
    print(
        f"Generated {len(supply_lines)} supply hubs, "
        f"{routed_state_pairs} adjacent-state hub connections and "
        f"{len(rail_lines)} unique level-3 railway segments."
    )


def validate(states: list[dict]) -> None:
    counts = defaultdict(int)
    by_id = {s["id"]: s for s in states}
    for s in states:
        counts[s["owner"]] += 1
    expected = {"WEF": 141, "EEF": 141, "OBS": 825}
    actual = {k: counts[k] for k in expected}
    if actual != expected:
        raise RuntimeError(f"Unexpected ownership counts: {actual}, expected {expected}")
    for sid in WEF_ADD:
        if by_id[sid]["owner"] != "WEF":
            raise RuntimeError(f"State {sid} was not moved to WEF")
    for sid in EEF_ADD:
        if by_id[sid]["owner"] != "EEF":
            raise RuntimeError(f"State {sid} was not moved to EEF")
    for sid in WEF_REMOVE | EEF_REMOVE:
        if by_id[sid]["owner"] != "OBS":
            raise RuntimeError(f"State {sid} was not moved to OBS")
    for sid, province in SUPPLY_PORTS.items():
        if by_id[sid]["owner"] != "EEF" or province not in by_id[sid]["provinces"]:
            raise RuntimeError(f"Invalid supply port {sid}/{province}")


def normalize_victory_points(states: list[dict]) -> None:
    """Relocate inherited misplaced VPs, keeping one value per province."""
    province_state = {}
    for s in states:
        for province in s["provinces"]:
            if province in province_state:
                raise RuntimeError(f"Duplicate province {province}")
            province_state[province] = s
    values = {}
    ordered = {s["id"]: [] for s in states}
    for s in states:
        for province, value in s["vps"]:
            if province not in province_state:
                raise RuntimeError(f"Undefined VP province {province}")
            values[province] = max(value, values.get(province, value))
            if province_state[province]["id"] == s["id"] and province not in ordered[s["id"]]:
                ordered[s["id"]].append(province)
    # Preserve existing valid VP order, including each state's supply-hub choice.
    for s in states:
        for province, _ in s["vps"]:
            sid = province_state[province]["id"]
            if province not in ordered[sid]:
                ordered[sid].append(province)
    for s in states:
        s["vps"] = [(province, values[province]) for province in ordered[s["id"]]]


def main() -> int:
    state_paths = sorted(STATES_DIR.glob("*.txt"))
    if len(state_paths) != 1107:
        raise RuntimeError(f"Expected 1107 state files, found {len(state_paths)}")

    states = [parse_state(p) for p in state_paths]
    normalize_victory_points(states)
    validate(states)

    for s in states:
        s["path"].write_text(render_state(s), encoding="utf-8")

    generate_supply_and_railways(states)

    forbidden = (
        "add_dynamic_modifier",
        "add_state_modifier",
        "stronghold_network",
        "bunker =",
        "coastal_bunker",
        "dockyard",
        "air_base",
        "anti_air_building",
        "rocket_site",
        "nuclear_reactor",
    )
    for p in state_paths:
        text = p.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                raise RuntimeError(f"Forbidden token {token!r} survived in {p}")
        sid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        if "naval_base" in text and sid not in SUPPLY_PORTS:
            raise RuntimeError(f"Unexpected naval base in {p}")
        is_player = bool(re.search(r"(?m)^\s*owner\s*=\s*(?:WEF|EEF)\s*$", text))
        if ("resources = {" in text) != is_player:
            raise RuntimeError(f"Resource block mismatch for player/observer state {p}")
        for building, level in PLAYER_BUILDING_PACKAGE.items():
            signature = f"\t\t\t{building} = {level}"
            if (signature in text) != is_player:
                raise RuntimeError(f"Static building {building} mismatch in {p}")
        if re.search(r"(?m)^\s*(?:synthetic_refinery|steel_refinery|aluminium_refinery|hydro_steel_refinery_inactive|hydro_aluminium_refinery_inactive)\s*=", text):
            raise RuntimeError(f"Unexpected additional refinery in {p}")

    print("Static scenario map regenerated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
