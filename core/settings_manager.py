"""
设置管理器
将大部分配置项从 AstrBot 插件配置迁移到本地 JSON 文件，
通过 WebUI 管理，简化插件配置。
"""
import json
import os
import logging
from typing import Any

logger = logging.getLogger("citlali.settings")

# 默认设置
DEFAULT_SETTINGS = {
    # 功能开关
    "affinity_enabled": True,
    "inject_context": True,
    "decay_enabled": True,
    "upgrade_notify": True,
    "time_schedule_enabled": True,
    "special_dates_enabled": True,
    "react_mode_enabled": False,
    "react_cooldown_seconds": 30,

    # 好感度
    "daily_chat_min": 5,
    "daily_chat_max": 15,
    "daily_decay_min": 3,
    "daily_decay_max": 1,
    "checkin_min": 15,
    "checkin_max": 30,
    "checkin_cooldown_hours": 24,
    "stage_thresholds": [0, 50, 150, 400, 800, 1500],

    # 时区
    "timezone_offset": 8,
}


class SettingsManager:
    """设置管理器"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "plugin_settings.json")
        self._data: dict = {}
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        # 补全缺失的默认值
        for k, v in DEFAULT_SETTINGS.items():
            if k not in self._data:
                self._data[k] = v

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None) -> Any:
        return self._data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    def get_all(self) -> dict:
        return dict(self._data)

    def update(self, data: dict):
        """批量更新"""
        for k, v in data.items():
            if k in DEFAULT_SETTINGS:
                self._data[k] = v
        self._save()

    def reset(self):
        """重置为默认值"""
        self._data = dict(DEFAULT_SETTINGS)
        self._save()
