import pytest
from src.agent.executor import AgentExecutor


def test_agent_executor_validation():
    try:
        # Valid cases
        executor = AgentExecutor(max_concurrent=5)
        assert executor.max_concurrent == 5
        
        executor2 = AgentExecutor()
        assert executor2.max_concurrent == 5
        
        # Invalid cases (TypeError)
        with pytest.raises(TypeError):
            AgentExecutor(max_concurrent="5")
            
        with pytest.raises(TypeError):
            AgentExecutor(max_concurrent=True)
            
        # Invalid cases (ValueError)
        with pytest.raises(ValueError):
            AgentExecutor(max_concurrent=0)
            
        with pytest.raises(ValueError):
            AgentExecutor(max_concurrent=-1)
    except Exception as e:
        pytest.fail(f"AgentExecutor test failed with unexpected exception: {e}")
