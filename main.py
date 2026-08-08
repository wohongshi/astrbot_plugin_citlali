"""
茜特菈莉·好感度系统 AstrBot 插件
- 好感度系统
- 日程时段系统
- 群聊 React 模式
- 解锁内容、随机事件、日记、记忆关联、被遗忘提醒
- 记忆功能由 LivingMemory 插件提供
- 主动回复由 enhance_mode 插件提供
"""
import asyncio
import os
import random
import time
from datetime import datetime
from typing import Any

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, StarTools, register
from astrbot.api import logger

from .core.affinity_manager import AffinityManager, AffinityStage, STAGE_NAMES
from .core.context_builder import ContextBuilder
from .core.group_chat import GroupChatManager
from .core.unlock_manager import UnlockManager
from .core.event_manager import EventManager
from .core.diary_manager import DiaryManager, render_diary_image
from .core.memory_association import MemoryAssociation
from .core.forgotten_reminder import ForgottenReminder
from .core.time_schedule import (
    get_current_window, get_window_name, get_time_context,
    get_special_date_context, CITLALI_SCHEDULE,
)


@register(
    "citlali_affinity",
    "CitlaliDev",
    "茜特菈莉好感度系统 - 日程+群聊+解锁+事件+日记",
    "4.0.0",
    "https://github.com/wohongshi/astrbot_plugin_citlali",
)
class CitlaliAffinityPlugin(Star):

    def __init__(self, context: Context, config: dict[str, Any] = None):
        super().__init__(context)
        self.ctx = context
        self.config = config or {}

        self.data_dir = str(StarTools.get_data_dir("citlali_affinity"))

        # 设置管理器
        from .core.settings_manager import SettingsManager
        self.settings = SettingsManager(self.data_dir)

        # 核心组件
        self.affinity_mgr = AffinityManager(self.data_dir)
        self.context_builder = ContextBuilder(self.affinity_mgr)
        self.group_chat = GroupChatManager(self)
        self.unlock_mgr = UnlockManager(self.data_dir)
        self.event_mgr = EventManager(self.data_dir)
        self.diary_mgr = DiaryManager(self.data_dir, context)
        self.association = MemoryAssociation(self.data_dir)
        self.forgotten = ForgottenReminder(self.data_dir)

        self._last_decay = 0

        # 日程系统配置路径
        from .core.time_schedule import set_config_path
        set_config_path(self.data_dir)

        # 应用阶段阈值
        from .core.affinity_manager import set_stage_thresholds
        thresholds = self.settings.get("stage_thresholds", [0, 50, 150, 400, 800, 1500])
        set_stage_thresholds(thresholds)

        # 注册 WebUI
        self._register_pages()

        logger.info("[Citlali] 茜特菈莉好感度系统已加载")

    def _register_pages(self):
        if not hasattr(self.ctx, "register_web_api"):
            return
        try:
            from .pages.pages_api import register_pages
            register_pages(self)
            logger.info("[Citlali] WebUI Pages 已注册")
        except Exception as e:
            logger.warning(f"[Citlali] WebUI 注册失败: {e}", exc_info=True)

    # ==================== 指令 ====================

    @filter.command("帮助")
    async def cmd_help(self, event: AstrMessageEvent):
        yield event.plain_result(
            "✦ 茜特菈莉·指令列表 ✦\n"
            "━━━━━━━━━━━━━━\n"
            "  /好感度    查看你和奶奶的关系\n"
            "  /签到      每日签到增加好感\n"
            "  /日程      查看奶奶当前在干嘛\n"
            "  /排行      好感度排行榜\n"
            "  /叫我 <名>  让奶奶记住你的名字\n"
            "  /占卜      让奶奶给你占卜\n"
            "  /小说      让奶奶推荐小说\n"
            "  /喝酒      陪奶奶喝一杯\n"
            "  /解锁      查看已解锁内容\n"
            "  /日记      查看奶奶的日记（旅行者专属）\n"
            "  /事件      查看最近发生的事件\n"
            "  /xt状态    系统运行状态\n"
            "━━━━━━━━━━━━━━"
        )

    @filter.command("好感度")
    async def cmd_affinity(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        user = self.affinity_mgr.get_user(user_id)
        stage = AffinityStage(user.get("stage", 0))
        affinity = user.get("affinity", 0)
        stage_name = STAGE_NAMES[stage]
        total = user.get("total_messages", 0)
        nickname = user.get("nickname", "")

        from .core.affinity_manager import STAGE_THRESHOLDS
        stages = sorted(AffinityStage)
        idx = stages.index(stage)
        if idx < len(stages) - 1:
            next_t = STAGE_THRESHOLDS[stages[idx + 1]]
            curr_t = STAGE_THRESHOLDS[stage]
            prog = (affinity - curr_t) / (next_t - curr_t) * 100
            bar = self._bar(prog)
            prog_text = f"{bar} {prog:.0f}%"
        else:
            prog_text = "已满 ❤"

        resp = {
            AffinityStage.STRANGER: "哼，找我什么事？奶奶我很忙的。",
            AffinityStage.ACQUAINTANCE: "哦，是你啊。有什么事？",
            AffinityStage.FRIEND: "来了？坐吧。要不要喝一杯？",
            AffinityStage.CLOSE_FRIEND: "你来了啊。（放下书，嘴角翘了一下）今天想聊什么？",
            AffinityStage.CONFIDANT: "……你来了。（声音变柔）我刚好看到一个有意思的段落。",
            AffinityStage.TRAVELER: "哼，你怎么又来了？（放下书，眼睛在发光）……带酒了吗？",
        }

        name_text = f"  昵称: {nickname}\n" if nickname else ""
        yield event.plain_result(
            f"✦ 茜特菈莉·好感度 ✦\n━━━━━━━━━━━━━━\n"
            f"  关系: {stage_name}\n{name_text}"
            f"  好感: {affinity}\n"
            f"  进度: {prog_text}\n  对话: {total} 次\n"
            f"━━━━━━━━━━━━━━\n{resp.get(stage, '')}"
        )

    @filter.command("签到")
    async def cmd_checkin(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        user = self.affinity_mgr.get_user(user_id)
        now = time.time()
        last = user.get("last_checkin", 0)

        if now - last < 86400:
            remaining = int((86400 - (now - last)) / 3600)
            yield event.plain_result(f"（瞥了你一眼）你今天已经来过了。{remaining}小时后再来。")
            return

        bonus = random.randint(15, 30)
        user["last_checkin"] = now
        delta, upgraded = self.affinity_mgr.add_affinity(user_id, "daily_chat", amount=bonus)

        stage = self.affinity_mgr.get_stage(user_id)
        resp = {
            AffinityStage.STRANGER: "哼……算你勤快。",
            AffinityStage.ACQUAINTANCE: "哦，又来了？坐吧。",
            AffinityStage.FRIEND: "来了？今天奶奶我心情不错。",
            AffinityStage.CLOSE_FRIEND: "你来了啊。（嘴角翘了一下）",
            AffinityStage.CONFIDANT: "……你来了。我等你半天了。",
            AffinityStage.TRAVELER: "哼，你怎么才来？坐，陪我喝。",
        }

        upgrade_text = "\n关系提升了！" if upgraded else ""
        yield event.plain_result(resp.get(stage, '……嗯。'))
        yield event.plain_result(f"好感度 +{delta}（当前: {self.affinity_mgr.get_user(user_id)['affinity']}）{upgrade_text}")

    @filter.command("日程")
    async def cmd_schedule(self, event: AstrMessageEvent):
        window = get_current_window()
        window_name = get_window_name(window)
        schedule = CITLALI_SCHEDULE.get(window, {})
        now = datetime.now()
        yield event.plain_result(
            f"✦ 茜特菈莉·日程 ✦\n━━━━━━━━━━━━━━\n"
            f"  时间: {now.strftime('%H:%M')}\n"
            f"  时段: {window_name}\n"
            f"  活动: {schedule.get('activity', '-')}\n"
            f"  心情: {schedule.get('mood', '-')}\n"
            f"  位置: {schedule.get('location', '-')}\n"
            f"━━━━━━━━━━━━━━"
        )

    @filter.command("排行")
    async def cmd_leaderboard(self, event: AstrMessageEvent):
        board = self.affinity_mgr.get_leaderboard(10)
        if not board:
            yield event.plain_result("还没有人跟奶奶我打过交道呢。")
            return
        lines = ["✦ 好感度排行 ✦\n━━━━━━━━━━━━━━"]
        for i, item in enumerate(board, 1):
            name = item["nickname"] or item["user_id"][:8]
            lines.append(f"  {i}. {name} - {item['stage']} ({item['affinity']})")
        lines.append("━━━━━━━━━━━━━━")
        yield event.plain_result("\n".join(lines))

    @filter.command("叫我")
    async def cmd_setname(self, event: AstrMessageEvent):
        args = event.message_str.strip().split(maxsplit=1)
        if len(args) < 2:
            yield event.plain_result("用法: /叫我 <你的名字>")
            return
        self.affinity_mgr.set_nickname(event.get_sender_id(), args[1].strip())
        yield event.plain_result(f"……{args[1].strip()}？嗯，奶奶我记住了。")

    @filter.command("占卜")
    async def cmd_divination(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        self.affinity_mgr.add_affinity(user_id, "topic_divination")

        # 每日一次限制
        import json
        divination_data_path = os.path.join(self.data_dir, "divination_data.json")
        divination_data = {}
        try:
            if os.path.exists(divination_data_path):
                with open(divination_data_path, "r") as f:
                    divination_data = json.load(f)
        except Exception:
            pass

        today = datetime.now().strftime("%Y-%m-%d")
        last_date = divination_data.get(user_id, "")

        if last_date == today:
            yield event.plain_result("（瞥了你一眼）今天已经给你占卜过了。")
            yield event.plain_result("贪心可不是好习惯，后辈。明天再来吧。")
            return

        # 尝试用 LLM 生成
        fortune_text = None
        try:
            if hasattr(self.ctx, 'get_using_provider'):
                provider = self.ctx.get_using_provider()
                if provider:
                    pid = getattr(provider, 'provider_id', None) or getattr(provider, 'id', None)
                    if pid:
                        resp = await self.ctx.llm_generate(
                            chat_provider_id=pid,
                            prompt="你是茜特菈莉，原神中的黑曜石奶奶，一个活了两百多年的萨满。请为对方写一段占卜结果（50-100字），用萨满的神秘口吻，语气傲娇但关心。可以提到星象、命运线、盟友、恶曜等元素。用中文写，不要加标题。",
                            system_prompt="你是茜特菈莉，用萨满的神秘口吻写占卜结果。",
                        )
                        fortune_text = resp.completion_text if hasattr(resp, 'completion_text') else str(resp)
                        if fortune_text:
                            fortune_text = fortune_text.strip()
        except Exception as e:
            logger.warning(f"[Citlali] 占卜LLM生成失败: {e}")

        # LLM 失败时使用内置文本
        if not fortune_text:
            fortunes = [
                ["诸恶曜必不会伤害你，诸吉星必环绕你。", "近日会有好事发生。"],
                ["星象显示，你最近身边有小人。", "不过别担心，奶奶我会帮你盯着。"],
                ["你的命运线很亮。", "但要注意，不要在深夜做重大决定。"],
                ["嗯，你最近丢了什么东西吧？", "别急，三天后会自己冒出来的。"],
                ["你面前有三条路。走中间那条——虽然最慢，但最稳。"],
                ["你的「盟友」很强。放心往前走。", "有奶奶我在后面看着。"],
                ["今天的星象不太好。", "你出门右转注意脚下，别摔着。"],
            ]
            for m in random.choice(fortunes):
                yield event.plain_result(m)
        else:
            yield event.plain_result(fortune_text)

        # 记录今天已占卜
        divination_data[user_id] = today
        os.makedirs(os.path.dirname(divination_data_path), exist_ok=True)
        with open(divination_data_path, "w") as f:
            json.dump(divination_data, f)

    @filter.command("小说")
    async def cmd_novel(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        self.affinity_mgr.add_affinity(user_id, "topic_novel")
        recs = [
            ["哦，你感兴趣啊？", "《蜃楼战记》是稻妻八重堂的活化石级老系列。篇幅超长，换过三次作者，最终也没揭开真相。", "你一定要看！"],
            ["这本《奥西兹小姐事件簿》！枫丹风格的推理小说，神里绫华也是忠实读者。", "我有番外篇，要看吗？"],
            ["《再这样下去要成为败犬女主了！》八重堂今年最热销的！", "我读到高潮时直接喊出来了。"],
            ["《转生成为雷电将军，然后天下无敌》和《拜托了我的狐仙宫司》——绝版珍藏。", "我两本都要，一本都不能少。"],
            ["《沉秋拾剑录》……书是好书。", "但签售会不来纳塔——这事儿我记一辈子。"],
        ]
        for m in random.choice(recs):
            yield event.plain_result(m)

    @filter.command("喝酒")
    async def cmd_drink(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        window = get_current_window()
        self.affinity_mgr.add_affinity(user_id, "topic_wine")

        if window == "morning":
            yield event.plain_result("大早上就喝酒？！")
            yield event.plain_result("虽然奶奶我昨晚的酒还没醒，但也不至于这么早吧。")
        elif window == "noon":
            yield event.plain_result("中午好。其实我还是很节制的，起床到中午不会喝酒。")
            yield event.plain_result("至于熬夜就是另一码事了……你要来点吗？")
        else:
            drinks = [
                ["来，陪奶奶我喝一杯。璃月的酒，不错。", "岁月献给小酒杯——嗝。"],
                ["你知道吗……这瓶酒我存了好久了。", "今天心情不错，开了吧。"],
                ["还剩半瓶。你要来点吗？", "别告诉别人奶奶我喝这么多。"],
                ["嗝……你别看我这样，奶奶我酒量很好的。", "……大概。"],
                ["坐。今晚的月色不错。", "适合喝酒。"],
            ]
            for m in random.choice(drinks):
                yield event.plain_result(m)

    @filter.command("解锁")
    async def cmd_unlock(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        stage = self.affinity_mgr.get_stage(user_id)
        new_items = self.unlock_mgr.get_new_unlocks(user_id, stage)

        if new_items:
            for item in new_items:
                content = item.get("content", "")
                if isinstance(content, list):
                    yield event.plain_result(f"🔓 新解锁：{item['title']}")
                    for line in content:
                        yield event.plain_result(line)
                else:
                    yield event.plain_result(f"🔓 新解锁：{item['title']}")
                    yield event.plain_result(content)
        else:
            all_items = self.unlock_mgr.get_all_unlocks(user_id, stage)
            if all_items:
                yield event.plain_result(f"当前阶段已解锁 {len(all_items)} 项内容。没有新的。")
            else:
                yield event.plain_result("还没有解锁任何内容。多来找奶奶我聊聊。")

    @filter.command("日记")
    async def cmd_diary(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        stage = self.affinity_mgr.get_stage(user_id)

        if stage < AffinityStage.TRAVELER:
            yield event.plain_result("……你想看奶奶我的日记？")
            yield event.plain_result("还早呢。等你跟奶奶我再熟一点再说。")
            return

        today_diary = self.diary_mgr.get_today_diary(user_id)
        if today_diary:
            img_path = self._save_diary_image(today_diary)
            if img_path:
                yield event.image_result(img_path)
            else:
                yield event.plain_result(today_diary)
            return

        yield event.plain_result("……你要看我的日记？")
        yield event.plain_result("好吧。等我写一下。")

        # 获取最近事件作为日记素材
        recent_events = self.event_mgr.get_recent_events(user_id, 3)
        diary_text = await self.diary_mgr.write_diary(user_id, recent_events=recent_events)
        if diary_text:
            img_path = self._save_diary_image(diary_text)
            if img_path:
                yield event.image_result(img_path)
            else:
                yield event.plain_result(diary_text)
        else:
            yield event.plain_result("……今天没什么好写的。")

    @filter.command("事件")
    async def cmd_events(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        events = self.event_mgr.get_recent_events(user_id, 5)
        if not events:
            yield event.plain_result("最近没什么特别的事发生。")
            return
        yield event.plain_result("✦ 最近的事 ✦")
        for e in events:
            ts = e.get("time", 0)
            date = time.strftime("%m-%d", time.localtime(ts)) if ts else "-"
            yield event.plain_result(f"[{date}] {e['title']}：{e['narrative']}")

    @filter.command("xt状态")
    async def cmd_status(self, event: AstrMessageEvent):
        stats = self.affinity_mgr.get_stats()
        window = get_current_window()
        window_name = get_window_name(window)
        schedule = CITLALI_SCHEDULE.get(window, {})
        lines = [
            "✦ 茜特菈莉·系统状态 ✦", "━━━━━━━━━━━━━━",
            f"  好感度系统: ✓",
            f"  当前时段:   {window_name} ({schedule.get('activity', '-')})",
            f"  总用户:     {stats['total_users']}",
            f"  总对话:     {stats['total_messages']}",
            "━━━━━━━━━━━━━━", "  关系分布:",
        ]
        for sn, cnt in stats["stage_counts"].items():
            if cnt > 0:
                lines.append(f"    {sn}: {cnt}")
        yield event.plain_result("\n".join(lines))

    # ==================== 群聊事件 ====================

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        message = event.message_str
        sender_id = event.get_sender_id()
        session_id = event.unified_msg_origin

        if not message or not message.strip():
            return

        # React 模式
        should_reply, preset_reply = await self.group_chat.should_react(event, message, sender_id)
        if should_reply and preset_reply:
            yield event.plain_result(preset_reply)

    # ==================== LLM 钩子 ====================

    @filter.on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        if not self.settings.get("inject_context"):
            return

        user_id = event.get_sender_id()
        message = event.message_str
        session_id = event.unified_msg_origin

        # 每日衰减
        if self.settings.get("decay_enabled"):
            now = time.time()
            if now - self._last_decay > 3600:
                self.affinity_mgr.decay_daily()
                self._last_decay = now

        # 好感度触发
        if self.settings.get("affinity_enabled"):
            triggers = self.context_builder.detect_affinity_trigger(message)
            upgraded = False
            new_stage = None
            old_stage = self.affinity_mgr.get_stage(user_id)

            for trigger in triggers:
                _, up = self.affinity_mgr.add_affinity(user_id, trigger)
                if up:
                    upgraded = True
                    new_stage = self.affinity_mgr.get_stage(user_id)

            if upgraded and self.settings.get("upgrade_notify") and new_stage:
                msg = self.context_builder.build_upgrade_message(old_stage, new_stage)
                self._inject_context(req, f"[关系升级:{STAGE_NAMES[new_stage]}] {msg}")

        # 被遗忘提醒（仅私聊）
        is_group = hasattr(event, 'get_message_type') and str(getattr(event, 'get_message_type', lambda: '')()).lower().find('group') >= 0
        if not is_group:
            forgotten_msg = self.forgotten.check_forgotten(user_id)
            if forgotten_msg:
                self._inject_context(req, f"[用户久别归来] {forgotten_msg}")

        # 随机事件
        if random.random() < 0.08:
            window = get_current_window()
            event_result = self.event_mgr.check_event(user_id, window)
            if event_result:
                dialogue = event_result.get("dialogue", [])
                if dialogue:
                    self._inject_context(req,
                        f"[随机事件:{event_result['title']}] {event_result['narrative']}。回应示例: {' '.join(dialogue)}")
                bonus = event_result.get("affinity_bonus", 0)
                if bonus > 0 and self.settings.get("affinity_enabled"):
                    self.affinity_mgr.add_affinity(user_id, "daily_chat", amount=bonus)

        # 构建上下文
        ctx = self.context_builder.build_context(user_id)

        # 时段上下文
        time_ctx = get_time_context()
        if time_ctx:
            ctx = time_ctx + "\n" + ctx

        # 特殊日期
        special = get_special_date_context()
        if special:
            ctx = special + "\n" + ctx

        # 群聊上下文
        group_ctx = self.group_chat.get_group_context(session_id)
        if group_ctx:
            ctx = group_ctx + "\n" + ctx

        # 记忆关联
        assoc_ctx = self.association.get_context_for_user(user_id)
        if assoc_ctx:
            ctx = assoc_ctx + "\n" + ctx

        self._inject_context(req, ctx)

    def _inject_context(self, req, content: str):
        """注入上下文到 system_prompt"""
        if hasattr(req, 'system_prompt') and req.system_prompt:
            req.system_prompt = content + "\n\n" + req.system_prompt
        elif hasattr(req, 'contexts'):
            req.contexts.append({"role": "system", "content": content})

    def _save_diary_image(self, text: str) -> str | None:
        """将日记渲染为图片并保存"""
        import os
        img_data = render_diary_image(text)
        if not img_data:
            return None
        img_path = os.path.join(self.data_dir, "diary_temp.png")
        try:
            with open(img_path, "wb") as f:
                f.write(img_data)
            return img_path
        except Exception as e:
            logger.warning(f"[Citlali] 保存日记图片失败: {e}")
            return None

    def _bar(self, pct: float, len: int = 10) -> str:
        f = int(pct / 100 * len)
        return "█" * f + "░" * (len - f)
