import pytest
import sys
import logging
import argparse
from unittest.mock import patch
from src.cli.main import cli, non_negative_int

logger = logging.getLogger(__name__)

class TestCLI:
    def test_non_negative_int_valid(self):
        try:
            assert non_negative_int("0") == 0
            assert non_negative_int("10") == 10
        except Exception as e:
            logger.error(f"Error in test_non_negative_int_valid: {str(e)}")
            raise

    def test_non_negative_int_negative(self):
        try:
            with pytest.raises(argparse.ArgumentTypeError) as exc_info:
                non_negative_int("-5")
            assert "must be non-negative" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_non_negative_int_negative: {str(e)}")
            raise

    def test_non_negative_int_invalid_string(self):
        try:
            with pytest.raises(argparse.ArgumentTypeError) as exc_info:
                non_negative_int("abc")
            assert "must be a valid integer" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_non_negative_int_invalid_string: {str(e)}")
            raise

    @patch("sys.argv", ["cli_bin", "logs", "agent-123", "--tail", "10"])
    def test_cli_logs_valid_tail(self):
        try:
            # Should run successfully without raising SystemExit or unexpected error
            cli()
        except SystemExit as e:
            if e.code != 0:
                logger.error(f"CLI exited unexpectedly with code {e.code}")
                raise
        except Exception as e:
            logger.error(f"Error in test_cli_logs_valid_tail: {str(e)}")
            raise

    @patch("sys.argv", ["cli_bin", "logs", "agent-123", "--tail", "-5"])
    def test_cli_logs_negative_tail(self):
        try:
            with pytest.raises(SystemExit) as exc_info:
                cli()
            assert exc_info.value.code == 2
        except Exception as e:
            logger.error(f"Error in test_cli_logs_negative_tail: {str(e)}")
            raise
