"""
Auth service: JWT creation/validation, password hashing,
FastAPI dependencies for authentication and tier-gating.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt_lib
from config import get_settings, tier_gte
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from models import User
from sqlalchemy.ext.asyncio import AsyncSession

_bearer = HTTPBearer(auto_error=False)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_hash_password__mutmut: MutantDict = {}  # type: ignore


# ── Passwords ─────────────────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x_hash_password__mutmut)
def hash_password(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:72], _bcrypt_lib.gensalt()).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_orig(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:72], _bcrypt_lib.gensalt()).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_1(plain: str) -> str:
    return _bcrypt_lib.hashpw(None, _bcrypt_lib.gensalt()).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_2(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:72], None).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_3(plain: str) -> str:
    return _bcrypt_lib.hashpw(_bcrypt_lib.gensalt()).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_4(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:72], ).decode()


# ── Passwords ─────────────────────────────────────────────────────────────────


def x_hash_password__mutmut_5(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:73], _bcrypt_lib.gensalt()).decode()

mutants_x_hash_password__mutmut['_mutmut_orig'] = x_hash_password__mutmut_orig # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_1'] = x_hash_password__mutmut_1 # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_2'] = x_hash_password__mutmut_2 # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_3'] = x_hash_password__mutmut_3 # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_4'] = x_hash_password__mutmut_4 # type: ignore # mutmut generated
mutants_x_hash_password__mutmut['x_hash_password__mutmut_5'] = x_hash_password__mutmut_5 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_verify_password__mutmut)
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], hashed.encode())
    except Exception:
        return False


def x_verify_password__mutmut_orig(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], hashed.encode())
    except Exception:
        return False


def x_verify_password__mutmut_1(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(None, hashed.encode())
    except Exception:
        return False


def x_verify_password__mutmut_2(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], None)
    except Exception:
        return False


def x_verify_password__mutmut_3(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(hashed.encode())
    except Exception:
        return False


def x_verify_password__mutmut_4(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], )
    except Exception:
        return False


def x_verify_password__mutmut_5(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:73], hashed.encode())
    except Exception:
        return False


def x_verify_password__mutmut_6(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], hashed.encode())
    except Exception:
        return True

mutants_x_verify_password__mutmut['_mutmut_orig'] = x_verify_password__mutmut_orig # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_1'] = x_verify_password__mutmut_1 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_2'] = x_verify_password__mutmut_2 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_3'] = x_verify_password__mutmut_3 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_4'] = x_verify_password__mutmut_4 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_5'] = x_verify_password__mutmut_5 # type: ignore # mutmut generated
mutants_x_verify_password__mutmut['x_verify_password__mutmut_6'] = x_verify_password__mutmut_6 # type: ignore # mutmut generated


# ── JWT ───────────────────────────────────────────────────────────────────────


def _secret() -> str:
    return get_settings().jwt_secret_key


def _algo() -> str:
    return get_settings().jwt_algorithm
mutants_x__utcnow_naive__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__utcnow_naive__mutmut)
def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive DB/JWT datetime usage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def x__utcnow_naive__mutmut_orig() -> datetime:
    """UTC timestamp compatible with existing naive DB/JWT datetime usage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def x__utcnow_naive__mutmut_1() -> datetime:
    """UTC timestamp compatible with existing naive DB/JWT datetime usage."""
    return datetime.now(None).replace(tzinfo=None)

mutants_x__utcnow_naive__mutmut['_mutmut_orig'] = x__utcnow_naive__mutmut_orig # type: ignore # mutmut generated
mutants_x__utcnow_naive__mutmut['x__utcnow_naive__mutmut_1'] = x__utcnow_naive__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_access_token__mutmut)
def create_access_token(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_orig(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_1(user_id: int, tier: str, is_owner: bool) -> str:
    s = None
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_2(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = None
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_3(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() - timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_4(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=None)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_5(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        None,
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_6(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        None,
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_7(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=None,
    )


def x_create_access_token__mutmut_8(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_9(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_10(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        )


def x_create_access_token__mutmut_11(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"XXsubXX": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_12(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"SUB": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_13(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(None), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_14(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "XXtierXX": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_15(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "TIER": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_16(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "XXownerXX": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_17(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "OWNER": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_18(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "XXexpXX": expire},
        _secret(),
        algorithm=_algo(),
    )


def x_create_access_token__mutmut_19(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "EXP": expire},
        _secret(),
        algorithm=_algo(),
    )

mutants_x_create_access_token__mutmut['_mutmut_orig'] = x_create_access_token__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_1'] = x_create_access_token__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_2'] = x_create_access_token__mutmut_2 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_3'] = x_create_access_token__mutmut_3 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_4'] = x_create_access_token__mutmut_4 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_5'] = x_create_access_token__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_6'] = x_create_access_token__mutmut_6 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_7'] = x_create_access_token__mutmut_7 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_8'] = x_create_access_token__mutmut_8 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_9'] = x_create_access_token__mutmut_9 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_10'] = x_create_access_token__mutmut_10 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_11'] = x_create_access_token__mutmut_11 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_12'] = x_create_access_token__mutmut_12 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_13'] = x_create_access_token__mutmut_13 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_14'] = x_create_access_token__mutmut_14 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_15'] = x_create_access_token__mutmut_15 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_16'] = x_create_access_token__mutmut_16 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_17'] = x_create_access_token__mutmut_17 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_18'] = x_create_access_token__mutmut_18 # type: ignore # mutmut generated
mutants_x_create_access_token__mutmut['x_create_access_token__mutmut_19'] = x_create_access_token__mutmut_19 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_decode_access_token__mutmut)
def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_orig(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_1(token: str) -> dict | None:
    try:
        return jwt.decode(None, _secret(), algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_2(token: str) -> dict | None:
    try:
        return jwt.decode(token, None, algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_3(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=None)
    except JWTError:
        return None


def x_decode_access_token__mutmut_4(token: str) -> dict | None:
    try:
        return jwt.decode(_secret(), algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_5(token: str) -> dict | None:
    try:
        return jwt.decode(token, algorithms=[_algo()])
    except JWTError:
        return None


def x_decode_access_token__mutmut_6(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), )
    except JWTError:
        return None

mutants_x_decode_access_token__mutmut['_mutmut_orig'] = x_decode_access_token__mutmut_orig # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_1'] = x_decode_access_token__mutmut_1 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_2'] = x_decode_access_token__mutmut_2 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_3'] = x_decode_access_token__mutmut_3 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_4'] = x_decode_access_token__mutmut_4 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_5'] = x_decode_access_token__mutmut_5 # type: ignore # mutmut generated
mutants_x_decode_access_token__mutmut['x_decode_access_token__mutmut_6'] = x_decode_access_token__mutmut_6 # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut: MutantDict = {}  # type: ignore


# ── Refresh tokens ────────────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x_generate_refresh_token__mutmut)
def generate_refresh_token() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_orig() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_1() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = None
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_2() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(None)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_3() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(49)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_4() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(48)
    hashed = None
    return raw, hashed


# ── Refresh tokens ────────────────────────────────────────────────────────────


def x_generate_refresh_token__mutmut_5() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(None).hexdigest()
    return raw, hashed

mutants_x_generate_refresh_token__mutmut['_mutmut_orig'] = x_generate_refresh_token__mutmut_orig # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut['x_generate_refresh_token__mutmut_1'] = x_generate_refresh_token__mutmut_1 # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut['x_generate_refresh_token__mutmut_2'] = x_generate_refresh_token__mutmut_2 # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut['x_generate_refresh_token__mutmut_3'] = x_generate_refresh_token__mutmut_3 # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut['x_generate_refresh_token__mutmut_4'] = x_generate_refresh_token__mutmut_4 # type: ignore # mutmut generated
mutants_x_generate_refresh_token__mutmut['x_generate_refresh_token__mutmut_5'] = x_generate_refresh_token__mutmut_5 # type: ignore # mutmut generated
mutants_x_generate_link_code__mutmut: MutantDict = {}  # type: ignore


# ── Telegram link codes ───────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x_generate_link_code__mutmut)
def generate_link_code() -> str:
    return secrets.token_hex(8).upper()  # e.g. "A1B2C3D4E5F6A7B8"


# ── Telegram link codes ───────────────────────────────────────────────────────


def x_generate_link_code__mutmut_orig() -> str:
    return secrets.token_hex(8).upper()  # e.g. "A1B2C3D4E5F6A7B8"


# ── Telegram link codes ───────────────────────────────────────────────────────


def x_generate_link_code__mutmut_1() -> str:
    return secrets.token_hex(8).lower()  # e.g. "A1B2C3D4E5F6A7B8"


# ── Telegram link codes ───────────────────────────────────────────────────────


def x_generate_link_code__mutmut_2() -> str:
    return secrets.token_hex(None).upper()  # e.g. "A1B2C3D4E5F6A7B8"


# ── Telegram link codes ───────────────────────────────────────────────────────


def x_generate_link_code__mutmut_3() -> str:
    return secrets.token_hex(9).upper()  # e.g. "A1B2C3D4E5F6A7B8"

mutants_x_generate_link_code__mutmut['_mutmut_orig'] = x_generate_link_code__mutmut_orig # type: ignore # mutmut generated
mutants_x_generate_link_code__mutmut['x_generate_link_code__mutmut_1'] = x_generate_link_code__mutmut_1 # type: ignore # mutmut generated
mutants_x_generate_link_code__mutmut['x_generate_link_code__mutmut_2'] = x_generate_link_code__mutmut_2 # type: ignore # mutmut generated
mutants_x_generate_link_code__mutmut['x_generate_link_code__mutmut_3'] = x_generate_link_code__mutmut_3 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut: MutantDict = {}  # type: ignore


# ── FastAPI dependencies ──────────────────────────────────────────────────────


@_mutmut_mutated(mutants_x__get_user_from_token__mutmut)
async def _get_user_from_token(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_orig(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_1(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_2(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = None
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_3(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(None)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_4(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_5(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = None
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_6(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(None)
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_7(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get(None, 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_8(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", None))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_9(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get(0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_10(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", ))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_11(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("XXsubXX", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_12(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("SUB", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_13(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 1))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_14(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = None
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_15(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(None, user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_16(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, None)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_17(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(user_id)
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_18(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, )
    if not row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_19(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row and not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_20(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if row or not row.is_active:
        return None
    return row


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def x__get_user_from_token__mutmut_21(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or row.is_active:
        return None
    return row

mutants_x__get_user_from_token__mutmut['_mutmut_orig'] = x__get_user_from_token__mutmut_orig # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_1'] = x__get_user_from_token__mutmut_1 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_2'] = x__get_user_from_token__mutmut_2 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_3'] = x__get_user_from_token__mutmut_3 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_4'] = x__get_user_from_token__mutmut_4 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_5'] = x__get_user_from_token__mutmut_5 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_6'] = x__get_user_from_token__mutmut_6 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_7'] = x__get_user_from_token__mutmut_7 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_8'] = x__get_user_from_token__mutmut_8 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_9'] = x__get_user_from_token__mutmut_9 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_10'] = x__get_user_from_token__mutmut_10 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_11'] = x__get_user_from_token__mutmut_11 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_12'] = x__get_user_from_token__mutmut_12 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_13'] = x__get_user_from_token__mutmut_13 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_14'] = x__get_user_from_token__mutmut_14 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_15'] = x__get_user_from_token__mutmut_15 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_16'] = x__get_user_from_token__mutmut_16 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_17'] = x__get_user_from_token__mutmut_17 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_18'] = x__get_user_from_token__mutmut_18 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_19'] = x__get_user_from_token__mutmut_19 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_20'] = x__get_user_from_token__mutmut_20 # type: ignore # mutmut generated
mutants_x__get_user_from_token__mutmut['x__get_user_from_token__mutmut_21'] = x__get_user_from_token__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_current_user__mutmut)
async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_orig(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_1(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_2(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(None, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_3(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_4(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_5(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_6(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_7(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=None,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_8(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=None,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_9(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers=None,
        )
    return user


async def x_get_current_user__mutmut_10(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_11(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_12(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            )
    return user


async def x_get_current_user__mutmut_13(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="XXNot authenticatedXX",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_14(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_15(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT AUTHENTICATED",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_16(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"XXWWW-AuthenticateXX": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_17(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"www-authenticate": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_18(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-AUTHENTICATE": "Bearer"},
        )
    return user


async def x_get_current_user__mutmut_19(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "XXBearerXX"},
        )
    return user


async def x_get_current_user__mutmut_20(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "bearer"},
        )
    return user


async def x_get_current_user__mutmut_21(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "BEARER"},
        )
    return user

mutants_x_get_current_user__mutmut['_mutmut_orig'] = x_get_current_user__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_1'] = x_get_current_user__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_2'] = x_get_current_user__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_3'] = x_get_current_user__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_4'] = x_get_current_user__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_5'] = x_get_current_user__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_6'] = x_get_current_user__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_7'] = x_get_current_user__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_8'] = x_get_current_user__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_9'] = x_get_current_user__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_10'] = x_get_current_user__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_11'] = x_get_current_user__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_12'] = x_get_current_user__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_13'] = x_get_current_user__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_14'] = x_get_current_user__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_15'] = x_get_current_user__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_16'] = x_get_current_user__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_17'] = x_get_current_user__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_18'] = x_get_current_user__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_19'] = x_get_current_user__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_20'] = x_get_current_user__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_current_user__mutmut['x_get_current_user__mutmut_21'] = x_get_current_user__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_current_user_optional__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_current_user_optional__mutmut)
async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(creds, db)


async def x_get_current_user_optional__mutmut_orig(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(creds, db)


async def x_get_current_user_optional__mutmut_1(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(None, db)


async def x_get_current_user_optional__mutmut_2(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(creds, None)


async def x_get_current_user_optional__mutmut_3(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(db)


async def x_get_current_user_optional__mutmut_4(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(creds, )

mutants_x_get_current_user_optional__mutmut['_mutmut_orig'] = x_get_current_user_optional__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_current_user_optional__mutmut['x_get_current_user_optional__mutmut_1'] = x_get_current_user_optional__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_current_user_optional__mutmut['x_get_current_user_optional__mutmut_2'] = x_get_current_user_optional__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_current_user_optional__mutmut['x_get_current_user_optional__mutmut_3'] = x_get_current_user_optional__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_current_user_optional__mutmut['x_get_current_user_optional__mutmut_4'] = x_get_current_user_optional__mutmut_4 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_require_tier__mutmut)
def require_tier(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_orig(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_1(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_2(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(None, min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_3(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, None):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_4(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_5(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, ):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_6(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=None,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_7(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                detail=None,
            )
        return user

    return _dep


def x_require_tier__mutmut_8(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def x_require_tier__mutmut_9(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                )
        return user

    return _dep


def x_require_tier__mutmut_10(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=403,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep

mutants_x_require_tier__mutmut['_mutmut_orig'] = x_require_tier__mutmut_orig # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_1'] = x_require_tier__mutmut_1 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_2'] = x_require_tier__mutmut_2 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_3'] = x_require_tier__mutmut_3 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_4'] = x_require_tier__mutmut_4 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_5'] = x_require_tier__mutmut_5 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_6'] = x_require_tier__mutmut_6 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_7'] = x_require_tier__mutmut_7 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_8'] = x_require_tier__mutmut_8 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_9'] = x_require_tier__mutmut_9 # type: ignore # mutmut generated
mutants_x_require_tier__mutmut['x_require_tier__mutmut_10'] = x_require_tier__mutmut_10 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_user_to_dict__mutmut)
def user_to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_orig(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_1(u: User) -> dict:
    return {
        "XXidXX": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_2(u: User) -> dict:
    return {
        "ID": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_3(u: User) -> dict:
    return {
        "id": u.id,
        "XXemailXX": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_4(u: User) -> dict:
    return {
        "id": u.id,
        "EMAIL": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_5(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "XXfull_nameXX": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_6(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "FULL_NAME": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_7(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "XXis_ownerXX": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_8(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "IS_OWNER": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_9(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "XXsubscription_tierXX": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_10(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "SUBSCRIPTION_TIER": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_11(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "XXsubscription_statusXX": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_12(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "SUBSCRIPTION_STATUS": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_13(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "XXsubscription_period_endXX": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_14(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "SUBSCRIPTION_PERIOD_END": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_15(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "XXtelegram_linkedXX": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_16(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "TELEGRAM_LINKED": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_17(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(None),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_18(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "XXtelegram_link_codeXX": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_19(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "TELEGRAM_LINK_CODE": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_20(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "XXmin_confidence_overrideXX": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_21(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "MIN_CONFIDENCE_OVERRIDE": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_22(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "XXdiscord_webhook_urlXX": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_23(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "DISCORD_WEBHOOK_URL": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_24(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(None, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_25(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, None, None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_26(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr("discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_27(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_28(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", ),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_29(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "XXdiscord_webhook_urlXX", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_30(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "DISCORD_WEBHOOK_URL", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_31(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "XXwebhook_urlXX": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_32(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "WEBHOOK_URL": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_33(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(None, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_34(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, None, None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_35(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr("webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_36(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_37(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", ),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_38(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "XXwebhook_urlXX", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_39(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "WEBHOOK_URL", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_40(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "XXoauth_providerXX": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_41(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "OAUTH_PROVIDER": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_42(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(None, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_43(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, None, None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_44(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr("oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_45(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_46(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", ),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_47(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "XXoauth_providerXX", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_48(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "OAUTH_PROVIDER", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_49(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "XXauto_executeXX": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_50(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "AUTO_EXECUTE": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_51(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(None, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_52(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, None, False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_53(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", None),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_54(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr("auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_55(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_56(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", ),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_57(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "XXauto_executeXX", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_58(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "AUTO_EXECUTE", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_59(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", True),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_60(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "XXauto_execute_min_confXX": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_61(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "AUTO_EXECUTE_MIN_CONF": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_62(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(None, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_63(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, None, None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_64(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr("auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_65(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_66(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", ),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_67(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "XXauto_execute_min_confXX", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_68(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "AUTO_EXECUTE_MIN_CONF", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_69(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "XXauto_execute_brokerXX": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_70(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "AUTO_EXECUTE_BROKER": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_71(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(None, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_72(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, None, None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_73(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr("auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_74(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_75(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", ),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_76(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "XXauto_execute_brokerXX", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_77(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "AUTO_EXECUTE_BROKER", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_78(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "XXauto_execute_qty_dollarsXX": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_79(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "AUTO_EXECUTE_QTY_DOLLARS": getattr(u, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_80(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(None, "auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_81(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, None, None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_82(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr("auto_execute_qty_dollars", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_83(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_84(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", ),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_85(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "XXauto_execute_qty_dollarsXX", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_86(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "AUTO_EXECUTE_QTY_DOLLARS", None),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_87(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "XXcreated_atXX": u.created_at.isoformat() if u.created_at else None,
    }


def x_user_to_dict__mutmut_88(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "CREATED_AT": u.created_at.isoformat() if u.created_at else None,
    }

mutants_x_user_to_dict__mutmut['_mutmut_orig'] = x_user_to_dict__mutmut_orig # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_1'] = x_user_to_dict__mutmut_1 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_2'] = x_user_to_dict__mutmut_2 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_3'] = x_user_to_dict__mutmut_3 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_4'] = x_user_to_dict__mutmut_4 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_5'] = x_user_to_dict__mutmut_5 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_6'] = x_user_to_dict__mutmut_6 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_7'] = x_user_to_dict__mutmut_7 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_8'] = x_user_to_dict__mutmut_8 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_9'] = x_user_to_dict__mutmut_9 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_10'] = x_user_to_dict__mutmut_10 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_11'] = x_user_to_dict__mutmut_11 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_12'] = x_user_to_dict__mutmut_12 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_13'] = x_user_to_dict__mutmut_13 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_14'] = x_user_to_dict__mutmut_14 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_15'] = x_user_to_dict__mutmut_15 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_16'] = x_user_to_dict__mutmut_16 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_17'] = x_user_to_dict__mutmut_17 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_18'] = x_user_to_dict__mutmut_18 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_19'] = x_user_to_dict__mutmut_19 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_20'] = x_user_to_dict__mutmut_20 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_21'] = x_user_to_dict__mutmut_21 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_22'] = x_user_to_dict__mutmut_22 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_23'] = x_user_to_dict__mutmut_23 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_24'] = x_user_to_dict__mutmut_24 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_25'] = x_user_to_dict__mutmut_25 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_26'] = x_user_to_dict__mutmut_26 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_27'] = x_user_to_dict__mutmut_27 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_28'] = x_user_to_dict__mutmut_28 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_29'] = x_user_to_dict__mutmut_29 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_30'] = x_user_to_dict__mutmut_30 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_31'] = x_user_to_dict__mutmut_31 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_32'] = x_user_to_dict__mutmut_32 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_33'] = x_user_to_dict__mutmut_33 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_34'] = x_user_to_dict__mutmut_34 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_35'] = x_user_to_dict__mutmut_35 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_36'] = x_user_to_dict__mutmut_36 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_37'] = x_user_to_dict__mutmut_37 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_38'] = x_user_to_dict__mutmut_38 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_39'] = x_user_to_dict__mutmut_39 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_40'] = x_user_to_dict__mutmut_40 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_41'] = x_user_to_dict__mutmut_41 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_42'] = x_user_to_dict__mutmut_42 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_43'] = x_user_to_dict__mutmut_43 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_44'] = x_user_to_dict__mutmut_44 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_45'] = x_user_to_dict__mutmut_45 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_46'] = x_user_to_dict__mutmut_46 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_47'] = x_user_to_dict__mutmut_47 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_48'] = x_user_to_dict__mutmut_48 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_49'] = x_user_to_dict__mutmut_49 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_50'] = x_user_to_dict__mutmut_50 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_51'] = x_user_to_dict__mutmut_51 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_52'] = x_user_to_dict__mutmut_52 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_53'] = x_user_to_dict__mutmut_53 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_54'] = x_user_to_dict__mutmut_54 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_55'] = x_user_to_dict__mutmut_55 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_56'] = x_user_to_dict__mutmut_56 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_57'] = x_user_to_dict__mutmut_57 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_58'] = x_user_to_dict__mutmut_58 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_59'] = x_user_to_dict__mutmut_59 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_60'] = x_user_to_dict__mutmut_60 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_61'] = x_user_to_dict__mutmut_61 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_62'] = x_user_to_dict__mutmut_62 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_63'] = x_user_to_dict__mutmut_63 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_64'] = x_user_to_dict__mutmut_64 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_65'] = x_user_to_dict__mutmut_65 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_66'] = x_user_to_dict__mutmut_66 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_67'] = x_user_to_dict__mutmut_67 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_68'] = x_user_to_dict__mutmut_68 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_69'] = x_user_to_dict__mutmut_69 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_70'] = x_user_to_dict__mutmut_70 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_71'] = x_user_to_dict__mutmut_71 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_72'] = x_user_to_dict__mutmut_72 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_73'] = x_user_to_dict__mutmut_73 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_74'] = x_user_to_dict__mutmut_74 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_75'] = x_user_to_dict__mutmut_75 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_76'] = x_user_to_dict__mutmut_76 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_77'] = x_user_to_dict__mutmut_77 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_78'] = x_user_to_dict__mutmut_78 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_79'] = x_user_to_dict__mutmut_79 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_80'] = x_user_to_dict__mutmut_80 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_81'] = x_user_to_dict__mutmut_81 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_82'] = x_user_to_dict__mutmut_82 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_83'] = x_user_to_dict__mutmut_83 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_84'] = x_user_to_dict__mutmut_84 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_85'] = x_user_to_dict__mutmut_85 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_86'] = x_user_to_dict__mutmut_86 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_87'] = x_user_to_dict__mutmut_87 # type: ignore # mutmut generated
mutants_x_user_to_dict__mutmut['x_user_to_dict__mutmut_88'] = x_user_to_dict__mutmut_88 # type: ignore # mutmut generated
