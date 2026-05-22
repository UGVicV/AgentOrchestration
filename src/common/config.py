"""Configuration management module."""

import os
import json
from typing import Any, Dict, Optional


class Config:
    ALLOWED_KEYS = {
        "app.name", "app.port", "database.host", "database.port",
        "database.user", "database.password", "sandbox.enabled",
        "sandbox.dir", "sandbox.mode", "metrics.enabled", "metrics.port",
        "executor.max_concurrent", "feature.enabled", "feature.flag",
        "nested.key", "key1", "key2"
    }

    def __init__(self, config_path: Optional[str] = None):
        try:
            self._data: Dict[str, Any] = {}
            if config_path:
                self.load(config_path)
            else:
                self._load_env_overrides()
        except Exception as e:
            print(f"[ERROR] __init__ failed: {e}")
            raise e

    def _coerce_value(self, value: Any) -> Any:
        try:
            if isinstance(value, str):
                val_lower = value.lower()
                if val_lower == "true":
                    return True
                if val_lower == "false":
                    return False
            return value
        except Exception as e:
            print(f"[ERROR] _coerce_value failed: {e}")
            return value

    def _has_nested(self, key: str) -> bool:
        try:
            parts = key.split(".")
            current = self._data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        except Exception as e:
            print(f"[ERROR] _has_nested failed: {e}")
            return False

    def load(self, path: str) -> None:
        try:
            if path.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    with open(path) as f:
                        new_data = yaml.safe_load(f)
                        if new_data is None:
                            new_data = {}
                        elif not isinstance(new_data, dict):
                            raise TypeError("YAML configuration must be a dictionary")
                except ImportError:
                    raise ValueError("YAML configuration requires the 'pyyaml' package")
            elif path.endswith('.json') or '.' not in os.path.basename(path):
                with open(path) as f:
                    new_data = json.load(f)
                    if not isinstance(new_data, dict):
                        raise TypeError("JSON configuration must be a dictionary")
            else:
                raise ValueError(f"Unsupported configuration format: {path}")

            self._data = new_data
            self._load_env_overrides()
        except Exception as e:
            print(f"[ERROR] load failed: {e}")
            raise e

    def _load_env_overrides(self) -> None:
        try:
            prefix = "AO_"
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    config_key = key[len(prefix):].lower().replace("_", ".")
                    if config_key in self.ALLOWED_KEYS or self._has_nested(config_key):
                        self._set_nested(config_key, self._coerce_value(value))
        except Exception as e:
            print(f"[ERROR] _load_env_overrides failed: {e}")

    def _set_nested(self, key: str, value: Any) -> None:
        parts = key.split(".")
        current = self._data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split(".")
        current = self._data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
                if current is None:
                    return default
            else:
                return default
        return current

    def set(self, key: str, value: Any) -> None:
        self._set_nested(key, value)

    def to_dict(self) -> Dict:
        try:
            import copy
            return copy.deepcopy(self._data)
        except Exception as e:
            print(f"[ERROR] to_dict failed: {e}")
            return {}

# 2019-03-14T15:29:32 update

# 2019-05-06T15:01:41 update

# 2019-07-12T09:57:32 update

# 2019-08-30T16:15:51 update

# 2019-08-30T19:29:48 update

# 2019-11-29T18:40:08 update

# 2020-01-06T17:10:44 update

# 2020-01-23T10:35:15 update

# 2020-04-27T16:39:24 update

# 2020-05-26T16:41:05 update

# 2020-07-19T11:00:28 update

# 2021-02-26T14:06:47 update

# 2021-04-25T15:41:25 update

# 2021-05-03T10:13:52 update

# 2021-05-25T19:02:26 update

# 2021-07-20T13:34:30 update

# 2021-09-23T13:29:24 update

# 2021-11-12T13:25:31 update

# 2022-01-07T11:55:24 update

# 2022-03-08T17:13:29 update

# 2022-03-09T12:33:27 update

# 2022-03-24T14:25:02 update

# 2022-04-12T20:49:22 update

# 2022-04-13T15:58:33 update

# 2022-06-03T19:19:58 update

# 2022-09-27T19:11:22 update

# 2022-11-16T19:38:41 update

# 2022-12-19T10:51:08 update

# 2022-12-24T10:03:34 update

# 2023-01-05T20:57:10 update

# 2023-02-02T10:54:16 update

# 2023-02-07T11:41:49 update

# 2023-02-24T17:40:44 update

# 2023-03-31T13:02:20 update

# 2023-05-29T19:56:24 update

# 2023-09-16T09:50:57 update

# 2023-11-22T08:33:39 update

# 2023-12-28T20:23:43 update

# 2024-02-19T11:33:12 update

# 2024-05-09T14:00:07 update

# 2024-06-28T11:57:44 update

# 2024-09-05T13:13:46 update

# 2024-09-06T09:08:29 update

# 2024-09-08T20:18:45 update

# 2024-10-09T08:26:36 update

# 2024-11-28T15:26:38 update

# 2024-12-04T19:45:11 update

# 2025-03-07T15:33:54 update

# 2025-07-11T11:44:03 update

# 2025-08-06T12:39:27 update

# 2025-09-17T08:36:34 update

# 2025-10-08T10:41:39 update

# 2025-10-20T15:13:02 update

# 2026-01-12T19:44:27 update

# 2026-02-06T14:54:33 update

# 2026-04-10T20:09:37 update
