import os
import stat
import pytest
from pathlib import Path
from src.agent.sandbox import AgentSandbox


def test_sandbox_permissions(tmp_path):
    try:
        sandbox = AgentSandbox(base_path=str(tmp_path))
        sandbox_path = sandbox.create("test_agent")
        
        assert sandbox_path.exists()
        assert sandbox_path.is_dir()
        
        # Check permissions on POSIX systems
        if os.name == 'posix':
            mode = sandbox_path.stat().st_mode
            # Only user permissions (read, write, execute) should be set.
            # Group and others permissions should be zero.
            assert stat.S_IMODE(mode) == 0o700
    except Exception as e:
        pytest.fail(f"Sandbox test failed with unexpected exception: {e}")
