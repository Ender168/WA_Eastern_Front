"""User-visible choices, compact layout and conditional jet grants."""
import itertools,json,re,unittest
from test_national_focus_trees import ROOT,focus_nodes,localisation,eval_gate,read,baseline
from test_scenario_regressions import get,walk,Node,parse


def evaluate(nodes, done, dlcs):
    values=[]
    for n in nodes:
        if n.key=='has_dlc':values.append(n.value.strip('"') in dlcs)
        elif n.key=='OR':values.append(any(evaluate([c],done,dlcs) for c in n.value))
        elif n.key=='AND':values.append(evaluate(n.value,done,dlcs))
        elif n.key=='NOT':values.append(not evaluate(n.value,done,dlcs))
        else:values.append(eval_gate([n],done=done))
    return all(values)


def grants(nodes,done,dlcs):
    result=set()
    for n in nodes:
        if n.key=='if' and evaluate(get(n.value,'limit'),done,dlcs):
            result|=grants([c for c in n.value if c.key!='limit'],done,dlcs)
        elif n.key=='set_technology':result|={c.key for c in n.value if c.value=='1'}
    return result


class GermanRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())
        cls.rows={r['code']:r for r in cls.manifest['schools']['GER']}
        cls.nodes=focus_nodes()
        cls.jet_effect=get(read('common/scripted_effects/waef_focus_effects.txt'),'waef_grant_german_jet_aircraft')
        cls.catalogue=json.loads((ROOT/'docs/TECHNOLOGY_LOCALISATION_CATALOGUE.json').read_text())
        cls.air=baseline.technology_blocks((ROOT/'common/technologies/air_techs_ger.txt').read_text())

    def test_compact_layout_and_detached_industry(self):
        coords=[(int(get(self.nodes[r['id']],'x')),int(get(self.nodes[r['id']],'y'))) for r in self.rows.values()]
        self.assertEqual(min(x for x,y in coords),9)
        self.assertLessEqual(max(x for x,y in coords)-min(x for x,y in coords),17)
        self.assertLessEqual(max(y for x,y in coords),7)
        # Nonoverlapping coordinates are not enough: adjacent labels also need room.
        for y in {y for x,y in coords}:
            xs=sorted(x for x,row in coords if row==y)
            self.assertTrue(all(b-a>=2 for a,b in zip(xs,xs[1:])),(y,xs))
        for c,t in [('P1','concentrated_industry'),('P2','dispersed_industry')]:
            r=self.rows[c];self.assertEqual(r['days'],21);self.assertEqual(r['prerequisites'],[])
            self.assertEqual(r['technologies'],[t])
            self.assertTrue(any(x.key=='standard_industry' and x.value=='0'
                                for b in walk(get(self.nodes[r['id']],'completion_reward'))
                                if b.key=='set_technology' for x in b.value))

    def test_hidden_long_links_preserve_real_focus_requirements(self):
        for c in ['T1','H1','A1','W1','S1','B1','R1','C70','O2']:
            row=self.rows[c];node=self.nodes[row['id']]
            required=row['availability_requires']
            actual=[get(n.value,'focus') for n in node if n.key=='prerequisite']
            self.assertEqual(actual,row['display_prerequisites'])
            self.assertEqual(set(actual)|set(required),set(row['prerequisites']))
            self.assertFalse(eval_gate(get(node,'available'),done=[]))
            self.assertTrue(eval_gate(get(node,'available'),done=required))
            for missing in required:
                self.assertFalse(eval_gate(get(node,'available'),done=[f for f in required if f!=missing]))

    def test_only_two_tank_routes_with_identical_integrated_light_vehicles(self):
        self.assertFalse(any(c.startswith('L') for c in self.rows))
        for level in [1,2,3]:
            medium=set(self.rows['T'+str(level)]['technologies'])
            heavy=set(self.rows['H'+str(level)]['technologies'])
            shared=medium&heavy
            self.assertTrue(shared)
            self.assertTrue(all(any(s in t for s in ['light','scout','combat_armoured','armoured_car']) for t in shared))
            self.assertFalse(any('heavy' in t for t in medium))
            self.assertFalse(any('medium' in t or 'modern' in t for t in heavy))
            for prefix in ['T','H']:
                self.assertEqual(self.rows[prefix+str(level)]['prerequisites'],
                                 ['WAEF_GER_C00' if level==1 else 'WAEF_GER_'+prefix+str(level-1)])
        all_shared=set().union(*(set(self.rows['T'+str(i)]['technologies'])&set(self.rows['H'+str(i)]['technologies']) for i in [1,2,3]))
        self.assertTrue(any('light_tank' in t for t in all_shared))
        self.assertTrue(any('combat_armoured_car' in t for t in all_shared))
        self.assertEqual(self.rows['T1']['exclusive'],['WAEF_GER_H1'])
        self.assertIn('WAEF_GER_T1',self.rows['H1']['exclusive'])

    def test_motorisation_and_mechanisation_have_an_independent_three_stage_branch(self):
        self.assertEqual(self.rows['M1']['prerequisites'],['WAEF_GER_C00'])
        for i in [2,3]:self.assertEqual(self.rows['M'+str(i)]['prerequisites'],['WAEF_GER_M'+str(i-1)])
        mobile=set().union(*(set(self.rows['M'+str(i)]['technologies']) for i in [1,2,3]))
        self.assertTrue(any('mechanized_infantry' in t for t in mobile))
        for r in self.rows.values():
            if r['code'].startswith(('T','H')):self.assertFalse(mobile&set(r['technologies']))

    def test_three_strike_choices_share_only_other_first_packages_at_stage_three(self):
        basics={p:set(self.rows[p+'1']['technologies']) for p in ['S','B','R']}
        all_basics=set().union(*basics.values())
        for p in ['S','B','R']:
            self.assertEqual(set(self.rows[p+'1']['exclusive']),{f'WAEF_GER_{q}1' for q in ['S','B','R'] if q!=p})
            for q in ['S','B','R']:
                if p==q:continue
                alternative=basics[q]
                self.assertTrue(alternative)
                for i in [1,2]:self.assertFalse(set(self.rows[p+str(i)]['technologies'])&alternative)
                self.assertTrue(alternative<=set(self.rows[p+'3']['technologies']))
                advanced=(set(self.rows[q+'2']['technologies'])|set(self.rows[q+'3']['technologies']))-all_basics
                self.assertFalse(set(self.rows[p+'3']['technologies'])&advanced)
        # Both equipment modes must actually receive a basic strategic aircraft.
        self.assertIn('ger_strategic_bomber_1',basics['R'])
        self.assertIn('ger_strategic_bomber_ad_tech_1',basics['R'])

    def test_focke_wulf_fighters_exclude_messerschmitt_and_heavy_tanks(self):
        for a,b in [('W1','A1'),('W1','H1')]:
            self.assertIn('WAEF_GER_'+b,self.rows[a]['exclusive'])
            self.assertIn('WAEF_GER_'+a,self.rows[b]['exclusive'])
        for r in self.rows.values():
            for t in r['technologies']:
                model=self.catalogue[t]['english']
                if re.search(r'(?:Fw\s*190|Ta\s*152)',model):
                    self.assertIn(r['code'],['W1','W2','W3'],(r['code'],t,model))
                    self.assertEqual(self.manifest['research_gates'][t]['requires_focus'],['WAEF_GER_W1'])
                if re.search(r'Bf\s*109',model):self.assertIn(r['code'],['A1','A2','A3'])
        # Carrier Fw 190 technologies have no "multirole" in their IDs.
        self.assertIn('ger_cv_fighter_3',self.rows['W2']['technologies'])
        self.assertIn('ger_cv_fighter_5',self.rows['W3']['technologies'])

    def test_jet_grants_require_electronics_and_work_in_both_orders_and_dlc_modes(self):
        for c in ['C25','A3','W3','S3','B3','R3','U3']:
            self.assertEqual(get(get(self.nodes['WAEF_GER_'+c],'completion_reward'),'waef_grant_german_jet_aircraft'),'yes')
        for r in self.rows.values():self.assertFalse(any('_jet_' in t for t in r['technologies']))
        for dlcs in [set(),{'By Blood Alone'}, {'By Blood Alone','No Step Back'}]:
            designer='By Blood Alone' in dlcs
            for route in ['A3','B3','U3']:
                aircraft=set().union(*(set(e['technologies']) for e in self.manifest['german_jet_rewards'] if 'WAEF_GER_'+route in e['requires_any']))
                expected={t for t in aircraft if ('_ad_tech_' in t)==designer}
                self.assertTrue(expected)
                for order in itertools.permutations(['C25',route]):
                    done=set();awarded=set()
                    for step in order:
                        done.add('WAEF_GER_'+step)
                        awarded|=grants(self.jet_effect,done,dlcs)
                        if len(done)==1:self.assertFalse(awarded)
                    self.assertEqual(awarded,expected,(order,dlcs))
            # Focke-Wulf cannot receive or research Messerschmitt jet fighters.
            self.assertFalse(grants(self.jet_effect,{'WAEF_GER_C25','WAEF_GER_W3'},dlcs))
            # Finishing a strike alternative never awards the closed bomber jets.
            self.assertFalse(grants(self.jet_effect,{'WAEF_GER_C25','WAEF_GER_S3'},dlcs))
            self.assertFalse(grants(self.jet_effect,{'WAEF_GER_C25','WAEF_GER_R3'},dlcs))

    def test_all_jet_research_including_postwar_models_requires_finished_electronics(self):
        checked=[]
        for name,body in self.air.items():
            if '_jet_' not in name:continue
            gate=self.manifest['research_gates'][name]
            self.assertEqual(gate['requires_all_focus'],['WAEF_GER_C25'])
            allow=get(parse('allow = {'+baseline.named_blocks(body,'allow')[0]+'}'),'allow')
            ours=[Node('OR',next(n.value for n in allow if n.key=='OR' and any(c.key=='NOT' and 'tag' in str(c.value) for c in n.value)))]
            for route in gate['requires_focus']:
                self.assertFalse(eval_gate(ours,done=[route],date=19550101),name)
                self.assertTrue(eval_gate(ours,done=[route,'WAEF_GER_C25'],date=19360101),name)
            self.assertTrue(eval_gate(ours,tag='GER'),name)
            checked.append(name)
        self.assertGreater(len(checked),20)
        for name in ['ger_jet_fighter_multirole_1','ger_jet_fighter_multirole_ad_tech_1']:
            self.assertEqual(self.manifest['research_gates'][name]['requires_focus'],['WAEF_GER_A1'])
        for name in ['ger_jet_fighter_2','ger_jet_fighter_ad_tech_3']:
            self.assertEqual(self.manifest['research_gates'][name]['requires_focus'],['WAEF_GER_W1'])

    def test_all_reward_technology_names_and_screenshot_keys_are_localized(self):
        required={t for rs in self.manifest['schools'].values() for r in rs for t in r['technologies']}
        required|={t for entry in self.manifest['german_jet_rewards'] for t in entry['technologies']}
        required|={'ger_transport_plane_3','ger_attacker_ad_tech_3','ger_cas_ad_tech_4','ger_fast_bomber_ad_tech_3','ger_patrol_ad_tech_2','ger_strategic_bomber_ad_tech_1'}
        for lang in ['english','russian']:
            labels=localisation(lang);self.assertFalse(required-labels.keys())
            for t in required:self.assertNotRegex(labels[t],r'\$|_ad_tech_|_equipment_|^'+re.escape(t)+'$')
