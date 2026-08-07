# 茜特菈莉·好感度系统

<p align="center">
  <b>「哼，你怎么又来了？……带酒了吗？」</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/版本-3.6.0-e94560?style=flat-square" alt="版本">
  <img src="https://img.shields.io/badge/AstrBot-≥4.24.2-3b82f6?style=flat-square" alt="AstrBot">
  <img src="https://img.shields.io/badge/Python-3.10+-4ecca3?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/许可证-AGPL--3.0-f2e8e5?style=flat-square" alt="License">
</p>

<p align="center">
  原神「茜特菈莉（黑曜石奶奶）」完整 AI Agent 方案<br>
  好感度 · 记忆引擎 · 日程系统 · 群聊增强 · 解锁内容 · 随机事件 · 每日日记 · WebUI<br>
  一个插件，零外部依赖，开箱即用
</p>

---

## 目录

- [这是什么](#这是什么)
- [功能总览](#功能总览)
- [安装部署](#安装部署)
- [配置说明](#配置说明)
- [指令列表](#指令列表)
- [WebUI 使用](#webui-使用)
- [文件结构](#文件结构)
- [更新日志](#更新日志)

---

## 这是什么？

一个 AstrBot 插件，让你的机器人变成茜特菈莉——那个活了两百多年、嘴硬心软、沉迷轻小说的黑曜石奶奶。

她会记住你说过的话，会因为你三天没来找她而好感度下降，会在深夜喝酒时比白天更容易说真心话，会在群里听到别人聊小说时忍不住插嘴。随着好感度提升，她会逐渐卸下伪装，解锁专属的故事和对话。

**零外部依赖**——记忆引擎、好感度、日程系统全部自包含，不需要安装其他记忆插件。

---

## 功能总览

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

**自动触发**：聊小说+10~20、聊酒+8~15、叫"奶奶"+15~25、关心她+20~30、看穿她+25~35

**每日衰减**：3天不来自动降好感

**签到系统**：`/签到` 每日一次，+15~30 好感

### 🧠 记忆引擎

自包含长期记忆系统，基于 LivingMemory 实现模式：

- **aiosqlite** 异步存储（无线程问题）
- **Embedding 向量检索** — 调用 AstrBot Embedding Provider
- **BM25 文本检索** — 中文 bigram 分词 + TF-IDF
- **混合检索** — BM25 + 向量 RRF 融合排序
- **自动对话总结** — 每 N 轮调用 LLM 总结为结构化记忆
- **图谱系统** — 自动抽取实体和关系，Canvas 可视化
- **时间衰减 + 访问强化** — 旧记忆降权，常被提及的保留

### 🌙 日程时段系统

| 时段 | 时间 | 语态 |
|:---:|:---:|:---|
| 🌙 深夜 | 23-06 | 微醺、感性、容易说真心话 |
| 🌅 早晨 | 06-11 | 起床气、迷糊、不耐烦 |
| ☀️ 中午 | 11-14 | 逐渐清晰 |
| 🌤️ 下午 | 14-18 | 最"正常"的状态 |
| 🌆 晚上 | 18-23 | 放松、微醺、话变多 |

时区可在 WebUI 配置（默认 UTC+8 北京时间）。所有时段的起止时间、活动、心情、语态都可在 WebUI 编辑。

特殊日期（新年/情人节/万圣节/圣诞节）有专属回复。

### 💬 群聊增强

内置 React 模式和主动回复，与好感度/日程/记忆深度联动：

- **React 模式**：感知群聊上下文，好感度越高越容易回复
- **主动回复**：不被@也可能说话，群聊冷场时自言自语
- **关键词触发**：小说/酒/占卜/天气自动触发预设回复
- **防刷屏**：冷却机制，默认概率较低
- **独立 Provider**：主动回复可配置独立模型，回退到默认

### 🔓 解锁内容

每个阶段解锁专属对话和故事（熟人2项、朋友3项、好友4项、知己4项、旅行者5项）。新解锁时自动提示。

### 🎲 随机事件

10 种事件按时段触发：发现新书、好酒到手、睡过头了、找书、下雨天、尝试做饭、看星星、做了个梦、欧洛伦来访、翻到旧信。

### 📖 每日日记

旅行者专属。LLM 从第一人称视角生成日记，PIL 渲染为米色纸张风格图片发送。每天可写一次，保留30天历史。LLM 不可用时自动使用备用模板。

### 🔗 记忆关联

追踪用户间关系，让她能说"上次你和XX一起来的"。

### 💤 被遗忘提醒

用户久别归来时触发专属回复（仅私聊）：3-7天/7-30天/30天以上分级。

### 🔄 LLM 轮询器

多 Provider 轮换，限额自动切换冷却，失败重试。用于记忆总结等后台任务。

---

## 安装部署

### 前置要求

- AstrBot ≥ 4.24.2
- Python 3.10+
- 一个 Embedding Provider（推荐硅基流动 BAAI/bge-m3，免费）
- 一个 LLM Provider（用于记忆总结，可选）
- 中文字体（用于日记图片渲染）

### 方式一：WebUI 上传（推荐）

1. 下载本仓库的 `citlali_affinity_plugin.zip`
2. 打开 AstrBot WebUI → **插件** → 右下角 **+** 按钮
3. 选择 **上传 zip**，上传下载的文件
4. 等待安装完成，重启 AstrBot

### 方式二：手动安装

```bash
# 进入 AstrBot 数据目录
cd /path/to/astrbot/data/plugins

# 克隆仓库
git clone https://github.com/wohongshi/astrbot_plugin_citlali.git

# 或者复制已下载的文件夹
cp -r /path/to/astrbot_plugin_citlali/ ./citlali_affinity/

# 重启 AstrBot
```

### 方式三：Docker 环境

```bash
# 将插件挂载到容器内
docker run -v /path/to/astrbot_plugin_citlali:/data/plugins/citlali_affinity ...
```

### 安装后配置

#### 1. 配置 Embedding Provider

AstrBot WebUI → **服务提供商** → **新增** → **Embedding**：

推荐：[硅基流动](https://cloud.siliconflow.cn/) BAAI/bge-m3（免费）
- API Base: `https://api.siliconflow.cn/v1`
- 模型: `BAAI/bge-m3`

#### 2. 配置插件

AstrBot WebUI → **插件** → **citlali_affinity** → **配置**：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `embedding_provider_id` | Embedding Provider ID | 留空自动选择 |
| `llm_provider_id` | LLM Provider ID（记忆总结用） | `zhipu/glm-4.7-flash` |

#### 3. 设置人格

将 `persona/system_prompt.md` 的内容粘贴到 AstrBot WebUI → **人格设定** 中。

#### 4. 上传知识库（推荐）

AstrBot WebUI → **知识库** → **创建知识库**：
- 名称：茜特菈莉世界观
- Embedding 模型：选择刚才配置的
- 上传 `persona/knowledge_base/` 下的 12 个 .md 文件

#### 5. 安装中文字体（日记图片需要）

```bash
# Debian/Ubuntu
apt install fonts-noto-cjk

# Alpine
apk add font-noto-cjk

# 检查是否安装成功
fc-list :lang=zh | head -5
```

#### 6. 重启 AstrBot

```bash
# Docker
docker restart astrbot

# 直接运行
systemctl restart astrbot
# 或
python main.py
```

#### 7. 验证安装

发送 `/xt状态`，确认：
- 好感度系统: ✓
- 记忆引擎: ✓
- 上下文注入: ✓

#### 8. WebUI 设置

插件详情页 → **Pages** → **dashboard**，调整各项参数。

---

## 配置说明

### AstrBot 插件配置（只需2项）

| 配置项 | 说明 |
|--------|------|
| `embedding_provider_id` | Embedding Provider ID，留空自动选择 |
| `llm_provider_id` | LLM Provider ID，记忆总结用，留空自动选择 |

### WebUI 设置（28项，全部可视化配置）

| 分类 | 参数 |
|------|------|
| 功能开关 | 好感度、记忆引擎、上下文注入、每日衰减、升级通知、日程系统、特殊日期、群聊React、主动回复 |
| 阶段阈值 | 6个阶段所需好感度（自由调整） |
| 好感度参数 | 对话/签到/衰减的数值范围、签到冷却时间 |
| 记忆参数 | 自动总结轮次、召回条数 |
| LLM轮询 | 重试等待、最大失败、冷却时间 |
| 群聊参数 | React冷却、主动回复概率、主动回复冷却、主动回复独立Provider |
| 时区 | UTC偏移量（默认+8） |

### 模型使用策略

| 功能 | 使用的模型 |
|------|-----------|
| 正常聊天 | AstrBot 默认模型 |
| 好感度/指令 | AstrBot 默认模型 |
| 日记生成 | AstrBot 默认模型 |
| 记忆总结 | `llm_provider_id`（可配置） |
| 群聊主动回复 | `active_reply_provider_id`（可独立配置） |

---

## 指令列表

17 个中文指令：

| 指令 | 功能 | 好感度 |
|:---|:---|:---:|
| `/帮助` | 指令列表 | - |
| `/好感度` | 查看关系和进度 | - |
| `/签到` | 每日签到 | +15~30 |
| `/日程` | 查看当前时段 | - |
| `/回忆 <词>` | 从记忆检索 | - |
| `/记住 <话>` | 写入长期记忆 | +20 |
| `/排行` | 好感度排行榜 | - |
| `/叫我 <名>` | 设置昵称 | - |
| `/占卜` | 随机占卜结果 | +10~18 |
| `/小说` | 推荐小说 | +10~20 |
| `/喝酒` | 陪她喝一杯（时段敏感） | +8~15 |
| `/解锁` | 查看已解锁内容 | - |
| `/日记` | 写/查看日记（旅行者专属） | - |
| `/事件` | 查看最近事件 | - |
| `/记忆总结` | 手动触发记忆总结 | - |
| `/记忆 子命令` | 记忆管理 | - |
| `/xt状态` | 系统状态（含对话缓冲进度） | - |

---

## WebUI 使用

通过 AstrBot 插件 Pages 系统访问：

**AstrBot WebUI → 插件 → citlali_affinity → Pages → dashboard**

### 页面说明

| 页面 | 功能 |
|------|------|
| 📊 总览 | 用户数、记忆数、图谱节点、当前时段、LLM状态、对话缓冲进度 |
| 👥 用户 | 搜索、排行、详情弹窗、手动调整好感度、里程碑查看 |
| 🧠 记忆 | 关键词搜索记忆、最近记忆列表 |
| 🕸️ 图谱 | Canvas 力导向可视化，节点着色，关系标签 |
| 🌙 日程 | 编辑 5 个时段的起止时间、活动、心情、语态 |
| ⚙️ 设置 | 功能开关、阶段阈值、好感度参数、记忆参数、群聊参数、时区 |
| 🔄 LLM | 轮询状态、测试连接 |

---

## 文件结构

```
astrbot_plugin_citlali/
├── metadata.yaml                    插件元数据
├── _conf_schema.json                AstrBot 配置 Schema
├── main.py                          主入口（17指令+3事件处理器）
├── requirements.txt                 依赖（aiohttp, numpy, Pillow, aiosqlite）
├── README.md                        本文件
│
├── core/                            核心模块
│   ├── affinity_manager.py          好感度（6阶段+衰减+签到+动态阈值）
│   ├── context_builder.py           动态上下文构建
│   ├── memory_engine.py             记忆引擎（aiosqlite+Embedding+BM25+向量RRF）
│   ├── time_schedule.py             日程系统（5时段+特殊日期+时区+可编辑）
│   ├── llm_rotator.py               LLM轮询器（多Provider+限额重试）
│   ├── settings_manager.py          设置管理（28项WebUI可配置）
│   ├── group_chat.py                群聊增强（React+主动回复+独立Provider）
│   ├── unlock_manager.py            解锁内容（6阶段专属对话/故事）
│   ├── event_manager.py             随机事件（10种按时段触发）
│   ├── diary_manager.py             每日日记（LLM生成+PIL图片渲染）
│   ├── memory_association.py        记忆关联（用户间关系追踪）
│   └── forgotten_reminder.py        被遗忘提醒（3级时间触发）
│
├── pages/                           WebUI
│   └── dashboard/
│       └── index.html               完整管理面板（7页）
│
└── persona/                         角色资源
    ├── system_prompt.md             核心人格设定
    └── knowledge_base/              知识库（12个文件）
        ├── 01_人生经历.md
        ├── 02_千灵节灌酒事件.md
        ├── 03_对旅行者的真实想法.md
        ├── 04_轻小说藏书.md
        ├── 05_提瓦特各地见闻.md
        ├── 06_节日与庆典.md
        ├── 07_内心独白与自我认知.md
        ├── 08_萨满能力体系.md
        ├── 09_生活细节与日常习惯.md
        ├── 10_完整台词库.md
        ├── 11_传说任务剧情.md
        └── 12_角色语音补充.md
```

---

## 更新日志

### v3.6.0
- 记忆引擎基于 LivingMemory 模式重写（aiosqlite + AstrBot Provider API）
- Provider 发现机制统一（get_all_embedding_providers / get_using_provider）
- 日记系统改用 AstrBot 默认模型
- 群聊增强支持独立 Provider 配置
- 新增 `/记忆总结` 手动触发指令
- `/xt状态` 显示对话缓冲进度
- 上下文注入改用 system_prompt 直接修改
- 修复 SQLite 多线程错误
- 修复 Provider 未定义错误

### v3.5.0
- 人格不再假设对方是旅行者
- LLM Provider 放回 AstrBot 插件配置
- WebUI 测试连接功能
- 时区可配置

### v3.4.0
- 好感度解锁内容、随机事件、被遗忘提醒、每日日记、记忆关联
- 阶段阈值 WebUI 可调

### v3.3.0
- 群聊增强（React 模式 + 主动回复）

### v3.2.0
- 设置管理页面、LLM 轮询器

### v3.1.0
- WebUI 日程编辑、分条回复风格

### v3.0.0
- 自包含记忆引擎、日程时段系统、WebUI 管理面板

---

## 致谢

- [AstrBot](https://github.com/AstrBotDevs/AstrBot) — 机器人框架
- [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory) — 记忆系统实现参考
- [astrbot_enhance_mode](https://github.com/Axi404/astrbot_plugin_astrbot_enhance_mode) — 群聊增强设计参考
- [原神 WIKI](https://wiki.biligame.com/ys/) — 角色资料

---

<p align="center">
  <i>「漫长的时光让人麻木……但你这家伙，老是把人拽回现实。」</i>
</p>
