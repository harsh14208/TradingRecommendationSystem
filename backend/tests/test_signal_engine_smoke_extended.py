import unittest

from services.gates.warning import apply_warning_deconfliction


class TestSignalEngineSmokeExtended(unittest.TestCase):
    def test_apply_warning_deconfliction_equivalence(self):
        # Keep this test file lightweight and independent.
        # We validate the haircut behavior is stable for a few extra heads.
        conf = 90.0
        # BUY: any overbought head should haircut.
        rationale = [{"head": "CCI Extreme Overbought"}]
        self.assertEqual(
            apply_warning_deconfliction("BUY", conf, rationale),
            round(max(35.0, conf * 0.92), 1),
        )

        # SELL: any oversold head should haircut.
        rationale = [{"head": "Williams %R Oversold"}]
        self.assertEqual(
            apply_warning_deconfliction("SELL", conf, rationale),
            round(max(35.0, conf * 0.92), 1),
        )

        # Unknown head should not change.
        rationale = [{"head": "Completely Unknown Head"}]
        self.assertEqual(
            apply_warning_deconfliction("BUY", conf, rationale),
            conf,
        )
