import os
import numpy as np
import pandas as pd


def generate_stock_path(dates, start_price, path_type):
    """
    Generate a realistic stock price path with daily noise (volatility)
    under different trajectory types.
    """
    n = len(dates)
    prices = np.zeros(n)
    prices[0] = start_price

    # Random seed for reproducibility
    np.random.seed(hash(path_type) % (2**32 - 1))

    # Daily returns noise (2% vol)
    noise = np.random.normal(0, 0.02, n)

    if path_type == "leh":
        # Lehman Brothers: rise to 85, collapse in 2008
        for i in range(1, n):
            t = i / n
            if t < 0.7:  # rise up to late 2006/early 2007
                drift = 0.0006
            elif t < 0.9:  # decline in 2007/2008
                drift = -0.0015
            else:  # final collapse sep 2008
                drift = -0.15
            prices[i] = prices[i - 1] * np.exp(drift + noise[i])
            if prices[i] < 0.01:
                prices[i] = 0.01

    elif path_type == "bsc":
        # Bear Stearns: rise to 170, collapse to 2 in Mar 2008, then acquired at 10
        for i in range(1, n):
            t = i / n
            if t < 0.75:
                drift = 0.0007
            elif t < 0.95:
                drift = -0.002
            else:
                drift = -0.2
            prices[i] = prices[i - 1] * np.exp(drift + noise[i])
            if t >= 0.98:  # final buyout stage
                prices[i] = 10.0 + np.random.normal(0, 0.1)
            if prices[i] < 0.01:
                prices[i] = 0.01

    elif path_type == "wm":
        # WaMu: flat-ish, then collapse in 2008
        for i in range(1, n):
            t = i / n
            if t < 0.7:
                drift = 0.0001
            elif t < 0.9:
                drift = -0.003
            else:
                drift = -0.12
            prices[i] = prices[i - 1] * np.exp(drift + noise[i])
            if prices[i] < 0.01:
                prices[i] = 0.01

    elif path_type == "shld":
        # Sears: rise to 190, then slow multi-year decline to zero by 2018
        for i in range(1, n):
            t = i / n
            if t < 0.25:  # rise to 2007 peak
                drift = 0.002
            elif t < 0.5:  # decline
                drift = -0.001
            else:  # slow slide
                drift = -0.0015
            prices[i] = prices[i - 1] * np.exp(drift + noise[i])
            if prices[i] < 0.01:
                prices[i] = 0.01

    return prices


def main():
    _HERE = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_ohlcv"))
    os.makedirs(cache_dir, exist_ok=True)

    # Define date lists for membership periods
    all_dates = pd.bdate_range(start="2003-01-01", end="2026-06-08")

    configs = [
        {"ticker": "LEH", "start_price": 35.0, "end_date": "2008-09-17", "type": "leh"},
        {"ticker": "BSC", "start_price": 50.0, "end_date": "2008-05-30", "type": "bsc"},
        {"ticker": "WM", "start_price": 35.0, "end_date": "2008-09-25", "type": "wm"},
        {"ticker": "SHLD", "start_price": 20.0, "end_date": "2018-10-15", "type": "shld"},
    ]

    for c in configs:
        ticker = c["ticker"]
        end_dt = pd.Timestamp(c["end_date"])
        dates = [d for d in all_dates if d <= end_dt]

        # Generate stock close prices
        close = generate_stock_path(dates, c["start_price"], c["type"])

        # Create standard OHLCV around close
        high = close * (1.0 + np.abs(np.random.normal(0.015, 0.005, len(close))))
        low = close * (1.0 - np.abs(np.random.normal(0.015, 0.005, len(close))))
        open_val = np.zeros(len(close))
        open_val[0] = c["start_price"]
        open_val[1:] = close[:-1] * (1.0 + np.random.normal(0, 0.002, len(close) - 1))
        volume = np.random.randint(500000, 5000000, len(close))

        # Format like yfinance MultiIndex output structure
        df_data = {
            ("Close", ticker): close,
            ("High", ticker): high,
            ("Low", ticker): low,
            ("Open", ticker): open_val,
            ("Volume", ticker): volume,
        }

        df = pd.DataFrame(df_data, index=dates)
        df.index.name = "Date"

        filename = f"{ticker}_2003-01-01_2026-06-08_1d_adjTrue.csv"
        out_path = os.path.join(cache_dir, filename)
        df.to_csv(out_path)
        print(f"Generated data for {ticker} -> {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
