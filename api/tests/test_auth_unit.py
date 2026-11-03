from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest

from finsense_api.auth.passwords import hash_password, verify_password
from finsense_api.auth.routes import REGISTERED_ROLE, public_user
from finsense_api.auth.tokens import decode_token, issue_token
from finsense_api.auth.validators import parse_credentials
from finsense_api.errors import ApiError


def test_password_roundtrip():
    hashed = hash_password("ledger-pass")
    assert verify_password(hashed, "ledger-pass")
    assert not verify_password(hashed, "other-pass")


def test_token_roundtrip():
    config = SimpleNamespace(jwt_secret="test-secret-at-least-32-bytes-long", jwt_expires_days=1)
    token = issue_token(7, "user", config)
    payload = decode_token(token, config)
    assert payload["sub"] == "7"
    assert payload["role"] == "user"


def test_token_rejects_garbage():
    config = SimpleNamespace(jwt_secret="test-secret-at-least-32-bytes-long", jwt_expires_days=1)
    with pytest.raises(jwt.PyJWTError):
        decode_token("not-a-token", config)


def test_token_rejects_expired():
    config = SimpleNamespace(jwt_secret="test-secret-at-least-32-bytes-long", jwt_expires_days=1)
    token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
        },
        "test-secret-at-least-32-bytes-long",
        algorithm="HS256",
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token, config)


def test_register_role_is_fixed_user():
    assert REGISTERED_ROLE == "user"


def test_public_user_hides_password():
    shown = public_user(
        SimpleNamespace(
            id=1,
            username="lucia",
            role="user",
            status="active",
            password_hash="secret",
        )
    )
    assert shown == {"id": 1, "username": "lucia", "role": "user", "status": "active"}


def test_parse_credentials_ignores_role():
    username, password = parse_credentials(
        {"username": "student", "password": "ledger-pass", "role": "admin", "status": "disabled"}
    )
    assert username == "student"
    assert password == "ledger-pass"


def test_parse_credentials_accepts_local_passwords():
    assert parse_credentials({"username": "admin", "password": "admin"})[1] == "admin"
    assert parse_credentials({"username": "student", "password": "123456"})[1] == "123456"


def test_parse_credentials_rejects_empty_or_too_long_password():
    with pytest.raises(ApiError) as caught:
        parse_credentials({"username": "student", "password": ""})
    assert caught.value.status == 400
    with pytest.raises(ApiError) as caught:
        parse_credentials({"username": "student", "password": "x" * 65})
    assert caught.value.status == 400
