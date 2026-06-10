"""TSYS-12d: migration smoke tests.

Validate the Alembic revision graph without needing a live database: exactly one
head (no forked heads from concurrent sessions), a complete linear chain from
base, and a real downgrade for every revision that has an upgrade. This catches
the multi-session migration hazards (forked heads, orphaned revisions, missing
downgrades) in CI.
"""

import re
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

_BACKEND = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def script_dir() -> ScriptDirectory:
    cfg = Config(str(_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_exactly_one_head(script_dir):
    heads = script_dir.get_heads()
    assert len(heads) == 1, f"expected a single migration head, found forked heads: {heads}"


def test_chain_is_linear_and_reaches_base(script_dir):
    head = script_dir.get_current_head()
    # Walk down() from head to base; every revision must have <= 1 down_revision.
    visited = 0
    for rev in script_dir.walk_revisions("base", head):
        down = rev.down_revision
        assert down is None or isinstance(down, str), f"{rev.revision} has a branched down_revision: {down}"
        visited += 1
    total = len(list(script_dir.walk_revisions()))
    assert visited == total, f"chain from base→head visits {visited} but {total} revisions exist (orphans?)"


def test_every_revision_has_a_real_downgrade(script_dir):
    """A revision whose upgrade() calls op.* must have a non-empty downgrade()."""
    offenders = []
    for rev in script_dir.walk_revisions():
        src = Path(rev.module.__file__).read_text()
        up = _body(src, "upgrade")
        down = _body(src, "downgrade")
        if "op." in up and "op." not in down:
            offenders.append(rev.revision)
    assert not offenders, f"revisions with a no-op downgrade despite a real upgrade: {offenders}"


def _body(src: str, func: str) -> str:
    """Crudely extract a top-level function body from migration source."""
    m = re.search(rf"def {func}\(\)[^\n]*:\n(.*?)(?=\ndef |\Z)", src, re.DOTALL)
    return m.group(1) if m else ""
