"""
services/lineage.py

QENG-2c: Dataset/version lineage.
Tracks and versions data pulls, feature transforms, calendars, and corporate action configurations.
"""

import hashlib
import json
from datetime import datetime

DATA_LINEAGE_VERSION = "v1.2.0"

LINEAGE_CONFIG = {
    "data_version": DATA_LINEAGE_VERSION,
    "vendor": "Polygon.io",
    "endpoints": {
        "ohlcv": "/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}",
        "quotes": "/v3/quotes/{ticker}",
        "snapshots": "/v2/snapshot/locale/us/markets/stocks/tickers",
        "dividends": "/v3/reference/dividends",
        "splits": "/v3/reference/splits",
    },
    "adjustment_mode": "split_and_dividend_adjusted",
    "market_calendar": "NYSE",
    "corporate_action_handling": {
        "splits": "backward_adjusted",
        "dividends": "backward_adjusted_reinvested",
        "source": "Polygon.io reference endpoints verified against yfinance fallback",
    },
    "schema_versions": {
        "signals": "v8.0",
        "feature_snapshots": "v2.0",
        "broker_orders": "v2.0",
        "research_experiments": "v1.0"
    }
}

def get_lineage_hash() -> str:
    """Return a unique hash of the lineage config for verification."""
    config_str = json.dumps(LINEAGE_CONFIG, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()

def get_lineage_meta() -> dict:
    """Return the complete metadata block for tracing."""
    return {
        "lineage_hash": get_lineage_hash(),
        "timestamp": datetime.now().isoformat(),
        **LINEAGE_CONFIG
    }
