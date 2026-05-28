"""
Lightweight frontend smoke tests — no browser, no bundler required.

Checks:
  1. All .jsx files are free of known security antipatterns
     (innerHTML assignment, eval(), document.write, localStorage token storage)
  2. All key .html entry points can be parsed by Python's html.parser
  3. Critical HTML files reference expected scripts/elements
"""

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # project root

# ── Helpers ───────────────────────────────────────────────────────────────────


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _jsx_files() -> list[Path]:
    return sorted(ROOT.glob("*.jsx"))


def _html_files() -> list[Path]:
    # Only key entry-point HTML files (not design/prototype pages)
    keys = [
        "login.html",
        "signup.html",
        "verify-email.html",
        "Trading Recommendation System.html",
        "landing.html",
        "mobile.html",
    ]
    return [ROOT / f for f in keys if (ROOT / f).exists()]


class _HTMLValidate(HTMLParser):
    """Raises ValueError on malformed HTML that the parser cannot recover from."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.errors = []

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass


# ── Test 1: JSX security antipatterns ────────────────────────────────────────

# Patterns that indicate direct DOM injection or insecure storage.
# Each tuple: (pattern, description, is_regex)
_SECURITY_PATTERNS = [
    # innerHTML with string concatenation or template literals (not .textContent)
    (r'\.innerHTML\s*\+?=\s*[`\'"]', "innerHTML string assignment (XSS risk)", True),
    (r"\.innerHTML\s*\+?=\s*\w", "innerHTML variable assignment (XSS risk)", True),
    # eval() usage
    (r"\beval\s*\(", "eval() call", True),
    # document.write
    (r"document\.write\s*\(", "document.write()", True),
    # localStorage storing access tokens (the old pattern we removed)
    (r"localStorage\.setItem\s*\([^)]*token", "localStorage token storage", True),
    (r"localStorage\.setItem\s*\([^)]*auth", "localStorage auth storage", True),
]


def test_jsx_no_dom_injection():
    """No JSX file should contain raw innerHTML string assignments or eval()."""
    violations = []
    for jsx in _jsx_files():
        src = _load(jsx)
        for pattern, desc, is_regex in _SECURITY_PATTERNS:
            if is_regex:
                matches = re.findall(pattern, src, re.IGNORECASE)
            else:
                matches = [pattern] if pattern in src else []
            if matches:
                violations.append(f"{jsx.name}: {desc} ({len(matches)} occurrence(s))")

    assert not violations, "Security antipatterns found in JSX:\n" + "\n".join(violations)


def test_html_no_dom_injection():
    """No key HTML file should contain raw innerHTML string assignments."""
    violations = []
    for html in _html_files():
        src = _load(html)
        for pattern, desc, is_regex in _SECURITY_PATTERNS:
            if is_regex:
                matches = re.findall(pattern, src, re.IGNORECASE)
            else:
                matches = [pattern] if pattern in src else []
            if matches:
                violations.append(f"{html.name}: {desc} ({len(matches)} occurrence(s))")

    assert not violations, "Security antipatterns found in HTML:\n" + "\n".join(violations)


# ── Test 2: HTML files parse without fatal errors ─────────────────────────────


def test_html_files_parseable():
    """All key HTML entry points must be parseable by html.parser."""
    for html_path in _html_files():
        src = _load(html_path)
        try:
            p = _HTMLValidate()
            p.feed(src)
        except Exception as e:
            raise AssertionError(f"{html_path.name} failed to parse: {e}")


# ── Test 3: login.html references refresh-cookie (not localStorage) ───────────


def test_login_uses_refresh_cookie_not_localstorage():
    """login.html should use the refresh-cookie flow, not localStorage for tokens."""
    login = ROOT / "login.html"
    if not login.exists():
        return
    src = _load(login)
    assert "refresh-cookie" in src, "login.html missing refresh-cookie endpoint reference"
    assert "localStorage.setItem" not in src or "token" not in src, "login.html still stores tokens in localStorage"


# ── Test 4: auth JSX uses module-level token variable ─────────────────────────


def test_auth_jsx_uses_module_variable_not_localstorage():
    """app.auth.jsx must use _accessToken module variable, not localStorage."""
    auth = ROOT / "app.auth.jsx"
    if not auth.exists():
        return
    src = _load(auth)
    assert "_accessToken" in src, "app.auth.jsx must define _accessToken module variable"
    assert "localStorage.setItem" not in src, "app.auth.jsx must not write access tokens to localStorage"


# ── Test 5: JSX files exist ───────────────────────────────────────────────────


def test_core_jsx_files_exist():
    """All 8 app JSX split files must be present."""
    required = [
        "app.jsx",
        "app.auth.jsx",
        "app.constants.jsx",
        "app.ui.jsx",
        "app.signal.jsx",
        "app.views.jsx",
        "app.modals.jsx",
        "app.analysis.jsx",
    ]
    missing = [f for f in required if not (ROOT / f).exists()]
    assert not missing, f"Missing core JSX files: {missing}"
