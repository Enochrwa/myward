"""Unit tests for security utilities."""
from __future__ import annotations

import pytest

from myward.services.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    plain = "supersecret123"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token() -> None:
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.username == "testuser"


def test_decode_invalid_token() -> None:
    result = decode_access_token("not.a.valid.token")
    assert result is None
