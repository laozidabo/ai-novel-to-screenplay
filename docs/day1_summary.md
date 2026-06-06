# 第1天工作总结

## 项目背景

### 比赛信息
- **比赛名称**：AI+教育 限时3日议题实战赛
- **选题**：议题三 — AI小说转剧本工具
- **时限**：3天（2026年6月7日-6月9日）
- **评审重点**：产品价值（40%）> 开发过程与质量（40%）> 演示与表达（20%）

### 比赛要求
1. 将3个章节以上的小说文本自动转换为结构化剧本（YAML格式）
2. 输出可编辑、可进一步打磨的剧本初稿
3. 额外写一份YAML Schema设计文档（含设计原因）

### 提交内容
- 公开的GitHub仓库
- Demo视频
- README文档

### PR规范
1. 基于PR添加新功能
2. 每个PR只做一件事，粒度尽可能细
3. PR描述包含：标题、功能描述、实现思路、测试方式
4. PR合并后主分支随时可运行

---

## 技术方案

### 技术栈
- **语言**：Python 3.14
- **Web框架**：Gradio
- **AI API**：DeepSeek（通过openai库调用）
- **YAML处理**：PyYAML + jsonschema
- **环境管理**：venv虚拟环境（CachyOS PEP 668要求）

### 核心架构：Map-Reduce流水线
```
章节解析 → 逐章AI分析(Map) → 合并Story Bible(Reduce) → 生成剧本JSON → Schema校验 → 导出YAML
```

### 项目结构
```
ai-novel-to-screenplay/
├── app.py                  # Gradio主界面
├── converter.py            # AI转换逻辑（待实现）
├── prompts.py              # 提示词模板（待实现）
├── schema.py               # Schema校验模块
├── chapter_parser.py       # 章节解析模块
├── requirements.txt        # 依赖清单
├── setup.sh                # 一键初始化脚本
├── .env.example            # 环境变量示例
├── .gitignore              # 忽略规则
├── README.md               # 项目说明
├── docs/                   # 文档目录
├── examples/               # 示例文件
└── schemas/
    └── screenplay.schema.json  # YAML Schema定义
```

---

## 第1天完成的工作

### PR #1 — 项目初始化+最小界面
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/1
- **内容**：创建项目骨架、依赖配置、一键初始化脚本、最小Gradio界面
- **文件**：requirements.txt, .gitignore, .env.example, setup.sh, app.py, 空模块文件

### PR #2 — UI优化
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/2
- **内容**：暗色文学质感主题（深蓝背景+金色点缀），自定义CSS样式
- **设计**：Noto Serif SC字体 + JetBrains Mono等宽字体，左右分栏布局

### PR #3 — 章节检测逻辑
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/3
- **内容**：实现chapter_parser.py，支持多种中文章节格式
- **支持格式**：第X章、第X回、第X节、Chapter X、序章、楔子等
- **功能**：detect_chapters(), split_chapters(), get_chapter_count()

### PR #4 — 章节拆分+UI展示
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/4
- **内容**：章节解析器集成到界面，实时显示章节数量和详情列表
- **功能**：颜色状态指示（绿色≥3章、黄色<3章、红色未检测）、章节详情列表

### PR #5 — YAML Schema文件定义
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/5
- **内容**：创建JSON Schema文件，定义结构化剧本的完整格式规范
- **结构**：12个顶层字段，7个必填字段，幕→场景→块三层嵌套

### PR #6 — Schema校验函数+UI集成
- **链接**：https://github.com/laozidabo/ai-novel-to-screenplay/pull/6
- **内容**：实现schema.py校验模块，集成到界面显示Schema规范信息
- **功能**：validate_screenplay(), validate_screenplay_full(), get_schema_summary()

---

## 测试验证

### 测试小说
- **文件**：agar.txt（《蛊真人》）
- **规模**：800万字，2335章
- **章节格式**：第X节：标题

### 已验证功能
- ✅ 环境搭建（bash setup.sh）
- ✅ 界面启动（python app.py）
- ✅ 章节检测（支持多种格式）
- ✅ Schema校验（合法/非法数据）
- ✅ 界面实时更新（章节信息、统计）

---

## 第2天计划

### 核心转换功能（PR #7~#13）
| PR | 内容 |
|----|------|
| #7 | Schema校验UI完善 |
| #8 | 基础提示词模板 |
| #9 | 单章AI转换（接UI） |
| #10 | 多章Map处理 |
| #11 | Reduce合并Story Bible |
| #12 | 剧本生成函数 |
| #13 | 完整流水线串联 |

### 关键技术点
- DeepSeek API调用（通过openai库）
- 多阶段提示词设计
- Map-Reduce架构处理长文本
- robust JSON解析（容错处理）

---

## 第3天计划

### 打磨收尾（PR #14~#20）
| PR | 内容 |
|----|------|
| #14 | 电视剧剧本格式 |
| #15 | 短视频脚本+格式选择UI |
| #16 | API错误处理 |
| #17 | 输入验证 |
| #18 | 内置示例+使用说明 |
| #19 | 流式输出优化 |
| #20 | 文档完善（Schema文档+README） |

---

## PR时间线

| 时间 | PR | 状态 |
|------|-----|:---:|
| 第1天 | #1 项目初始化 | ✅ |
| | #2 UI优化 | ✅ |
| | #3 章节检测 | ✅ |
| | #4 章节UI | ✅ |
| | #5 Schema文件 | ✅ |
| | #6 Schema校验 | ✅ |
| 第2天 | #7~#13 核心转换 | ⏳ |
| 第3天 | #14~#20 打磨收尾 | ⏳ |
