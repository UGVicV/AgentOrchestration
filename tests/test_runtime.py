import pytest
from src.agent.runtime import (
    AgentRuntime,
    RuntimeState,
)


class TestRuntimeCommandValidation:
    def setup_method(self):
        self.runtime = AgentRuntime()

    def test_empty_command_rejected(self):
        try:
            with pytest.raises(
                ValueError,
                match="non-empty list",
            ):
                self.runtime.start(
                    "agent-1", []
                )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_none_command_rejected(self):
        try:
            with pytest.raises(
                ValueError,
                match="non-empty list",
            ):
                self.runtime.start(
                    "agent-1", None
                )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_non_list_command_rejected(
        self,
    ):
        try:
            with pytest.raises(
                ValueError,
                match="non-empty list",
            ):
                self.runtime.start(
                    "agent-1",
                    "echo hello",
                )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_non_string_items_rejected(
        self,
    ):
        try:
            with pytest.raises(
                ValueError,
                match="must be strings",
            ):
                self.runtime.start(
                    "agent-1", [123, 456]
                )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_state_not_mutated_on_reject(
        self,
    ):
        try:
            with pytest.raises(ValueError):
                self.runtime.start(
                    "agent-1", []
                )
            state = self.runtime.get_state(
                "agent-1"
            )
            assert (
                state == RuntimeState.STOPPED
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_valid_command_runs(self):
        try:
            result = self.runtime.start(
                "agent-1",
                ["echo", "hello"],
            )
            assert result is True
            state = self.runtime.get_state(
                "agent-1"
            )
            assert state in (
                RuntimeState.RUNNING,
                RuntimeState.CRASHED,
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

# 2019-01-23T10:28:57 update
