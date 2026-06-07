"""
AI小说转剧本工具 - 主界面

Gradio Web界面，支持输入小说文本并展示转换结果。
功能：
- 自动章节识别（第X章、Chapter X等）
- AI智能转换（角色、场景、对话、动作）
- 多格式输出（电影/电视剧/短视频）
- 结构化YAML剧本
- 实时进度显示
- 一键复制/下载
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml

# 自定义CSS样式
CUSTOM_CSS = """
/* 全局字体和背景 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --accent-warm: #e2b714;
    --accent-soft: #f0c040;
    --text-primary: #e8e8e8;
    --text-secondary: #a0a0b0;
    --text-muted: #6c6c7e;
    --border: #2a2a4a;
    --success: #4ade80;
    --error: #f87171;
}

/* 主容器 */
.gradio-container {
    background: var(--bg-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    min-height: 100vh;
}

/* 标题区域 */
.header-section {
    text-align: center;
    padding: 2rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}

.header-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-warm);
    letter-spacing: 0.15em;
    margin: 0;
    text-shadow: 0 2px 8px rgba(226, 183, 20, 0.2);
}

.header-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    letter-spacing: 0.08em;
}

/* 统计信息栏 */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 0.8rem 0;
    margin-bottom: 1rem;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.stat-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-warm);
    opacity: 0.7;
}

/* 主内容区域 */
.main-content {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0;
    align-items: stretch;
    min-height: 65vh;
}

/* 面板通用样式 */
.panel {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.panel-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.panel-label {
    font-family: 'Noto Serif SC', serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--accent-warm);
    letter-spacing: 0.1em;
}

.panel-badge {
    font-size: 0.75rem;
    color: var(--text-muted);
    background: rgba(226, 183, 20, 0.1);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    border: 1px solid rgba(226, 183, 20, 0.2);
}

/* 中间转换按钮列 */
.center-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 1.5rem;
    gap: 1rem;
}

/* 自定义输入框 */
.input-textbox textarea, .output-textbox textarea {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.8 !important;
    border: none !important;
    padding: 1.2rem !important;
    resize: none !important;
}

.input-textbox textarea::placeholder {
    color: var(--text-muted) !important;
    font-style: italic;
}

.input-textbox textarea:focus, .output-textbox textarea:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* 转换按钮 */
.convert-btn {
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-soft)) !important;
    color: var(--bg-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.15em !important;
    padding: 1rem 2rem !important;
    border: none !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(226, 183, 20, 0.3) !important;
    min-width: 140px !important;
}

.convert-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(226, 183, 20, 0.4) !important;
}

.convert-btn:active {
    transform: translateY(0) !important;
}

/* 箭头指示 */
.arrow-icon {
    color: var(--accent-warm);
    font-size: 1.5rem;
    opacity: 0.6;
}

/* 底部操作栏 */
.action-bar {
    display: flex;
    justify-content: center;
    gap: 1rem;
    padding: 1.5rem 0;
    margin-top: 1rem;
}

.action-btn {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.action-btn:hover {
    border-color: var(--accent-warm) !important;
    color: var(--accent-warm) !important;
}

/* 状态指示 */
.status-bar {
    text-align: center;
    padding: 0.5rem;
    color: var(--text-muted);
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
}

/* 格式选择器 */
.format-selector {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin: 0.5rem 0;
}

.format-chip {
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    cursor: pointer;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    transition: all 0.2s ease;
}

.format-chip.active {
    background: rgba(226, 183, 20, 0.15);
    border-color: var(--accent-warm);
    color: var(--accent-warm);
}

/* Gradio组件覆盖 */
.gradio-container .prose {
    color: var(--text-primary) !important;
}

.gradio-container .prose h1,
.gradio-container .prose h2 {
    color: var(--accent-warm) !important;
}

/* 全局覆盖Gradio默认样式 */
.gradio-container {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.gradio-container textarea,
.gradio-container input {
    background: transparent !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

.gradio-container textarea:focus,
.gradio-container input:focus {
    border-color: var(--accent-warm) !important;
    box-shadow: 0 0 0 1px var(--accent-warm) !important;
}

/* 按钮样式覆盖 */
.gradio-container button.primary {
    background: linear-gradient(135deg, var(--accent-warm), var(--accent-soft)) !important;
    color: var(--bg-primary) !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
}

.gradio-container button.secondary {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
}

/* 隐藏Gradio默认标签 */
.panel .gradio-group {
    border: none !important;
    background: transparent !important;
}

.panel label, .panel .label-wrap {
    display: none !important;
}

/* 滚动条样式 */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* 响应式 */
@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    .center-column {
        flex-direction: row;
        padding: 0.5rem 0;
    }
    .header-title {
        font-size: 1.5rem;
    }
}
"""

# Gradio自定义主题
custom_theme = gr.themes.Base(
    primary_hue=gr.themes.colors.yellow,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[
        gr.themes.GoogleFont("Noto Serif SC"),
        gr.themes.GoogleFont("JetBrains Mono"),
        "serif",
    ],
)


def build_schema_info_html(is_valid=None, errors=None):
    """
    构建Schema校验状态（简洁版，不破坏视觉连贯性）。
    """
    if is_valid is None:
        return ""
    elif is_valid:
        return '<div style="text-align: center; padding: 0.3rem; font-size: 0.7rem; color: #4ade80;">✓ Schema校验通过</div>'
    else:
        error_text = errors[0] if errors else "未知错误"
        return f'<div style="text-align: center; padding: 0.3rem; font-size: 0.7rem; color: #f87171;">✗ {error_text}</div>'


def convert_novel_with_progress(text):
    """
    带进度显示的完整转换流水线。
    使用生成器yield中间结果，实现进度更新。
    """
    if not text or not text.strip():
        yield "请输入小说文本", build_schema_info_html(), ""
        return

    char_count = len(text)
    detected_count = get_chapter_count(text)
    chapters = split_chapters(text)
    chapter_count = len(chapters)

    if detected_count < 1:
        yield (
            "# ❌ 未检测到章节\n\n"
            "请确保文本包含章节标记，如：\n"
            "- 第一章 标题\n"
            "- 第1章 标题\n"
            "- 第一回 标题\n"
            "- Chapter 1 标题",
            build_schema_info_html(),
            "❌ 失败",
        )
        return

    # 限制最多处理5章（避免API超时和费用）
    if chapter_count > 5:
        chapters = chapters[:5]
        chapter_count = 5

    # 检查API密钥
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        yield (
            "# ❌ API密钥未配置\n\n"
            "请按以下步骤配置：\n\n"
            "1. 编辑 `~/ai-novel-to-screenplay/.env` 文件\n"
            "2. 将 `DEEPSEEK_API_KEY=your_api_key_here` 改为你的真实API Key\n"
            "3. 保存后重启应用\n\n"
            "获取API Key：https://platform.deepseek.com/",
            build_schema_info_html(is_valid=False, errors=["API密钥未配置"]),
            "❌ API未配置",
        )
        return

    # ========================================
    # 步骤1：逐章分析（Map）
    # ========================================
    # 预估时间：每章约15秒分析 + 20秒合并 + 30秒生成
    est_per_chapter = 15
    est_merge = 20
    est_generate = 30
    est_total = chapter_count * est_per_chapter + est_merge + est_generate

    try:
        analyses = []
        for i, ch in enumerate(chapters):
            est_remaining = (chapter_count - i) * est_per_chapter + est_merge + est_generate
            yield (
                f"# ⏳ 正在分析第 {i+1}/{chapter_count} 章\n\n"
                f"> {ch['title']}\n\n"
                f"⏱ 预估剩余 {est_remaining} 秒",
                build_schema_info_html(),
                f"⏳ 分析第{i+1}章 · ~{est_remaining}s",
            )
            result, error = analyze_chapter(ch["content"])
            if error:
                yield (
                    f"# ❌ 第{i+1}章分析失败\n\n"
                    f"**错误信息**：{error}\n\n"
                    f"---\n\n"
                    f"**可能原因**：\n"
                    f"- API余额不足\n"
                    f"- 网络连接问题\n"
                    f"- 文本内容过长",
                    build_schema_info_html(is_valid=False, errors=[error]),
                    "❌ 章节分析失败",
                )
                return
            analyses.append(result)
    except Exception as e:
        yield (
            f"# ❌ 章节分析异常\n\n"
            f"**错误**：{str(e)}\n\n"
            f"请检查网络连接和API配置。",
            build_schema_info_html(is_valid=False, errors=[str(e)]),
            "❌ 异常",
        )
        return

    # ========================================
    # 步骤2：合并Story Bible（Reduce）
    # ========================================
    try:
        yield (
            "# ⏳ 正在合并角色和场景\n\n"
            f"> 合并各章分析结果\n\n"
            f"⏱ 预估剩余 {est_merge + est_generate} 秒",
            build_schema_info_html(),
            f"⏳ 合并中 · ~{est_merge + est_generate}s",
        )
        story_bible, error = generate_story_bible(analyses)
        if error:
            yield (
                f"# ❌ Story Bible合并失败\n\n"
                f"**错误信息**：{error}",
                build_schema_info_html(is_valid=False, errors=[error]),
                "❌ 合并失败",
            )
            return
    except Exception as e:
        yield (
            f"# ❌ Story Bible合并异常\n\n"
            f"**错误**：{str(e)}",
            build_schema_info_html(is_valid=False, errors=[str(e)]),
            "❌ 异常",
        )
        return

    # ========================================
    # 步骤3：生成剧本（Generate）
    # ========================================
    try:
        yield (
            "# ⏳ 正在生成剧本\n\n"
            f"⏱ 预估剩余 {est_generate} 秒",
            build_schema_info_html(),
            f"⏳ 生成中 · ~{est_generate}s",
        )
        screenplay, error = generate_screenplay(story_bible, analyses, chapter_count)
        if screenplay is None:
            yield (
                f"# ❌ 剧本生成失败\n\n"
                f"**错误信息**：{error}",
                build_schema_info_html(is_valid=False, errors=[error]),
                "❌ 生成失败",
            )
            return
    except Exception as e:
        yield (
            f"# ❌ 剧本生成异常\n\n"
            f"**错误**：{str(e)}",
            build_schema_info_html(is_valid=False, errors=[str(e)]),
            "❌ 异常",
        )
        return

    # ========================================
    # 步骤4：YAML输出
    # ========================================
    yaml_output = to_yaml(screenplay)

    # Schema校验
    is_valid, errors = validate_screenplay(screenplay)

    # 构建输出
    title = screenplay.get("title", "未知")
    characters = screenplay.get("characters", [])
    acts = screenplay.get("acts", [])
    total_scenes = sum(len(act.get("scenes", [])) for act in acts)

    output = f"""# {title}

> 基于 {chapter_count} 章小说文本自动生成的结构化剧本

---

{yaml_output}

---

**统计**：{len(characters)} 个角色 · {len(acts)} 幕 · {total_scenes} 个场景"""

    if error:
        output += f"\n\n⚠️ {error}"

    yield output, build_schema_info_html(is_valid=is_valid, errors=errors), "✅ 转换完成"


# 保留旧函数名兼容
def convert_novel(text):
    """兼容旧接口，取最终结果"""
    for result in convert_novel_with_progress(text):
        final = result
    return final[0], final[1]


def load_example():
    """加载示例小说文本"""
    import os
    example_path = os.path.join(os.path.dirname(__file__), "examples", "sample_novel.txt")
    try:
        with open(example_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "示例文件未找到"


def update_stats(text):
    """更新输入统计，包含章节信息"""
    if not text or not text.strip():
        return (
            '<div class="stats-bar"><div class="stat-item"><span class="stat-dot"></span><span>等待输入</span></div></div>',
            "",
        )

    chars = len(text)
    chapters = split_chapters(text)
    chapter_count = len(chapters)

    # 统计栏
    if chapter_count >= 3:
        status_color = "#4ade80"
        status_text = f"已检测 {chapter_count} 章 ✓"
    elif chapter_count > 0:
        status_color = "#fbbf24"
        status_text = f"已检测 {chapter_count} 章（需要至少3章）"
    else:
        status_color = "#f87171"
        status_text = "未检测到章节标记，将自动分块"

    stats_html = f"""
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-dot"></span>
            <span>字数: {chars:,}</span>
        </div>
        <div class="stat-item">
            <span class="stat-dot" style="background: {status_color}"></span>
            <span>{status_text}</span>
        </div>
    </div>
    """

    # 章节详情
    if chapters:
        chapter_rows = ""
        for ch in chapters[:20]:  # 最多显示20章
            ch_len = len(ch["content"])
            chapter_rows += f"""
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #2a2a4a; font-size: 0.8rem;">
                <span style="color: #e2b714; min-width: 2rem;">{ch['index']}</span>
                <span style="color: #e8e8e8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{ch['title']}</span>
                <span style="color: #6c6c7e; min-width: 4rem; text-align: right;">{ch_len:,}字</span>
            </div>
            """
        if chapter_count > 20:
            chapter_rows += f'<div style="color: #6c6c7e; font-size: 0.75rem; padding: 0.3rem 0;">... 还有 {chapter_count - 20} 章</div>'

        detail_html = f"""
        <div style="padding: 0.5rem 1rem; max-height: 200px; overflow-y: auto;">
            {chapter_rows}
        </div>
        """
    else:
        detail_html = ""

    return stats_html, detail_html


# Gradio界面
with gr.Blocks(title="AI小说转剧本工具") as demo:

    # 头部
    gr.HTML("""
    <div class="header-section">
        <h1 class="header-title">剧 · 本 · 工 · 坊</h1>
        <p class="header-subtitle">AI 小说转剧本工具 · 将文字化为舞台</p>
    </div>
    """)

    # 使用说明
    with gr.Accordion("📖 使用说明", open=False):
        gr.Markdown("""
**快速体验**：点击「📖 加载示例」按钮，然后点击「转 换」

**使用步骤**：
1. 在左侧粘贴小说文本（至少3个章节）
2. 点击「转 换」按钮
3. 等待2-3分钟，右侧显示YAML格式剧本

**章节格式要求**：
- `第一章 标题` / `第1章 标题` / `第一回 标题`
- `Chapter 1 标题` / `序章` / `楔子`

**输出内容**：
- 结构化YAML剧本（幕→场景→块）
- 角色表（含描述、类型）
- 五点结构映射（开场→冲突→中点→高潮→结局）
- Schema校验结果

**技术栈**：Python + Gradio + DeepSeek API
        """)

    # 统计栏
    stats_display = gr.HTML("""
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-dot"></span>
            <span>就绪</span>
        </div>
    </div>
    """)

    # 章节详情
    chapter_detail = gr.HTML("")

    # 主内容区
    with gr.Row(equal_height=True):
        # 左侧输入面板
        with gr.Column(scale=5):
            gr.HTML("""
            <div class="panel-header">
                <span class="panel-label">原 · 文</span>
                <span class="panel-badge">小说文本</span>
            </div>
            """)
            input_text = gr.Textbox(
                placeholder="在此粘贴小说文本...\n\n建议包含3个以上章节，每章以「第X章」开头。\n\n示例：\n第一章 风起\n那年春天...",
                lines=22,
                max_lines=30,
                show_label=False,
                elem_classes=["input-textbox"],
                container=False,
            )

        # 中间操作区
        with gr.Column(scale=1, min_width=160):
            gr.HTML('<div class="center-column">')
            convert_btn = gr.Button(
                "转 换",
                variant="primary",
                elem_classes=["convert-btn"],
                size="lg",
            )
            gr.HTML("""
                <div class="arrow-icon">→</div>
                <div style="color: #6c6c7e; font-size: 0.75rem; text-align: center;">
                    YAML格式
                </div>
            """)
            example_btn = gr.Button(
                "📖 加载示例",
                variant="secondary",
                size="sm",
            )
            gr.HTML("</div>")

        # 右侧输出面板
        with gr.Column(scale=5):
            gr.HTML("""
            <div class="panel-header">
                <span class="panel-label">剧 · 本</span>
                <span class="panel-badge">YAML 输出</span>
            </div>
            """)
            output_text = gr.Textbox(
                placeholder="剧本输出将在此显示...\n\n转换完成后，您可以：\n• 复制内容\n• 下载 .yaml 文件",
                lines=18,
                max_lines=30,
                show_label=False,
                interactive=False,
                elem_classes=["output-textbox"],
                container=False,
            )

            # 复制和下载按钮
            with gr.Row():
                copy_btn = gr.Button("📋 复制", size="sm", variant="secondary")
                download_btn = gr.Button("💾 下载YAML", size="sm", variant="secondary")

            # Schema校验状态
            schema_status = gr.HTML("")


    # 底部操作栏
    gr.HTML("""
    <div class="action-bar">
        <div style="color: #6c6c7e; font-size: 0.8rem;">
            支持格式：电影剧本 · 电视剧剧本 · 短视频脚本
        </div>
    </div>
    """)

    # 状态栏
    status_bar = gr.HTML("""
    <div class="status-bar">
        就绪 · 等待输入
    </div>
    """)

    # 事件绑定（流式进度）
    convert_btn.click(
        fn=convert_novel_with_progress,
        inputs=input_text,
        outputs=[output_text, schema_status, status_bar],
    )

    example_btn.click(
        fn=load_example,
        outputs=input_text,
    )

    # 复制功能（JavaScript）
    copy_btn.click(
        fn=None,
        inputs=output_text,
        outputs=None,
        js="(text) => {navigator.clipboard.writeText(text); return '已复制！'}",
    )

    # 下载功能
    def download_yaml(text):
        if not text:
            return None
        import tempfile
        import os
        # 清理YAML内容（去掉Markdown标题）
        lines = text.split("\n")
        yaml_lines = []
        in_yaml = False
        for line in lines:
            if line.startswith("schema_version:"):
                in_yaml = True
            if in_yaml:
                yaml_lines.append(line)
        yaml_content = "\n".join(yaml_lines)
        if not yaml_content:
            yaml_content = text
        # 写入临时文件
        filepath = os.path.join(tempfile.gettempdir(), "screenplay.yaml")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        return filepath

    download_btn.click(
        fn=download_yaml,
        inputs=output_text,
        outputs=gr.File(label="下载YAML"),
    )

    input_text.change(
        fn=update_stats,
        inputs=input_text,
        outputs=[stats_display, chapter_detail],
    )


if __name__ == "__main__":
    print("=" * 50)
    print("AI小说转剧本工具 v1.0.0")
    print("=" * 50)
    print("启动中...")
    demo.launch(theme=custom_theme, css=CUSTOM_CSS)
