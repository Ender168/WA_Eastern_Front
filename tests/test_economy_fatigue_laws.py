"""Validate restored World Ablaze law-fatigue mission definitions and start symmetry."""
import re
import sys
import unittest
from pathlib import Path

from test_scenario_regressions import ROOT, condition, get, parse, read, walk

sys.path.insert(0, str(ROOT / "tools"))
import generate_wa_compatibility as compat


ECONOMY = {
    "exiled_economy": 70,
    "civilian_economy": 70,
    "low_economic_mobilisation": 42,
    "partial_economic_mobilisation": 56,
    "war_economy": 35,
    "tot_economic_mobilisation": 28,
    "over_mobilisation": 21,
}
TRADE = {
    "free_trade": 140,
    "export_focus": 70,
    "limited_exports": 70,
    "closed_economy": 112,
    "embargoed_economy": 56,
    "collectivization": 112,
}
CONSCRIPTION = {
    "disarmed_nation": 70,
    "USA_selective_service": 56,
    "volunteer_only": 56,
    "limited_conscription": 56,
    "extensive_conscription": 42,
    "service_by_requirement": 35,
    "all_adults_serve": 28,
    "scraping_the_barrel": 21,
}
ALL = ECONOMY | TRADE | CONSCRIPTION
IDS = {"economy_fatigue_" + name + "_mission" for name in ALL}


class WorldAblazeLawFatigueTests(unittest.TestCase):
    def test_all_21_real_missions_and_original_timers(self):
        definitions = get(read("common/decisions/waef_economy_fatigue_laws.txt"), "economy_decisions")
        missions = {node.key: node.value for node in definitions}
        self.assertEqual(set(missions), IDS)
        self.assertEqual(set(compat.RESTORED_FATIGUE_LAW_MISSIONS), IDS)
        for law, timeout in ALL.items():
            key = "economy_fatigue_" + law + "_mission"
            definition = missions[key]
            self.assertEqual(int(get(definition, "days_mission_timeout")), timeout, key)
            self.assertEqual(get(get(definition, "allowed"), "always"), "no", key)
            self.assertIsNotNone(get(definition, "complete_effect"), key)
            self.assertIsNotNone(get(definition, "timeout_effect"), key)

    def test_restored_decisions_are_not_duplicated_as_dummies(self):
        dummy = get(read("common/decisions/waef_legacy_compatibility.txt"), "economy_decisions")
        names = {node.key for node in dummy}
        self.assertFalse(names & IDS)
        for key in ("CAN_aluminium_company_of_canada_stage_a", "TUR_repeal_the_wealth_tax"):
            self.assertIn(key, names)
        categories = read("common/decisions/categories/waef_legacy_compatibility.txt")
        economy = get(categories, "economy_decisions")
        for side in ("WEF", "EEF"):
            self.assertTrue(condition(get(economy, "allowed"), set(), tag=side))
            self.assertTrue(condition(get(economy, "visible"), set(), tag=side))
        self.assertFalse(condition(get(economy, "allowed"), set(), tag="OBS"))
        self.assertFalse(condition(get(economy, "visible"), set(), tag="OBS"))

    def test_both_player_histories_initialize_zero_fatigue_and_three_missions(self):
        for tag, label in (("WEF", "Western Front"), ("EEF", "Eastern Front")):
            content = (ROOT / "history/countries" / f"{tag} - {label}.txt").read_text()
            self.assertIn("add_ideas = economy_fatigue_0", content)
            self.assertIn("set_variable = { economic_fatigue = 0 }", content)
            activated = re.findall(r"activate_mission\s*=\s*(economy_fatigue_[A-Za-z0-9_]+_mission)", content)
            self.assertCountEqual(
                activated,
                ["economy_fatigue_civilian_economy_mission",
                 "economy_fatigue_free_trade_mission",
                 "economy_fatigue_volunteer_only_mission"],
                tag,
            )

    def test_no_disabled_focus_blocks_fatigue_increases(self):
        missions = get(read("common/decisions/waef_economy_fatigue_laws.txt"), "economy_decisions")
        for node in missions:
            self.assertFalse(any(inner.key == "focus_progress" for inner in walk(node.value)), node.key)
        body = (ROOT / "common/decisions/waef_economy_fatigue_laws.txt").read_text()
        self.assertGreaterEqual(body.count("economy_fatigue_level_up_1 = yes"), 11)
        self.assertIn("economy_fatigue_level_down_1 = yes", body)

    def test_compatibility_generator_retains_explicit_exclusions(self):
        source = (ROOT / "tools/generate_wa_compatibility.py").read_text()
        self.assertIn("if name in RESTORED_FATIGUE_LAW_MISSIONS:", source)
        self.assertIn("if name == 'economy_decisions':", source)
        self.assertIn("if category != 'economy_decisions':", source)


if __name__ == "__main__":
    unittest.main()
