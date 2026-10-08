"""Timed scenario spirits and their expiry/replacement contract."""
from datetime import date, timedelta
from pathlib import Path
import unittest
from test_scenario_regressions import read, get, walk, execute

ROOT = Path(__file__).resolve().parents[1]
AIRCRAFT = set('transport_plane_equipment small_fighter_airframe cv_small_fighter_airframe small_fighter_multirole_airframe small_fighter_interceptor_airframe small_bomber_airframe cv_small_bomber_airframe medium_fighter_multirole_airframe fast_bomber_airframe medium_bomber_airframe medium_heavy_bomber_airframe large_bomber_airframe large_heavy_bomber_airframe small_naval_bomber_airframe cv_small_naval_bomber_airframe medium_fighter_airframe medium_scout_airframe large_maritime_patrol_airframe suicide_craft_equipment'.split())

class ScenarioSpiritTests(unittest.TestCase):
    def test_both_sides_receive_identical_spirits_and_expiry_dates(self):
        for tag, name in [('WEF', 'Western'), ('EEF', 'Eastern')]:
            history = read(f'history/countries/{tag} - {name} Front.txt')
            self.assertEqual(sum(n.key == 'add_ideas' and n.value == 'waef_unyielding_resistance' for n in history), 1)
            timed = {get(n.value, 'idea'): int(get(n.value, 'days')) for n in history if n.key == 'add_timed_idea'}
            self.assertEqual(date(1941, 1, 1) + timedelta(days=timed['waef_initial_production_drive']), date(1941, 7, 1))
            self.assertEqual(date(1941, 1, 1) + timedelta(days=timed['waef_initial_doctrine_window']), date(1941, 1, 30))
            self.assertFalse(any(n.key == 'add_ideas' and n.value == 'waef_initial_doctrine_window' for n in history))

    def test_exact_modifiers_and_aircraft_coverage(self):
        ideas = get(get(read('common/ideas/waef_scenario_ideas.txt'), 'ideas'), 'country')
        self.assertEqual(float(get(get(get(ideas, 'waef_unyielding_resistance'), 'modifier'), 'surrender_limit')), 1.0)
        spirit = get(ideas, 'waef_initial_production_drive')
        self.assertEqual(float(get(get(spirit, 'modifier'), 'production_factory_efficiency_gain_factor')), .8)
        bonuses = get(spirit, 'equipment_bonus')
        self.assertEqual({n.key for n in bonuses}, AIRCRAFT)
        for n in bonuses:
            self.assertEqual(get(n.value, 'instant'), 'yes')
            self.assertEqual(float(get(n.value, 'build_cost_ic')), -.2)

    def test_expiry_retains_restrictions_and_daily_fallback_is_timer_independent(self):
        ideas = get(get(read('common/ideas/waef_doctrine_ideas.txt'), 'ideas'), 'country')
        execute(get(get(ideas, 'waef_initial_doctrine_window'), 'on_remove'), current := set())
        self.assertEqual(current, {'waef_naval_doctrine_lock'})
        lock = get(get(ideas, 'waef_naval_doctrine_lock'), 'modifier')
        self.assertEqual(float(get(lock, 'naval_doctrine_cost_factor')), 10)
        self.assertEqual(float(get(lock, 'production_speed_dockyard_factor')), -10)
        actions = get(read('common/on_actions/waef_doctrine_on_actions.txt'), 'on_actions')
        for tag in ('WEF', 'EEF'):
            checks = [n.value for n in get(get(actions, 'on_daily_'+tag), 'effect') if n.key == 'if']
            self.assertEqual(len(checks), 1)
            limit = get(checks[0], 'limit')
            self.assertEqual(get(limit, 'date'), '1941.1.29')
            self.assertEqual(get(get(limit, 'NOT'), 'has_idea'), 'waef_naval_doctrine_lock')
            self.assertFalse(any(n.key == 'has_idea' and n.value == 'waef_initial_doctrine_window' for n in walk(limit)))

    def test_permanent_research_boost_for_both_sides(self):
        ideas = get(get(read('common/ideas/waef_scenario_ideas.txt'), 'ideas'), 'country')
        self.assertEqual(float(get(get(get(ideas, 'waef_accelerated_research'), 'modifier'), 'research_speed_factor')), -10.0)
        for tag, name in [('WEF', 'Western'), ('EEF', 'Eastern')]:
            history = read(f'history/countries/{tag} - {name} Front.txt')
            self.assertEqual(sum(n.key == 'add_ideas' and n.value == 'waef_accelerated_research' for n in history), 1)

    def test_player_buildings_and_all_category_slots(self):
        for p in (ROOT/'history/states').glob('*.txt'):
            state = get(read(p.relative_to(ROOT)), 'state')
            history = get(state, 'history')
            buildings = get(history, 'buildings')
            if get(history, 'owner') in ('WEF', 'EEF'):
                self.assertEqual(get(buildings, 'hydro_aluminium_refinery'), '1', p.name)
                self.assertEqual(get(buildings, 'industrial_complex'), '3', p.name)
            else:
                self.assertIsNone(get(buildings, 'industrial_complex'), p.name)
        for p in (ROOT/'common/state_category').glob('*.txt'):
            slots = [n.value for n in walk(read(p.relative_to(ROOT))) if n.key == 'local_building_slots']
            self.assertEqual(slots, ['20'], p.name)

    def test_localisation_for_both_languages(self):
        for lang in ('english', 'russian'):
            text = (ROOT/f'localisation/{lang}/waef_l_{lang}.yml').read_text(encoding='utf-8-sig')
            for key in ('waef_unyielding_resistance', 'waef_initial_production_drive', 'waef_accelerated_research'):
                for suffix in ('', '_desc'):
                    self.assertEqual(text.count(f' {key}{suffix}:0 '), 1)

if __name__ == '__main__':
    unittest.main()
