#!/usr/bin/env python3
"""Generate dormant decision definitions and narrow, pinned WA safety overlays."""
from __future__ import annotations
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
WA_COMMIT = "691c7085f3ec1333ac2a0742983da8a64011ca8b"

@dataclass
class Block:
    name: str
    start: int
    end: int
    opening: int
    closing: int
    depth: int

def blocks(text: str) -> list[Block]:
    tokens = [m for m in re.finditer(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+', text)
              if not m.group().startswith('#')]
    stack = []
    result = []
    for i, token in enumerate(tokens):
        value = token.group()
        if value == '{':
            name = tokens[i-2].group().strip('"') if i >= 2 and tokens[i-1].group() == '=' else ''
            start = tokens[i-2].start() if name else token.start()
            stack.append((name, start, token.start(), len(stack)))
        elif value == '}':
            if not stack:
                raise ValueError("Unmatched closing brace")
            name, start, opening, depth = stack.pop()
            if name:
                result.append(Block(name, start, token.end(), opening, token.start(), depth))
    if stack:
        raise ValueError("Unclosed block")
    return sorted(result, key=lambda b: b.start)

def top_blocks(text: str) -> list[Block]:
    return [b for b in blocks(text) if b.depth == 0]

def replace_body(text: str, name: str, transform, depth: int | None = None) -> str:
    selected = [b for b in blocks(text) if b.name == name and (depth is None or b.depth == depth)]
    if len(selected) != 1:
        raise RuntimeError(f"Expected one {name}, found {len(selected)}")
    b = selected[0]
    return text[:b.opening+1] + transform(text[b.opening+1:b.closing]) + text[b.closing:]

def exclude_observer_scopes(text: str) -> str:
    edits = []
    scopes = {'every_country', 'every_other_country', 'random_country', 'random_other_country'}
    for b in blocks(text):
        if b.name not in scopes:
            continue
        children = top_blocks(text[b.opening+1:b.closing])
        limit = next((c for c in children if c.name == 'limit'), None)
        if limit:
            pos = b.opening + 1 + limit.opening + 1
            edits.append((pos, '\n                NOT = { tag = OBS }\n'))
        else:
            edits.append((b.opening+1, '\n                limit = { NOT = { tag = OBS } }\n'))
    for pos, value in sorted(edits, reverse=True):
        text = text[:pos] + value + text[pos:]
    return text

def guard_periodic_actions(text: str) -> str:
    edits = []
    for b in blocks(text):
        if b.name not in {'on_daily', 'on_weekly', 'on_monthly', 'on_bi_yearly_pulse'}:
            continue
        body = text[b.opening+1:b.closing]
        for child in top_blocks(body):
            if child.name != 'effect':
                continue
            left = b.opening+1+child.opening+1
            right = b.opening+1+child.closing
            edits += [(left, '\n            if = {\n                limit = { NOT = { tag = OBS } }\n'),
                      (right, '\n            }\n')]
    for pos, value in sorted(edits, reverse=True):
        text = text[:pos] + value + text[pos:]
    return text

def decision_compatibility(wa_root: Path) -> None:
    categories = set()
    decisions = {}
    missions = set()
    for p in sorted((wa_root/'common/decisions/categories').glob('*.txt')):
        categories.update(b.name for b in top_blocks(p.read_text(encoding='utf-8-sig')))
    for p in sorted((wa_root/'common/decisions').glob('*.txt')):
        text = p.read_text(encoding='utf-8-sig')
        for category in top_blocks(text):
            categories.add(category.name)
            body = text[category.opening+1:category.closing]
            for decision in top_blocks(body):
                if decision.name in {'allowed','visible','available','ai_will_do'}:
                    continue
                old = decisions.setdefault(decision.name, category.name)
                if old != category.name:
                    raise RuntimeError(f"Decision {decision.name} appears in two categories")
                db = body[decision.opening+1:decision.closing]
                if re.search(r'\bdays_mission_timeout\s*=', db):
                    missions.add(decision.name)
    # Include legacy vanilla IDs still referenced in the inherited WA scripts.
    decision_keys = 'has_active_mission|has_decision|activate_mission|remove_decision|unlock_decision_tooltip'
    category_keys = 'unlock_decision_category_tooltip|has_decision_category'
    for directory in ('common', 'events'):
        for p in (wa_root/directory).rglob('*.txt'):
            text = re.sub(r'#[^\n]*', '', p.read_text(encoding='utf-8-sig', errors='replace'))
            for key, name in re.findall(rf'\b({decision_keys})\s*=\s*([A-Za-z][A-Za-z0-9_]*)\b', text):
                if name not in {'yes','no'}:
                    decisions.setdefault(name, 'waef_legacy_compatibility')
                    if key == 'has_active_mission': missions.add(name)
            categories.update(re.findall(rf'\b(?:{category_keys})\s*=\s*([A-Za-z][A-Za-z0-9_]*)\b', text))
    categories.update(decisions.values())
    header = f'# Generated dormant compatibility definitions from WA {WA_COMMIT}.\n# IDs remain resolvable; historical decisions are unavailable in this scenario.\n\n'
    cat = header
    for name in sorted(categories):
        cat += f'{name} = {{\n    icon = generic_political_actions\n    allowed = {{ always = no }}\n    visible = {{ always = no }}\n}}\n\n'
    grouped = defaultdict(list)
    for name, category in decisions.items(): grouped[category].append(name)
    out = header
    for category in sorted(grouped):
        out += f'{category} = {{\n'
        for name in sorted(grouped[category]):
            out += f'    {name} = {{\n        icon = generic_political_discourse\n        allowed = {{ always = no }}\n        visible = {{ always = no }}\n        available = {{ always = no }}\n        cost = 0\n'
            if name in missions: out += '        days_mission_timeout = 1\n        activation = { always = no }\n'
            out += '        ai_will_do = { base = 0 }\n    }\n'
        out += '}\n\n'
    (ROOT/'common/decisions/categories/waef_legacy_compatibility.txt').write_text(cat.rstrip()+'\n')
    (ROOT/'common/decisions/waef_legacy_compatibility.txt').write_text(out.rstrip()+'\n')
    print(f'Compatibility: {len(categories)} categories, {len(decisions)} dormant decisions')

def clean_layout(text: str) -> str:
    lines = []
    for line in text.splitlines():
        indent = re.match(r'[ \t]*', line).group()
        lines.append((indent.expandtabs(4) + line[len(indent):]).rstrip())
    return '\n'.join(lines) + '\n'

def safety_overlays(wa_root: Path) -> None:
    for name in ('100_wa_on_actions.txt', 'EAI_startup_on_actions.txt', 'EAI_misc_on_actions.txt'):
        rel = Path('common/on_actions')/name
        text = (wa_root/rel).read_text(encoding='utf-8-sig')
        text = guard_periodic_actions(exclude_observer_scopes(text))
        (ROOT/rel).write_text(clean_layout(f'# Pinned WA overlay: {WA_COMMIT}; excludes passive OBS.\n'+text))
    rel = Path('common/scripted_effects/WA_scripted_effects.txt')
    text = (wa_root/rel).read_text(encoding='utf-8-sig')
    def trade_guard(body):
        return '\n    set_variable = { civilian_factories_trade_percentage = 0 }\n    if = {\n        limit = { NOT = { tag = OBS } num_of_civilian_factories > 0 }\n'+body+'\n    }\n'
    text = replace_body(text, 'civilian_factories_trade_percentage', trade_guard, depth=0)
    (ROOT/rel).write_text(clean_layout(f'# Pinned WA overlay: {WA_COMMIT}; zero-safe civilian trade ratio.\n'+text))
    rel = Path('events/EAI_construction.txt')
    text = (wa_root/rel).read_text(encoding='utf-8-sig')
    event = next(b for b in top_blocks(text) if re.search(r'\bid\s*=\s*EAI_C\.0\b',text[b.opening+1:b.closing]))
    body = text[event.opening+1:event.closing]
    body = replace_body(body, 'immediate', lambda x: '\n        if = {\n            limit = { NOT = { tag = OBS } num_of_factories > 0 }\n'+x+'\n        }\n', depth=0)
    text = text[:event.opening+1]+body+text[event.closing:]
    (ROOT/rel).write_text(clean_layout(f'# Pinned WA overlay: {WA_COMMIT}; excludes OBS and zero-factory initialization.\n'+text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('wa_root', type=Path)
    args = parser.parse_args()
    if not (args.wa_root/'common/decisions').is_dir(): raise SystemExit('Expected a World Ablaze checkout')
    decision_compatibility(args.wa_root)
    safety_overlays(args.wa_root)

if __name__ == '__main__': main()
