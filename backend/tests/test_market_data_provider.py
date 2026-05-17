import pandas as pd
import pytest
from unittest.mock import AsyncMock, patch

from services import market_data


def _df(close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({
        "Open": [close - 1, close],
        "High": [close, close + 1],
        "Low": [close - 2, close - 1],
        "Close": [close - 1, close],
        "Volume": [1000, 1200],
    })


@pytest.mark.asyncio
async def test_histories_batch_prefers_polygon_and_falls_back_missing():
    with patch("services.polygon_client.get_polygon_histories_batch", new=AsyncMock(return_value={"AAPL": _df(200)})):
        with patch.object(market_data, "_fetch_histories_batch", return_value={"MSFT": _df(300)}) as yf:
            out = await market_data.get_histories_batch(["AAPL", "MSFT"])

    assert set(out) == {"AAPL", "MSFT"}
    assert out["AAPL"]["Close"].iloc[-1] == 200
    yf.assert_called_once()


@pytest.mark.asyncio
async def test_quotes_batch_prefers_polygon_and_falls_back_missing():
    polygon_quotes = [{"t": "AAPL", "p": 200.0, "c": 1.0}]
    yf_quotes = [{"t": "MSFT", "p": 300.0, "c": -1.0}]
    with patch("services.polygon_client.get_polygon_quotes_batch", new=AsyncMock(return_value=polygon_quotes)):
        with patch.object(market_data, "_yf_is_blocked", return_value=False):
            with patch.object(market_data, "_fetch_quotes_batch", return_value=yf_quotes):
                out = await market_data.get_quotes_batch(["AAPL", "MSFT"])

    assert out == polygon_quotes + yf_quotes


@pytest.mark.asyncio
async def test_infos_batch_prefers_polygon_and_falls_back_missing():
    with patch("services.polygon_client.get_polygon_infos_batch", new=AsyncMock(return_value={"AAPL": {"company": "Apple Inc."}})):
        with patch.object(market_data, "_rate_limited", new=AsyncMock(return_value={"company": "Microsoft Corporation"})):
            out = await market_data.get_infos_sequential(["AAPL", "MSFT"])

    assert out["AAPL"]["company"] == "Apple Inc."
    assert out["MSFT"]["company"] == "Microsoft Corporation"
