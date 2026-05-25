import pytest
from unittest.mock import patch
from src.agent.sandbox import (
    AgentSandbox,
    ResourceLimits,
)
from src.common.config import Config


class TestResourceLimits:
    def test_valid_limits(self):
        try:
            # Positive integers
            limits = ResourceLimits(
                cpu_time=10,
                memory_mb=256,
                disk_mb=50,
            )
            assert limits.cpu_time == 10
            assert limits.memory_mb == 256
            assert limits.disk_mb == 50

            # Float values (converted to int)
            limits = ResourceLimits(
                cpu_time=10.5,
                memory_mb=256.0,
                disk_mb=50.2,
            )
            assert limits.cpu_time == 10
            assert limits.memory_mb == 256
            assert limits.disk_mb == 50

            # Numeric strings
            limits = ResourceLimits(
                cpu_time="30",
                memory_mb="128",
                disk_mb="10",
            )
            assert limits.cpu_time == 30
            assert limits.memory_mb == 128
            assert limits.disk_mb == 10

            # Numeric float strings
            limits = ResourceLimits(
                cpu_time="30.5",
                memory_mb="128.0",
                disk_mb="10.2",
            )
            assert limits.cpu_time == 30
            assert limits.memory_mb == 128
            assert limits.disk_mb == 10
        except Exception as e:
            print(
                "Error in"
                f" test_valid_limits: {e}"
            )
            raise

    def test_invalid_negative_limits(self):
        try:
            with pytest.raises(
                ValueError,
                match="cpu_time must be"
                " positive",
            ):
                ResourceLimits(cpu_time=-10)

            with pytest.raises(
                ValueError,
                match="memory_mb must be"
                " positive",
            ):
                ResourceLimits(memory_mb=0)

            with pytest.raises(
                ValueError,
                match="disk_mb must be"
                " positive",
            ):
                ResourceLimits(disk_mb=-1)
        except Exception as e:
            print(
                "Error in test_invalid"
                f"_negative_limits: {e}"
            )
            raise

    def test_invalid_non_numeric_limits(self):
        try:
            with pytest.raises(
                ValueError,
                match="cpu_time must be"
                " numeric",
            ):
                ResourceLimits(
                    cpu_time="abc"
                )

            with pytest.raises(
                ValueError,
                match="memory_mb must be"
                " numeric",
            ):
                ResourceLimits(
                    memory_mb=[512]
                )

            with pytest.raises(
                ValueError,
                match="disk_mb must be"
                " numeric",
            ):
                ResourceLimits(disk_mb=None)

            with pytest.raises(
                ValueError,
                match="cpu_time must be"
                " numeric",
            ):
                # Booleans not acceptable
                ResourceLimits(cpu_time=True)
        except Exception as e:
            print(
                "Error in test_invalid"
                f"_non_numeric_limits: {e}"
            )
            raise

    def test_config_integration(
        self, tmp_path
    ):
        try:
            # Valid config
            config_file = (
                tmp_path / "valid_limits.json"
            )
            config_file.write_text(
                '{"sandbox": {'
                '"cpu_time": "120",'
                ' "memory_mb": 1024,'
                ' "disk_mb": 200}}'
            )
            config = Config(str(config_file))

            limits = ResourceLimits(
                cpu_time=config.get(
                    "sandbox.cpu_time"
                ),
                memory_mb=config.get(
                    "sandbox.memory_mb"
                ),
                disk_mb=config.get(
                    "sandbox.disk_mb"
                ),
            )
            assert limits.cpu_time == 120
            assert limits.memory_mb == 1024
            assert limits.disk_mb == 200

            # Invalid config (negative value)
            bad_file = (
                tmp_path
                / "invalid_limits.json"
            )
            bad_file.write_text(
                '{"sandbox": {'
                '"cpu_time": -10,'
                ' "memory_mb": 1024,'
                ' "disk_mb": 200}}'
            )
            bad_config = Config(str(bad_file))

            with pytest.raises(
                ValueError,
                match="cpu_time must be"
                " positive",
            ):
                ResourceLimits(
                    cpu_time=bad_config.get(
                        "sandbox.cpu_time"
                    ),
                    memory_mb=bad_config.get(
                        "sandbox.memory_mb"
                    ),
                    disk_mb=bad_config.get(
                        "sandbox.disk_mb"
                    ),
                )
        except Exception as e:
            print(
                "Error in test_config"
                f"_integration: {e}"
            )
            raise


class TestCleanupAll:
    def test_cleanup_all_success(
        self, tmp_path
    ):
        try:
            sb = AgentSandbox(str(tmp_path))
            sb.create("agent-1")
            sb.create("agent-2")
            result = sb.cleanup_all()
            assert len(
                result["succeeded"]
            ) == 2
            assert len(result["failed"]) == 0
            assert (
                "agent-1"
                in result["succeeded"]
            )
            assert (
                "agent-2"
                in result["succeeded"]
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_cleanup_all_partial_fail(
        self, tmp_path
    ):
        try:
            sb = AgentSandbox(str(tmp_path))
            sb.create("ok-agent")
            sb.create("bad-agent")
            original_destroy = sb.destroy

            def mock_destroy(agent_id):
                if agent_id == "bad-agent":
                    raise OSError(
                        "permission denied"
                    )
                return original_destroy(
                    agent_id
                )

            with patch.object(
                sb, "destroy",
                side_effect=mock_destroy,
            ):
                result = sb.cleanup_all()
            assert len(result["failed"]) >= 1
            failed_ids = [
                f["agent_id"]
                for f in result["failed"]
            ]
            assert "bad-agent" in failed_ids
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_cleanup_all_empty(
        self, tmp_path
    ):
        try:
            sb = AgentSandbox(str(tmp_path))
            result = sb.cleanup_all()
            assert result["succeeded"] == []
            assert result["failed"] == []
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )
