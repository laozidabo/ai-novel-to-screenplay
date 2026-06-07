"""
AI小说转剧本工具 - 主界面

温暖文学风格的创作者工具
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
    --bg: #f8f5f0;
    --bg-card: #ffffff;
    --bg-input: #faf8f5;
    --accent: #8b6914;
    --accent-light: #c4a35a;
    --accent-bg: rgba(139, 105, 20, 0.06);
    --text: #2c2c2c;
    --text-sec: #666666;
    --text-muted: #999999;
    --border: #e8e2d8;
    --border-light: #f0ece4;
}

.gradio-container { background: var(--bg) !important; }
.gradio-container label, .gradio-container .label-wrap { display: none !important; }
.gradio-container textarea { background: var(--bg-input) !important; color: var(--text) !important; }
.gradio-container textarea::placeholder { color: var(--text-muted) !important; font-style: italic; }
"""

# ============================================================
# Schema信息
# ============================================================
def build_schema_info_html(is_valid=None, errors=None):
    if is_valid is None:
        return ""
    elif is_valid:
        return '<div style="text-align:center;padding:0.3rem;font-size:0.7rem;color:#4a8c5c;">✓ 校验通过</div>'
    else:
        error_text = errors[0] if errors else "未知错误"
        return f'<div style="text-align:center;padding:0.3rem;font-size:0.7rem;color:#c44d4d;">✗ {error_text}</div>'

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

    # 头部
    gr.HTML("""
    <div style="text-align:center;padding:2rem 0 1rem;background:#fff;border-bottom:1px solid #e8e2d8;">
        <h1 style="font-family:'Noto Serif SC',serif;font-size:1.8rem;font-weight:600;color:#8b6914;letter-spacing:0.2em;margin:0;">剧 本 工 坊</h1>
        <p style="font-size:0.85rem;color:#999;letter-spacing:0.1em;margin:0.5rem 0 0;">AI 小说转剧本工具 · 将文字化为舞台</p>
    </div>
    """)

    # 使用说明
    with gr.Accordion("📖 使用说明", open=False):
        gr.Markdown("""
**快速体验**：点击「📖 加载示例」→ 点击「转 换」

**章节格式**：第一章 标题 / 第1章 标题 / Chapter 1

**输出内容**：结构化YAML剧本 · 角色表 · 场景 · 对话
        """)

    # 主内容区 - 两栏并排
    with gr.Row():
        # 左侧：原文
        with gr.Column():
            gr.HTML('<div style="padding:0.6rem 1rem;background:rgba(139,105,20,0.06);border-bottom:1px solid #e8e2d8;font-size:0.8rem;color:#8b6914;letter-spacing:0.15em;font-weight:600;">原 文 <span style="float:right;color:#999;font-weight:400;font-size:0.7rem;">小说文本</span></div>')
            input_text = gr.Textbox(
                placeholder="在此粘贴小说文本...\n\n建议包含3个以上章节，每章以「第X章」开头。",
                lines=22,
                max_lines=30,
                show_label=False,
                container=False,
            )

        # 右侧：剧本
        with gr.Column():
            gr.HTML('<div style="padding:0.6rem 1rem;background:rgba(139,105,20,0.06);border-bottom:1px solid #e8e2d8;font-size:0.8rem;color:#8b6914;letter-spacing:0.15em;font-weight:600;">剧 本 <span style="float:right;color:#999;font-weight:400;font-size:0.7rem;">YAML 输出</span></div>')
            output_text = gr.Textbox(
                placeholder="剧本输出将在此显示...\n\n点击「转 换」开始",
                lines=22,
                max_lines=30,
                show_label=False,
                interactive=False,
                container=False,
            )

    # 控制栏
    with gr.Row():
        gr.HTML('<div style="flex:1;"></div>')
        example_btn = gr.Button("📖 加载示例", size="sm")
        convert_btn = gr.Button("转 换", variant="primary", size="lg")
        copy_btn = gr.Button("📋 复制", size="sm")
        download_btn = gr.Button("💾 下载YAML", size="sm")
        gr.HTML('<div style="flex:1;"></div>')

    # 状态栏
    status_bar = gr.HTML('<div style="text-align:center;padding:0.5rem;color:#999;font-size:0.75rem;border-top:1px solid #f0ece4;">就绪 · 等待输入</div>')
    schema_status = gr.HTML("", visible=False)

    # 事件绑定
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
