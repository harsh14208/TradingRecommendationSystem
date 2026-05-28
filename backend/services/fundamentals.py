"""
Fundamental quality signals from yfinance balance sheet / income statement / cashflow.
No API key required. Each ticker fetch is cached for 24h (statements update quarterly).

Signals:
  - Piotroski F-Score (9-point financial health)
  - Free cash flow yield
  - Revenue growth acceleration (QoQ)
  - Return on equity (ROE) trend
  - Dividend yield vs 10Y rate gap
  - Net share buyback yield
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf

from services.market_data import _retry, _session

_executor = ThreadPoolExecutor(max_workers=2)
_fund_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 86400  # 24h — financials are quarterly


def _fetch_fundamentals(ticker: str) -> dict:
    cached = _fund_cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result = {}
    try:
        t = yf.Ticker(ticker, session=_session)

        # ── Pull all statements ────────────────────────────────────────────
        info = _retry(lambda: t.info)
        fin = _retry(lambda: t.financials)  # annual income stmt
        qfin = _retry(lambda: t.quarterly_financials)  # quarterly income stmt
        bs = _retry(lambda: t.balance_sheet)  # annual balance sheet
        qbs = _retry(lambda: t.quarterly_balance_sheet)
        cf = _retry(lambda: t.cashflow)  # annual cashflow
        qcf = _retry(lambda: t.quarterly_cashflow)

        import pandas as pd

        def _row(df, *keys):
            """Return most recent value for the first matching row label."""
            if df is None or df.empty:
                return None
            for k in keys:
                for idx in df.index:
                    if k.lower() in str(idx).lower():
                        vals = df.loc[idx].dropna()
                        return float(vals.iloc[0]) if not vals.empty else None
            return None

        # ── Piotroski F-Score (9 binary tests) ────────────────────────────
        f = 0

        # Profitability (4 tests)
        roa = None
        total_assets_1 = _row(bs, "total assets")
        net_income_1 = _row(fin, "net income")
        if total_assets_1 and total_assets_1 != 0 and net_income_1 is not None:
            roa = net_income_1 / total_assets_1
            if roa > 0:
                f += 1

        cfo = _row(cf, "operating cash flow", "cash from operations", "total cash from operations")
        if cfo is not None and cfo > 0:
            f += 1

        # Delta ROA (need 2 years)
        try:
            if fin is not None and not fin.empty and bs is not None and not bs.empty:
                ni_series = (
                    fin.loc[[i for i in fin.index if "net income" in str(i).lower()][0]]
                    if any("net income" in str(i).lower() for i in fin.index)
                    else None
                )
                ta_series = (
                    bs.loc[[i for i in bs.index if "total assets" in str(i).lower()][0]]
                    if any("total assets" in str(i).lower() for i in bs.index)
                    else None
                )
                if ni_series is not None and ta_series is not None and len(ni_series) >= 2 and len(ta_series) >= 2:
                    roa_now = (
                        float(ni_series.iloc[0]) / float(ta_series.iloc[0]) if float(ta_series.iloc[0]) != 0 else None
                    )
                    roa_prev = (
                        float(ni_series.iloc[1]) / float(ta_series.iloc[1]) if float(ta_series.iloc[1]) != 0 else None
                    )
                    if roa_now is not None and roa_prev is not None and roa_now > roa_prev:
                        f += 1
        except Exception:
            pass

        # Accruals (CFO/Assets > ROA)
        if cfo is not None and total_assets_1 and total_assets_1 != 0 and roa is not None:
            if (cfo / total_assets_1) > roa:
                f += 1

        # Leverage & liquidity (3 tests)
        try:
            if bs is not None and not bs.empty and len(bs.columns) >= 2:
                ltd_idx = [i for i in bs.index if "long term debt" in str(i).lower()]
                ca_idx = [
                    i
                    for i in bs.index
                    if "current assets" in str(i).lower() or "total current assets" in str(i).lower()
                ]
                cl_idx = [
                    i
                    for i in bs.index
                    if "current liabilities" in str(i).lower() or "total current liabilities" in str(i).lower()
                ]
                if ltd_idx:
                    ltd_now = float(bs.loc[ltd_idx[0]].iloc[0]) if not pd.isna(bs.loc[ltd_idx[0]].iloc[0]) else 0
                    ltd_prev = float(bs.loc[ltd_idx[0]].iloc[1]) if not pd.isna(bs.loc[ltd_idx[0]].iloc[1]) else 0
                    if ltd_now < ltd_prev:
                        f += 1
                if ca_idx and cl_idx:
                    cr_now = float(bs.loc[ca_idx[0]].iloc[0]) / max(float(bs.loc[cl_idx[0]].iloc[0]), 1)
                    cr_prev = float(bs.loc[ca_idx[0]].iloc[1]) / max(float(bs.loc[cl_idx[0]].iloc[1]), 1)
                    if cr_now > cr_prev:
                        f += 1
                # No new share dilution
                sh_idx = [
                    i
                    for i in bs.index
                    if "share issued" in str(i).lower()
                    or "common stock" in str(i).lower()
                    or "shares outstanding" in str(i).lower()
                ]
                if sh_idx and len(bs.columns) >= 2:
                    sh_now = float(bs.loc[sh_idx[0]].iloc[0]) if not pd.isna(bs.loc[sh_idx[0]].iloc[0]) else None
                    sh_prev = float(bs.loc[sh_idx[0]].iloc[1]) if not pd.isna(bs.loc[sh_idx[0]].iloc[1]) else None
                    if sh_now is not None and sh_prev is not None and sh_now <= sh_prev * 1.01:
                        f += 1
        except Exception:
            pass

        # Efficiency (2 tests)
        try:
            if fin is not None and not fin.empty and len(fin.columns) >= 2:
                rev_idx = [i for i in fin.index if "revenue" in str(i).lower() or "total revenue" in str(i).lower()]
                cogs_idx = [i for i in fin.index if "cost of" in str(i).lower()]
                if rev_idx and cogs_idx:
                    rev_now = float(fin.loc[rev_idx[0]].iloc[0])
                    rev_prev = float(fin.loc[rev_idx[0]].iloc[1])
                    cogs_now = float(fin.loc[cogs_idx[0]].iloc[0])
                    cogs_prev = float(fin.loc[cogs_idx[0]].iloc[1])
                    gm_now = (rev_now - cogs_now) / rev_now if rev_now != 0 else None
                    gm_prev = (rev_prev - cogs_prev) / rev_prev if rev_prev != 0 else None
                    if gm_now is not None and gm_prev is not None and gm_now > gm_prev:
                        f += 1
                ta_idx = [i for i in bs.index if "total assets" in str(i).lower()]
                if rev_idx and ta_idx and len(bs.columns) >= 2:
                    at_now = float(fin.loc[rev_idx[0]].iloc[0]) / max(float(bs.loc[ta_idx[0]].iloc[0]), 1)
                    at_prev = float(fin.loc[rev_idx[0]].iloc[1]) / max(float(bs.loc[ta_idx[0]].iloc[1]), 1)
                    if at_now > at_prev:
                        f += 1
        except Exception:
            pass

        result["piotroski_f"] = f

        # ── Free Cash Flow Yield ───────────────────────────────────────────
        try:
            market_cap = info.get("marketCap")
            capex = _row(cf, "capital expenditures", "purchase of property", "capex")
            if cfo is not None and capex is not None and market_cap and market_cap > 0:
                fcf = cfo - abs(capex)
                result["fcf_yield"] = round(fcf / market_cap * 100, 2)
                result["fcf"] = fcf
        except Exception:
            pass

        # ── Revenue growth QoQ acceleration ───────────────────────────────
        try:
            if qfin is not None and not qfin.empty:
                rev_idx = [i for i in qfin.index if "revenue" in str(i).lower() or "total revenue" in str(i).lower()]
                if rev_idx and len(qfin.columns) >= 4:
                    rev = qfin.loc[rev_idx[0]].dropna()
                    if len(rev) >= 4:
                        g1 = (float(rev.iloc[0]) / float(rev.iloc[1]) - 1) * 100 if float(rev.iloc[1]) != 0 else None
                        g2 = (float(rev.iloc[1]) / float(rev.iloc[2]) - 1) * 100 if float(rev.iloc[2]) != 0 else None
                        g3 = (float(rev.iloc[2]) / float(rev.iloc[3]) - 1) * 100 if float(rev.iloc[3]) != 0 else None
                        result["rev_growth_q1"] = round(g1, 2) if g1 is not None else None
                        result["rev_growth_q2"] = round(g2, 2) if g2 is not None else None
                        result["rev_growth_q3"] = round(g3, 2) if g3 is not None else None
                        if g1 is not None and g2 is not None:
                            result["rev_accelerating"] = bool(g1 > g2)
        except Exception:
            pass

        # ── ROE trend ─────────────────────────────────────────────────────
        try:
            if fin is not None and bs is not None and not fin.empty and not bs.empty and len(fin.columns) >= 2:
                ni_idx = [i for i in fin.index if "net income" in str(i).lower()]
                eq_idx = [
                    i for i in bs.index if "stockholders equity" in str(i).lower() or "total equity" in str(i).lower()
                ]
                if ni_idx and eq_idx:
                    roe_now = float(fin.loc[ni_idx[0]].iloc[0]) / max(abs(float(bs.loc[eq_idx[0]].iloc[0])), 1) * 100
                    roe_prev = float(fin.loc[ni_idx[0]].iloc[1]) / max(abs(float(bs.loc[eq_idx[0]].iloc[1])), 1) * 100
                    result["roe_now"] = round(roe_now, 2)
                    result["roe_prev"] = round(roe_prev, 2)
                    result["roe_improving"] = bool(roe_now > roe_prev)
        except Exception:
            pass

        # ── Dividend yield vs 10Y rate ─────────────────────────────────────
        try:
            div_yield = info.get("dividendYield")
            if div_yield and div_yield > 0:
                result["div_yield_pct"] = round(float(div_yield) * 100, 2)
        except Exception:
            pass

        # ── Buyback yield ─────────────────────────────────────────────────
        try:
            if cf is not None and not cf.empty:
                rep_idx = [
                    i
                    for i in cf.index
                    if "repurchase" in str(i).lower() or "buyback" in str(i).lower() or "common stock" in str(i).lower()
                ]
                mktcap = info.get("marketCap")
                if rep_idx and mktcap and mktcap > 0 and len(cf.columns) >= 1:
                    buyback = abs(float(cf.loc[rep_idx[0]].iloc[0])) if not pd.isna(cf.loc[rep_idx[0]].iloc[0]) else 0
                    result["buyback_yield"] = round(buyback / mktcap * 100, 2)
        except Exception:
            pass

        # ── Share dilution YoY ────────────────────────────────────────────
        # Counterpart to buyback yield: if share count is growing, holders are
        # being diluted regardless of buyback activity on the cash-flow statement.
        try:
            sh_current = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
            if bs is not None and not bs.empty and sh_current and sh_current > 0 and len(bs.columns) >= 2:
                sh_idx = [
                    i
                    for i in bs.index
                    if "share issued" in str(i).lower()
                    or "common stock" in str(i).lower()
                    or "shares outstanding" in str(i).lower()
                ]
                if sh_idx:
                    sh_prev_bs = float(bs.loc[sh_idx[0]].iloc[-1]) if not pd.isna(bs.loc[sh_idx[0]].iloc[-1]) else None
                    if sh_prev_bs and sh_prev_bs > 0:
                        growth_pct = (sh_current - sh_prev_bs) / sh_prev_bs * 100
                        result["shares_growth_yoy"] = round(growth_pct, 2)
        except Exception:
            pass

    except Exception as e:
        print(f"[fundamentals] {ticker}: {e}")

    _fund_cache[ticker] = (result, time.time())
    return result


async def get_fundamentals(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_fundamentals, ticker)
