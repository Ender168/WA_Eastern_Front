"""Checks the reviewed seven-school tree, research restrictions and timed missions."""
from pathlib import Path
import json,re,unittest,itertools
from test_scenario_regressions import parse,get,walk,Node
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_1940_tech_baseline as baseline

def read(rel):return parse((ROOT/rel).read_text(encoding='utf-8-sig'))
def text(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def focus_nodes():
 return {get(n.value,'id'):n.value for path in (ROOT/'common/national_focus').glob('waef_*_tech_focus.txt') for n in get(parse(path.read_text()),'focus_tree') if n.key=='focus'}
def localisation(lang):
 result={}
 for p in list((ROOT/'localisation'/lang).glob('*focus*.yml'))+list((ROOT/'localisation'/'replace').glob(f'*focus*_l_{lang}.yml')):
  assert p.read_bytes().startswith(b'\xef\xbb\xbf'),p
  for k,v in re.findall(r'^\s*(\w+):\d*\s+"(.*)"',p.read_text(encoding='utf-8-sig'),re.M):
   assert k not in result,(k,p)
   result[k]=v
 return result

def eval_gate(nodes,tag='WEF',done=(),date=19420101):
 vals=[]
 for n in nodes:
  if n.key=='tag':vals.append(tag==n.value)
  elif n.key=='always':vals.append(n.value=='yes')
  elif n.key=='date':
   y,m,d=map(int,n.value.split('.'));vals.append(date>y*10000+m*100+d)
  elif n.key=='has_completed_focus':vals.append(n.value in done)
  elif n.key=='OR':vals.append(any(eval_gate([x],tag,done,date) for x in n.value))
  elif n.key=='AND':vals.append(eval_gate(n.value,tag,done,date))
  elif n.key=='NOT':vals.append(not eval_gate(n.value,tag,done,date))
  else:raise ValueError(n.key)
 return all(vals)

class NationalFocusTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(text('docs/NATIONAL_FOCUS_MANIFEST.json'));cls.nodes=focus_nodes()
  cls.techs={}
  for p in (ROOT/'common/technologies').glob('*.txt'):
   for k,v in baseline.technology_blocks(p.read_text()).items():cls.techs[k]=baseline.parse_tech(k,str(p),v)
 def test_all_seven_schools_and_real_rewards(self):
  self.assertEqual(set(self.m['schools']),{'GER','SOV','USA','ENG','FRA','ITA','JAP'})
  self.assertEqual(len(self.nodes),269)
  for code,rows in self.m['schools'].items():
   self.assertEqual(len(rows),53 if code=='GER' else 36)
   for row in rows:
    node=self.nodes[row['id']];self.assertEqual(int(get(node,'cost'))*7,row['days'])
    self.assertTrue(get(node,'completion_reward'))
    granted={x.key for n in walk(get(node,'completion_reward')) if n.key=='set_technology' for x in n.value if x.value=='1'}
    self.assertEqual(granted,set(row['technologies']))
 def test_no_future_technology_in_any_focus_reward(self):
  for rows in self.m['schools'].values():
   for row in rows:
    self.assertTrue(eval_gate(get(self.nodes[row['id']],'available'),done=row.get('availability_requires',[]),date=row['year']*10000+101))
    self.assertTrue(eval_gate(get(self.nodes[row['id']],'available'),done=row.get('availability_requires',[]),date=19360101))
    self.assertNotIn('date',[n.key for n in walk(get(self.nodes[row['id']],'available'))])
    for tech in row['technologies']:
     self.assertIn(tech,self.techs)
     self.assertLessEqual(self.techs[tech].year,row['year'],(row['id'],tech))
 def test_focus_graph_is_reachable_and_has_no_overlap(self):
  for code,rows in self.m['schools'].items():
   coords=set();done=set();todo=list(rows)
   for r in rows:
    n=self.nodes[r['id']];coord=(get(n,'x'),get(n,'y'))
    self.assertNotIn(coord,coords,(code,r['id']));coords.add(coord)
   while todo:
    ready=[r for r in todo if set(r['prerequisites'])<=done]
    self.assertTrue(ready,'Unreachable prerequisite cycle: '+code)
    for r in ready:done.add(r['id']);todo.remove(r)
 def test_mutually_exclusive_choices_are_symmetric(self):
  for rows in self.m['schools'].values():
   lookup={r['id']:r for r in rows}
   for r in rows:
    if r['exclusive']:
     for other in r['exclusive']:self.assertIn(r['id'],lookup[other]['exclusive'])
     self.assertEqual([n.value for n in get(self.nodes[r['id']],'mutually_exclusive') if n.key=='focus'],r['exclusive'])
 def test_shared_rewards_are_identical_for_all_schools(self):
  reference={r['code']:r for r in self.m['schools']['GER'] if r['code'].startswith('C')}
  for code,rows in self.m['schools'].items():
   for r in rows:
    if r['code'] in reference:
     a=reference[r['code']]
     self.assertEqual((r['year'],r['days'],r['technologies'],[e for e in r['effects'] if e!='waef_grant_german_jet_aircraft = yes']),(a['year'],a['days'],a['technologies'],[e for e in a['effects'] if e!='waef_grant_german_jet_aircraft = yes']))
 def test_all_seven_assimilations_switch_and_grant_baseline(self):
  src=read('common/decisions/waef_technology_assimilation.txt')
  from generate_national_focus_trees import SCHOOLS,START_EXCEPTIONS
  for c,s in SCHOOLS.items():
   node=next(n for n in walk(src) if n.key=='waef_assimilate_'+s+'_technologies')
   effect=get(node.value,'complete_effect')
   self.assertEqual(get(get(effect,'load_focus_tree'),'tree'),f'WAEF_{c}_TECH_DOCTRINE')
   self.assertEqual(get(get(effect,'load_focus_tree'),'keep_completed'),'no')
   self.assertEqual(get(effect,'waef_grant_'+s+'_1940_technologies'),'yes')
   flags=[n.value for n in effect if n.key=='set_country_flag']
   self.assertIn('waef_1940_technology_baseline_applied',flags)
   grants={x.key for n in walk(effect) if n.key=='set_technology' for x in n.value}
   self.assertEqual(grants,set(START_EXCEPTIONS.get(c,[])))
 def test_reward_cannot_unlock_an_alternative_route(self):
  for code,rows in self.m['schools'].items():
   deps={r['id']:r['prerequisites'] for r in rows}
   def ancestors(f):return {f}|set().union(*(ancestors(p) for p in deps[f]))
   for r in rows:
    for t in r['technologies']:
     gate=self.m['research_gates'].get(t,{}).get('requires_focus')
     if gate:self.assertTrue(set(gate if isinstance(gate,list) else [gate]) & ancestors(r['id']),(r['id'],t,gate))
 def test_generated_script_files_have_balanced_blocks(self):
  for folder in ['common/technologies','common/national_focus','common/decisions','common/scripted_effects','common/scripted_triggers','common/dynamic_modifiers']:
   for path in (ROOT/folder).glob('*.txt'):
    if folder=='common/technologies' or path.name.startswith('waef_'):
     parse(path.read_text(encoding='utf-8-sig'))
 def test_both_fronts_have_independent_operation_modifiers(self):
  effects=read('common/scripted_effects/waef_focus_operations.txt')
  for scale in ['local','regional']:
   keys=[get(n.value,'modifier') for n in walk(get(effects,'waef_activate_'+scale+'_offensive')) if n.key=='add_dynamic_modifier']
   self.assertEqual(set(keys),{f'waef_{tag}_offensive_{scale}_modifier' for tag in ['wef','eef']})
  for mission in ['waef_local_offensive_21','waef_regional_offensive_45']:
   n=get(get(read('common/decisions/waef_focus_operations.txt'),'waef_operations'),mission)
   self.assertEqual(get(get(n,'cancel_effect'),'waef_fail_'+('local' if 'local' in mission else 'regional')+'_offensive'),'yes')
 def test_closed_routes_cannot_be_researched_even_after_1945(self):
  for name,gate in self.m['research_gates'].items():
   if not gate.get('requires_focus'):continue
   allow=get(parse('allow = {'+baseline.named_blocks(self.techs[name].body,'allow')[0]+'}'),'allow')
   # Existing upstream restrictions may include other triggers. Select the added OR.
   ours=[Node('OR',next(n.value for n in allow if n.key=='OR' and any(c.key=='NOT' and 'tag' in str(c.value) for c in n.value)),'=')]
   self.assertFalse(eval_gate(ours,date=19550101),name)
   options=gate['requires_focus'] if isinstance(gate['requires_focus'],list) else [gate['requires_focus']]
   for choice in options:self.assertTrue(eval_gate(ours,done=[choice]+gate.get('requires_all_focus',[]),date=19360101),name)
   self.assertNotIn('date',[n.key for n in walk(ours)])
   self.assertTrue(eval_gate(ours,tag='GER',date=19360101),name)
 def test_localisation_covers_all_new_visible_keys(self):
  keys=set(self.nodes)|{k+'_desc' for k in self.nodes}
  ideas=get(get(read('common/ideas/waef_focus_programmes.txt'),'ideas'),'country')
  keys|={n.key for n in ideas}|{n.key+'_desc' for n in ideas}
  for rel in ['common/decisions/waef_focus_operations.txt','common/decisions/waef_armament_fatigue.txt']:
   for cat in read(rel):keys|={n.key for n in cat.value}|{n.key+'_desc' for n in cat.value}
  for rel in ['common/decisions/categories/waef_focus_operations.txt','common/dynamic_modifiers/waef_focus_operations.txt']:
   keys|={n.key for n in read(rel)}|{n.key+'_desc' for n in read(rel)}
  for n in walk(read('common/decisions/waef_focus_operations.txt')):
   if n.key in ['custom_effect_tooltip','custom_cost_text','tooltip']:keys.add(n.value)
  for lang in ['russian','english']:
   loc=localisation(lang)
   self.assertFalse(keys-loc.keys(),(lang,keys-loc.keys()))
   self.assertTrue(all(loc[k].strip() for k in keys))
 def test_repeating_fatigue_uses_one_timer_and_does_not_hook_law_changes(self):
  source=read('common/decisions/waef_armament_fatigue.txt');mission=get(get(source,'economy_fatigue'),'waef_armament_fatigue')
  self.assertEqual(get(mission,'days_mission_timeout'),'70')
  self.assertEqual(get(get(mission,'timeout_effect'),'economy_fatigue_level_up_1'),'yes')
  self.assertEqual(len([n for n in walk(mission) if n.key=='activate_mission']),1)
  effect=get(read('common/scripted_effects/waef_focus_effects.txt'),'waef_start_armament_fatigue')
  guard=get(get(get(effect,'if'),'limit'),'NOT');self.assertEqual(get(guard,'has_active_mission'),'waef_armament_fatigue')
  self.assertNotIn('waef_armament_fatigue',text('common/decisions/waef_economy_fatigue_laws.txt'))
 def test_operation_states_regions_and_forts_cover_the_map_once(self):
  targets=json.loads(text('docs/OPERATION_TARGETS.json'))
  states=[sid for ids in targets['state_regions'].values() for sid in ids]
  self.assertEqual(len(states),282);self.assertEqual(len(set(states)),282)
  self.assertEqual({str(x) for x in states},set(targets['fort_provinces']))
  for sid,pids in targets['fort_provinces'].items():self.assertTrue(1<=len(pids)<=3);self.assertEqual(len(pids),len(set(pids)))
 def test_operation_success_timeout_and_failure_all_cleanup(self):
  cat=get(read('common/decisions/waef_focus_operations.txt'),'waef_operations')
  for key in ['waef_local_offensive_21','waef_local_offensive_28','waef_regional_offensive_45','waef_regional_offensive_52']:
   mission=get(cat,key);self.assertIn('waef_operation_full_control',[n.key for n in walk(get(mission,'available'))])
   self.assertIn('waef_cleanup_operation',[n.key for n in walk(get(mission,'complete_effect'))])
   self.assertIn('waef_cleanup_operation',[n.key for n in walk(get(mission,'timeout_effect'))])
  effects=read('common/scripted_effects/waef_focus_operations.txt')
  for scale in ['local','regional']:
   self.assertEqual(get(get(effects,'waef_fail_'+scale+'_offensive'),'waef_cleanup_operation'),'yes')
  cleanup=get(effects,'waef_cleanup_operation')
  self.assertEqual(get(cleanup,'clear_array'),'waef_operation_states')
  self.assertEqual(get(cleanup,'clr_country_flag'),'waef_operation_in_progress')
 def test_no_unknown_experience_effect_or_fort_inflation(self):
  for p in (ROOT/'common/national_focus').glob('waef*'):
   self.assertNotRegex(p.read_text(),r'add_(army|air)_experience\s*=')
  ops=text('common/decisions/waef_focus_operations.txt')
  self.assertIn('level < 2',ops);self.assertNotIn('add_building_construction',ops)
  self.assertIn('cancel_effect = { clr_country_flag = waef_fortification_in_progress }',ops)
if __name__=='__main__':unittest.main()
