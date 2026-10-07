"""Validate static state resources, building grants and regeneration."""
import unittest

from test_scenario_regressions import ROOT, get, parse
import regenerate_clean_scenario as generator


class StateEconomyTests(unittest.TestCase):
    RESOURCES = {
        "oil": 2,
        "bauxite": 11,
        "rubber": 3,
        "tungsten": 2,
        "chromium": 3,
        "coal": 35,
        "iron": 120,
    }
    BUILDINGS = {
        "industrial_complex": 2,
        "arms_factory": 5,
        "fuel_silo": 1,
        "hydro_steel_refinery": 12,
        "hydro_aluminium_refinery": 5,
    }

    def test_generator_settings_and_city_capacity(self):
        self.assertEqual(generator.PLAYER_RESOURCE_PACKAGE, self.RESOURCES)
        self.assertEqual(generator.PLAYER_BUILDING_PACKAGE,
                         {k: self.BUILDINGS[k] for k in
                          ("fuel_silo", "hydro_steel_refinery", "hydro_aluminium_refinery")})
        city = get(get(parse((ROOT / "common/state_category/city.txt").read_text()), "state_categories"), "city")
        self.assertEqual(int(get(city, "local_building_slots")), 40)
        self.assertEqual(sum(self.BUILDINGS.values()), 25)

    def test_player_regions_and_observer(self):
        counts = {"WEF": 0, "EEF": 0, "OBS": 0}
        for path in (ROOT / "history/states").glob("*.txt"):
            state = get(parse(path.read_text(encoding="utf-8-sig")), "state")
            self.assertEqual(get(state, "state_category"), "city", str(path))
            history = get(state, "history")
            owner = get(history, "owner")
            counts[owner] += 1
            resources = get(state, "resources")
            buildings = get(history, "buildings")
            if owner in ("WEF", "EEF"):
                self.assertIsNotNone(resources, str(path))
                self.assertEqual({n.key: int(n.value) for n in resources}, self.RESOURCES, str(path))
                for key, expected in self.BUILDINGS.items():
                    self.assertEqual(int(get(buildings, key)), expected, f"{path}: {key}")
                self.assertEqual(int(get(buildings, "infrastructure")), 7)
            else:
                self.assertEqual(owner, "OBS")
                self.assertIsNone(resources, str(path))
                for key in self.BUILDINGS:
                    self.assertIsNone(get(buildings, key), f"{path}: {key}")
        self.assertEqual(counts, {"WEF": 141, "EEF": 141, "OBS": 825})

    def test_regenerator_preserves_starting_economy(self):
        for filename, owner in [("810-E. Berlin.txt", "WEF"),
                                ("219-Moscow.txt", "EEF"),
                                ("962-Saaremaa.txt", "OBS")]:
            parsed = generator.parse_state(ROOT / "history/states" / filename)
            self.assertEqual(parsed["owner"], owner)
            state = get(parse(generator.render_state(parsed)), "state")
            resources = get(state, "resources")
            buildings = get(get(state, "history"), "buildings")
            if owner == "OBS":
                self.assertIsNone(resources)
                self.assertIsNone(get(buildings, "fuel_silo"))
            else:
                self.assertEqual({n.key: int(n.value) for n in resources}, self.RESOURCES)
                for key, value in self.BUILDINGS.items():
                    self.assertEqual(int(get(buildings, key)), value)

if __name__ == "__main__":
    unittest.main()
