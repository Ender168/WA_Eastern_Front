"""Simulate the actual semiannual scenario effect, including the HOI4 no-leap-year date thresholds."""
import re
import unittest
from pathlib import Path
from test_scenario_regressions import get, read, walk, ROOT


def tuple_date(value):
    return tuple(int(x) for x in str(value).split("."))


def matches(conditions, spirits, current_date):
    decisions = []
    for node in conditions:
        if node.key == "date":
            if node.op != ">":
                raise AssertionError(f"Unsupported date operator {node.op}")
            decisions.append(tuple_date(current_date) > tuple_date(node.value))
        elif node.key == "has_idea":
            decisions.append(node.value in spirits)
        elif node.key == "NOT":
            decisions.append(not matches(node.value, spirits, current_date))
        elif node.key == "OR":
            decisions.append(any(matches([sub], spirits, current_date) for sub in node.value))
        else:
            raise AssertionError(f"Unexpected condition {node.key}")
    return all(decisions)


def advance(nodes, spirits, current_date, event_ids):
    for node in nodes:
        if node.key != "if":
            raise AssertionError(f"Unexpected mobilization effect {node.key}")
        if not matches(get(node.value, "limit"), spirits, current_date):
            continue
        for inner in node.value:
            if inner.key == "limit":
                continue
            if inner.key == "add_ideas":
                spirits.add(inner.value)
            elif inner.key == "swap_ideas":
                previous = get(inner.value, "remove_idea")
                next_idea = get(inner.value, "add_idea")
                if previous not in spirits:
                    raise AssertionError(f"Cannot swap absent spirit {previous}")
                spirits.remove(previous)
                spirits.add(next_idea)
            elif inner.key == "country_event":
                event_ids.append(get(inner.value, "id"))
            else:
                raise AssertionError(f"Unexpected mobilization operation {inner.key}")


class SemiannualMobilizationTests(unittest.TestCase):
    def test_two_country_hooks_keep_fuel_sync_and_call_mobilization_once(self):
        actions = get(read("common/on_actions/waef_doctrine_on_actions.txt"), "on_actions")
        self.assertFalse((ROOT / "common/on_actions/waef_mobilization_on_actions.txt").exists())
        for tag in ("WEF", "EEF"):
            hooks = [item for item in actions if item.key == "on_daily_" + tag]
            self.assertEqual(len(hooks), 1)
            commands = get(hooks[0].value, "effect")
            self.assertEqual(len([x for x in commands if x.key == "waef_sync_fuel_capacity_penalty"]), 1)
            self.assertEqual(len([x for x in commands if x.key == "waef_apply_scheduled_mobilization"]), 1)

    def test_every_march_september_and_adjacent_days(self):
        script = get(read("common/scripted_effects/waef_mobilization_effects.txt"), "waef_apply_scheduled_mobilization")
        definitions = get(get(read("common/ideas/waef_scenario_ideas.txt"), "ideas"), "country")
        for tag in ("WEF", "EEF"):
            with self.subTest(tag=tag):
                spirits = set()
                event_ids = []
                counter = 0

                # January 1 and the day before the first mobilization wave must be unchanged.
                for day in ("1941.1.1", "1941.2.28"):
                    advance(script, spirits, day, event_ids)
                    self.assertFalse(spirits)

                for year in range(1941, 1946):
                    for month, eve in ((3, 2), (9, 8)):
                        prior = f"{year}.{eve}.{28 if month == 3 else 31}"
                        target = f"{year}.{month}.1"
                        # HOI4 has no leap day, including in 1944.
                        advance(script, spirits, prior, event_ids)
                        self.assertEqual(len(spirits), 0 if counter == 0 else 1)
                        if counter:
                            self.assertEqual(spirits, {f"waef_mobilization_{counter * 5:02d}"})
                        advance(script, spirits, target, event_ids)
                        counter += 1
                        code = f"{counter * 5:02d}"
                        self.assertEqual(spirits, {f"waef_mobilization_{code}"})
                        amount = float(get(get(get(definitions, f"waef_mobilization_{code}"), "modifier"), "conscription"))
                        self.assertAlmostEqual(amount, counter * 0.005)
                        # A daily hook may run again; it must not stack another spirit or event.
                        advance(script, spirits, target, event_ids)
                        self.assertEqual(spirits, {f"waef_mobilization_{code}"})
                        advance(script, spirits, f"{year}.{month}.2", event_ids)
                        self.assertEqual(spirits, {f"waef_mobilization_{code}"})
                        self.assertEqual(event_ids, ["waef.2"])
                self.assertEqual(counter, 10)
                for day in ("1945.9.30", "1946.3.1", "1947.9.1"):
                    advance(script, spirits, day, event_ids)
                    self.assertEqual(spirits, {"waef_mobilization_50"})
                    self.assertEqual(event_ids, ["waef.2"])

    def test_spirits_and_explanation_event_only_once(self):
        defs = get(get(read("common/ideas/waef_scenario_ideas.txt"), "ideas"), "country")
        names = [n.key for n in defs if re.fullmatch(r"waef_mobilization_\d{2}", n.key)]
        self.assertEqual(len(names), 10)
        self.assertIsNone(get(defs, "waef_prewar_truce"))
        self.assertIsNotNone(get(defs, "waef_offensive_momentum"))
        events = [get(e.value, "id") for e in read("events/waef_events.txt") if e.key == "country_event"]
        self.assertEqual(events.count("waef.2"), 1)
        for path in ("localisation/english/waef_l_english.yml", "localisation/russian/waef_l_russian.yml"):
            content = (ROOT / path).read_text(encoding="utf-8-sig")
            for name in names:
                self.assertIn(" " + name + ":0", content)
            for key in ("waef.2.t", "waef.2.d", "waef.2.a"):
                self.assertIn(" " + key + ":0", content)


if __name__ == "__main__":
    unittest.main()
