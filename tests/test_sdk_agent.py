import pytest
import logging
from typing import Any, Dict
from src.sdk.agent import BaseAgent

logger = logging.getLogger(__name__)

class MockAgent(BaseAgent):
    async def setup(self) -> None:
        pass

    async def handle_task(self, task: Dict[str, Any]) -> Any:
        pass

    async def cleanup(self) -> None:
        pass


class TestBaseAgentMetadata:
    def setup_method(self):
        try:
            self.agent = MockAgent(agent_id="test-id", name="test-agent")
        except Exception as e:
            logger.error(f"Error in setup_method: {str(e)}")
            raise

    def test_set_valid_metadata(self):
        try:
            self.agent.set_metadata("key1", "value1")
            assert self.agent.get_metadata("key1") == "value1"
        except Exception as e:
            logger.error(f"Error in test_set_valid_metadata: {str(e)}")
            raise

    def test_set_empty_metadata_key(self):
        try:
            with pytest.raises(ValueError) as exc_info:
                self.agent.set_metadata("", "value")
            assert "cannot be empty" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_set_empty_metadata_key: {str(e)}")
            raise

    def test_set_whitespace_metadata_key(self):
        try:
            with pytest.raises(ValueError) as exc_info:
                self.agent.set_metadata("   ", "value")
            assert "cannot be empty" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_set_whitespace_metadata_key: {str(e)}")
            raise

    def test_set_non_string_metadata_key(self):
        try:
            with pytest.raises(TypeError) as exc_info:
                self.agent.set_metadata(123, "value")  # type: ignore
            assert "must be a string" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_set_non_string_metadata_key: {str(e)}")
            raise
