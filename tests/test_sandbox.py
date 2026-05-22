import pytest
from src.agent.sandbox import ResourceLimits
from src.common.config import Config


class TestResourceLimits:
    def test_valid_limits(self):
        try:
            # Positive integers
            limits = ResourceLimits(cpu_time=10, memory_mb=256, disk_mb=50)
            assert limits.cpu_time == 10
            assert limits.memory_mb == 256
            assert limits.disk_mb == 50

            # Float values (should be converted to int)
            limits = ResourceLimits(cpu_time=10.5, memory_mb=256.0, disk_mb=50.2)
            assert limits.cpu_time == 10
            assert limits.memory_mb == 256
            assert limits.disk_mb == 50

            # Numeric strings
            limits = ResourceLimits(cpu_time="30", memory_mb="128", disk_mb="10")
            assert limits.cpu_time == 30
            assert limits.memory_mb == 128
            assert limits.disk_mb == 10

            # Numeric float strings
            limits = ResourceLimits(cpu_time="30.5", memory_mb="128.0", disk_mb="10.2")
            assert limits.cpu_time == 30
            assert limits.memory_mb == 128
            assert limits.disk_mb == 10
        except Exception as e:
            print(f"Error in test_valid_limits: {e}")
            raise

    def test_invalid_negative_limits(self):
        try:
            with pytest.raises(ValueError, match="cpu_time must be positive"):
                ResourceLimits(cpu_time=-10)

            with pytest.raises(ValueError, match="memory_mb must be positive"):
                ResourceLimits(memory_mb=0)

            with pytest.raises(ValueError, match="disk_mb must be positive"):
                ResourceLimits(disk_mb=-1)
        except Exception as e:
            print(f"Error in test_invalid_negative_limits: {e}")
            raise

    def test_invalid_non_numeric_limits(self):
        try:
            with pytest.raises(ValueError, match="cpu_time must be numeric"):
                ResourceLimits(cpu_time="abc")

            with pytest.raises(ValueError, match="memory_mb must be numeric"):
                ResourceLimits(memory_mb=[512])

            with pytest.raises(ValueError, match="disk_mb must be numeric"):
                ResourceLimits(disk_mb=None)

            with pytest.raises(ValueError, match="cpu_time must be numeric"):
                ResourceLimits(cpu_time=True)  # Booleans are not acceptable
        except Exception as e:
            print(f"Error in test_invalid_non_numeric_limits: {e}")
            raise

    def test_config_integration(self, tmp_path):
        try:
            # Valid config
            config_file = tmp_path / "valid_limits.json"
            config_file.write_text('{"sandbox": {"cpu_time": "120", "memory_mb": 1024, "disk_mb": 200}}')
            config = Config(str(config_file))

            limits = ResourceLimits(
                cpu_time=config.get("sandbox.cpu_time"),
                memory_mb=config.get("sandbox.memory_mb"),
                disk_mb=config.get("sandbox.disk_mb")
            )
            assert limits.cpu_time == 120
            assert limits.memory_mb == 1024
            assert limits.disk_mb == 200

            # Invalid config (negative value)
            config_file_invalid = tmp_path / "invalid_limits.json"
            config_file_invalid.write_text('{"sandbox": {"cpu_time": -10, "memory_mb": 1024, "disk_mb": 200}}')
            config_invalid = Config(str(config_file_invalid))

            with pytest.raises(ValueError, match="cpu_time must be positive"):
                ResourceLimits(
                    cpu_time=config_invalid.get("sandbox.cpu_time"),
                    memory_mb=config_invalid.get("sandbox.memory_mb"),
                    disk_mb=config_invalid.get("sandbox.disk_mb")
                )
        except Exception as e:
            print(f"Error in test_config_integration: {e}")
            raise
