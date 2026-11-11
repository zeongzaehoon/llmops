"""Characterization: auth/jwt.py token creation round-trip.

JWT_SECRET_KEY is set by conftest before `auth` is imported.
"""
from datetime import datetime, timezone

import pytest
from jose import jwt

from auth import SECRET_KEY, ALGORITHM
from auth.jwt import create_token


def test_create_token_round_trip():
    access, refresh = create_token("user-123")

    a = jwt.decode(access, SECRET_KEY, algorithms=[ALGORITHM])
    r = jwt.decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])

    assert a["sub"] == "user-123"
    assert a["type"] == "access"
    assert r["sub"] == "user-123"
    assert r["type"] == "refresh"


def test_access_not_expired_and_refresh_outlives_access():
    access, refresh = create_token("u")
    a = jwt.decode(access, SECRET_KEY, algorithms=[ALGORITHM])
    r = jwt.decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])

    now = datetime.now(timezone.utc).timestamp()
    assert a["exp"] > now
    assert r["exp"] > a["exp"]


def test_wrong_secret_fails_to_decode():
    access, _ = create_token("u")
    with pytest.raises(Exception):
        jwt.decode(access, "wrong-secret", algorithms=[ALGORITHM])
