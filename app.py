"""
AI小说转剧本工具 - 主界面

编辑器级精致感 + 文学气质的创作者工具
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml

# ============================================================
# 自定义CSS
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-deep: #0f0f13;
    --bg-panel: #16161d;
    --bg-hover: #1e1e28;
    --accent: #d4a853;
    --accent-glow: rgba(212, 168, 83, 0.3);
    --accent-dim: rgba(212, 168, 83, 0.1);
    --text-primary: #e8e4dd;
    --text-secondary: #8a8690;
    --text-muted: #5a5660;
    --border: #2a2a35;
    --green: #7dc87d;
    --red: #d45d5d;
    --blue: #6da7d4;
}

/* 全局 */
.gradio-container {
    background: var(--bg-deep) !important;
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 2rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg-panel);
}

.header-left, .header-right {
    font-size: 0.85rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    min-width: 120px;
}

.header-right { text-align: right; }

.header-center {
    text-align: center;
}

.header-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.2em;
    margin: 0;
}

.header-status {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ===== MAIN LAYOUT ===== */
.main-layout {
    display: grid;
    grid-template-columns: 1fr 120px 1fr;
    height: calc(100vh - 120px);
    gap: 0;
}

/* 左右面板 */
.panel-left, .panel-right {
    background: var(--bg-panel);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.panel-left {
    border-right: 1px solid var(--border);
}

.panel-right {
    border-left: 1px solid var(--border);
}

.panel-label {
    padding: 0.8rem 1.2rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-label-tag {
    color: var(--accent);
    font-weight: 600;
}

.panel-label-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
}

/* 中间控制区 */
.control-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    background: var(--bg-deep);
    position: relative;
}

.control-column::before {
    content: '';
    position: absolute;
    top: 10%;
    bottom: 10%;
    left: 50%;
    width: 1px;
    background: linear-gradient(
        to bottom,
        transparent,
        var(--border) 20%,
        var(--accent-dim) 50%,
        var(--border) 80%,
        transparent
    );
    transform: translateX(-50%);
}

/* 转换按钮 */
.convert-btn-wrapper {
    position: relative;
    z-index: 1;
}

.convert-btn {
    width: 64px !important;
    height: 64px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, var(--accent), #c49a3d) !important;
    color: var(--bg-deep) !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    border: none !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px var(--accent-glow), 0 0 40px rgba(212, 168, 83, 0.1) !important;
    animation: glow-pulse 2s ease-in-out infinite !important;
    padding: 0 !important;
    min-width: 64px !important;
}

.convert-btn:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 0 30px var(--accent-glow), 0 0 60px rgba(212, 168, 83, 0.2) !important;
}

.convert-btn:active {
    transform: scale(0.95) !important;
}

@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 20px var(--accent-glow), 0 0 40px rgba(212, 168, 83, 0.1); }
    50% { box-shadow: 0 0 30px var(--accent-glow), 0 0 60px rgba(212, 168, 83, 0.2); }
}

/* 进度指示 */
.progress-ring {
    width: 80px;
    height: 80px;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
}

.progress-ring.active {
    opacity: 1;
}

.progress-ring svg {
    animation: rotate 2s linear infinite;
}

.progress-ring circle {
    stroke: var(--accent);
    stroke-width: 2;
    fill: none;
    stroke-dasharray: 200;
    stroke-dashoffset: 200;
    stroke-linecap: round;
}

@keyframes rotate {
    100% { transform: rotate(360deg); }
}

/* 箭头指示 */
.arrow-down {
    color: var(--text-muted);
    font-size: 1.2rem;
    opacity: 0.4;
    z-index: 1;
}

/* 示例按钮 */
.example-btn {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    padding: 0.4rem 0.8rem !important;
    border-radius: 4px !important;
    font-size: 0.7rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    z-index: 1 !important;
    min-width: auto !important;
    width: auto !important;
}

.example-btn:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* 输入输出文本框 */
.input-textbox textarea, .output-textbox textarea {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-size: 0.9rem !important;
    line-height: 1.9 !important;
    border: none !important;
    padding: 1rem 1.2rem !important;
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

/* ===== FOOTER ===== */
.app-footer {
    display: grid;
    grid-template-columns: 1fr 120px 1fr;
    border-top: 1px solid var(--border);
    background: var(--bg-panel);
}

.footer-left, .footer-right {
    padding: 0.6rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.footer-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

.footer-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
}

.footer-btn {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    padding: 0.3rem 0.8rem !important;
    border-radius: 3px !important;
    font-size: 0.7rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    min-width: auto !important;
    width: auto !important;
}

.footer-btn:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* 状态指示 */
.status-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    margin-right: 0.4rem;
    transition: background 0.3s;
}

.status-dot.ready { background: var(--green); }
.status-dot.working { background: var(--accent); animation: blink 1s infinite; }
.status-dot.error { background: var(--red); }

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* YAML语法高亮 */
.yaml-output {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.6;
    padding: 1rem;
    overflow-y: auto;
    max-height: 100%;
}

.yaml-key { color: var(--accent); }
.yaml-string { color: var(--green); }
.yaml-number { color: var(--blue); }
.yaml-comment { color: var(--text-muted); font-style: italic; }

/* 使用说明 */
.usage-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    margin: 0.5rem;
}

.usage-panel h3 {
    color: var(--accent);
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

.usage-panel p, .usage-panel li {
    color: var(--text-secondary);
    font-size: 0.75rem;
    line-height: 1.6;
}

/* Schema信息 */
.schema-info {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.8rem;
    margin: 0.5rem;
    font-size: 0.75rem;
}

.schema-field {
    display: flex;
    justify-content: space-between;
    padding: 0.2rem 0;
    border-bottom: 1px solid var(--border);
}

.schema-field-name { color: var(--text-primary); }
.schema-field-type { color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }
.schema-field-required { color: var(--accent); font-size: 0.65rem; }

/* 滚动条 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* 响应式 */
@media (max-width: 900px) {
    .main-layout {
        grid-template-columns: 1fr;
        height: auto;
    }
    .control-column {
        flex-direction: row;
        padding: 1rem;
    }
    .control-column::before { display: none; }
}
"""

# ============================================================
# Gradio主题
# ============================================================
custom_theme = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[
        gr.themes.GoogleFont("Noto Serif SC"),
        gr.themes.GoogleFont("JetBrains Mono"),
        "serif",
    ],
)

# ============================================================
# YAML语法高亮
# ============================================================
def highlight_yaml(text):
    """将YAML文本转为带语法高亮的HTML"""
    if not text:
        return ""
    import re
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        # 转义HTML
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # 高亮key: value
        match = re.match(r'^(\s*)([\w_]+)(\s*:\s*)(.*)', line)
        if match:
            indent, key, colon, value = match.groups()
            # 高亮value
            if value.startswith('"') or value.startswith("'"):
                value_html = f'<span class="yaml-string">{value}</span>'
            elif value.replace('.', '').replace('-', '').isdigit():
                value_html = f'<span class="yaml-number">{value}</span>'
            elif value in ('true', 'false', 'null'):
                value_html = f'<span class="yaml-number">{value}</span>'
            else:
                value_html = f'<span class="yaml-string">{value}</span>'
            html_lines.append(f'{indent}<span class="yaml-key">{key}</span>{colon}{value_html}')
        elif line.strip().startswith('#'):
            html_lines.append(f'<span class="yaml-comment">{line}</span>')
        elif line.strip().startswith('- '):
            # 列表项
            match2 = re.match(r'^(\s*-\s*)(.*)', line)
            if match2:
                indent, content = match2.groups()
                html_lines.append(f'{indent}<span class="yaml-string">{content}</span>')
            else:
                html_lines.append(line)
        else:
            html_lines.append(line)
    return '<div class="yaml-output">' + '<br>'.join(html_lines) + '</div>'


# ============================================================
# 构建Schema信息HTML
# ============================================================
def build_schema_info_html(is_valid=None, errors=None):
    summary = get_schema_summary()
    if is_valid is None:
        status = '<span style="color: var(--text-muted);">等待校验</span>'
    elif is_valid:
        status = '<span style="color: var(--green);">✓ 通过</span>'
    else:
        status = f'<span style="color: var(--red);">✗ 失败</span>'

    fields_html = ""
    for f in summary["fields"]:
        req = ' <span class="schema-field-required">必填</span>' if f["required"] else ""
        fields_html += f'<div class="schema-field"><span class="schema-field-name">{f["name"]}{req}</span><span class="schema-field-type">{f["type"]}</span></div>'

    errors_html = ""
    if errors:
        for e in errors[:3]:
            errors_html += f'<div style="color: var(--red); font-size: 0.7rem;">• {e}</div>'

    return f'''
    <div class="schema-info">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: var(--accent);">Schema</span>
            {status}
        </div>
        {fields_html}
        {errors_html}
    </div>
    '''


# ============================================================
# 核心转换函数（带进度）
# ============================================================
def convert_novel_with_progress(text):
    if not text or not text.strip():
        yield "请输入小说文本", build_schema_info_html(), "就绪"
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

    if chapter_count < 3:
        yield (
            f"⚠️ 检测到 {chapter_count} 章，需要至少 3 章",
            build_schema_info_html(),
            "⚠️ 章节不足",
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
                f"⏳ 分析第 {i+1}/{chapter_count} 章...\n\n> {ch['title']}",
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

    # 高亮YAML
    yaml_html = highlight_yaml(yaml_output)

    output = f"# {title}\n\n> {len(characters)} 角色 · {len(acts)} 幕 · {total_scenes} 场景\n\n{yaml_output}"
    if error:
        output += f"\n\n⚠️ {error}"

    yield output, build_schema_info_html(is_valid=is_valid, errors=errors), f"✅ {title}"


# ============================================================
# 兼容旧接口
# ============================================================
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
        return "等待输入...", ""
    chars = len(text)
    count = get_chapter_count(text)
    if count >= 3:
        return f"{chars:,} 字 · {count} 章 ✓", ""
    elif count > 0:
        return f"{chars:,} 字 · {count} 章（需要≥3）", ""
    else:
        return f"{chars:,} 字 · 未检测到章节", ""


# ============================================================
# 界面
# ============================================================
with gr.Blocks(title="剧本工坊") as demo:

    # ===== HEADER =====
    gr.HTML("""
    <div class="app-header">
        <div class="header-left">原 · 文</div>
        <div class="header-center">
            <div class="header-title">剧 · 本 · 工 · 坊</div>
            <div class="header-status"><span class="status-dot ready"></span>就绪</div>
        </div>
        <div class="header-right">剧 · 本</div>
    </div>
    """)

    # ===== MAIN =====
    with gr.Row(equal_height=True, elem_classes=["main-layout"]):

        # 左侧：原文
        with gr.Column(scale=1, elem_classes=["panel-left"]):
            gr.HTML('<div class="panel-label"><span class="panel-label-tag">原文</span><span class="panel-label-info">小说文本</span></div>')
            input_text = gr.Textbox(
                placeholder="在此粘贴小说文本...\n\n至少3个章节，每章以「第X章」开头。",
                lines=25,
                max_lines=40,
                show_label=False,
                elem_classes=["input-textbox"],
                container=False,
            )

        # 中间：控制区
        with gr.Column(scale=0, min_width=120, elem_classes=["control-column"]):
            gr.HTML('<div class="arrow-down">▼</div>')
            convert_btn = gr.Button("▶", elem_classes=["convert-btn"], size="lg")
            gr.HTML("""
            <div style="color: var(--text-muted); font-size: 0.65rem; text-align: center; z-index: 1;">
                转 换
            </div>
            """)
            example_btn = gr.Button("📖 示例", elem_classes=["example-btn"], size="sm")
            gr.HTML('<div class="arrow-down">▼</div>')

        # 右侧：剧本
        with gr.Column(scale=1, elem_classes=["panel-right"]):
            gr.HTML('<div class="panel-label"><span class="panel-label-tag">剧本</span><span class="panel-label-info">YAML 输出</span></div>')
            output_text = gr.Textbox(
                placeholder="剧本输出将在此显示...\n\n点击「▶ 转换」开始",
                lines=25,
                max_lines=40,
                show_label=False,
                interactive=False,
                elem_classes=["output-textbox"],
                container=False,
            )

    # ===== FOOTER =====
    gr.HTML("""
    <div class="app-footer">
        <div class="footer-left">
            <span class="footer-stat" id="input-stats">等待输入</span>
        </div>
        <div class="footer-center"></div>
        <div class="footer-right">
            <span class="footer-stat" id="output-status"></span>
        </div>
    </div>
    """)

    # Schema信息（隐藏）
    schema_status = gr.HTML(build_schema_info_html(), visible=False)
    status_bar = gr.HTML("就绪", visible=False)

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

    input_text.change(
        fn=update_stats,
        inputs=input_text,
        outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False)],
    )


if __name__ == "__main__":
    print("=" * 50)
    print("剧本工坊 v1.0.0")
    print("=" * 50)
    demo.launch(theme=custom_theme, css=CUSTOM_CSS)
