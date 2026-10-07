"""Check war preparation UI, June 22 unlock, and direct scripted declarations."""
import unittest
from pathlib import Path
from test_scenario_regressions import ROOT, get, read


def get_decisions():
    return get(read("common/decisions/waef_war_setup.txt"), "waef_war_setup")


class WarSetupTests(unittest.TestCase):
    def test_mission_and_symmetric_start(self):
        decisions = get_decisions()
        mission = get(decisions, "waef_war_preparation_countdown")
        self.assertEqual(get(mission, "days_mission_timeout"), "172")
        self.assertEqual(get(mission, "selectable_mission"), "no")
        self.assertEqual(get(get(mission, "activation"), "always"), "no")
        self.assertEqual(get(get(mission, "available"), "always"), "no")
        self.assertEqual(get(get(mission, "timeout_effect"), "set_country_flag"), "waef_war_unlocked")
        for tag, label in (("WEF","Western Front"), ("EEF","Eastern Front")):
            content = (ROOT / "history" / "countries" / f"{tag} - {label}.txt").read_text()
            self.assertEqual(content.count("activate_mission = waef_war_preparation_countdown"), 1)
            self.assertNotIn("waef_prewar_truce", content)

    def test_june22_date_fallback_and_war_target(self):
        declaration = get(get_decisions(), "waef_declare_scenario_war")
        for block_name in ("visible", "available"):
            dates = [node.value for node in get(declaration, block_name)
                     if node.key == "OR" for child in node.value if child.key == "date"
                     for node in [child]]
            self.assertEqual(dates, ["1941.6.21"])
        effects = get(declaration, "complete_effect")
        blocks = [node for node in effects if node.key in ("if", "else_if")]
        self.assertEqual(len(blocks), 2)
        for block, owner, opponent in zip(blocks, ("WEF","EEF"), ("EEF","WEF")):
            self.assertEqual(get(get(block.value, "limit"), "tag"), owner)
            self.assertEqual(get(get(block.value, "declare_war_on"), "target"), opponent)
            self.assertEqual(get(get(block.value, "declare_war_on"), "type"), "annex_everything")
        timed = get(effects, "add_timed_idea")
        self.assertEqual(get(timed, "idea"), "waef_offensive_momentum")
        self.assertEqual(get(timed, "days"), "90")
        self.assertEqual(get(effects, "set_country_flag"), "waef_scenario_war_declared")
        self.assertEqual(get(declaration, "cost"), "0")
        self.assertEqual(get(declaration, "fire_only_once"), "yes")

    def test_no_prewar_ban_and_localized(self):
        defs = get(get(read("common/ideas/waef_scenario_ideas.txt"), "ideas"), "country")
        self.assertIsNone(get(defs, "waef_prewar_truce"))
        self.assertEqual(get(get(get(defs, "waef_offensive_momentum"), "modifier"), "army_attack_factor"), "0.10")
        category = get(read("common/decisions/categories/waef_categories.txt"), "waef_war_setup")
        self.assertEqual(get(category, "priority"), "9960")
        for locale in ("russian", "english"):
            path = ROOT / "localisation" / locale / ("waef_l_" + locale + ".yml")
            content = path.read_text(encoding="utf-8-sig")
            for key in ("waef_war_setup","waef_war_preparation_countdown","waef_declare_scenario_war"):
                self.assertIn(" " + key + ":0", content)


if __name__ == "__main__":
    unittest.main()
