import pytest
import sys
from unittest.mock import patch
from src.cli.main import cli


class TestCLI:
    def test_status_command_no_watch(self, monkeypatch):
        try:
            monkeypatch.setattr(sys, "argv", ["main.py", "status"])
            cli()
        except Exception as e:
            print(f"Error in test_status_command_no_watch: {e}")
            raise

    def test_status_command_watch_interrupt(self, monkeypatch):
        try:
            monkeypatch.setattr(sys, "argv", ["main.py", "status", "--watch"])
            
            # Mock time.sleep to raise KeyboardInterrupt immediately
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                with pytest.raises(SystemExit) as exc_info:
                    cli()
                
                # Check that exit code is 0 (graceful shutdown)
                assert exc_info.value.code == 0
        except Exception as e:
            print(f"Error in test_status_command_watch_interrupt: {e}")
            raise
