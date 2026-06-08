"""
services/engines/context.py

ScoringContext class to handle shared mutable state during signal scoring.
"""

from typing import Dict, List, Set, Optional, Any
import pandas as pd

class ScoringContext:
    def __init__(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = ticker
        self.df = df
        self.info = info
        self.market_ctx = market_ctx or {}
        
        # Scoring state
        self.score = 0.0
        self.rationale = []
        self.sources = {"Technical"}
        self.dominant = "macd"
        self._force_hold = False
        
        # Penalties
        self.vol_confidence_penalty = 0.0
        self.rs_confidence_penalty = 0.0
        self.insider_confidence_penalty = 0.0
        
        # Sub-score caps
        self.osc_score = 0.0
        self.ma_score = 0.0
        self.trend_score = 0.0
        self.volume_score = 0.0
        self.mean_rev_score = 0.0
        self.momentum_score = 0.0
        self.analyst_score = 0.0
        self.pc_score = 0.0
        self.soc_bucket = 0.0
        self.ichimoku_score = 0.0
        
        # Ticker variables
        self.price = 0.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
