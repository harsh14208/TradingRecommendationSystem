"""Tests for the cross-sectional h=63 paper sleeve."""

from __future__ import annotations

import pandas as pd
import pytest

from services import cross_sectional_sleeve as cs


def _history(n: int = 260, price: float = 100.0) -> pd.DataFrame:
    """Return a minimal OHLCV history that satisfies the h=63 feature window."""
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


def _monkeypatch_score(monkeypatch, pct_by_ticker: dict[str, float]) -> None:
    """Replace the h=63 batch scorer with a deterministic percentile map."""
    from services import cross_sectional_shadow as css

    def _fake_score(_histories):
        return pct_by_ticker

    monkeypatch.setattr(css, "score_batch_h63", _fake_score)
    monkeypatch.setattr(css, "_MIN_NAMES", 1)


def test_build_book_top_bottom_decile(monkeypatch) -> None:
    """Top decile becomes BUY, bottom decile becomes SELL."""
    _monkeypatch_score(monkeypatch, {"A": 5.0, "B": 15.0, "C": 85.0, "D": 95.0})
    histories = {t: _history(price=10.0 * i) for i, t in enumerate(["A", "B", "C", "D"], start=1)}
    long_leg, short_leg, pct = cs.build_cross_sectional_book(histories)
    assert set(long_leg) == {"D"}
    assert set(short_leg) == {"A"}
    assert pct["D"] == 95.0


def test_make_sleeve_signals_entries_only(monkeypatch) -> None:
    """Entry signals are produced with shadow cohort and sleeve notional."""
    _monkeypatch_score(monkeypatch, {"A": 5.0, "B": 95.0})
    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}
    signals = cs.make_cross_sectional_sleeve_signals(histories, sleeve_capital=10_000.0)

    assert len(signals) == 2
    actions = {s["ticker"]: s["action"] for s in signals}
    assert actions == {"A": "SELL", "B": "BUY"}

    for sig in signals:
        assert sig["cohort"] == "shadow"
        assert sig["sleeve"] == "CrossSectional"
        assert sig["style"] == "position"
        assert sig["recommendedHoldDays"] == 63
        assert sig["confidence"] >= 40.0
        assert sig["sleeve_notional"] == pytest.approx(5_000.0, rel=1e-3)
        assert not sig.get("sleeve_exit", False)


def test_make_sleeve_signals_exits_for_stale_positions(monkeypatch) -> None:
    """A ticker that drops out of the desired book generates an exit signal."""
    _monkeypatch_score(monkeypatch, {"A": 95.0})  # only A is long today
    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}
    active = {"B": "BUY"}  # B was long yesterday but is no longer in the book

    signals = cs.make_cross_sectional_sleeve_signals(histories, 10_000.0, active_positions=active)

    entry = next(s for s in signals if s["ticker"] == "A")
    exit_sig = next(s for s in signals if s["ticker"] == "B")

    assert entry["action"] == "BUY"
    assert exit_sig["action"] == "SELL"
    assert exit_sig.get("sleeve_exit") is True
    assert exit_sig["sleeve_notional"] is None


def test_make_sleeve_signals_no_exit_when_still_desired(monkeypatch) -> None:
    """No exit signal is emitted when a ticker remains in the same leg."""
    _monkeypatch_score(monkeypatch, {"A": 95.0, "B": 5.0})
    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}
    active = {"A": "BUY", "B": "SELL"}

    signals = cs.make_cross_sectional_sleeve_signals(histories, 10_000.0, active_positions=active)

    assert len(signals) == 2
    assert all(not s.get("sleeve_exit") for s in signals)


def test_make_sleeve_signals_closes_short_on_exit(monkeypatch) -> None:
    """A short position that drops out of the book generates a BUY cover signal."""
    _monkeypatch_score(monkeypatch, {"A": 95.0})
    histories = {"A": _history(price=10.0), "B": _history(price=20.0)}
    active = {"B": "SELL"}

    signals = cs.make_cross_sectional_sleeve_signals(histories, 10_000.0, active_positions=active)

    cover = next(s for s in signals if s["ticker"] == "B")
    assert cover["action"] == "BUY"
    assert cover.get("sleeve_exit") is True


def test_target_sleeve_capital_positive_allocation() -> None:
    """CrossSectional sleeve receives a positive risk-adjusted allocation."""
    sharpes = {"MR": 0.96, "CrossSectional": 0.55, "Trend": 0.0}
    vols = {"MR": 0.044, "CrossSectional": 0.126, "Trend": 0.12}
    alloc = cs.target_sleeve_capital(100_000.0, sharpes, vols)
    assert 0.0 < alloc <= 50_000.0


def test_target_sleeve_capital_zero_on_no_equity() -> None:
    """Zero equity yields zero allocation."""
    assert cs.target_sleeve_capital(0.0, {"CrossSectional": 0.55}) == 0.0


def test_make_sleeve_signals_empty_when_model_fails(monkeypatch) -> None:
    """If the scorer returns nothing and there are no active positions, signals are empty."""
    _monkeypatch_score(monkeypatch, {})
    histories = {"A": _history(price=10.0)}
    assert cs.make_cross_sectional_sleeve_signals(histories, 10_000.0) == []
