"""
被遗忘提醒
当用户很久没来后再次出现时，说一句特别的话。
仅私聊有效。
"""
import json
import os
import random
import time
from typing import Optional


# 按消失时长分级的回复
FORGOTTEN_RESPONSES = {
    # 3-7天
    "short": [
        "哼，你还知道来？",
        "哦，你来了。奶奶我以为你忘了路了。",
        "……你还活着啊。我还以为你被深渊吞了。",
    ],
    # 7-30天
    "medium": [
        "（放下书，看了你一眼）……好久不见。",
        "（别过脸）……你还知道回来。",
        "哼。奶奶我不想你。一点都没想。（声音越来越小）",
        "（沉默了一会儿）……你来了就好。",
    ],
    # 30天以上
    "long": [
        "（看到你的一瞬间愣住了）……你……",
        "（眼眶有点红，但立刻别过脸）……你还知道来？奶奶我以为你……算了。",
        "（声音有点哑）……你还记得路啊。",
        "（很久没说话，然后小声）……我以为你不会来了。",
        "（把一本书塞到你手里）这本……我本来想等你来了给你看。等了好久。",
    ],
}


class ForgottenReminder:
    """被遗忘提醒管理器"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "forgotten_data.json")
        self._data: dict = {}  # user_id -> {"last_active": timestamp}
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

    def update_active(self, user_id: str):
        """更新用户最后活跃时间"""
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id]["last_active"] = time.time()
        self._save()

    def check_forgotten(self, user_id: str) -> Optional[str]:
        """
        检查用户是否"被遗忘"后归来。
        返回回复文本或 None。
        仅在用户长时间不活跃后首次出现时触发。
        """
        now = time.time()
        user_data = self._data.get(user_id, {})
        last_active = user_data.get("last_active", 0)

        if last_active == 0:
            # 首次见面，不触发
            self.update_active(user_id)
            return None

        inactive_days = (now - last_active) / 86400

        # 检查是否已经触发过（避免重复）
        last_trigger = user_data.get("last_forgotten_trigger", 0)
        if now - last_trigger < 86400 * 3:  # 3天内不重复触发
            self.update_active(user_id)
            return None

        response = None
        if inactive_days >= 30:
            response = random.choice(FORGOTTEN_RESPONSES["long"])
        elif inactive_days >= 7:
            response = random.choice(FORGOTTEN_RESPONSES["medium"])
        elif inactive_days >= 3:
            response = random.choice(FORGOTTEN_RESPONSES["short"])

        if response:
            self._data[user_id]["last_forgotten_trigger"] = now

        self.update_active(user_id)
        return response
