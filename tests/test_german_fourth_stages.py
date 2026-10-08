"""Coverage and redistribution checks for the fourth-stage playtest revision."""
import json,unittest
from test_national_focus_trees import ROOT,focus_nodes,localisation,baseline
from test_scenario_regressions import get

class FourthStageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())
  cls.rows={r['code']:r for r in cls.m['schools']['GER']};cls.nodes=focus_nodes()
  cls.tech={}
  for path in (ROOT/'common/technologies').glob('*.txt'):
   for n,b in baseline.technology_blocks(path.read_text()).items():cls.tech[n]=baseline.parse_tech(n,str(path),b)

 def test_all_focus_description_redundancy_is_removed(self):
  for lang in ['russian','english']:
   loc=localisation(lang)
   for fid in self.nodes:self.assertEqual(loc[fid+'_desc'],'',fid)

 def test_auxiliary_branch_removed_and_support_aircraft_are_preserved(self):
  self.assertFalse(any(c.startswith('U') for c in self.rows))
  for i in [1,2,3]:
   a=set(self.rows['A'+str(i)]['technologies']);w=set(self.rows['W'+str(i)]['technologies'])
   for t in a|w:
    if 'scout_plane' in t or 'transport_plane' in t or t=='ger_air_upgrade_1':self.assertIn(t,a&w)
  for t in ['ger_scout_plane_3','ger_scout_plane_ad_tech_3']:
   self.assertIn(t,self.rows['A1']['technologies']);self.assertIn(t,self.rows['W1']['technologies'])
  self.assertIn('ger_heavy_fighter_ad_tech_2',self.rows['A2']['technologies'])
  self.assertIn('ger_heavy_fighter_ad_tech_conversion_2',self.rows['B2']['technologies'])
  for gate in self.m['research_gates'].values():self.assertNotIn('WAEF_GER_U',str(gate))

 def test_late_tanks_are_exclusively_in_fourth_stage(self):
  groups={'T4':{'ger_modern_2','ger_modern_3','ger_modern_4','ger_modern_tank_chassis_1_2','ger_modern_tank_chassis_1_3','ger_modern_tank_chassis_2','ger_modern_tank_1_td'},
          'H4':{'ger_super_heavy_1','ger_super_heavy_tank_chassis_1','ger_heavy_tank_chassis_5','ger_landkruiser_1','ger_landkruiser_tank_chassis_1','ger_heavy_assault_tank_4_spg'}}
  for target,ids in groups.items():
   self.assertTrue(ids<=set(self.rows[target]['technologies']))
   for c,r in self.rows.items():
    if c!=target:self.assertFalse(ids&set(r['technologies']),(target,c))
   for t in ids:self.assertEqual(self.m['research_gates'][t]['requires_focus'],['WAEF_GER_'+target])
  self.assertIn('ger_modern_1',self.rows['T2']['technologies'])
  self.assertIn('ger_heavy_tank_chassis_4',self.rows['H3']['technologies'])

 def test_infantry_late_years_are_split_without_loss(self):
  self.assertEqual(self.rows['I4']['prerequisites'],['WAEF_GER_I3'])
  for c,year in [('I3',1944),('I4',1945)]:
   self.assertTrue(self.rows[c]['technologies'])
   self.assertEqual({self.tech[t].year for t in self.rows[c]['technologies']},{year})
  self.assertIn('ger_heavy_infantry_weapons_6',self.rows['I3']['technologies'])
  self.assertIn('ger_infantry_weapons_7',self.rows['I4']['technologies'])
  self.assertIn('ger_heavy_infantry_weapons_7',self.rows['I4']['technologies'])
