"""Tests for auth middleware session rotation."""

import time
import pytest

from src.api.middleware import (
    create_session,
    rotate_refresh_token,
    validate_session,
    revoke_session,
    revoke_token,
    cleanup_expired_sessions,
    _sessions,
    _revoked_tokens,
    SESSION_TIMEOUT,
)


def setup_function():
    try:
        _sessions.clear()
        _revoked_tokens.clear()
    except Exception as e:
        pytest.fail(f"Setup failed: {e}")


def test_create_session_returns_ids():
    try:
        session_id, refresh_token = create_session("user1", ["read", "write"])
        assert session_id is not None
        assert refresh_token is not None
        assert session_id in _sessions
        assert _sessions[session_id]["user_id"] == "user1"
        assert _sessions[session_id]["scopes"] == ["read", "write"]
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_rotate_refresh_token_valid():
    try:
        session_id, old_token = create_session("user1", ["read"])
        new_token = rotate_refresh_token(session_id, old_token)

        assert new_token is not None
        assert new_token != old_token
        assert _sessions[session_id]["refresh_token_hash"] != old_token
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_rotate_refresh_token_invalid_token():
    try:
        session_id, old_token = create_session("user1", ["read"])
        new_token = rotate_refresh_token(session_id, "wrong_token")

        assert new_token is None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_rotate_refresh_token_revoked_token():
    try:
        session_id, old_token = create_session("user1", ["read"])
        revoke_token(old_token)

        new_token = rotate_refresh_token(session_id, old_token)
        assert new_token is None
        assert session_id not in _sessions
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_rotate_refresh_token_expired_session():
    try:
        session_id, old_token = create_session("user1", ["read"])

        _sessions[session_id]["last_rotated"] = (
            time.time() - SESSION_TIMEOUT - 1
        )

        new_token = rotate_refresh_token(session_id, old_token)
        assert new_token is None
        assert session_id not in _sessions
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_rotate_refresh_token_reuse_after_rotation():
    try:
        session_id, old_token = create_session("user1", ["read"])
        rotate_refresh_token(session_id, old_token)

        result = rotate_refresh_token(session_id, old_token)
        assert result is None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_validate_session_valid():
    try:
        session_id, _ = create_session("user1", ["read", "write"])
        user_id = validate_session(session_id)

        assert user_id == "user1"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_validate_session_with_required_scopes():
    try:
        session_id, _ = create_session("user1", ["read", "write"])

        assert validate_session(session_id, ["read"]) == "user1"
        assert validate_session(session_id, ["read", "write"]) == "user1"
        assert validate_session(session_id, ["admin"]) is None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_validate_session_expired():
    try:
        session_id, _ = create_session("user1", ["read"])

        _sessions[session_id]["last_rotated"] = (
            time.time() - SESSION_TIMEOUT - 1
        )

        assert validate_session(session_id) is None
        assert session_id not in _sessions
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_validate_session_nonexistent():
    try:
        assert validate_session("nonexistent") is None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_revoke_session():
    try:
        session_id, _ = create_session("user1", ["read"])
        assert revoke_session(session_id) is True
        assert session_id not in _sessions
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_revoke_session_nonexistent():
    try:
        assert revoke_session("nonexistent") is False
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_revoke_token():
    try:
        _, refresh_token = create_session("user1", ["read"])
        revoke_token(refresh_token)

        from src.api.middleware import _hash_token
        assert _hash_token(refresh_token) in _revoked_tokens
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_cleanup_expired_sessions():
    try:
        session_id1, _ = create_session("user1", ["read"])
        session_id2, _ = create_session("user2", ["read"])

        _sessions[session_id1]["last_rotated"] = (
            time.time() - SESSION_TIMEOUT - 1
        )

        cleaned = cleanup_expired_sessions()

        assert cleaned == 1
        assert session_id1 not in _sessions
        assert session_id2 in _sessions
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_multiple_sessions_same_user():
    try:
        session_id1, token1 = create_session("user1", ["read"])
        session_id2, token2 = create_session("user1", ["write"])

        assert validate_session(session_id1) == "user1"
        assert validate_session(session_id2) == "user1"

        new_token = rotate_refresh_token(session_id1, token1)
        assert new_token is not None

        assert validate_session(session_id1) == "user1"
        assert validate_session(session_id2) == "user1"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_session_rotation_preserves_scopes():
    try:
        session_id, old_token = create_session(
            "user1", ["read", "write", "admin"]
        )
        new_token = rotate_refresh_token(session_id, old_token)

        assert new_token is not None
        assert _sessions[session_id]["scopes"] == ["read", "write", "admin"]
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
