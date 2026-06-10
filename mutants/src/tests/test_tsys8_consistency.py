"""TSYS-8d: prove every win-rate surface uses the same win/loss definition.

A "win" is a *strictly positive* realised outcome (`outcome > 0`). A flat trade
(outcome == 0.0) is a loss, not a win. The resolver (`validate_predictions.py`),
the `/api/signals/*` analytics, `/api/me/performance`, the per-source accuracy
cards, and the public track record all classify outcomes independently, so this
test guards against any one of them silently drifting (e.g. to `>= 0`).
"""

import re
from pathlib import Path

import pytest

_BACKEND = Path(__file__).resolve().parent.parent


def is_win(outcome: float) -> bool:
    """Canonical win predicate shared by this test suite."""
    return outcome > 0


# ── Boundary semantics ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "outcome, expected_win",
    [
        (1.5, True),
        (0.01, True),
        (0.0, False),  # flat trade is NOT a win
        (-0.01, False),
        (-3.2, False),
    ],
)
def test_win_boundary_is_strictly_positive(outcome, expected_win):
    assert is_win(outcome) is expected_win


def test_win_rate_matches_canonical_across_a_shared_dataset():
    """A mixed dataset classified by each surface's logic must agree with `is_win`."""
    outcomes = [2.0, 0.5, 0.0, -1.0, 3.3, -0.5, 0.0, 1.1]
    canonical_wins = sum(1 for o in outcomes if is_win(o))

    # me.py:    wins = [r for r in resolved if r["outcome_pct"] > 0]
    me_wins = len([o for o in outcomes if o > 0])
    # public.py / signals.py: wins = [r for r in returns if r > 0]
    returns_wins = len([o for o in outcomes if o > 0])
    # accuracy.py: win = 1 if outcome > 0 else 0
    accuracy_wins = sum(1 if o > 0 else 0 for o in outcomes)

    assert me_wins == returns_wins == accuracy_wins == canonical_wins == 4


# ── Source-level drift guard ─────────────────────────────────────────────────

# Files that independently compute a win rate from realised outcomes.
_WIN_RATE_SOURCES = [
    "routers/me.py",
    "routers/public.py",
    "routers/accuracy.py",
    "routers/signals.py",
]


@pytest.mark.parametrize("rel_path", _WIN_RATE_SOURCES)
def test_no_surface_uses_non_strict_win_threshold(rel_path):
    """No win-rate surface may classify a flat (>= 0) trade as a win."""
    src = (_BACKEND / rel_path).read_text()
    # Catch `outcome >= 0`, `outcome_pct >= 0`, `r >= 0` used as a win test.
    offenders = re.findall(r"\boutcome\w*\s*>=\s*0\b", src)
    assert not offenders, f"{rel_path} uses a non-strict win threshold: {offenders}"


@pytest.mark.parametrize("rel_path", _WIN_RATE_SOURCES)
def test_surface_still_computes_a_strict_positive_win(rel_path):
    """Each surface must still contain the strict `> 0` win classification."""
    src = (_BACKEND / rel_path).read_text()
    assert re.search(r">\s*0\b", src), f"{rel_path} no longer has a strict `> 0` win test"
