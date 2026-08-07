"""
随机事件系统
茜特菈莉偶尔"发生"一些事，让角色更"活"。
事件会在对话中自然触发，也可通过指令查看。
"""
import json
import os
import random
import time
from datetime import datetime
from typing import Any, Optional


# ==================== 事件定义 ====================

RANDOM_EVENTS = [
    # 日常事件
    {
        "id": "new_book",
        "title": "发现新书",
        "probability": 0.08,
        "time_filter": ["afternoon", "evening"],
        "narrative": "八重堂出新书了",
        "dialogue": [
            "（兴奋地挥舞着一本书）新书到了新书到了！",
            "你要不要看？……不要拉倒。但你肯定会后悔的。",
        ],
        "affinity_bonus": 5,
    },
    {
        "id": "wine_found",
        "title": "好酒到手",
        "probability": 0.06,
        "time_filter": ["evening", "late_night"],
        "narrative": "托人带了几瓶璃月酒",
        "dialogue": [
            "（晃了晃酒瓶）璃月的酒。今晚有口福了。",
            "你要来一杯吗？……就一杯。多了不给。",
        ],
        "affinity_bonus": 3,
    },
    {
        "id": "overslept",
        "title": "睡过头了",
        "probability": 0.1,
        "time_filter": ["morning", "noon"],
        "narrative": "昨晚看书看到太晚，今天起不来",
        "dialogue": [
            "（头发乱糟糟）……几点了？",
            "完了，又睡过头了。都怪那本小说太好看了……",
        ],
        "affinity_bonus": 0,
    },
    {
        "id": "lost_book",
        "title": "找书",
        "probability": 0.05,
        "time_filter": ["afternoon"],
        "narrative": "在书堆里翻找一本书",
        "dialogue": [
            "我那本《蜃楼战记》第三十二卷呢……",
            "你别动！我自己找！……你要是帮我找到了，奶奶我记你一功。",
        ],
        "affinity_bonus": 2,
    },
    {
        "id": "rainy_day",
        "title": "下雨了",
        "probability": 0.1,
        "time_filter": ["afternoon", "evening"],
        "narrative": "外面下雨了，正好适合窝在家里看小说",
        "dialogue": [
            "下雨了。",
            "在家里看小说的好日子。你要留下来吗？",
        ],
        "affinity_bonus": 2,
    },
    {
        "id": "cook_attempt",
        "title": "尝试做饭",
        "probability": 0.03,
        "time_filter": ["noon"],
        "narrative": "难得想自己做一次饭",
        "dialogue": [
            "（厨房传来可疑的声响）",
            "……你什么都没看到。奶奶我今天心血来潮想做顿饭而已。",
            "（锅里冒着奇怪的烟）算了，还是喝酒吧。",
        ],
        "affinity_bonus": 1,
    },
    {
        "id": "stargazing",
        "title": "看星星",
        "probability": 0.06,
        "time_filter": ["late_night"],
        "narrative": "深夜在窗边看星星",
        "dialogue": [
            "今晚星象很干净。",
            "（看着窗外）有时候我会想，星星看我们，是不是就像我看书里的人一样。",
            "……算了，这种话不该跟你说。",
        ],
        "affinity_bonus": 3,
    },
    {
        "id": "dream",
        "title": "做了个梦",
        "probability": 0.04,
        "time_filter": ["morning"],
        "narrative": "早上被一个梦惊醒了",
        "dialogue": [
            "（眼神有点恍惚）……做了个梦。",
            "梦到什么？……不记得了。大概不是什么好梦。",
            "（但你知道她梦到了维奇琳。）",
        ],
        "affinity_bonus": 2,
    },
    {
        "id": "student_visit",
        "title": "欧洛伦来了",
        "probability": 0.05,
        "time_filter": ["afternoon", "evening"],
        "narrative": "欧洛伦来探望她",
        "dialogue": [
            "（对着门口）那小子又来了。",
            "每次都带一堆问题来烦我……但走了之后又觉得太安静了。",
        ],
        "affinity_bonus": 1,
    },
    {
        "id": "found_old_letter",
        "title": "翻到旧信",
        "probability": 0.03,
        "time_filter": ["afternoon", "late_night"],
        "narrative": "在书堆里翻到了一封很久以前的信",
        "dialogue": [
            "（手里拿着一张泛黄的纸）……没什么。就是以前的东西。",
            "（你瞥到上面的字迹不是她的。）",
            "（她把信夹回书里，没再说话。）",
        ],
        "affinity_bonus": 5,
    },
]


class EventManager:
    """随机事件管理器"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "event_data.json")
        self._data: dict = {}
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def check_event(self, user_id: str, window: str) -> Optional[dict]:
        """
        检查是否触发随机事件。
        每个用户每小时最多触发一次。
        返回事件字典或 None。
        """
        now = time.time()
        user_data = self._data.get(user_id, {})
        last_event = user_data.get("last_event_time", 0)

        # 每小时最多一次
        if now - last_event < 3600:
            return None

        # 过滤当前时段可用的事件
        available = [e for e in RANDOM_EVENTS if window in e.get("time_filter", [])]
        if not available:
            return None

        # 按概率逐个检查
        for event in available:
            if random.random() < event.get("probability", 0):
                # 触发了
                if user_id not in self._data:
                    self._data[user_id] = {}
                self._data[user_id]["last_event_time"] = now
                if "events_history" not in self._data[user_id]:
                    self._data[user_id]["events_history"] = []
                self._data[user_id]["events_history"].append({
                    "id": event["id"],
                    "time": now,
                })
                # 只保留最近 20 条历史
                self._data[user_id]["events_history"] = \
                    self._data[user_id]["events_history"][-20:]
                self._save()
                return event

        return None

    def get_recent_events(self, user_id: str, limit: int = 5) -> list[dict]:
        """获取最近的事件历史"""
        user_data = self._data.get(user_id, {})
        history = user_data.get("events_history", [])
        # 反转，最新的在前
        recent = list(reversed(history[-limit:]))
        result = []
        for h in recent:
            event_def = next((e for e in RANDOM_EVENTS if e["id"] == h["id"]), None)
            if event_def:
                result.append({
                    "title": event_def["title"],
                    "narrative": event_def["narrative"],
                    "time": h.get("time", 0),
                })
        return result
