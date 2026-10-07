"""Keep map VP weights consistent with the strategic objective manifest."""
import json
import unittest

from test_scenario_regressions import ROOT
import regenerate_clean_scenario as generator


class StrategicVictoryPointTests(unittest.TestCase):
    def test_checked_in_weights_and_regeneration_preserve_locations(self):
        objectives = json.loads((ROOT / "tools/waef_strategic_cities.json").read_text())["objectives"]
        targets = {city["province"]: city["state"] for city in objectives}
        self.assertEqual(len(targets), 40)
        states = [generator.parse_state(p) for p in sorted((ROOT / "history/states").glob("*.txt"))]
        actual = {province: (s["id"], value) for s in states for province, value in s["vps"]}
        for province, sid in targets.items():
            self.assertEqual(actual[province], (sid, 10))
        for province, (_, value) in actual.items():
            self.assertEqual(value, 10 if province in targets else 1)
        before = [generator.render_state(s) for s in states]
        # Rebuilding from older VP weights must restore this policy while
        # preserving VP order, hence the generator's first-VP supply hubs.
        for s in states:
            s["vps"] = [(province, 37) for province, _ in s["vps"]]
        generator.apply_strategic_victory_point_values(states)
        self.assertEqual([generator.render_state(s) for s in states], before)
        generator.apply_strategic_victory_point_values(states)
        self.assertEqual([generator.render_state(s) for s in states], before)


if __name__ == "__main__":
    unittest.main()
