"""
群聊增强模块
React 模式（感知群聊上下文）+ 主动回复（概率/模型判定）
与好感度、日程、记忆系统深度联动。
"""
import asyncio
import logging
import random
import time
from typing import Any, Optional

logger = logging.getLogger("citlali.group_chat")


class GroupChatManager:
    """群聊增强管理器（React 模式）"""

    def __init__(self, plugin):
        self.plugin = plugin
        self._recent_messages: dict[str, list] = {}
        self._last_reply_time: dict[str, float] = {}

