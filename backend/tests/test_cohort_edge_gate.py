"""Tests for the self-calibrating cohort expected-value gate (QENG-COHORT)."""

import services.cohort_edge_gate as ceg
from services.cohort_edge_gate import (
    GLOBAL_MIN_N,
    cache_snapshot,
    compute_snapshot,
    get_cohort_decision,
)


def _rows(action, style, sector, vals):
    return [(action, style, sector, v) for v in vals]


def setup_function(_):
    # Each test installs its own snapshot; start from a clean cache.
    cache_snapshot(None)


def teardown_function(_):
    cache_snapshot(None)


def test_cold_start_passes_through():
    """No snapshot → every signal delivers at neutral size (never starve a fresh deploy)."""
    cache_snapshot(None)
    d = get_cohort_decision("BUY", "position", "XLK")
    assert d.deliver is True
    assert d.size_mult == 1.0
    assert "cold-start" in d.reason


def test_below_global_min_n_passes_through():
    """Fewer than GLOBAL_MIN_N resolved → passthrough mode, even for a bad cohort."""
    rows = _rows("SELL", "intraday", "XLK", [-5.0] * 5)  # awful, but tiny sample
    snap = compute_snapshot(rows)
    cache_snapshot(snap)
    assert snap["passthrough"] is True
    d = get_cohort_decision("SELL", "intraday", "XLK")
    assert d.deliver is True
    assert "passthrough" in d.reason


def test_blocks_negative_edge_cohort():
    """A large, clearly-negative cohort is blocked (lower bound < 0)."""
    rows = (
        _rows("BUY", "position", "XLF", [-1.5] * 60)  # strongly negative net edge
        + _rows("BUY", "position", "XLK", [2.0] * (GLOBAL_MIN_N))  # keep total above passthrough
    )
    snap = compute_snapshot(rows)
    cache_snapshot(snap)
    d = get_cohort_decision("BUY", "position", "XLF")
    assert d.deliver is False
    assert d.lb_net < 0
    assert "BLOCKED" in d.reason


def test_delivers_positive_edge_cohort_and_upsizes():
    """A large, clearly-positive cohort delivers and gets size > 1.0."""
    rows = (
        _rows("BUY", "position", "XLK", [3.0] * 120)  # strong, consistent positive edge
        + _rows("BUY", "position", "XLF", [-1.0] * 30)
    )
    snap = compute_snapshot(rows)
    cache_snapshot(snap)
    d = get_cohort_decision("BUY", "position", "XLK")
    assert d.deliver is True
    assert d.lb_net > 0
    assert d.size_mult > 1.0


def test_thin_cohort_falls_back_to_parent():
    """A cohort below N_MIN_OWN inherits the parent (action×style) decision."""
    rows = (
        _rows("BUY", "position", "XLK", [3.0] * 100)  # makes the BUY|position parent positive
        + _rows("BUY", "position", "XLV", [2.5] * 5)  # thin child of a good parent
    )
    snap = compute_snapshot(rows)
    cache_snapshot(snap)
    d = get_cohort_decision("BUY", "position", "XLV")
    # Thin child borrows the (positive) parent's verdict rather than its own noisy mean.
    assert d.deliver is True
    assert d.matched_key in ("BUY|position", "BUY|position|XLV")


def test_thin_but_hard_negative_child_is_not_masked_by_good_parent():
    """A thin child with a clearly negative own-cohort signal (n>=5) is still blocked
    even when its parent is positive — defense against a good parent masking a bad child."""
    rows = (
        _rows("BUY", "position", "XLK", [3.0] * 100)  # positive parent
        + _rows("BUY", "position", "XLE", [-6.0] * 8)  # thin but unambiguously bad child
    )
    snap = compute_snapshot(rows)
    cache_snapshot(snap)
    d = get_cohort_decision("BUY", "position", "XLE")
    assert d.deliver is False


def test_friction_is_subtracted():
    """Net edge = gross − round-trip friction; a cohort exactly at friction is ~0 net."""
    rows = _rows("BUY", "position", "XLK", [ceg.FRICTION] * 100) + _rows("BUY", "swing", "XLK", [5.0] * 30)
    snap = compute_snapshot(rows)
    cohort = snap["cohorts"]["BUY|position|XLK"]
    assert abs(cohort["raw_net"]) < 1e-6  # gross == friction → net 0


def test_auto_recovery_on_new_snapshot():
    """Recomputing with improved outcomes flips a previously-blocked cohort back on —
    no constant edited. This is the auto-recovery property."""
    bad = _rows("BUY", "position", "XLF", [-2.0] * 60) + _rows("BUY", "position", "XLK", [2.0] * 30)
    cache_snapshot(compute_snapshot(bad))
    assert get_cohort_decision("BUY", "position", "XLF").deliver is False

    good = _rows("BUY", "position", "XLF", [3.0] * 60) + _rows("BUY", "position", "XLK", [2.0] * 30)
    cache_snapshot(compute_snapshot(good))
    assert get_cohort_decision("BUY", "position", "XLF").deliver is True
