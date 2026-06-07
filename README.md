# 剧 本 工 坊 · AI 小说转剧本

> **AI · 小 · 说 · 转 · 剧 · 本 · 工 · 具**
> 将任意长篇网络小说自动转换为好莱坞标准的结构化剧本（YAML 格式），支持超长文本（2000+ 章）。

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![Gradio](https://img.shields.io/badge/gradio-6.x-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## ✨ 核心亮点

| 能力 | 说明 |
|------|------|
| 📚 **书架扫描** | 一键扫描本地小说文件夹，支持 .txt 巨文件（22MB/2335 章实测 < 0.5s） |
| 🎯 **精准章节定位** | 自动识别「第 N 章/回/节」「Chapter N」等 7+ 种格式 |
| 🧠 **AI Map-Reduce** | 逐章提取角色/场景/对话/动作 → 合并 Story Bible → 生成结构化剧本 |
| ✅ **Schema 校验** | JSON Schema 保证输出可被下游工具直接消费 |
| 💾 **历史记录** | 所有转换结果本地持久化，跨设备挂载自动恢复 |
| 🎨 **典雅中国风 UI** | 印章/卷轴/毛笔字体，竹青朱砂配色 |
| 🚀 **流式进度** | 三步骤进度条（壹/贰/叁），实时显示当前章节 |

## 🚀 30 秒上手

```bash
git clone https://github.com/laozidabo/ai-novel-to-screenplay.git
cd ai-novel-to-screenplay
bash setup.sh                    # 1. 创建 venv + 安装依赖
cp .env.example .env             # 2. 填入 DEEPSEEK_API_KEY
./venv/bin/python app.py         # 3. 启动 (浏览器打开 http://127.0.0.1:7868)
```

> 提示：评委/队友可运行 `./venv/bin/python verify_run.py` 一键验证可运行性。

## 📖 详细文档

### 1. 准备 API Key

注册 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API Key，编辑 `.env`：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 2. 启动应用

```bash
./venv/bin/python app.py
```

浏览器打开 `http://127.0.0.1:7868`。

> 端口被占用？设置环境变量 `GRADIO_SERVER_PORT=7869 ./venv/bin/python app.py`

### 3. 三种使用方式

#### 方式 A：直接粘贴（≤ 5 章）
在「📝 小说原文」框粘贴文本，点击 `🔄 转 换`。

#### 方式 B：内置示例
点击 `📖 加载示例` → 选 `示例 1：第一章（最快）` → `🔄 转 换`。

#### 方式 C：书架扫描（任意大小）★ 推荐
1. 在「📚 书架」面板粘贴文件夹路径（如 `/home/user/小说库`）
2. 点击 `🔍 扫 描`，下拉框出现所有 .txt 文件（含精确章节数）
3. 选中文件，填写「起始章」「结束章」（默认 1-5）
4. 点击 `📥 载入章节` → 文本自动填入输入框
5. 点击 `🔄 转 换`

### 4. 端到端验证

```bash
./venv/bin/python verify_run.py
```

自动检查 6 项：文件齐全 / 语法正确 / 依赖装好 / 启动成功 / API 正常 / 自动清理。
退出码 0 = 全部通过，1 = 有失败。适合 CI 集成。

## 🎬 转换流水线

```
小说文本 (任意长度)
    ↓
┌─────────────────────────────────┐
│  壹 · 解析章节                    │  ← 自动识别「第 N 章/回/节」
│  (chapter_parser.py)              │
└─────────────────────────────────┘
    ↓ chapters[0..N]
┌─────────────────────────────────┐
│  贰 · AI 分析 (Map)              │  ← 逐章调用 DeepSeek
│  (converter.py · analyze)        │     提取角色/场景/对话/动作
└─────────────────────────────────┘
    ↓ analyses[]
┌─────────────────────────────────┐
│  Story Bible 合并 (Reduce)       │  ← 角色去重 + 关系建立
│  (converter.py · compile_bible)  │
└─────────────────────────────────┘
    ↓ story_bible
┌─────────────────────────────────┐
│  叁 · 生成剧本 (Reduce)          │  ← 幕→场景→块 三层结构
│  (converter.py · generate)        │     严格好莱坞格式
└─────────────────────────────────┘
    ↓ screenplay
┌─────────────────────────────────┐
│  Schema 校验 (schema.py)          │  ← JSON Schema 严格验证
└─────────────────────────────────┘
    ↓
YAML 输出 → 📄 YAML 原文 / 📥 下载
```

## 📂 项目结构

```
ai-novel-to-screenplay/
├── app.py                  # Gradio 主界面（含书架 UI + 进度条 + 历史记录）
├── library.py              # 📚 书架: 文件夹扫描 + 章节范围读取
├── converter.py            # AI 转换 Map-Reduce 流水线
├── prompts.py              # 三阶段提示词模板
├── schema.py               # JSON Schema 校验
├── chapter_parser.py       # 章节识别（7+ 种格式）
├── verify_run.py           # 端到端可运行性验证脚本
├── requirements.txt        # 依赖清单
├── setup.sh                # 一键初始化 (venv + pip install)
├── .env.example            # 环境变量示例
├── schemas/
│   └── screenplay.schema.json
├── docs/
│   └── yaml_schema.md
└── examples/
    └── sample_novel.txt    # 内置示例 (3 章)
```

## 📋 输出格式

```yaml
schema_version: "1.0.0"
title: "剧本标题"
characters:                    # 角色表
  - name: "林惊羽"
    role: "protagonist"
    description: "重生者, 前世魔尊"
acts:                          # 幕
  - id: "A1"
    title: "第一幕"
    scenes:                    # 场景
      - id: "S001"
        heading: "EXT. 天庭 - 日"
        blocks:                # 块
          - type: "action"
            text: "狂风扑面..."
          - type: "dialogue"
            character: "方源"
            text: "魔道永昌!"
```

完整 Schema 见 [`docs/yaml_schema.md`](docs/yaml_schema.md)。

## 🔍 支持的章节格式

| 格式 | 示例 |
|------|------|
| 中文数字 | `第一章` / `第十二章` / `第一百零八章` |
| 阿拉伯数字 | `第1章` / `第123章` |
| 回/节变体 | `第一回` / `第N节` / `第1节` |
| 英文 | `Chapter 1` / `CHAPTER 12` |
| 特殊 | `序章` / `楔子` / `尾声` / `终章` |

> 实测支持「人界」「魔界」类超长网文（22MB / 2335 章）。

## ⚙️ 配置

### 环境变量 (`.env`)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEPSEEK_API_KEY` | (必填) | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API 端点 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 模型名 |
| `GRADIO_SERVER_PORT` | `7868` | UI 端口（端口冲突时调整） |

### 性能参数 (可调)

- 单次最多处理章节数: **5 章** (`converter.py`)
- 单章最长文本: **60,000 字** (`library.py:_read_chapters_range`)
- 单次扫描最大文件: **100 MB** (`library.py:MAX_FILE_SIZE`)
- 扫描目录深度: **4 层** (`library.py:MAX_DEPTH`)

## 🧪 验证与测试

```bash
# 端到端验证 (推荐 push 前跑一遍)
./venv/bin/python verify_run.py

# 单元测试 (TODO)
./venv/bin/python -m pytest tests/
```

`verify_run.py` 会:
1. 检查所有 .py 文件存在
2. AST 语法校验
3. 检查并补装依赖
4. 启动临时 app 实例 (端口 7870)
5. 测试 3 个核心 API: 扫描 / 加载 / 错误处理
6. 自动清理 .env 和进程

## 🤝 贡献

欢迎 PR！但请遵守仓库根目录 [`AGENTS.md`](AGENTS.md) 的约定:
- **小颗粒 PR**: 一个功能一个 PR
- **commit 时间戳**: 必须落在比赛窗口内
- **可运行性**: 合并后主分支必须能用 `./venv/bin/python app.py` 跑通
- **不提交密钥**: `.env` 和 `outputs/` 已在 `.gitignore` 中

## 📜 许可证

MIT

---

**Built with ❤️ for [AI+Education Hackathon]**
