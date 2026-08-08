# 茜特菈莉·好感度系统

<p align="center">
  <b>「哼，你怎么又来了？……带酒了吗？」</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/版本-4.0.0-e94560?style=flat-square" alt="版本">
  <img src="https://img.shields.io/badge/AstrBot-≥4.24.2-3b82f6?style=flat-square" alt="AstrBot">
  <img src="https://img.shields.io/badge/Python-3.10+-4ecca3?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/许可证-AGPL--3.0-f2e8e5?style=flat-square" alt="License">
</p>

<p align="center">
  原神「茜特菈莉（黑曜石奶奶）」完整 AI Agent 方案<br>
  好感度 · 日程系统 · 群聊增强 · 解锁内容 · 随机事件 · 每日日记 · 记忆关联 · 被遗忘提醒 · WebUI
</p>

---

## 这是什么？

一个 AstrBot 插件，让你的机器人变成茜特菈莉——那个活了两百多年、嘴硬心软、沉迷轻小说的黑曜石奶奶。

她会记住你说过的话，会因为你三天没来找她而好感度下降，会在深夜喝酒时比白天更容易说真心话，会在群里听到别人聊小说时忍不住插嘴。随着好感度提升，她会逐渐卸下伪装，解锁专属的故事和对话。

**推荐搭配插件**：
- [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory) — 长期记忆
- [enhance_mode](https://github.com/Axi404/astrbot_plugin_astrbot_enhance_mode) — 群聊主动回复

---

## 功能

### 💕 好感度系统

6 个关系阶段，阈值可在 WebUI 自由调整：

| 阶段 | 默认阈值 | 她的表现 |
|:---:|:---:|:---|
| 陌生人 | 0 | 威严冷淡，话里带刺 |
| 熟人 | 50 | 稍微放下架子 |
| 朋友 | 150 | 会主动聊轻小说 |
| 好友 | 400 | 暴露懒散和局促 |
| 知己 | 800 | 威严撑不过三句话 |
| 旅行者 | 1500 | 完全卸下伪装 |

好感度自动触发：聊小说+10~20、聊酒+8~15、叫"奶奶"+15~25、关心她+20~30、看穿她+25~35。每日签到+15~30。3天不来自动衰减。

### 🌙 日程时段系统

| 时段 | 时间 | 语态 |
|:---:|:---:|:---|
| 🌙 深夜 | 23-06 | 微醺、感性 |
| 🌅 早晨 | 06-11 | 起床气、迷糊 |
| ☀️ 中午 | 11-14 | 逐渐清晰 |
| 🌤️ 下午 | 14-18 | 最"正常" |
| 🌆 晚上 | 18-23 | 放松、微醺 |

所有时段的起止时间、活动、心情、语态都在 WebUI 可编辑。时区可配置。特殊日期有专属回复。

### 💬 群聊增强

React 模式：感知群聊上下文，好感度越高越容易回复，深夜更活跃。关键词触发（小说/酒/占卜/天气）。30秒冷却防刷屏。

### 🔓 解锁内容

每个阶段解锁专属对话和故事。新解锁时自动提示。

### 🎲 随机事件

10 种事件按时段触发：发现新书、好酒到手、睡过头了、看星星、做了个梦等。

### 📖 每日日记

旅行者专属。LLM 从第一人称视角生成 200-400 字日记，自动注入最近事件作为素材，PIL 渲染为图片发送。每天一次。

### 🔮 占卜

LLM 生成个性化占卜结果（萨满口吻）。每天限一次，LLM 不可用时回退到内置模板。

### 🔗 记忆关联

追踪用户间关系，让她能说"上次你和XX一起来的"。

### 💤 被遗忘提醒

久别归来时专属回复（仅私聊）：3-7天/7-30天/30天以上分级。

---

## 指令

| 指令 | 功能 |
|:---|:---|
| `/帮助` | 指令列表 |
| `/好感度` | 查看关系和进度 |
| `/签到` | 每日签到 |
| `/日程` | 查看当前时段 |
| `/排行` | 好感度排行榜 |
| `/叫我 <名>` | 设置昵称 |
| `/占卜` | 每日占卜（LLM生成，每天一次） |
| `/小说` | 推荐小说 |
| `/喝酒` | 陪她喝一杯（时段敏感） |
| `/解锁` | 查看已解锁内容 |
| `/日记` | 写/查看日记（旅行者专属） |
| `/事件` | 查看最近事件 |
| `/xt状态` | 系统状态 |

---

## 安装

### 1. 安装插件

复制到 `data/plugins/citlali_affinity/`，或 WebUI 上传 zip。

### 2. 配置插件

AstrBot WebUI → 插件 → 配置：`embedding_provider_id`（留空自动选择）

### 3. 设置人格

将 `persona/system_prompt.md` 粘贴到 AstrBot 人格设定。

### 4. 上传知识库

创建知识库，上传 `persona/knowledge_base/` 下的 13 个 .md 文件。

### 5. 安装中文字体

```bash
apt install fonts-noto-cjk
```

### 6. 重启 AstrBot

### 7. WebUI 设置

插件详情页 → Pages → dashboard，调整参数。

---

## WebUI

| 页面 | 功能 |
|------|------|
| 📊 总览 | 用户数、对话数、当前时段、旅行者数、关系分布 |
| 👥 用户 | 搜索、排行、详情弹窗、手动调整好感度 |
| 🌙 日程 | 编辑 5 个时段的时间/活动/心情/语态 |
| ⚙️ 设置 | 功能开关、阶段阈值、好感度参数、群聊参数、时区 |

---

## 文件结构

```
astrbot_plugin_citlali/
├── main.py                      主入口（13指令+2事件处理器）
├── core/
│   ├── affinity_manager.py      好感度
│   ├── context_builder.py       动态上下文
│   ├── time_schedule.py         日程系统
│   ├── settings_manager.py      设置管理
│   ├── group_chat.py            群聊增强
│   ├── unlock_manager.py        解锁内容
│   ├── event_manager.py         随机事件
│   ├── diary_manager.py         每日日记
│   ├── memory_association.py    记忆关联
│   └── forgotten_reminder.py    被遗忘提醒
├── pages/dashboard/index.html   WebUI
└── persona/
    ├── system_prompt.md         人格
    └── knowledge_base/ (13个)   知识库
```

---

## 更新日志

### v4.0.0
- 精简插件，移除内置记忆引擎和LLM轮询（推荐配合LivingMemory）
- 人格不再假设对方是旅行者
- 新增知识库 13_官方语音补录

### v3.6.0
- 日记加长（200-400字）+ 自动注入最近事件
- 占卜改用LLM生成 + 每日一次限制
- 上下文注入改用 system_prompt 直接修改
- 修复群聊 should_react 方法

### v3.5.0
- 时区可配置
- 修复 SQLite 多线程错误

### v3.4.0
- 解锁内容、随机事件、被遗忘提醒、每日日记、记忆关联

### v3.3.0
- 群聊增强（React模式）

---

## 致谢

- [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory)
- [astrbot_enhance_mode](https://github.com/Axi404/astrbot_plugin_astrbot_enhance_mode)
- [原神 WIKI](https://wiki.biligame.com/ys/)

---

<p align="center">
  <i>「漫长的时光让人麻木……但你这家伙，老是把人拽回现实。」</i>
</p>
