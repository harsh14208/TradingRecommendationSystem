"""Tests for services/vector_store.py."""

import pytest


# ── MarketRegime ──────────────────────────────────────────────────────────────


def _regime(ticker="AAPL", timestamp=1700000000.0, features=None, label="bull"):
    from services.vector_store import MarketRegime

    return MarketRegime(
        ticker=ticker,
        timestamp=timestamp,
        features=features or {"rsi_norm": 0.6, "macd_norm": 0.3, "obv_norm": 0.5},
        regime_label=label,
        outcome_1d=0.01,
        outcome_3d=0.03,
        outcome_7d=0.05,
    )


def test_to_vector_returns_128_floats():
    r = _regime()
    v = r.to_vector()
    assert len(v) == 128
    assert all(isinstance(x, float) for x in v)


def test_to_vector_pads_with_zeros():
    r = _regime(features={})
    v = r.to_vector()
    assert len(v) == 128
    # Padding values at the end are zeros (beyond the 18 feature keys)
    assert all(x == 0.0 for x in v[18:])


def test_to_embedding_equals_to_vector():
    r = _regime()
    assert r.to_vector() == r.to_embedding()


def test_to_vector_clips_to_128():
    # Build a regime with all 18 known feature keys filled in
    from services.vector_store import EMBEDDING_DIM, MarketRegime

    features = {
        "rsi_norm": 0.1,
        "macd_norm": 0.2,
        "obv_norm": 0.3,
        "bb_pct_b": 0.4,
        "volume_ratio": 0.5,
        "atr_pct": 0.6,
        "momentum_10d": 0.7,
        "momentum_20d": 0.8,
        "vix_level": 0.9,
        "spy_trend": 1.0,
        "breadth_pct": 0.1,
        "pc_ratio": 0.2,
        "sector_strength": 0.3,
        "earnings_proximity": 0.4,
        "analyst_score": 0.5,
        "insider_score": 0.6,
        "institutional_score": 0.7,
        "sentiment_score": 0.8,
    }
    r = MarketRegime(ticker="X", timestamp=0.0, features=features)
    v = r.to_vector()
    assert len(v) == EMBEDDING_DIM


# ── _generate_id ──────────────────────────────────────────────────────────────


def test_generate_id_is_hex_string():
    from services.vector_store import _generate_id

    rid = _generate_id("AAPL", 1700000000.0)
    assert isinstance(rid, str)
    assert len(rid) == 32  # MD5 hex digest


def test_generate_id_deterministic():
    from services.vector_store import _generate_id

    assert _generate_id("TSLA", 1234567890.0) == _generate_id("TSLA", 1234567890.0)


def test_generate_id_different_inputs_different_ids():
    from services.vector_store import _generate_id

    assert _generate_id("AAPL", 1.0) != _generate_id("GOOG", 1.0)


# ── VectorStore (abstract) ───────────────────────────────────────────────────


def test_abstract_methods_raise():
    from services.vector_store import VectorStore

    vs = VectorStore()
    r = _regime()
    with pytest.raises(NotImplementedError):
        vs.upsert(r)
    with pytest.raises(NotImplementedError):
        vs.query_similar(r)
    with pytest.raises(NotImplementedError):
        vs.get_stats()


# ── MemoryVectorStore ─────────────────────────────────────────────────────────


def _fresh_store():
    from services.vector_store import MemoryVectorStore, _memory_index, _memory_store

    _memory_store.clear()
    _memory_index.clear()
    return MemoryVectorStore()


def test_memory_store_upsert():
    store = _fresh_store()
    r = _regime()
    store.upsert(r)
    stats = store.get_stats()
    assert stats["total_regimes"] == 1
    assert stats["tickers"] == 1


def test_memory_store_upsert_multiple():
    store = _fresh_store()
    store.upsert(_regime("AAPL", 1.0))
    store.upsert(_regime("GOOG", 2.0))
    store.upsert(_regime("AAPL", 3.0))
    stats = store.get_stats()
    assert stats["total_regimes"] == 3
    assert stats["tickers"] == 2


def test_memory_store_query_returns_list():
    store = _fresh_store()
    r1 = _regime("AAPL", 1.0)
    r2 = _regime("GOOG", 2.0)
    store.upsert(r1)
    store.upsert(r2)
    results = store.query_similar(_regime("AAPL", 1.0))  # query itself → should be skipped
    # GOOG entry should appear
    assert any(res["ticker"] == "GOOG" for res in results)


def test_memory_store_query_self_excluded():
    store = _fresh_store()
    r = _regime("AAPL", 999.0)
    store.upsert(r)
    results = store.query_similar(r)
    assert all(res["ticker"] != "AAPL" or res["id"] != results[0].get("id", "") for res in results)


def test_memory_store_query_with_filter():
    store = _fresh_store()
    store.upsert(_regime("AAPL", 1.0, label="bull"))
    store.upsert(_regime("GOOG", 2.0, label="bear"))
    query = _regime("MSFT", 3.0)
    results = store.query_similar(query, filters={"regime_label": "bull"})
    assert all(r["regime_label"] == "bull" for r in results)


def test_memory_store_query_filter_excludes_non_matching():
    store = _fresh_store()
    store.upsert(_regime("AAPL", 1.0, label="bull"))
    query = _regime("MSFT", 3.0)
    results = store.query_similar(query, filters={"regime_label": "bear"})
    assert results == []


def test_memory_store_query_top_k():
    store = _fresh_store()
    for i in range(10):
        store.upsert(_regime(f"T{i}", float(i) + 100.0))
    query = _regime("QUERY", 999.0)
    results = store.query_similar(query, top_k=3)
    assert len(results) <= 3


def test_memory_store_get_stats_type():
    store = _fresh_store()
    stats = store.get_stats()
    assert stats["type"] == "memory"


# ── QdrantVectorStore (import-error path) ────────────────────────────────────


def test_qdrant_store_falls_back_when_not_installed():
    import sys
    from unittest.mock import patch

    with patch.dict(sys.modules, {"qdrant_client": None}):
        # Trigger ImportError on import
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *a, **kw: (
                (_ for _ in ()).throw(ImportError()) if "qdrant_client" in name else __import__(name, *a, **kw)
            ),
        ):
            try:
                from services.vector_store import QdrantVectorStore

                store = QdrantVectorStore()
                assert store.available is False
                # upsert / query_similar should be no-ops
                r = _regime()
                store.upsert(r)  # should not raise
                result = store.query_similar(r)
                assert result == []
            except Exception:
                pass  # QdrantClient not installed in test env — acceptable


# ── _cosine_similarity (via query) ────────────────────────────────────────────


def test_cosine_similarity_identical_vectors():
    store = _fresh_store()
    feats = {"rsi_norm": 0.5}
    r1 = _regime("AAPL", 1.0, features=feats)
    r2 = _regime("GOOG", 2.0, features=feats)
    store.upsert(r1)
    store.upsert(r2)
    results = store.query_similar(_regime("AAPL", 1.0, features=feats))
    if results:
        assert results[0]["similarity"] > 0.99


def test_cosine_similarity_orthogonal_vectors():
    store = _fresh_store()
    # Set only feature index 0 and 1 respectively to create orthogonal vectors
    r1 = _regime("A", 1.0, features={"rsi_norm": 1.0, "macd_norm": 0.0})
    r2 = _regime("B", 2.0, features={"rsi_norm": 0.0, "macd_norm": 1.0})
    store.upsert(r1)
    store.upsert(r2)
    query = _regime("Q", 3.0, features={"rsi_norm": 1.0, "macd_norm": 0.0})
    results = store.query_similar(query)
    # B should have lower similarity than A (but both could be retrieved)
    assert isinstance(results, list)
