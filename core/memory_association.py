"""
记忆关联模块
追踪用户之间的关系，让茜特菈莉记住"谁和谁一起来过"。
"""
import json
import os
import time
from typing import Optional


class MemoryAssociation:
    """用户关系记忆"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "association_data.json")
        self._data: dict = {}  # "userA:userB" -> {interactions: [...]}
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

    def _key(self, user_a: str, user_b: str) -> str:
        """生成稳定的 key（排序）"""
        return ":".join(sorted([user_a, user_b]))

    def record_interaction(self, user_a: str, user_b: str, context: str = "",
                           nick_a: str = "", nick_b: str = ""):
        """记录一次互动"""
        key = self._key(user_a, user_b)
        if key not in self._data:
            self._data[key] = {
                "users": [user_a, user_b],
                "nicknames": {},
                "interactions": [],
                "first_seen": time.time(),
            }

        assoc = self._data[key]
        if nick_a:
            assoc["nicknames"][user_a] = nick_a
        if nick_b:
            assoc["nicknames"][user_b] = nick_b

        assoc["interactions"].append({
            "time": time.time(),
            "context": context[:200],
        })
        # 只保留最近 50 条
        assoc["interactions"] = assoc["interactions"][-50:]
        assoc["last_seen"] = time.time()
        self._save()

    def get_association(self, user_a: str, user_b: str) -> Optional[dict]:
        """获取两个用户之间的关系信息"""
        key = self._key(user_a, user_b)
        data = self._data.get(key)
        if not data:
            return None
        return {
            "count": len(data.get("interactions", [])),
            "first_seen": data.get("first_seen", 0),
            "last_seen": data.get("last_seen", 0),
            "nicknames": data.get("nicknames", {}),
            "recent_context": data["interactions"][-1]["context"] if data.get("interactions") else "",
        }

    def get_user_associations(self, user_id: str) -> list[dict]:
        """获取一个用户的所有关联"""
        results = []
        for key, data in self._data.items():
            users = data.get("users", [])
            if user_id in users:
                other = users[1] if users[0] == user_id else users[0]
                results.append({
                    "other_user": other,
                    "other_nickname": data.get("nicknames", {}).get(other, ""),
                    "count": len(data.get("interactions", [])),
                    "last_seen": data.get("last_seen", 0),
                })
        results.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
        return results

    def get_context_for_user(self, user_id: str, nickname: str = "") -> str:
        """
        为指定用户生成关联上下文，注入到 LLM 请求中。
        格式：[关联] 用户A(昵称) 和 用户B(昵称) 见过X次
        """
        assocs = self.get_user_associations(user_id)
        if not assocs:
            return ""

        lines = []
        for a in assocs[:3]:  # 最多显示3个关联
            other_nick = a.get("other_nickname", "") or a["other_user"][:8]
            count = a.get("count", 0)
            lines.append(f"{other_nick}({count}次)")

        if lines:
            return "[关联]" + ",".join(lines)
        return ""
