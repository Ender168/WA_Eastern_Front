"""German playtest rules applied to the six other national schools."""
import json,unittest
from test_national_focus_trees import ROOT,focus_nodes,eval_gate
from test_scenario_regressions import get

class NationalRevisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text());cls.nodes=focus_nodes()

 def test_all_schools_have_short_entry_industry_choices_and_four_infantry_stages(self):
  for code,records in self.m['schools'].items():
   r={x['code']:x for x in records}
   self.assertEqual(r['C00']['days'],14)
   for n,tech,other in [('P1','concentrated_industry','P2'),('P2','dispersed_industry','P1')]:
    self.assertEqual(r[n]['days'],21);self.assertEqual(r[n]['technologies'],[tech])
    self.assertEqual(r[n]['exclusive'],['WAEF_'+code+'_'+other]);self.assertFalse(r[n]['prerequisites'])
   for n,year in [('I1',1941),('I2',1943),('I3',1944),('I4',1945)]:
    self.assertEqual(r[n]['year'],year);self.assertTrue(r[n]['technologies'])
   for n in ('T4','H4'):self.assertTrue(r[n]['technologies'])
   self.assertEqual(r['T1']['exclusive'],['WAEF_'+code+'_H1'])
   self.assertIn('WAEF_'+code+'_T1',r['H1']['exclusive'])

 def test_jet_routes_need_both_own_stage_three_and_completed_electronics(self):
  for code,records in self.m['schools'].items():
   r={x['code']:x for x in records}
   for p in ('A','W','S','B','R'):
    stage=r[p+'4'];self.assertEqual(stage['days'],7);self.assertTrue(stage['technologies'])
    deps=['WAEF_'+code+'_'+p+'3','WAEF_'+code+'_C25']
    self.assertEqual(stage['prerequisites'],deps)
    prerequisites=[get(n.value,'focus') for n in self.nodes[stage['id']] if n.key=='prerequisite']
    self.assertEqual(prerequisites,deps)
    for tech in stage['technologies']:
     gate=self.m['research_gates'][tech]
     self.assertIn(stage['id'],gate['requires_focus']);self.assertEqual(gate['requires_all_focus'],[deps[1]])
   self.assertFalse(any(t.startswith(code.lower()+'_') and 'jet' in t for x in records if x['code'] not in ('A4','W4','S4','B4','R4') for t in x['technologies']))

 def test_late_national_tanks_are_in_fourth_stage_and_not_researchable_early(self):
  for code,records in self.m['schools'].items():
   if code=='GER':continue
   r={x['code']:x for x in records}
   for p in ('T','H'):
    for stage in range(1,4):
     self.assertFalse(any('super_heavy' in t for t in r[p+str(stage)]['technologies']))
    for tech in r[p+'4']['technologies']:
     if any(x in tech for x in ('light','scout','combat_car','armoured_car')):continue
     self.assertEqual(self.m['research_gates'][tech]['requires_focus'],['WAEF_'+code+'_'+p+'4'])

 def test_third_strike_stage_grants_other_first_stage_packages(self):
  for code,records in self.m['schools'].items():
   r={x['code']:x for x in records}
   for p in ('S','B','R'):
    self.assertEqual(set(r[p+'1']['exclusive']),{'WAEF_'+code+'_'+q+'1' for q in ('S','B','R') if q!=p})
    for q in ('S','B','R'):
     if q!=p:self.assertTrue(set(r[q+'1']['technologies'])<=set(r[p+'3']['technologies']))

 def test_shared_light_armour_and_recon_and_separate_motorisation(self):
  for code,records in self.m['schools'].items():
   r={x['code']:x for x in records}
   for n in range(1,4):
    a=set(r['T'+str(n)]['technologies']);b=set(r['H'+str(n)]['technologies'])
    for t in a|b:
     if any(x in t for x in ('light','scout','combat_car','armoured_car')):self.assertIn(t,a&b)
    a=set(r['A'+str(n)]['technologies']);b=set(r['W'+str(n)]['technologies'])
    for t in a|b:
     if 'scout_plane' in t or 'transport_plane' in t:self.assertIn(t,a&b)
   for x in records:
    if x['code'].startswith(('T','H')):self.assertFalse(any(any(s in t for s in ('mechanized','motorised','motorized','amphibious')) for t in x['technologies']))
   if code!='GER':self.assertEqual(r['H1']['exclusive'],['WAEF_'+code+'_T1'])

if __name__=='__main__':unittest.main()
