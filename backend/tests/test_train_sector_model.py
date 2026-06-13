"""
Tests for sector-specific XGBoost entry model training and QENG-1c promotion
registry flow (§117).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import select

from database import AsyncSessionLocal, init_db
from models import ActionAuditLog, ModelRegistry, ResearchExperiment


def _make_indicator_df(start_date: datetime, n: int, label_seed: int) -> pd.DataFrame:
    """Build a deterministic indicator DataFrame indexed by date.

    Features are coerced toward the label so the model can learn a trivial
    separable pattern.  label_seed toggles the mean of the features.
    """
    dates = pd.date_range(start=start_date, periods=n, freq="B")
    rng = np.random.default_rng(seed=abs(label_seed) + 1)
    base = float(label_seed)
    df = pd.DataFrame(
        {
            "bb_pct_b": rng.normal(base + 0.35, 0.05, n),
            "ibs": rng.normal(base + 0.35, 0.05, n),
            "vwap_pct": rng.normal(base * 2.0 - 1.0, 0.1, n),
            "rsi": np.clip(rng.normal(40.0 + base * 15.0, 5.0, n), 10.0, 90.0),
            "adx": rng.normal(20.0, 3.0, n),
            "rvol": rng.normal(1.0, 0.1, n),
            "price_zscore": rng.normal(base * 1.5 - 0.75, 0.15, n),
            "ou_halflife": rng.normal(5.0, 1.0, n),
            "hurst": rng.normal(0.40, 0.03, n),
        },
        index=dates,
    )
    return df


def _make_trades(start_date: datetime, n: int, label: int) -> pd.DataFrame:
    """Build a trade DataFrame for a single ticker."""
    dates = pd.date_range(start=start_date, periods=n, freq="B")
    net = 2.5 if label == 1 else -2.5
    return pd.DataFrame(
        {
            "date": dates,
            "net_pct": [net] * n,
            "atr_pct": [2.0] * n,
            "dow": [d.weekday() for d in dates],
        }
    )


def _make_all_results(tickers: list[str], n_per_ticker: int, start_date: datetime) -> list:
    """Return all_results tuple list usable by train_sector_model."""
    results = []
    for ticker in tickers:
        # Alternate label per row so every train/test split contains both classes.
        indicators = _make_indicator_df(start_date, n_per_ticker, label_seed=0)
        for i in range(n_per_ticker):
            indicators.iloc[i, :] = _make_indicator_df(start_date + timedelta(days=i), n=1, label_seed=i % 2).iloc[0, :]
        trades = _make_trades(start_date, n_per_ticker, label=0)
        trades["net_pct"] = [2.5 if i % 2 == 0 else -2.5 for i in range(n_per_ticker)]
        results.append((ticker, trades, 0.0, indicators))
    return results


def _vix_dict(start_date: datetime, n: int) -> dict:
    dates = pd.date_range(start=start_date, periods=n, freq="B")
    return {pd.Timestamp(d): 18.0 for d in dates}


@pytest.fixture(autouse=True, scope="module")
def _setup_test_db():
    import os

    db_path = "./test_db.sqlite"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    asyncio.run(init_db())


@pytest.mark.asyncio
async def test_train_sector_model_insufficient_data():
    """Sector models require a minimum backtest sample size to train."""
    from scripts.train_backtest_ml import train_sector_model

    start = datetime(2020, 1, 1)
    all_results = _make_all_results(["JPM", "BAC"], n_per_ticker=5, start_date=start)
    vix = _vix_dict(start, 10)

    meta = train_sector_model(
        all_results,
        vix,
        sector_etf="XLF",
        sector_tickers={"JPM", "BAC"},
        champion_auc=None,
        min_samples=100,
    )
    assert meta is None


@pytest.mark.asyncio
async def test_train_sector_model_beat_champion(tmp_path, monkeypatch):
    """A sector model that beats the champion is saved and returns metadata."""
    from scripts.train_backtest_ml import train_sector_model

    monkeypatch.setattr("scripts.train_backtest_ml._DATA_DIR", tmp_path)

    start = datetime(2018, 1, 1)
    n_per_ticker = 80
    all_results = _make_all_results(["JPM", "BAC"], n_per_ticker=n_per_ticker, start_date=start)
    vix = _vix_dict(start, n_per_ticker)

    meta = train_sector_model(
        all_results,
        vix,
        sector_etf="XLF",
        sector_tickers={"JPM", "BAC"},
        champion_auc=None,
        min_samples=100,
    )
    assert meta is not None
    assert meta["sector_etf"] == "XLF"
    assert meta["deployed"] is True
    assert meta["n_total"] >= 100
    assert meta["model_id"].startswith("sector-entry-XLF-")
    assert (tmp_path / "backtest_ml_model_XLF.json").exists()
    assert (tmp_path / "backtest_ml_features_XLF.json").exists()


@pytest.mark.asyncio
async def test_train_sector_model_records_registry():
    """Training writes a pending ModelRegistry + ResearchExperiment row."""
    from scripts.train_backtest_ml import _record_sector_model_pending

    meta = {
        "model_id": "sector-entry-XLF-1234567890",
        "sector_etf": "XLF",
        "n_total": 120,
        "n_train": 84,
        "n_test": 36,
        "oos_auc": 0.62,
        "cv_auc_mean": 0.60,
        "feature_names": ["bb_pct_b", "ibs"],
        "tickers": ["JPM", "BAC"],
    }

    await _record_sector_model_pending(meta)

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == meta["model_id"]))
        model = res.scalar_one_or_none()
        assert model is not None
        assert model.approval_decision == "pending"
        assert model.is_active is False
        assert model.metrics["oos_auc"] == 0.62

        exp_res = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.search_space == {"model_id": meta["model_id"], "sector": meta["sector_etf"]}
            )
        )
        exp = exp_res.scalar_one_or_none()
        assert exp is not None
        assert exp.decision == "pending"
        assert exp.promotion_status == "pending"

        audit_res = await db.execute(
            select(ActionAuditLog)
            .where(ActionAuditLog.action == "train_sector_model")
            .order_by(ActionAuditLog.created_at.desc())
        )
        audit = audit_res.scalars().first()
        assert audit is not None
        assert audit.details["model_id"] == meta["model_id"]


@pytest.mark.asyncio
async def test_promote_sector_model_checklist(tmp_path, monkeypatch):
    """QENG-1c promotion CLI activates the model and creates a live experiment."""
    import argparse

    from scripts.promote_sector_model import promote_sector_model
    from scripts.train_backtest_ml import _record_sector_model_pending

    # Seed a pending registry row.
    meta = {
        "model_id": "sector-entry-XLP-1234567890",
        "sector_etf": "XLP",
        "n_total": 110,
        "n_train": 77,
        "n_test": 33,
        "oos_auc": 0.63,
        "cv_auc_mean": 0.61,
        "feature_names": ["bb_pct_b"],
    }
    await _record_sector_model_pending(meta)

    args = argparse.Namespace(
        sector="XLP",
        model_id=meta["model_id"],
        oos_auc=0.63,
        cost_adjusted_sharpe=0.35,
        rollback_plan="Deactivate model and restore buy_thresh=999",
        expiration_days=30,
    )

    await promote_sector_model(args)

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == meta["model_id"]))
        model = res.scalar_one_or_none()
        assert model is not None
        assert model.approval_decision == "approved"
        assert model.is_active is True

        exp_res = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.decision == "promoted",
                ResearchExperiment.promotion_status == "live",
                ResearchExperiment.search_space == {"model_id": meta["model_id"], "sector": meta["sector_etf"]},
            )
        )
        exp = exp_res.scalar_one_or_none()
        assert exp is not None
        retest = datetime.fromisoformat(exp.dsr_pbo["retest_date"])
        assert retest > datetime.utcnow() + timedelta(days=29)

        audit_res = await db.execute(
            select(ActionAuditLog)
            .where(ActionAuditLog.action == "promote_sector_model")
            .order_by(ActionAuditLog.created_at.desc())
        )
        audit = audit_res.scalars().first()
        assert audit is not None
        assert audit.details["sector"] == "XLP"


@pytest.mark.asyncio
async def test_promote_sector_model_rejects_low_metrics(tmp_path, monkeypatch):
    """Promotion CLI must reject models that do not meet the QENG-1c bar."""
    import argparse

    from scripts.promote_sector_model import promote_sector_model
    from scripts.train_backtest_ml import _record_sector_model_pending

    meta = {
        "model_id": "sector-entry-XLU-1234567890",
        "sector_etf": "XLU",
        "n_total": 50,
        "n_train": 35,
        "n_test": 15,
        "oos_auc": 0.52,
        "cv_auc_mean": 0.50,
        "feature_names": ["bb_pct_b"],
    }
    await _record_sector_model_pending(meta)

    args = argparse.Namespace(
        sector="XLU",
        model_id=meta["model_id"],
        oos_auc=0.52,
        cost_adjusted_sharpe=-0.05,
        rollback_plan="none",
        expiration_days=30,
    )

    await promote_sector_model(args)

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == meta["model_id"]))
        model = res.scalar_one_or_none()
        # Should remain pending because the checklist rejected activation.
        assert model is not None
        assert model.approval_decision == "pending"
        assert model.is_active is False

        exp_res = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.search_space.contains({"model_id": meta["model_id"]}),
                ResearchExperiment.decision == "promoted",
            )
        )
        assert exp_res.scalar_one_or_none() is None
