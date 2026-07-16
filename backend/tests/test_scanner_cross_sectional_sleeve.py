"""Scanner integration tests for the cross-sectional h=63 paper sleeve."""

from __future__ import annotations

import pandas as pd
import pytest

from services import scanner
from services import cross_sectional_shadow as css


def _history(n: int = 260, price: float = 100.0) -> pd.DataFrame:
    rng = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=n, freq="B")
    closes = [price * (1.001**i) for i in range(n)]
    return pd.DataFrame(
        {
            "Open": closes,
            "High": closes,
            "Low": closes,
            "Close": closes,
            "Volume": [1_000_000] * n,
        },
        index=rng,
    )


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def scalars(self):
        return self


class _FakeSession:
    def __init__(self, active_rows=None):
        self._active_rows = active_rows or []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, _stmt):
        return _FakeResult(self._active_rows)


class _FakeSessionLocal:
    def __init__(self, active_rows=None):
        self._active_rows = active_rows

    def __call__(self):
        return _FakeSession(self._active_rows)


@pytest.fixture
def _patch_score(monkeypatch):
    """Install a deterministic h=63 scorer."""

    def _score(_histories):
        return {"A": 95.0, "B": 5.0}

    monkeypatch.setattr(css, "score_batch_h63", _score)
    monkeypatch.setattr(css, "_MIN_NAMES", 1)


@pytest.fixture
def _patch_account(monkeypatch):
    """Return a fixed $100k Alpaca paper account."""

    async def _get_account(_key, _secret):
        return {"equity": "100000.00", "buying_power": "100000.00"}

    from services import alpaca_rest

    monkeypatch.setattr(alpaca_rest, "get_account", _get_account)


@pytest.mark.asyncio
async def test_build_cross_sectional_sleeve_signals_integration(monkeypatch, _patch_score, _patch_account) -> None:
    """Scanner helper builds shadow-cohort sleeve signals using live equity + active positions."""
    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}

    # No active sleeve positions today.
    monkeypatch.setattr(scanner, "AsyncSessionLocal", _FakeSessionLocal([]))

    class _MockSettings:
        alpaca_api_key = "test_key"
        alpaca_api_secret = type("S", (), {"get_secret_value": lambda self: "test_secret"})()

    signals = await scanner._build_cross_sectional_sleeve_signals(histories, _MockSettings())

    assert len(signals) == 2
    actions = {s["ticker"]: s["action"] for s in signals}
    assert actions == {"A": "BUY", "B": "SELL"}
    for sig in signals:
        assert sig["cohort"] == "shadow"
        assert sig["sleeve"] == "CrossSectional"
        assert sig["sleeve_notional"] is not None and sig["sleeve_notional"] > 0


@pytest.mark.asyncio
async def test_build_cross_sectional_sleeve_signals_with_exit(monkeypatch, _patch_score, _patch_account) -> None:
    """A stale sleeve position that is no longer in the book generates an exit signal."""
    histories = {"A": _history(price=10.0), "B": _history(price=20.0), "C": _history(price=30.0)}

    # C was long yesterday but is not in today's top/bottom decile.
    monkeypatch.setattr(
        scanner, "AsyncSessionLocal", _FakeSessionLocal([type("R", (), {"ticker": "C", "action": "BUY"})])
    )

    class _MockSettings:
        alpaca_api_key = "test_key"
        alpaca_api_secret = type("S", (), {"get_secret_value": lambda self: "test_secret"})()

    signals = await scanner._build_cross_sectional_sleeve_signals(histories, _MockSettings())

    entry_tickers = {s["ticker"] for s in signals if not s.get("sleeve_exit")}
    exit_tickers = {s["ticker"] for s in signals if s.get("sleeve_exit")}
    assert entry_tickers == {"A", "B"}
    assert exit_tickers == {"C"}


@pytest.mark.asyncio
async def test_build_cross_sectional_sleeve_signals_skips_without_equity(monkeypatch, _patch_score) -> None:
    """If Alpaca equity is unavailable, the helper returns an empty list gracefully."""

    async def _empty_account(_key, _secret):
        return {"equity": "0.00", "buying_power": "0.00"}

    from services import alpaca_rest

    monkeypatch.setattr(alpaca_rest, "get_account", _empty_account)

    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}

    class _MockSettings:
        alpaca_api_key = "test_key"
        alpaca_api_secret = type("S", (), {"get_secret_value": lambda self: "test_secret"})()

    signals = await scanner._build_cross_sectional_sleeve_signals(histories, _MockSettings())
    assert signals == []
