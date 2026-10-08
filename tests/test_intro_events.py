import unittest
from pathlib import Path
from test_scenario_regressions import read, get, walk
ROOT=Path(__file__).resolve().parents[1]

class IntroEventTests(unittest.TestCase):
    def test_both_countries_receive_intro_once(self):
        startup=get(get(read('common/on_actions/waef_intro_on_actions.txt'),'on_actions'),'on_startup')
        effect=get(startup,'effect')
        for tag in ['WEF','EEF']:
            branch=get(get(effect,tag),'if')
            self.assertEqual(get(branch,'set_country_flag'),'waef_intro_shown')
            self.assertEqual(get(get(branch,'country_event'),'id'),'waef_intro.1')
            self.assertEqual(get(get(get(branch,'limit'),'NOT'),'has_country_flag'),'waef_intro_shown')
        self.assertNotIn('days',[n.key for n in walk(startup)])

    def test_read_opens_rules_skip_has_no_gameplay_effects(self):
        events=[n.value for n in read('events/waef_intro_events.txt') if n.key=='country_event']
        self.assertEqual(len(events),2)
        intro,rules=events
        self.assertEqual(get(intro,'id'),'waef_intro.1')
        options=[n.value for n in intro if n.key=='option']
        self.assertEqual(get(get(options[0],'country_event'),'id'),'waef_intro.2')
        self.assertEqual({n.key for n in options[1]},{'name','ai_chance'})
        self.assertEqual(get(rules,'id'),'waef_intro.2')
        self.assertEqual({n.key for n in get(rules,'option')},{'name'})
        for lang in ['russian','english']:
            content=(ROOT/'localisation'/lang/f'waef_intro_l_{lang}.yml').read_text(encoding='utf-8-sig')
            for node in [*walk(events[0]), *walk(events[1])]:
                if node.key in ['title','desc','name']:
                    self.assertIn(node.value+':0',content)
