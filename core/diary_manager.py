"""
每日日记系统
只有旅行者阶段才能使用。日记以图片形式发送。
使用 LLM 生成日记内容，PIL 渲染为图片。
"""
import asyncio
import json
import logging
import os
import random
import textwrap
import time
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("citlali.diary")


class DiaryManager:
    """每日日记管理器"""

    def __init__(self, data_dir: str, ctx=None):
        self._path = os.path.join(data_dir, "diary_data.json")
        self._data: dict = {}
        self._ctx = ctx
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

    def can_write(self, user_id: str) -> bool:
        """检查今天是否已经写过日记"""
        today = datetime.now().strftime("%Y-%m-%d")
        user_data = self._data.get(user_id, {})
        return user_data.get("last_diary_date") != today

    async def write_diary(self, user_id: str, context: str = "", recent_events: list = None) -> Optional[str]:
        """
        生成今日日记。
        使用 AstrBot 默认 LLM，包含最近事件。
        """
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        hour = now.hour
        if 23 <= hour or hour < 6:
            time_of_day = "深夜"
        elif hour < 11:
            time_of_day = "早晨"
        elif hour < 14:
            time_of_day = "中午"
        elif hour < 18:
            time_of_day = "下午"
        else:
            time_of_day = "晚上"

        # 构建最近事件文本
        events_text = ""
        if recent_events:
            events_text = "\n最近发生的事：\n"
            for e in recent_events:
                events_text += f"- {e.get('title', '')}: {e.get('narrative', '')}\n"

        prompt_parts = [
            f"你是茜特菈莉，原神中的「黑曜石奶奶」，烟谜主的大萨满，活了两百多年的萨满兼轻小说宅女。",
            f"现在是{today}的{time_of_day}。请以你的视角写一篇日记（200-400字）。",
            f"要求：",
            f"- 第一人称，语气懒散、傲娇，偶尔感性",
            f"- 写今天做了什么、看了什么小说、喝了什么酒、想起了什么",
            f"- 偶尔提到「那个人」（旅行者），但不要说太直白",
            f"- 可以写一点内心独白，可以写维奇琳、欧洛伦",
            f"- 要有细节，比如窗外的风、酒的味道、书里的情节",
            f"- 用中文写，不要加标题",
        ]

        if events_text:
            prompt_parts.append(f"\n{events_text}")

        prompt = "\n".join(prompt_parts)

        # 使用 AstrBot 默认 LLM
        diary_text = None
        try:
            if self._ctx and hasattr(self._ctx, 'get_using_provider'):
                provider = self._ctx.get_using_provider()
                if provider:
                    pid = getattr(provider, 'provider_id', None) or getattr(provider, 'id', None)
                    if pid:
                        resp = await self._ctx.llm_generate(
                            chat_provider_id=pid,
                            prompt=prompt,
                            system_prompt="你是茜特菈莉。用第一人称写日记，语气懒散傲娇，要有细节和情感。",
                        )
                        diary_text = resp.completion_text if hasattr(resp, 'completion_text') else str(resp)
                        if diary_text:
                            diary_text = diary_text.strip()
        except Exception as e:
            logger.warning(f"[Citlali] 日记生成失败: {e}")

        # 失败时使用备用模板
        if not diary_text:
            diary_text = self._fallback_diary(time_of_day, events_text)

        if not diary_text:
            return None

        # 保存
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id]["last_diary_date"] = today
        self._data[user_id]["last_diary_text"] = diary_text
        self._data[user_id]["last_diary_time"] = time.time()
        if "diary_history" not in self._data[user_id]:
            self._data[user_id]["diary_history"] = []
        self._data[user_id]["diary_history"].append({
            "date": today,
            "text": diary_text,
            "time": time.time(),
        })
        # 保留最近 30 天
        self._data[user_id]["diary_history"] = \
            self._data[user_id]["diary_history"][-30:]
        self._save()

        return diary_text

    def get_today_diary(self, user_id: str) -> Optional[str]:
        """获取今天的日记（如果写过）"""
        today = datetime.now().strftime("%Y-%m-%d")
        user_data = self._data.get(user_id, {})
        if user_data.get("last_diary_date") == today:
            return user_data.get("last_diary_text")
        return None

    def get_diary_history(self, user_id: str, limit: int = 7) -> list[dict]:
        """获取日记历史"""
        user_data = self._data.get(user_id, {})
        history = user_data.get("diary_history", [])
        return list(reversed(history[-limit:]))

    def _fallback_diary(self, time_of_day: str, context: str = "") -> str:
        """LLM 不可用时的备用日记（更长、更丰富）"""
        import random

        # 基础模板
        templates = [
            f"{time_of_day}。窝在沙发上看小说，酒瓶又空了两本。窗外的风跟纳塔的不一样——但我说不上来哪里不同。算了，继续看书。偶尔会想，要是有人能陪我一起看就好了。不过那样的话，我就不能一边看一边吐槽作者了。",
            f"{time_of_day}。《蜃楼战记》又更新了，虽然换了个作者，但东之山君还是那个东之山君。有些东西变了，有些东西一直没变。就像我。两百年了，还是喜欢窝在家里看书喝酒。外面的世界变了好多，但我懒得去看。",
            f"{time_of_day}。翻到一本旧书，夹着一张很久以前的书签。不记得是谁送的了。……不，我记得。只是不想说。维奇琳以前总说我书太多，该扔掉一些。我没扔。有些东西扔了就真的没了。",
            f"{time_of_day}。天气不错，适合发呆。想出门走走，但走到门口又回来了。外面太吵了。还是家里好。欧洛伦那小子说要来看我，被我骂回去了。……其实他来了也好，至少有人说话。",
            f"{time_of_day}。深夜了，星星很亮。我坐在窗边喝酒，想起很多年前的事。那时候维奇琳还在，我们一起看过星星。她说星星是死人的眼睛。我说那我认识的死人也太多了。她笑了。我也笑了。",
            f"{time_of_day}。又做了一个梦。梦到自己在一个很远的地方，身边一个人都没有。醒来的时候枕头是湿的。……大概是酒洒了吧。对，一定是酒洒了。",
            f"{time_of_day}。八重堂的新书到了，我一口气看完了。结局不太好，女主最后一个人走了。我合上书，沉默了很久。有时候觉得，书里的角色比我活得明白。至少她们知道自己想要什么。",
        ]

        base = random.choice(templates)

        # 如果有最近事件，追加
        if context:
            base += f"\n\n{context}"

        return base


def render_diary_image(text: str, date: str = "") -> Optional[bytes]:
    """
    将日记文本渲染为图片。
    返回 PNG 图片的字节数据。
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        logger.warning("PIL 未安装，无法生成日记图片")
        return None

    if not date:
        date = datetime.now().strftime("%Y年%m月%d日")

    # 图片参数
    width = 600
    padding = 40
    line_height = 28
    font_size = 16

    # 尝试加载中文字体
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue

    if not font:
        font = ImageFont.load_default()

    # 计算文本行
    chars_per_line = (width - padding * 2) // (font_size + 2)
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=chars_per_line)
        lines.extend(wrapped if wrapped else [""])

    # 计算图片高度
    header_height = 80
    height = header_height + len(lines) * line_height + padding * 2

    # 创建图片（米色背景，模拟纸张）
    img = Image.new("RGB", (width, height), color=(253, 246, 227))
    draw = ImageDraw.Draw(img)

    # 标题
    title_font = font
    try:
        title_font = ImageFont.truetype(font.path, 20) if font.path else font
    except Exception:
        pass

    draw.text((padding, 20), "✦ 奶奶的日记 ✦", fill=(180, 50, 50), font=title_font)
    draw.text((padding, 50), date, fill=(120, 100, 80), font=font)

    # 分割线
    draw.line([(padding, header_height - 5), (width - padding, header_height - 5)],
              fill=(200, 180, 150), width=1)

    # 正文
    y = header_height + 10
    for line in lines:
        draw.text((padding, y), line, fill=(60, 50, 40), font=font)
        y += line_height

    # 装饰线
    draw.line([(padding, height - 30), (width - padding, height - 30)],
              fill=(200, 180, 150), width=1)
    draw.text((width - padding - 100, height - 25), "—— 茜特菈莉",
              fill=(150, 120, 90), font=font)

    # 导出为 PNG 字节
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    return buf.getvalue()
