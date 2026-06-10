"""TSYS-6d: parity tests for the BE-1 signal-engine decomposition.

`signal_engine` re-exports the leaf helpers and the assembler from
`services.engines.*` for backward compatibility. These tests prove the
decomposition did not fork behavior: the names exposed by `signal_engine` are
the *same objects* defined in the extracted modules, and the pure helpers return
identical results through either import path. If someone re-implements one of
these in `signal_engine` instead of re-exporting, the identity check fails.
"""

import pytest

from services import signal_engine
from services.engines import assembler, helpers

# (name, defining module) for every symbol re-exported by signal_engine.
_REEXPORTED = [
    ("_current_session", helpers),
    ("_score_to_action", helpers),
    ("_levels", helpers),
    ("_make_plain_english", helpers),
    ("_assemble_signal", assembler),
]


@pytest.mark.parametrize("name, source_mod", _REEXPORTED)
def test_reexport_is_same_object(name, source_mod):
    assert hasattr(signal_engine, name), f"signal_engine no longer re-exports {name}"
    assert getattr(signal_engine, name) is getattr(source_mod, name), (
        f"{name} re-exported by signal_engine is a different object than "
        f"{source_mod.__name__}.{name} — the decomposition has forked."
    )


def test_score_to_action_parity():
    for score in (10, 45, 50, 55, 80, 95):
        assert signal_engine._score_to_action(score) == helpers._score_to_action(score)


def test_levels_parity():
    via_engine = signal_engine._levels(100.0, 2.0, "BUY", "swing")
    via_helpers = helpers._levels(100.0, 2.0, "BUY", "swing")
    assert via_engine == via_helpers


def test_score_to_action_known_directions():
    """Lock the canonical (asymmetric) thresholds so a refactor can't silently
    move them: BUY at score>=35, SELL at score<=-30, HOLD in between."""
    assert signal_engine._score_to_action(80)[0] == "BUY"
    assert signal_engine._score_to_action(-50)[0] == "SELL"
    assert signal_engine._score_to_action(10)[0] == "HOLD"
