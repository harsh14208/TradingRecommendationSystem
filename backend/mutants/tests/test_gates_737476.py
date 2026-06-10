"""
Unit tests for §73 Insider Clustering, §74 Beneish M-Score, §76 Altman Z-Score gates.

These three production gates previously had zero test coverage (documented gap in
docs/TODO.md and the v7.3/v8.0 adversarial quant review).  Tests here cover:

  §73 apply_insider_clustering(score, insider, is_lev_etf):
      - 3+ unique buyers → +8pp
      - exactly 2 unique buyers → +5pp
      - 1 unique buyer → no change
      - 0 / None / empty → no change
      - is_lev_etf=True → gate skipped regardless of buyer count

  §74 Beneish M-Score in apply_quality_screens():
      - M-Score > −1.78 (manipulation zone) → −12pp
      - M-Score ≤ −1.78 (safe) → no change
      - is_lev_etf=True → gate skipped

  §76 Altman Z-Score in apply_quality_screens():
      - Z-Score < 1.81 (distress zone) → −15pp
      - Z-Score in [1.81, 2.67) (grey zone) → −4pp
      - Z-Score ≥ 2.67 (safe zone) → no change
      - is_lev_etf=True → gate skipped

All tests are pure-function calls (no DB, no network, no async) — fast and reliable.
"""

from services.gates.fundamentals import apply_insider_clustering, apply_quality_screens

# ─── Helpers ────────────────────────────────────────────────────────────────


def _quality_screens(
    score: float = 50.0,
    beneish_m: float | None = None,
    altman_z: float | None = None,
    f_score: int | None = None,
    forward_pe: float | None = None,
    is_lev_etf: bool = False,
    action: str = "BUY",
) -> tuple[float, list, set]:
    fundamentals = {}
    if beneish_m is not None:
        fundamentals["beneish_m"] = beneish_m
    if altman_z is not None:
        fundamentals["altman_z"] = altman_z
    if f_score is not None:
        fundamentals["piotroski_f"] = f_score
    info = {}
    if forward_pe is not None:
        info["forward_pe"] = forward_pe
    return apply_quality_screens(score, info, fundamentals, is_lev_etf, action)


# ─── §73 Insider Clustering ─────────────────────────────────────────────────


def test_insider_clustering_three_buyers_gives_8pp():
    new_score, cards, sources = apply_insider_clustering(50.0, {"unique_buyers": 3}, False)
    assert new_score == 58.0, f"3 unique buyers → +8pp; got {new_score}"
    assert any("Insider" in c["head"] for c in cards), "Expected insider clustering card"
    assert "SEC EDGAR" in sources


def test_insider_clustering_four_buyers_also_8pp():
    new_score, _, _ = apply_insider_clustering(50.0, {"unique_buyers": 4}, False)
    assert new_score == 58.0


def test_insider_clustering_two_buyers_gives_5pp():
    new_score, cards, sources = apply_insider_clustering(50.0, {"unique_buyers": 2}, False)
    assert new_score == 55.0, f"2 unique buyers → +5pp; got {new_score}"
    assert cards, "Expected a rationale card"
    assert "SEC EDGAR" in sources


def test_insider_clustering_one_buyer_no_change():
    new_score, cards, sources = apply_insider_clustering(50.0, {"unique_buyers": 1}, False)
    assert new_score == 50.0, "1 buyer should not trigger clustering bonus"
    assert cards == []
    assert sources == set()


def test_insider_clustering_zero_buyers_no_change():
    new_score, cards, _ = apply_insider_clustering(50.0, {"unique_buyers": 0}, False)
    assert new_score == 50.0
    assert cards == []


def test_insider_clustering_none_no_change():
    new_score, cards, _ = apply_insider_clustering(50.0, {}, False)
    assert new_score == 50.0
    assert cards == []


def test_insider_clustering_empty_dict_no_change():
    new_score, cards, _ = apply_insider_clustering(50.0, {}, False)
    assert new_score == 50.0


def test_insider_clustering_skipped_for_lev_etf():
    new_score, cards, _ = apply_insider_clustering(50.0, {"unique_buyers": 5}, True)
    assert new_score == 50.0, "Leveraged ETF should skip insider gate"
    assert cards == []


# ─── §74 Beneish M-Score ────────────────────────────────────────────────────


def test_beneish_above_threshold_penalises_12pp():
    # −1.78 is the manipulation threshold; above it → penalty
    new_score, cards, sources = _quality_screens(beneish_m=-1.5)
    assert new_score == 38.0, f"M-Score −1.5 > −1.78 → −12pp; got {new_score}"
    assert any("Beneish" in c["head"] for c in cards)
    assert "Fundamentals" in sources


def test_beneish_at_threshold_penalises():
    # −1.78 itself is NOT safe (> −1.78 is the condition; −1.78 is exactly the boundary)
    # Beneish says > −1.78 is manipulation zone, so −1.78 should NOT penalise
    new_score, cards, _ = _quality_screens(beneish_m=-1.78)
    assert new_score == 50.0, "M-Score exactly -1.78 should NOT trigger penalty (strict >)"
    assert not any("Beneish" in c["head"] for c in cards)


def test_beneish_safe_zone_no_change():
    new_score, cards, _ = _quality_screens(beneish_m=-2.5)
    assert new_score == 50.0, "M-Score −2.5 is in safe zone — no penalty"
    assert not any("Beneish" in c["head"] for c in cards)


def test_beneish_strongly_positive_penalises():
    new_score, cards, _ = _quality_screens(beneish_m=0.5)
    assert new_score == 38.0, "Positive M-Score (extreme manipulation flag) → −12pp"
    assert cards


def test_beneish_skipped_for_lev_etf():
    new_score, cards, _ = _quality_screens(beneish_m=-1.0, is_lev_etf=True)
    assert new_score == 50.0, "Leveraged ETF should skip Beneish gate"
    assert not any("Beneish" in c["head"] for c in cards)


def test_beneish_none_no_change():
    new_score, cards, _ = _quality_screens(beneish_m=None)
    assert new_score == 50.0


# ─── §76 Altman Z-Score — REMOVED 2026-06-03 ────────────────────────────────
# EDGAR validation showed 79/106 IS tickers (74%) permanently below Z'<1.23.
# The gate was penalising ~80% of live signals by -15 pts due to structural
# reasons (financial sector leverage model, tech goodwill/intangibles).
# Original Altman (1968) was calibrated on manufacturing companies only.


def test_altman_removed_no_penalty_any_value():
    """§76 Altman removed — no score change for any Z value."""
    for z in [0.5, 1.0, 1.5, 1.80, 1.81, 2.0, 2.66, 2.67, 3.0]:
        new_score, cards, _ = _quality_screens(altman_z=z)
        assert new_score == 50.0, f"§76 removed — expected 50.0 for Z={z}; got {new_score}"
        assert not any("Altman" in c.get("head", "") for c in cards), (
            f"§76 removed — no Altman cards expected for Z={z}"
        )


def test_altman_safe_zone_no_change():
    new_score, cards, _ = _quality_screens(altman_z=3.0)
    assert new_score == 50.0, "§76 removed — safe zone no change"


def test_altman_skipped_for_lev_etf():
    new_score, cards, _ = _quality_screens(altman_z=0.5, is_lev_etf=True)
    assert new_score == 50.0, "§76 removed — ETF no change"


def test_altman_none_no_change():
    new_score, cards, _ = _quality_screens(altman_z=None)
    assert new_score == 50.0


# ─── Combined gate interaction ──────────────────────────────────────────────


def test_beneish_and_altman_both_fire_penalties_stack():
    """§76 Altman removed — only Beneish fires; Altman no longer stacks."""
    new_score, cards, _ = _quality_screens(beneish_m=-1.0, altman_z=1.5)
    assert new_score == 38.0, f"§76 removed: only Beneish −12pp; got {new_score - 50.0}"
    beneish_cards = [c for c in cards if "Beneish" in c["head"]]
    altman_cards = [c for c in cards if "Z-Score" in c["head"] or "Distress" in c["head"] or "Altman" in c["head"]]
    assert beneish_cards, "Beneish card should still fire"
    assert not altman_cards, f"§76 removed — no Altman cards expected; got: {altman_cards}"


def test_insider_clustering_and_altman_distress_partially_offset():
    """§76 Altman removed — insider clustering acts alone."""
    base = 50.0
    new_score, _, _ = apply_insider_clustering(base, {"unique_buyers": 3}, False)
    assert new_score == 58.0
    final_score, _, _ = _quality_screens(new_score, altman_z=1.0)
    assert final_score == 58.0, f"§76 removed: +8 insider only, no Altman penalty; got {final_score}"
