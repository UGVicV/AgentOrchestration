"""Tests for tenant-scoped batch cancel endpoint."""

import pytest
from src.api.routes import register_execution, verify_execution_access


class TestTenantScopeVerification:
    """Test the tenant scope verification logic for batch cancel."""

    def setup_method(self):
        try:
            # Clear tenant registry
            import src.api.routes as routes
            routes._tenant_registry.clear()
        except Exception as e:
            pytest.fail(f"Setup failed: {e}")

    def test_unscoped_access_allowed(self):
        """No tenant = unrestricted access."""
        try:
            register_execution("exec-1", "tenant-a")
            assert verify_execution_access("exec-1", None) is True
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_correct_tenant_allowed(self):
        """Matching tenant should pass."""
        try:
            register_execution("exec-1", "tenant-a")
            assert verify_execution_access("exec-1", "tenant-a") is True
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_wrong_tenant_rejected(self):
        """Wrong tenant should be blocked."""
        try:
            register_execution("exec-1", "tenant-a")
            assert verify_execution_access("exec-1", "tenant-b") is False
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_unknown_execution_allowed(self):
        """Untracked executions are accessible."""
        try:
            assert verify_execution_access("unknown-exec", "tenant-a") is True
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_multiple_tenants_isolation(self):
        """Tenants should only see their own executions."""
        try:
            register_execution("exec-1", "tenant-a")
            register_execution("exec-2", "tenant-b")
            register_execution("exec-3", "tenant-a")

            assert verify_execution_access("exec-1", "tenant-a") is True
            assert verify_execution_access("exec-2", "tenant-a") is False
            assert verify_execution_access("exec-3", "tenant-a") is True
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_batch_cancel_endpoint_exists(self):
        """Verify the batch-cancel route is registered."""
        try:
            from src.api.routes import router
            routes = [r.path for r in router.routes]
            assert "/agents/batch-cancel" in routes
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")
