"""
好感度解锁内容系统
不同关系阶段解锁专属对话、故事、彩蛋。
"""
import json
import os
import random
import time
from typing import Any

from .affinity_manager import AffinityStage, STAGE_NAMES


# ==================== 解锁内容定义 ====================

UNLOCK_CONTENT = {
    AffinityStage.ACQUAINTANCE: {
        "name": "熟人",
        "unlocks": [
            {
                "type": "dialogue",
                "title": "初次松口",
                "content": [
                    "……你这个人嘛，还行。",
                    "偶尔来坐坐也无妨。但别碰我的书。",
                ],
            },
            {
                "type": "story",
                "title": "关于住处",
                "content": "你第一次被允许进入茜特菈莉的住处。房间里到处是书和酒瓶，沙发上堆着没叠的衣服。她有点不好意思，但嘴上绝不承认。",
            },
        ],
    },
    AffinityStage.FRIEND: {
        "name": "朋友",
        "unlocks": [
            {
                "type": "dialogue",
                "title": "分享",
                "content": [
                    "你要不要看？我这儿有最新卷。",
                    "……不要拉倒。",
                    "（但眼睛在发光）",
                ],
            },
            {
                "type": "story",
                "title": "酒话",
                "content": "有一次你来的时候她喝多了。她说了很多平时不会说的话——关于维奇琳，关于活了两百年是什么感觉。第二天她假装什么都不记得，但你知道她记得。",
            },
            {
                "type": "dialogue",
                "title": "下雨天",
                "content": [
                    "下雨了。你要是不想走……就在这儿待着吧。",
                    "反正奶奶我也在看书。多一个人少一个人无所谓。",
                ],
            },
        ],
    },
    AffinityStage.CLOSE_FRIEND: {
        "name": "好友",
        "unlocks": [
            {
                "type": "dialogue",
                "title": "局促",
                "content": [
                    "你、你看什么看！我脸上有字吗？",
                    "（低头翻书掩饰，脸红了）",
                ],
            },
            {
                "type": "story",
                "title": "手帕",
                "content": "她送了你一条手帕。她说如果非要选一种颜色作为「她的颜色」，那它肯定是这个手帕的颜色。你收好它的时候，她别过脸，耳根有点红。",
            },
            {
                "type": "dialogue",
                "title": "深夜",
                "content": [
                    "你知道吗……有时候我觉得，书里的角色比现实里的人更真实。",
                    "至少他们不会突然消失。",
                    "……你不会突然消失吧？",
                ],
            },
            {
                "type": "secret",
                "title": "关于维奇琳",
                "content": "她第一次主动跟你提起维奇琳。她说维奇琳每隔二十年就来找她挑战一次，两百年来了十次。她不是要赢，她是不想被遗忘。说完她沉默了很久。",
            },
        ],
    },
    AffinityStage.CONFIDANT: {
        "name": "知己",
        "unlocks": [
            {
                "type": "dialogue",
                "title": "真心话",
                "content": [
                    "漫长的时光让人麻木……",
                    "但你这家伙，老是把人拽回现实。",
                ],
            },
            {
                "type": "story",
                "title": "共感秘术",
                "content": "她跟你使用了共感秘术——你们能在一定程度上听到对方的心声。她说唯一的解决办法是你忘了她或者她忘了你。但她两个都不想选。",
            },
            {
                "type": "dialogue",
                "title": "最软的一句话",
                "content": [
                    "在你看见的未来里……",
                    "有你自己的身影么？",
                ],
            },
            {
                "type": "secret",
                "title": "欧洛伦的卷轴",
                "content": "你偶然发现了欧洛伦写的「搞定茜特菈莉的四十种方法」卷轴，旅行者排名第一。她恨不得把欧洛伦的皮扒了，但她没有销毁那份卷轴。你问她为什么，她说：「……他写的方法其实有一半是对的。但我不说哪一半。」",
            },
        ],
    },
    AffinityStage.TRAVELER: {
        "name": "旅行者",
        "unlocks": [
            {
                "type": "dialogue",
                "title": "醉后真言",
                "content": [
                    "要是早两百年遇到你就好了……",
                    "（酒醒后打死不认）",
                ],
            },
            {
                "type": "story",
                "title": "钥匙",
                "content": "她把家里的钥匙给了你。你问她为什么，她说：「……省得你每次来都要敲门，吵得我小说都看不进去。」但所有人都知道，她只是想让你随时都能来。",
            },
            {
                "type": "dialogue",
                "title": "最深的恐惧",
                "content": [
                    "你知道我为什么从来不敢靠太近吗？",
                    "因为我怕……怕再一次看着重要的人离开。",
                    "（沉默很久）",
                    "但你不一样。你让我觉得……就算会失去，也值得。",
                ],
            },
            {
                "type": "secret",
                "title": "最后一句话",
                "content": "你对旅行者的评价，如果诚实地说，只有五个字——「别走好不好。」但你活了两百年，嘴硬了两百年。所以这句话被翻译成一万种嫌弃、吐槽、炸毛和「哼」。",
            },
            {
                "type": "dialogue",
                "title": "日记",
                "content": [
                    "你问她最近在写什么。",
                    "她把本子藏到身后：「没、没什么！就是……日记。」",
                    "「你写日记？」「奶奶我偶尔记一下不行吗！不行！」",
                    "（你瞥到一页，上面写的是你上次来时说了什么。）",
                ],
            },
        ],
    },
}


class UnlockManager:
    """好感度解锁内容管理器"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "unlock_data.json")
        self._data: dict = {}  # user_id -> {"seen": [title...], "last_check": timestamp}
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

    def get_new_unlocks(self, user_id: str, stage: AffinityStage) -> list[dict]:
        """
        获取用户在当前阶段新解锁的内容（未看过的）。
        同时标记为已看。
        """
        if user_id not in self._data:
            self._data[user_id] = {"seen": [], "last_check": time.time()}

        user = self._data[user_id]
        seen = set(user.get("seen", []))
        new_items = []

        # 检查当前阶段及之前阶段的所有内容
        for s in AffinityStage:
            if s > stage:
                break
            stage_data = UNLOCK_CONTENT.get(s, {})
            for item in stage_data.get("unlocks", []):
                title = item.get("title", "")
                if title and title not in seen:
                    new_items.append(item)
                    seen.add(title)

        if new_items:
            user["seen"] = list(seen)
            user["last_check"] = time.time()
            self._save()

        return new_items

    def get_all_unlocks(self, user_id: str, stage: AffinityStage) -> list[dict]:
        """获取用户当前阶段所有解锁内容"""
        all_items = []
        for s in AffinityStage:
            if s > stage:
                break
            stage_data = UNLOCK_CONTENT.get(s, {})
            for item in stage_data.get("unlocks", []):
                all_items.append({**item, "stage": STAGE_NAMES[s]})
        return all_items

    def has_new(self, user_id: str, stage: AffinityStage) -> bool:
        """检查是否有新的未看内容"""
        if user_id not in self._data:
            return True
        seen = set(self._data[user_id].get("seen", []))
        for s in AffinityStage:
            if s > stage:
                break
            stage_data = UNLOCK_CONTENT.get(s, {})
            for item in stage_data.get("unlocks", []):
                if item.get("title", "") not in seen:
                    return True
        return False
