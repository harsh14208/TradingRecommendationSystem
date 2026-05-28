"""
Earnings calendar and EPS surprise history via yfinance (free, no API key).
"""

import asyncio
import time as _time
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf

from services.market_data import _retry, _session

_executor = ThreadPoolExecutor(max_workers=2)
_cal_cache: dict[str, tuple[dict, float]] = {}
_surp_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 3600 * 4  # 4 hours — earnings dates don't change intraday


def _fetch_earnings_calendar(ticker: str) -> dict:
    cached = _cal_cache.get(ticker)
    if cached and _time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    try:
        from datetime import datetime

        t = yf.Ticker(ticker, session=_session)
        cal = _retry(lambda: t.calendar)
        if cal is None:
            return {}

        result: dict = {}
        # yfinance returns a dict; key may be "Earnings Date" or list
        raw_date = cal.get("Earnings Date") or cal.get("earningsDate")
        if raw_date is None and isinstance(cal, dict):
            # Some versions return a flat dict with a single key
            for k, v in cal.items():
                if "earning" in k.lower():
                    raw_date = v
                    break

        if raw_date is not None:
            if isinstance(raw_date, (list, tuple)) and len(raw_date) > 0:
                raw_date = raw_date[0]
            if hasattr(raw_date, "date"):
                raw_date = raw_date.date()
            today = datetime.now().date()
            try:
                days_to = (raw_date - today).days
                result["next_earnings_date"] = str(raw_date)
                result["days_to_earnings"] = days_to
            except Exception:
                pass

        # ── Days SINCE last earnings (post-earnings cooldown) ────────────
        try:
            t2 = yf.Ticker(ticker, session=_session)
            eh = _retry(lambda: t2.earnings_history)
            if eh is not None and not (hasattr(eh, "empty") and eh.empty):
                import pandas as _pd

                dates = []
                for col in eh.columns:
                    if "date" in col.lower():
                        dates = [d for d in eh[col] if _pd.notna(d)]
                        break
                if not dates and hasattr(eh, "index"):
                    dates = list(eh.index)
                if dates:
                    past = [d for d in dates if hasattr(d, "date") and d.date() < datetime.now().date()]
                    if past:
                        last_dt = max(past)
                        days_since = (datetime.now().date() - last_dt.date()).days
                        result["last_earnings_date"] = str(last_dt.date())
                        result["days_since_earnings"] = days_since
        except Exception:
            pass

        _cal_cache[ticker] = (result, _time.time())
        return result
    except Exception as e:
        print(f"[earnings] calendar {ticker}: {e}")
        return {}


def _fetch_earnings_surprise(ticker: str) -> dict:
    cached = _surp_cache.get(ticker)
    if cached and _time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    try:
        t = yf.Ticker(ticker, session=_session)
        hist = _retry(lambda: t.earnings_history)
        if hist is None or (hasattr(hist, "empty") and hist.empty):
            return {}

        # Normalise column names — yfinance varies across versions
        col_map = {}
        for c in hist.columns:
            cl = c.lower().replace(" ", "_")
            if "actual" in cl:
                col_map["actual"] = c
            elif "estimate" in cl:
                col_map["estimate"] = c

        if "actual" not in col_map or "estimate" not in col_map:
            return {}

        recent = hist.tail(4)
        beats = misses = 0
        surprise_pcts = []
        for _, row in recent.iterrows():
            act = row.get(col_map["actual"])
            est = row.get(col_map["estimate"])
            if act is None or est is None:
                continue
            try:
                a, e = float(act), float(est)
                if a > e:
                    beats += 1
                elif a < e:
                    misses += 1
                if abs(e) > 0.001:
                    surprise_pcts.append((a - e) / abs(e) * 100)
            except (TypeError, ValueError):
                pass

        # Consecutive beats from most recent backwards
        consec = 0
        for _, row in hist.iloc[::-1].iterrows():
            act = row.get(col_map["actual"])
            est = row.get(col_map["estimate"])
            if act is None or est is None:
                break
            try:
                if float(act) > float(est):
                    consec += 1
                else:
                    break
            except (TypeError, ValueError):
                break

        avg_surprise = round(sum(surprise_pcts) / len(surprise_pcts), 1) if surprise_pcts else None
        last_surprise = round(surprise_pcts[-1], 1) if surprise_pcts else None

        result = {
            "beats_last_4q": beats,
            "misses_last_4q": misses,
            "consec_beats": consec,
            "avg_surprise_pct": avg_surprise,
            "last_surprise_pct": last_surprise,
        }

        # ── Finnhub EPS surprise acceleration ────────────────────────────────
        # Compares Q1 (most recent) vs Q4 (oldest) surprise magnitude.
        # Accelerating beats = management execution improving = alpha signal.
        # Uses the same Finnhub key already configured; zero extra auth cost.
        try:
            import finnhub
            from config import get_settings

            _key = get_settings().finnhub_api_key
            if _key:
                _client = finnhub.Client(api_key=_key)
                _fh_eps = _client.company_earnings(ticker, limit=4) or []
                if len(_fh_eps) >= 2:
                    _surp_list = [q.get("surprisePercent", 0) for q in _fh_eps if q.get("surprisePercent") is not None]
                    if len(_surp_list) >= 2:
                        # Index 0 = most recent, last index = oldest
                        acceleration = round(_surp_list[0] - _surp_list[-1], 2)
                        result["surprise_acceleration"] = acceleration
                        result["quarterly_surprises"] = [round(s, 2) for s in _surp_list]
        except Exception:
            pass  # Finnhub unavailable — yfinance data still valid

        _surp_cache[ticker] = (result, _time.time())
        return result
    except Exception as e:
        print(f"[earnings] surprise {ticker}: {e}")
        return {}


async def get_earnings_calendar(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_earnings_calendar, ticker)


async def get_earnings_surprise(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_earnings_surprise, ticker)
