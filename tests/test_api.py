import sys
import os
import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

# Import ExceptionMiddleware trực tiếp bằng cách thêm thư mục src/api vào path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/api"))
)
from middleware import ExceptionMiddleware  # noqa: E402


# Tạo một AuthMiddleware giả lập tương tự như AuthMiddleware thật
class MockAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if (
            request.url.path.startswith("/api/v2")
            and request.url.path != "/api/v2/auth/token"
        ):
            token = request.headers.get("Authorization", "")
            if not token.startswith("Bearer "):
                return Response(status_code=401, content="Unauthorized")
        return await call_next(request)


def test_exception_middleware_unhandled_exception():
    try:
        app = FastAPI()

        # Đăng ký ExceptionMiddleware
        app.add_middleware(
            ExceptionMiddleware,
            cors_origins="http://localhost:3000,http://example.com",
            trusted_hosts="*"
        )

        @app.get("/api/v2/test-error")
        async def trigger_error():
            raise RuntimeError("Test unhandled exception")

        client = TestClient(app)
        response = client.get(
            "/api/v2/test-error",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 500
        data = response.json()
        assert data == {"detail": "Internal Server Error"}
        assert (
            response.headers.get("Access-Control-Allow-Origin")
            == "http://localhost:3000"
        )
        assert (
            response.headers.get("Access-Control-Allow-Credentials")
            == "true"
        )
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


def test_exception_middleware_auth_error():
    try:
        app = FastAPI()

        # Đăng ký MockAuthMiddleware trước
        app.add_middleware(MockAuthMiddleware)

        # Đăng ký ExceptionMiddleware sau cùng để nó nằm ở lớp ngoài cùng
        app.add_middleware(
            ExceptionMiddleware,
            cors_origins="http://localhost:3000,http://example.com",
            trusted_hosts="*"
        )

        @app.get("/api/v2/agents")
        async def get_agents():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get(
            "/api/v2/agents",
            headers={"Origin": "http://example.com"}
        )

        print("DEBUG - Response status code:", response.status_code)
        print("DEBUG - Response headers:", dict(response.headers))
        print("DEBUG - Response text:", response.text)

        assert response.status_code == 401
        assert response.text == "Unauthorized"

        assert (
            response.headers.get("Access-Control-Allow-Origin")
            == "http://example.com"
        )
        assert (
            response.headers.get("Access-Control-Allow-Credentials")
            == "true"
        )
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
