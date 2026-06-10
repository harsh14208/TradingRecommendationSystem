"""
Dynamic Minimum Spanning Tree (MST) cointegration pairs discovery.

Replaces the 14 hard-coded pairs in cointegration.py with a universe-wide
graph that refreshes every Sunday.

Algorithm:
  1. Build pairwise correlation matrix from rolling 90-day returns.
  2. Convert to correlation-distance: D[i,j] = sqrt(2*(1 - |rho|)).
  3. Compute MST via Kruskal's algorithm (pure numpy — no scipy needed).
  4. Test each MST edge for Engle-Granger cointegration (ADF p < 0.05,
     rolling correlation >= 0.75).
  5. Persist passing pairs to data/mst_pairs_live.json (TTL 7 days).

Pairs are consumed by cointegration.get_pairs_signals() alongside the
static PAIRS list.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

log = logging.getLogger("signal.trade.mst_coint")

_DATA_DIR = Path(__file__).parent.parent / "data"
_CACHE_FILE = _DATA_DIR / "mst_pairs_live.json"
_CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

# Minimum requirements for a pair to be included
_MIN_CORR = 0.75  # rolling 90-day Pearson correlation
_MAX_COINT_P = 0.05  # Engle-Granger ADF p-value threshold
_MIN_WINDOW = 60  # minimum shared history required
_ROLL_WINDOW = 90  # correlation + spread estimation window


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__kruskal_mst__mutmut: MutantDict = {}  # type: ignore


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x__kruskal_mst__mutmut)
def _kruskal_mst(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_orig(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_1(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = None
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_2(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[1]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_3(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = None
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_4(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(None):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_5(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(None, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_6(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, None):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_7(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_8(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, ):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_9(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i - 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_10(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 2, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_11(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append(None)
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_12(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = None

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_13(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(None)

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_14(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(None))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_15(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] == x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_16(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = None
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_17(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = None
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_18(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = None
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_19(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = None
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_20(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(None), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_21(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(None)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_22(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri == rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_23(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = None
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_24(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append(None)
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_25(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(None)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_26(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) != n - 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_27(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n + 1:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_28(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 2:
                break

    return mst_edges


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def x__kruskal_mst__mutmut_29(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                return

    return mst_edges

mutants_x__kruskal_mst__mutmut['_mutmut_orig'] = x__kruskal_mst__mutmut_orig # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_1'] = x__kruskal_mst__mutmut_1 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_2'] = x__kruskal_mst__mutmut_2 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_3'] = x__kruskal_mst__mutmut_3 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_4'] = x__kruskal_mst__mutmut_4 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_5'] = x__kruskal_mst__mutmut_5 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_6'] = x__kruskal_mst__mutmut_6 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_7'] = x__kruskal_mst__mutmut_7 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_8'] = x__kruskal_mst__mutmut_8 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_9'] = x__kruskal_mst__mutmut_9 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_10'] = x__kruskal_mst__mutmut_10 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_11'] = x__kruskal_mst__mutmut_11 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_12'] = x__kruskal_mst__mutmut_12 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_13'] = x__kruskal_mst__mutmut_13 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_14'] = x__kruskal_mst__mutmut_14 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_15'] = x__kruskal_mst__mutmut_15 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_16'] = x__kruskal_mst__mutmut_16 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_17'] = x__kruskal_mst__mutmut_17 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_18'] = x__kruskal_mst__mutmut_18 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_19'] = x__kruskal_mst__mutmut_19 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_20'] = x__kruskal_mst__mutmut_20 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_21'] = x__kruskal_mst__mutmut_21 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_22'] = x__kruskal_mst__mutmut_22 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_23'] = x__kruskal_mst__mutmut_23 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_24'] = x__kruskal_mst__mutmut_24 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_25'] = x__kruskal_mst__mutmut_25 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_26'] = x__kruskal_mst__mutmut_26 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_27'] = x__kruskal_mst__mutmut_27 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_28'] = x__kruskal_mst__mutmut_28 # type: ignore # mutmut generated
mutants_x__kruskal_mst__mutmut['x__kruskal_mst__mutmut_29'] = x__kruskal_mst__mutmut_29 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut: MutantDict = {}  # type: ignore


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


@_mutmut_mutated(mutants_x__engle_granger_p__mutmut)
def _engle_granger_p(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_orig(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_1(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = None
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_2(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(None, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_3(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, None)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_4(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_5(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, )
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_6(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = None
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_7(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va + (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_8(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb - intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_9(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope / vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_10(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = None
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_11(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(None, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_12(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag=None, maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_13(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=None)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_14(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_15(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_16(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", )
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_17(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="XXAICXX", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_18(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="aic", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_19(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=6)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_20(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(None)  # p-value
    except Exception:
        return None


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def x__engle_granger_p__mutmut_21(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[2])  # p-value
    except Exception:
        return None

mutants_x__engle_granger_p__mutmut['_mutmut_orig'] = x__engle_granger_p__mutmut_orig # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_1'] = x__engle_granger_p__mutmut_1 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_2'] = x__engle_granger_p__mutmut_2 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_3'] = x__engle_granger_p__mutmut_3 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_4'] = x__engle_granger_p__mutmut_4 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_5'] = x__engle_granger_p__mutmut_5 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_6'] = x__engle_granger_p__mutmut_6 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_7'] = x__engle_granger_p__mutmut_7 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_8'] = x__engle_granger_p__mutmut_8 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_9'] = x__engle_granger_p__mutmut_9 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_10'] = x__engle_granger_p__mutmut_10 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_11'] = x__engle_granger_p__mutmut_11 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_12'] = x__engle_granger_p__mutmut_12 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_13'] = x__engle_granger_p__mutmut_13 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_14'] = x__engle_granger_p__mutmut_14 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_15'] = x__engle_granger_p__mutmut_15 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_16'] = x__engle_granger_p__mutmut_16 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_17'] = x__engle_granger_p__mutmut_17 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_18'] = x__engle_granger_p__mutmut_18 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_19'] = x__engle_granger_p__mutmut_19 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_20'] = x__engle_granger_p__mutmut_20 # type: ignore # mutmut generated
mutants_x__engle_granger_p__mutmut['x__engle_granger_p__mutmut_21'] = x__engle_granger_p__mutmut_21 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut: MutantDict = {}  # type: ignore


# ── Main public API ───────────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x_compute_mst_pairs__mutmut)
def compute_mst_pairs(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_orig(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_1(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = None
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_2(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_3(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) <= 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_4(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 5:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_5(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = None
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_6(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how=None, axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_7(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=None)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_8(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_9(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", )
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_10(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[+window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_11(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="XXallXX", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_12(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="ALL", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_13(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=2)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_14(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = None
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_15(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(None)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_16(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = None
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_17(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n <= 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_18(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 5:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_19(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = None  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_20(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(None).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_21(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df * df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_22(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(None)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_23(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(2)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_24(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = None
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_25(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[1]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_26(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T <= _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_27(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = None
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_28(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(None)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_29(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = None
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_30(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(None, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_31(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, None, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_32(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, None)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_33(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(-1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_34(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_35(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, )
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_36(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, +1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_37(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -2.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_38(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 2.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_39(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(None, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_40(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, None)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_41(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_42(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, )

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_43(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 2.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_44(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = None
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_45(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(None)
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_46(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 / (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_47(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(3.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_48(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 + np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_49(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (2.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_50(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(None)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_51(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(None, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_52(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, None)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_53(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_54(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, )

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_55(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 1.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_56(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = None
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_57(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(None)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_58(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug(None, n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_59(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", None, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_60(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, None)

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_61(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug(n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_62(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_63(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, )

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_64(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("XX[mst] %d tickers → %d MST edgesXX", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_65(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d mst edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_66(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[MST] %D TICKERS → %D MST EDGES", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_67(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = None  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_68(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = None

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_69(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = None

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_70(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = None
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_71(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(None)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_72(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = None

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_73(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(None)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_74(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = None
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_75(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = (np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_76(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) & np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_77(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(None) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_78(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(None))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_79(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() <= _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_80(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            break

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_81(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = None
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_82(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = None

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_83(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = None
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_84(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(None, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_85(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, None)
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_86(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_87(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, )
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_88(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = None
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_89(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(None)
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_90(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(None, vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_91(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], None)[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_92(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_93(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], )[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_94(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[+roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_95(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[+roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_96(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[1, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_97(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 2])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_98(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(None) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_99(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) <= _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_100(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            break

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_101(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = None
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_102(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(None, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_103(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, None)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_104(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_105(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, )
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_106(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None and coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_107(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is not None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_108(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p >= _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_109(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            break

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_110(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = None
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_111(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(None, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_112(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, None)
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_113(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_114(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, )
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_115(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(31, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_116(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(None))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_117(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) / 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_118(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 1.8))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_119(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = None
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_120(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(None, vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_121(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], None)[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_122(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_123(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], )[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_124(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[1, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_125(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 2]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_126(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = None
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_127(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(None)
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_128(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(None))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_129(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(None) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_130(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) <= 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_131(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1.0000000001:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_132(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            break
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_133(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = None
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_134(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num * beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_135(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = None
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_136(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v + beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_137(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta / vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_138(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = None
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_139(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(None)
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_140(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = None
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_141(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(None)
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_142(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma <= 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_143(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1.00000001:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_144(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            break
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_145(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = None

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_146(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) * sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_147(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] + mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_148(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[+1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_149(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-2] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_150(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            None
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_151(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "XXt1XX": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_152(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "T1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_153(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "XXt2XX": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_154(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "T2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_155(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "XXbetaXX": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_156(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "BETA": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_157(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(None, 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_158(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), None),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_159(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_160(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), ),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_161(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(None), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_162(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 7),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_163(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "XXzscoreXX": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_164(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "ZSCORE": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_165(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(None, 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_166(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), None),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_167(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_168(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), ),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_169(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(None), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_170(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 4),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_171(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "XXcorrelationXX": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_172(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "CORRELATION": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_173(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(None, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_174(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, None),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_175(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_176(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, ),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_177(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 5),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_178(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "XXcoint_pXX": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_179(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "COINT_P": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_180(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(None, 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_181(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), None),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_182(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_183(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), ),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_184(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(None), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_185(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 5),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_186(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "XXdistanceXX": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_187(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "DISTANCE": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_188(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(None, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_189(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, None),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_190(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_191(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, ),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_192(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 5),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_193(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "XXcomputed_atXX": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_194(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "COMPUTED_AT": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_195(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info(None, len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_196(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", None, len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_197(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), None)
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_198(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info(len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_199(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_200(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), )
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_201(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("XX[mst] %d / %d MST edges pass cointegration filterXX", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_202(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d mst edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


# ── Main public API ───────────────────────────────────────────────────────────


def x_compute_mst_pairs__mutmut_203(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[MST] %D / %D MST EDGES PASS COINTEGRATION FILTER", len(active_pairs), len(mst_edges))
    return active_pairs

mutants_x_compute_mst_pairs__mutmut['_mutmut_orig'] = x_compute_mst_pairs__mutmut_orig # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_1'] = x_compute_mst_pairs__mutmut_1 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_2'] = x_compute_mst_pairs__mutmut_2 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_3'] = x_compute_mst_pairs__mutmut_3 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_4'] = x_compute_mst_pairs__mutmut_4 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_5'] = x_compute_mst_pairs__mutmut_5 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_6'] = x_compute_mst_pairs__mutmut_6 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_7'] = x_compute_mst_pairs__mutmut_7 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_8'] = x_compute_mst_pairs__mutmut_8 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_9'] = x_compute_mst_pairs__mutmut_9 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_10'] = x_compute_mst_pairs__mutmut_10 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_11'] = x_compute_mst_pairs__mutmut_11 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_12'] = x_compute_mst_pairs__mutmut_12 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_13'] = x_compute_mst_pairs__mutmut_13 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_14'] = x_compute_mst_pairs__mutmut_14 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_15'] = x_compute_mst_pairs__mutmut_15 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_16'] = x_compute_mst_pairs__mutmut_16 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_17'] = x_compute_mst_pairs__mutmut_17 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_18'] = x_compute_mst_pairs__mutmut_18 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_19'] = x_compute_mst_pairs__mutmut_19 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_20'] = x_compute_mst_pairs__mutmut_20 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_21'] = x_compute_mst_pairs__mutmut_21 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_22'] = x_compute_mst_pairs__mutmut_22 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_23'] = x_compute_mst_pairs__mutmut_23 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_24'] = x_compute_mst_pairs__mutmut_24 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_25'] = x_compute_mst_pairs__mutmut_25 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_26'] = x_compute_mst_pairs__mutmut_26 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_27'] = x_compute_mst_pairs__mutmut_27 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_28'] = x_compute_mst_pairs__mutmut_28 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_29'] = x_compute_mst_pairs__mutmut_29 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_30'] = x_compute_mst_pairs__mutmut_30 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_31'] = x_compute_mst_pairs__mutmut_31 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_32'] = x_compute_mst_pairs__mutmut_32 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_33'] = x_compute_mst_pairs__mutmut_33 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_34'] = x_compute_mst_pairs__mutmut_34 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_35'] = x_compute_mst_pairs__mutmut_35 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_36'] = x_compute_mst_pairs__mutmut_36 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_37'] = x_compute_mst_pairs__mutmut_37 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_38'] = x_compute_mst_pairs__mutmut_38 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_39'] = x_compute_mst_pairs__mutmut_39 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_40'] = x_compute_mst_pairs__mutmut_40 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_41'] = x_compute_mst_pairs__mutmut_41 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_42'] = x_compute_mst_pairs__mutmut_42 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_43'] = x_compute_mst_pairs__mutmut_43 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_44'] = x_compute_mst_pairs__mutmut_44 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_45'] = x_compute_mst_pairs__mutmut_45 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_46'] = x_compute_mst_pairs__mutmut_46 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_47'] = x_compute_mst_pairs__mutmut_47 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_48'] = x_compute_mst_pairs__mutmut_48 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_49'] = x_compute_mst_pairs__mutmut_49 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_50'] = x_compute_mst_pairs__mutmut_50 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_51'] = x_compute_mst_pairs__mutmut_51 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_52'] = x_compute_mst_pairs__mutmut_52 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_53'] = x_compute_mst_pairs__mutmut_53 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_54'] = x_compute_mst_pairs__mutmut_54 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_55'] = x_compute_mst_pairs__mutmut_55 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_56'] = x_compute_mst_pairs__mutmut_56 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_57'] = x_compute_mst_pairs__mutmut_57 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_58'] = x_compute_mst_pairs__mutmut_58 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_59'] = x_compute_mst_pairs__mutmut_59 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_60'] = x_compute_mst_pairs__mutmut_60 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_61'] = x_compute_mst_pairs__mutmut_61 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_62'] = x_compute_mst_pairs__mutmut_62 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_63'] = x_compute_mst_pairs__mutmut_63 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_64'] = x_compute_mst_pairs__mutmut_64 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_65'] = x_compute_mst_pairs__mutmut_65 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_66'] = x_compute_mst_pairs__mutmut_66 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_67'] = x_compute_mst_pairs__mutmut_67 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_68'] = x_compute_mst_pairs__mutmut_68 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_69'] = x_compute_mst_pairs__mutmut_69 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_70'] = x_compute_mst_pairs__mutmut_70 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_71'] = x_compute_mst_pairs__mutmut_71 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_72'] = x_compute_mst_pairs__mutmut_72 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_73'] = x_compute_mst_pairs__mutmut_73 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_74'] = x_compute_mst_pairs__mutmut_74 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_75'] = x_compute_mst_pairs__mutmut_75 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_76'] = x_compute_mst_pairs__mutmut_76 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_77'] = x_compute_mst_pairs__mutmut_77 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_78'] = x_compute_mst_pairs__mutmut_78 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_79'] = x_compute_mst_pairs__mutmut_79 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_80'] = x_compute_mst_pairs__mutmut_80 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_81'] = x_compute_mst_pairs__mutmut_81 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_82'] = x_compute_mst_pairs__mutmut_82 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_83'] = x_compute_mst_pairs__mutmut_83 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_84'] = x_compute_mst_pairs__mutmut_84 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_85'] = x_compute_mst_pairs__mutmut_85 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_86'] = x_compute_mst_pairs__mutmut_86 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_87'] = x_compute_mst_pairs__mutmut_87 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_88'] = x_compute_mst_pairs__mutmut_88 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_89'] = x_compute_mst_pairs__mutmut_89 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_90'] = x_compute_mst_pairs__mutmut_90 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_91'] = x_compute_mst_pairs__mutmut_91 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_92'] = x_compute_mst_pairs__mutmut_92 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_93'] = x_compute_mst_pairs__mutmut_93 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_94'] = x_compute_mst_pairs__mutmut_94 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_95'] = x_compute_mst_pairs__mutmut_95 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_96'] = x_compute_mst_pairs__mutmut_96 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_97'] = x_compute_mst_pairs__mutmut_97 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_98'] = x_compute_mst_pairs__mutmut_98 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_99'] = x_compute_mst_pairs__mutmut_99 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_100'] = x_compute_mst_pairs__mutmut_100 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_101'] = x_compute_mst_pairs__mutmut_101 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_102'] = x_compute_mst_pairs__mutmut_102 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_103'] = x_compute_mst_pairs__mutmut_103 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_104'] = x_compute_mst_pairs__mutmut_104 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_105'] = x_compute_mst_pairs__mutmut_105 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_106'] = x_compute_mst_pairs__mutmut_106 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_107'] = x_compute_mst_pairs__mutmut_107 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_108'] = x_compute_mst_pairs__mutmut_108 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_109'] = x_compute_mst_pairs__mutmut_109 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_110'] = x_compute_mst_pairs__mutmut_110 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_111'] = x_compute_mst_pairs__mutmut_111 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_112'] = x_compute_mst_pairs__mutmut_112 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_113'] = x_compute_mst_pairs__mutmut_113 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_114'] = x_compute_mst_pairs__mutmut_114 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_115'] = x_compute_mst_pairs__mutmut_115 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_116'] = x_compute_mst_pairs__mutmut_116 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_117'] = x_compute_mst_pairs__mutmut_117 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_118'] = x_compute_mst_pairs__mutmut_118 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_119'] = x_compute_mst_pairs__mutmut_119 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_120'] = x_compute_mst_pairs__mutmut_120 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_121'] = x_compute_mst_pairs__mutmut_121 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_122'] = x_compute_mst_pairs__mutmut_122 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_123'] = x_compute_mst_pairs__mutmut_123 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_124'] = x_compute_mst_pairs__mutmut_124 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_125'] = x_compute_mst_pairs__mutmut_125 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_126'] = x_compute_mst_pairs__mutmut_126 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_127'] = x_compute_mst_pairs__mutmut_127 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_128'] = x_compute_mst_pairs__mutmut_128 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_129'] = x_compute_mst_pairs__mutmut_129 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_130'] = x_compute_mst_pairs__mutmut_130 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_131'] = x_compute_mst_pairs__mutmut_131 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_132'] = x_compute_mst_pairs__mutmut_132 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_133'] = x_compute_mst_pairs__mutmut_133 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_134'] = x_compute_mst_pairs__mutmut_134 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_135'] = x_compute_mst_pairs__mutmut_135 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_136'] = x_compute_mst_pairs__mutmut_136 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_137'] = x_compute_mst_pairs__mutmut_137 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_138'] = x_compute_mst_pairs__mutmut_138 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_139'] = x_compute_mst_pairs__mutmut_139 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_140'] = x_compute_mst_pairs__mutmut_140 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_141'] = x_compute_mst_pairs__mutmut_141 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_142'] = x_compute_mst_pairs__mutmut_142 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_143'] = x_compute_mst_pairs__mutmut_143 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_144'] = x_compute_mst_pairs__mutmut_144 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_145'] = x_compute_mst_pairs__mutmut_145 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_146'] = x_compute_mst_pairs__mutmut_146 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_147'] = x_compute_mst_pairs__mutmut_147 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_148'] = x_compute_mst_pairs__mutmut_148 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_149'] = x_compute_mst_pairs__mutmut_149 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_150'] = x_compute_mst_pairs__mutmut_150 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_151'] = x_compute_mst_pairs__mutmut_151 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_152'] = x_compute_mst_pairs__mutmut_152 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_153'] = x_compute_mst_pairs__mutmut_153 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_154'] = x_compute_mst_pairs__mutmut_154 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_155'] = x_compute_mst_pairs__mutmut_155 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_156'] = x_compute_mst_pairs__mutmut_156 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_157'] = x_compute_mst_pairs__mutmut_157 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_158'] = x_compute_mst_pairs__mutmut_158 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_159'] = x_compute_mst_pairs__mutmut_159 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_160'] = x_compute_mst_pairs__mutmut_160 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_161'] = x_compute_mst_pairs__mutmut_161 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_162'] = x_compute_mst_pairs__mutmut_162 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_163'] = x_compute_mst_pairs__mutmut_163 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_164'] = x_compute_mst_pairs__mutmut_164 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_165'] = x_compute_mst_pairs__mutmut_165 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_166'] = x_compute_mst_pairs__mutmut_166 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_167'] = x_compute_mst_pairs__mutmut_167 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_168'] = x_compute_mst_pairs__mutmut_168 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_169'] = x_compute_mst_pairs__mutmut_169 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_170'] = x_compute_mst_pairs__mutmut_170 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_171'] = x_compute_mst_pairs__mutmut_171 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_172'] = x_compute_mst_pairs__mutmut_172 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_173'] = x_compute_mst_pairs__mutmut_173 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_174'] = x_compute_mst_pairs__mutmut_174 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_175'] = x_compute_mst_pairs__mutmut_175 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_176'] = x_compute_mst_pairs__mutmut_176 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_177'] = x_compute_mst_pairs__mutmut_177 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_178'] = x_compute_mst_pairs__mutmut_178 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_179'] = x_compute_mst_pairs__mutmut_179 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_180'] = x_compute_mst_pairs__mutmut_180 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_181'] = x_compute_mst_pairs__mutmut_181 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_182'] = x_compute_mst_pairs__mutmut_182 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_183'] = x_compute_mst_pairs__mutmut_183 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_184'] = x_compute_mst_pairs__mutmut_184 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_185'] = x_compute_mst_pairs__mutmut_185 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_186'] = x_compute_mst_pairs__mutmut_186 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_187'] = x_compute_mst_pairs__mutmut_187 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_188'] = x_compute_mst_pairs__mutmut_188 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_189'] = x_compute_mst_pairs__mutmut_189 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_190'] = x_compute_mst_pairs__mutmut_190 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_191'] = x_compute_mst_pairs__mutmut_191 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_192'] = x_compute_mst_pairs__mutmut_192 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_193'] = x_compute_mst_pairs__mutmut_193 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_194'] = x_compute_mst_pairs__mutmut_194 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_195'] = x_compute_mst_pairs__mutmut_195 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_196'] = x_compute_mst_pairs__mutmut_196 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_197'] = x_compute_mst_pairs__mutmut_197 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_198'] = x_compute_mst_pairs__mutmut_198 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_199'] = x_compute_mst_pairs__mutmut_199 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_200'] = x_compute_mst_pairs__mutmut_200 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_201'] = x_compute_mst_pairs__mutmut_201 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_202'] = x_compute_mst_pairs__mutmut_202 # type: ignore # mutmut generated
mutants_x_compute_mst_pairs__mutmut['x_compute_mst_pairs__mutmut_203'] = x_compute_mst_pairs__mutmut_203 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_refresh_mst_pairs__mutmut)
async def refresh_mst_pairs(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_orig(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_1(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = None
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_2(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns or len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_3(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None or "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_4(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_5(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "XXCloseXX" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_6(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_7(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "CLOSE" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_8(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" not in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_9(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) > _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_10(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = None

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_11(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(None)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_12(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["XXCloseXX"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_13(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_14(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["CLOSE"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_15(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) <= 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_16(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 6:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_17(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning(None, len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_18(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", None)
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_19(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning(len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_20(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", )
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_21(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("XX[mst] Too few histories (%d) to build MSTXX", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_22(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] too few histories (%d) to build mst", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_23(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[MST] TOO FEW HISTORIES (%D) TO BUILD MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_24(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 1

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_25(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = None

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_26(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(None).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_27(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = None

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_28(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(None, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_29(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, None)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_30(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_31(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, )

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_32(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=None, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_33(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=None)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_34(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_35(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, )
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_36(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=False, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_37(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=False)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_38(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(None, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_39(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, None) as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_40(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open("w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_41(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, ) as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_42(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "XXwXX") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_43(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "W") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_44(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(None, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_45(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, None)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_46(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_47(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, )

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_48(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"XXpairsXX": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_49(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"PAIRS": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_50(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "XXcomputed_atXX": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_51(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "COMPUTED_AT": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_52(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info(None, len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_53(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", None, _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_54(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), None)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_55(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info(len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_56(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_57(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), )
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_58(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("XX[mst] Saved %d dynamic pairs to %sXX", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_59(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


async def x_refresh_mst_pairs__mutmut_60(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[MST] SAVED %D DYNAMIC PAIRS TO %S", len(pairs), _CACHE_FILE)
    return len(pairs)

mutants_x_refresh_mst_pairs__mutmut['_mutmut_orig'] = x_refresh_mst_pairs__mutmut_orig # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_1'] = x_refresh_mst_pairs__mutmut_1 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_2'] = x_refresh_mst_pairs__mutmut_2 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_3'] = x_refresh_mst_pairs__mutmut_3 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_4'] = x_refresh_mst_pairs__mutmut_4 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_5'] = x_refresh_mst_pairs__mutmut_5 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_6'] = x_refresh_mst_pairs__mutmut_6 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_7'] = x_refresh_mst_pairs__mutmut_7 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_8'] = x_refresh_mst_pairs__mutmut_8 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_9'] = x_refresh_mst_pairs__mutmut_9 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_10'] = x_refresh_mst_pairs__mutmut_10 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_11'] = x_refresh_mst_pairs__mutmut_11 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_12'] = x_refresh_mst_pairs__mutmut_12 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_13'] = x_refresh_mst_pairs__mutmut_13 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_14'] = x_refresh_mst_pairs__mutmut_14 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_15'] = x_refresh_mst_pairs__mutmut_15 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_16'] = x_refresh_mst_pairs__mutmut_16 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_17'] = x_refresh_mst_pairs__mutmut_17 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_18'] = x_refresh_mst_pairs__mutmut_18 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_19'] = x_refresh_mst_pairs__mutmut_19 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_20'] = x_refresh_mst_pairs__mutmut_20 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_21'] = x_refresh_mst_pairs__mutmut_21 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_22'] = x_refresh_mst_pairs__mutmut_22 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_23'] = x_refresh_mst_pairs__mutmut_23 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_24'] = x_refresh_mst_pairs__mutmut_24 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_25'] = x_refresh_mst_pairs__mutmut_25 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_26'] = x_refresh_mst_pairs__mutmut_26 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_27'] = x_refresh_mst_pairs__mutmut_27 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_28'] = x_refresh_mst_pairs__mutmut_28 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_29'] = x_refresh_mst_pairs__mutmut_29 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_30'] = x_refresh_mst_pairs__mutmut_30 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_31'] = x_refresh_mst_pairs__mutmut_31 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_32'] = x_refresh_mst_pairs__mutmut_32 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_33'] = x_refresh_mst_pairs__mutmut_33 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_34'] = x_refresh_mst_pairs__mutmut_34 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_35'] = x_refresh_mst_pairs__mutmut_35 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_36'] = x_refresh_mst_pairs__mutmut_36 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_37'] = x_refresh_mst_pairs__mutmut_37 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_38'] = x_refresh_mst_pairs__mutmut_38 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_39'] = x_refresh_mst_pairs__mutmut_39 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_40'] = x_refresh_mst_pairs__mutmut_40 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_41'] = x_refresh_mst_pairs__mutmut_41 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_42'] = x_refresh_mst_pairs__mutmut_42 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_43'] = x_refresh_mst_pairs__mutmut_43 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_44'] = x_refresh_mst_pairs__mutmut_44 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_45'] = x_refresh_mst_pairs__mutmut_45 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_46'] = x_refresh_mst_pairs__mutmut_46 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_47'] = x_refresh_mst_pairs__mutmut_47 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_48'] = x_refresh_mst_pairs__mutmut_48 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_49'] = x_refresh_mst_pairs__mutmut_49 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_50'] = x_refresh_mst_pairs__mutmut_50 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_51'] = x_refresh_mst_pairs__mutmut_51 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_52'] = x_refresh_mst_pairs__mutmut_52 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_53'] = x_refresh_mst_pairs__mutmut_53 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_54'] = x_refresh_mst_pairs__mutmut_54 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_55'] = x_refresh_mst_pairs__mutmut_55 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_56'] = x_refresh_mst_pairs__mutmut_56 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_57'] = x_refresh_mst_pairs__mutmut_57 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_58'] = x_refresh_mst_pairs__mutmut_58 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_59'] = x_refresh_mst_pairs__mutmut_59 # type: ignore # mutmut generated
mutants_x_refresh_mst_pairs__mutmut['x_refresh_mst_pairs__mutmut_60'] = x_refresh_mst_pairs__mutmut_60 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load_mst_pairs__mutmut)
def load_mst_pairs() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_orig() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_1() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_2() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(None) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_3() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = None
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_4() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(None)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_5() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = None
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_6() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() + float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_7() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(None)
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_8() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get(None, 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_9() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", None))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_10() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get(0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_11() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", ))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_12() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("XXcomputed_atXX", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_13() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("COMPUTED_AT", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_14() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 1))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_15() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age >= _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_16() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug(None, age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_17() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", None)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_18() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug(age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_19() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", )
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_20() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("XX[mst] Cache stale (%.0f days old)XX", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_21() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_22() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[MST] CACHE STALE (%.0F DAYS OLD)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_23() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age * 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_24() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86401)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_25() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get(None, [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_26() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", None)
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_27() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get([])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_28() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", )
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_29() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("XXpairsXX", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_30() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("PAIRS", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_31() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug(None, e)
        return []


def x_load_mst_pairs__mutmut_32() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", None)
        return []


def x_load_mst_pairs__mutmut_33() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug(e)
        return []


def x_load_mst_pairs__mutmut_34() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", )
        return []


def x_load_mst_pairs__mutmut_35() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("XX[mst] Cache load failed: %sXX", e)
        return []


def x_load_mst_pairs__mutmut_36() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] cache load failed: %s", e)
        return []


def x_load_mst_pairs__mutmut_37() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[MST] CACHE LOAD FAILED: %S", e)
        return []

mutants_x_load_mst_pairs__mutmut['_mutmut_orig'] = x_load_mst_pairs__mutmut_orig # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_1'] = x_load_mst_pairs__mutmut_1 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_2'] = x_load_mst_pairs__mutmut_2 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_3'] = x_load_mst_pairs__mutmut_3 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_4'] = x_load_mst_pairs__mutmut_4 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_5'] = x_load_mst_pairs__mutmut_5 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_6'] = x_load_mst_pairs__mutmut_6 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_7'] = x_load_mst_pairs__mutmut_7 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_8'] = x_load_mst_pairs__mutmut_8 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_9'] = x_load_mst_pairs__mutmut_9 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_10'] = x_load_mst_pairs__mutmut_10 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_11'] = x_load_mst_pairs__mutmut_11 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_12'] = x_load_mst_pairs__mutmut_12 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_13'] = x_load_mst_pairs__mutmut_13 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_14'] = x_load_mst_pairs__mutmut_14 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_15'] = x_load_mst_pairs__mutmut_15 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_16'] = x_load_mst_pairs__mutmut_16 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_17'] = x_load_mst_pairs__mutmut_17 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_18'] = x_load_mst_pairs__mutmut_18 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_19'] = x_load_mst_pairs__mutmut_19 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_20'] = x_load_mst_pairs__mutmut_20 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_21'] = x_load_mst_pairs__mutmut_21 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_22'] = x_load_mst_pairs__mutmut_22 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_23'] = x_load_mst_pairs__mutmut_23 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_24'] = x_load_mst_pairs__mutmut_24 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_25'] = x_load_mst_pairs__mutmut_25 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_26'] = x_load_mst_pairs__mutmut_26 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_27'] = x_load_mst_pairs__mutmut_27 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_28'] = x_load_mst_pairs__mutmut_28 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_29'] = x_load_mst_pairs__mutmut_29 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_30'] = x_load_mst_pairs__mutmut_30 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_31'] = x_load_mst_pairs__mutmut_31 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_32'] = x_load_mst_pairs__mutmut_32 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_33'] = x_load_mst_pairs__mutmut_33 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_34'] = x_load_mst_pairs__mutmut_34 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_35'] = x_load_mst_pairs__mutmut_35 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_36'] = x_load_mst_pairs__mutmut_36 # type: ignore # mutmut generated
mutants_x_load_mst_pairs__mutmut['x_load_mst_pairs__mutmut_37'] = x_load_mst_pairs__mutmut_37 # type: ignore # mutmut generated
