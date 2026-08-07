"""
群聊增强模块
React 模式：感知群聊上下文，根据好感度/时段决定是否回复。
"""
import random
import time
import logging

logger = logging.getLogger("citlali.group_chat")


class GroupChatManager:
    """群聊增强管理器（React 模式）"""

    def __init__(self, plugin):
        self.plugin = plugin
        self._recent_messages: dict[str, list] = {}
        self._last_reply_time: dict[str, float] = {}

    async def should_react(self, event, message: str, sender_id: str) -> tuple[bool, str]:
        """
        判断是否应该对群聊消息做出反应。
        返回 (是否回复, 回复内容) — 内容为空则由 LLM 生成。
        """
        if not self.plugin.settings.get("react_mode_enabled", False):
            return False, ""

        session_id = event.unified_msg_origin

        # 记录消息到缓冲区
        if session_id not in self._recent_messages:
            self._recent_messages[session_id] = []
        self._recent_messages[session_id].append({
            "sender": sender_id,
            "content": message,
            "time": time.time(),
        })
        self._recent_messages[session_id] = self._recent_messages[session_id][-30:]

        # 冷却检查
        cooldown = self.plugin.settings.get("react_cooldown_seconds", 30)
        last = self._last_reply_time.get(session_id, 0)
        if time.time() - last < cooldown:
            return False, ""

        # 好感度影响
        from .affinity_manager import AffinityStage
        stage = self.plugin.affinity_mgr.get_stage(sender_id)
        stage_value = int(stage)

        # 日程时段修正
        from .time_schedule import get_current_window
        window = get_current_window()
        window_mods = {
            "late_night": 1.3,
            "morning": 0.5,
            "noon": 0.8,
            "afternoon": 1.0,
            "evening": 1.2,
        }
        window_mod = window_mods.get(window, 1.0)

        # 基础回复概率
        base_probs = {0: 0.02, 1: 0.04, 2: 0.08, 3: 0.12, 4: 0.18, 5: 0.25}
        base_prob = base_probs.get(stage_value, 0.02) * window_mod

        # 关键词检测
        trigger_result = self._check_triggers(message, sender_id, stage, window)
        if trigger_result:
            if random.random() < 0.7:
                self._last_reply_time[session_id] = time.time()
                return True, trigger_result

        # 被提及
        if self._is_mentioned(message):
            self._last_reply_time[session_id] = time.time()
            return True, ""

        # 概率触发
        if random.random() < base_prob:
            self._last_reply_time[session_id] = time.time()
            return True, ""

        return False, ""

    def _check_triggers(self, message: str, sender_id: str, stage, window: str) -> str:
        """检测群聊消息中的触发词"""
        msg = message.lower()

        # 小说
        novel_keywords = ["小说", "新书", "更新", "停更", "八重堂", "蜃楼", "轻小说", "看书"]
        if any(k in msg for k in novel_keywords):
            if random.random() < 0.4:
                return random.choice([
                    "哦？你们在聊小说？",
                    "（竖起耳朵）什么小说？奶奶我也想听。",
                    "八重堂出新书了？！",
                ])

        # 酒
        wine_keywords = ["喝酒", "酒", "干杯", "醉", "举杯"]
        if any(k in msg for k in wine_keywords):
            if window in ("evening", "late_night"):
                if random.random() < 0.5:
                    return random.choice([
                        "（晃了晃酒瓶）……你们在喝什么？",
                        "岁月献给小酒杯……嗝。",
                        "带上奶奶我。",
                    ])
            elif window == "morning":
                return "大早上就喝酒？"

        # 占卜
        divination_keywords = ["占卜", "命运", "星象", "预言", "算命"]
        if any(k in msg for k in divination_keywords):
            if random.random() < 0.3:
                return random.choice([
                    "困于迷雾的旅者……需要奶奶我帮忙看看吗？",
                    "哼，占卜这种事，还得找专业的人。",
                ])

        # 天气
        weather_keywords = ["下雨了", "下雪了", "好热", "好冷"]
        if any(k in msg for k in weather_keywords):
            if random.random() < 0.3:
                if "下雨" in msg:
                    return "下雨了。在家里看小说的好日子。"
                elif "下雪" in msg:
                    return "下雪了？！奶奶我从来没见过！"
                elif "热" in msg:
                    return "纳塔的太阳不会累的。不像我，我会。"

        # 被叫奶奶
        if "奶奶" in msg and random.random() < 0.3:
            if int(stage) >= 3:
                return "嗯？谁在叫我？"
            else:
                return "哼。"

        return ""

    def _is_mentioned(self, message: str) -> bool:
        """检测是否被提及"""
        keywords = ["茜特菈莉", "黑曜石奶奶", "黑曜石", "萨满"]
        return any(k in message for k in keywords)

    def get_group_context(self, session_id: str) -> str:
        """获取群聊上下文摘要"""
        messages = self._recent_messages.get(session_id, [])
        if not messages:
            return ""

        recent = messages[-5:]
        lines = []
        for m in recent:
            sender = m.get("sender", "?")[:8]
            content = m.get("content", "")[:50]
            lines.append(f"{sender}: {content}")

        return "[群聊近况]\n" + "\n".join(lines)
