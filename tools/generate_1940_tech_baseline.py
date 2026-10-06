#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_EFFECTS = ROOT / "common" / "scripted_effects" / "waef_1940_tech_baseline.txt"
OUT_MANIFEST = ROOT / "docs" / "TECH_BASELINE_1940.md"

WA_COMMIT = "691c7085f3ec1333ac2a0742983da8a64011ca8b"
TREE_URL = f"https://api.github.com/repos/World-Ablaze/world-ablaze-beta/git/trees/{WA_COMMIT}?recursive=1"
RAW = f"https://raw.githubusercontent.com/World-Ablaze/world-ablaze-beta/{WA_COMMIT}/"

CUTOFF_YEAR = 1940

# WAEF uses the neutral industry philosophy as the common 1940 baseline.
# The two mutually exclusive specialisations remain unresearched.
FORCE_EXCLUDE = {"concentrated_industry", "dispersed_industry"}

SHARED_FILES = {
    "common/technologies/industry.txt",
    "common/technologies/electronic_mechanical_engineering.txt",
    "common/technologies/support.txt",
}

SCHOOLS = {
    "french": "fra",
    "italian": "ita",
    "japanese": "jap",
    "german": "ger",
    "soviet": "sov",
    "british": "eng",
    "unitedstates": "usa",
}

NATIONAL_PREFIXES = (
    "air_techs_",
    "armor_",
    "artillery_",
    "infantry_",
    "naval_",
)


@dataclass(frozen=True)
class Tech:
    name: str
    path: str
    body: str
    year: int
    has_folder: bool
    doctrine: bool
    dependencies: tuple[str, ...]
    sub_technologies: tuple[str, ...]
    leads_to: tuple[str, ...]
    requires_dlc: tuple[str, ...]
    forbids_dlc: tuple[str, ...]


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "WAEF-tech-generator"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8-sig")


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        buf = []
        in_string = False
        escaped = False
        for ch in line:
            if in_string:
                buf.append(ch)
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                    buf.append(ch)
                elif ch == "#":
                    break
                else:
                    buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out)


def matching_brace(text: str, open_pos: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for i in range(open_pos, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise RuntimeError("Unclosed brace block")


def named_blocks(text: str, name: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(name)}\s*=\s*\{{")
    out = []
    pos = 0
    while True:
        m = pattern.search(text, pos)
        if not m:
            return out
        open_pos = text.find("{", m.start())
        close_pos = matching_brace(text, open_pos)
        out.append(text[open_pos + 1:close_pos])
        pos = close_pos + 1


def technology_blocks(text: str) -> dict[str, str]:
    clean = strip_comments(text)
    m = re.search(r"\btechnologies\s*=\s*\{", clean)
    if not m:
        return {}
    outer_open = clean.find("{", m.start())
    outer_close = matching_brace(clean, outer_open)
    body = clean[outer_open + 1:outer_close]

    result: dict[str, str] = {}
    i = 0
    depth = 0
    in_string = False
    escaped = False
    while i < len(body):
        ch = body[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            i += 1
            continue
        if ch in "{}":
            depth += 1 if ch == "{" else -1
            i += 1
            continue
        if depth == 0:
            mtech = re.match(r"\s*([A-Za-z0-9_\.\-]+)\s*=\s*\{", body[i:])
            if mtech:
                name = mtech.group(1)
                open_pos = i + mtech.group(0).rfind("{")
                close_pos = matching_brace(body, open_pos)
                result[name] = body[open_pos + 1:close_pos]
                i = close_pos + 1
                continue
        i += 1
    return result


def token_list(block: str, key: str) -> tuple[str, ...]:
    values: list[str] = []
    for inner in named_blocks(block, key):
        values.extend(re.findall(r"\b([A-Za-z0-9_\.\-]+)\s*(?:=\s*1)?\b", inner))
    ignored = {"if", "limit", "has_dlc", "NOT", "OR", "AND", "yes", "no"}
    return tuple(dict.fromkeys(v for v in values if v not in ignored and not v.isdigit()))


def dlc_signature(block: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    requires: set[str] = set()
    forbids: set[str] = set()
    for inner in named_blocks(block, "allow_branch"):
        neg = set(re.findall(r'NOT\s*=\s*\{\s*has_dlc\s*=\s*"([^"]+)"\s*\}', inner, flags=re.S))
        all_dlc = set(re.findall(r'has_dlc\s*=\s*"([^"]+)"', inner))
        forbids |= neg
        requires |= (all_dlc - neg)
    return tuple(sorted(requires)), tuple(sorted(forbids))


def parse_tech(name: str, path: str, body: str) -> Tech:
    year_match = re.search(r"\bstart_year\s*=\s*(\d+)", body)
    year = int(year_match.group(1)) if year_match else 1936
    has_folder = bool(re.search(r"\bfolder\s*=\s*\{", body))
    doctrine = bool(re.search(r"\bdoctrine\s*=\s*yes\b", body))
    requires, forbids = dlc_signature(body)
    return Tech(
        name=name,
        path=path,
        body=body,
        year=year,
        has_folder=has_folder,
        doctrine=doctrine,
        dependencies=token_list(body, "dependencies"),
        sub_technologies=token_list(body, "sub_technologies"),
        leads_to=tuple(dict.fromkeys(re.findall(
            r"\bleads_to_tech\s*=\s*([A-Za-z0-9_\.\-]+)", body
        ))),
        requires_dlc=requires,
        forbids_dlc=forbids,
    )


def selected_national_files(all_paths: set[str], suffix: str) -> set[str]:
    wanted = set()
    for stem in NATIONAL_PREFIXES:
        p = f"common/technologies/{stem}{suffix}.txt"
        if p in all_paths:
            wanted.add(p)
    return wanted


def closure(seed: set[str], techs: dict[str, Tech]) -> set[str]:
    chosen = set(seed)
    queue = deque(seed)
    while queue:
        name = queue.popleft()
        tech = techs[name]

        # Real prerequisites must not point beyond the requested cutoff.
        for dep in tech.dependencies:
            if dep not in techs or dep in chosen:
                continue
            child = techs[dep]
            if child.doctrine:
                continue
            if child.year > CUTOFF_YEAR:
                # WA contains a few early technologies with later retrofitted
                # dependencies. The scenario cutoff wins: grant the early
                # technology directly, but never drag future tech backward.
                continue
            chosen.add(dep)
            queue.append(dep)

        # sub_technologies are variants unlocked by the parent, not
        # prerequisites. Keep only variants that themselves fit the cutoff.
        for sub in tech.sub_technologies:
            if sub not in techs or sub in chosen:
                continue
            child = techs[sub]
            if child.doctrine or child.year > CUTOFF_YEAR:
                continue
            chosen.add(sub)
            queue.append(sub)

    return chosen


def eligible_seed(path_set: set[str], techs: dict[str, Tech]) -> set[str]:
    return {
        name
        for name, tech in techs.items()
        if tech.path in path_set
        and tech.has_folder
        and not tech.doctrine
        and tech.year <= CUTOFF_YEAR
        and name not in FORCE_EXCLUDE
    }


def effective_conditions(techs: dict[str, Tech]) -> dict[str, set[tuple[tuple[str, ...], tuple[str, ...]]]]:
    parents: dict[str, set[str]] = defaultdict(set)
    for parent_name, tech in techs.items():
        for child in tech.leads_to:
            if child in techs:
                parents[child].add(parent_name)

    unconditional = ((), ())
    memo: dict[str, set[tuple[tuple[str, ...], tuple[str, ...]]]] = {}

    def resolve(name: str, stack: set[str]) -> set[tuple[tuple[str, ...], tuple[str, ...]]]:
        if name in memo:
            return memo[name]
        if name in stack:
            return {unconditional}

        tech = techs[name]
        explicit = (tech.requires_dlc, tech.forbids_dlc)
        if explicit != unconditional:
            memo[name] = {explicit}
            return memo[name]

        parent_names = parents.get(name, set())
        if not parent_names:
            memo[name] = {unconditional}
            return memo[name]

        conditions: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
        next_stack = set(stack)
        next_stack.add(name)
        for parent in parent_names:
            conditions |= resolve(parent, next_stack)

        # If any valid path is unconditional, the child is unconditional.
        if unconditional in conditions:
            conditions = {unconditional}
        memo[name] = conditions or {unconditional}
        return memo[name]

    for name in techs:
        resolve(name, set())
    return memo


def condition_key(tech: Tech) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return tech.requires_dlc, tech.forbids_dlc


def render_set(names: list[str], indent: str) -> list[str]:
    if not names:
        return []
    lines = [indent + "set_technology = {"]
    lines += [indent + f"    {name} = 1" for name in names]
    lines.append(indent + "}")
    return lines


def render_effect(
    effect_name: str,
    names: set[str],
    techs: dict[str, Tech],
    conditions: dict[str, set[tuple[tuple[str, ...], tuple[str, ...]]]],
) -> str:
    grouped: dict[tuple[tuple[str, ...], tuple[str, ...]], list[str]] = defaultdict(list)
    unconditional_key = ((), ())

    for name in sorted(names):
        alternatives = conditions[name]
        if unconditional_key in alternatives:
            grouped[unconditional_key].append(name)
            continue
        for signature in alternatives:
            grouped[signature].append(name)

    lines = [f"{effect_name} = {{"]
    unconditional = grouped.pop(unconditional_key, [])
    lines += render_set(sorted(set(unconditional)), "    ")

    for (requires, forbids), group_names in sorted(grouped.items()):
        lines += ["", "    if = {", "        limit = {"]
        for dlc in requires:
            lines.append(f'            has_dlc = "{dlc}"')
        for dlc in forbids:
            lines.append(f'            NOT = {{ has_dlc = "{dlc}" }}')
        lines += ["        }"]
        lines += render_set(sorted(set(group_names)), "        ")
        lines += ["    }"]
    lines += ["}", ""]
    return "\n".join(lines)


def main() -> None:
    tree = json.loads(fetch_text(TREE_URL))
    paths = {
        item["path"]
        for item in tree["tree"]
        if item.get("type") == "blob"
        and item["path"].startswith("common/technologies/")
        and item["path"].endswith(".txt")
    }

    all_techs: dict[str, Tech] = {}
    duplicates: dict[str, list[str]] = defaultdict(list)
    for path in sorted(paths):
        text = fetch_text(RAW + path)
        for name, body in technology_blocks(text).items():
            tech = parse_tech(name, path, body)
            if name in all_techs:
                duplicates[name].extend([all_techs[name].path, path])
            else:
                all_techs[name] = tech
    if duplicates:
        raise RuntimeError("Duplicate technology IDs: " + repr(dict(duplicates)))

    conditions = effective_conditions(all_techs)
    shared = closure(eligible_seed(SHARED_FILES, all_techs), all_techs)

    school_sets: dict[str, set[str]] = {}
    school_files: dict[str, set[str]] = {}
    for school, suffix in SCHOOLS.items():
        files = selected_national_files(paths, suffix)
        school_files[school] = files
        national = closure(eligible_seed(files, all_techs), all_techs)
        school_sets[school] = national - shared

    effects = [
        "# Generated from World Ablaze technology definitions.",
        f"# Pinned WA commit: {WA_COMMIT}",
        f"# Cutoff: start_year <= {CUTOFF_YEAR}.",
        "# Doctrine technologies are excluded; Grand Strategy is assigned by Assimilate.",
        "",
        render_effect("waef_grant_shared_1940_technologies", shared, all_techs, conditions),
    ]
    for school in SCHOOLS:
        effects.append(render_effect(
            f"waef_grant_{school}_1940_technologies",
            school_sets[school],
            all_techs,
            conditions,
        ))
    OUT_EFFECTS.parent.mkdir(parents=True, exist_ok=True)
    OUT_EFFECTS.write_text("\n".join(effects), encoding="utf-8")

    manifest = [
        "# WAEF 1940 Technology Baseline",
        "",
        f"Pinned World Ablaze commit: `{WA_COMMIT}`.",
        "",
        "Rules:",
        f"- cutoff: `start_year <= {CUTOFF_YEAR}`;",
        "- a technology without an explicit start year is treated as 1936 only if it is visible in a technology folder;",
        "- shared seeds: Industry, Electronics, Support;",
        "- military seeds: only the selected national air/armor/artillery/infantry/naval files;",
        "- doctrine technologies are excluded;",
        "- dependencies and sub-technologies are included recursively only while they remain at or before the cutoff;",
        "- DLC-gated branches inherit their DLC conditions through leads_to_tech chains;",
        "- standard_industry is granted as the neutral common industry philosophy;",
        "- concentrated_industry and dispersed_industry are intentionally excluded.",
        "",
        f"Shared technologies: **{len(shared)}**.",
        "",
    ]
    for school in SCHOOLS:
        names = school_sets[school]
        manifest += [
            f"## {school}",
            "",
            "Source files:",
            *[f"- `{p}`" for p in sorted(school_files[school])],
            "",
            f"National technologies: **{len(names)}**.",
            f"Total with shared: **{len(names | shared)}**.",
            "",
            "Technology IDs:",
            "",
            *[f"- `{name}` ({all_techs[name].year})" for name in sorted(names)],
            "",
        ]
    OUT_MANIFEST.write_text("\n".join(manifest), encoding="utf-8")

    print(f"Shared <=1940 technologies: {len(shared)}")
    for school in SCHOOLS:
        print(
            f"{school}: {len(school_sets[school])} national, "
            f"{len(school_sets[school] | shared)} total"
        )


if __name__ == "__main__":
    main()
