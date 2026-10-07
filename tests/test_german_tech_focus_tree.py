"""Regression checks for German technology-assimilation focus-tree switching."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GermanTechFocusTreeTests(unittest.TestCase):
    def test_german_assimilation_loads_german_focus_tree(self):
        text = (ROOT / "common/decisions/waef_technology_assimilation.txt").read_text(
            encoding="utf-8-sig"
        )
        start = text.index("waef_assimilate_german_technologies")
        end = text.index("waef_assimilate_soviet_technologies", start)
        section = text[start:end]

        self.assertIn("set_country_flag = german_technologies_tree_flag", section)
        self.assertIn("tree = WAEF_GER_TECH_DOCTRINE", section)
        self.assertIn("keep_completed = no", section)
        self.assertIn("mark_focus_tree_layout_dirty = yes", section)

    def test_german_tree_is_gated_by_assimilated_school(self):
        text = (ROOT / "common/national_focus/waef_germany_tech_focus.txt").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("id = WAEF_GER_TECH_DOCTRINE", text)
        self.assertIn("has_country_flag = german_technologies_tree_flag", text)
        self.assertIn("tag = WEF", text)
        self.assertIn("tag = EEF", text)
        self.assertIn("reset_on_civilwar = no", text)


if __name__ == "__main__":
    unittest.main()
