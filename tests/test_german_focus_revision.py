"""User-visible choices and reward localization from the German playtest."""
import json,re,unittest
from test_national_focus_trees import ROOT,focus_nodes,localisation
from test_scenario_regressions import get,walk
class GermanRevisionTests(unittest.TestCase):
 def setUp(self):
  self.rows={r['code']:r for r in json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())['schools']['GER']}
  self.nodes=focus_nodes()
 def test_compact_layout_and_detached_industry(self):
  coords=[int(get(self.nodes[r['id']],'x')) for r in self.rows.values()]
  self.assertLessEqual(max(coords)-min(coords),24)
  for c,t in [('P1','concentrated_industry'),('P2','dispersed_industry')]:
   r=self.rows[c];self.assertEqual(r['days'],21);self.assertEqual(r['prerequisites'],[])
   self.assertEqual(r['technologies'],[t])
   n=self.nodes[r['id']]
   self.assertTrue(any(x.key=='standard_industry' and x.value=='0' for b in walk(get(n,'completion_reward')) if b.key=='set_technology' for x in b.value))
 def test_tank_routes_share_light_cars_but_exclude_medium_heavy(self):
  light=set().union(*(set(self.rows['L'+str(i)]['technologies']) for i in [1,2,3]))
  self.assertTrue(any('light_tank' in t for t in light))
  self.assertTrue(any('combat_car' in t or 'scout' in t for t in light))
  self.assertEqual(self.rows['T1']['exclusive'],['WAEF_GER_H1'])
  self.assertEqual(self.rows['H1']['exclusive'],['WAEF_GER_T1'])
  for prefix in ['T','H']:
   for i in [1,2,3]:
    ts=self.rows[prefix+str(i)]['technologies']
    self.assertFalse(any('heavy' in t for t in ts) if prefix=='T' else any('medium_tank' in t for t in ts))
 def test_three_air_choices_and_exact_strategic_basics(self):
  baseline=set(self.rows['S1']['technologies'])|set(self.rows['B1']['technologies'])
  all_strike=set().union(*(set(self.rows[p+str(i)]['technologies']) for p in ['S','B'] for i in [1,2,3]))
  for p in ['S','B','R']:
   self.assertEqual(set(self.rows[p+'1']['exclusive']),{f'WAEF_GER_{q}1' for q in ['S','B','R'] if q!=p})
  for i in [1,2,3]:self.assertEqual(set(self.rows['R'+str(i)]['technologies'])&all_strike,baseline)
 def test_all_reward_technology_names_and_screenshot_keys_are_localized(self):
  m=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())
  required={t for rs in m['schools'].values() for r in rs for t in r['technologies']}
  required|={'ger_transport_plane_3','ger_attacker_ad_tech_3','ger_cas_ad_tech_4','ger_fast_bomber_ad_tech_3','ger_patrol_ad_tech_2','ger_strategic_bomber_ad_tech_1'}
  for lang in ['english','russian']:
   labels=localisation(lang);self.assertFalse(required-labels.keys())
   for t in required:self.assertNotRegex(labels[t],r'\$|_ad_tech_|_equipment_|^'+re.escape(t)+'$')
