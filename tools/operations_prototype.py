"""Offline operation accounting and exact map audit; does not change game scripts."""
from dataclasses import dataclass
from pathlib import Path
import argparse
import csv
import json
import re
from collections import defaultdict
from generate_1940_tech_baseline import named_blocks, strip_comments

@dataclass
class Operation:
    preparation_days: int
    offensive_days: int
    fatigue: int = 0
    phase: str = 'preparation'
    elapsed: int = 0
    preparation_refund: int = 0
    fatigue_days: int = 0
    fatigue_interval: int = 7

    def tick(self, victory=False, at_war=True):
        """Daily ordering: peace, victory, charge, phase boundary. One call per day."""
        if self.phase in ('victory', 'failed', 'cancelled'):
            return
        if not at_war:
            self.phase = 'cancelled'
            return
        if victory:
            self.fatigue = max(0, self.fatigue - self.preparation_refund)
            self.phase = 'victory'
            return
        self.elapsed += 1
        self.fatigue_days += 1
        if self.fatigue_days >= self.fatigue_interval:
            before = self.fatigue
            self.fatigue = min(100, self.fatigue + 1)
            if self.phase == 'preparation':
                self.preparation_refund += self.fatigue - before
            self.fatigue_days = 0
        if self.phase == 'preparation' and self.elapsed == self.preparation_days:
            self.phase = 'offensive'
            self.elapsed = 0
        elif self.phase == 'offensive' and self.elapsed == self.offensive_days:
            self.phase = 'failed'


def enemy_majority(provinces, enemy_controlled):
    return 2 * len(set(provinces) & set(enemy_controlled)) > len(set(provinces))


def audit(wa_root, mod_root):
    land = set()
    for row in csv.reader((wa_root / 'map/definition.csv').read_text(encoding='utf-8-sig').splitlines(), delimiter=';'):
        if len(row) > 4 and row[0].isdigit() and row[4] == 'land':
            land.add(int(row[0]))
    province_region = {}
    for path in sorted((wa_root / 'map/strategicregions').glob('*.txt')):
        raw = strip_comments(path.read_text(encoding='utf-8-sig'))
        region = int(re.search(r'\bid\s*=\s*(\d+)', raw)[1])
        for province in map(int, re.findall(r'\d+', named_blocks(raw, 'provinces')[0])):
            if province in province_region:
                raise ValueError(f'Duplicate region for {province}')
            province_region[province] = region
    regions = defaultdict(lambda: {'provinces': [], 'states': []})
    states = {}
    split_states = {}
    for path in sorted((mod_root / 'history/states').glob('*.txt')):
        raw = strip_comments(path.read_text(encoding='utf-8-sig'))
        if not re.search(r'owner\s*=\s*(WEF|EEF)\b', raw):
            continue
        sid = int(re.search(r'\bid\s*=\s*(\d+)', raw)[1])
        provinces = sorted(set(map(int, re.findall(r'\d+', named_blocks(raw, 'provinces')[0]))) & land)
        membership = defaultdict(list)
        for province in provinces:
            membership[province_region[province]].append(province)
        states[str(sid)] = {'provinces': provinces, 'tactical_eligible': len(provinces) > 7, 'regions': sorted(membership)}
        if len(membership) != 1:
            split_states[str(sid)] = sorted(membership)
        for rid, ps in membership.items():
            regions[rid]['provinces'].extend(ps)
            regions[rid]['states'].append(sid)
    assert len(states) == 282
    return {
        'scope': 'WEF/EEF playable land provinces; excludes OBS, sea and lakes',
        'tactical_minimum_provinces': 8,
        'state_count': len(states),
        'tactical_eligible_count': sum(s['tactical_eligible'] for s in states.values()),
        'split_states': split_states,
        'states': states,
        'regions': {str(rid): {'states': sorted(set(data['states'])), 'provinces': sorted(set(data['provinces'])), 'playable_enemy_minimum': len(set(data['provinces'])) // 2 + 1, 'full_region_land_provinces': sorted(p for p, r in province_region.items() if r == rid and p in land), 'full_region_enemy_minimum': sum(r == rid and p in land for p, r in province_region.items()) // 2 + 1} for rid, data in sorted(regions.items())},
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wa-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.wa_root, Path(__file__).resolve().parents[1])
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('state_count', 'tactical_eligible_count', 'split_states')}))
