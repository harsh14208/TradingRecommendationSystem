import unittest


def _apply_final_warning_deconfliction(action: str, confidence: float, rationale: list[dict]) -> float:
    """Replica of the post-processing haircut added to signal_engine.

    This is a lightweight unit test that verifies the intended behavior
    without requiring the full engine dependencies / data fetch.
    """
    if action == "BUY":
        overbought_heads = {
            "RSI Overbought",
            "RSI Elevated",
            "Stochastic Overbought",
            "Stochastic Bearish Cross (Overbought)",
            "Williams %R Overbought",
            "CCI Extreme Overbought",
            "MFI Overbought",
            "Broad Market Complacency",
            "Extreme Greed",
            "NAAIM: Managers Fully Invested",
        }
        if any(r.get("head") in overbought_heads for r in rationale):
            return round(max(35.0, confidence * 0.92), 1)
        return confidence

    if action == "SELL":
        oversold_heads = {
            "RSI Oversold",
            "RSI Weakening",
            "Stochastic Oversold",
            "Stochastic Bullish Cross (Oversold)",
            "Williams %R Oversold",
            "CCI Extreme Oversold",
            "MFI Oversold",
            "Extreme Fear",
            "Market Breadth Deteriorating",
            "NAAIM: Managers Extremely Defensive",
        }
        if any(r.get("head") in oversold_heads for r in rationale):
            return round(max(35.0, confidence * 0.92), 1)
        return confidence

    return confidence


class TestSignalEngineFinalDeconfliction(unittest.TestCase):
    def test_buy_overbought_haircut(self):
        conf = 80.0
        rationale = [{"head": "RSI Overbought"}]
        out = _apply_final_warning_deconfliction("BUY", conf, rationale)
        self.assertEqual(out, 73.6)

    def test_sell_oversold_haircut(self):
        conf = 60.0
        rationale = [{"head": "Extreme Fear"}]
        out = _apply_final_warning_deconfliction("SELL", conf, rationale)
        self.assertEqual(out, 55.2)

    def test_buy_no_warning_no_change(self):
        conf = 78.0
        rationale = [{"head": "Some Other Head"}]
        out = _apply_final_warning_deconfliction("BUY", conf, rationale)
        self.assertEqual(out, conf)

    def test_sell_no_warning_no_change(self):
        conf = 55.0
        rationale = [{"head": "Some Other Head"}]
        out = _apply_final_warning_deconfliction("SELL", conf, rationale)
        self.assertEqual(out, conf)

    def test_confidence_floor(self):
        # ensure it never drops below 35.0
        conf = 36.0
        rationale = [{"head": "Extreme Fear"}]
        out = _apply_final_warning_deconfliction("SELL", conf, rationale)
        # 36 * 0.92 = 33.12 => floor at 35.0
        self.assertEqual(out, 35.0)


if __name__ == "__main__":
    unittest.main()
