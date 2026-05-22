import pytest
import logging
from src.agent.executor import AgentExecutor

logger = logging.getLogger(__name__)

class TestAgentExecutorValidation:
    def test_init_valid_max_concurrent(self):
        try:
            executor = AgentExecutor(max_concurrent=10)
            assert executor.max_concurrent == 10
        except Exception as e:
            logger.error(f"Error in test_init_valid_max_concurrent: {str(e)}")
            raise

    def test_init_zero_max_concurrent(self):
        try:
            with pytest.raises(ValueError) as exc_info:
                AgentExecutor(max_concurrent=0)
            assert "must be a positive integer" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_init_zero_max_concurrent: {str(e)}")
            raise

    def test_init_negative_max_concurrent(self):
        try:
            with pytest.raises(ValueError) as exc_info:
                AgentExecutor(max_concurrent=-5)
            assert "must be a positive integer" in str(exc_info.value)
        except Exception as e:
            logger.error(f"Error in test_init_negative_max_concurrent: {str(e)}")
            raise

    def test_init_non_int_max_concurrent(self):
        try:
            with pytest.raises(TypeError) as exc_info:
                AgentExecutor(max_concurrent="abc")  # type: ignore
            assert "must be an integer" in str(exc_info.value)

            with pytest.raises(TypeError):
                AgentExecutor(max_concurrent=True)  # type: ignore
        except Exception as e:
            logger.error(f"Error in test_init_non_int_max_concurrent: {str(e)}")
            raise
