from datetime import UTC, datetime

from app.core.security import (
    create_access_token,
    decode_token,
    generate_refresh_token_value,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)


def test_hash_password_produces_different_hash_each_time():
    first = hash_password("Sup3rSecret!")
    second = hash_password("Sup3rSecret!")
    assert first != second


def test_verify_password_accepts_correct_password():
    hashed = hash_password("Sup3rSecret!")
    assert verify_password("Sup3rSecret!", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("Sup3rSecret!")
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_round_trips_claims():
    token = create_access_token("user-123", "admin", {"view_markets": True})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert payload["permissions"] == {"view_markets": True}
    assert payload["type"] == "access"


def test_refresh_token_value_is_unique_and_long():
    first = generate_refresh_token_value()
    second = generate_refresh_token_value()
    assert first != second
    assert len(first) > 20


def test_refresh_token_hash_is_deterministic():
    raw = "some-refresh-token-value"
    assert hash_refresh_token(raw) == hash_refresh_token(raw)


def test_refresh_token_expiry_is_in_the_future():
    assert refresh_token_expiry() > datetime.now(UTC)
