"""
Pre-warmed Vector Store for Market Regime Analysis.

This module provides a vector database abstraction for storing and querying
market regime embeddings. When a new signal triggers, the agent can query:
"When has RSI, MACD, and OBV looked like this before, and what was the 48-hour outcome?"

Supports Qdrant, Milvus, or in-memory fallback (Chroma/FAISS).
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
VECTOR_DB_TYPE = "memory"  # Options: "qdrant", "milvus", "memory"
COLLECTION_NAME = "market_regimes"
EMBEDDING_DIM = 128  # Matches the feature vector size

# In-memory fallback storage
_memory_store: dict[str, dict] = {}
_memory_index: dict[str, list[float]] = {}


@dataclass
class MarketRegime:
    """Represents a market regime snapshot for vector storage."""

    ticker: str
    timestamp: float
    features: dict[str, float]  # Normalized indicator values
    outcome_1d: Optional[float] = None
    outcome_3d: Optional[float] = None
    outcome_7d: Optional[float] = None
    regime_label: str = ""  # "bull", "bear", "neutral", "volatile"
    metadata: dict = field(default_factory=dict)

    def to_vector(self) -> list[float]:
        """Convert features to a normalized embedding vector."""
        # Feature ordering must be consistent
        feature_keys = [
            "rsi_norm",
            "macd_norm",
            "obv_norm",
            "bb_pct_b",
            "volume_ratio",
            "atr_pct",
            "momentum_10d",
            "momentum_20d",
            "vix_level",
            "spy_trend",
            "breadth_pct",
            "pc_ratio",
            "sector_strength",
            "earnings_proximity",
            "analyst_score",
            "insider_score",
            "institutional_score",
            "sentiment_score",
        ]
        vector = [self.features.get(k, 0.0) for k in feature_keys]
        # Pad to EMBEDDING_DIM if needed
        while len(vector) < EMBEDDING_DIM:
            vector.append(0.0)
        return vector[:EMBEDDING_DIM]

    def to_embedding(self) -> list[float]:
        """Generate embedding using simple feature normalization."""
        return self.to_vector()


def _generate_id(ticker: str, timestamp: float) -> str:
    """Generate a unique ID for a market regime."""
    key = f"{ticker}_{timestamp}"
    return hashlib.md5(key.encode()).hexdigest()


class VectorStore:
    """Abstract vector store interface."""

    def upsert(self, regime: MarketRegime):
        """Store a market regime embedding."""
        raise NotImplementedError

    def query_similar(
        self,
        regime: MarketRegime,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """Find similar historical market regimes."""
        raise NotImplementedError

    def get_stats(self) -> dict:
        """Return store statistics."""
        raise NotImplementedError


class MemoryVectorStore(VectorStore):
    """In-memory vector store fallback using simple cosine similarity."""

    def upsert(self, regime: MarketRegime):
        regime_id = _generate_id(regime.ticker, regime.timestamp)
        vector = regime.to_vector()
        _memory_store[regime_id] = {
            "ticker": regime.ticker,
            "timestamp": regime.timestamp,
            "outcome_1d": regime.outcome_1d,
            "outcome_3d": regime.outcome_3d,
            "outcome_7d": regime.outcome_7d,
            "regime_label": regime.regime_label,
            "metadata": regime.metadata,
        }
        _memory_index[regime_id] = vector
        logger.debug(f"Stored regime {regime_id} for {regime.ticker}")

    def query_similar(
        self,
        regime: MarketRegime,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """Find similar regimes using cosine similarity."""
        query_vector = regime.to_vector()
        results = []

        for reg_id, stored_vector in _memory_index.items():
            # Skip self
            if reg_id == _generate_id(regime.ticker, regime.timestamp):
                continue

            # Apply filters
            stored = _memory_store[reg_id]
            if filters:
                skip = False
                for key, value in filters.items():
                    if stored.get(key) != value:
                        skip = True
                        break
                if skip:
                    continue

            # Compute cosine similarity
            similarity = _cosine_similarity(query_vector, stored_vector)
            results.append(
                {
                    "id": reg_id,
                    "similarity": similarity,
                    **stored,
                }
            )

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_stats(self) -> dict:
        return {
            "type": "memory",
            "total_regimes": len(_memory_store),
            "tickers": len(set(v["ticker"] for v in _memory_store.values())),
        }


class QdrantVectorStore(VectorStore):
    """Qdrant vector database implementation."""

    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None):
        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(url=url, api_key=api_key)
            self._ensure_collection()
            self.available = True
        except ImportError:
            logger.warning("Qdrant client not installed, falling back to memory store")
            self.available = False
            self.client = None

    def _ensure_collection(self):
        from qdrant_client.http import models

        try:
            self.client.get_collection(COLLECTION_NAME)
        except Exception:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, regime: MarketRegime):
        if not self.available:
            return
        from qdrant_client.http import models

        regime_id = _generate_id(regime.ticker, regime.timestamp)
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=regime_id,
                    vector=regime.to_vector(),
                    payload={
                        "ticker": regime.ticker,
                        "timestamp": regime.timestamp,
                        "outcome_1d": regime.outcome_1d,
                        "outcome_3d": regime.outcome_3d,
                        "outcome_7d": regime.outcome_7d,
                        "regime_label": regime.regime_label,
                        **regime.metadata,
                    },
                )
            ],
        )

    def query_similar(
        self,
        regime: MarketRegime,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        if not self.available:
            return []
        from qdrant_client.http import models

        query_filter = None
        if filters:
            conditions = [
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value),
                )
                for key, value in filters.items()
            ]
            query_filter = models.Filter(must=conditions)

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=regime.to_vector(),
            limit=top_k,
            query_filter=query_filter,
        )
        return [
            {
                "id": r.id,
                "similarity": r.score,
                **r.payload,
            }
            for r in results
        ]

    def get_stats(self) -> dict:
        if not self.available:
            return {"type": "qdrant", "available": False}
        info = self.client.get_collection(COLLECTION_NAME)
        return {
            "type": "qdrant",
            "available": True,
            "total_regimes": info.points_count,
        }


class MilvusVectorStore(VectorStore):
    """Milvus vector database implementation."""

    def __init__(self, uri: str = "http://localhost:19530"):
        try:
            from pymilvus import Collection, connections, utility

            connections.connect(uri=uri)
            self.uri = uri
            if not utility.has_collection(COLLECTION_NAME):
                self._create_collection()
            self.collection = Collection(COLLECTION_NAME)
            self.available = True
        except ImportError:
            logger.warning("Milvus client not installed, falling back to memory store")
            self.available = False
            self.collection = None

    def _create_collection(self):
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, utility

        fields = [
            FieldSchema(name="id", dtype=DataType.VarChar, is_primary=True, max_length=64),
            FieldSchema(name="ticker", dtype=DataType.VarChar, max_length=20),
            FieldSchema(name="timestamp", dtype=DataType.Double),
            FieldSchema(name="outcome_1d", dtype=DataType.Float),
            FieldSchema(name="outcome_3d", dtype=DataType.Float),
            FieldSchema(name="outcome_7d", dtype=DataType.Float),
            FieldSchema(name="regime_label", dtype=DataType.VarChar, max_length=20),
            FieldSchema(name="embedding", dtype=DataType.FloatVector, dim=EMBEDDING_DIM),
        ]
        schema = CollectionSchema(fields=fields, description="Market regime embeddings")
        utility.create_collection(collection_name=COLLECTION_NAME, schema=schema)
        # Create index for vector search
        collection = Collection(COLLECTION_NAME)
        collection.create_index(
            field_name="embedding",
            index_params={"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}},
        )

    def upsert(self, regime: MarketRegime):
        if not self.available:
            return
        regime_id = _generate_id(regime.ticker, regime.timestamp)
        data = [
            [regime_id],
            [regime.ticker],
            [regime.timestamp],
            [regime.outcome_1d or 0.0],
            [regime.outcome_3d or 0.0],
            [regime.outcome_7d or 0.0],
            [regime.regime_label],
            [regime.to_vector()],
        ]
        self.collection.insert(data)
        self.collection.flush()

    def query_similar(
        self,
        regime: MarketRegime,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        if not self.available:
            return []
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        expr = None
        if filters:
            conditions = " and ".join(
                f'{k} == "{v}"' if isinstance(v, str) else f"{k} == {v}" for k, v in filters.items()
            )
            expr = conditions

        self.collection.load()
        results = self.collection.search(
            data=[regime.to_vector()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["ticker", "timestamp", "outcome_1d", "outcome_3d", "outcome_7d", "regime_label"],
        )
        return [
            {
                "id": hit.id,
                "similarity": hit.score,
                "ticker": hit.entity.get("ticker"),
                "timestamp": hit.entity.get("timestamp"),
                "outcome_1d": hit.entity.get("outcome_1d"),
                "outcome_3d": hit.entity.get("outcome_3d"),
                "outcome_7d": hit.entity.get("outcome_7d"),
                "regime_label": hit.entity.get("regime_label"),
            }
            for hit in results[0]
        ]

    def get_stats(self) -> dict:
        if not self.available:
            return {"type": "milvus", "available": False}
        return {
            "type": "milvus",
            "available": True,
            "total_regimes": self.collection.num_entities,
        }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# Factory function
def get_vector_store() -> VectorStore:
    """Get the appropriate vector store based on configuration."""
    if VECTOR_DB_TYPE == "qdrant":
        import os

        store = QdrantVectorStore(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        if store.available:
            return store
        logger.warning("Qdrant unavailable, falling back to memory store")
        return MemoryVectorStore()
    elif VECTOR_DB_TYPE == "milvus":
        import os

        store = MilvusVectorStore(uri=os.getenv("MILVUS_URI", "http://localhost:19530"))
        if store.available:
            return store
        logger.warning("Milvus unavailable, falling back to memory store")
        return MemoryVectorStore()
    else:
        return MemoryVectorStore()


# Global store instance
_vector_store: Optional[VectorStore] = None


def init_vector_store():
    """Initialize the global vector store."""
    global _vector_store
    _vector_store = get_vector_store()
    logger.info(f"Vector store initialized: {_vector_store.get_stats()}")
    return _vector_store


def get_store() -> VectorStore:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = init_vector_store()
    return _vector_store


def store_regime(
    ticker: str,
    features: dict[str, float],
    outcome_1d: Optional[float] = None,
    outcome_3d: Optional[float] = None,
    outcome_7d: Optional[float] = None,
    regime_label: str = "",
    metadata: Optional[dict] = None,
):
    """Convenience function to store a market regime."""
    regime = MarketRegime(
        ticker=ticker,
        timestamp=time.time(),
        features=features,
        outcome_1d=outcome_1d,
        outcome_3d=outcome_3d,
        outcome_7d=outcome_7d,
        regime_label=regime_label,
        metadata=metadata or {},
    )
    get_store().upsert(regime)


def query_similar_regimes(
    ticker: str,
    features: dict[str, float],
    top_k: int = 10,
    filters: Optional[dict] = None,
) -> list[dict]:
    """Convenience function to query similar market regimes."""
    regime = MarketRegime(
        ticker=ticker,
        timestamp=time.time(),
        features=features,
    )
    return get_store().query_similar(regime, top_k=top_k, filters=filters)


def get_regime_summary(similar_regimes: list[dict]) -> dict:
    """Generate a summary of similar historical regimes and their outcomes."""
    if not similar_regimes:
        return {
            "count": 0,
            "avg_outcome_1d": None,
            "avg_outcome_3d": None,
            "avg_outcome_7d": None,
            "win_rate_1d": None,
            "win_rate_3d": None,
            "win_rate_7d": None,
            "message": "No similar historical regimes found",
        }

    outcomes_1d = [r["outcome_1d"] for r in similar_regimes if r.get("outcome_1d") is not None]
    outcomes_3d = [r["outcome_3d"] for r in similar_regimes if r.get("outcome_3d") is not None]
    outcomes_7d = [r["outcome_7d"] for r in similar_regimes if r.get("outcome_7d") is not None]

    def avg(lst):
        return sum(lst) / len(lst) if lst else None

    def win_rate(lst):
        if not lst:
            return None
        wins = sum(1 for x in lst if x > 0)
        return wins / len(lst)

    # Find most common regime label
    labels = [r.get("regime_label", "") for r in similar_regimes if r.get("regime_label")]
    most_common_label = max(set(labels), key=labels.count) if labels else ""

    avg_sim = sum(r.get("similarity", 0) for r in similar_regimes) / len(similar_regimes)

    return {
        "count": len(similar_regimes),
        "avg_similarity": round(avg_sim, 3),
        "most_common_regime": most_common_label,
        "avg_outcome_1d": round(avg(outcomes_1d), 2) if outcomes_1d else None,
        "avg_outcome_3d": round(avg(outcomes_3d), 2) if outcomes_3d else None,
        "avg_outcome_7d": round(avg(outcomes_7d), 2) if outcomes_7d else None,
        "win_rate_1d": round(win_rate(outcomes_1d) * 100, 1) if outcomes_1d else None,
        "win_rate_3d": round(win_rate(outcomes_3d) * 100, 1) if outcomes_3d else None,
        "win_rate_7d": round(win_rate(outcomes_7d) * 100, 1) if outcomes_7d else None,
        "message": f"Found {len(similar_regimes)} similar market regimes (avg similarity: {avg_sim:.2f})",
    }


# ── RAG: Nearest-Neighbour Rationale Writer ────────────────────────────────────
# Retrieves the 5 most similar historical regimes from the vector store and
# generates a plain-English narrative rationale card using the LLM.
# Falls back to a template if LLM is unavailable.


def generate_rag_rationale(
    ticker: str,
    features: dict[str, float],
    signal_action: str,
    signal_confidence: float,
    top_k: int = 5,
) -> dict | None:
    """
    RAG-enhanced rationale card.
    1. Queries vector store for similar historical market setups.
    2. Builds a context string from the top-K nearest neighbours.
    3. Feeds context + current signal to local LLM for a narrative rationale.
    4. Returns a rationale dict compatible with signal_engine's rationale list.

    Returns None if no similar regimes or store is empty.
    """
    try:
        similar = query_similar_regimes(ticker, features, top_k=top_k)
        if not similar:
            return None

        summary = get_regime_summary(similar)
        n_sim = summary["count"]
        wr_7d = summary.get("win_rate_7d")
        avg_7d = summary.get("avg_outcome_7d")
        label = summary.get("most_common_regime", "mixed")

        if wr_7d is None or n_sim < 3:
            return None

        # Try LLM narration
        rag_body = None
        try:
            from services.local_llm import get_llm_client

            llm = get_llm_client()
            if llm:
                prompt = (
                    f"Ticker: {ticker}. Current signal: {signal_action} at "
                    f"{signal_confidence:.0f}% confidence. "
                    f"Found {n_sim} historically similar setups. "
                    f"In those setups: 7-day win rate was {wr_7d:.0f}%, "
                    f"avg return was {avg_7d:+.2f}%, "
                    f"most common regime was '{label}'. "
                    f"Write 2 sentences explaining what this historical pattern "
                    f"implies for the current trade setup. Be specific and concise."
                )
                rag_body = llm.generate(
                    prompt, system_prompt="You are a quantitative trading analyst writing signal rationale cards."
                )
        except Exception:
            pass

        if not rag_body:
            # Template fallback
            rag_body = (
                f"The current {ticker} setup matches {n_sim} historically similar "
                f"market regimes ('{label}' label). In those regimes, the 7-day "
                f"win rate was {wr_7d:.0f}% with an average return of "
                f"{avg_7d:+.2f}%. Historical pattern suggests "
                f"{'follow-through is likely' if (wr_7d or 0) > 55 else 'caution is warranted'}."
            )

        return {
            "src": "Vector Store",
            "head": f"RAG: {n_sim} Similar Setups — {wr_7d:.0f}% 7d Win Rate",
            "body": rag_body,
            "sentiment": "pos" if (wr_7d or 0) > 55 else "neg",
            "meta": (f"n_similar={n_sim} wr_7d={wr_7d:.0f}% avg_7d={avg_7d:+.2f}% regime={label}"),
        }
    except Exception as e:
        logger.debug(f"[vector_store] RAG rationale failed for {ticker}: {e}")
        return None


# ── Reflection Memory: store lessons from losing trades ───────────────────────

_REFLECTION_KEY_PREFIX = "reflection:"


def store_reflection(ticker: str, signal_action: str, outcome_pct: float, features: dict, lesson: str) -> None:
    """
    Save a loss reflection to the vector store so the engine can learn from it.
    Called by the automated reflection loop in scanner.py after LLM analysis.
    """
    if outcome_pct > 0:
        return  # only store lessons from losing trades
    try:
        vs = get_store()
        entry_id = f"{_REFLECTION_KEY_PREFIX}{ticker}_{int(time.time())}"
        vs.store(
            MarketRegime(
                ticker=ticker,
                timestamp=time.time(),
                features={**features, "was_loss": 1.0, "outcome_pct": outcome_pct},
                metadata={"lesson": lesson, "action": signal_action, "type": "reflection"},
            )
        )
        logger.info(f"[vector_store] Reflection stored for {ticker} ({signal_action}) loss: {lesson[:60]}")
    except Exception as e:
        logger.debug(f"[vector_store] store_reflection failed: {e}")


def query_reflections(ticker: str, features: dict, top_k: int = 3) -> list[str]:
    """
    Retrieve relevant past loss lessons for a ticker setup.
    Returns list of lesson strings (empty if no relevant reflections stored).
    """
    try:
        vs = get_store()
        reflections = vs.query_similar(
            MarketRegime(ticker=ticker, timestamp=time.time(), features=features),
            top_k=top_k,
            filters={"metadata.type": "reflection"},
        )
        return [r.get("metadata", {}).get("lesson", "") for r in reflections if r.get("metadata", {}).get("lesson")]
    except Exception:
        return []
