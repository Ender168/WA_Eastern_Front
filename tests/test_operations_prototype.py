import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from operations_prototype import Operation, enemy_majority

class OperationsPrototypeTests(unittest.TestCase):
    def test_strict_majority(self):
        self.assertFalse(enemy_majority(range(8), range(4)))
        self.assertTrue(enemy_majority(range(8), range(5)))

    def test_tactical_success_refunds_only_preparation(self):
        op = Operation(7, 14, fatigue=10)
        for _ in range(14): op.tick()
        self.assertEqual((op.fatigue, op.preparation_refund), (12, 1))
        op.tick(victory=True)
        self.assertEqual((op.phase, op.fatigue), ('victory', 11))
        op.tick()
        self.assertEqual(op.fatigue, 11)

    def test_strategic_clock_does_not_reset_at_phase_boundary(self):
        op = Operation(30, 60)
        for _ in range(35): op.tick()
        self.assertEqual((op.phase, op.elapsed, op.fatigue, op.preparation_refund), ('offensive', 5, 5, 4))

    def test_cap_never_refunds_unapplied_fatigue(self):
        op = Operation(30, 60, fatigue=99)
        for _ in range(30): op.tick()
        self.assertEqual(op.preparation_refund, 1)
        op.tick(victory=True)
        self.assertEqual(op.fatigue, 99)

    def test_peace_and_expiry_keep_charges(self):
        op = Operation(7, 14)
        for _ in range(21): op.tick()
        self.assertEqual((op.phase, op.fatigue), ('failed', 3))
        op = Operation(7, 14)
        for _ in range(7): op.tick()
        op.tick(at_war=False)
        self.assertEqual((op.phase, op.fatigue), ('cancelled', 1))

    def test_victory_precedes_daily_charge(self):
        op = Operation(7, 14)
        for _ in range(13): op.tick()
        op.tick(victory=True)
        self.assertEqual((op.phase, op.fatigue), ('victory', 0))
