import pytest
from src.sdk.client import OrchestratorClient
from src.sdk.decorators import on_event

class TestSDKClient:
    def test_register_agent_blank_name_fails(self):
        client = OrchestratorClient()
        with pytest.raises(ValueError) as excinfo:
            client.register_agent("", "worker.processor")
        assert "Agent name cannot be blank" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            client.register_agent("   ", "worker.processor")
        assert "Agent name cannot be blank" in str(excinfo.value)

    def test_on_event_decorator_blank_name_fails(self):
        with pytest.raises(ValueError) as excinfo:
            @on_event("")
            async def handler():
                pass
        assert "Event type cannot be blank" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            @on_event("   ")
            async def handler():
                pass
        assert "Event type cannot be blank" in str(excinfo.value)

    def test_on_event_decorator_valid(self):
        @on_event("agent.started")
        async def handler():
            return "ok"
        
        assert handler.__event_handler__ == "agent.started"
