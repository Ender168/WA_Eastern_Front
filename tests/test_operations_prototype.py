import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from operations_prototype import Operation, enemy_majority

class OperationsPrototypeTests(unittest.TestCase):
    def test_strict_majority(self):
        self.assertFalse(enemy_majority(range(8), range(4)))
        self.assertTrue(enemy_majority(range(8), range(5)))

    def test_preparation_is_charged_immediately(self):
        op = Operation(7, 14, fatigue=10)
        self.assertEqual((op.fatigue, op.preparation_refund), (12, 2))
        for _ in range(7): op.tick()
        self.assertEqual(op.fatigue, 12)

    def test_thirty_offensive_days_charge_three_points(self):
        op = Operation(15, 30)
        for _ in range(45): op.tick()
        self.assertEqual((op.phase, op.fatigue), ('failed', 5))

    def test_victory_refunds_only_preparation(self):
        op = Operation(7, 14, fatigue=10)
        for _ in range(17): op.tick()
        op.tick(victory=True)
        self.assertEqual((op.phase, op.fatigue), ('victory', 11))
        op.tick()
        self.assertEqual(op.fatigue, 11)

    def test_cap_never_refunds_unapplied_fatigue(self):
        op = Operation(30, 60, fatigue=99, preparation_charge=5)
        self.assertEqual(op.preparation_refund, 1)
        op.tick(victory=True)
        self.assertEqual(op.fatigue, 99)

    def test_victory_precedes_tenth_day_charge(self):
        op = Operation(7, 14)
        for _ in range(16): op.tick()
        op.tick(victory=True)
        self.assertEqual((op.phase, op.fatigue), ('victory', 0))
