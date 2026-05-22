import pytest
import asyncio
import time
from typing import Dict, Any
from src.agent.executor import AgentExecutor


class TestAgentExecutor:
    def setup_method(self):
        pass

    def test_executor_success(self):
        try:
            executor = AgentExecutor(max_results=5)
            async def handler(agent_id: str, task: Dict[str, Any]) -> str:
                return "hello-success"

            execution_id = asyncio.run(executor.execute("agent-1", {"id": "task-1"}, handler))
            assert execution_id is not None
            
            result = executor.get_result(execution_id)
            assert result is not None
            assert result["result"] == "hello-success"
            assert result["agent_id"] == "agent-1"
            assert result["task_id"] == "task-1"
            assert "timestamp" in result
        except Exception as e:
            pytest.fail(f"test_executor_success failed with: {e}")

    def test_executor_error_handling(self):
        try:
            executor = AgentExecutor(max_results=5)
            async def handler(agent_id: str, task: Dict[str, Any]) -> str:
                raise ValueError("Oops, something went wrong")

            execution_id = asyncio.run(executor.execute("agent-1", {"id": "task-2"}, handler))
            assert execution_id is not None
            
            result = executor.get_result(execution_id)
            assert result is not None
            assert "error" in result
            assert "Oops, something went wrong" in result["error"]
            assert "timestamp" in result
        except Exception as e:
            pytest.fail(f"test_executor_error_handling failed with: {e}")

    def test_executor_max_results(self):
        try:
            executor = AgentExecutor(max_results=2)
            async def handler(agent_id: str, task: Dict[str, Any]) -> str:
                return task["val"]

            exec_1 = asyncio.run(executor.execute("agent-1", {"id": "t1", "val": "one"}, handler))
            exec_2 = asyncio.run(executor.execute("agent-1", {"id": "t2", "val": "two"}, handler))
            
            assert executor.get_result(exec_1) is not None
            assert executor.get_result(exec_2) is not None
            
            exec_3 = asyncio.run(executor.execute("agent-1", {"id": "t3", "val": "three"}, handler))
            
            assert executor.get_result(exec_1) is None
            assert executor.get_result(exec_2) is not None
            assert executor.get_result(exec_3) is not None
        except Exception as e:
            pytest.fail(f"test_executor_max_results failed with: {e}")

    def test_executor_ttl(self):
        try:
            executor = AgentExecutor(ttl=0.05)
            async def handler(agent_id: str, task: Dict[str, Any]) -> str:
                return "quick"

            exec_id = asyncio.run(executor.execute("agent-1", {"id": "ttl-task"}, handler))
            
            assert executor.get_result(exec_id) is not None
            
            time.sleep(0.1)
            
            assert executor.get_result(exec_id) is None
        except Exception as e:
            pytest.fail(f"test_executor_ttl failed with: {e}")
