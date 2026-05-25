import pytest
import sys
from unittest.mock import patch
from src.cli.main import cli, SUPPORTED_OUTPUT_MODES


class TestCLI:
    def test_status_command_no_watch(
        self, monkeypatch
    ):
        try:
            monkeypatch.setattr(
                sys, "argv",
                ["main.py", "status"],
            )
            cli()
        except Exception as e:
            print(
                "Error in"
                " test_status_command"
                f"_no_watch: {e}"
            )
            raise

    def test_status_command_watch_interrupt(
        self, monkeypatch
    ):
        try:
            monkeypatch.setattr(
                sys, "argv",
                ["main.py", "status", "--watch"],
            )

            # Mock time.sleep to raise
            # KeyboardInterrupt immediately
            with patch(
                "time.sleep",
                side_effect=KeyboardInterrupt,
            ):
                with pytest.raises(
                    SystemExit
                ) as exc_info:
                    cli()

                # Check exit code is 0
                assert exc_info.value.code == 0
        except Exception as e:
            print(
                "Error in"
                " test_status_command"
                f"_watch_interrupt: {e}"
            )
            raise

    def test_output_mode_valid(
        self, monkeypatch
    ):
        try:
            for mode in SUPPORTED_OUTPUT_MODES:
                monkeypatch.setattr(
                    sys, "argv",
                    [
                        "main.py",
                        "--output", mode,
                        "status",
                    ],
                )
                cli()
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_output_mode_unsupported(
        self, monkeypatch
    ):
        try:
            monkeypatch.setattr(
                sys, "argv",
                [
                    "main.py",
                    "--output", "yaml",
                    "status",
                ],
            )
            with pytest.raises(
                SystemExit
            ) as exc_info:
                cli()
            # argparse exits with code 2
            # for invalid arguments
            assert exc_info.value.code == 2
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_output_mode_default(
        self, monkeypatch
    ):
        try:
            monkeypatch.setattr(
                sys, "argv",
                ["main.py", "status"],
            )
            # Should not raise — defaults
            # to "text" output mode
            cli()
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_supported_output_modes_constant(
        self,
    ):
        try:
            assert "text" in SUPPORTED_OUTPUT_MODES
            assert "json" in SUPPORTED_OUTPUT_MODES
            assert (
                "table" in SUPPORTED_OUTPUT_MODES
            )
            assert (
                "yaml"
                not in SUPPORTED_OUTPUT_MODES
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )
