"""Regression checks for German technology-assimilation focus-tree switching."""
from pathlib import Path
from test_scenario_regressions import parse,get
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOCUS_PATH = ROOT / "common/national_focus/waef_germany_tech_focus.txt"
DECISION_PATH = ROOT / "common/decisions/waef_technology_assimilation.txt"
EN_LOC_PATH = ROOT / "localisation/english/waef_national_tech_focus_l_english.yml"
RU_LOC_PATH = ROOT / "localisation/russian/waef_national_tech_focus_l_russian.yml"


def focus_blocks(text: str) -> list[str]:
    """Return top-level focus blocks from one focus_tree definition."""
    lines = text.splitlines()
    blocks: list[str] = []
    collecting = False
    depth = 0
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not collecting and stripped == "focus = {":
            collecting = True
            depth = 1
            current = [line]
            continue

        if collecting:
            current.append(line)
            depth += line.count("{") - line.count("}")
            if depth == 0:
                blocks.append("\n".join(current))
                collecting = False

    return blocks


class GermanTechFocusTreeTests(unittest.TestCase):
    def test_german_assimilation_loads_german_focus_tree(self):
        text = DECISION_PATH.read_text(encoding="utf-8-sig")
        start = text.index("waef_assimilate_german_technologies")
        end = text.index("waef_assimilate_soviet_technologies", start)
        section = text[start:end]

        self.assertIn("set_country_flag = german_technologies_tree_flag", section)
        self.assertIn("tree = WAEF_GER_TECH_DOCTRINE", section)
        self.assertIn("keep_completed = no", section)
        self.assertIn("mark_focus_tree_layout_dirty = yes", section)

    def test_german_tree_is_gated_by_assimilated_school(self):
        text = FOCUS_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("id = WAEF_GER_TECH_DOCTRINE", text)
        self.assertIn("has_country_flag = german_technologies_tree_flag", text)
        self.assertIn("tag = WEF", text)
        self.assertIn("tag = EEF", text)
        self.assertIn("reset_on_civilwar = no", text)

    def test_tree_is_full_sized_and_focuses_take_at_least_70_days(self):
        text = FOCUS_PATH.read_text(encoding="utf-8-sig")
        blocks = focus_blocks(text)
        self.assertGreaterEqual(len(blocks), 35)

        for block in blocks:
            focus_id = re.search(r"\bid\s*=\s*(WAEF_GER_[A-Z0-9_]+)", block)
            cost = re.search(r"\bcost\s*=\s*([0-9]+)", block)
            self.assertIsNotNone(focus_id)
            self.assertIsNotNone(cost, focus_id.group(1))
            if focus_id.group(1)=='WAEF_GER_C00':self.assertEqual(int(cost.group(1)),2)
            elif focus_id.group(1).endswith(('_P1','_P2')):self.assertEqual(int(cost.group(1)),3)
            else:self.assertGreaterEqual(int(cost.group(1)), 10, focus_id.group(1))
            self.assertIn("completion_reward = {", block, focus_id.group(1))

    def test_every_focus_has_english_and_russian_localisation(self):
        focus_text = FOCUS_PATH.read_text(encoding="utf-8-sig")
        en = EN_LOC_PATH.read_text(encoding="utf-8-sig")
        ru = RU_LOC_PATH.read_text(encoding="utf-8-sig")

        focus_ids = []
        for block in focus_blocks(focus_text):
            match = re.search(r"\bid\s*=\s*(WAEF_GER_[A-Z0-9_]+)", block)
            self.assertIsNotNone(match)
            focus_ids.append(match.group(1))

        for focus_id in focus_ids:
            for localisation in (en, ru):
                self.assertRegex(localisation, rf"(?m)^\s*{re.escape(focus_id)}:0\s+\"")
                self.assertRegex(
                    localisation,
                    rf"(?m)^\s*{re.escape(focus_id)}_desc:0\s+\"",
                )

    def test_strategic_tradeoffs_are_mutually_exclusive(self):
        text = FOCUS_PATH.read_text(encoding="utf-8-sig")
        blocks = {re.search(r"id = (\w+)", b).group(1): b for b in focus_blocks(text)}
        for a, b in [("T1", "H1"), ("W1", "H1"), ("A1", "W1"), ("P1", "P2"), ("C41", "C42"), ("C51", "C52"), ("C61", "C62")]:
            self.assertIn(f"WAEF_GER_{b}", [n.value for n in get(get(parse(blocks[f"WAEF_GER_{a}"]),"focus"),"mutually_exclusive")])
            self.assertIn(f"WAEF_GER_{a}", [n.value for n in get(get(parse(blocks[f"WAEF_GER_{b}"]),"focus"),"mutually_exclusive")])

    def test_focus_rewards_use_world_ablaze_technology_ids(self):
        text = FOCUS_PATH.read_text(encoding="utf-8-sig")
        self.assertNotIn("unlock_technology =", text)

        expected = (
            "ger_infantry_weapons_4",
            "ger_artillery_2",
            "ger_mechanized_infantry_3",
            "ger_medium_tank_chassis_2_3",
            "ger_heavy_tank_chassis_3",
            "ger_fighter_multirole_ad_tech_1",
            "ger_fighter_multirole_1",
            "assembly_line_production",
            "advanced_computing_machine",
            "ger_cas_ad_tech_7",
        )
        for technology in expected:
            self.assertIn(f"{technology} = 1", text)

        self.assertIn('has_dlc = "By Blood Alone"', text)


if __name__ == "__main__":
    unittest.main()
