import json
import unittest
from pathlib import Path
from test_scenario_regressions import parse, get, walk
ROOT = Path(__file__).resolve().parents[1]
def read(path): return parse((ROOT/path).read_text(encoding='utf-8-sig'))

class OperationsRuntimeTests(unittest.TestCase):
    def test_tactical_targets_meet_seven_province_threshold(self):
        audit=json.loads((ROOT/'docs/OPERATIONS_MAP_AUDIT.json').read_text())
        decision=get(get(read('common/decisions/waef_focus_operations.txt'),'waef_tactical_operations'),'waef_local_offensive')
        actual={int(n.key) for n in get(decision,'targets')}
        expected={int(sid) for sid,data in audit['states'].items() if len(data['provinces'])>=7}
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),187)
        for sid in [188,1000,73]: self.assertNotIn(sid,actual)

    def test_offensives_have_no_war_gate_cooldown_or_partial_highlight(self):
        cats=read('common/decisions/waef_focus_operations.txt')
        for key in ['waef_tactical_operations','waef_strategic_operations']:
            nodes=list(walk(get(cats,key)))
            self.assertNotIn('has_war',[n.key for n in nodes])
            self.assertNotIn('has_war_with',[n.key for n in nodes])
            self.assertNotIn('add_war_support',[n.key for n in nodes])
            self.assertFalse(any('cooldown' in str(n.value) for n in nodes))
        nodes=list(walk(get(cats,'waef_strategic_operations')))
        self.assertNotIn('highlight_states',[n.key for n in nodes])
        self.assertNotIn('on_map_mode',[n.key for n in nodes])

    def test_fatigue_timer_and_victory_stop_all_missions(self):
        cats=read('common/decisions/waef_focus_operations.txt')
        for scale,cat in [('local','waef_tactical_operations'),('regional','waef_strategic_operations')]:
            key=f'waef_{scale}_operation_fatigue'
            mission=get(get(cats,cat),key)
            self.assertEqual(get(mission,'days_mission_timeout'),'7' if scale=='local' else '10')
            timeout=list(walk(get(mission,'timeout_effect')))
            self.assertIn('waef_win_operation',[n.key for n in timeout])
            self.assertIn('waef_charge_offensive_fatigue',[n.key for n in timeout])
            self.assertIn(key,[n.value for n in timeout if n.key=='activate_mission'])
        effects=read('common/scripted_effects/waef_focus_operations.txt')
        cleanup=get(effects,'waef_cleanup_operation')
        removed=[n.value for n in cleanup if n.key=='remove_mission']
        self.assertEqual(len(removed),6)
        self.assertEqual(get(get(effects,'waef_win_operation'),'waef_cleanup_operation'),'yes')
        self.assertEqual(get(get(effects,'waef_charge_offensive_fatigue'),'economy_fatigue_level_up_1'),'yes')
        daily=read('common/on_actions/waef_doctrine_on_actions.txt')
        for tag in ['WEF','EEF']:
            self.assertEqual(get(get(get(daily,'on_actions'),'on_daily_'+tag)[0].value,'waef_check_operation_victory'),'yes')

    def test_test_war_has_no_date_gate_or_extra_bonus(self):
        decision=get(get(read('common/decisions/waef_war_setup.txt'),'waef_war_setup'),'waef_test_declare_war')
        nodes=list(walk(decision))
        self.assertNotIn('date',[n.key for n in nodes])
        self.assertNotIn('add_timed_idea',[n.key for n in nodes])
        self.assertEqual({n.value for n in nodes if n.key=='target'},{'WEF','EEF'})
        self.assertEqual(get(decision,'cost'),'0')

    def test_region_province_list_is_hidden_behind_one_tooltip(self):
        cats=read('common/decisions/waef_focus_operations.txt')
        for decision in get(cats,'waef_strategic_operations'):
            if get(decision.value,'custom_cost_text') != 'waef_regional_cost_tt':
                continue
            available=get(decision.value,'available')
            tooltip=get(available,'custom_trigger_tooltip')
            self.assertEqual(get(tooltip,'tooltip'),'waef_enemy_region_majority_tt')
            self.assertTrue(any(n.key.startswith('waef_enemy_majority_region_') for n in tooltip))
            self.assertFalse(any(n.key.startswith('waef_enemy_majority_region_') for n in available))

    def test_unavailable_and_rear_regions_are_hidden(self):
        cats=read('common/decisions/waef_focus_operations.txt')
        triggers=read('common/scripted_triggers/waef_focus_operations.txt')
        for decision in get(cats,'waef_strategic_operations'):
            if get(decision.value,'custom_cost_text') != 'waef_regional_cost_tt':
                continue
            rid=decision.key.rsplit('_',1)[1]
            visible=get(decision.value,'visible')
            self.assertEqual(get(visible,'command_power'),'49')
            self.assertEqual(get(visible,'has_political_power'),'49')
            self.assertEqual(get(visible,'waef_enemy_majority_region_'+rid),'yes')
            self.assertEqual(get(visible,'waef_frontline_region_'+rid),'yes')
            self.assertIn('waef_operation_in_progress',[n.value for n in walk(visible) if n.key=='has_country_flag'])
            frontline=get(triggers,'waef_frontline_region_'+rid)
            for target in get(frontline,'OR'):
                self.assertEqual(get(get(target.value,'ROOT'),'waef_enemy_in_state_'+target.key),'yes')
                self.assertEqual(get(get(target.value,'any_neighbor_state'),'is_controlled_by'),'ROOT')
