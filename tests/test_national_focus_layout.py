"""Reviewed compact national layouts and approved content snapshots."""
import dataclasses,hashlib,json,unittest
from test_national_focus_trees import ROOT,focus_nodes,eval_gate
from test_scenario_regressions import get

class NationalLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())
        cls.lock=json.loads((ROOT/'docs/NATIONAL_FOCUS_CONTENT_LOCK.json').read_text())
        cls.nodes=focus_nodes()

    def test_other_school_contents_match_the_reviewed_revision(self):
        self.assertEqual(set(self.lock['schools']),{'SOV','USA','ENG','FRA','ITA','JAP'})
        for code,expected in self.lock['schools'].items():
            content=[{k:r[k] for k in self.lock['fields']} for r in self.m['schools'][code]]
            actual=hashlib.sha256(json.dumps(content,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
            self.assertEqual(actual,expected,code)
            rewards={r['id']:get(self.nodes[r['id']],'completion_reward') for r in self.m['schools'][code]}
            digest=hashlib.sha256(json.dumps(rewards,sort_keys=True,ensure_ascii=False,default=dataclasses.asdict,separators=(',',':')).encode()).hexdigest()
            self.assertEqual(digest,self.lock['reward_ast'][code],code)

    def test_all_schools_use_the_same_common_positions_and_compact_extent(self):
        ref={r['code']:self.nodes[r['id']] for r in self.m['schools']['GER']}
        for code,rows in self.m['schools'].items():
            coords=[]
            for r in rows:
                node=self.nodes[r['id']];x,y=int(get(node,'x')),int(get(node,'y'));coords.append((x,y))
                if r['code'].startswith('C') or r['code']=='O2':
                    self.assertEqual((x,y),(int(get(ref[r['code']],'x')),int(get(ref[r['code']],'y'))))
            self.assertEqual(min(x for x,y in coords),9)
            self.assertLessEqual(max(x for x,y in coords),26)
            self.assertLessEqual(max(y for x,y in coords),8)
            for y in {y for x,y in coords}:
                xs=sorted(x for x,row in coords if row==y)
                self.assertTrue(all(b-a>=2 for a,b in zip(xs,xs[1:])),(code,y,xs))

    def test_display_link_changes_preserve_all_dependency_conditions(self):
        for code,rows in self.m['schools'].items():
            for r in rows:
                node=self.nodes[r['id']]
                visible=[get(n.value,'focus') for n in node if n.key=='prerequisite']
                required=r['availability_requires']
                self.assertEqual(visible,r['display_prerequisites'])
                self.assertEqual(set(visible)|set(required),set(r['prerequisites']),(code,r['code']))
                self.assertTrue(eval_gate(get(node,'available'),done=required))
                for missing in required:
                    self.assertFalse(eval_gate(get(node,'available'),done=[f for f in required if f!=missing]))
