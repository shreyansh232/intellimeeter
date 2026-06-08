from datetime import timedelta

import pytest

from app.core.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_creation_and_decoding():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded


def test_jwt_token_expiration():
    data = {"sub": "test@example.com"}
    # Token that expires in the past
    token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    decoded = decode_access_token(token)
    assert decoded is None


def test_invalid_jwt_token():
    assert decode_access_token("invalid_token") is None
