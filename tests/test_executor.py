import pytest
from src.agent.executor import AgentExecutor


class TestAgentExecutor:
    def test_valid_max_concurrent(self):
        try:
            # Positive integers
            executor = AgentExecutor(max_concurrent=10)
            assert executor.max_concurrent == 10

            # Float values (should be converted to int)
            executor = AgentExecutor(max_concurrent=5.2)
            assert executor.max_concurrent == 5

            # Numeric strings
            executor = AgentExecutor(max_concurrent="7")
            assert executor.max_concurrent == 7
        except Exception as e:
            print(f"Error in test_valid_max_concurrent: {e}")
            raise

    def test_invalid_negative_max_concurrent(self):
        try:
            with pytest.raises(ValueError, match="max_concurrent must be positive"):
                AgentExecutor(max_concurrent=0)

            with pytest.raises(ValueError, match="max_concurrent must be positive"):
                AgentExecutor(max_concurrent=-5)
        except Exception as e:
            print(f"Error in test_invalid_negative_max_concurrent: {e}")
            raise

    def test_invalid_type_max_concurrent(self):
        try:
            with pytest.raises(ValueError, match="max_concurrent must be numeric"):
                AgentExecutor(max_concurrent="abc")

            with pytest.raises(ValueError, match="max_concurrent must be numeric"):
                AgentExecutor(max_concurrent=None)

            with pytest.raises(ValueError, match="max_concurrent must be numeric"):
                AgentExecutor(max_concurrent=True)  # Booleans are not allowed
        except Exception as e:
            print(f"Error in test_invalid_type_max_concurrent: {e}")
            raise
