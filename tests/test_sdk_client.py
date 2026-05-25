import pytest
from unittest.mock import (
    patch,
    MagicMock,
)
from src.sdk.client import (
    OrchestratorClient,
    NO_CONTENT_CODES,
)


class TestClientNoContent:
    def setup_method(self):
        self.client = OrchestratorClient(
            base_url="http://localhost",
            api_key="test-key",
        )

    def test_204_returns_empty_dict(self):
        try:
            mock_resp = MagicMock()
            mock_resp.status = 204
            mock_resp.read.return_value = b""
            mock_resp.__enter__ = (
                lambda s: mock_resp
            )
            mock_resp.__exit__ = (
                MagicMock(return_value=False)
            )
            with patch(
                "src.sdk.client.urlopen",
                return_value=mock_resp,
            ):
                result = self.client._request(
                    "DELETE", "/agents/123"
                )
            assert result == {}
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_205_returns_empty_dict(self):
        try:
            mock_resp = MagicMock()
            mock_resp.status = 205
            mock_resp.read.return_value = b""
            mock_resp.__enter__ = (
                lambda s: mock_resp
            )
            mock_resp.__exit__ = (
                MagicMock(return_value=False)
            )
            with patch(
                "src.sdk.client.urlopen",
                return_value=mock_resp,
            ):
                result = self.client._request(
                    "DELETE", "/agents/123"
                )
            assert result == {}
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_empty_body_200(self):
        try:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b""
            mock_resp.__enter__ = (
                lambda s: mock_resp
            )
            mock_resp.__exit__ = (
                MagicMock(return_value=False)
            )
            with patch(
                "src.sdk.client.urlopen",
                return_value=mock_resp,
            ):
                result = self.client._request(
                    "GET", "/agents"
                )
            assert result == {}
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_200_with_json_body(self):
        try:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = (
                b'{"id": "abc"}'
            )
            mock_resp.__enter__ = (
                lambda s: mock_resp
            )
            mock_resp.__exit__ = (
                MagicMock(return_value=False)
            )
            with patch(
                "src.sdk.client.urlopen",
                return_value=mock_resp,
            ):
                result = self.client._request(
                    "GET", "/agents/abc"
                )
            assert result == {"id": "abc"}
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_no_content_codes_constant(
        self,
    ):
        try:
            assert 204 in NO_CONTENT_CODES
            assert 205 in NO_CONTENT_CODES
            assert 200 not in NO_CONTENT_CODES
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )
