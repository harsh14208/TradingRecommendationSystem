"""§90: Validate WATCH bench tickers for universe expansion batch 3."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WATCH = ["PANW", "BWA", "FTI", "EQH", "TRGP", "APTV", "DHI", "FIVE", "ITW"]

# Monkey-patch TICKERS for a focused run
import scripts.backtest_technicals as bt
bt.TICKERS = WATCH
bt.START = "2004-01-01"
bt.END = "2026-06-01"

if __name__ == "__main__":
    print(f"§90 WATCH bench validation — {len(WATCH)} tickers")
    print(f"Tickers: {', '.join(WATCH)}\n")
    # Run backtest via main()
    bt.main()
