"""Dedicated options-trading universe.

The ~100 highest options-volume underlyings that are tradable in the Alpaca
options paper account. Kept in a dependency-free leaf module so both the live
scanner (``services.options_scanner``) and the VRP scorer
(``scripts.orats_opportunity_model`` / ``services.options_engine``) can import it
without a circular dependency.

  - EXCLUDES cash-settled index options (SPX/NDX/RUT/VIX) — Alpaca trades only
    equity/ETF options, so index exposure is via ETF proxies (SPY/QQQ/IWM/DIA).
  - EXCLUDES leveraged/inverse ETFs (TQQQ/SQQQ/SOXL/UVXY/VXX/…) — blocked by the
    options engine (_is_leveraged) due to vol-decay; orders would be rejected.

Used two ways: (1) the scorer keeps these names regardless of the market-cap /
AUM floor so high-options sub-cap names (MARA/RIOT/AMC/GME) are scored; (2) the
scanner filters the VRP book to this set so only liquid, listed contracts trade.
"""

from __future__ import annotations

OPTIONS_UNIVERSE: frozenset[str] = frozenset(
    {
        # Broad-market & international ETFs (index proxies)
        "SPY",
        "QQQ",
        "IWM",
        "DIA",
        "EEM",
        "EFA",
        "FXI",
        "EWZ",
        "KWEB",
        "VEA",
        "VWO",
        # Sector & thematic ETFs
        "XLF",
        "XLE",
        "XLK",
        "XLV",
        "XLI",
        "XLY",
        "XLP",
        "XLU",
        "XLB",
        "XLC",
        "XLRE",
        "SMH",
        "KRE",
        "XBI",
        "IBB",
        "GDX",
        "XOP",
        "XRT",
        "ARKK",
        # Commodity / rate ETFs
        "GLD",
        "SLV",
        "TLT",
        "HYG",
        "LQD",
        "USO",
        # Mega-cap tech & semis
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "GOOGL",
        "GOOG",
        "META",
        "TSLA",
        "AVGO",
        "AMD",
        "NFLX",
        "INTC",
        "MU",
        "QCOM",
        "ORCL",
        "CRM",
        "ADBE",
        "CSCO",
        "TXN",
        "AMAT",
        # Financials
        "JPM",
        "BAC",
        "WFC",
        "C",
        "GS",
        "MS",
        "V",
        "MA",
        "AXP",
        # High options-volume / momentum / retail names
        "PLTR",
        "COIN",
        "MSTR",
        "MARA",
        "RIOT",
        "SOFI",
        "NIO",
        "F",
        "GM",
        "PYPL",
        "SHOP",
        "UBER",
        "ABNB",
        "SNAP",
        "ROKU",
        "DKNG",
        "HOOD",
        "SMCI",
        "GME",
        "AMC",
        # Consumer / health / energy / industrial blue chips
        "DIS",
        "BA",
        "T",
        "VZ",
        "KO",
        "PEP",
        "WMT",
        "COST",
        "HD",
        "NKE",
        "MCD",
        "SBUX",
        "XOM",
        "CVX",
        "OXY",
        "PFE",
        "MRNA",
        "JNJ",
        "LLY",
        "UNH",
        "CAT",
        "DE",
        "GE",
        "CVS",
    }
)
