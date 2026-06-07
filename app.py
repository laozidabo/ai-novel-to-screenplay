"""
AI小说转剧本工具 - 主界面

温暖文学风格的创作者工具
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml

# ============================================================
# 自定义CSS - 温暖文学风格
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-page: #f8f5f0;
    --bg-card: #ffffff;
    --bg-input: #faf8f5;
    --accent: #8b6914;
    --accent-light: #c4a35a;
    --accent-bg: rgba(139, 105, 20, 0.06);
    --text-primary: #2c2c2c;
    --text-secondary: #666666;
    --text-muted: #999999;
    --border: #e8e2d8;
    --border-light: #f0ece4;
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --shadow-hover: 0 2px 8px rgba(0,0,0,0.08);
    --green: #4a8c5c;
    --red: #c44d4d;
    --radius: 8px;
}

/* 全局 */
.gradio-container {
    background: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    min-height: 100vh;
}

/* 隐藏Gradio默认元素 */
.gradio-container .prose { color: var(--text-primary) !important; }
.gradio-container .prose h1, .gradio-container .prose h2 { color: var(--accent) !important; }
.gradio-container label, .gradio-container .label-wrap { display: none !important; }
.gradio-container .gradio-group { border: none !important; background: transparent !important; }

/* ===== HEADER ===== */
.app-header {
    text-align: center;
    padding: 2.5rem 2rem 1.5rem;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}

.header-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.2em;
    margin: 0 0 0.5rem 0;
}

.header-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    margin: 0;
}

/* ===== MAIN LAYOUT ===== */
.main-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

.panels-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

/* 面板 */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: box-shadow 0.2s ease;
}

.panel:hover {
    box-shadow: var(--shadow-hover);
}

.panel-header {
    padding: 0.8rem 1.2rem;
    border-bottom: 1px solid var(--border-light);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--accent-bg);
}

.panel-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.15em;
}

.panel-badge {
    font-size: 0.65rem;
    color: var(--text-muted);
    background: var(--bg-page);
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    border: 1px solid var(--border-light);
}

/* 输入输出文本框 */
.input-textbox textarea, .output-textbox textarea {
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-size: 0.9rem !important;
    line-height: 1.9 !important;
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

/* ===== CONTROL BAR ===== */
.control-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1.2rem 0;
    margin-bottom: 1.5rem;
}

.convert-btn {
    background: var(--accent) !important;
    color: white !important;
    font-family: 'Noto Serif SC', serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.8rem 2.5rem !important;
    border: none !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(139, 105, 20, 0.2) !important;
}

.convert-btn:hover {
    background: #7a5c12 !important;
    box-shadow: 0 3px 10px rgba(139, 105, 20, 0.3) !important;
    transform: translateY(-1px) !important;
}

.convert-btn:active {
    transform: translateY(0) !important;
}

.example-btn {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 5px !important;
    font-size: 0.8rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.example-btn:hover {
    border-color: var(--accent-light) !important;
    color: var(--accent) !important;
    background: var(--accent-bg) !important;
}

/* ===== ACTION BAR ===== */
.action-bar {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    padding: 0.8rem 0;
    margin-bottom: 1rem;
}

.action-btn {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    padding: 0.4rem 1rem !important;
    border-radius: 4px !important;
    font-size: 0.75rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.action-btn:hover {
    border-color: var(--accent-light) !important;
    color: var(--accent) !important;
}

/* ===== STATUS BAR ===== */
.status-bar {
    text-align: center;
    padding: 0.6rem;
    color: var(--text-muted);
    font-size: 0.75rem;
    border-top: 1px solid var(--border-light);
    background: var(--bg-card);
}

/* ===== USAGE PANEL ===== */
.usage-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}

.usage-panel h3 {
    color: var(--accent);
    font-size: 0.85rem;
    margin: 0 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-light);
}

.usage-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.usage-item {
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.usage-item strong {
    color: var(--text-primary);
    display: block;
    margin-bottom: 0.2rem;
}

/* ===== SCHEMA INFO ===== */
.schema-info {
    text-align: center;
    padding: 0.4rem;
    font-size: 0.7rem;
    color: var(--text-muted);
}

.schema-info.success { color: var(--green); }
.schema-info.error { color: var(--red); }

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .panels-container {
        grid-template-columns: 1fr;
    }
    .header-title {
        font-size: 1.4rem;
    }
    .usage-grid {
        grid-template-columns: 1fr;
    }
}
"""

# ============================================================
# Gradio主题
# ============================================================
custom_theme = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.stone,
    neutral_hue=gr.themes.colors.stone,
    font=[
        gr.themes.GoogleFont("Noto Serif SC"),
        gr.themes.GoogleFont("JetBrains Mono"),
        "serif",
    ],
)

# ============================================================
# Schema信息
# ============================================================
def build_schema_info_html(is_valid=None, errors=None):
    if is_valid is None:
        return ""
    elif is_valid:
        return '<div class="schema-info success">✓ Schema校验通过</div>'
    else:
        error_text = errors[0] if errors else "未知错误"
        return f'<div class="schema-info error">✗ {error_text}</div>'

# ============================================================
# 核心转换逻辑
# ============================================================
def _convert_core(text):
    if not text or not text.strip():
        yield "请输入小说文本", build_schema_info_html(), ""
        return

    detected_count = get_chapter_count(text)
    chapters = split_chapters(text)
    chapter_count = len(chapters)

    if detected_count < 1:
        yield (
            "❌ 未检测到章节\n\n请确保文本包含章节标记（如「第一章」）",
            build_schema_info_html(),
            "❌ 失败",
        )
        return

    if chapter_count > 5:
        chapters = chapters[:5]
        chapter_count = 5

    import os
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        yield (
            "❌ API密钥未配置\n\n编辑 .env 文件，填入 DEEPSEEK_API_KEY",
            build_schema_info_html(is_valid=False, errors=["API密钥未配置"]),
            "❌ 未配置",
        )
        return

    # Map
    try:
        analyses = []
        for i, ch in enumerate(chapters):
            yield (
                f"⏳ 正在分析第 {i+1}/{chapter_count} 章...\n\n> {ch['title']}",
                build_schema_info_html(),
                f"⏳ 分析第{i+1}章",
            )
            result, error = analyze_chapter(ch["content"])
            if error:
                yield (
                    f"❌ 第{i+1}章分析失败: {error}",
                    build_schema_info_html(is_valid=False, errors=[error]),
                    "❌ 失败",
                )
                return
            analyses.append(result)
    except Exception as e:
        yield (f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常")
        return

    # Reduce
    try:
        yield ("⏳ 合并角色和场景...", build_schema_info_html(), "⏳ 合并中")
        story_bible, error = generate_story_bible(analyses)
        if error:
            yield (f"❌ 合并失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌ 失败")
            return
    except Exception as e:
        yield (f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常")
        return

    # Generate
    try:
        yield ("⏳ 生成剧本...", build_schema_info_html(), "⏳ 生成中")
        screenplay, error = generate_screenplay(story_bible, analyses, chapter_count)
        if screenplay is None:
            yield (f"❌ 生成失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌ 失败")
            return
    except Exception as e:
        yield (f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常")
        return

    # Output
    yaml_output = to_yaml(screenplay)
    is_valid, errors = validate_screenplay(screenplay)
    title = screenplay.get("title", "未知")
    characters = screenplay.get("characters", [])
    acts = screenplay.get("acts", [])
    total_scenes = sum(len(act.get("scenes", [])) for act in acts)

    output = f"# {title}\n\n> {len(characters)} 角色 · {len(acts)} 幕 · {total_scenes} 场景\n\n{yaml_output}"
    if error:
        output += f"\n\n⚠️ {error}"

    yield output, build_schema_info_html(is_valid=is_valid, errors=errors), f"✅ {title}"

# ============================================================
# 包装函数（兼容旧接口）
# ============================================================
def convert_novel_with_progress(text):
    for result in _convert_core(text):
        yield result[0], result[1], result[2]

def convert_novel(text):
    for result in convert_novel_with_progress(text):
        final = result
    return final[0], final[1]

def load_example():
    import os
    path = os.path.join(os.path.dirname(__file__), "examples", "sample_novel.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "示例文件未找到"

def update_stats(text):
    if not text or not text.strip():
        return "等待输入", ""
    chars = len(text)
    count = get_chapter_count(text)
    if count >= 3:
        return f"{chars:,} 字 · {count} 章", ""
    elif count > 0:
        return f"{chars:,} 字 · {count} 章", ""
    else:
        return f"{chars:,} 字", ""

# ============================================================
# 界面
# ============================================================
with gr.Blocks(title="剧本工坊") as demo:

    # ===== HEADER =====
    gr.HTML("""
    <div class="app-header">
        <h1 class="header-title">剧 本 工 坊</h1>
        <p class="header-subtitle">AI 小说转剧本工具 · 将文字化为舞台</p>
    </div>
    """)

    # ===== 使用说明 =====
    with gr.Accordion("📖 使用说明", open=False):
        gr.HTML("""
        <div class="usage-panel">
            <div class="usage-grid">
                <div class="usage-item">
                    <strong>快速体验</strong>
                    点击「📖 加载示例」→ 点击「转 换」
                </div>
                <div class="usage-item">
                    <strong>章节格式</strong>
                    第一章 标题 / 第1章 标题 / Chapter 1
                </div>
                <div class="usage-item">
                    <strong>输出内容</strong>
                    结构化YAML剧本 · 角色表 · 场景 · 对话
                </div>
                <div class="usage-item">
                    <strong>技术栈</strong>
                    Python + Gradio + DeepSeek API
                </div>
            </div>
        </div>
        """)

    # ===== 主内容区 =====
    with gr.Row(equal_height=True, elem_classes=["panels-container"]):
        # 左侧：原文
        with gr.Column():
            gr.HTML("""
            <div class="panel-header">
                <span class="panel-label">原 文</span>
                <span class="panel-badge">小说文本</span>
            </div>
            """)
            input_text = gr.Textbox(
                placeholder="在此粘贴小说文本...\n\n建议包含3个以上章节，每章以「第X章」开头。",
                lines=22,
                max_lines=30,
                show_label=False,
                elem_classes=["input-textbox"],
                container=False,
            )

        # 右侧：剧本
        with gr.Column():
            gr.HTML("""
            <div class="panel-header">
                <span class="panel-label">剧 本</span>
                <span class="panel-badge">YAML 输出</span>
            </div>
            """)
            output_text = gr.Textbox(
                placeholder="剧本输出将在此显示...\n\n点击「转 换」开始",
                lines=22,
                max_lines=30,
                show_label=False,
                interactive=False,
                elem_classes=["output-textbox"],
                container=False,
            )

    # ===== 控制栏 =====
    gr.HTML("""
    <div class="control-bar">
        <span style="color: var(--text-muted); font-size: 0.8rem;">点击转换 →</span>
    </div>
    """)

    with gr.Row(elem_classes=["control-bar"]):
        convert_btn = gr.Button("转 换", variant="primary", elem_classes=["convert-btn"])
        example_btn = gr.Button("📖 加载示例", elem_classes=["example-btn"])

    # ===== 操作栏 =====
    with gr.Row(elem_classes=["action-bar"]):
        copy_btn = gr.Button("📋 复制", size="sm", variant="secondary", elem_classes=["action-btn"])
        download_btn = gr.Button("💾 下载YAML", size="sm", variant="secondary", elem_classes=["action-btn"])

    # ===== 状态栏 =====
    status_bar = gr.HTML("""
    <div class="status-bar">
        就绪 · 等待输入
    </div>
    """)

    # Schema信息（隐藏）
    schema_status = gr.HTML("", visible=False)

    # ===== 事件绑定 =====
    convert_btn.click(
        fn=convert_novel_with_progress,
        inputs=input_text,
        outputs=[output_text, schema_status, status_bar],
    )

    example_btn.click(
        fn=load_example,
        outputs=input_text,
    )

    # 复制功能
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
        import tempfile, os
        lines = text.split("\n")
        yaml_lines = []
        in_yaml = False
        for line in lines:
            if line.startswith("schema_version:"):
                in_yaml = True
            if in_yaml:
                yaml_lines.append(line)
        yaml_content = "\n".join(yaml_lines) if yaml_lines else text
        filepath = os.path.join(tempfile.gettempdir(), "screenplay.yaml")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        return filepath

    download_btn.click(
        fn=download_yaml,
        inputs=output_text,
        outputs=gr.File(label="下载YAML"),
    )


if __name__ == "__main__":
    print("=" * 50)
    print("剧本工坊 v1.0.0")
    print("=" * 50)
    demo.launch(theme=custom_theme, css=CUSTOM_CSS)
