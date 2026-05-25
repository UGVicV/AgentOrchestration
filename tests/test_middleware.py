import pytest
from src.api.middleware import (
    _redact_headers,
    REDACTED,
)


class TestRedactHeaders:
    def test_redacts_authorization(self):
        try:
            headers = {
                "Authorization": "Bearer tok",
                "Content-Type": "app/json",
            }
            safe = _redact_headers(headers)
            assert safe["Authorization"] == (
                REDACTED
            )
            assert (
                safe["Content-Type"]
                == "app/json"
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_redacts_cookie(self):
        try:
            headers = {
                "Cookie": "session=abc",
                "Host": "localhost",
            }
            safe = _redact_headers(headers)
            assert safe["Cookie"] == REDACTED
            assert (
                safe["Host"] == "localhost"
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_redacts_x_api_key(self):
        try:
            headers = {
                "X-Api-Key": "secret-key",
            }
            safe = _redact_headers(headers)
            assert (
                safe["X-Api-Key"] == REDACTED
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_preserves_safe_headers(self):
        try:
            headers = {
                "Content-Type": "text/html",
                "Accept": "*/*",
                "User-Agent": "test/1.0",
            }
            safe = _redact_headers(headers)
            assert safe == headers
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_empty_headers(self):
        try:
            safe = _redact_headers({})
            assert safe == {}
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_case_insensitive(self):
        try:
            headers = {
                "authorization": "Bearer x",
                "AUTHORIZATION": "Bearer y",
            }
            safe = _redact_headers(headers)
            for v in safe.values():
                assert v == REDACTED
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )
