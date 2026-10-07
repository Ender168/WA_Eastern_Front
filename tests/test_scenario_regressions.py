"""Regression checks for actual WAEF scripts and generated scenario data."""
from pathlib import Path
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_1940_tech_baseline as tech
import regenerate_clean_scenario as mapgen
import generate_wa_compatibility as compat

@dataclass
class Node:
    key: str
    value: object
    op: str = '='

def parse(text):
    tokens = [m.group() for m in re.finditer(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[<>=!?]+|[^\s{}<>=!?#"]+', text)
              if not m.group().startswith('#')]
    pos = 0
    def body(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens):
            key = tokens[pos]; pos += 1
            if key == '}':
                if not nested: raise ValueError('Unmatched closing brace')
                return result
            if pos < len(tokens) and tokens[pos] in ('=', '>', '<', '>=', '<=', '!=', '==', '?='):
                op = tokens[pos]; pos += 1
                value = tokens[pos]; pos += 1
                if value == '{': value = body(True)
                result.append(Node(key.strip('"'), value, op))
            else: result.append(Node(key.strip('"'), None, ''))
        if nested: raise ValueError('Unclosed block')
        return result
    return body()

def read(rel): return parse((ROOT / rel).read_text(encoding='utf-8-sig'))
def get(nodes, key, default=None): return next((n.value for n in nodes if n.key == key), default)
def walk(nodes):
    for n in nodes:
        yield n
        if isinstance(n.value, list): yield from walk(n.value)

def condition(nodes, ideas, tag='WEF', civ=282, factories=987):
    values = []
    for n in nodes:
        if n.key == 'has_idea': values.append(n.value in ideas)
        elif n.key == 'tag': values.append(tag == n.value)
        elif n.key == 'always': values.append(n.value == 'yes')
        elif n.key == 'NOT': values.append(not condition(n.value, ideas, tag, civ, factories))
        elif n.key == 'OR': values.append(any(condition([c], ideas, tag, civ, factories) for c in n.value))
        elif n.key == 'num_of_civilian_factories': values.append(civ > float(n.value))
        elif n.key == 'num_of_factories': values.append(factories > float(n.value))
        else: raise ValueError('Unsupported test trigger: '+n.key)
    return all(values)

def execute(nodes, ideas):
    taken = False
    for n in nodes:
        if n.key == 'if':
            taken = condition(get(n.value, 'limit'), ideas)
            if taken: execute([c for c in n.value if c.key != 'limit'], ideas)
        elif n.key == 'else_if':
            if not taken and condition(get(n.value, 'limit'), ideas):
                taken = True
                execute([c for c in n.value if c.key != 'limit'], ideas)
        elif n.key == 'else':
            if not taken: execute(n.value, ideas)
            taken = True
        elif n.key == 'remove_ideas': ideas.discard(n.value)
        elif n.key == 'add_ideas': ideas.add(n.value)
        else: raise ValueError('Unsupported test effect: '+n.key)

class ScenarioRegressionTests(unittest.TestCase):
    def test_fuel_repeat_calls_and_all_economy_transitions(self):
        effect = get(read('common/scripted_effects/waef_fuel_effects.txt'), 'waef_sync_fuel_capacity_penalty')
        definitions = get(get(read('common/ideas/waef_doctrine_ideas.txt'), 'ideas'), 'country')
        choices = [('civilian_economy','civilian',-.4), ('low_economic_mobilisation','early',-.2),
                   ('partial_economic_mobilisation','partial',-.1), ('war_economy','full',0),
                   ('tot_economic_mobilisation','full',0), ('undisturbed_isolation','civilian',-.4)]
        # Test forward/backward law changes and repair a previously corrupted save.
        spirits = {'waef_reduced_fuel_capacity_'+x for x in ('civilian','early','partial','full')}
        current = set(spirits)
        for law, expected, law_modifier in choices + list(reversed(choices)):
            current = (current & spirits) | {law}
            for _ in range(4):
                execute(effect, current)
                self.assertEqual(current & spirits, {'waef_reduced_fuel_capacity_'+expected})
                modifier = float(get(get(get(definitions,'waef_reduced_fuel_capacity_'+expected),'modifier'),'max_fuel_factor'))
                self.assertAlmostEqual(1 + law_modifier + modifier, .25)

    def test_unknown_law_cannot_receive_full_penalty(self):
        current = {'unknown_economy','waef_reduced_fuel_capacity_full'}
        execute(get(read('common/scripted_effects/waef_fuel_effects.txt'),'waef_sync_fuel_capacity_penalty'),current)
        self.assertEqual(current, {'unknown_economy'})

    def test_technology_exclusions_survive_recursive_dependencies(self):
        def t(name, body): return tech.parse_tech(name, 'test', body)
        excluded = 'fra_fast_bomber_ad_tech_1_2'
        data = {'root':t('root',f'start_year = 1939 sub_technologies = {{ {excluded} }}'),
                excluded:t(excluded,'start_year = 1940')}
        self.assertEqual(tech.closure({'root',excluded},data), {'root'})
        baseline = (ROOT/'common/scripted_effects/waef_1940_tech_baseline.txt').read_text()
        for name in tech.FORCE_EXCLUDE: self.assertNotRegex(baseline, rf'\b{name}\s*=\s*1')

    def test_subtechnology_inherits_dlc(self):
        data = {n:tech.parse_tech(n,'test',b) for n,b in {
            'parent':'allow_branch = { has_dlc = "By Blood Alone" } sub_technologies = { child }',
            'child':'start_year = 1940'}.items()}
        self.assertEqual(tech.effective_conditions(data)['child'], {(('By Blood Alone',),())})
        effects = get(read('common/scripted_effects/waef_1940_tech_baseline.txt'),'waef_grant_french_1940_technologies')
        self.assertNotIn('fra_cv_cas_ad_tech_2',[n.key for n in get(effects,'set_technology')])

    def test_all_state_vps_and_ownership(self):
        counts = Counter(); provinces = set(); states = {}
        for p in (ROOT/'history/states').glob('*.txt'):
            state = get(parse(p.read_text()),'state'); sid = int(get(state,'id'))
            self.assertNotIn(sid,states); states[sid]=state
            owned = {int(n.key) for n in get(state,'provinces')}
            self.assertFalse(provinces & owned); provinces |= owned
            history = get(state,'history'); counts[get(history,'owner')] += 1
            for n in history:
                if n.key == 'victory_points': self.assertIn(int(n.value[0].key),owned)
        self.assertEqual(len(states),1107)
        self.assertEqual(counts, {'WEF':141,'EEF':141,'OBS':825})
        for sid,province in mapgen.SUPPLY_PORTS.items():
            port = get(get(get(states[sid],'history'),'buildings'),str(province))
            self.assertEqual(get(port,'naval_base'),'1')

    def test_vp_repair_preserves_hub_order(self):
        states = [{'id':1,'provinces':[2,3],'vps':[(3,10),(2,5),(4,7)]},
                  {'id':2,'provinces':[4],'vps':[(4,10)]}]
        mapgen.normalize_victory_points(states)
        self.assertEqual(states[0]['vps'],[(3,10),(2,5)])
        self.assertEqual(states[1]['vps'],[(4,10)])
        before = repr(states); mapgen.normalize_victory_points(states)
        self.assertEqual(repr(states),before)

    def test_railways_and_capital_connections(self):
        # Known forbidden boundaries in pinned WA, caught in the original audit.
        blocked = {tuple(sorted(e)) for e in [(9587,11570),(3641,13390),(13391,11587),
                   (13391,6675),(9633,6675),(11618,671),(6691,3674),(6691,6687),
                   (3684,9650),(6692,9649),(685,11633),(685,9649),(4545,1450),(6763,1450)]}
        graph = defaultdict(set)
        for line in (ROOT/'map/railways.txt').read_text().splitlines():
            row = list(map(int,line.split())); self.assertEqual(row[1],len(row)-2)
            for a,b in zip(row[2:],row[3:]):
                self.assertNotIn(tuple(sorted((a,b))),blocked)
                graph[a].add(b); graph[b].add(a)
        ownership = {}
        for p in (ROOT/'history/states').glob('*.txt'):
            state=get(parse(p.read_text()),'state');tag=get(get(state,'history'),'owner')
            for n in get(state,'provinces'): ownership[int(n.key)] = tag
        hubs = [int(x.split()[1]) for x in (ROOT/'map/supply_nodes.txt').read_text().splitlines()]
        self.assertEqual(len(hubs),282); self.assertEqual(len(set(hubs)),282)
        for tag,capital in [('WEF',6521),('EEF',6380)]:
            seen={capital}; pending=deque([capital])
            while pending:
                for n in graph[pending.popleft()] - seen:
                    if ownership[n] == tag: seen.add(n); pending.append(n)
            missing={n for n in hubs if ownership[n]==tag and n not in seen}
            self.assertEqual(missing, {11047} if tag=='EEF' else set())

    def test_observer_and_zero_factory_guards(self):
        trade=get(read('common/scripted_effects/WA_scripted_effects.txt'),'civilian_factories_trade_percentage')
        gate=get(get(trade,'if'),'limit')
        self.assertFalse(condition(gate,set(),tag='OBS'))
        self.assertFalse(condition(gate,set(),civ=0))
        self.assertTrue(condition(gate,set()))
        eai=next(n.value for n in read('events/EAI_construction.txt')
                 if n.key == 'country_event' and get(n.value,'id')=='EAI_C.0')
        gate=get(get(get(eai,'immediate'),'if'),'limit')
        self.assertFalse(condition(gate,set(),tag='OBS'))
        self.assertFalse(condition(gate,set(),factories=0))
        for rel in ['common/on_actions/100_wa_on_actions.txt','common/on_actions/EAI_misc_on_actions.txt']:
            for action in get(read(rel),'on_actions'):
                if action.key in ('on_daily','on_weekly'):
                    for n in action.value:
                        if n.key=='effect':
                            gate=get(get(n.value,'if'),'limit')
                            self.assertFalse(condition(gate,set(),tag='OBS'))

    def test_commanders_are_distinct_and_legacy_decisions_are_dormant(self):
        source=read('common/decisions/waef_technology_assimilation.txt')
        for effect,total in [('create_corps_commander',50),('create_field_marshal',5)]:
            names=[get(n.value,'name') for n in walk(source) if n.key==effect]
            self.assertEqual(len(names),total); self.assertEqual(len(set(names)),total)
        decisions=read('common/decisions/waef_legacy_compatibility.txt')
        definitions=set()
        for category in decisions:
            for decision in category.value:
                definitions.add(decision.key)
                self.assertFalse(condition(get(decision.value,'allowed'),set()))
                self.assertFalse(condition(get(decision.value,'visible'),set()))
        self.assertIn('TUR_etatism_crisis_2',definitions)
        self.assertIn('FRA_modernize_airforce_mission',definitions)

    def test_starting_armies_activate_manpower_accounting(self):
        decisions = read('common/decisions/waef_technology_assimilation.txt')
        forces = next(n.value for n in walk(decisions) if n.key == 'waef_create_starting_forces')
        grants = [n.value for n in walk(forces) if n.key == 'add_timed_idea']
        self.assertEqual(len(grants), 1)
        self.assertEqual(get(grants[0], 'idea'), 'waef_manpower_accounting')
        self.assertEqual(int(get(grants[0], 'days')), 700)
        calls = [n.value for n in walk(forces) if n.key == 'country_event']
        self.assertEqual([get(e, 'id') for e in calls], ['waef.1'])

        definitions = get(get(read('common/ideas/waef_doctrine_ideas.txt'), 'ideas'), 'country')
        spirit = get(definitions, 'waef_manpower_accounting')
        self.assertEqual(int(get(get(spirit, 'modifier'), 'weekly_manpower')), -57400)
        event = get(read('events/waef_events.txt'), 'country_event')
        self.assertEqual(get(event, 'id'), 'waef.1')
        self.assertEqual(get(event, 'is_triggered_only'), 'yes')
        for path in ('localisation/english/waef_l_english.yml', 'localisation/russian/waef_l_russian.yml'):
            text = (ROOT / path).read_text(encoding='utf-8-sig')
            for key in ('waef_manpower_accounting', 'waef_manpower_accounting_desc', 'waef.1.t', 'waef.1.d', 'waef.1.a'):
                self.assertRegex(text, rf'(?m)^ {re.escape(key)}:0 ')

    def test_every_script_has_balanced_blocks(self):
        for directory in ('common','history','events'):
            for p in (ROOT/directory).rglob('*.txt'):
                with self.subTest(file=str(p.relative_to(ROOT))): compat.blocks(p.read_text(encoding='utf-8-sig'))

if __name__ == '__main__': unittest.main()
