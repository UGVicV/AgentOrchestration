import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from fastapi.responses import Response

from src.api.server import create_app

def test_security_headers_on_success():
    try:
        app = create_app()
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")

def test_security_headers_on_unauthorized():
    try:
        app = create_app()
        client = TestClient(app)
        # /api/v2/agents requires authentication
        response = client.get("/api/v2/agents")
        
        assert response.status_code == 401
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")

def test_security_headers_on_exception():
    try:
        app = create_app()
        
        @app.get("/trigger-error")
        async def trigger_error():
            raise ValueError("Simulated unhandled exception")
            
        client = TestClient(app)
        response = client.get("/trigger-error")
        
        assert response.status_code == 500
        assert "Internal Server Error" in response.text
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")

def test_request_state_cleanup():
    try:
        app = create_app()
        requests_list = []
        
        @app.get("/test-cleanup")
        async def test_cleanup(request: Request):
            requests_list.append(request)
            return {"status": "ok"}
            
        client = TestClient(app)
        response = client.get("/test-cleanup")
        
        assert response.status_code == 200
        assert len(requests_list) == 1
        assert hasattr(requests_list[0].state, "_cleanup")
        assert requests_list[0].state._cleanup is True
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
