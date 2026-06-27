"""Tests for the real warning-deconfliction function used in production.

These tests import ``apply_warning_deconfliction`` from the production gate
module rather than replicating its logic, so they will fail if the real
engine implementation changes.
"""

import unittest

from services.gates.warning import apply_warning_deconfliction


class TestSignalEngineFinalDeconfliction(unittest.TestCase):
    def test_buy_overbought_haircut(self):
        conf = 80.0
        rationale = [{"head": "RSI Overbought"}]
        out = apply_warning_deconfliction("BUY", conf, rationale)
        self.assertEqual(out, 73.6)

    def test_sell_oversold_haircut(self):
        conf = 60.0
        rationale = [{"head": "Extreme Fear"}]
        out = apply_warning_deconfliction("SELL", conf, rationale)
        self.assertEqual(out, 55.2)

    def test_buy_no_warning_no_change(self):
        conf = 78.0
        rationale = [{"head": "Some Other Head"}]
        out = apply_warning_deconfliction("BUY", conf, rationale)
        self.assertEqual(out, conf)

    def test_sell_no_warning_no_change(self):
        conf = 55.0
        rationale = [{"head": "Some Other Head"}]
        out = apply_warning_deconfliction("SELL", conf, rationale)
        self.assertEqual(out, conf)

    def test_confidence_floor(self):
        # ensure it never drops below 35.0
        conf = 36.0
        rationale = [{"head": "Extreme Fear"}]
        out = apply_warning_deconfliction("SELL", conf, rationale)
        # 36 * 0.92 = 33.12 => floor at 35.0
        self.assertEqual(out, 35.0)

    def test_hold_action_unchanged(self):
        conf = 50.0
        rationale = [{"head": "RSI Overbought"}]
        out = apply_warning_deconfliction("HOLD", conf, rationale)
        self.assertEqual(out, conf)

    def test_multiple_conflicting_heads_only_apply_once(self):
        conf = 80.0
        rationale = [{"head": "RSI Overbought"}, {"head": "Stochastic Overbought"}]
        out = apply_warning_deconfliction("BUY", conf, rationale)
        # single 0.92 multiplier, not compounded
        self.assertEqual(out, 73.6)


if __name__ == "__main__":
    unittest.main()
