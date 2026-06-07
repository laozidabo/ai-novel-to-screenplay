# AI小说转剧本工具

将小说文本自动转换为结构化剧本（YAML格式），帮助作者快速获得可编辑的剧本初稿。

## 功能特点

- **自动章节识别**：支持"第X章"、"第X回"、"Chapter X"等多种格式
- **AI智能转换**：基于DeepSeek API，自动提取角色、场景、对话、动作
- **专业剧本格式**：对齐好莱坞标准（INT./EXT.场景标题、动作描写、对话格式）
- **多格式输出**：支持电影剧本、电视剧剧本、短视频脚本三种格式
- **结构化输出**：YAML格式，幕→场景→块三层结构，便于编辑和二次开发
- **Schema校验**：自动校验输出格式，确保数据正确性
- **实时进度**：转换过程中显示当前步骤
- **一键体验**：内置示例小说，打开即可体验
- **复制/下载**：支持一键复制YAML内容或下载.yaml文件

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/laozidabo/ai-novel-to-screenplay.git
cd ai-novel-to-screenplay
```

### 2. 一键初始化环境

```bash
bash setup.sh
```

### 3. 配置API密钥

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

获取API Key：https://platform.deepseek.com/

### 4. 启动应用

```bash
source venv/bin/activate
python app.py
```

浏览器打开 `http://127.0.0.1:7860`

## 使用方法

1. 在左侧输入框粘贴小说文本（至少3个章节）
2. 点击「转 换」按钮
3. 等待2-3分钟
4. 右侧显示YAML格式剧本

**快速体验**：点击「📖 加载示例」按钮，然后点击「转 换」

## 输出格式

输出为结构化YAML剧本，包含：

```yaml
schema_version: "1.0.0"
title: "剧本标题"
characters:
  - name: "角色名"
    role: "protagonist"
    description: "角色描述"
acts:
  - id: "A1"
    title: "第一幕"
    scenes:
      - id: "S001"
        heading: "EXT. 地点 - 时间"
        blocks:
          - type: "action"
            text: "动作描写"
          - type: "dialogue"
            character: "角色名"
            text: "台词内容"
```

完整Schema定义见 [docs/yaml_schema.md](docs/yaml_schema.md)

## 技术栈

- **Python 3.14**
- **Gradio**：Web界面框架
- **DeepSeek API**：AI文本转换
- **PyYAML**：YAML生成
- **jsonschema**：Schema校验

## 项目结构

```
ai-novel-to-screenplay/
├── app.py                  # Gradio主界面
├── converter.py            # AI转换逻辑（Map-Reduce流水线）
├── prompts.py              # 提示词模板（三阶段）
├── schema.py               # Schema校验模块
├── chapter_parser.py       # 章节解析模块
├── requirements.txt        # 依赖清单
├── setup.sh                # 一键初始化脚本
├── .env.example            # 环境变量示例
├── schemas/
│   └── screenplay.schema.json  # JSON Schema定义
├── docs/
│   └── yaml_schema.md      # Schema设计文档
└── examples/
    └── sample_novel.txt    # 示例小说（3章）
```

## AI转换流水线

```
小说文本
    ↓
章节解析（自动识别"第X章"等）
    ↓
逐章AI分析（Map）→ 提取角色、场景、对话、动作
    ↓
合并Story Bible（Reduce）→ 角色去重、关系建立
    ↓
生成结构化剧本 → 幕→场景→块
    ↓
Schema校验 → 确保格式正确
    ↓
YAML输出
```

## 支持的章节格式

- `第一章 标题` / `第1章 标题` / `第十二章 标题`
- `第一回 标题` / `第1回 标题`
- `第一节 标题` / `第1节 标题`
- `Chapter 1 标题` / `CHAPTER 1 标题`
- `序章` / `楔子` / `尾声` / `终章`

## 依赖

```
gradio>=4.0.0
openai>=1.0.0
pyyaml>=6.0
jsonschema>=4.0.0
python-dotenv>=1.0.0
httpx[socks]>=0.24.0
```

## 许可证

MIT
