"""Specific playtest requirements from the user's national schedule document."""
import json,re,unittest
from test_national_focus_trees import ROOT,focus_nodes,eval_gate,baseline
from test_scenario_regressions import get,read,walk

class NationalRevisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text());cls.nodes=focus_nodes()
  cls.rows={c:{r['code']:r for r in rs} for c,rs in cls.m['schools'].items()}

 def test_document_year_schedules_and_motorisation_duration(self):
  expected={'FRA':{'I':[1942,1944,1946,1950],'G':[1941,1943,1945,1948]},
   'ITA':{'I':[1941,1943,1945,1947],'G':[1941,1943,1945,1948]},
   'JAP':{'I':[1942,1944,1946],'G':[1942,1944,1946,1949]},
   'SOV':{'I':[1942,1944,1946,1947,1949,1950],'G':[1943,1945,1947,1948]},
   'ENG':{'I':[1942,1944,1947,1949],'G':[1942,1944,1946,1948]},
   'USA':{'I':[1942,1944,1945,1948,1950],'G':[1942,1944,1946,1948]}}
  for c,groups in expected.items():
   r=self.rows[c];self.assertEqual(r['C00']['days'],14)
   for p,years in groups.items():
    actual=[x['year'] for n,x in r.items() if re.fullmatch(p+r'\d+',n)]
    self.assertEqual(actual,years,c)
   motor=[x for n,x in r.items() if re.fullmatch(r'M\d+',n)]
   if c in ('SOV','ENG'):self.assertFalse(motor)
   else:self.assertEqual([x['days'] for x in motor],[42]*3)

 def test_exact_tank_models_and_shared_auxiliary_vehicles(self):
  checks={'FRA':{'T1':['fra_medium_4'],'T2':['fra_medium_5','fra_medium_6','fra_medium_7'],'T3':['fra_modern_1','fra_modern_4'],'T4':['fra_modern_2'],'T5':['fra_modern_3']},
   'ITA':{'T1':['ita_medium_4','ita_light_4'],'T2':['ita_medium_5','ita_modern_1','ita_light_5'],'T3':['ita_medium_6','ita_modern_2','ita_light_6'],'T4':['ita_modern_3','ita_light_7'],'T5':['ita_modern_4'],
          'H1':['ita_heavy_1','ita_light_4'],'H2':['ita_heavy_2','ita_light_5'],'H3':['ita_heavy_3','ita_light_6'],'H4':['ita_heavy_4','ita_light_7']},
   'JAP':{'T1':['jap_medium_6','jap_medium_7'],'T2':['jap_medium_8','jap_medium_9'],'T3':['jap_modern_1'],'T4':['jap_modern_2'],'T5':['jap_modern_3'],
          'H1':['jap_super_heavy_2','jap_light_5'],'H2':['jap_heavy_3','jap_light_6'],'H3':['jap_super_heavy_3','jap_light_7']},
   'SOV':{'T3':['sov_medium_6','sov_medium_8','sov_light_6'],'T4':['sov_modern_1'],'T5':['sov_modern_2'],'H7':['sov_heavy_10'],'H8':['sov_heavy_11']},
   'ENG':{'T1':['eng_medium_5'],'T2':['eng_medium_6'],'T3':['eng_medium_7'],'T4':['eng_medium_8'],'T5':['eng_modern_1'],'T6':['eng_modern_2'],
          'H1':['eng_heavy_4'],'H2':['eng_heavy_5','eng_super_heavy_1'],'H3':['eng_heavy_6'],'H4':['eng_heavy_8'],'H5':['eng_heavy_9']},
   'USA':{'T1':['usa_medium_3'],'T2':['usa_medium_4','usa_medium_6','usa_medium_7'],'T3':['usa_medium_5','usa_modern_1'],'T4':['usa_modern_2'],'T5':['usa_modern_3','usa_modern_4'],
          'H1':['usa_heavy_1'],'H2':['usa_heavy_2','usa_heavy_3'],'H3':['usa_heavy_4']}}
  for c,stages in checks.items():
   for stage,ids in stages.items():self.assertTrue(set(ids)<=set(self.rows[c][stage]['technologies']),(c,stage,ids))
  self.assertNotIn('sov_modern_1',self.rows['SOV']['T3']['technologies'])
  self.assertFalse(any('light' in n or 'armoured_car' in n for n in self.rows['ITA']['T5']['technologies']))
  for c in ('SOV','ENG'):
   for p in ('T','H'):
    ids={t for n,r in self.rows[c].items() if n.startswith(p) for t in r['technologies']}
    self.assertTrue(any('mechanized' in t for t in ids),(c,p))

 def test_startup_requests_and_withdrawn_starting_aircraft(self):
  starts=self.m['start_exceptions']
  self.assertTrue({'ita_medium_3','ita_medium_tank_chassis_3'}<=set(starts['ITA']))
  self.assertFalse({'ita_fighter_4','ita_interceptor_ad_tech_2'}&set(starts['ITA']))
  self.assertTrue({'jap_medium_4','jap_super_heavy_1'}<=set(starts['JAP']))
  self.assertTrue({'sov_fighter_multirole_5','sov_fighter_3','sov_attacker_1','sov_strike_bomber_3'}<=set(starts['SOV']))
  for c in ('SOV','ENG','USA'):
   inventory={}
   for n,b in baseline.technology_blocks((ROOT/f'common/technologies/artillery_{c.lower()}.txt').read_text()).items():inventory[n]=baseline.parse_tech(n,'',b)
   self.assertTrue({n for n,t in inventory.items() if t.year==1941}<=set(starts[c]))
  for c in ('ITA','JAP','SOV','ENG','USA'):
   rewards={t for r in self.rows[c].values() for t in r['technologies']}
   self.assertFalse(rewards&set(starts.get(c,())))
  source=(ROOT/'common/scripted_effects/waef_1940_tech_baseline.txt').read_text()
  for n in ('eng_fighter_multirole_2','eng_fighter_multirole_ad_tech_2'):self.assertNotRegex(source,rf'\b{n}\s*=\s*1')
  self.assertIn('eng_fighter_multirole_2',self.rows['ENG']['W1']['technologies'])
  self.assertIn('ita_fighter_4',self.rows['ITA']['A1']['technologies'])

 def test_french_exceptions_and_electronics_requirements_without_diagonal_links(self):
  r=self.rows['FRA'];self.assertIn('fra_fast_bomber_ad_tech_3',r['B1']['technologies'])
  self.assertIn('fra_fighter_7',r['A4']['technologies']);self.assertIn('fra_fighter_multirole_ad_tech_6',r['W4']['technologies'])
  for c,boundary in {'FRA':4,'ITA':5,'JAP':4,'SOV':4,'ENG':4,'USA':4}.items():
   for n,r in self.rows[c].items():
    if not re.fullmatch(r'[AWSBR]\d+',n):continue
    node=self.nodes[r['id']];visible=[get(x.value,'focus') for x in node if x.key=='prerequisite']
    self.assertNotIn('WAEF_'+c+'_C25',visible);self.assertNotIn('WAEF_'+c+'_C00',visible)
    if int(n[1:])>=boundary:self.assertIn('WAEF_'+c+'_C25',r['availability_requires'])
    for tech in r['technologies']:
     if 'jet' in tech:
      self.assertEqual(self.m['research_gates'][tech]['requires_all_focus'],['WAEF_'+c+'_C25'])
      self.assertIn('WAEF_'+c+'_C25',r['availability_requires'])

 def test_programme_modifiers_removed_and_strike_cross_grants_preserved(self):
  for c,rows in self.rows.items():
   if c=='GER':continue
   for n,r in rows.items():
    if re.fullmatch(r'[THAWSBR]\d+',n):
     self.assertFalse(any(e.startswith('add_ideas') or e=='waef_start_armament_fatigue = yes' for e in r['effects']))
   for p in ('S','B','R'):
    for q in ('S','B','R'):
     if p!=q:self.assertTrue(set(rows[q+'1']['technologies'])<=set(rows[p+'3']['technologies']))

if __name__=='__main__':unittest.main()
