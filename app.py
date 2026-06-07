"""
AI小说转剧本工具 - 主界面

温暖文学风格 + 视觉层次感
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml

# ============================================================
# 自定义CSS - 温暖文学 + 视觉层次
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #f5f0e8;
    --bg-warm: #f0ebe0;
    --bg-card: #fffdf9;
    --bg-input: #faf7f0;
    --accent: #8b6914;
    --accent-dark: #6b5010;
    --accent-light: #c4a35a;
    --accent-glow: rgba(139, 105, 20, 0.08);
    --text: #3a3226;
    --text-sec: #7a7062;
    --text-muted: #a89e90;
    --border: #e0d8c8;
    --border-light: #ece6da;
    --shadow-sm: 0 1px 2px rgba(60, 40, 10, 0.04);
    --shadow-md: 0 2px 8px rgba(60, 40, 10, 0.06);
    --shadow-lg: 0 4px 16px rgba(60, 40, 10, 0.08);
    --green: #4a7c5c;
    --red: #b84d4d;
    --radius: 10px;
}

/* 全局背景 - 微妙渐变 */
.gradio-container {
    background: linear-gradient(170deg, #f8f3eb 0%, #f0ebe0 50%, #ece5d8 100%) !important;
    color: var(--text) !important;
    font-family: 'Noto Serif SC', serif !important;
    min-height: 100vh;
}

/* 纸张纹理叠加 */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.02'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* 隐藏Gradio默认元素 */
.gradio-container label, .gradio-container .label-wrap { display: none !important; }
.gradio-container .gradio-group { border: none !important; background: transparent !important; }
.gradio-container .container { position: relative; z-index: 1; }

/* ===== HEADER ===== */
.header {
    background: linear-gradient(180deg, #fffdf9 0%, #f5f0e8 100%);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    position: relative;
}

.header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}

.header h1 {
    font-family: 'Noto Serif SC', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.25em;
    margin: 0;
    text-shadow: 0 1px 2px rgba(139, 105, 20, 0.1);
}

.header p {
    font-size: 0.85rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    margin: 0.6rem 0 0;
}

/* ===== USAGE SECTION ===== */
.usage-wrap {
    max-width: 900px;
    margin: 0 auto 1.5rem;
    padding: 0 2rem;
}

.usage-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
}

.usage-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}

.usage-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.usage-card .icon {
    font-size: 1.5rem;
    margin-bottom: 0.4rem;
}

.usage-card .title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 0.2rem;
}

.usage-card .desc {
    font-size: 0.68rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* ===== MAIN PANELS ===== */
.panels {
    max-width: 1100px;
    margin: 0 auto 1.5rem;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-md);
    transition: box-shadow 0.2s ease;
}

.panel:hover {
    box-shadow: var(--shadow-lg);
}

.panel-head {
    padding: 0.7rem 1.2rem;
    background: linear-gradient(135deg, rgba(139, 105, 20, 0.06) 0%, rgba(139, 105, 20, 0.02) 100%);
    border-bottom: 1px solid var(--border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-head .label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.15em;
}

.panel-head .badge {
    font-size: 0.65rem;
    color: var(--text-muted);
    background: var(--bg);
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    border: 1px solid var(--border-light);
}

/* Textareas */
.gradio-container textarea {
    background: var(--bg-input) !important;
    color: var(--text) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-size: 0.88rem !important;
    line-height: 1.9 !important;
    border: none !important;
    padding: 1.2rem !important;
    resize: none !important;
}

.gradio-container textarea::placeholder {
    color: var(--text-muted) !important;
    font-style: italic;
}

.gradio-container textarea:focus {
    box-shadow: inset 0 0 0 2px var(--accent-glow) !important;
    outline: none !important;
}

/* ===== CONTROL BAR ===== */
.controls {
    max-width: 1100px;
    margin: 0 auto 1.5rem;
    padding: 0 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
}

.convert-btn {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%) !important;
    color: #fff !important;
    font-family: 'Noto Serif SC', serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.2em !important;
    padding: 0.75rem 3rem !important;
    border: none !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 3px 12px rgba(139, 105, 20, 0.25) !important;
}

.convert-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 105, 20, 0.35) !important;
}

.convert-btn:active {
    transform: translateY(0) !important;
}

.example-btn, .copy-btn, .download-btn {
    background: var(--bg-card) !important;
    color: var(--text-sec) !important;
    border: 1px solid var(--border) !important;
    padding: 0.5rem 1rem !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
}

.example-btn:hover, .copy-btn:hover, .download-btn:hover {
    border-color: var(--accent-light) !important;
    color: var(--accent) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ===== STATUS ===== */
.status {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 2rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.72rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-light);
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .panels { grid-template-columns: 1fr; }
    .usage-cards { grid-template-columns: repeat(2, 1fr); }
    .header h1 { font-size: 1.5rem; }
}
"""

# ============================================================
# Schema信息
# ============================================================
def build_schema_info_html(is_valid=None, errors=None):
    if is_valid is None:
        return ""
    elif is_valid:
        return '<div style="text-align:center;padding:0.3rem;font-size:0.7rem;color:#4a7c5c;">✓ 校验通过</div>'
    else:
        error_text = errors[0] if errors else "未知错误"
        return f'<div style="text-align:center;padding:0.3rem;font-size:0.7rem;color:#b84d4d;">✗ {error_text}</div>'

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
        yield "❌ 未检测到章节\n\n请确保文本包含章节标记（如「第一章」）", build_schema_info_html(), "❌ 失败"
        return

    if chapter_count > 5:
        chapters = chapters[:5]
        chapter_count = 5

    import os
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        yield "❌ API密钥未配置\n\n编辑 .env 文件，填入 DEEPSEEK_API_KEY", build_schema_info_html(is_valid=False, errors=["API密钥未配置"]), "❌ 未配置"
        return

    try:
        analyses = []
        for i, ch in enumerate(chapters):
            yield f"⏳ 分析第 {i+1}/{chapter_count} 章...\n\n> {ch['title']}", build_schema_info_html(), f"⏳ 分析第{i+1}章"
            result, error = analyze_chapter(ch["content"])
            if error:
                yield f"❌ 第{i+1}章分析失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌ 失败"
                return
            analyses.append(result)
    except Exception as e:
        yield f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常"
        return

    try:
        yield "⏳ 合并角色和场景...", build_schema_info_html(), "⏳ 合并中"
        story_bible, error = generate_story_bible(analyses)
        if error:
            yield f"❌ 合并失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌ 失败"
            return
    except Exception as e:
        yield f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常"
        return

    try:
        yield "⏳ 生成剧本...", build_schema_info_html(), "⏳ 生成中"
        screenplay, error = generate_screenplay(story_bible, analyses, chapter_count)
        if screenplay is None:
            yield f"❌ 生成失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌ 失败"
            return
    except Exception as e:
        yield f"❌ 异常: {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌ 异常"
        return

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

def convert_novel(text):
    for result in _convert_core(text):
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

# ============================================================
# 界面
# ============================================================
with gr.Blocks(title="剧本工坊") as demo:

    # ===== HEADER =====
    gr.HTML("""
    <div class="header">
        <h1>剧 本 工 坊</h1>
        <p>AI 小说转剧本工具 · 将文字化为舞台</p>
    </div>
    """)

    # ===== USAGE CARDS =====
    gr.HTML("""
    <div class="usage-wrap">
        <div class="usage-cards">
            <div class="usage-card">
                <div class="icon">📖</div>
                <div class="title">加载示例</div>
                <div class="desc">一键体验转换效果</div>
            </div>
            <div class="usage-card">
                <div class="icon">🔄</div>
                <div class="title">AI转换</div>
                <div class="desc">智能识别角色场景</div>
            </div>
            <div class="usage-card">
                <div class="icon">📋</div>
                <div class="title">YAML输出</div>
                <div class="desc">结构化剧本格式</div>
            </div>
            <div class="usage-card">
                <div class="icon">💾</div>
                <div class="title">导出下载</div>
                <div class="desc">一键复制或下载</div>
            </div>
        </div>
    </div>
    """)

    # ===== MAIN PANELS =====
    with gr.Row(elem_classes=["panels"]):
        with gr.Column():
            gr.HTML("""
            <div class="panel">
                <div class="panel-head">
                    <span class="label">原 文</span>
                    <span class="badge">小说文本</span>
                </div>
            </div>
            """)
            input_text = gr.Textbox(
                placeholder="在此粘贴小说文本...\n\n建议包含3个以上章节，每章以「第X章」开头。",
                lines=20,
                max_lines=30,
                show_label=False,
                container=False,
            )

        with gr.Column():
            gr.HTML("""
            <div class="panel">
                <div class="panel-head">
                    <span class="label">剧 本</span>
                    <span class="badge">YAML 输出</span>
                </div>
            </div>
            """)
            output_text = gr.Textbox(
                placeholder="剧本输出将在此显示...\n\n点击「转 换」开始",
                lines=20,
                max_lines=30,
                show_label=False,
                interactive=False,
                container=False,
            )

    # ===== CONTROLS =====
    with gr.Row(elem_classes=["controls"]):
        example_btn = gr.Button("📖 加载示例", elem_classes=["example-btn"])
        convert_btn = gr.Button("转 换", variant="primary", elem_classes=["convert-btn"])
        copy_btn = gr.Button("📋 复制", elem_classes=["copy-btn"])
        download_btn = gr.Button("💾 下载YAML", elem_classes=["download-btn"])

    # ===== STATUS =====
    status_bar = gr.HTML('<div class="status">就绪 · 等待输入</div>')
    schema_status = gr.HTML("", visible=False)

    # ===== EVENTS =====
    convert_btn.click(
        fn=convert_novel,
        inputs=input_text,
        outputs=[output_text, schema_status],
    )

    example_btn.click(fn=load_example, outputs=input_text)

    copy_btn.click(
        fn=None, inputs=output_text, outputs=None,
        js="(text) => {navigator.clipboard.writeText(text); return '已复制！'}",
    )

    def download_yaml(text):
        if not text: return None
        import tempfile, os
        lines = text.split("\n")
        yaml_lines = []
        in_yaml = False
        for line in lines:
            if line.startswith("schema_version:"): in_yaml = True
            if in_yaml: yaml_lines.append(line)
        yaml_content = "\n".join(yaml_lines) if yaml_lines else text
        filepath = os.path.join(tempfile.gettempdir(), "screenplay.yaml")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        return filepath

    download_btn.click(fn=download_yaml, inputs=output_text, outputs=gr.File(label="下载YAML"))

if __name__ == "__main__":
    print("剧本工坊 v1.0.0")
    demo.launch()
