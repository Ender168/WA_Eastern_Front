"""Behavioral regressions for the main-branch review fixes."""
import unittest
from test_scenario_regressions import read, get, walk
from test_national_focus_trees import focus_nodes


def matches(nodes, flags=(), ideas=(), aat=False, resources=None):
    resources = resources or {}
    def match(n):
        if n.key == 'NOT': return not matches(n.value, flags, ideas, aat, resources)
        if n.key == 'AND': return matches(n.value, flags, ideas, aat, resources)
        if n.key == 'OR': return any(matches([c], flags, ideas, aat, resources) for c in n.value)
        if n.key == 'has_country_flag': return n.value in flags
        if n.key == 'has_idea': return n.value in ideas
        if n.key == 'has_dlc': return aat
        if n.key in ('command_power', 'has_political_power'):
            assert n.op == '<'
            return resources[n.key] < float(n.value)
        raise AssertionError(n.key)
    return all(match(n) for n in nodes)


def run(nodes, flags, ideas, techs, aat=False):
    taken = False
    for n in nodes:
        if n.key in ('if', 'else_if'):
            allowed = n.key == 'if' or not taken
            if allowed and matches(get(n.value, 'limit'), flags, ideas, aat):
                run([c for c in n.value if c.key != 'limit'], flags, ideas, techs, aat)
                taken = True
            elif n.key == 'if': taken = False
        elif n.key == 'set_country_flag': flags.add(n.value)
        elif n.key == 'add_ideas': ideas.add(n.value)
        elif n.key == 'set_technology':
            for t in n.value:
                (techs.add if t.value == '1' else techs.discard)(t.key)
        elif n.key == 'waef_sync_production_line':
            run(get(read('common/scripted_effects/waef_focus_effects.txt'), n.key), flags, ideas, techs, aat)
        else: raise AssertionError(n.key)


class ReviewFixTests(unittest.TestCase):
    def test_dead_operational_focus_removed_only_from_affected_schools(self):
        nodes = focus_nodes()
        for school in ('GER', 'SOV', 'USA', 'ITA', 'JAP'):
            self.assertNotIn('WAEF_'+school+'_O2', nodes)
        for school in ('ENG', 'FRA'):
            self.assertIn('WAEF_'+school+'_O2', nodes)

    def test_industry_choice_in_both_completion_orders_and_dlc_modes(self):
        nodes = focus_nodes()
        for school in ('GER', 'SOV', 'USA', 'ITA', 'JAP', 'ENG', 'FRA'):
            for choice, wanted, other in [('C41', 'streamlined_line_comp', 'flexible_line_comp'), ('C42', 'flexible_line_comp', 'streamlined_line_comp')]:
                for order in [('C15', choice), (choice, 'C15')]:
                    for aat in (False, True):
                        flags, ideas, techs = set(), set(), set()
                        for index, node in enumerate(order):
                            run(get(nodes['WAEF_'+school+'_'+node], 'completion_reward'), flags, ideas, techs, aat)
                            if index == 0: self.assertFalse({wanted, other} & techs)
                        self.assertEqual({wanted, other} & techs, set() if aat else {wanted})
                        # Repeated reconciliation does not stack or unlock the other line.
                        run(get(read('common/scripted_effects/waef_focus_effects.txt'), 'waef_sync_production_line'), flags, ideas, techs, aat)
                        self.assertEqual({wanted, other} & techs, set() if aat else {wanted})

    def test_fractional_cost_boundaries(self):
        categories = read('common/decisions/waef_focus_operations.txt')
        cases = []
        for category in categories:
            for decision in category.value:
                gate = get(decision.value, 'custom_cost_trigger')
                if gate is None: continue
                if decision.key.startswith('waef_prepare_defensive_line'):
                    cases.extend([(gate, 25, (), False), (gate, 15, ('waef_fra_operations_specialisation',), False)])
                else: cases.append((gate, 25 if decision.key == 'waef_local_offensive' else 50, (), True))
        self.assertGreater(len(cases), 4)
        for gate, cost, flags, command in cases:
            for resource in ('command_power', 'has_political_power') if command else ('has_political_power',):
                for amount, expected in [(cost - 1, False), (cost - .01, False), (cost, True), (cost + .01, True)]:
                    resources = {'command_power': cost, 'has_political_power': cost}
                    resources[resource] = amount
                    self.assertEqual(matches(gate, flags=flags, resources=resources), expected)
