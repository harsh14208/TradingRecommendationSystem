"""
services/engines/context.py

ScoringContext class to handle shared mutable state during signal scoring.
"""

from typing import Dict, List, Set, Optional, Any
import pandas as pd


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁScoringContextǁ__init____mutmut: MutantDict = {}  # type: ignore

class ScoringContext:
    @_mutmut_mutated(mutants_xǁScoringContextǁ__init____mutmut)
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
    def xǁScoringContextǁ__init____mutmut_orig(
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
    def xǁScoringContextǁ__init____mutmut_1(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = None
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
    def xǁScoringContextǁ__init____mutmut_2(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = ticker
        self.df = None
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
    def xǁScoringContextǁ__init____mutmut_3(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = ticker
        self.df = df
        self.info = None
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
    def xǁScoringContextǁ__init____mutmut_4(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = ticker
        self.df = df
        self.info = info
        self.market_ctx = None
        
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
    def xǁScoringContextǁ__init____mutmut_5(
        self,
        ticker: str,
        df: pd.DataFrame,
        info: dict,
        market_ctx: Optional[dict] = None
    ):
        self.ticker = ticker
        self.df = df
        self.info = info
        self.market_ctx = market_ctx and {}
        
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
    def xǁScoringContextǁ__init____mutmut_6(
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
        self.score = None
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
    def xǁScoringContextǁ__init____mutmut_7(
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
        self.score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_8(
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
        self.rationale = None
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
    def xǁScoringContextǁ__init____mutmut_9(
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
        self.sources = None
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
    def xǁScoringContextǁ__init____mutmut_10(
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
        self.sources = {"XXTechnicalXX"}
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
    def xǁScoringContextǁ__init____mutmut_11(
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
        self.sources = {"technical"}
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
    def xǁScoringContextǁ__init____mutmut_12(
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
        self.sources = {"TECHNICAL"}
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
    def xǁScoringContextǁ__init____mutmut_13(
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
        self.dominant = None
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
    def xǁScoringContextǁ__init____mutmut_14(
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
        self.dominant = "XXmacdXX"
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
    def xǁScoringContextǁ__init____mutmut_15(
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
        self.dominant = "MACD"
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
    def xǁScoringContextǁ__init____mutmut_16(
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
        self._force_hold = None
        
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
    def xǁScoringContextǁ__init____mutmut_17(
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
        self._force_hold = True
        
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
    def xǁScoringContextǁ__init____mutmut_18(
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
        self.vol_confidence_penalty = None
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
    def xǁScoringContextǁ__init____mutmut_19(
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
        self.vol_confidence_penalty = 1.0
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
    def xǁScoringContextǁ__init____mutmut_20(
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
        self.rs_confidence_penalty = None
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
    def xǁScoringContextǁ__init____mutmut_21(
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
        self.rs_confidence_penalty = 1.0
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
    def xǁScoringContextǁ__init____mutmut_22(
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
        self.insider_confidence_penalty = None
        
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
    def xǁScoringContextǁ__init____mutmut_23(
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
        self.insider_confidence_penalty = 1.0
        
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
    def xǁScoringContextǁ__init____mutmut_24(
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
        self.osc_score = None
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
    def xǁScoringContextǁ__init____mutmut_25(
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
        self.osc_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_26(
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
        self.ma_score = None
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
    def xǁScoringContextǁ__init____mutmut_27(
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
        self.ma_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_28(
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
        self.trend_score = None
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
    def xǁScoringContextǁ__init____mutmut_29(
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
        self.trend_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_30(
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
        self.volume_score = None
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
    def xǁScoringContextǁ__init____mutmut_31(
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
        self.volume_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_32(
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
        self.mean_rev_score = None
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
    def xǁScoringContextǁ__init____mutmut_33(
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
        self.mean_rev_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_34(
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
        self.momentum_score = None
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
    def xǁScoringContextǁ__init____mutmut_35(
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
        self.momentum_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_36(
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
        self.analyst_score = None
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
    def xǁScoringContextǁ__init____mutmut_37(
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
        self.analyst_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_38(
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
        self.pc_score = None
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
    def xǁScoringContextǁ__init____mutmut_39(
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
        self.pc_score = 1.0
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
    def xǁScoringContextǁ__init____mutmut_40(
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
        self.soc_bucket = None
        self.ichimoku_score = 0.0
        
        # Ticker variables
        self.price = 0.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_41(
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
        self.soc_bucket = 1.0
        self.ichimoku_score = 0.0
        
        # Ticker variables
        self.price = 0.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_42(
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
        self.ichimoku_score = None
        
        # Ticker variables
        self.price = 0.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_43(
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
        self.ichimoku_score = 1.0
        
        # Ticker variables
        self.price = 0.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_44(
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
        self.price = None
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_45(
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
        self.price = 1.0
        self.atr = 0.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_46(
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
        self.atr = None
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_47(
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
        self.atr = 1.0
        self.vix = None
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_48(
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
        self.vix = ""
        self.tech = {}
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_49(
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
        self.tech = None
        self._atr_pct_pre = 0.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_50(
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
        self._atr_pct_pre = None
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_51(
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
        self._atr_pct_pre = 1.02
        self._is_low_atr = False
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_52(
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
        self._is_low_atr = None
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_53(
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
        self._is_low_atr = True
        self._is_lev_etf = False
    def xǁScoringContextǁ__init____mutmut_54(
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
        self._is_lev_etf = None
    def xǁScoringContextǁ__init____mutmut_55(
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
        self._is_lev_etf = True

mutants_xǁScoringContextǁ__init____mutmut['_mutmut_orig'] = ScoringContext.xǁScoringContextǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_1'] = ScoringContext.xǁScoringContextǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_2'] = ScoringContext.xǁScoringContextǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_3'] = ScoringContext.xǁScoringContextǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_4'] = ScoringContext.xǁScoringContextǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_5'] = ScoringContext.xǁScoringContextǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_6'] = ScoringContext.xǁScoringContextǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_7'] = ScoringContext.xǁScoringContextǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_8'] = ScoringContext.xǁScoringContextǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_9'] = ScoringContext.xǁScoringContextǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_10'] = ScoringContext.xǁScoringContextǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_11'] = ScoringContext.xǁScoringContextǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_12'] = ScoringContext.xǁScoringContextǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_13'] = ScoringContext.xǁScoringContextǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_14'] = ScoringContext.xǁScoringContextǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_15'] = ScoringContext.xǁScoringContextǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_16'] = ScoringContext.xǁScoringContextǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_17'] = ScoringContext.xǁScoringContextǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_18'] = ScoringContext.xǁScoringContextǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_19'] = ScoringContext.xǁScoringContextǁ__init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_20'] = ScoringContext.xǁScoringContextǁ__init____mutmut_20 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_21'] = ScoringContext.xǁScoringContextǁ__init____mutmut_21 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_22'] = ScoringContext.xǁScoringContextǁ__init____mutmut_22 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_23'] = ScoringContext.xǁScoringContextǁ__init____mutmut_23 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_24'] = ScoringContext.xǁScoringContextǁ__init____mutmut_24 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_25'] = ScoringContext.xǁScoringContextǁ__init____mutmut_25 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_26'] = ScoringContext.xǁScoringContextǁ__init____mutmut_26 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_27'] = ScoringContext.xǁScoringContextǁ__init____mutmut_27 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_28'] = ScoringContext.xǁScoringContextǁ__init____mutmut_28 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_29'] = ScoringContext.xǁScoringContextǁ__init____mutmut_29 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_30'] = ScoringContext.xǁScoringContextǁ__init____mutmut_30 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_31'] = ScoringContext.xǁScoringContextǁ__init____mutmut_31 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_32'] = ScoringContext.xǁScoringContextǁ__init____mutmut_32 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_33'] = ScoringContext.xǁScoringContextǁ__init____mutmut_33 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_34'] = ScoringContext.xǁScoringContextǁ__init____mutmut_34 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_35'] = ScoringContext.xǁScoringContextǁ__init____mutmut_35 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_36'] = ScoringContext.xǁScoringContextǁ__init____mutmut_36 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_37'] = ScoringContext.xǁScoringContextǁ__init____mutmut_37 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_38'] = ScoringContext.xǁScoringContextǁ__init____mutmut_38 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_39'] = ScoringContext.xǁScoringContextǁ__init____mutmut_39 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_40'] = ScoringContext.xǁScoringContextǁ__init____mutmut_40 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_41'] = ScoringContext.xǁScoringContextǁ__init____mutmut_41 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_42'] = ScoringContext.xǁScoringContextǁ__init____mutmut_42 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_43'] = ScoringContext.xǁScoringContextǁ__init____mutmut_43 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_44'] = ScoringContext.xǁScoringContextǁ__init____mutmut_44 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_45'] = ScoringContext.xǁScoringContextǁ__init____mutmut_45 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_46'] = ScoringContext.xǁScoringContextǁ__init____mutmut_46 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_47'] = ScoringContext.xǁScoringContextǁ__init____mutmut_47 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_48'] = ScoringContext.xǁScoringContextǁ__init____mutmut_48 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_49'] = ScoringContext.xǁScoringContextǁ__init____mutmut_49 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_50'] = ScoringContext.xǁScoringContextǁ__init____mutmut_50 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_51'] = ScoringContext.xǁScoringContextǁ__init____mutmut_51 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_52'] = ScoringContext.xǁScoringContextǁ__init____mutmut_52 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_53'] = ScoringContext.xǁScoringContextǁ__init____mutmut_53 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_54'] = ScoringContext.xǁScoringContextǁ__init____mutmut_54 # type: ignore # mutmut generated
mutants_xǁScoringContextǁ__init____mutmut['xǁScoringContextǁ__init____mutmut_55'] = ScoringContext.xǁScoringContextǁ__init____mutmut_55 # type: ignore # mutmut generated
