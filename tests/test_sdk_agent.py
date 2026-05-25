import pytest
from src.sdk.agent import BaseAgent
from typing import Any, Dict

class MockAgent(BaseAgent):
    async def setup(self) -> None:
        pass

    async def handle_task(self, task: Dict[str, Any]) -> Any:
        pass

    async def cleanup(self) -> None:
        pass

def test_set_metadata_valid():
    try:
        agent = MockAgent(agent_id="test_id", name="test_agent")
        agent.set_metadata("valid_key", "value")
        assert agent.get_metadata("valid_key") == "value"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")

def test_set_metadata_trim():
    try:
        agent = MockAgent(agent_id="test_id", name="test_agent")
        agent.set_metadata("  trimmed_key  ", "value")
        assert agent.get_metadata("trimmed_key") == "value"
        assert agent.get_metadata("  trimmed_key  ") == "value"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")

def test_set_metadata_empty_key():
    try:
        agent = MockAgent(agent_id="test_id", name="test_agent")
        with pytest.raises(ValueError, match="Metadata key cannot be empty or whitespace-only"):
            agent.set_metadata("", "value")
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")

def test_set_metadata_whitespace_only_key():
    try:
        agent = MockAgent(agent_id="test_id", name="test_agent")
        with pytest.raises(ValueError, match="Metadata key cannot be empty or whitespace-only"):
            agent.set_metadata("     ", "value")
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")

def test_set_metadata_invalid_type_key():
    try:
        agent = MockAgent(agent_id="test_id", name="test_agent")
        with pytest.raises(TypeError, match="Metadata key must be a string"):
            agent.set_metadata(123, "value")  # type: ignore
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
