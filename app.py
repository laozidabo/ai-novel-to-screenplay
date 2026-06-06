"""
AI小说转剧本工具 - 主界面

Gradio Web界面，支持输入小说文本并展示转换结果。
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary

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


def convert_novel(text):
    """
    转换小说文本为剧本格式（占位函数，后续PR接入真实转换）
    """
    if not text or not text.strip():
        return "请输入小说文本", ""

    char_count = len(text)
    chapter_count = get_chapter_count(text)

    # 占位输出
    output = f"""# 剧本输出（占位）

---

> AI转换功能将在后续版本中实现。

## 输入统计

- 字数：{char_count:,}
- 章节数：{chapter_count}

---

*等待接入 DeepSeek API...*"""

    # Schema信息
    summary = get_schema_summary()
    schema_info = f"""
    <div style="padding: 0.5rem 1rem; font-size: 0.8rem; color: #a0a0b0;">
        <div style="margin-bottom: 0.3rem; color: #e2b714;">Schema规范</div>
        <div>必填字段: {summary['required_count']} / {summary['total_fields']}</div>
        <div>状态: 等待AI转换...</div>
    </div>
    """

    return output, schema_info


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
                lines=20,
                max_lines=30,
                show_label=False,
                interactive=False,
                elem_classes=["output-textbox"],
                container=False,
            )

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

    # 事件绑定
    convert_btn.click(
        fn=convert_novel,
        inputs=input_text,
        outputs=[output_text, schema_status],
    ).then(
        fn=lambda: '<div class="status-bar">转换完成</div>',
        outputs=status_bar,
    )

    input_text.change(
        fn=update_stats,
        inputs=input_text,
        outputs=[stats_display, chapter_detail],
    )


if __name__ == "__main__":
    demo.launch(theme=custom_theme, css=CUSTOM_CSS)
