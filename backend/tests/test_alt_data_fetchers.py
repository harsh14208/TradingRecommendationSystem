#!/usr/bin/env python3
"""Tests for §104–§110 alt-data fetchers.

Each test mocks the external HTTP response and verifies:
1. Parsing logic produces expected DataFrame shape/columns
2. PIT merge functions attach features correctly
3. No exceptions on malformed/missing data
"""

from __future__ import annotations

from datetime import date

import pandas as pd

# §104: FINRA short volume
from services.finra_short_volume import _aggregate_venues, _parse_finra_sv_txt, merge_sv_pit

# §105: SEC FTD
from services.sec_ftd import _parse_ftd_csv, merge_ftd_pit

# §106: Sentiment (UMCSENT primary + optional NAAIM/AAII)
from services.sentiment_naaim_aaii import _parse_naaim_xlsx, merge_sentiment_pit

# §107: GDELT
from services.gdelt_news_tone import _parse_gkg_csv, _extract_org_tone, merge_gdelt_tone_pit

# §108: FINRA ATS
from services.finra_ats_dark_pool import _parse_ats_csv, merge_ats_pit

# §109: Wikipedia
from services.wikipedia_pageviews import _parse_wiki_json, merge_wikipedia_pit

# §110: OCC
from services.occ_volume_oi import _parse_occ_csv, merge_occ_pit

# §110: CBOE delayed-quotes options chain
from services.options_cboe import (
    _normalize_contracts,
    _parse_option_symbol,
    build_options_chain_daily_row,
    fetch_cboe_options_chain,
)


class TestFinraShortVolume:
    """§104 — FINRA daily short-sale volume."""

    def test_parse_finra_sv_txt(self) -> None:
        content = b"Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n20240102|AAPL|1000000|5000|5000000|CNMS\n20240102|MSFT|800000|3000|4000000|CNMS\n"
        df = _parse_finra_sv_txt(content)
        assert df is not None
        assert len(df) == 2
        assert set(df.columns) >= {"date", "symbol", "short_volume", "total_volume", "market"}
        assert df.iloc[0]["symbol"] == "AAPL"
        assert df.iloc[0]["short_volume"] == 1_000_000

    def test_merge_sv_pit(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        sv = pd.DataFrame(
            {
                "date": [date(2024, 1, 2), date(2024, 1, 3)],
                "ticker": ["AAPL", "AAPL"],
                "short_volume_ratio": [20.0, 22.0],
                "sv_ratio_5d_delta": [-1.5, -2.5],
            }
        )
        result = merge_sv_pit(df, sv, "AAPL")
        assert "sv_ratio" in result.columns
        assert "sv_ratio_5d_delta" in result.columns
        # FINRA T data is usable from T+1 onward.
        assert result["sv_ratio"].iloc[0] == 0.0  # 2024-01-02
        assert result["sv_ratio"].iloc[1] == 20.0  # 2024-01-03

    def test_merge_sv_pit_empty(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        result = merge_sv_pit(df, pd.DataFrame(), "AAPL")
        assert result["sv_ratio"].iloc[0] == 0.0

    def test_parse_finra_sv_txt_missing_short_exempt(self) -> None:
        """Early per-venue files lack ShortExemptVolume."""
        content = b"Date|Symbol|ShortVolume|TotalVolume|Market\n20090803|A|100|500|Q\n"
        df = _parse_finra_sv_txt(content)
        assert df is not None
        assert len(df) == 1
        assert df.iloc[0]["short_volume"] == 100
        assert df.iloc[0]["total_volume"] == 500
        assert df.iloc[0]["short_exempt_volume"] is pd.NA

    def test_aggregate_venues(self) -> None:
        df = pd.DataFrame(
            {
                "date": [date(2009, 8, 3), date(2009, 8, 3), date(2009, 8, 3)],
                "symbol": ["AAPL", "AAPL", "AAPL"],
                "short_volume": [100, 200, 300],
                "short_exempt_volume": [1, 2, 3],
                "total_volume": [1000, 2000, 3000],
                "market": ["Q", "N", "D"],
            }
        )
        agg = _aggregate_venues(df)
        assert len(agg) == 1
        assert agg.iloc[0]["short_volume"] == 600
        assert agg.iloc[0]["total_volume"] == 6000
        assert set(agg.iloc[0]["market"].split(",")) == {"D", "N", "Q"}


class TestSecFtd:
    """§105 — SEC fails-to-deliver."""

    def test_parse_ftd_csv(self) -> None:
        content = b"SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE\n20240102|037833100|AAPL|50000|Apple Inc|185.50\n"
        df = _parse_ftd_csv(content)
        assert df is not None
        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "AAPL"
        assert df.iloc[0]["ftd_shares"] == 50_000

    def test_merge_ftd_pit(self) -> None:
        idx = pd.date_range("2024-02-15", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        ftd = pd.DataFrame(
            {
                "ticker": ["AAPL", "AAPL"],
                "effective_date": [date(2024, 2, 15), date(2024, 2, 16)],
                "ftd_shares": [10000, 12000],
                "ftd_63d_pctile": [80.0, 85.0],
            }
        )
        result = merge_ftd_pit(df, ftd, "AAPL")
        assert "ftd_shares" in result.columns
        assert "ftd_63d_pctile" in result.columns
        assert result["ftd_63d_pctile"].iloc[0] == 80.0


class TestSentimentNaaimAaii:
    """§106 — NAAIM / AAII sentiment."""

    def test_parse_naaim_xlsx(self) -> None:
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        ws.append(["Date", "Mean/Average"])
        ws.append(["2024-01-02", 45.2])
        ws.append(["2024-01-03", 42.1])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        df = _parse_naaim_xlsx(buf.read())
        assert df is not None
        assert len(df) == 2
        assert "naaim_exposure" in df.columns
        assert df["naaim_exposure"].iloc[0] == 45.2

    def test_merge_sentiment_pit(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        umcsent = pd.DataFrame(
            {
                "date": [date(2024, 1, 1), date(2024, 1, 2)],  # +14d lag baked in
                "umcsent": [65.0, 62.0],
            }
        )
        naaim = pd.DataFrame(
            {
                "date": [date(2024, 1, 2), date(2024, 1, 3)],
                "naaim_exposure": [45.0, 42.0],
            }
        )
        aaii = pd.DataFrame(
            {
                "date": [date(2024, 1, 2)],
                "aaii_bullish": [30.0],
                "aaii_bearish": [40.0],
                "aaii_bull_bear_spread": [-10.0],
            }
        )
        result = merge_sentiment_pit(df, umcsent, naaim, aaii)
        assert "umcsent" in result.columns
        assert "naaim_exposure" in result.columns
        assert "aaii_bull_bear_spread" in result.columns
        assert result["umcsent"].iloc[0] == 62.0


class TestGdeltNewsTone:
    """§107 — GDELT news tone (bounded pilot)."""

    def test_parse_gkg_csv(self) -> None:
        # GKG 1.0 daily zip: columns 0=DATE, 6=ORGANIZATIONS, 7=TONE
        import io as _io
        import zipfile

        header = "DATE\tNUMARTS\tCOUNTS\tTHEMES\tLOCATIONS\tPERSONS\tORGANIZATIONS\tTONE\n"
        row = "20240102\t1\t\t\t\t\tApple Inc|Microsoft\t-1.23,2.34,3.45,4.56,5.67,6.78\n"
        buf = _io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("20240102.gkg.csv", (header + row).encode())
        content = buf.getvalue()
        df = _parse_gkg_csv(content)
        assert df is not None
        assert len(df) == 1
        assert "organizations" in df.columns
        assert "tone" in df.columns
        assert df.iloc[0]["date"] == date(2024, 1, 2)

    def test_extract_org_tone(self) -> None:
        df = pd.DataFrame(
            {
                "date": [date(2024, 1, 2)],
                "organizations": ["Apple Inc"],
                "tone": ["-1.5,2.0,3.0,4.0,5.0,6.0"],
            }
        )
        sub = _extract_org_tone(df, "AAPL")
        assert sub is not None
        assert len(sub) == 1
        assert sub.iloc[0]["tone_score"] == -1.5

    def test_merge_gdelt_tone_pit(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        gdelt = pd.DataFrame(
            {
                "date": [date(2024, 1, 1)],  # +1 day lag = Jan 2 usable
                "ticker": ["AAPL"],
                "tone_mean": [-1.5],
                "tone_std": [0.5],
            }
        )
        result = merge_gdelt_tone_pit(df, gdelt, "AAPL")
        assert "tone_mean" in result.columns
        assert "tone_z" in result.columns
        assert result["tone_z"].iloc[0] == -3.0


class TestFinraAtsDarkPool:
    """§108 — FINRA ATS dark-pool weekly."""

    def test_parse_ats_csv(self) -> None:
        content = b"IssueSymbolIdentifier,TotalWeeklyShareQuantity,ATSShareQuantity,MediaShareQuantity\nAAPL,50000000,15000000,5000000\n"
        df = _parse_ats_csv(content)
        assert df is not None
        assert len(df) == 1
        assert df.iloc[0]["ticker"] == "AAPL"
        assert df.iloc[0]["ats_ratio"] == 30.0

    def test_merge_ats_pit(self) -> None:
        idx = pd.date_range("2024-01-22", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        ats = pd.DataFrame(
            {
                "week_start_date": [date(2024, 1, 8)],  # +14 day lag = Jan 22 usable
                "ticker": ["AAPL"],
                "ats_ratio": [35.0],
            }
        )
        result = merge_ats_pit(df, ats, "AAPL")
        assert "ats_ratio" in result.columns
        assert result["ats_ratio"].iloc[0] == 35.0


class TestWikipediaPageviews:
    """§109 — Wikipedia pageviews."""

    def test_parse_wiki_json(self) -> None:
        data = {"items": [{"timestamp": "2024010200", "views": 5000}, {"timestamp": "2024010300", "views": 5200}]}
        df = _parse_wiki_json(data)
        assert df is not None
        assert len(df) == 2
        assert "views" in df.columns
        assert df.iloc[0]["views"] == 5000

    def test_merge_wikipedia_pit(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        wiki = pd.DataFrame(
            {
                "date": [date(2024, 1, 1)],  # +1 day lag = Jan 2 usable
                "ticker": ["AAPL"],
                "views": [5000],
                "views_z": [1.5],
            }
        )
        result = merge_wikipedia_pit(df, wiki, "AAPL")
        assert "views" in result.columns
        assert "views_z" in result.columns
        assert result["views_z"].iloc[0] == 1.5


class TestOccVolumeOi:
    """§110 — OCC daily volume/OI."""

    def test_parse_occ_csv(self) -> None:
        content = b"Underlying,Call/Put,Volume,Open Interest\nAAPL,C,10000,50000\nAAPL,P,8000,40000\n"
        df = _parse_occ_csv(content)
        assert df is not None
        assert len(df) == 2
        assert df.iloc[0]["ticker"] == "AAPL"
        assert df.iloc[0]["volume"] == 10_000

    def test_merge_occ_pit(self) -> None:
        idx = pd.date_range("2024-01-02", periods=3)
        df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)
        occ = pd.DataFrame(
            {
                "date": [date(2024, 1, 1)],  # +1 day lag = Jan 2 usable
                "ticker": ["AAPL"],
                "pcr_volume": [80.0],
                "pcr_oi": [80.0],
            }
        )
        result = merge_occ_pit(df, occ, "AAPL")
        assert "pcr_volume" in result.columns
        assert "pcr_oi" in result.columns
        assert result["pcr_volume"].iloc[0] == 80.0


class TestCboeOptions:
    """§110 — CBOE delayed-quotes options chain."""

    @staticmethod
    def _sample_cboe_payload() -> dict:
        return {
            "timestamp": "2026-06-11 16:00:00",
            "symbol": "AAPL",
            "data": {
                "symbol": "AAPL",
                "current_price": 220.0,
                "options": [
                    {
                        "option": "AAPL260711C00220000",
                        "bid": 5.0,
                        "ask": 5.2,
                        "iv": 0.28,
                        "open_interest": 5000.0,
                        "volume": 1200.0,
                        "delta": 0.25,
                        "gamma": 0.05,
                        "theta": -0.1,
                        "vega": 0.2,
                        "rho": 0.01,
                    },
                    {
                        "option": "AAPL260711P00220000",
                        "bid": 4.8,
                        "ask": 5.0,
                        "iv": 0.30,
                        "open_interest": 4000.0,
                        "volume": 900.0,
                        "delta": -0.25,
                        "gamma": 0.04,
                        "theta": -0.09,
                        "vega": 0.18,
                        "rho": -0.01,
                    },
                    {
                        "option": "AAPL260718C00230000",
                        "bid": 3.0,
                        "ask": 3.2,
                        "iv": 0.26,
                        "open_interest": 3000.0,
                        "volume": 600.0,
                        "delta": 0.25,
                        "gamma": 0.04,
                        "theta": -0.08,
                        "vega": 0.22,
                        "rho": 0.01,
                    },
                    {
                        "option": "AAPL260718P00230000",
                        "bid": 3.5,
                        "ask": 3.7,
                        "iv": 0.27,
                        "open_interest": 2500.0,
                        "volume": 500.0,
                        "delta": -0.25,
                        "gamma": 0.04,
                        "theta": -0.07,
                        "vega": 0.21,
                        "rho": -0.01,
                    },
                ],
            },
        }

    def test_parse_option_symbol(self) -> None:
        parsed = _parse_option_symbol("AAPL260711C00220000", "AAPL")
        assert parsed is not None
        assert parsed["option_type"] == "call"
        assert parsed["strike"] == 220.0
        assert parsed["expiration_date"] == date(2026, 7, 11)

    def test_parse_option_symbol_put(self) -> None:
        parsed = _parse_option_symbol("AAPL260711P00210000", "AAPL")
        assert parsed is not None
        assert parsed["option_type"] == "put"
        assert parsed["strike"] == 210.0

    def test_normalize_contracts(self) -> None:
        payload = self._sample_cboe_payload()
        contracts = _normalize_contracts("AAPL", payload["data"]["options"], 220.0)
        assert len(contracts) == 4
        call = next(c for c in contracts if c["option_type"] == "call" and c["strike"] == 220.0)
        assert call["iv"] == 0.28
        assert call["volume"] == 1200
        assert call["open_interest"] == 5000
        assert call["mid"] == 5.1

    def test_fetch_cboe_options_chain(self) -> None:
        payload = self._sample_cboe_payload()
        result = fetch_cboe_options_chain("AAPL", payload=payload)
        assert result is not None
        assert result["source"] == "cboe"
        assert result["spot"] == 220.0
        assert result["total_vol"] == 3200
        assert result["pc_ratio"] is not None
        assert result["avg_iv"] is not None
        assert result["near_iv"] is not None
        assert result["far_iv"] is not None
        assert result["skew_25d"] is not None
        assert "contracts" in result

    def test_build_options_chain_daily_row(self) -> None:
        payload = self._sample_cboe_payload()
        row = build_options_chain_daily_row("AAPL", date(2026, 6, 11), payload=payload)
        assert row is not None
        assert row["ticker"] == "AAPL"
        assert row["date"] == date(2026, 6, 11)
        assert row["contract_count"] == 4
        assert row["total_volume"] == 3200
        assert row["source"] == "cboe"
        assert row["contracts_snapshot"] is not None
        assert len(row["contracts_snapshot"]) == 4

    def test_fetch_cboe_options_chain_low_volume(self) -> None:
        payload = self._sample_cboe_payload()
        for opt in payload["data"]["options"]:
            opt["volume"] = 1.0
        result = fetch_cboe_options_chain("AAPL", payload=payload)
        assert result is None

    def test_fetch_cboe_options_chain_malformed(self) -> None:
        result = fetch_cboe_options_chain("AAPL", payload={"data": {"options": []}})
        assert result is None
