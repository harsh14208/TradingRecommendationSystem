"""
Tests for pure and lightweight functions in services/auth_svc.py:
  - hash_password / verify_password
  - create_access_token / decode_access_token
  - generate_refresh_token
  - generate_link_code
  - user_to_dict
"""

import os
import sys
from datetime import datetime

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models import User
from services.auth_svc import (
    create_access_token,
    decode_access_token,
    generate_link_code,
    generate_refresh_token,
    hash_password,
    user_to_dict,
    verify_password,
)

# ── hash_password / verify_password ──────────────────────────────────────────


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        result = hash_password("securepass123")
        assert isinstance(result, str)

    def test_hash_different_from_plaintext(self):
        assert hash_password("secret") != "secret"

    def test_two_hashes_different(self):
        """bcrypt uses random salt — two hashes of same password differ."""
        h1 = hash_password("same_pass")
        h2 = hash_password("same_pass")
        assert h1 != h2

    def test_verify_correct_password(self):
        hashed = hash_password("correcthorse")
        assert verify_password("correcthorse", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correcthorse")
        assert verify_password("wronghorse", hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password("correcthorse")
        assert verify_password("", hashed) is False

    def test_verify_invalid_hash_returns_false(self):
        """If the stored hash is garbage, verify_password should return False."""
        assert verify_password("password", "not_a_valid_hash") is False

    def test_hash_long_password_truncated(self):
        """bcrypt truncates at 72 bytes — passwords > 72 chars hash the same."""
        long = "a" * 80
        h = hash_password(long)
        assert verify_password("a" * 80, h) is True


# ── JWT: create / decode ───────────────────────────────────────────────────────


class TestJwtTokens:
    def test_create_and_decode_roundtrip(self):
        token = create_access_token(user_id=1, tier="pro", is_owner=False)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["tier"] == "pro"
        assert payload["owner"] is False

    def test_owner_flag_in_token(self):
        token = create_access_token(user_id=99, tier="free", is_owner=True)
        payload = decode_access_token(token)
        assert payload["owner"] is True

    def test_decode_invalid_token_returns_none(self):
        result = decode_access_token("this.is.garbage")
        assert result is None

    def test_decode_empty_string_returns_none(self):
        result = decode_access_token("")
        assert result is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token(user_id=1, tier="free", is_owner=False)
        tampered = token[:-5] + "XXXXX"
        result = decode_access_token(tampered)
        assert result is None

    def test_token_is_string(self):
        token = create_access_token(user_id=5, tier="basic", is_owner=False)
        assert isinstance(token, str)
        assert len(token) > 20


# ── generate_refresh_token ────────────────────────────────────────────────────


class TestRefreshToken:
    def test_returns_two_strings(self):
        raw, hashed = generate_refresh_token()
        assert isinstance(raw, str)
        assert isinstance(hashed, str)

    def test_raw_and_hashed_differ(self):
        raw, hashed = generate_refresh_token()
        assert raw != hashed

    def test_hashed_is_sha256_hex(self):
        """SHA256 hex digest is always 64 characters."""
        _, hashed = generate_refresh_token()
        assert len(hashed) == 64
        assert all(c in "0123456789abcdef" for c in hashed)

    def test_raw_token_sufficiently_long(self):
        """URL-safe token from 48 bytes should be long."""
        raw, _ = generate_refresh_token()
        assert len(raw) >= 60

    def test_two_tokens_unique(self):
        raw1, _ = generate_refresh_token()
        raw2, _ = generate_refresh_token()
        assert raw1 != raw2


# ── generate_link_code ────────────────────────────────────────────────────────


class TestLinkCode:
    def test_returns_string(self):
        code = generate_link_code()
        assert isinstance(code, str)

    def test_is_uppercase(self):
        code = generate_link_code()
        assert code == code.upper()

    def test_length_is_16(self):
        """secrets.token_hex(8) → 16 hex chars."""
        code = generate_link_code()
        assert len(code) == 16

    def test_two_codes_unique(self):
        c1 = generate_link_code()
        c2 = generate_link_code()
        assert c1 != c2


# ── user_to_dict ──────────────────────────────────────────────────────────────


class TestUserToDict:
    def _make_user(self, **kwargs):
        u = User(
            id=kwargs.get("id", 1),
            email=kwargs.get("email", "test@example.com"),
            full_name=kwargs.get("full_name", "Test User"),
            is_owner=kwargs.get("is_owner", False),
            subscription_tier=kwargs.get("subscription_tier", "free"),
        )
        u.subscription_status = kwargs.get("subscription_status", "inactive")
        u.subscription_period_end = kwargs.get("subscription_period_end")
        u.telegram_chat_id = kwargs.get("telegram_chat_id")
        u.telegram_link_code = kwargs.get("telegram_link_code", "ABC123")
        u.min_confidence_override = kwargs.get("min_confidence_override")
        u.created_at = kwargs.get("created_at")
        return u

    def test_basic_fields_present(self):
        user = self._make_user()
        d = user_to_dict(user)
        assert d["id"] == 1
        assert d["email"] == "test@example.com"
        assert d["full_name"] == "Test User"

    def test_telegram_linked_false_when_no_chat_id(self):
        user = self._make_user(telegram_chat_id=None)
        d = user_to_dict(user)
        assert d["telegram_linked"] is False

    def test_telegram_linked_true_when_chat_id_set(self):
        user = self._make_user(telegram_chat_id="12345")
        d = user_to_dict(user)
        assert d["telegram_linked"] is True

    def test_subscription_period_end_none(self):
        user = self._make_user(subscription_period_end=None)
        d = user_to_dict(user)
        assert d["subscription_period_end"] is None

    def test_subscription_period_end_iso_format(self):
        from datetime import datetime

        end = datetime(2025, 12, 31, 0, 0, 0)
        user = self._make_user(subscription_period_end=end)
        d = user_to_dict(user)
        assert "2025-12-31" in d["subscription_period_end"]

    def test_created_at_none_returns_none(self):
        user = self._make_user(created_at=None)
        d = user_to_dict(user)
        assert d["created_at"] is None

    def test_created_at_isoformat(self):
        created = datetime(2024, 6, 15, 10, 30, 0)
        user = self._make_user(created_at=created)
        d = user_to_dict(user)
        assert "2024-06-15" in d["created_at"]

    def test_is_owner_field(self):
        user = self._make_user(is_owner=True)
        d = user_to_dict(user)
        assert d["is_owner"] is True

    def test_subscription_tier_field(self):
        user = self._make_user(subscription_tier="pro")
        d = user_to_dict(user)
        assert d["subscription_tier"] == "pro"
