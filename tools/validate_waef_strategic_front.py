#!/usr/bin/env python3
"""Static checks for the WAEF strategic front."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "tools/waef_strategic_cities.json").read_text(encoding="utf-8"))
D = (ROOT / "common/decisions/waef_strategic_front.txt").read_text(encoding="utf-8-sig")
RU = (ROOT / "localisation/russian/waef_strategic_front_l_russian.yml").read_text(encoding="utf-8-sig")
EN = (ROOT / "localisation/english/waef_strategic_front_l_english.yml").read_text(encoding="utf-8-sig")
cities = DATA["objectives"]
assert len(cities) == 40
assert sum(x["owner"] == "WEF" for x in cities) == 20
assert sum(x["owner"] == "EEF" for x in cities) == 20
assert len({x["province"] for x in cities}) == 40
assert len({x["slug"] for x in cities}) == 40
assert DATA["capture_days"] == 14 and DATA["collapse_days"] == 30 and DATA["collapse_threshold"] == 16

for city in cities:
    p = list((ROOT / "history/states").glob(str(city["state"]) + "-*.txt"))
    assert len(p) == 1, city
    content = p[0].read_text(encoding="utf-8-sig")
    assert "owner = " + city["owner"] in content, city
    vps = [(int(a), int(b)) for a,b in re.findall(r"victory_points\s*=\s*\{\s*(\d+)\s+(-?\d+)\s*\}", content)]
    assert city["province"] in {p for p,_ in vps}, city
    for kind in ("capture", "liberate", "captured", "lost"):
        key = "waef_strategic_" + kind + "_" + city["slug"]
        assert D.count(key + " = {") == 1, key
        assert " " + key + ":0 " in RU, key
        assert " " + key + ":0 " in EN, key
for t in ("wef", "eef"):
    assert D.count("waef_strategic_collapse_" + t + " = {") == 1
assert D.count("days_mission_timeout = 14") == 80
assert D.count("days_mission_timeout = 30") == 2
assert D.count("controls_province = ") == 240
assert D.count("{") == D.count("}")
for lang in (RU,EN):
    keys = re.findall(r"(?m)^\s+([^:#\s]+):0 ",lang)
    assert len(keys) == len(set(keys))
print("PASS: 20+20 cities, unique VP provinces, 80 timed city missions, 2 collapse missions, localisations")
