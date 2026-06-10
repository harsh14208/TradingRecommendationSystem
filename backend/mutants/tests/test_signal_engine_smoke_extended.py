import unittest


class TestSignalEngineSmokeExtended(unittest.TestCase):
    def test__apply_final_warning_deconfliction_equivalence(self):
        # Keep this test file lightweight and independent.
        # We validate the haircut behavior is stable for a few extra heads.
        from tests.test_signal_engine_confidence import (
            _apply_final_warning_deconfliction,
        )

        conf = 90.0
        # BUY: any overbought head should haircut.
        rationale = [{"head": "CCI Extreme Overbought"}]
        self.assertEqual(
            _apply_final_warning_deconfliction("BUY", conf, rationale),
            round(max(35.0, conf * 0.92), 1),
        )

        # SELL: any oversold head should haircut.
        rationale = [{"head": "Williams %R Oversold"}]
        self.assertEqual(
            _apply_final_warning_deconfliction("SELL", conf, rationale),
            round(max(35.0, conf * 0.92), 1),
        )

        # Unknown head should not change.
        rationale = [{"head": "Completely Unknown Head"}]
        self.assertEqual(
            _apply_final_warning_deconfliction("BUY", conf, rationale),
            conf,
        )
