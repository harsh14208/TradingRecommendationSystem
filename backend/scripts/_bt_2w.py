import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import scripts.backtest_technicals as bt

bt.START = "2026-05-10"
bt.main()
